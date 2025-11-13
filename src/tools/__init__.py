"""
Tools package for Logistics AI Agent.

This package contains all LangChain tools that the AI agent can invoke:
- Routing: Distance matrix calculations
- Database: Data access (orders, vehicles, depot)
- Cost: Economic analysis
- Optimization: OR-Tools VRP solver
- Scenario Analysis: What-if comparisons and sensitivity analysis
"""

from src.tools.routing_tool import calculate_distance_matrix
from src.tools.database_tool import (
    get_orders,
    get_vehicles,
    get_depot_info,
    get_database_stats
)
from src.tools.cost_tool import calculate_route_economics
from src.tools.optimizer_tool import solve_vrp
from src.tools.scenario_tool import compare_scenarios, analyze_parameter_sensitivity

# List of all available tools for the agent
ALL_TOOLS = [
    get_orders,
    get_vehicles,
    get_depot_info,
    calculate_distance_matrix,
    solve_vrp,
    calculate_route_economics,
    get_database_stats,
    compare_scenarios,
    analyze_parameter_sensitivity
]

__all__ = [
    "calculate_distance_matrix",
    "get_orders",
    "get_vehicles",
    "get_depot_info",
    "get_database_stats",
    "calculate_route_economics",
    "solve_vrp",
    "compare_scenarios",
    "analyze_parameter_sensitivity",
    "ALL_TOOLS",
]
