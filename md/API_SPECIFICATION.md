text
# API Specification - Logistics AI Agent

## Base URL

**Development**: `http://localhost:8000`
**Production**: `https://logistics-agent-xyz.onrender.com`

## Authentication

Currently no authentication (PoC). API keys will be added in production.

## Endpoints

### 1. Health Check

**GET** `/health`

Check if the service is running.

**Response 200**:
{
"status": "healthy",
"version": "0.1.0",
"timestamp": "2025-11-11T09:18:00Z"
}

text

---

### 2. Agent Query (Main Endpoint)

**POST** `/ask`

Submit a natural language query to the agent.

**Request Body**:
{
"query": "Route 20 deliveries with 3 vehicles, minimize cost, keep cold-chain under 2 hours",
"context": {
"fuel_price": 3.50,
"driver_wage": 15.00
},
"max_iterations": 5,
"include_explanation": true,
"return_alternatives": false
}

text

**Request Schema**:
{
query: string; // Natural language query
context?: object; // Optional context
max_iterations?: number; // Max agent iterations (default: 5)
include_explanation?: boolean; // Include reasoning (default: true)
return_alternatives?: boolean; // Return alternative solutions (default: false)
}

text

**Response 200**:
{
"response_text": "I've created an optimal routing plan for your 20 deliveries...",
"routes": [
{
"vehicle_id": "V001",
"stops": ["D001", "C012", "C005", "C018", "D001"],
"total_distance_km": 85.3,
"total_time_minutes": 245,
"total_cost_usd": 127.50,
"emissions_kg": 21.3,
"load_sequence":,​
"time_sequence": ,
"constraints_satisfied": true,
"constraint_violations": []
}
],
"total_cost": 327.50,
"total_emissions": 61.25,
"execution_time_seconds": 8.3,
"tools_called": ["get_orders", "get_vehicles", "calculate_distance_matrix", "solve_vrp", "calculate_route_economics"],
"alternatives": null,
"metadata": {
"iterations": 4,
"orders_count": 20,
"vehicles_used": 3
}
}

text

**Response 400** (Bad Request):
{
"error": true,
"error_type": "ValidationError",
"message": "Invalid query: order count exceeds limit",
"details": {}
}

text

**Response 500** (Server Error):
{
"error": true,
"error_type": "ToolExecutionError",
"message": "OR-Tools solver timed out",
"details": {"timeout_seconds": 20}
}

text

---

### 3. Direct VRP Solver (Baseline)

**POST** `/solve_vrp_direct`

Directly solve VRP without agent (for comparison).

**Request Body**:
{
"orders": ["O001", "O002", "O003"],
"vehicles": ["V001", "V002"],
"constraints": {
"max_time": 480,
"respect_time_windows": true
},
"objective": "minimize_cost"
}

text

**Response 200**:
{
"routes": [...],
"total_cost": 285.00,
"execution_time_seconds": 5.2
}

text

---

### 4. Get Orders

**GET** `/orders`

Fetch orders from database.

**Query Parameters**:
- `order_ids`: Comma-separated order IDs (optional)
- `count`: Number of orders to return (optional)
- `cold_chain_only`: boolean (optional)

**Example**: `/orders?count=10&cold_chain_only=true`

**Response 200**:
{
"orders": [
{
"order_id": "O001",
"customer_id": "C001",
"demand": 15.0,
"service_time": 10,
"time_window_start": 480,
"time_window_end": 720,
"latitude": 40.7128,
"longitude": -74.0060,
"is_cold_chain": true,
"priority": "high"
}
],
"count": 10
}

text

---

### 5. Get Vehicles

**GET** `/vehicles`

Fetch vehicles from database.

**Query Parameters**:
- `vehicle_ids`: Comma-separated vehicle IDs (optional)
- `available_only`: boolean (default: true)

**Response 200**:
{
"vehicles": [
{
"vehicle_id": "V001",
"capacity": 100.0,
"max_working_hours": 8.0,
"cost_per_km": 2.50,
"fixed_cost": 50.0,
"emissions_factor": 0.25,
"speed_kmh": 50.0,
"available": true
}
],
"count": 3
}

text

---

### 6. Statistics

**GET** `/stats`

Get API usage statistics.

**Response 200**:
{
"total_queries": 142,
"successful_queries": 138,
"failed_queries": 4,
"average_response_time": 12.4,
"uptime_seconds": 86400,
"openai_api_calls": 456,
"estimated_cost_usd": 2.35
}

text

---

## Error Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid input parameters |
| 404 | Not Found | Resource not found |
| 500 | Server Error | Internal server error |
| 503 | Service Unavailable | Service temporarily down |

---

## Rate Limiting

**PoC**: No rate limiting
**Production**: 60 requests/minute per IP

---

## Swagger Documentation

Interactive API documentation available at:
- `http://localhost:8000/docs` (development)
- `https://logistics-agent-xyz.onrender.com/docs` (production)

---

**Document Status**: ✅ Complete
**Last Updated**: 2025-11-11