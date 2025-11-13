# Technical Specification - Logistics AI Agent

## System Overview

The Logistics AI Agent is a tool-use LLM system that orchestrates specialized optimization algorithms to solve transportation planning problems through natural language interfaces.

## Architecture Layers

### Layer 1: Interface Layer
- **FastAPI REST API**: HTTP endpoints for queries
- **Streamlit Web UI** (optional): Visual interface for demonstrations
- **CLI Tool**: Command-line interface for testing

### Layer 2: Agent Orchestration Layer
- **LangChain Agent Runtime**: Core orchestration logic
- **OpenAI GPT-4**: Language model for reasoning
- **State Management**: Conversation history, tool results
- **Guardrails**: Input validation, safety checks

### Layer 3: Tool Execution Layer
- **Routing Tool**: Distance/time matrix calculations
- **Optimization Tool**: OR-Tools VRP solver
- **Database Tool**: Order/vehicle data access
- **Cost Calculator Tool**: Economic analysis

### Layer 4: Data Layer
- **SQLite Database**: Operational data (orders, vehicles, depots)
- **CSV Files**: Solomon benchmark datasets
- **Configuration**: Parameters, cost models

## Technology Stack Details

### Core Dependencies

[tool.poetry.dependencies]
python = "^3.10"
fastapi = "^0.109.0"
uvicorn = "^0.27.0"
langchain = "^0.1.0"
langchain-openai = "^0.0.5"
openai = "^1.10.0"
ortools = "^9.8.0"
pandas = "^2.1.0"
numpy = "^1.26.0"
pydantic = "^2.5.0"
python-dotenv = "^1.0.0"
sqlalchemy = "^2.0.0"
streamlit = "^1.30.0" # optional
pytest = "^7.4.0"
httpx = "^0.26.0"

text

### Environment Variables

Required
OPENAI_API_KEY=sk-...

Optional
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_TEMPERATURE=0.0
DATABASE_URL=sqlite:///./logistics.db
LOG_LEVEL=INFO
MAX_AGENT_ITERATIONS=5
AGENT_TIMEOUT=30

text

## Data Models

### Order Model
class Order(BaseModel):
order_id: str
customer_id: str
demand: float # units (e.g., kg, packages)
service_time: int # minutes
time_window_start: int # minutes from midnight
time_window_end: int # minutes from midnight
latitude: float
longitude: float
is_cold_chain: bool = False
priority: Literal["low", "medium", "high"] = "medium"

text

### Vehicle Model
class Vehicle(BaseModel):
vehicle_id: str
capacity: float # units
max_working_hours: float # hours
cost_per_km: float # USD
fixed_cost: float # USD per shift
emissions_factor: float # kg CO2 per km
speed_kmh: float = 50.0
available: bool = True

text

### Depot Model
class Depot(BaseModel):
depot_id: str
name: str
latitude: float
longitude: float
time_window_start: int = 0 # open time (minutes from midnight)
time_window_end: int = 1440 # close time

text

### Route Model (Output)
class Route(BaseModel):
vehicle_id: str
stops: List[str] # ordered list of customer IDs
total_distance_km: float
total_time_minutes: float
total_cost_usd: float
emissions_kg: float
load_sequence: List[float] # cumulative load at each stop
time_sequence: List[int] # arrival time at each stop
constraints_satisfied: bool
constraint_violations: List[str] = []

text

### Agent Query Model
class AgentQuery(BaseModel):
query: str
context: Optional[Dict[str, Any]] = None
max_iterations: int = 5
include_explanation: bool = True
return_alternatives: bool = False

text

### Agent Response Model
class AgentResponse(BaseModel):
response_text: str # natural language explanation
routes: List[Route]
total_cost: float
total_emissions: float
execution_time_seconds: float
tools_called: List[str]
alternatives: Optional[List[Dict[str, Any]]] = None
metadata: Dict[str, Any] = {}

text

## Tool Specifications

### Tool 1: Routing Tool

**Purpose**: Calculate distance and time matrices between locations

