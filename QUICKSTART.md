# Logistics AI Agent - Quick Start Guide

Welcome to the Logistics AI Agent! This guide will help you get started quickly.

## Prerequisites

✅ **Already Done:**
- Python 3.10+ installed
- All dependencies installed (ortools, langchain, fastapi, etc.)
- Database initialized with 50 sample orders and 10 vehicles
- OpenAI API key configured in `.env`

## Starting the API Server

### Option 1: Using the start script (Recommended)

```bash
python scripts/start_api.py
```

### Option 2: Using uvicorn directly

```bash
uvicorn src.main:app --reload
```

### Option 3: Enable debug mode

```bash
python scripts/start_api.py --reload --debug
```

The server will start at: **http://localhost:8000**

## Accessing the API

### Interactive Documentation

Open your browser and navigate to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Quick Test

1. **Health Check:**
```bash
curl http://localhost:8000/health
```

2. **Get Statistics:**
```bash
curl http://localhost:8000/stats
```

## Using the Agent

### Simple Query

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How many orders and vehicles do we have available?"
  }'
```

### Routing Query

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Route 10 deliveries with 2 vehicles, minimize cost",
    "max_iterations": 5,
    "include_explanation": true
  }'
```

### Complex Query with Context

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Route 20 deliveries with 3 vehicles. All cold-chain items must be delivered within 2 hours. Minimize total cost.",
    "context": {
      "fuel_price": 3.50,
      "driver_wage": 18.00
    }
  }'
```

## Running Tests

### Test All Tools

```bash
python scripts/test_tools.py
```

### Test API Endpoints

```bash
# Start the server first in one terminal:
python scripts/start_api.py

# Then in another terminal, run tests:
python scripts/test_agent_query.py
```

## Example Queries to Try

1. **Database Queries:**
   - "Show me all cold-chain orders"
   - "How many vehicles with capacity over 200 units do we have?"
   - "What's the total demand across all orders?"

2. **Simple Routing:**
   - "Route 5 deliveries with 1 vehicle"
   - "Find the shortest route for 10 deliveries using 2 vehicles"
   - "What's the cheapest way to deliver 15 orders?"

3. **Complex Routing:**
   - "Route 20 deliveries with 3 vehicles, minimize emissions"
   - "Assign all high-priority orders to the fastest vehicles"
   - "Create a routing plan that completes all deliveries before 5 PM"

4. **Cost Analysis:**
   - "Calculate the cost difference between using 2 vs 3 vehicles for 10 deliveries"
   - "What would the emissions be if we doubled the number of deliveries?"
   - "Compare the cost of minimizing distance vs minimizing time"

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/stats` | GET | Usage statistics |
| `/tools` | GET | List available tools |
| `/ask` | POST | Agent query (natural language) |
| `/solve_vrp_direct` | POST | Direct VRP solving (structured) |

## Troubleshooting

### Server Won't Start

**Error:** `ModuleNotFoundError: No module named 'ortools'`
**Solution:**
```bash
pip install ortools pandas numpy langchain langchain-openai fastapi uvicorn
```

**Error:** `No OpenAI API key found`
**Solution:** Check your `.env` file has:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

### Database Errors

**Error:** `No orders found in database`
**Solution:** Reinitialize database:
```bash
python scripts/setup_database.py --reset --load-data --yes
```

### Agent Timeout

**Error:** `Agent execution timed out`
**Solution:** Increase timeout in `.env`:
```
AGENT_TIMEOUT=60
```

## Next Steps

1. **Try the Interactive Docs**: http://localhost:8000/docs
   - Explore all endpoints
   - Try different queries
   - See request/response schemas

2. **Run Experiments**: Use the test scripts to understand how the agent works

3. **Read the Documentation**:
   - `PROJECT_OVERVIEW.md` - Project goals and scope
   - `TECHNICAL_SPECIFICATION.md` - Architecture details
   - `API_SPECIFICATION.md` - API reference
   - `IMPLEMENTATION_PLAN.md` - Development guide

4. **Customize**:
   - Add more orders: Edit `data/orders.csv`
   - Add vehicles: Edit `data/vehicles.csv`
   - Adjust costs: Modify `.env` parameters
   - Reload data: `python scripts/setup_database.py --reset --load-data --yes`

## Performance Notes

- **Simple queries** (database stats): <1 second
- **Routing queries** (5-10 orders): 10-20 seconds
- **Complex routing** (20+ orders): 20-40 seconds
- **Timeout limit**: 30 seconds (configurable)

The agent needs time for:
1. LLM reasoning (5-10 seconds)
2. OR-Tools solving (5-20 seconds depending on problem size)
3. Tool orchestration (2-5 seconds)

## Support

For issues or questions:
- Check the logs in the terminal where the server is running
- Review `TECHNICAL_SPECIFICATION.md` for detailed architecture
- Test tools individually: `python scripts/test_tools.py`

---

**Happy Routing! 🚚**
