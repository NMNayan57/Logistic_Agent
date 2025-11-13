"""
Generate sample logistics data for testing and demonstration.

This script creates realistic sample data files:
- orders.csv: Customer delivery orders
- vehicles.csv: Fleet vehicles
- depot.csv: Distribution center information

Usage:
    python scripts/create_sample_data.py
"""

import random
import pandas as pd
from pathlib import Path

# Set random seed for reproducibility
random.seed(42)


def generate_orders(num_orders: int = 50) -> pd.DataFrame:
    """
    Generate sample delivery orders.

    Args:
        num_orders: Number of orders to generate

    Returns:
        DataFrame with order data
    """
    orders = []

    # Base location (New York City area)
    base_lat = 40.7128
    base_lon = -74.0060

    # Initialize cluster variables
    cluster_lat = base_lat
    cluster_lon = base_lon

    for i in range(1, num_orders + 1):
        # Cluster some orders geographically (simulate neighborhoods)
        if i % 5 == 0:
            # Start new cluster
            cluster_lat = base_lat + random.uniform(-0.5, 0.5)
            cluster_lon = base_lon + random.uniform(-0.5, 0.5)

        # Add noise around cluster center
        lat = cluster_lat + random.uniform(-0.05, 0.05)
        lon = cluster_lon + random.uniform(-0.05, 0.05)

        # Time windows (business hours: 8 AM - 6 PM = 480 - 1080 minutes)
        tw_start = random.randint(480, 900)  # 8 AM - 3 PM
        tw_duration = random.randint(120, 300)  # 2-5 hours window
        tw_end = tw_start + tw_duration

        # Ensure we don't exceed 6 PM
        if tw_end > 1080:
            tw_end = 1080

        order = {
            "order_id": f"O{i:03d}",
            "customer_id": f"C{i:03d}",
            "demand": round(random.uniform(5, 30), 1),
            "service_time": random.randint(5, 20),
            "time_window_start": tw_start,
            "time_window_end": tw_end,
            "latitude": round(lat, 6),
            "longitude": round(lon, 6),
            "is_cold_chain": random.random() < 0.2,  # 20% are cold-chain
            "priority": random.choice(["low", "medium", "medium", "high"])  # Weighted
        }
        orders.append(order)

    return pd.DataFrame(orders)


def generate_vehicles(num_vehicles: int = 10) -> pd.DataFrame:
    """
    Generate sample fleet vehicles.

    Args:
        num_vehicles: Number of vehicles to generate

    Returns:
        DataFrame with vehicle data
    """
    vehicles = []

    # Vehicle type configurations
    vehicle_types = [
        {
            "type": "van",
            "capacity": 100,
            "cost_per_km": 2.00,
            "fixed_cost": 50.0,
            "emissions_factor": 0.20,
            "speed_kmh": 55.0
        },
        {
            "type": "small_truck",
            "capacity": 200,
            "cost_per_km": 2.50,
            "fixed_cost": 70.0,
            "emissions_factor": 0.28,
            "speed_kmh": 50.0
        },
        {
            "type": "large_truck",
            "capacity": 400,
            "cost_per_km": 3.50,
            "fixed_cost": 100.0,
            "emissions_factor": 0.35,
            "speed_kmh": 45.0
        }
    ]

    for i in range(1, num_vehicles + 1):
        # Randomly select vehicle type
        vtype = random.choice(vehicle_types)

        # Add some variation
        capacity_variation = random.uniform(0.9, 1.1)
        cost_variation = random.uniform(0.95, 1.05)

        vehicle = {
            "vehicle_id": f"V{i:03d}",
            "capacity": round(vtype["capacity"] * capacity_variation, 1),
            "max_working_hours": 8.0,
            "cost_per_km": round(vtype["cost_per_km"] * cost_variation, 2),
            "fixed_cost": vtype["fixed_cost"],
            "emissions_factor": vtype["emissions_factor"],
            "speed_kmh": vtype["speed_kmh"],
            "available": True,
            "vehicle_type": vtype["type"]
        }
        vehicles.append(vehicle)

    return pd.DataFrame(vehicles)


def generate_depot() -> pd.DataFrame:
    """
    Generate depot information.

    Returns:
        DataFrame with depot data (single row)
    """
    depot = {
        "depot_id": "D001",
        "name": "Main Distribution Center",
        "latitude": 40.7580,  # Manhattan
        "longitude": -73.9855,
        "time_window_start": 0,  # Midnight
        "time_window_end": 1440,  # Next midnight (24/7 operation)
        "address": "123 Warehouse Street, New York, NY 10001"
    }

    return pd.DataFrame([depot])


def main():
    """Generate and save all sample data files."""
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    print(">> Generating sample logistics data...\n")

    # Generate orders
    print("[Orders] Generating orders...")
    orders_df = generate_orders(num_orders=50)
    orders_path = data_dir / "orders.csv"
    orders_df.to_csv(orders_path, index=False)
    print(f"   [OK] Created {orders_path} ({len(orders_df)} orders)")
    print(f"   - {orders_df['is_cold_chain'].sum()} cold-chain orders")
    print(f"   - Priority distribution: {orders_df['priority'].value_counts().to_dict()}")

    # Generate vehicles
    print("\n[Vehicles] Generating vehicles...")
    vehicles_df = generate_vehicles(num_vehicles=10)
    vehicles_path = data_dir / "vehicles.csv"
    vehicles_df.to_csv(vehicles_path, index=False)
    print(f"   [OK] Created {vehicles_path} ({len(vehicles_df)} vehicles)")
    print(f"   - Type distribution: {vehicles_df['vehicle_type'].value_counts().to_dict()}")
    print(f"   - Total capacity: {vehicles_df['capacity'].sum():.1f} units")

    # Generate depot
    print("\n[Depot] Generating depot...")
    depot_df = generate_depot()
    depot_path = data_dir / "depot.csv"
    depot_df.to_csv(depot_path, index=False)
    print(f"   [OK] Created {depot_path}")

    # Summary
    print("\n" + "="*60)
    print("[SUCCESS] Sample data generation complete!")
    print("="*60)
    print(f"\nGenerated files:")
    print(f"  - {orders_path} ({orders_path.stat().st_size / 1024:.1f} KB)")
    print(f"  - {vehicles_path} ({vehicles_path.stat().st_size / 1024:.1f} KB)")
    print(f"  - {depot_path} ({depot_path.stat().st_size / 1024:.1f} KB)")
    print("\nYou can now use these files to test the system:")
    print("  python scripts/setup_database.py")


if __name__ == "__main__":
    main()
