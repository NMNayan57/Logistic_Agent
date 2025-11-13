"""
API endpoint to initialize database with sample data.
This is for production deployment where scripts can't be run directly.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db, OrderDB, VehicleDB, DepotDB, get_database_stats
from src.models.depot import Depot
from src.models.order import Order
from src.models.vehicle import Vehicle
import random

router = APIRouter()


def create_sample_depot() -> Depot:
    """Create a sample depot in New York City."""
    return Depot(
        depot_id="DEPOT001",
        name="Main Distribution Center - NYC",
        latitude=40.7128,
        longitude=-74.0060,
        time_window_start=0,
        time_window_end=720,  # 12 hours
        address="123 Main St, New York, NY 10001"
    )


def create_sample_orders(num_orders: int = 20) -> list[Order]:
    """Create sample delivery orders around NYC."""
    orders = []
    base_lat = 40.7128
    base_lon = -74.0060

    random.seed(42)

    for i in range(1, num_orders + 1):
        # Create clusters of orders
        if i % 5 == 0:
            cluster_lat = base_lat + random.uniform(-0.3, 0.3)
            cluster_lon = base_lon + random.uniform(-0.3, 0.3)
        else:
            cluster_lat = orders[-1].latitude if orders else base_lat
            cluster_lon = orders[-1].longitude if orders else base_lon

        lat = cluster_lat + random.uniform(-0.05, 0.05)
        lon = cluster_lon + random.uniform(-0.05, 0.05)

        order = Order(
            order_id=f"O{i:03d}",
            customer_id=f"C{i:03d}",
            demand=random.randint(5, 50),
            service_time=random.randint(5, 20),
            time_window_start=random.randint(0, 300),
            time_window_end=random.randint(400, 720),
            latitude=lat,
            longitude=lon,
            is_cold_chain=random.choice([True, False]),
            priority=random.choice(["high", "medium", "low"])
        )
        orders.append(order)

    return orders


def create_sample_vehicles(num_vehicles: int = 5) -> list[Vehicle]:
    """Create sample delivery vehicles."""
    vehicles = []

    vehicle_types = [
        {"type": "small_van", "capacity": 100, "cost_per_km": 0.8, "emissions": 0.15},
        {"type": "medium_truck", "capacity": 200, "cost_per_km": 1.2, "emissions": 0.25},
        {"type": "large_truck", "capacity": 300, "cost_per_km": 1.8, "emissions": 0.40},
    ]

    for i in range(1, num_vehicles + 1):
        vtype = vehicle_types[i % len(vehicle_types)]

        vehicle = Vehicle(
            vehicle_id=f"V{i:03d}",
            capacity=vtype["capacity"],
            max_working_hours=8.0,
            cost_per_km=vtype["cost_per_km"],
            fixed_cost=50.0,
            emissions_factor=vtype["emissions"],
            speed_kmh=40.0,
            available=True,
            vehicle_type=vtype["type"]
        )
        vehicles.append(vehicle)

    return vehicles


@router.post("/init-sample-data")
async def initialize_sample_data(
    num_orders: int = 20,
    num_vehicles: int = 5,
    reset: bool = False,
    db: Session = Depends(get_db)
):
    """
    Initialize database with sample data.

    Args:
        num_orders: Number of sample orders to create (default: 20)
        num_vehicles: Number of sample vehicles to create (default: 5)
        reset: If True, delete existing data first

    Returns:
        Success message with statistics
    """
    try:
        # Check if data already exists
        existing_stats = get_database_stats(db)

        if existing_stats["orders_count"] > 0 and not reset:
            return {
                "status": "data_exists",
                "message": "Database already contains data. Use reset=true to recreate.",
                "stats": existing_stats
            }

        # Reset if requested
        if reset:
            db.query(OrderDB).delete()
            db.query(VehicleDB).delete()
            db.query(DepotDB).delete()
            db.commit()

        # Create sample data
        depot = create_sample_depot()
        orders = create_sample_orders(num_orders)
        vehicles = create_sample_vehicles(num_vehicles)

        # Insert depot
        depot_db = DepotDB(
            depot_id=depot.depot_id,
            name=depot.name,
            latitude=depot.latitude,
            longitude=depot.longitude,
            time_window_start=depot.time_window_start,
            time_window_end=depot.time_window_end,
            address=depot.address
        )
        db.add(depot_db)

        # Insert orders
        for order in orders:
            order_db = OrderDB(
                order_id=order.order_id,
                customer_id=order.customer_id,
                demand=order.demand,
                service_time=order.service_time,
                time_window_start=order.time_window_start,
                time_window_end=order.time_window_end,
                latitude=order.latitude,
                longitude=order.longitude,
                is_cold_chain=order.is_cold_chain,
                priority=order.priority
            )
            db.add(order_db)

        # Insert vehicles
        for vehicle in vehicles:
            vehicle_db = VehicleDB(
                vehicle_id=vehicle.vehicle_id,
                capacity=vehicle.capacity,
                max_working_hours=vehicle.max_working_hours,
                cost_per_km=vehicle.cost_per_km,
                fixed_cost=vehicle.fixed_cost,
                emissions_factor=vehicle.emissions_factor,
                speed_kmh=vehicle.speed_kmh,
                available=vehicle.available,
                vehicle_type=vehicle.vehicle_type
            )
            db.add(vehicle_db)

        # Commit all changes
        db.commit()

        # Get final statistics
        final_stats = get_database_stats(db)

        return {
            "status": "success",
            "message": "Sample data initialized successfully!",
            "stats": final_stats,
            "data_created": {
                "depot": depot.name,
                "orders": len(orders),
                "vehicles": len(vehicles)
            }
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error initializing sample data: {str(e)}"
        )
