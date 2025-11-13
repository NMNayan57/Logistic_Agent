"""
Scenario Comparison Tool for What-If Analysis

This tool allows users to compare multiple what-if scenarios for the same
routing problem with different parameters (fuel prices, vehicle counts,
speed reductions due to traffic, etc.).
"""

import json
from typing import Dict, Any, List, Optional
from langchain.tools import tool
import logging

from .optimizer_tool import solve_vrp
from .cost_tool import calculate_route_economics

logger = logging.getLogger(__name__)


@tool
def compare_scenarios(base_order_ids: str, base_vehicle_ids: str, scenarios: str) -> str:
    """
    Compare multiple what-if scenarios for vehicle routing optimization.

    This tool runs the VRP solver with different parameters to show how
    changes in constraints, costs, or resources affect the optimal solution.

    Args:
        base_order_ids: JSON string of order IDs (e.g., '["O001", "O002"]')
        base_vehicle_ids: JSON string of vehicle IDs (e.g., '["V001", "V002"]')
        scenarios: JSON string defining scenarios to compare. Each scenario
                  can override these parameters:
                  - fuel_price_per_liter: float (default: 1.5)
                  - driver_wage_per_hour: float (default: 15.0)
                  - avg_speed_reduction: float 0-1 (traffic impact, default: 0)
                  - max_route_time_minutes: int (default: 480)
                  - num_vehicles: int (override vehicle count)

    Example:
        scenarios = {
            "baseline": {
                "description": "Current conditions"
            },
            "fuel_spike": {
                "description": "25% fuel price increase",
                "fuel_price_per_liter": 1.875
            },
            "rush_hour": {
                "description": "Heavy traffic (20% slower)",
                "avg_speed_reduction": 0.2
            },
            "add_vehicle": {
                "description": "Add one more vehicle",
                "num_vehicles": 3
            }
        }

    Returns:
        JSON string with comparison table showing costs, times, distances,
        emissions, and key differences for each scenario.
    """
    try:
        # Parse inputs
        order_ids = json.loads(base_order_ids)
        vehicle_ids = json.loads(base_vehicle_ids)
        scenario_configs = json.loads(scenarios)

        logger.info(f"Comparing {len(scenario_configs)} scenarios for {len(order_ids)} orders")

        # Default parameters
        DEFAULT_PARAMS = {
            "fuel_price_per_liter": 1.5,
            "driver_wage_per_hour": 15.0,
            "avg_speed_reduction": 0.0,
            "max_route_time_minutes": 480,
            "num_vehicles": len(vehicle_ids)
        }

        results = {}

        # Run VRP for each scenario
        for scenario_name, scenario_config in scenario_configs.items():
            description = scenario_config.get("description", scenario_name)

            # Merge with defaults
            params = {**DEFAULT_PARAMS, **scenario_config}

            # Handle vehicle count override
            if params["num_vehicles"] != len(vehicle_ids):
                # For simplicity, duplicate last vehicle if adding, or truncate if removing
                scenario_vehicle_ids = vehicle_ids.copy()
                if params["num_vehicles"] > len(vehicle_ids):
                    # Add more vehicles (clone last vehicle)
                    for _ in range(params["num_vehicles"] - len(vehicle_ids)):
                        scenario_vehicle_ids.append(vehicle_ids[-1])
                else:
                    # Use fewer vehicles
                    scenario_vehicle_ids = vehicle_ids[:params["num_vehicles"]]
            else:
                scenario_vehicle_ids = vehicle_ids

            # Solve VRP for this scenario
            # Prepare constraints
            constraints = {
                "max_route_time_minutes": params["max_route_time_minutes"],
                "avg_speed_reduction": params["avg_speed_reduction"]
            }

            vrp_result = json.loads(solve_vrp.invoke({
                "order_ids": json.dumps(order_ids),
                "vehicle_ids": json.dumps(scenario_vehicle_ids),
                "constraints": json.dumps(constraints),
                "objective": "minimize_distance"
            }))

            if vrp_result.get("status") == "error":
                results[scenario_name] = {
                    "description": description,
                    "status": "error",
                    "error": vrp_result.get("message", "Unknown error")
                }
                continue

            # Apply speed reduction to route times (if applicable)
            routes = vrp_result.get("routes", [])
            speed_reduction = params["avg_speed_reduction"]

            if speed_reduction > 0:
                # Speed reduction increases travel time
                # If speed is reduced by X%, time increases by X/(1-X)%
                # Example: 30% speed reduction → 1/(1-0.3) = 1.43x time (43% increase)
                time_multiplier = 1 / (1 - speed_reduction)

                adjusted_total_time = 0
                for route in routes:
                    original_time = route.get("time_minutes", 0)
                    adjusted_time = original_time * time_multiplier
                    route["time_minutes"] = adjusted_time
                    adjusted_total_time += adjusted_time

                # Update total time in VRP result
                vrp_result["total_time_minutes"] = adjusted_total_time

            # Calculate economics with scenario-specific parameters and adjusted times
            routes_json = json.dumps(routes)
            economics = json.loads(calculate_route_economics.invoke({
                "routes": routes_json,
                "fuel_price_per_liter": params["fuel_price_per_liter"],
                "driver_wage_per_hour": params["driver_wage_per_hour"]
            }))

            # Store results
            results[scenario_name] = {
                "description": description,
                "status": "success",
                "parameters": {
                    "fuel_price": params["fuel_price_per_liter"],
                    "driver_wage": params["driver_wage_per_hour"],
                    "speed_reduction": params["avg_speed_reduction"],
                    "max_time": params["max_route_time_minutes"],
                    "num_vehicles": params["num_vehicles"]
                },
                "metrics": {
                    "total_cost_usd": economics.get("total_cost_usd", 0),
                    "total_distance_km": vrp_result.get("total_distance_km", 0),
                    "total_time_minutes": vrp_result.get("total_time_minutes", 0),
                    "total_emissions_kg": economics.get("total_emissions_kg", 0),
                    "fuel_cost_usd": economics.get("fuel_cost_usd", 0),
                    "labor_cost_usd": economics.get("labor_cost_usd", 0),
                    "num_routes": len(vrp_result.get("routes", [])),
                    "solver_status": vrp_result.get("solver_status", "unknown")
                },
                "routes": vrp_result.get("routes", [])
            }

        # Calculate differences from baseline
        if "baseline" in results and results["baseline"]["status"] == "success":
            baseline_cost = results["baseline"]["metrics"]["total_cost_usd"]
            baseline_time = results["baseline"]["metrics"]["total_time_minutes"]
            baseline_emissions = results["baseline"]["metrics"]["total_emissions_kg"]

            for scenario_name in results:
                if scenario_name != "baseline" and results[scenario_name]["status"] == "success":
                    scenario = results[scenario_name]

                    # Calculate cost percentage delta (handle zero baseline gracefully)
                    cost_delta = scenario["metrics"]["total_cost_usd"] - baseline_cost
                    if baseline_cost > 0:
                        cost_delta_percent = round((cost_delta / baseline_cost * 100), 1)
                    else:
                        # If baseline cost is 0, show absolute change only
                        cost_delta_percent = 0.0 if cost_delta == 0 else None

                    scenario["differences"] = {
                        "cost_delta_usd": round(cost_delta, 2),
                        "cost_delta_percent": cost_delta_percent,
                        "time_delta_minutes": round(scenario["metrics"]["total_time_minutes"] - baseline_time, 1),
                        "emissions_delta_kg": round(scenario["metrics"]["total_emissions_kg"] - baseline_emissions, 2)
                    }

        # Summary
        summary = {
            "total_scenarios": len(scenario_configs),
            "successful_scenarios": sum(1 for r in results.values() if r.get("status") == "success"),
            "comparison_results": results
        }

        return json.dumps(summary, indent=2)

    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON input: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"status": "error", "message": error_msg})
    except Exception as e:
        error_msg = f"Scenario comparison failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return json.dumps({"status": "error", "message": error_msg})


