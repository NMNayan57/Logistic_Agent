"""
Database tools for accessing orders, vehicles, and depot information.

These tools allow the AI agent to query the database for logistics data
using natural language requests.
"""

from typing import Optional, List, Dict, Any
import json
from langchain.tools import tool
from sqlalchemy.orm import Session
from src.database import (
    get_db,
    OrderDB,
    VehicleDB,
    DepotDB,
    order_to_dict,
    vehicle_to_dict,
    depot_to_dict
)
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


@tool
def get_orders(
    order_ids: Optional[str] = None,
    count: Optional[int] = None,
    filters: Optional[str] = None
) -> str:
    """
    Fetch order data from the database.

    This tool retrieves customer delivery orders with optional filtering.
    Use this when you need to get order details for routing.

    Args:
        order_ids: Optional JSON string of order IDs to fetch.
                  Format: '["O001", "O002", "O003"]'
                  If None, returns all orders (subject to count limit)
        count: Optional maximum number of orders to return.
               Default: None (returns all matching orders)
        filters: Optional JSON string of filter criteria.
                Format: '{"is_cold_chain": true, "priority": "high"}'
                Supported filters:
                - is_cold_chain: boolean (only cold-chain orders)
                - priority: "low"/"medium"/"high"
                - min_demand: float (minimum demand)
                - max_demand: float (maximum demand)

    Returns:
        JSON string with list of orders and metadata.
        Format: {
            "orders": [{"order_id": "O001", "demand": 15.5, ...}, ...],
            "count": 10,
            "total_demand": 205.5
        }

    Example:
        >>> result = get_orders.invoke({"count": 10})
        >>> data = json.loads(result)
        >>> print(f"Found {data['count']} orders")
    """
    logger.info(f"Fetching orders (count={count}, filters={filters})")

    try:
        # Get database session
        db = next(get_db())

        try:
            # Start query
            query = db.query(OrderDB)

            # Filter by order IDs if provided
            if order_ids:
                ids_list = json.loads(order_ids)
                query = query.filter(OrderDB.order_id.in_(ids_list))
                logger.debug(f"Filtering by order IDs: {len(ids_list)} IDs")

            # Apply filters if provided
            if filters:
                filter_dict = json.loads(filters)

                if "is_cold_chain" in filter_dict:
                    query = query.filter(OrderDB.is_cold_chain == filter_dict["is_cold_chain"])
                    logger.debug(f"Filtering by cold_chain={filter_dict['is_cold_chain']}")

                if "priority" in filter_dict:
                    query = query.filter(OrderDB.priority == filter_dict["priority"])
                    logger.debug(f"Filtering by priority={filter_dict['priority']}")

                if "min_demand" in filter_dict:
                    query = query.filter(OrderDB.demand >= filter_dict["min_demand"])
                    logger.debug(f"Filtering by min_demand={filter_dict['min_demand']}")

                if "max_demand" in filter_dict:
                    query = query.filter(OrderDB.demand <= filter_dict["max_demand"])
                    logger.debug(f"Filtering by max_demand={filter_dict['max_demand']}")

            # Apply count limit if specified
            if count:
                query = query.limit(count)

            # Execute query
            orders_db = query.all()

            # Convert to dictionaries
            orders = [order_to_dict(order) for order in orders_db]

            # Calculate statistics
            total_demand = sum(order["demand"] for order in orders)
            cold_chain_count = sum(1 for order in orders if order["is_cold_chain"])

            result = {
                "orders": orders,
                "count": len(orders),
                "total_demand": total_demand,
                "cold_chain_count": cold_chain_count
            }

            logger.info(f"Retrieved {len(orders)} orders, total demand: {total_demand:.1f}")
            return json.dumps(result)

        finally:
            db.close()

    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON format: {e}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg, "orders": []})

    except Exception as e:
        error_msg = f"Error fetching orders: {e}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg, "orders": []})