**Function Signature**:
@tool
def calculate_distance_matrix(
locations: List[Tuple[float, float]],
mode: Literal["euclidean", "manhattan", "osrm"] = "euclidean"
) -> str:
"""
Calculate distance and time matrices for given locations.

text
Args:
    locations: List of (latitude, longitude) tuples
    mode: Distance calculation method

Returns:
    JSON string with distance_matrix (km) and time_matrix (minutes)
"""
text

**Implementation Details**:
- Euclidean distance: `sqrt((lat2-lat1)^2 + (lon2-lon1)^2) * 111  # approx km`
- OSRM (optional): HTTP API call to OSRM service
- Output format: JSON with 2D arrays

### Tool 2: Optimization Tool

**Purpose**: Solve Vehicle Routing Problem with Time Windows (VRPTW)

**Function Signature**:
@tool
def solve_vrp(
order_ids: List[str],
vehicle_ids: List[str],
constraints: Dict[str, Any],
objective: Literal["minimize_cost", "minimize_distance", "minimize_time", "minimize_emissions"] = "minimize_cost"
) -> str:
"""
Solve VRP using Google OR-Tools.

text
Args:
    order_ids: List of order IDs to route
    vehicle_ids: List of available vehicle IDs
    constraints: Dict with 'max_time', 'respect_time_windows', 'avoid_zones', etc.
    objective: Optimization objective

Returns:
    JSON string with route assignments, costs, and KPIs
"""
text

**Implementation Details**:
- Use OR-Tools RoutingIndexManager and RoutingModel
- Add capacity constraint
- Add time window constraint
- Add distance/time callback
- Set search parameters (first solution: PATH_CHEAPEST_ARC, local search: GUIDED_LOCAL_SEARCH)
- Timeout: 20 seconds

### Tool 3: Database Tool

**Purpose**: Access order, vehicle, and depot data

**Function Signatures**:
@tool
def get_orders(
order_ids: Optional[List[str]] = None,
filters: Optional[Dict[str, Any]] = None
) -> str:
"""Fetch order data from database"""

@tool
def get_vehicles(
vehicle_ids: Optional[List[str]] = None,
only_available: bool = True
) -> str:
"""Fetch vehicle data from database"""

@tool
def get_depot_info() -> str:
"""Fetch depot location and operating hours"""

text

### Tool 4: Cost Calculator Tool

**Purpose**: Calculate economics of routing plans

**Function Signature**:
@tool
def calculate_route_economics(
routes: List[Dict[str, Any]],
fuel_price_per_liter: float = 1.5,
driver_wage_per_hour: float = 15.0
) -> str:
"""
Calculate cost, emissions, and time for routes.

text
Args:
    routes: List of route dictionaries with distance, time
    fuel_price_per_liter: Current fuel price
    driver_wage_per_hour: Driver hourly wage

Returns:
    JSON with total_cost, fuel_cost, labor_cost, emissions, breakdown
"""
text

## Agent Configuration

### System Prompt

SYSTEM_PROMPT = """You are an expert logistics planning assistant. Your role is to help users optimize vehicle routing and delivery planning.

You have access to these tools:

calculate_distance_matrix: Calculate distances/times between locations

solve_vrp: Solve vehicle routing problems with constraints

get_orders: Fetch order data from database

get_vehicles: Fetch available vehicle information

get_depot_info: Get depot location and hours

calculate_route_economics: Calculate costs and emissions

When a user asks for routing help:

First, fetch the relevant orders and vehicles

Calculate distance matrix for all locations

Call the VRP solver with appropriate constraints

Calculate economics of the solution

Provide a clear explanation of the routes, costs, and any trade-offs

Always explain your reasoning and highlight important constraints that were satisfied or violated.
"""

text

### Agent Parameters

agent_config = {
"llm": ChatOpenAI(model="gpt-4-turbo-preview", temperature=0.0),
"tools": [calculate_distance_matrix, solve_vrp, get_orders, get_vehicles, get_depot_info, calculate_route_economics],
"max_iterations": 5,
"max_execution_time": 30,
"verbose": True,
"return_intermediate_steps": True,
"handle_parsing_errors": True
}

