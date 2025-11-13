"""
Database setup and initialization script.

This script initializes the database, creates tables, and loads sample data.

Usage:
    python scripts/setup_database.py [--reset] [--load-data]

Options:
    --reset: Drop all existing tables and recreate (WARNING: deletes all data!)
    --load-data: Load sample data from CSV files after initialization
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import (
    init_database,
    reset_database,
    get_db,
    OrderDB,
    VehicleDB,
    DepotDB,
    get_database_stats
)
from src.data.loader import CSVLoader


def setup_database(reset: bool = False, yes: bool = False):
    """
    Initialize database schema.

    Args:
        reset: If True, drop and recreate all tables
        yes: If True, skip confirmation prompts
    """
    print("[INFO] Setting up database...\n")

    if reset:
        if not yes:
            confirm = input("[WARNING] This will delete all existing data. Continue? (yes/no): ")
            if confirm.lower() != "yes":
                print("[CANCELLED] Database reset cancelled.")
                return False
        reset_database()
    else:
        init_database()

    print("[OK] Database schema initialized successfully!\n")
    return True


def load_sample_data():
    """Load sample data from CSV files into database."""
    print("[INFO] Loading sample data into database...\n")

    data_dir = Path("data")

    # Check if CSV files exist
    orders_file = data_dir / "orders.csv"
    vehicles_file = data_dir / "vehicles.csv"
    depot_file = data_dir / "depot.csv"

    missing_files = []
    if not orders_file.exists():
        missing_files.append(str(orders_file))
    if not vehicles_file.exists():
        missing_files.append(str(vehicles_file))
    if not depot_file.exists():
        missing_files.append(str(depot_file))

    if missing_files:
        print("[ERROR] Missing required data files:")
        for f in missing_files:
            print(f"   - {f}")
        print("\n[INFO] Run this command first to generate sample data:")
        print("   python scripts/create_sample_data.py")
        return False

    # Load data using CSVLoader
    loader = CSVLoader()

    try:
        # Load from CSV
        print("[Orders] Loading orders...")
        orders = loader.load_orders_csv(orders_file)
        print(f"   [OK] Loaded {len(orders)} orders")

        print("[Vehicles] Loading vehicles...")
        vehicles = loader.load_vehicles_csv(vehicles_file)
        print(f"   [OK] Loaded {len(vehicles)} vehicles")

        print("[Depot] Loading depot...")
        depot = loader.load_depot_csv(depot_file)
        print(f"   [OK] Loaded depot: {depot.name}")

        # Insert into database
        db = next(get_db())

        try:
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

            print("\n[SUCCESS] Sample data loaded successfully!")

            # Show statistics
            stats = get_database_stats(db)
            print("\n[Stats] Database Statistics:")
            print(f"   - Orders: {stats['orders_count']}")
            print(f"   - Vehicles: {stats['vehicles_count']}")
            print(f"   - Depots: {stats['depots_count']}")

            return True

        except Exception as e:
            db.rollback()
            print(f"\n[ERROR] Error inserting data: {e}")
            return False

        finally:
            db.close()

    except Exception as e:
        print(f"\n[ERROR] Error loading data files: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Initialize database and optionally load sample data"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop and recreate all tables (WARNING: deletes all data!)"
    )
    parser.add_argument(
        "--load-data",
        action="store_true",
        help="Load sample data from CSV files"
    )
    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Skip confirmation prompts"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("  Logistics AI Agent - Database Setup")
    print("=" * 60)
    print()

    # Setup database schema
    if not setup_database(reset=args.reset, yes=args.yes):
        return

    # Load data if requested
    if args.load_data:
        print()
        if not load_sample_data():
            sys.exit(1)

    print("\n" + "=" * 60)
    print("[SUCCESS] Setup complete!")
    print("=" * 60)

    if not args.load_data:
        print("\n[INFO] To load sample data, run:")
        print("   python scripts/setup_database.py --load-data")

    print("\n[NEXT] You can now start the API server:")
    print("   uvicorn src.main:app --reload")
    print()


if __name__ == "__main__":
    main()