@tool
def analyze_parameter_sensitivity(order_ids: str, vehicle_ids: str, parameter: str,
                                   min_value: float, max_value: float, steps: int = 5) -> str:
    """
    Analyze how a single parameter affects routing outcomes across a range.

    This tool performs sensitivity analysis by varying one parameter while
    keeping others constant, useful for understanding optimization trade-offs.

    Args:
        order_ids: JSON string of order IDs
        vehicle_ids: JSON string of vehicle IDs
        parameter: Parameter to vary. Options:
                  - "fuel_price" ($/liter)
                  - "driver_wage" ($/hour)
                  - "speed_reduction" (0-1 fraction)
                  - "max_time" (minutes)
        min_value: Minimum value for parameter range
        max_value: Maximum value for parameter range
        steps: Number of data points to calculate (default: 5)

    Returns:
        JSON string with array of results showing how the parameter
        affects total cost, time, and other metrics.

    Example:
        Analyze fuel price impact from $1.00 to $2.50 in 5 steps:
        analyze_parameter_sensitivity(
            '["O001", "O002", "O003"]',
            '["V001", "V002"]',
            "fuel_price",
            1.0, 2.5, 5
        )
    """
    try:
        import numpy as np

        order_ids_list = json.loads(order_ids)
        vehicle_ids_list = json.loads(vehicle_ids)

        # Generate parameter values
        param_values = np.linspace(min_value, max_value, steps)

        results = []

        for value in param_values:
            # Build scenario config
            scenario_config = {}

            if parameter == "fuel_price":
                scenario_config["fuel_price_per_liter"] = float(value)
            elif parameter == "driver_wage":
                scenario_config["driver_wage_per_hour"] = float(value)
            elif parameter == "speed_reduction":
                scenario_config["avg_speed_reduction"] = float(value)
            elif parameter == "max_time":
                scenario_config["max_route_time_minutes"] = int(value)
            else:
                return json.dumps({
                    "status": "error",
                    "message": f"Unknown parameter: {parameter}"
                })

            # Run scenario
            scenarios_input = {f"{parameter}_{value:.2f}": scenario_config}
            comparison_result = json.loads(compare_scenarios(
                json.dumps(order_ids_list),
                json.dumps(vehicle_ids_list),
                json.dumps(scenarios_input)
            ))

            if comparison_result.get("comparison_results"):
                scenario_key = list(comparison_result["comparison_results"].keys())[0]
                scenario_result = comparison_result["comparison_results"][scenario_key]

                if scenario_result.get("status") == "success":
                    results.append({
                        "parameter_value": float(value),
                        "total_cost_usd": scenario_result["metrics"]["total_cost_usd"],
                        "total_time_minutes": scenario_result["metrics"]["total_time_minutes"],
                        "total_distance_km": scenario_result["metrics"]["total_distance_km"],
                        "total_emissions_kg": scenario_result["metrics"]["total_emissions_kg"]
                    })

        summary = {
            "parameter": parameter,
            "range": {"min": float(min_value), "max": float(max_value)},
            "steps": steps,
            "results": results,
            "insights": _generate_sensitivity_insights(results, parameter)
        }

        return json.dumps(summary, indent=2)

    except Exception as e:
        error_msg = f"Sensitivity analysis failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return json.dumps({"status": "error", "message": error_msg})