text

## API Endpoints

### POST `/ask`

**Request**:
{
"query": "Route 20 deliveries with 3 vehicles, minimize cost",
"context": {},
"max_iterations": 5,
"include_explanation": true
}

text

**Response**:
{
"response_text": "I've created an optimal routing plan...",
"routes": [...],
"total_cost": 327.50,
"total_emissions": 61.25,
"execution_time_seconds": 8.3,
"tools_called": ["get_orders", "get_vehicles", "calculate_distance_matrix", "solve_vrp", "calculate_route_economics"]
}

text

### POST `/solve_vrp_direct`

**Purpose**: Direct VRP solving (baseline comparison)

**Request**:
{
"orders": ["O1", "O2", ...],
"vehicles": ["V1", "V2"],
"constraints": {"max_time": 480},
"objective": "minimize_cost"
}

text

### GET `/health`

**Response**:
{
"status": "healthy",
"version": "0.1.0",
"timestamp": "2025-11-11T09:18:00Z"
}

text

### GET `/stats`

**Response**:
{
"total_queries": 142,
"successful_queries": 138,
"failed_queries": 4,
"average_response_time": 12.4,
"uptime_seconds": 86400
}

text

## Database Schema

### SQLite Tables

CREATE TABLE orders (
order_id TEXT PRIMARY KEY,
customer_id TEXT NOT NULL,
demand REAL NOT NULL,
service_time INTEGER NOT NULL,
time_window_start INTEGER NOT NULL,
time_window_end INTEGER NOT NULL,
latitude REAL NOT NULL,
longitude REAL NOT NULL,
is_cold_chain BOOLEAN DEFAULT 0,
priority TEXT DEFAULT 'medium',
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE vehicles (
vehicle_id TEXT PRIMARY KEY,
capacity REAL NOT NULL,
max_working_hours REAL NOT NULL,
cost_per_km REAL NOT NULL,
fixed_cost REAL NOT NULL,
emissions_factor REAL NOT NULL,
speed_kmh REAL DEFAULT 50.0,
available BOOLEAN DEFAULT 1,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE depots (
depot_id TEXT PRIMARY KEY,
name TEXT NOT NULL,
latitude REAL NOT NULL,
longitude REAL NOT NULL,
time_window_start INTEGER DEFAULT 0,
time_window_end INTEGER DEFAULT 1440,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE routes_history (
route_id TEXT PRIMARY KEY,
query TEXT NOT NULL,
solution JSON NOT NULL,
total_cost REAL NOT NULL,
execution_time REAL NOT NULL,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

text

## Error Handling

### Error Types

class LogisticsAgentError(Exception):
"""Base exception for logistics agent"""

class ToolExecutionError(LogisticsAgentError):
"""Tool failed to execute"""

class ConstraintViolationError(LogisticsAgentError):
"""Solution violates hard constraints"""

class DataNotFoundError(LogisticsAgentError):
"""Required data not found in database"""

class OptimizationTimeoutError(LogisticsAgentError):
"""VRP solver exceeded time limit"""

text

### Error Responses

{
"error": true,
"error_type": "ToolExecutionError",
"message": "OR-Tools solver timed out after 20 seconds",
"details": {"orders_count": 100, "vehicles_count": 5},
"suggestions": ["Reduce problem size", "Increase timeout", "Use heuristic solver"]
}

text

## Testing Strategy

### Unit Tests
- Each tool function independently
- Data models validation
- Database operations

### Integration Tests
- Agent workflow end-to-end
- API endpoints
- Tool chaining

### Performance Tests
- Response time benchmarks
- Concurrent request handling
- Memory usage profiling

### Evaluation Tests
- Solomon benchmark instances
- Comparison with OR-Tools baseline
- Constraint satisfaction validation

---

**Document Status**: ✅ Complete
**Last Updated**: 2025-11-11