# Logistics AI Agent

An intelligent AI agent system for transportation and logistics optimization that uses Large Language Models (LLMs) to orchestrate specialized optimization tools.

## Overview

This project demonstrates a novel application of LLM-based tool-use agents in the logistics domain. The agent understands natural language requests from logistics managers and returns actionable routing plans with cost/time/emissions analysis.

## Features

- **Natural Language Interface**: Submit routing queries in plain English
- **Intelligent Tool Orchestration**: LLM automatically selects and chains appropriate optimization tools
- **Vehicle Routing Optimization**: Solves VRPTW (Vehicle Routing Problem with Time Windows) using OR-Tools
- **Economic Analysis**: Calculates costs, emissions, and time for all routes
- **Explainable AI**: Generates human-readable explanations for routing decisions
- **REST API**: FastAPI backend with interactive documentation
- **Research-Ready**: Benchmarking against Solomon VRPTW instances

## Architecture

```
┌─────────────────────────────────────────┐
│         Interface Layer                 │
│  FastAPI REST API | Streamlit UI | CLI  │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────┴───────────────────────┐
│    Agent Orchestration Layer            │
│  LangChain AgentExecutor + OpenAI GPT-4 │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────┴───────────────────────┐
│       Tool Execution Layer              │
│  Routing | Optimizer | Database | Cost  │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────┴───────────────────────┐
│          Data Layer                     │
│  SQLite Database | Solomon Benchmark    │
└─────────────────────────────────────────┘
```

## Technology Stack

- **LLM Provider**: OpenAI GPT-4
- **Agent Framework**: LangChain
- **Web Framework**: FastAPI
- **Optimization**: Google OR-Tools
- **Database**: SQLite (upgradeable to PostgreSQL)
- **Data Processing**: Pandas, NumPy
- **Testing**: Pytest
- **Deployment**: Docker, Render.com

## Quick Start

### Prerequisites

- Python 3.10 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- Git

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd Agent
```

2. **Create virtual environment**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-actual-key-here
```

5. **Initialize the database**
```bash
python scripts/setup_database.py
```

6. **Load sample data**
```bash
python scripts/load_solomon_data.py
```

### Running the Application

**Start the FastAPI server:**
```bash
uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`

**Access the interactive documentation:**
Open your browser to `http://localhost:8000/docs`

**Test with a sample query:**
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Route 20 deliveries with 3 vehicles, minimize cost"
  }'
```

## Usage Examples

### Example 1: Basic Routing
```python
import requests

response = requests.post("http://localhost:8000/ask", json={
    "query": "Route 10 deliveries with 2 vehicles, minimize distance"
})

print(response.json()["response_text"])
```

### Example 2: Cold-Chain Constraints
```python
response = requests.post("http://localhost:8000/ask", json={
    "query": "Route 20 deliveries with 3 vehicles. All cold-chain items must be delivered within 2 hours. Minimize total cost."
})
```

### Example 3: Time Window Constraints
```python
response = requests.post("http://localhost:8000/ask", json={
    "query": "Route 15 deliveries avoiding downtown between 8 AM and 6 PM. Use maximum 4 vehicles."
})
```

## Project Structure

```
Agent/
├── data/                   # Data files
│   ├── solomon/           # Solomon benchmark instances
│   ├── orders.csv         # Sample orders
│   ├── vehicles.csv       # Sample vehicles
│   └── depot.csv          # Depot information
├── src/                   # Source code
│   ├── agent/            # Agent orchestration
│   ├── tools/            # Tool implementations
│   ├── models/           # Data models
│   ├── data/             # Data processing
│   ├── api/              # API endpoints
│   └── utils/            # Utilities
├── tests/                # Test files
├── notebooks/            # Jupyter notebooks
├── scripts/              # Utility scripts
├── requirements.txt      # Python dependencies
├── .env.example          # Environment template
└── README.md            # This file
```

## Development

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_tools.py
```

### Code Formatting
```bash
# Format code with black
black src/ tests/

# Lint with flake8
flake8 src/ tests/

# Type checking with mypy
mypy src/
```

## API Endpoints

### Main Endpoints

- `POST /ask` - Submit natural language query to agent
- `POST /solve_vrp_direct` - Direct VRP solving (baseline comparison)
- `GET /orders` - Fetch orders from database
- `GET /vehicles` - Fetch available vehicles
- `GET /health` - Health check
- `GET /stats` - API usage statistics

See full API documentation at `/docs` when server is running.

## Research & Evaluation

This project is designed for academic research. See the evaluation methodology:

### Benchmarks
- Solomon VRPTW benchmark instances (C, R, RC classes)
- Comparison with OR-Tools direct solver
- Baseline heuristics (greedy, random)

### Metrics
- Solution quality (optimality gap, total cost, distance)
- Computational efficiency (response time, API costs)
- Explainability (human evaluation ratings)
- Robustness (edge case handling)

### Running Experiments
```bash
python scripts/run_experiments.py --instances data/solomon/ --output results/
```

## Deployment

### Docker

```bash
# Build image
docker build -t logistics-agent .

# Run container
docker run -p 8000:8000 --env-file .env logistics-agent
```

### Render.com

1. Push code to GitHub
2. Create new Web Service on Render
3. Connect repository
4. Add environment variables (OPENAI_API_KEY, etc.)
5. Deploy

## Contributing

This is a research project. Contributions are welcome for:

- Additional optimization algorithms
- New tool implementations
- Enhanced evaluation metrics
- Bug fixes and improvements

## License

MIT License - See LICENSE file for details

## Citation

If you use this project in your research, please cite:

```bibtex
@software{logistics_ai_agent_2025,
  title={Logistics AI Agent: LLM-Based Tool Orchestration for Transportation Optimization},
  author={Your Name},
  year={2025},
  url={https://github.com/yourusername/logistics-ai-agent}
}
```

## Acknowledgments

- Solomon VRPTW benchmark dataset
- Google OR-Tools team
- LangChain community
- OpenAI API

## Contact

For questions or collaboration:
- Email: your.email@example.com
- GitHub Issues: [Create an issue](https://github.com/yourusername/logistics-ai-agent/issues)

## Roadmap

### PoC (Current)
- [x] Basic agent setup
- [x] OR-Tools integration
- [x] FastAPI endpoints
- [ ] Solomon benchmark evaluation

### Future Enhancements
- [ ] Multi-depot routing
- [ ] Real-time dynamic rerouting
- [ ] Web UI (Streamlit)
- [ ] Integration with real TMS systems
- [ ] Support for other LLMs (Claude, Gemini)
- [ ] Multi-modal logistics (rail, air, sea)

---

**Version**: 0.1.0
**Status**: Development
**Last Updated**: 2025-11-12