def _generate_sensitivity_insights(results: List[Dict], parameter: str) -> Dict[str, Any]:
    """Generate insights from sensitivity analysis results."""
    if len(results) < 2:
        return {"message": "Insufficient data for insights"}

    costs = [r["total_cost_usd"] for r in results]
    times = [r["total_time_minutes"] for r in results]

    cost_change = costs[-1] - costs[0]
    cost_percent = (cost_change / costs[0] * 100) if costs[0] > 0 else 0

    time_change = times[-1] - times[0]

    return {
        "cost_impact": {
            "absolute_change_usd": round(cost_change, 2),
            "percent_change": round(cost_percent, 1),
            "sensitivity": "high" if abs(cost_percent) > 20 else "moderate" if abs(cost_percent) > 10 else "low"
        },
        "time_impact": {
            "absolute_change_minutes": round(time_change, 1),
            "significant": abs(time_change) > 30
        },
        "recommendation": _get_sensitivity_recommendation(parameter, cost_percent, time_change)
    }


def _get_sensitivity_recommendation(parameter: str, cost_percent: float, time_change: float) -> str:
    """Generate actionable recommendation based on sensitivity analysis."""
    if parameter == "fuel_price":
        if abs(cost_percent) > 20:
            return "Fuel costs are highly sensitive. Consider fuel hedging contracts or route optimization to minimize distance."
        else:
            return "Fuel price changes have moderate impact. Current routing efficiency is good."

    elif parameter == "driver_wage":
        if abs(cost_percent) > 15:
            return "Labor costs dominate. Focus on minimizing total route time and number of vehicles needed."
        else:
            return "Labor costs are well-controlled. Current vehicle utilization is efficient."

    elif parameter == "speed_reduction":
        if time_change > 60:
            return "Traffic has major impact on delivery times. Consider earlier dispatch times or alternate routes."
        else:
            return "Routes are resilient to moderate traffic delays."

    return "Analysis complete. Review results for insights."
