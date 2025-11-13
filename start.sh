#!/bin/bash
# Start script for Render deployment

# Use PORT from environment or default to 10000
PORT=${PORT:-10000}

# Start uvicorn server
uvicorn src.main:app --host 0.0.0.0 --port $PORT
