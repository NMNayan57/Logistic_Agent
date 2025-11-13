"""
FastAPI application for Logistics AI Agent.

This module provides the REST API interface for the logistics agent.
"""

import time
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.agent import get_agent, LogisticsAgent
from src.models.query import AgentQuery, AgentResponse, DirectVRPRequest, DirectVRPResponse
from src.models.route import Route
from src.tools import solve_vrp, calculate_route_economics
from src.database import get_database_stats, get_db
from src.config import get_settings
from src.utils.logger import setup_logger
import json

# Initialize logger
logger = setup_logger(__name__)

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Logistics AI Agent API",
    description="AI-powered logistics planning and vehicle routing optimization using LLMs and OR-Tools",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Application state
app_state = {
    "start_time": datetime.utcnow(),
    "total_queries": 0,
    "successful_queries": 0,
    "failed_queries": 0,
    "total_execution_time": 0.0
}


# ============================================================================
# Health & Status Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Logistics AI Agent API",
        "status": "online",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns service health status and basic information.
    """
    uptime_seconds = (datetime.utcnow() - app_state["start_time"]).total_seconds()

    return {
        "status": "healthy",
        "version": "0.1.0",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": uptime_seconds,
        "model": settings.openai_model
    }


@app.get("/stats")
async def get_stats(db=Depends(get_db)):
    """
    Get API usage statistics and database information.

    Returns query statistics and database counts.
    """
    try:
        # Get database stats
        db_stats = get_database_stats(db)

        # Calculate average response time
        avg_response_time = 0.0
        if app_state["total_queries"] > 0:
            avg_response_time = app_state["total_execution_time"] / app_state["total_queries"]

        uptime_seconds = (datetime.utcnow() - app_state["start_time"]).total_seconds()

        return {
            "api_stats": {
                "total_queries": app_state["total_queries"],
                "successful_queries": app_state["successful_queries"],
                "failed_queries": app_state["failed_queries"],
                "average_response_time": round(avg_response_time, 2),
                "uptime_seconds": int(uptime_seconds)
            },
            "database_stats": db_stats,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Agent Endpoints
# ============================================================================

@app.post("/ask")
async def ask_agent(query: AgentQuery, agent: LogisticsAgent = Depends(get_agent)):
    """
    Main endpoint for agent queries.

    Submit a natural language query to the logistics agent.
    The agent will use appropriate tools to solve the routing problem
    and provide a comprehensive response with routes and costs.

    Args:
        query: AgentQuery object with the natural language question

    Returns:
        AgentResponse with routes, costs, and natural language explanation

    Example:
        ```
        POST /ask
        {
            "query": "Route 20 deliveries with 3 vehicles, minimize cost",
            "context": {"fuel_price": 3.50},
            "max_iterations": 5,
            "include_explanation": true
        }
        ```
    """
    logger.info(f"Received agent query: {query.query[:100]}...")

    app_state["total_queries"] += 1
    start_time = time.time()

    try:
        # Execute agent
        result = agent.ask(
            query=query.query,
            context=query.context
        )

        execution_time = time.time() - start_time
        app_state["total_execution_time"] += execution_time

        if not result["success"]:
            app_state["failed_queries"] += 1
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Agent execution failed")
            )

        app_state["successful_queries"] += 1

        # Extract structured data from intermediate steps
        routes = []
        total_cost = 0.0
        total_emissions = 0.0
        total_distance = 0.0
        total_time = 0.0
        constraint_violations = []

        if result.get("intermediate_steps"):
            for step in result["intermediate_steps"]:
                try:
                    tool_action = step[0]
                    tool_output = step[1]
                    tool_name = tool_action.tool if hasattr(tool_action, 'tool') else None

                    # Parse VRP solution
                    if tool_name == "solve_vrp":
                        try:
                            vrp_data = json.loads(tool_output)
                            routes = vrp_data.get("routes", [])
                            total_distance = vrp_data.get("total_distance_km", 0)
                            total_time = vrp_data.get("total_time_minutes", 0)
                            
                            # Extract constraint violations if present
                            if "constraint_violations" in vrp_data:
                                constraint_violations = vrp_data["constraint_violations"]
                        except (json.JSONDecodeError, AttributeError) as e:
                            logger.warning(f"Failed to parse VRP output: {e}")

                    # Parse economics/cost data
                    elif tool_name == "calculate_route_economics":
                        try:
                            econ_data = json.loads(tool_output)
                            total_cost = econ_data.get("total_cost_usd", 0.0)
                            total_emissions = econ_data.get("total_emissions_kg", 0.0)
                        except (json.JSONDecodeError, AttributeError) as e:
                            logger.warning(f"Failed to parse economics output: {e}")

                except Exception as e:
                    logger.warning(f"Error parsing tool step: {e}")
                    continue

        # AUTO-CALCULATE economics if agent didn't call the economics tool
        if total_cost == 0.0 and routes:
            logger.warning("Agent did not call calculate_route_economics, using fallback calculation")
            for route in routes:
                distance = route.get("distance_km", 0)
                time_mins = route.get("time_minutes", 0)

                # Default cost parameters
                fuel_cost = distance * 0.35 * settings.default_fuel_price_per_liter
                labor_cost = (time_mins / 60.0) * settings.default_driver_wage_per_hour
                fixed_cost = 50.0  # per vehicle per day
                maintenance_cost = distance * 0.10

                route_cost = fuel_cost + labor_cost + fixed_cost + maintenance_cost
                route_emissions = distance * 0.35  # kg CO2 per km

                total_cost += route_cost
                total_emissions += route_emissions

            logger.info(f"Fallback calculation: ${total_cost:.2f}, {total_emissions:.2f} kg CO2")

        response = {
            "response_text": result["response"],
            "routes": routes,
            "total_cost": round(total_cost, 2),
            "total_emissions": round(total_emissions, 2),
            "total_distance": round(total_distance, 2),
            "total_time": round(total_time, 2),
            "execution_time_seconds": round(execution_time, 2),
            "tools_called": result["tools_called"],
            "intermediate_steps": result.get("intermediate_steps", []),
            "metadata": {
                "iterations": result["iterations"],
                "model": settings.openai_model,
                "success": result["success"],
                "constraint_violations": constraint_violations
            }
        }

        logger.info(f"Query completed successfully in {execution_time:.2f}s with {len(routes)} routes")

        return response

    except HTTPException:
        raise
    except Exception as e:
        app_state["failed_queries"] += 1
        execution_time = time.time() - start_time
        app_state["total_execution_time"] += execution_time

        logger.error(f"Error processing agent query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/solve_vrp_direct")
async def solve_vrp_direct_endpoint(request: DirectVRPRequest):
    """
    Direct VRP solving endpoint (baseline comparison).

    Solves VRP directly without the LLM agent layer.
    Useful for:
    - Baseline performance comparison
    - Direct API access when you already have structured data
    - Testing OR-Tools solver independently

    Args:
        request: DirectVRPRequest with order IDs, vehicle IDs, and constraints

    Returns:
        DirectVRPResponse with routes and solver metrics

    Example:
        ```
        POST /solve_vrp_direct
        {
            "order_ids": ["O001", "O002", "O003"],
            "vehicle_ids": ["V001", "V002"],
            "constraints": {"max_time": 480},
            "objective": "minimize_cost"
        }
        ```
    """
    logger.info("Received direct VRP solve request")

    start_time = time.time()

    try:
        # Call VRP solver tool directly
        result_json = solve_vrp.invoke({
            "order_ids": json.dumps(request.order_ids),
            "vehicle_ids": json.dumps(request.vehicle_ids),
            "constraints": json.dumps(request.constraints) if request.constraints else None,
            "objective": request.objective
        })

        result = json.loads(result_json)

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        execution_time = time.time() - start_time

        # Parse routes - transform field names to match Route model
        routes = []
        for route_data in result.get("routes", []):
            # Extract vehicle info
            vehicle_info = route_data.get("vehicle_info", {})
            distance = route_data.get("distance_km", 0)
            time_mins = route_data.get("time_minutes", 0)

            # Calculate costs and emissions (rough estimates)
            fuel_cost = distance * vehicle_info.get("fuel_consumption_per_km", 0.35) * 1.5  # $1.50/liter
            labor_cost = (time_mins / 60.0) * 15.0  # $15/hour
            fixed_cost = vehicle_info.get("fixed_cost_per_day", 50.0)
            total_cost = fuel_cost + labor_cost + fixed_cost

            emissions = distance * vehicle_info.get("emissions_kg_per_km", 0.35)

            # Transform to Route model format
            route = Route(
                vehicle_id=route_data.get("vehicle_id"),
                stops=route_data.get("stops", []),
                total_distance_km=distance,
                total_time_minutes=time_mins,
                total_cost_usd=round(total_cost, 2),
                emissions_kg=round(emissions, 2),
                load_sequence=route_data.get("load_sequence", []),
                time_sequence=route_data.get("time_sequence", []),
                constraints_satisfied=True,  # OR-Tools only returns feasible solutions
                constraint_violations=[]
            )
            routes.append(route)

        response = DirectVRPResponse(
            routes=routes,
            total_cost=sum(r.total_cost_usd for r in routes),
            execution_time_seconds=execution_time,
            solver_status=result.get("solver_status", "UNKNOWN"),
            metadata=result
        )

        logger.info(f"Direct VRP solved in {execution_time:.2f}s")

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error solving VRP directly: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class ScenarioComparisonRequest(BaseModel):
    """Request model for scenario comparison"""
    order_ids: list[str] = Field(..., description="List of order IDs to route")
    vehicle_ids: list[str] = Field(..., description="List of vehicle IDs available")
    scenarios: Dict[str, Dict[str, Any]] = Field(..., description="Dictionary of scenario configurations")


@app.post("/compare_scenarios")
async def compare_scenarios_endpoint(request: ScenarioComparisonRequest):
    """
    Compare multiple what-if scenarios for vehicle routing.

    This endpoint allows testing how different parameters affect routing outcomes.
    Perfect for research analysis and contingency planning.

    Args:
        order_ids: List of order IDs to route
        vehicle_ids: List of vehicle IDs available
        scenarios: Dictionary where each key is a scenario name and value contains:
            - description: Human-readable scenario description
            - fuel_price_per_liter: Optional float (default: 1.5)
            - driver_wage_per_hour: Optional float (default: 15.0)
            - avg_speed_reduction: Optional float 0-1 (default: 0.0)
            - max_route_time_minutes: Optional int (default: 480)
            - num_vehicles: Optional int (overrides vehicle count)

    Returns:
        JSON with comparison results showing costs, times, and differences

    Example:
        ```
        POST /compare_scenarios
        {
            "order_ids": ["O001", "O002", "O003", "O004", "O005"],
            "vehicle_ids": ["V001", "V002"],
            "scenarios": {
                "baseline": {
                    "description": "Current conditions"
                },
                "fuel_spike": {
                    "description": "25% fuel price increase",
                    "fuel_price_per_liter": 1.875
                },
                "add_vehicle": {
                    "description": "Add one more vehicle",
                    "num_vehicles": 3
                }
            }
        }
        ```
    """
    from src.tools.scenario_tool import compare_scenarios

    logger.info(f"Comparing {len(request.scenarios)} scenarios for {len(request.order_ids)} orders")

    start_time = time.time()

    try:
        # Call scenario comparison tool
        result_json = compare_scenarios.invoke({
            "base_order_ids": json.dumps(request.order_ids),
            "base_vehicle_ids": json.dumps(request.vehicle_ids),
            "scenarios": json.dumps(request.scenarios)
        })

        result = json.loads(result_json)

        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message", "Unknown error"))

        execution_time = time.time() - start_time

        response = {
            **result,
            "execution_time_seconds": round(execution_time, 2)
        }

        logger.info(f"Scenario comparison completed in {execution_time:.2f}s")

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing scenarios: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


class SensitivityAnalysisRequest(BaseModel):
    """Request model for sensitivity analysis"""
    order_ids: list[str] = Field(..., description="List of order IDs")
    vehicle_ids: list[str] = Field(..., description="List of vehicle IDs")
    parameter: str = Field(..., description="Parameter to vary")
    min_value: float = Field(..., description="Minimum value")
    max_value: float = Field(..., description="Maximum value")
    steps: int = Field(5, description="Number of data points")


@app.post("/analyze_sensitivity")
async def analyze_sensitivity_endpoint(request: SensitivityAnalysisRequest):
    """
    Analyze parameter sensitivity across a range.

    Tests how a single parameter affects routing outcomes.

    Args:
        order_ids: List of order IDs
        vehicle_ids: List of vehicle IDs
        parameter: Parameter to vary ("fuel_price", "driver_wage", "speed_reduction", "max_time")
        min_value: Minimum value for parameter range
        max_value: Maximum value for parameter range
        steps: Number of data points (default: 5)

    Returns:
        JSON with sensitivity analysis results and insights

    Example:
        ```
        POST /analyze_sensitivity
        {
            "order_ids": ["O001", "O002", "O003"],
            "vehicle_ids": ["V001", "V002"],
            "parameter": "fuel_price",
            "min_value": 1.0,
            "max_value": 2.5,
            "steps": 5
        }
        ```
    """
    from src.tools.scenario_tool import analyze_parameter_sensitivity

    logger.info(f"Analyzing {request.parameter} sensitivity from {request.min_value} to {request.max_value}")

    start_time = time.time()

    try:
        result_json = analyze_parameter_sensitivity.invoke({
            "order_ids": json.dumps(request.order_ids),
            "vehicle_ids": json.dumps(request.vehicle_ids),
            "parameter": request.parameter,
            "min_value": request.min_value,
            "max_value": request.max_value,
            "steps": request.steps
        })

        result = json.loads(result_json)

        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message", "Unknown error"))

        execution_time = time.time() - start_time

        response = {
            **result,
            "execution_time_seconds": round(execution_time, 2)
        }

        logger.info(f"Sensitivity analysis completed in {execution_time:.2f}s")

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing sensitivity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Tool Endpoints (for testing/debugging)
# ============================================================================

@app.get("/tools")
async def list_tools(agent: LogisticsAgent = Depends(get_agent)):
    """
    List all available tools the agent can use.

    Returns list of tool names and their descriptions.
    """
    from src.tools import ALL_TOOLS

    tools_info = []
    for tool in ALL_TOOLS:
        tools_info.append({
            "name": tool.name,
            "description": tool.description[:100] + "..." if len(tool.description) > 100 else tool.description
        })

    return {
        "tools": tools_info,
        "count": len(tools_info)
    }


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}")
    import traceback
    logger.error(traceback.format_exc())

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "type": type(exc).__name__
        }
    )


# ============================================================================
# Startup/Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("=" * 60)
    logger.info("Logistics AI Agent API Starting")
    logger.info("=" * 60)
    logger.info(f"Version: 0.1.0")
    logger.info(f"Model: {settings.openai_model}")
    logger.info(f"Database: {settings.database_url}")
    logger.info(f"Debug: {settings.debug}")

    # Initialize agent (warm up)
    try:
        agent = get_agent()
        logger.info(f"Agent initialized with {len(agent.get_available_tools())} tools")
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        logger.error("API will start but agent queries will fail until configuration is fixed")

    logger.info("API ready to accept requests")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Logistics AI Agent API")


# ============================================================================
# Run Application
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