@tool
def get_vehicles(
    vehicle_ids: Optional[str] = None,
    only_available: bool = True
) -> str:
    """
    Fetch vehicle data from the database.

    This tool retrieves fleet vehicle information for routing.
    Use this when you need to know available vehicles and their capacities.

    Args:
        vehicle_ids: Optional JSON string of vehicle IDs to fetch.
                    Format: '["V001", "V002", "V003"]'
                    If None, returns all vehicles
        only_available: If True, only return available vehicles.
                       Default: True

    Returns:
        JSON string with list of vehicles and metadata.
        Format: {
            "vehicles": [{"vehicle_id": "V001", "capacity": 100, ...}, ...],
            "count": 5,
            "total_capacity": 500.0,
            "available_count": 5
        }

    Example:
        >>> result = get_vehicles.invoke({"only_available": True})
        >>> data = json.loads(result)
        >>> print(f"Found {data['count']} available vehicles")
    """
    logger.info(f"Fetching vehicles (only_available={only_available})")

    try:
        # Get database session
        db = next(get_db())

        try:
            # Start query
            query = db.query(VehicleDB)

            # Filter by vehicle IDs if provided
            if vehicle_ids:
                ids_list = json.loads(vehicle_ids)
                query = query.filter(VehicleDB.vehicle_id.in_(ids_list))
                logger.debug(f"Filtering by vehicle IDs: {len(ids_list)} IDs")

            # Filter by availability
            if only_available:
                query = query.filter(VehicleDB.available == True)
                logger.debug("Filtering for available vehicles only")

            # Execute query
            vehicles_db = query.all()

            # Convert to dictionaries
            vehicles = [vehicle_to_dict(vehicle) for vehicle in vehicles_db]

            # Calculate statistics
            total_capacity = sum(vehicle["capacity"] for vehicle in vehicles)
            available_count = sum(1 for vehicle in vehicles if vehicle["available"])

            result = {
                "vehicles": vehicles,
                "count": len(vehicles),
                "total_capacity": total_capacity,
                "available_count": available_count
            }

            logger.info(f"Retrieved {len(vehicles)} vehicles, total capacity: {total_capacity:.1f}")
            return json.dumps(result)

        finally:
            db.close()

    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON format: {e}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg, "vehicles": []})

    except Exception as e:
        error_msg = f"Error fetching vehicles: {e}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg, "vehicles": []})


@tool
def get_depot_info() -> str:
    """
    Fetch depot location and operating hours.

    This tool retrieves information about the distribution center where
    vehicles start and end their routes.

    Returns:
        JSON string with depot information.
        Format: {
            "depot": {
                "depot_id": "D001",
                "name": "Main Distribution Center",
                "latitude": 40.7580,
                "longitude": -73.9855,
                "time_window_start": 0,
                "time_window_end": 1440,
                "address": "123 Warehouse St"
            }
        }

    Example:
        >>> result = get_depot_info.invoke({})
        >>> data = json.loads(result)
        >>> print(f"Depot: {data['depot']['name']}")
    """
    logger.info("Fetching depot information")

    try:
        # Get database session
        db = next(get_db())

        try:
            # Query first depot (assuming single depot for PoC)
            depot_db = db.query(DepotDB).first()

            if not depot_db:
                logger.warning("No depot found in database")
                return json.dumps({
                    "error": "No depot found in database",
                    "depot": None
                })

            # Convert to dictionary
            depot = depot_to_dict(depot_db)

            result = {"depot": depot}

            logger.info(f"Retrieved depot: {depot['name']}")
            return json.dumps(result)

        finally:
            db.close()

    except Exception as e:
        error_msg = f"Error fetching depot: {e}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg, "depot": None})


@tool
def get_database_stats() -> str:
    """
    Get database statistics and counts.

    This tool provides overview statistics about the database.
    Use this to understand what data is available.

    Returns:
        JSON string with database statistics.
        Format: {
            "orders_count": 50,
            "vehicles_count": 10,
            "depots_count": 1,
            "routes_history_count": 5
        }

    Example:
        >>> result = get_database_stats.invoke({})
        >>> data = json.loads(result)
        >>> print(f"Database has {data['orders_count']} orders")
    """
    logger.info("Fetching database statistics")

    try:
        # Get database session
        db = next(get_db())

        try:
            from src.database import get_database_stats as _get_stats
            stats = _get_stats(db)

            logger.info(f"Database stats: {stats['orders_count']} orders, {stats['vehicles_count']} vehicles")
            return json.dumps(stats)

        finally:
            db.close()

    except Exception as e:
        error_msg = f"Error fetching database stats: {e}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})
