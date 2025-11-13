text
# Implementation Plan - Logistics AI Agent

## Overview

This document provides a step-by-step implementation guide for Copilot to build the Logistics AI Agent system.

## Prerequisites

- Python 3.10+ installed
- VS Code with GitHub Copilot (Claude Sonnet 4.5)
- OpenAI API key
- Git for version control

## Project Structure to Create

logistics-ai-agent/
├── .env # API keys (create, don't commit)
├── .env.example # Template for environment variables
├── .gitignore # Git ignore file
├── README.md # Project documentation
├── requirements.txt # Python dependencies
├── pyproject.toml # Poetry configuration (optional)
├── Dockerfile # Docker configuration
├── docker-compose.yml # Docker Compose for local dev
├── render.yaml # Render deployment config
│
├── data/ # Data directory
│ ├── solomon/ # Solomon benchmark files
│ │ ├── C101.txt
│ │ ├── R101.txt
│ │ └── RC101.txt
│ ├── orders.csv # Sample orders
│ ├── vehicles.csv # Sample vehicles
│ └── depot.csv # Depot information
│
├── src/ # Source code
│ ├── init.py
│ ├── main.py # FastAPI application entry point
│ ├── config.py # Configuration management
│ ├── database.py # Database connection and models
│ │
│ ├── agent/ # Agent logic
│ │ ├── init.py
│ │ ├── orchestrator.py # LangChain agent setup
│ │ ├── prompts.py # System prompts
│ │ └── state.py # State management
│ │
│ ├── tools/ # Tool implementations
│ │ ├── init.py
│ │ ├── routing_tool.py # Distance calculations
│ │ ├── optimizer_tool.py # OR-Tools VRP solver
│ │ ├── database_tool.py # Data access tools
│ │ └── cost_tool.py # Cost calculator
│ │
│ ├── models/ # Data models
│ │ ├── init.py
│ │ ├── order.py # Order model
│ │ ├── vehicle.py # Vehicle model
│ │ ├── route.py # Route model
│ │ └── query.py # Query/Response models
│ │
│ ├── data/ # Data processing
│ │ ├── init.py
│ │ ├── loader.py # Load Solomon/CSV data
│ │ ├── schema.py # Database schema
│ │ └── preprocessor.py # Data preprocessing
│ │
│ ├── api/ # API endpoints
│ │ ├── init.py
│ │ ├── routes.py # API route handlers
│ │ └── dependencies.py # FastAPI dependencies
│ │
│ └── utils/ # Utilities
│ ├── init.py
│ ├── logger.py # Logging configuration
│ ├── validators.py # Input validation
│ └── helpers.py # Helper functions
│
├── tests/ # Test files
│ ├── init.py
│ ├── conftest.py # Pytest configuration
│ ├── test_tools.py # Tool unit tests
│ ├── test_agent.py # Agent integration tests
│ ├── test_api.py # API endpoint tests
│ └── test_data.py # Data processing tests
│
├── notebooks/ # Jupyter notebooks
│ ├── 01_data_exploration.ipynb
│ ├── 02_tool_testing.ipynb
│ └── 03_agent_evaluation.ipynb
│
└── scripts/ # Utility scripts
├── setup_database.py # Initialize database
├── load_solomon_data.py # Load benchmark data
└── run_experiments.py # Run evaluation experiments

text

## Implementation Steps

### Phase 1: Project Setup (Day 1)

#### Step 1.1: Create Project Directory
mkdir logistics-ai-agent
cd logistics-ai-agent
git init

text

#### Step 1.2: Create Virtual Environment
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

text

#### Step 1.3: Create requirements.txt
Core dependencies
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0

LangChain and LLM
langchain==0.1.0
langchain-openai==0.0.5
openai==1.10.0

Optimization
ortools==9.8.0

Data handling
pandas==2.1.0
numpy==1.26.0
sqlalchemy==2.0.25
alembic==1.13.1

Utilities
httpx==0.26.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0

Optional
streamlit==1.30.0
plotly==5.18.0

Development
pytest==7.4.0
pytest-asyncio==0.23.0
pytest-cov==4.1.0
black==24.1.0
flake8==7.0.0
mypy==1.8.0

text

#### Step 1.4: Install Dependencies
pip install -r requirements.txt

text

#### Step 1.5: Create .env File
.env
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_TEMPERATURE=0.0
DATABASE_URL=sqlite:///./logistics.db
LOG_LEVEL=INFO
MAX_AGENT_ITERATIONS=5
AGENT_TIMEOUT=30

