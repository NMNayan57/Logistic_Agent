"""
Test script for the Logistics AI Agent API.

This script sends test queries to the running API server.

Usage:
    # Start the API server first in another terminal:
    python scripts/start_api.py

    # Then run this test script:
    python scripts/test_agent_query.py
"""

import requests
import json
import time


def test_health():
    """Test health endpoint."""
    print("\n" + "=" * 60)
    print("Test 1: Health Check")
    print("=" * 60)

    try:
        response = requests.get("http://localhost:8000/health")
        response.raise_for_status()
        data = response.json()

        print("[OK] API is healthy")
        print(f"  - Status: {data['status']}")
        print(f"  - Version: {data['version']}")
        print(f"  - Model: {data['model']}")
        return True

    except Exception as e:
        print(f"[ERROR] Health check failed: {e}")
        return False


def test_stats():
    """Test stats endpoint."""
    print("\n" + "=" * 60)
    print("Test 2: Statistics")
    print("=" * 60)

    try:
        response = requests.get("http://localhost:8000/stats")
        response.raise_for_status()
        data = response.json()

        print("[OK] Statistics retrieved")
        print(f"  - Total queries: {data['api_stats']['total_queries']}")
        print(f"  - Orders in database: {data['database_stats']['orders_count']}")
        print(f"  - Vehicles in database: {data['database_stats']['vehicles_count']}")
        return True

    except Exception as e:
        print(f"[ERROR] Stats check failed: {e}")
        return False


def test_tools_list():
    """Test tools listing endpoint."""
    print("\n" + "=" * 60)
    print("Test 3: List Available Tools")
    print("=" * 60)

    try:
        response = requests.get("http://localhost:8000/tools")
        response.raise_for_status()
        data = response.json()

        print(f"[OK] {data['count']} tools available:")
        for tool in data['tools']:
            print(f"  - {tool['name']}: {tool['description'][:60]}...")
        return True

    except Exception as e:
        print(f"[ERROR] Tools list failed: {e}")
        return False


def test_agent_simple_query():
    """Test simple agent query."""
    print("\n" + "=" * 60)
    print("Test 4: Simple Agent Query")
    print("=" * 60)

    query = {
        "query": "How many orders and vehicles do we have available?",
        "max_iterations": 3,
        "include_explanation": True
    }

    print(f"Query: {query['query']}")
    print("\nSending request...")

    try:
        start_time = time.time()
        response = requests.post(
            "http://localhost:8000/ask",
            json=query,
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        execution_time = time.time() - start_time

        print(f"\n[OK] Query completed in {execution_time:.2f}s")
        print(f"\nAgent Response:")
        print("-" * 60)
        print(data['response_text'])
        print("-" * 60)
        print(f"\nTools called: {', '.join(data['tools_called'])}")
        print(f"Iterations: {data['metadata']['iterations']}")
        print(f"Execution time: {data['execution_time_seconds']:.2f}s")

        return True

    except requests.exceptions.Timeout:
        print("[ERROR] Request timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"[ERROR] Agent query failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_routing_query():
    """Test routing agent query."""
    print("\n" + "=" * 60)
    print("Test 5: Routing Agent Query")
    print("=" * 60)

    query = {
        "query": "Route 5 deliveries with 2 vehicles, minimize distance",
        "max_iterations": 5,
        "include_explanation": True
    }

    print(f"Query: {query['query']}")
    print("\nSending request (this may take 20-30 seconds)...")

    try:
        start_time = time.time()
        response = requests.post(
            "http://localhost:8000/ask",
            json=query,
            timeout=90
        )
        response.raise_for_status()
        data = response.json()
        execution_time = time.time() - start_time

        print(f"\n[OK] Query completed in {execution_time:.2f}s")
        print(f"\nAgent Response:")
        print("-" * 60)
        print(data['response_text'])
        print("-" * 60)
        print(f"\nTools called: {', '.join(data['tools_called'])}")
        print(f"Iterations: {data['metadata']['iterations']}")
        print(f"Execution time: {data['execution_time_seconds']:.2f}s")

        return True

    except requests.exceptions.Timeout:
        print("[ERROR] Request timed out after 90 seconds")
        return False
    except Exception as e:
        print(f"[ERROR] Agent query failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_direct_vrp():
    """Test direct VRP endpoint."""
    print("\n" + "=" * 60)
    print("Test 6: Direct VRP Solver")
    print("=" * 60)

    request_data = {
        "order_ids": ["O001", "O002", "O003", "O004", "O005"],
        "vehicle_ids": ["V001", "V002"],
        "constraints": {},
        "objective": "minimize_distance"
    }

    print(f"Solving VRP for {len(request_data['order_ids'])} orders...")

    try:
        start_time = time.time()
        response = requests.post(
            "http://localhost:8000/solve_vrp_direct",
            json=request_data,
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        execution_time = time.time() - start_time

        print(f"\n[OK] VRP solved in {execution_time:.2f}s")
        print(f"  - Routes: {len(data['routes'])}")
        print(f"  - Status: {data['solver_status']}")
        print(f"  - Execution time: {data['execution_time_seconds']:.2f}s")

        for i, route in enumerate(data['routes'], 1):
            print(f"\n  Route {i}:")
            print(f"    - Vehicle: {route['vehicle_id']}")
            print(f"    - Stops: {len(route['stops'])}")
            print(f"    - Distance: {route['total_distance_km']} km")
            print(f"    - Time: {route['total_time_minutes']} min")
            print(f"    - Cost: ${route['total_cost_usd']}")
            print(f"    - Emissions: {route['emissions_kg']} kg CO2")

        return True

    except Exception as e:
        print(f"[ERROR] Direct VRP failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "#" * 60)
    print("#  Logistics AI Agent - API Testing")
    print("#" * 60)
    print("\nMake sure the API server is running first!")
    print("Start it with: python scripts/start_api.py")
    print()

    input("Press Enter to continue with tests...")

    tests = [
        ("Health Check", test_health),
        ("Statistics", test_stats),
        ("Tools List", test_tools_list),
        ("Simple Agent Query", test_agent_simple_query),
        ("Routing Agent Query", test_agent_routing_query),
        ("Direct VRP Solver", test_direct_vrp),
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

        time.sleep(1)  # Brief pause between tests

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {name}")

    print(f"\n  Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] All tests passed!")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())
