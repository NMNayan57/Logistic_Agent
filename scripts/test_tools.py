"""
Test script for verifying all tools work correctly.

This script tests each tool individually to ensure they function properly
before integrating with the LLM agent.

Usage:
    python scripts/test_tools.py
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Must set up a minimal .env first
import os
os.environ.setdefault("OPENAI_API_KEY", "sk-test-key-not-used-for-tool-testing")
os.environ.setdefault("DATABASE_URL", "sqlite:///./logistics.db")

from src.tools import (
    get_orders,
    get_vehicles,
    get_depot_info,
    calculate_distance_matrix,
    solve_vrp,
    calculate_route_economics,
    get_database_stats
)


def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_database_stats():
    """Test database statistics tool."""
    print_section("Test 1: Database Statistics")

    result = get_database_stats.invoke({})
    data = json.loads(result)

    if "error" in data:
        print(f"[ERROR] {data['error']}")
        return False

    print(f"[OK] Database stats retrieved")
    print(f"  - Orders: {data.get('orders_count', 0)}")
    print(f"  - Vehicles: {data.get('vehicles_count', 0)}")
    print(f"  - Depots: {data.get('depots_count', 0)}")
    return True


def test_get_orders():
    """Test get_orders tool."""
    print_section("Test 2: Get Orders")

    result = get_orders.invoke({"count": 10})
    data = json.loads(result)

    if "error" in data:
        print(f"[ERROR] {data['error']}")
        return False

    print(f"[OK] Retrieved {data['count']} orders")
    print(f"  - Total demand: {data['total_demand']:.1f} units")
    print(f"  - Cold-chain orders: {data['cold_chain_count']}")

    if data['count'] > 0:
        sample = data['orders'][0]
        print(f"\n  Sample order: {sample['order_id']}")
        print(f"    - Customer: {sample['customer_id']}")
        print(f"    - Demand: {sample['demand']} units")
        print(f"    - Time window: {sample['time_window_start']}-{sample['time_window_end']} min")

    return True


def test_get_vehicles():
    """Test get_vehicles tool."""
    print_section("Test 3: Get Vehicles")

    result = get_vehicles.invoke({"only_available": True})
    data = json.loads(result)

    if "error" in data:
        print(f"[ERROR] {data['error']}")
        return False

    print(f"[OK] Retrieved {data['count']} vehicles")
    print(f"  - Total capacity: {data['total_capacity']:.1f} units")
    print(f"  - Available: {data['available_count']}")

    if data['count'] > 0:
        sample = data['vehicles'][0]
        print(f"\n  Sample vehicle: {sample['vehicle_id']}")
        print(f"    - Capacity: {sample['capacity']} units")
        print(f"    - Cost per km: ${sample['cost_per_km']}")
        print(f"    - Max hours: {sample['max_working_hours']}h")

    return True


def test_get_depot():
    """Test get_depot_info tool."""
    print_section("Test 4: Get Depot Info")

    result = get_depot_info.invoke({})
    data = json.loads(result)

    if "error" in data:
        print(f"[ERROR] {data['error']}")
        return False

    depot = data['depot']
    print(f"[OK] Depot retrieved: {depot['name']}")
    print(f"  - Location: ({depot['latitude']}, {depot['longitude']})")
    print(f"  - Hours: {depot['time_window_start']}-{depot['time_window_end']} min")

    return True


def test_distance_matrix():
    """Test calculate_distance_matrix tool."""
    print_section("Test 5: Calculate Distance Matrix")

    # Test with 3 locations
    locations = [
        [40.7128, -74.0060],  # NYC
        [40.7580, -73.9855],  # Manhattan
        [40.6892, -74.0445]   # Jersey City
    ]

    result = calculate_distance_matrix.invoke({
        "locations": json.dumps(locations),
        "mode": "euclidean"
    })
    data = json.loads(result)

    if "error" in data:
        print(f"[ERROR] {data['error']}")
        return False

    print(f"[OK] Distance matrix calculated")
    print(f"  - Locations: {data['num_locations']}")
    print(f"  - Mode: {data['mode']}")
    print(f"\n  Distance matrix (km):")
    for i, row in enumerate(data['distance_matrix']):
        print(f"    {i}: {[f'{d:.2f}' for d in row]}")

    return True


def test_solve_vrp():
    """Test solve_vrp tool."""
    print_section("Test 6: Solve VRP")

    # Get a small number of orders to test
    orders_result = get_orders.invoke({"count": 5})
    orders_data = json.loads(orders_result)

    if "error" in orders_data or orders_data['count'] == 0:
        print("[SKIP] No orders available for VRP test")
        return True

    # Get available vehicles
    vehicles_result = get_vehicles.invoke({"only_available": True})
    vehicles_data = json.loads(vehicles_result)

    if "error" in vehicles_data or vehicles_data['count'] == 0:
        print("[SKIP] No vehicles available for VRP test")
        return True

    # Get first 5 orders and 2 vehicles
    order_ids = [o['order_id'] for o in orders_data['orders'][:5]]
    vehicle_ids = [v['vehicle_id'] for v in vehicles_data['vehicles'][:2]]

    print(f"Testing with {len(order_ids)} orders and {len(vehicle_ids)} vehicles...")

    result = solve_vrp.invoke({
        "order_ids": json.dumps(order_ids),
        "vehicle_ids": json.dumps(vehicle_ids),
        "objective": "minimize_distance"
    })
    data = json.loads(result)

    if "error" in data:
        print(f"[ERROR] {data['error']}")
        return False

    print(f"[OK] VRP solved!")
    print(f"  - Routes found: {data['num_routes']}")
    print(f"  - Total distance: {data['total_distance_km']:.1f} km")
    print(f"  - Total time: {data['total_time_minutes']} min")
    print(f"  - Solver status: {data['solver_status']}")

    for i, route in enumerate(data['routes'], 1):
        print(f"\n  Route {i} ({route['vehicle_id']}):")
        print(f"    - Stops: {len(route['stops'])}")
        print(f"    - Distance: {route['distance_km']} km")
        print(f"    - Time: {route['time_minutes']} min")
        print(f"    - Path: {' -> '.join(route['stops'][:5])}{'...' if len(route['stops']) > 5 else ''}")

    return data  # Return for next test


def test_calculate_economics(vrp_solution=None):
    """Test calculate_route_economics tool."""
    print_section("Test 7: Calculate Route Economics")

    if not vrp_solution or "routes" not in vrp_solution:
        print("[SKIP] No VRP solution available for economics test")
        return True

    # Use routes from VRP solution
    routes_json = json.dumps(vrp_solution['routes'])

    result = calculate_route_economics.invoke({
        "routes": routes_json,
        "fuel_price_per_liter": 1.5,
        "driver_wage_per_hour": 15.0
    })
    data = json.loads(result)

    if "error" in data:
        print(f"[ERROR] {data['error']}")
        return False

    print(f"[OK] Economics calculated")
    print(f"  - Total cost: ${data['total_cost']:.2f}")
    print(f"  - Fuel cost: ${data['fuel_cost']:.2f}")
    print(f"  - Labor cost: ${data['labor_cost']:.2f}")
    print(f"  - Fixed cost: ${data['fixed_cost']:.2f}")
    print(f"  - Total emissions: {data['total_emissions_kg']:.1f} kg CO2")
    print(f"  - Cost per delivery: ${data['cost_per_delivery']:.2f}")

    return True


def main():
    """Run all tests."""
    print("\n" + "#" * 60)
    print("#  Logistics AI Agent - Tools Testing")
    print("#" * 60)

    tests = [
        ("Database Stats", test_database_stats),
        ("Get Orders", test_get_orders),
        ("Get Vehicles", test_get_vehicles),
        ("Get Depot", test_get_depot),
        ("Distance Matrix", test_distance_matrix),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n[EXCEPTION] {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Test VRP (returns solution for next test)
    vrp_solution = None
    try:
        vrp_solution = test_solve_vrp()
        results.append(("Solve VRP", vrp_solution is not None))
    except Exception as e:
        print(f"\n[EXCEPTION] {e}")
        import traceback
        traceback.print_exc()
        results.append(("Solve VRP", False))

    # Test economics with VRP solution
    try:
        econ_result = test_calculate_economics(vrp_solution if isinstance(vrp_solution, dict) else None)
        results.append(("Calculate Economics", econ_result))
    except Exception as e:
        print(f"\n[EXCEPTION] {e}")
        import traceback
        traceback.print_exc()
        results.append(("Calculate Economics", False))

    # Summary
    print_section("Test Summary")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {name}")

    print(f"\n  Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] All tools working correctly!")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
