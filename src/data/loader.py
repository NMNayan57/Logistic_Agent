"""
Data loading utilities for Solomon benchmark and CSV files.

This module provides functions to load and parse logistics data from
various formats including Solomon VRPTW benchmark files and CSV files.
"""

from typing import Dict, List, Any, Tuple
from pathlib import Path
import pandas as pd
from src.models import Order, Vehicle, Depot


class SolomonLoader:
    """
    Loader for Solomon VRPTW benchmark instances.

    The Solomon format is a standard benchmark for Vehicle Routing
    Problems with Time Windows. Files contain:
    - Vehicle information (capacity, number)
    - Depot location and time windows
    - Customer locations, demands, and time windows

    Format:
        Line 1: Instance name
        Line 2-4: Empty/comments
        Line 5: Vehicle info (NUMBER CAPACITY)
        Line 6-8: Empty/comments
        Line 9+: Customer data (CUST NO. XCOORD. YCOORD. DEMAND READY TIME DUE DATE SERVICE TIME)

    Example:
        >>> loader = SolomonLoader()
        >>> data = loader.load_instance("data/solomon/C101.txt")
        >>> print(data.keys())
        dict_keys(['instance_name', 'depot', 'orders', 'vehicle_capacity', 'num_vehicles'])
    """

    def load_instance(self, filepath: str | Path) -> Dict[str, Any]:
        """
        Load a Solomon VRPTW instance from file.

        Args:
            filepath: Path to Solomon instance file

        Returns:
            Dictionary containing:
                - instance_name: Name of the instance
                - depot: Depot dictionary
                - orders: List of order dictionaries
                - vehicle_capacity: Vehicle capacity
                - num_vehicles: Number of vehicles available

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"Solomon file not found: {filepath}")

        with open(filepath, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        if len(lines) < 10:
            raise ValueError(f"Invalid Solomon file format: {filepath}")

        # Parse instance name
        instance_name = lines[0]

        # Parse vehicle information (usually line 4 or 5)
        vehicle_line = None
        for i in range(4, 8):
            if i < len(lines):
                parts = lines[i].split()
                if len(parts) >= 2 and parts[0].isdigit():
                    vehicle_line = parts
                    data_start_line = i + 4
                    break

        if vehicle_line is None:
            raise ValueError(f"Could not find vehicle information in {filepath}")

        num_vehicles = int(vehicle_line[0])
        vehicle_capacity = float(vehicle_line[1])

        # Parse customer data
        depot_data = None
        orders_data = []

        for line in lines[data_start_line:]:
            parts = line.split()
            if len(parts) < 7:
                continue

            try:
                cust_no = int(parts[0])
                x_coord = float(parts[1])
                y_coord = float(parts[2])
                demand = float(parts[3])
                ready_time = int(float(parts[4]))
                due_date = int(float(parts[5]))
                service_time = int(float(parts[6]))

                customer_dict = {
                    "customer_no": cust_no,
                    "x_coord": x_coord,
                    "y_coord": y_coord,
                    "demand": demand,
                    "ready_time": ready_time,
                    "due_date": due_date,
                    "service_time": service_time
                }

                # Customer 0 is the depot
                if cust_no == 0:
                    depot_data = customer_dict
                else:
                    orders_data.append(customer_dict)

            except (ValueError, IndexError) as e:
                print(f"Warning: Skipping malformed line: {line} ({e})")
                continue

        if depot_data is None:
            raise ValueError(f"No depot found in {filepath}")

        # Convert to our data models format
        depot = {
            "depot_id": "D001",
            "name": f"Depot for {instance_name}",
            "latitude": depot_data["y_coord"],
            "longitude": depot_data["x_coord"],
            "time_window_start": depot_data["ready_time"],
            "time_window_end": depot_data["due_date"],
            "address": None
        }

        orders = []
        for i, order_data in enumerate(orders_data, 1):
            orders.append({
                "order_id": f"O{i:03d}",
                "customer_id": f"C{order_data['customer_no']:03d}",
                "demand": order_data["demand"],
                "service_time": order_data["service_time"],
                "time_window_start": order_data["ready_time"],
                "time_window_end": order_data["due_date"],
                "latitude": order_data["y_coord"],
                "longitude": order_data["x_coord"],
                "is_cold_chain": False,
                "priority": "medium"
            })

        return {
            "instance_name": instance_name,
            "depot": depot,
            "orders": orders,
            "vehicle_capacity": vehicle_capacity,
            "num_vehicles": num_vehicles
        }

    def load_to_models(self, filepath: str | Path) -> Tuple[Depot, List[Order], Dict[str, Any]]:
        """
        Load Solomon instance and convert to Pydantic models.

        Args:
            filepath: Path to Solomon instance file

        Returns:
            Tuple of (Depot, List[Order], vehicle_info_dict)
        """
        data = self.load_instance(filepath)

        depot = Depot(**data["depot"])
        orders = [Order(**order_dict) for order_dict in data["orders"]]

        vehicle_info = {
            "capacity": data["vehicle_capacity"],
            "num_vehicles": data["num_vehicles"]
        }

        return depot, orders, vehicle_info


class CSVLoader:
    """
    Loader for CSV data files.

    Supports loading orders, vehicles, and depots from CSV files.
    """

    @staticmethod
    def load_orders_csv(filepath: str | Path) -> List[Order]:
        """
        Load orders from CSV file.

        Expected columns:
            order_id, customer_id, demand, service_time, time_window_start,
            time_window_end, latitude, longitude, is_cold_chain, priority

        Args:
            filepath: Path to orders CSV file

        Returns:
            List of Order objects
        """
        df = pd.read_csv(filepath)

        required_cols = [
            "order_id", "customer_id", "demand", "service_time",
            "time_window_start", "time_window_end", "latitude", "longitude"
        ]

        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Set defaults for optional columns
        if "is_cold_chain" not in df.columns:
            df["is_cold_chain"] = False
        if "priority" not in df.columns:
            df["priority"] = "medium"

        orders = []
        for _, row in df.iterrows():
            try:
                order = Order(**row.to_dict())
                orders.append(order)
            except Exception as e:
                print(f"Warning: Skipping invalid order row: {e}")
                continue

        return orders

    @staticmethod
    def load_vehicles_csv(filepath: str | Path) -> List[Vehicle]:
        """
        Load vehicles from CSV file.

        Expected columns:
            vehicle_id, capacity, max_working_hours, cost_per_km,
            fixed_cost, emissions_factor, speed_kmh, available

        Args:
            filepath: Path to vehicles CSV file

        Returns:
            List of Vehicle objects
        """
        df = pd.read_csv(filepath)

        required_cols = [
            "vehicle_id", "capacity", "max_working_hours",
            "cost_per_km", "fixed_cost", "emissions_factor"
        ]

        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Set defaults for optional columns
        if "speed_kmh" not in df.columns:
            df["speed_kmh"] = 50.0
        if "available" not in df.columns:
            df["available"] = True

        vehicles = []
        for _, row in df.iterrows():
            try:
                vehicle = Vehicle(**row.to_dict())
                vehicles.append(vehicle)
            except Exception as e:
                print(f"Warning: Skipping invalid vehicle row: {e}")
                continue

        return vehicles

    @staticmethod
    def load_depot_csv(filepath: str | Path) -> Depot:
        """
        Load depot from CSV file.

        Expected columns:
            depot_id, name, latitude, longitude, time_window_start,
            time_window_end, address

        Args:
            filepath: Path to depot CSV file

        Returns:
            Depot object (returns first row if multiple depots)
        """
        df = pd.read_csv(filepath)

        required_cols = ["depot_id", "name", "latitude", "longitude"]

        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Set defaults for optional columns
        if "time_window_start" not in df.columns:
            df["time_window_start"] = 0
        if "time_window_end" not in df.columns:
            df["time_window_end"] = 1440
        if "address" not in df.columns:
            df["address"] = None

        if len(df) == 0:
            raise ValueError("Depot CSV file is empty")

        # Return first depot
        depot_dict = df.iloc[0].to_dict()
        return Depot(**depot_dict)


def load_all_solomon_instances(directory: str | Path) -> Dict[str, Dict[str, Any]]:
    """
    Load all Solomon instances from a directory.

    Args:
        directory: Path to directory containing Solomon .txt files

    Returns:
        Dictionary mapping instance name to instance data
    """
    directory = Path(directory)
    loader = SolomonLoader()

    instances = {}
    for filepath in directory.glob("*.txt"):
        try:
            data = loader.load_instance(filepath)
            instances[data["instance_name"]] = data
            print(f"✓ Loaded {data['instance_name']}: {len(data['orders'])} orders")
        except Exception as e:
            print(f"✗ Failed to load {filepath.name}: {e}")

    return instances
