text
# System Architecture - Logistics AI Agent

## High-Level Architecture Diagram

┌─────────────────────────────────────────────────────────────┐
│ INTERFACE LAYER │
│ │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │
│ │ FastAPI │ │ Streamlit │ │ CLI │ │
│ │ REST API │ │ Web UI │ │ Interface │ │
│ │ (Port 8000) │ │ (Port 8501) │ │ (python) │ │
│ └──────────────┘ └──────────────┘ └──────────────┘ │
│ │ │ │ │
└─────────┼──────────────────┼──────────────────┼──────────────┘
│ │ │
└──────────────────┴──────────────────┘
│
┌────────────────────────────┴─────────────────────────────────┐
│ AGENT ORCHESTRATION LAYER │
│ │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ LangChain AgentExecutor │ │
│ │ ┌──────────────────────────────────────────────────┐ │ │
│ │ │ OpenAI GPT-4 (Function Calling) │ │ │
│ │ │ - Model: gpt-4-turbo-preview │ │ │
│ │ │ - Temperature: 0.0 (deterministic) │ │ │
│ │ │ - Max tokens: 4096 │ │ │
│ │ └──────────────────────────────────────────────────┘ │ │
│ │ │ │
│ │ ┌──────────────────────────────────────────────────┐ │ │
│ │ │ State Manager │ │ │
│ │ │ - Conversation history: List[Message] │ │ │
│ │ │ - Tool call results: Dict[str, Any] │ │ │
│ │ │ - Current context: Dict[str, Any] │ │ │
│ │ └──────────────────────────────────────────────────┘ │ │
│ │ │ │
│ │ ┌──────────────────────────────────────────────────┐ │ │
│ │ │ Guardrails & Validation │ │ │
│ │ │ - Input sanitization │ │ │
│ │ │ - Cost budget checks (API calls) │ │ │
│ │ │ - Iteration limits (max 5) │ │ │
│ │ │ - Safety constraints verification │ │ │
│ │ └──────────────────────────────────────────────────┘ │ │
│ └────────────────────────────────────────────────────────┘ │
└────────────────────────────┬─────────────────────────────────┘
│
┌────────────────────────────┴─────────────────────────────────┐
│ TOOL EXECUTION LAYER │
│ │
│ ┌──────────────────┐ ┌──────────────────┐ │
│ │ Routing Tool │ │ Optimization Tool│ │
│ │ │ │ │ │
│ │ calculate_ │ │ solve_vrp() │ │
│ │ distance_matrix │ │ │ │
│ │ │ │ - OR-Tools VRP │ │
│ │ Modes: │ │ - Capacity │ │
│ │ - Euclidean │ │ - Time Windows │ │
│ │ - Manhattan │ │ - Custom cost │ │
│ │ - OSRM API │ │ │ │
│ └──────────────────┘ └──────────────────┘ │
│ │
│ ┌──────────────────┐ ┌──────────────────┐ │
│ │ Database Tool │ │ Cost Tool │ │
│ │ │ │ │ │
│ │ get_orders() │ │ calculate_route_│ │
│ │ get_vehicles() │ │ economics() │ │
│ │ get_depot_info()│ │ │ │
│ │ │ │ - Fuel costs │ │
│ │ SQLAlchemy ORM │ │ - Labor costs │ │
│ │ │ │ - Emissions │ │
│ └──────────────────┘ └──────────────────┘ │
└────────────────────────────┬─────────────────────────────────┘
│
┌────────────────────────────┴─────────────────────────────────┐
│ DATA LAYER │
│ │
│ ┌───────────────────────────────────────────────────────┐ │
│ │ SQLite Database (logistics.db) │ │
│ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │ │
│ │ │ orders │ │ vehicles │ │ depots │ │ │
│ │ │ table │ │ table │ │ table │ │ │
│ │ └─────────────┘ └─────────────┘ └─────────────┘ │ │
│ │ ┌─────────────────────────────────────────────┐ │ │
│ │ │ routes_history table │ │ │
│ │ └─────────────────────────────────────────────┘ │ │
│ └───────────────────────────────────────────────────────┘ │
│ │
│ ┌───────────────────────────────────────────────────────┐ │
│ │ File Storage │ │
│ │ - Solomon benchmark datasets (data/solomon/.txt) │ │
│ │ - Sample CSV files (data/.csv) │ │
│ │ - Configuration files (config/*.yaml) │ │
│ └───────────────────────────────────────────────────────┘ │
│ │
│ ┌───────────────────────────────────────────────────────┐ │
│ │ External APIs (Optional) │ │
│ │ - OSRM Routing Service (http://router.project-osrm.org)│
│ │ - Weather API (for advanced scenarios) │ │
│ │ - Traffic API (for real-time data) │ │
│ └───────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘

text

## Component Details

### 1. Interface Layer

**FastAPI REST API**:
- Handles HTTP requests
- Auto-generates Swagger/OpenAPI documentation at `/docs`
- Async request handling
- CORS middleware for frontend integration
- Request logging and monitoring

**Streamlit Web UI** (Optional):
- Simple form for entering queries
- Visual display of routes on map
- Cost breakdown charts
- Historical query browsing

**CLI Interface**:
- Command-line tool for testing
- Batch processing of queries
- Export results to CSV/JSON

### 2. Agent Orchestration Layer

**LangChain AgentExecutor**:
- Manages conversation flow
- Selects which tools to call based on user query
- Maintains state across multiple turns
- Handles errors and retries

**OpenAI GPT-4**:
- Understands natural language queries
- Generates tool calls with parameters
- Synthesizes responses from tool outputs
- Provides explanations and reasoning

**State Manager**:
- Tracks conversation history
- Caches tool results to avoid redundant calls
- Maintains user context (preferences, constraints)

**Guardrails**:
- Validates inputs before tool execution
- Checks API cost budgets
- Enforces iteration limits
- Verifies safety constraints (no unsafe routes)

### 3. Tool Execution Layer

**Routing Tool**:
- Calculates distance matrices
- Three modes: Euclidean (fast), Manhattan (grid-based), OSRM (realistic)
- Caches results for repeated queries
- Handles missing/invalid coordinates

**Optimization Tool**:
- Uses Google OR-Tools Routing library
- Supports multiple objectives (cost, distance, time, emissions)
- Enforces constraints (capacity, time windows, driver hours)
- Returns multiple solutions if requested

**Database Tool**:
- SQLAlchemy ORM for database access
- Filters orders by criteria (cold-chain, priority, time windows)
- Checks vehicle availability
- Retrieves depot information

**Cost Calculator Tool**:
- Calculates fuel costs (distance × fuel efficiency × price)
- Calculates labor costs (time × wage + overtime penalties)
- Calculates emissions (distance × emissions factor)
- Provides breakdown by vehicle

### 4. Data Layer

**SQLite Database**:
- Lightweight, file-based database
- Suitable for PoC (upgrade to PostgreSQL for production)
- Tables: orders, vehicles, depots, routes_history
- Indexed for fast queries

**File Storage**:
- Solomon benchmark datasets in standard format
- Sample CSV files for testing
- Configuration YAML files

**External APIs**:
- OSRM for realistic routing (optional)
- Weather/traffic APIs for advanced scenarios (future)

## Data Flow Example

### Query: "Route 20 deliveries with 3 vehicles, minimize cost"

User → FastAPI POST /ask
Request: {"query": "Route 20 deliveries with 3 vehicles, minimize cost"}

FastAPI → Agent Orchestrator
Creates AgentExecutor, passes query

Agent → GPT-4
"Understand query: need 20 orders, 3 vehicles, minimize cost"

GPT-4 → Tool: get_orders(count=20)
Response: [Order(...), Order(...), ...]

GPT-4 → Tool: get_vehicles(count=3)
Response: [Vehicle(...), Vehicle(...), Vehicle(...)]

GPT-4 → Tool: calculate_distance_matrix(locations=[...])
Response: {"distance_matrix": [[0, 12.3, ...], ...], "time_matrix": [...]}

GPT-4 → Tool: solve_vrp(orders=[...], vehicles=[...], objective="minimize_cost")
[OR-Tools solving for 10-20 seconds]
Response: {"routes": [...], "total_distance": 245, ...}

GPT-4 → Tool: calculate_route_economics(routes=[...])
Response: {"total_cost": 327.50, "fuel_cost": 147, "labor_cost": 180, ...}

GPT-4 → Agent
Synthesizes natural language response with route details

Agent → FastAPI
Returns AgentResponse with response_text, routes, costs

FastAPI → User
HTTP 200 with JSON response

text

**Total Time**: 8-15 seconds

## Deployment Architecture

### Local Development
localhost:8000 (FastAPI)
localhost:8501 (Streamlit)
SQLite file: ./logistics.db

text

### Production (Render.com)
https://logistics-agent-xyz.onrender.com (FastAPI)
PostgreSQL: internal Render database
Docker container with all dependencies
Environment variables from Render dashboard

text

## Security Considerations

### API Key Management
- OpenAI API key stored in environment variables
- Never committed to Git
- Rotated regularly

### Input Validation
- Sanitize all user inputs
- Validate coordinates are within reasonable bounds
- Check order counts don't exceed limits

### Rate Limiting
- Limit requests per user per minute
- Track API costs per query
- Alert if costs exceed threshold

### Data Privacy
- No personal customer data in PoC
- Synthetic datasets only
- GDPR-compliant for future production

## Scalability Considerations

### Current PoC Limitations
- Single instance (no horizontal scaling)
- SQLite (no concurrent writes)
- No caching layer
- Synchronous tool execution

### Future Improvements
- PostgreSQL with connection pooling
- Redis cache for distance matrices
- Celery for async task queue
- Load balancer for multiple instances
- Kubernetes deployment

## Monitoring & Logging

### Metrics to Track
- Request count per endpoint
- Average response time
- Tool call frequency
- Error rate
- OpenAI API cost per query

### Logging Strategy
- Structured logging (JSON format)
- Log levels: DEBUG, INFO, WARNING, ERROR
- Log all tool calls with parameters and results
- Log agent reasoning steps (for debugging)

### Health Checks
- `/health` endpoint returns service status
- Database connectivity check
- OpenAI API connectivity check
- OR-Tools availability check

---

**Document Status**: ✅ Complete
**Last Updated**: 2025-11-11