text

#### Step 1.6: Create .gitignore
.gitignore
venv/
pycache/
*.pyc
.env
.DS_Store
*.db
*.log
.pytest_cache/
.mypy_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/

text

### Phase 2: Data Layer (Day 2-3)

#### Step 2.1: Create Database Models (src/models/)

**File: src/models/order.py**
from pydantic import BaseModel, Field
from typing import Optional

class Order(BaseModel):
order_id: str
customer_id: str
demand: float = Field(..., gt=0)
service_time: int = Field(..., ge=0)
time_window_start: int = Field(..., ge=0, lt=1440)
time_window_end: int = Field(..., ge=0, le=1440)
latitude: float = Field(..., ge=-90, le=90)
longitude: float = Field(..., ge=-180, le=180)
is_cold_chain: bool = False
priority: str = "medium"

text

**File: src/models/vehicle.py**
Similar structure for Vehicle model
text

**File: src/models/route.py**
Similar structure for Route model
text

#### Step 2.2: Create Database Schema (src/database.py)
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./logistics.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class OrderDB(Base):
tablename = "orders"
# Define columns based on Order model

Similar for VehicleDB, DepotDB, RouteHistoryDB
text

#### Step 2.3: Create Data Loader (src/data/loader.py)
import pandas as pd
from pathlib import Path

def load_solomon_instance(filename: str) -> dict:
"""
Load Solomon VRPTW benchmark instance.

text
Args:
    filename: Path to Solomon .txt file

Returns:
    Dict with depot, customers, vehicle info
"""
# Implementation to parse Solomon format
pass
def load_csv_orders(filepath: str) -> pd.DataFrame:
"""Load orders from CSV file"""
return pd.read_csv(filepath)

text

#### Step 2.4: Download Solomon Benchmark Data
Create data/solomon/ directory
mkdir -p data/solomon

Download Solomon instances (C101, R101, RC101, etc.)
URL: https://www.sintef.no/projectweb/top/vrptw/solomon-benchmark/
Or use pre-packaged dataset from Kaggle
text

#### Step 2.5: Create Sample Data (scripts/create_sample_data.py)
import pandas as pd
import random

Generate sample orders.csv
orders = []
for i in range(50):
orders.append({
"order_id": f"O{i:03d}",
"customer_id": f"C{i:03d}",
"demand": random.uniform(5, 25),
"service_time": random.randint(5, 20),
"time_window_start": random.randint(480, 720),
"time_window_end": random.randint(780, 1080),
"latitude": random.uniform(40.0, 41.0),
"longitude": random.uniform(-74.5, -73.5),
"is_cold_chain": random.choice([True, False]),
"priority": random.choice(["low", "medium", "high"])
})

pd.DataFrame(orders).to_csv("data/orders.csv", index=False)

Similar for vehicles.csv, depot.csv
text

### Phase 3: Tool Implementation (Day 4-6)

#### Step 3.1: Routing Tool (src/tools/routing_tool.py)
from langchain.tools import tool
from typing import List, Tuple, Literal
import numpy as np
import json

@tool
def calculate_distance_matrix(
locations: List[Tuple[float, float]],
mode: Literal["euclidean", "manhattan", "osrm"] = "euclidean"
) -> str:
"""
Calculate distance and time matrices between locations.

text
Args:
    locations: List of (latitude, longitude) tuples
    mode: Distance calculation method

Returns:
    JSON string with distance_matrix (km) and time_matrix (minutes)
"""
if mode == "euclidean":
    n = len(locations)
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                lat1, lon1 = locations[i]
                lat2, lon2 = locations[j]
                # Approximate km distance
                dist = np.sqrt((lat2-lat1)**2 + (lon2-lon1)**2) * 111
                dist_matrix[i][j] = dist
    
    # Time matrix (assuming 50 km/h average speed)
    time_matrix = (dist_matrix / 50 * 60).astype(int)  # minutes
    
    return json.dumps({
        "distance_matrix": dist_matrix.tolist(),
        "time_matrix": time_matrix.tolist()
    })

# Implement other modes (OSRM, etc.)
raise NotImplementedError(f"Mode {mode} not implemented")
text

#### Step 3.2: Optimization Tool (src/tools/optimizer_tool.py)
from langchain.tools import tool
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import json

