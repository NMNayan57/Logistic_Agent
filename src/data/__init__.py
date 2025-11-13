"""
Data processing package for Logistics AI Agent.

This package contains modules for loading and processing logistics data
from various sources including Solomon benchmarks and CSV files.
"""

from src.data.loader import SolomonLoader, CSVLoader, load_all_solomon_instances

__all__ = [
    "SolomonLoader",
    "CSVLoader",
    "load_all_solomon_instances",
]
