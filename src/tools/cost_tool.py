"""
Cost calculator tool for route economics analysis.

This module provides tools to calculate costs, emissions, and economic
metrics for vehicle routes.
"""

from typing import List, Dict, Any
import json
from langchain.tools import tool
from src.utils.logger import setup_logger
from src.config import get_settings

logger = setup_logger(__name__)


@tool
def calculate_route_economics(
    routes: str,
    fuel_price_per_liter: float = 1.5,
    driver_wage_per_hour: float = 15.0
) -> str:
    """
    Calculate costs, emissions, and economics for vehicle routes.

    This tool analyzes the economic performance of routing solutions,
    including fuel costs, labor costs, and environmental impact.

    Args:
        routes: JSON string of route data.
               Format: [
                   {
                       "vehicle_id": "V001",
                       "distance_km": 85.3,
                       "time_minutes": 245,
                       "num_stops": 8,
                       "vehicle_info": {
                           "cost_per_km": 2.50,
                           "fixed_cost": 50.0,
                           "emissions_factor": 0.25
                       }
                   },
                   ...
               ]
        fuel_price_per_liter: Current fuel price (USD per liter).
                             Default: 1.5
        driver_wage_per_hour: Driver hourly wage (USD per hour).
                             Default: 15.0

    Returns:
        JSON string with cost breakdown and totals.
        Format: {
            "total_cost": 327.50,
            "fuel_cost": 147.00,
            "labor_cost": 180.00,
            "fixed_cost": 150.00,
            "variable_cost": 177.50,
            "total_distance_km": 245.0,
            "total_time_hours": 12.5,
            "total_emissions_kg": 61.25,
            "cost_per_km": 1.34,
            "cost_per_delivery": 16.38,
            "per_route_breakdown": [...]
        }

    Example:
        >>> routes_json = '[{"vehicle_id": "V001", "distance_km": 100, ...}]'
        >>> result = calculate_route_economics.invoke({
        ...     "routes": routes_json,
        ...     "fuel_price_per_liter": 1.5
        ... })
    """
    logger.info("Calculating route economics")

    try:
        # Parse routes
        routes_list = json.loads(routes)

        if not routes_list:
            return json.dumps({
                "error": "No routes provided",
                "total_cost": 0.0
            })

        logger.debug(f"Analyzing {len(routes_list)} routes")

        # Initialize totals
        total_distance = 0.0
        total_time_minutes = 0.0
        total_fuel_cost = 0.0
        total_labor_cost = 0.0
        total_fixed_cost = 0.0
        total_variable_cost = 0.0
        total_emissions = 0.0
        total_deliveries = 0

        per_route_breakdown = []

        # Calculate for each route
        for route in routes_list:
            vehicle_id = route.get("vehicle_id", "Unknown")
            distance_km = route.get("distance_km", 0.0)
            time_minutes = route.get("time_minutes", 0.0)
            num_stops = route.get("num_stops", 0)

            # Get vehicle info
            vehicle_info = route.get("vehicle_info", {})
            cost_per_km = vehicle_info.get("cost_per_km", 2.50)
            fixed_cost = vehicle_info.get("fixed_cost", 50.0)
            emissions_factor = vehicle_info.get("emissions_factor", 0.25)

            # Calculate route-specific costs
            # Fuel cost (assuming 10 km/liter average efficiency)
            fuel_consumption_liters = distance_km / 10.0
            route_fuel_cost = fuel_consumption_liters * fuel_price_per_liter

            # Labor cost
            time_hours = time_minutes / 60.0
            route_labor_cost = time_hours * driver_wage_per_hour

            # Variable cost (distance-based)
            route_variable_cost = distance_km * cost_per_km

            # Total route cost
            route_total_cost = route_fuel_cost + route_labor_cost + fixed_cost + route_variable_cost

            # Emissions
            route_emissions = distance_km * emissions_factor

            # Number of deliveries (stops minus depot start/end)
            route_deliveries = max(0, num_stops - 2)

            # Add to totals
            total_distance += distance_km
            total_time_minutes += time_minutes
            total_fuel_cost += route_fuel_cost
            total_labor_cost += route_labor_cost
            total_fixed_cost += fixed_cost
            total_variable_cost += route_variable_cost
            total_emissions += route_emissions
            total_deliveries += route_deliveries

            # Store breakdown
            per_route_breakdown.append({
                "vehicle_id": vehicle_id,
                "distance_km": round(distance_km, 2),
                "time_hours": round(time_hours, 2),
                "fuel_cost": round(route_fuel_cost, 2),
                "labor_cost": round(route_labor_cost, 2),
                "fixed_cost": round(fixed_cost, 2),
                "variable_cost": round(route_variable_cost, 2),
                "total_cost": round(route_total_cost, 2),
                "emissions_kg": round(route_emissions, 2),
                "deliveries": route_deliveries,
                "cost_per_delivery": round(route_total_cost / route_deliveries, 2) if route_deliveries > 0 else 0
            })

        # Calculate aggregate metrics
        total_cost = total_fuel_cost + total_labor_cost + total_fixed_cost + total_variable_cost
        total_time_hours = total_time_minutes / 60.0

        cost_per_km = total_cost / total_distance if total_distance > 0 else 0
        cost_per_delivery = total_cost / total_deliveries if total_deliveries > 0 else 0

        # Emissions per km
        emissions_per_km = total_emissions / total_distance if total_distance > 0 else 0

        # Build result
        result = {
            "total_cost": round(total_cost, 2),
            "total_cost_usd": round(total_cost, 2),  # Add for compatibility
            "fuel_cost": round(total_fuel_cost, 2),
            "fuel_cost_usd": round(total_fuel_cost, 2),  # Add for compatibility
            "labor_cost": round(total_labor_cost, 2),
            "labor_cost_usd": round(total_labor_cost, 2),  # Add for compatibility
            "fixed_cost": round(total_fixed_cost, 2),
            "variable_cost": round(total_variable_cost, 2),
            "total_distance_km": round(total_distance, 2),
            "total_time_hours": round(total_time_hours, 2),
            "total_emissions_kg": round(total_emissions, 2),
            "cost_per_km": round(cost_per_km, 2),
            "cost_per_delivery": round(cost_per_delivery, 2),
            "emissions_per_km": round(emissions_per_km, 3),
            "total_deliveries": total_deliveries,
            "num_routes": len(routes_list),
            "parameters": {
                "fuel_price_per_liter": fuel_price_per_liter,
                "driver_wage_per_hour": driver_wage_per_hour
            },
            "per_route_breakdown": per_route_breakdown
        }

        logger.info(
            f"Economics calculated: total_cost=${total_cost:.2f}, "
            f"distance={total_distance:.1f}km, "
            f"emissions={total_emissions:.1f}kg"
        )

        return json.dumps(result)

    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON format for routes: {e}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg, "total_cost": 0.0})

    except Exception as e:
        error_msg = f"Error calculating economics: {e}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg, "total_cost": 0.0})