@tool
def solve_vrp(
order_ids: List[str],
vehicle_ids: List[str],
constraints: dict,
objective: str = "minimize_cost"
) -> str:
"""
Solve Vehicle Routing Problem using OR-Tools.

text
Args:
    order_ids: List of order IDs to route
    vehicle_ids: List of available vehicle IDs
    constraints: Dict with max_time, respect_time_windows, etc.
    objective: Optimization objective

Returns:
    JSON string with route assignments and KPIs
"""
# 1. Fetch order and vehicle data from database
# 2. Calculate distance matrix
# 3. Set up OR-Tools routing model
# 4. Add constraints (capacity, time windows)
# 5. Solve
# 6. Extract routes and costs
# 7. Return as JSON

# (Implementation details to be filled by Copilot)
pass
text

#### Step 3.3: Database Tool (src/tools/database_tool.py)
from langchain.tools import tool
from src.database import SessionLocal, OrderDB, VehicleDB
import json

@tool
def get_orders(
order_ids: Optional[List[str]] = None,
count: Optional[int] = None,
filters: Optional[dict] = None
) -> str:
"""Fetch order data from database"""
db = SessionLocal()
query = db.query(OrderDB)

text
if order_ids:
    query = query.filter(OrderDB.order_id.in_(order_ids))
if filters:
    if filters.get("is_cold_chain"):
        query = query.filter(OrderDB.is_cold_chain == True)
    # Add more filter logic

if count:
    query = query.limit(count)

orders = query.all()
db.close()

return json.dumps([order_to_dict(o) for o in orders])
@tool
def get_vehicles(vehicle_ids: Optional[List[str]] = None) -> str:
"""Fetch vehicle data from database"""
# Similar implementation
pass

text

#### Step 3.4: Cost Calculator Tool (src/tools/cost_tool.py)
from langchain.tools import tool
import json

@tool
def calculate_route_economics(
routes: List[dict],
fuel_price_per_liter: float = 1.5,
driver_wage_per_hour: float = 15.0
) -> str:
"""
Calculate costs, emissions, and economics for routes.

text
Args:
    routes: List of route dicts with distance_km, time_minutes
    fuel_price_per_liter: Current fuel price
    driver_wage_per_hour: Driver hourly wage

Returns:
    JSON with total_cost, breakdowns, emissions
"""
total_distance = sum(r["distance_km"] for r in routes)
total_time_hours = sum(r["time_minutes"] for r in routes) / 60

# Fuel consumption (assume 10 km/liter)
fuel_liters = total_distance / 10
fuel_cost = fuel_liters * fuel_price_per_liter

# Labor cost
labor_cost = total_time_hours * driver_wage_per_hour

# Fixed costs (vehicle usage)
fixed_cost = len(routes) * 50  # $50 per vehicle per day

# Emissions (assume 2.5 kg CO2 per liter)
emissions_kg = fuel_liters * 2.5

return json.dumps({
    "total_cost": fuel_cost + labor_cost + fixed_cost,
    "fuel_cost": fuel_cost,
    "labor_cost": labor_cost,
    "fixed_cost": fixed_cost,
    "total_distance_km": total_distance,
    "total_time_hours": total_time_hours,
    "emissions_kg": emissions_kg,
    "per_route_breakdown": [...]
})
text

### Phase 4: Agent Implementation (Day 7-9)

#### Step 4.1: Agent Prompts (src/agent/prompts.py)
SYSTEM_PROMPT = """You are an expert logistics planning assistant...
(Full prompt from TECHNICAL_SPECIFICATION.md)
"""

HUMAN_PROMPT_TEMPLATE = """User query: {query}

Current context:

Available orders: {order_count}

Available vehicles: {vehicle_count}

Depot location: {depot_location}

Please help optimize this logistics request.
"""

text

#### Step 4.2: Agent Orchestrator (src/agent/orchestrator.py)
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.tools import (
calculate_distance_matrix,
solve_vrp,
get_orders,
get_vehicles,
get_depot_info,
calculate_route_economics
)
from src.agent.prompts import SYSTEM_PROMPT
import os

def create_agent() -> AgentExecutor:
"""Create and configure the LangChain agent"""

text
# Initialize LLM
llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
    temperature=float(os.getenv("OPENAI_TEMPERATURE", 0.0)),
    api_key=os.getenv("OPENAI_API_KEY")
)

# Define tools
tools = [
    calculate_distance_matrix,
    solve_vrp,
    get_orders,
    get_vehicles,
    get_depot_info,
    calculate_route_economics
]

# Create prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

# Create agent
agent = create_openai_functions_agent(llm, tools, prompt)

# Create executor
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=int(os.getenv("MAX_AGENT_ITERATIONS", 5)),
    max_execution_time=float(os.getenv("AGENT_TIMEOUT", 30)),
    return_intermediate_steps=True,
    handle_parsing_errors=True
)

