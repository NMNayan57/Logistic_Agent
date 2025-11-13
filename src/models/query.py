"""
Query and response models for the AI agent API.

This module defines the request and response schemas for interacting
with the Logistics AI Agent.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from src.models.route import Route


class AgentQuery(BaseModel):
    """
    Request model for agent queries.

    Attributes:
        query: Natural language query
        context: Optional context parameters (fuel price, wage, etc.)
        max_iterations: Maximum agent reasoning iterations
        include_explanation: Whether to include detailed explanation
        return_alternatives: Whether to return alternative solutions

    Example:
        >>> query = AgentQuery(
        ...     query="Route 20 deliveries with 3 vehicles, minimize cost",
        ...     context={"fuel_price": 3.50, "driver_wage": 15.00},
        ...     max_iterations=5,
        ...     include_explanation=True,
        ...     return_alternatives=False
        ... )
    """

    query: str = Field(
        ...,
        description="Natural language query",
        min_length=10,
        max_length=2000
    )

    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional context parameters (fuel_price, driver_wage, etc.)"
    )

    max_iterations: int = Field(
        default=5,
        description="Maximum agent iterations",
        ge=1,
        le=10
    )

    include_explanation: bool = Field(
        default=True,
        description="Include detailed natural language explanation"
    )

    return_alternatives: bool = Field(
        default=False,
        description="Return alternative solutions"
    )

    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"Query: {self.query[:50]}..."

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "query": "Route 20 deliveries with 3 vehicles, minimize cost, keep cold-chain under 2 hours",
                "context": {
                    "fuel_price": 3.50,
                    "driver_wage": 15.00
                },
                "max_iterations": 5,
                "include_explanation": True,
                "return_alternatives": False
            }
        }


class AgentResponse(BaseModel):
    """
    Response model for agent queries.

    Attributes:
        response_text: Natural language explanation of the solution
        routes: List of optimized routes
        total_cost: Total solution cost (USD)
        total_emissions: Total CO2 emissions (kg)
        execution_time_seconds: Time taken to generate solution
        tools_called: List of tools invoked by the agent
        alternatives: Optional alternative solutions
        metadata: Additional metadata about the solution

    Example:
        >>> response = AgentResponse(
        ...     response_text="I've created an optimal routing plan...",
        ...     routes=[route1, route2, route3],
        ...     total_cost=327.50,
        ...     total_emissions=61.25,
        ...     execution_time_seconds=8.3,
        ...     tools_called=["get_orders", "solve_vrp"],
        ...     alternatives=None,
        ...     metadata={"iterations": 4, "orders_count": 20}
        ... )
    """

    response_text: str = Field(
        ...,
        description="Natural language explanation of the solution",
        min_length=10
    )

    routes: List[Route] = Field(
        ...,
        description="List of optimized vehicle routes"
    )

    total_cost: float = Field(
        ...,
        description="Total solution cost (USD)",
        ge=0.0
    )

    total_emissions: float = Field(
        ...,
        description="Total CO2 emissions (kg)",
        ge=0.0
    )

    execution_time_seconds: float = Field(
        ...,
        description="Execution time in seconds",
        ge=0.0
    )

    tools_called: List[str] = Field(
        ...,
        description="List of tools invoked by the agent"
    )

    alternatives: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Alternative solutions (if requested)"
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (iterations, order count, etc.)"
    )

    def num_vehicles_used(self) -> int:
        """Get number of vehicles used in solution."""
        return len(self.routes)

    def total_distance_km(self) -> float:
        """Get total distance across all routes."""
        return sum(route.total_distance_km for route in self.routes)

    def total_time_hours(self) -> float:
        """Get total time across all routes in hours."""
        return sum(route.total_time_minutes for route in self.routes) / 60.0

    def num_deliveries(self) -> int:
        """Get total number of deliveries across all routes."""
        return sum(route.num_deliveries() for route in self.routes)

    def cost_per_delivery(self) -> float:
        """Calculate cost per delivery."""
        deliveries = self.num_deliveries()
        if deliveries == 0:
            return 0.0
        return self.total_cost / deliveries

    def emissions_per_km(self) -> float:
        """Calculate emissions per kilometer."""
        distance = self.total_distance_km()
        if distance == 0:
            return 0.0
        return self.total_emissions / distance

    def all_constraints_satisfied(self) -> bool:
        """Check if all routes satisfy constraints."""
        return all(route.is_feasible() for route in self.routes)

    def get_violations(self) -> List[str]:
        """Get all constraint violations across routes."""
        violations = []
        for route in self.routes:
            violations.extend(route.constraint_violations)
        return violations

    def __str__(self) -> str:
        """Human-readable string representation."""
        return (
            f"Solution: {self.num_vehicles_used()} vehicles, "
            f"{self.num_deliveries()} deliveries, "
            f"${self.total_cost:.2f}, "
            f"{self.execution_time_seconds:.1f}s"
        )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "response_text": "I've created an optimal routing plan for your 20 deliveries using 3 vehicles. Total cost: $327.50, Distance: 245km, CO2: 61.25kg",
                "routes": [
                    {
                        "vehicle_id": "V001",
                        "stops": ["D001", "C012", "C005", "D001"],
                        "total_distance_km": 85.3,
                        "total_time_minutes": 245,
                        "total_cost_usd": 127.50,
                        "emissions_kg": 21.3,
                        "load_sequence": [0, 15, 30, 0],
                        "time_sequence": [480, 510, 550, 725],
                        "constraints_satisfied": True,
                        "constraint_violations": []
                    }
                ],
                "total_cost": 327.50,
                "total_emissions": 61.25,
                "execution_time_seconds": 8.3,
                "tools_called": ["get_orders", "get_vehicles", "solve_vrp"],
                "alternatives": None,
                "metadata": {
                    "iterations": 4,
                    "orders_count": 20,
                    "vehicles_used": 3
                }
            }
        }


class DirectVRPRequest(BaseModel):
    """
    Request model for direct VRP solving (baseline comparison).

    Attributes:
        order_ids: List of order IDs to route
        vehicle_ids: List of available vehicle IDs
        constraints: Constraint dictionary
        objective: Optimization objective

    Example:
        >>> request = DirectVRPRequest(
        ...     order_ids=["O001", "O002", "O003"],
        ...     vehicle_ids=["V001", "V002"],
        ...     constraints={"max_time": 480, "respect_time_windows": True},
        ...     objective="minimize_cost"
        ... )
    """

    order_ids: List[str] = Field(
        ...,
        description="List of order IDs to route",
        min_length=1
    )

    vehicle_ids: List[str] = Field(
        ...,
        description="List of available vehicle IDs",
        min_length=1
    )

    constraints: Dict[str, Any] = Field(
        default_factory=dict,
        description="Constraint dictionary (max_time, respect_time_windows, etc.)"
    )

    objective: str = Field(
        default="minimize_cost",
        description="Optimization objective"
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "order_ids": ["O001", "O002", "O003"],
                "vehicle_ids": ["V001", "V002"],
                "constraints": {
                    "max_time": 480,
                    "respect_time_windows": True
                },
                "objective": "minimize_cost"
            }
        }


class DirectVRPResponse(BaseModel):
    """
    Response model for direct VRP solving.

    Attributes:
        routes: List of optimized routes
        total_cost: Total solution cost
        execution_time_seconds: Computation time
        solver_status: Solver status message
        metadata: Additional solver metadata
    """

    routes: List[Route] = Field(
        ...,
        description="List of optimized vehicle routes"
    )

    total_cost: float = Field(
        ...,
        description="Total solution cost (USD)",
        ge=0.0
    )

    execution_time_seconds: float = Field(
        ...,
        description="Solver execution time in seconds",
        ge=0.0
    )

    solver_status: str = Field(
        ...,
        description="Solver status (OPTIMAL, FEASIBLE, INFEASIBLE, etc.)"
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional solver metadata"
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "routes": [],
                "total_cost": 285.00,
                "execution_time_seconds": 5.2,
                "solver_status": "OPTIMAL",
                "metadata": {
                    "iterations": 1523,
                    "nodes_explored": 8942
                }
            }
        }