def calculate_carbon_footprint(distance_km: float, emissions_factor: float = 0.25) -> float:
    """
    Calculate carbon footprint for a given distance.

    Args:
        distance_km: Distance traveled (km)
        emissions_factor: CO2 emissions per km (kg CO2/km)
                         Default: 0.25 (typical for delivery van)

    Returns:
        CO2 emissions in kg
    """
    return distance_km * emissions_factor


def calculate_fuel_consumption(
    distance_km: float,
    efficiency_km_per_liter: float = 10.0
) -> float:
    """
    Calculate fuel consumption for a given distance.

    Args:
        distance_km: Distance traveled (km)
        efficiency_km_per_liter: Vehicle fuel efficiency
                                Default: 10.0 km/liter

    Returns:
        Fuel consumption in liters
    """
    return distance_km / efficiency_km_per_liter


def estimate_overtime_cost(
    time_hours: float,
    regular_hours: float = 8.0,
    regular_wage: float = 15.0,
    overtime_multiplier: float = 1.5
) -> Dict[str, float]:
    """
    Calculate labor cost with overtime.

    Args:
        time_hours: Total working hours
        regular_hours: Regular shift duration (hours)
        regular_wage: Regular hourly wage (USD/hour)
        overtime_multiplier: Overtime pay multiplier
                            Default: 1.5 (time-and-a-half)

    Returns:
        Dictionary with regular_cost, overtime_cost, total_cost
    """
    if time_hours <= regular_hours:
        return {
            "regular_hours": time_hours,
            "overtime_hours": 0.0,
            "regular_cost": time_hours * regular_wage,
            "overtime_cost": 0.0,
            "total_cost": time_hours * regular_wage
        }
    else:
        overtime_hours = time_hours - regular_hours
        overtime_wage = regular_wage * overtime_multiplier

        regular_cost = regular_hours * regular_wage
        overtime_cost = overtime_hours * overtime_wage
        total_cost = regular_cost + overtime_cost

        return {
            "regular_hours": regular_hours,
            "overtime_hours": overtime_hours,
            "regular_cost": regular_cost,
            "overtime_cost": overtime_cost,
            "total_cost": total_cost
        }