return agent_executor
Singleton instance
agent_executor = create_agent()

text

### Phase 5: API Implementation (Day 10-11)

#### Step 5.1: FastAPI App (src/main.py)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.agent.orchestrator import agent_executor
from src.models.query import AgentQuery, AgentResponse
import time
import logging

app = FastAPI(
title="Logistics AI Agent API",
description="AI-powered logistics planning and optimization",
version="0.1.0"
)

CORS middleware
app.add_middleware(
CORSMiddleware,
allow_origins=[""],
allow_credentials=True,
allow_methods=[""],
allow_headers=["*"]
)

@app.get("/")
async def root():
return {"message": "Logistics AI Agent API", "status": "online"}

@app.get("/health")
async def health():
return {
"status": "healthy",
"timestamp": time.time()
}

@app.post("/ask", response_model=AgentResponse)
async def ask_agent(query: AgentQuery):
"""
Main endpoint for agent queries.

text
Example:
    POST /ask
    {
        "query": "Route 20 deliveries with 3 vehicles, minimize cost",
        "max_iterations": 5,
        "include_explanation": true
    }
"""
try:
    start_time = time.time()
    
    # Execute agent
    result = agent_executor.invoke({"input": query.query})
    
    execution_time = time.time() - start_time
    
    # Parse result and create response
    response = AgentResponse(
        response_text=result["output"],
        routes=[],  # Parse from result
        total_cost=0.0,  # Parse from result
        total_emissions=0.0,  # Parse from result
        execution_time_seconds=execution_time,
        tools_called=[step.tool for step in result.get("intermediate_steps", [])],
        metadata={"iterations": len(result.get("intermediate_steps", []))}
    )
    
    return response
    
except Exception as e:
    logging.error(f"Agent execution failed: {e}")
    raise HTTPException(status_code=500, detail=str(e))
@app.post("/solve_vrp_direct")
async def solve_vrp_direct(request: dict):
"""Direct VRP solving (baseline comparison)"""
# Implementation
pass

if name == "main":
import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8000)

text

### Phase 6: Testing (Day 12-13)

#### Step 6.1: Create Tests (tests/test_tools.py)
import pytest
from src.tools.routing_tool import calculate_distance_matrix
from src.tools.optimizer_tool import solve_vrp

def test_distance_matrix():
locations = [(40.7128, -74.0060), (40.7580, -73.9855)]
result = calculate_distance_matrix.invoke({"locations": locations})
assert "distance_matrix" in result
assert "time_matrix" in result

def test_vrp_solver():
# Test with small instance
result = solve_vrp.invoke({
"order_ids": ["O001", "O002", "O003"],
"vehicle_ids": ["V001"],
"constraints": {},
"objective": "minimize_distance"
})
assert "routes" in result

text

#### Step 6.2: Integration Tests (tests/test_api.py)
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_endpoint():
response = client.get("/health")
assert response.status_code == 200
assert response.json()["status"] == "healthy"

def test_ask_endpoint():
response = client.post("/ask", json={
"query": "Route 5 deliveries with 1 vehicle",
"max_iterations": 3
})
assert response.status_code == 200
assert "response_text" in response.json()

text

### Phase 7: Deployment (Day 14-15)

#### Step 7.1: Create Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

text

#### Step 7.2: Create render.yaml
services:

type: web
name: logistics-agent-api
env: python
buildCommand: pip install -r requirements.txt
startCommand: uvicorn src.main:app --host 0.0.0.0 --port $PORT
envVars:

key: OPENAI_API_KEY
sync: false

key: DATABASE_URL
fromDatabase:
name: logistics-db
property: connectionString

text

#### Step 7.3: Deploy to Render
1. Push code to GitHub
2. Connect Render to repository
3. Add environment variables
4. Deploy

---

## Checklist for Copilot

- [ ] Create project structure
- [ ] Install dependencies
- [ ] Set up environment variables
- [ ] Create database models
- [ ] Implement data loaders
- [ ] Download/create sample data
- [ ] Implement routing tool
- [ ] Implement optimization tool (OR-Tools)
- [ ] Implement database tool
- [ ] Implement cost calculator tool
- [ ] Create agent prompts
- [ ] Build agent orchestrator
- [ ] Create FastAPI endpoints
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Create Dockerfile
- [ ] Test locally
- [ ] Deploy to Render

---

**Document Status**: ✅ Complete
**Last Updated**: 2025-11-11