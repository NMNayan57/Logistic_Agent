"""
Start the Logistics AI Agent API server.

This script starts the FastAPI server with uvicorn.

Usage:
    python scripts/start_api.py [--host HOST] [--port PORT] [--reload]
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import uvicorn
from src.config import get_settings


def main():
    """Start the API server."""
    parser = argparse.ArgumentParser(
        description="Start Logistics AI Agent API server"
    )
    parser.add_argument(
        "--host",
        default=None,
        help="Host to bind to (default: from config)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Port to bind to (default: from config)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload on code changes"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )

    args = parser.parse_args()

    # Get settings
    settings = get_settings()

    # Determine host and port
    host = args.host or settings.api_host
    port = args.port or settings.api_port
    reload = args.reload or settings.debug
    log_level = "debug" if args.debug else settings.log_level.lower()

    print("=" * 60)
    print("  Logistics AI Agent API Server")
    print("=" * 60)
    print(f"  Host: {host}")
    print(f"  Port: {port}")
    print(f"  Model: {settings.openai_model}")
    print(f"  Reload: {reload}")
    print(f"  Log Level: {log_level}")
    print("=" * 60)
    print()
    print(f"Starting server at http://{host}:{port}")
    print(f"API Documentation: http://{host}:{port}/docs")
    print()

    # Start server
    uvicorn.run(
        "src.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level
    )


if __name__ == "__main__":
    main()
