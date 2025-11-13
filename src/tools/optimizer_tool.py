"""
Optimization tool using Google OR-Tools for Vehicle Routing Problems.

This module provides the core VRP solver using OR-Tools to optimize
vehicle routes with capacity and time window constraints.
"""

from typing import List, Dict, Any, Literal, Optional
import json
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from langchain.tools import tool
from src.database import get_db, OrderDB, VehicleDB, DepotDB
from src.utils.logger import setup_logger
from src.config import get_settings

logger = setup_logger(__name__)


class VRPSolver:
    """
    Vehicle Routing Problem solver using Google OR-Tools.

    Solves VRPTW (VRP with Time Windows) with capacity constraints.
    """

    def __init__(
        self,
        orders: List[Dict[str, Any]],
        vehicles: List[Dict[str, Any]],
        depot: Dict[str, Any],
        distance_matrix: List[List[float]],
        time_matrix: List[List[int]],
        objective: str = "minimize_cost",
        constraints: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize VRP solver.

        Args:
            orders: List of order dictionaries
            vehicles: List of vehicle dictionaries
            depot: Depot dictionary
            distance_matrix: NxN distance matrix (km)
            time_matrix: NxN time matrix (minutes)
            objective: Optimization objective
            constraints: Optional constraints dict including:
                - max_route_time_minutes: Max route duration (default 480)
                - cold_chain_time_limit_minutes: Max cold-chain delivery time (default 120)
                - excluded_order_ids: List of order IDs to avoid/skip (optional)
        """
        self.orders = orders
        self.vehicles = vehicles
        self.depot = depot
        self.distance_matrix = distance_matrix
        self.time_matrix = time_matrix
        self.objective = objective
        self.constraints = constraints or {}

        # Build location list: [depot, order1, order2, ...]
        self.locations = [depot] + orders
        self.num_locations = len(self.locations)

        # Track excluded orders
        self.excluded_order_ids = self.constraints.get('excluded_order_ids', [])
        self.num_vehicles = len(vehicles)

        logger.info(
            f"VRP Problem: {len(orders)} orders, "
            f"{self.num_vehicles} vehicles, "
            f"{self.num_locations} total locations"
        )

    def create_data_model(self) -> Dict[str, Any]:
        """
        Create data model for OR-Tools.

        Returns:
            Data dictionary for routing model
        """
        data = {}

        # Distance matrix
        data["distance_matrix"] = self.distance_matrix
        data["time_matrix"] = self.time_matrix

        # Demands (depot has 0 demand)
        data["demands"] = [0] + [order["demand"] for order in self.orders]

        # Vehicle capacities
        data["vehicle_capacities"] = [v["capacity"] for v in self.vehicles]

        # Time windows (minutes from midnight)
        data["time_windows"] = [
            (self.depot["time_window_start"], self.depot["time_window_end"])
        ] + [
            (order["time_window_start"], order["time_window_end"])
            for order in self.orders
        ]

        # Service times (minutes)
        data["service_times"] = [0] + [order["service_time"] for order in self.orders]

        # Number of vehicles
        data["num_vehicles"] = self.num_vehicles

        # Depot index (always 0)
        data["depot"] = 0

        return data

    def solve(self, time_limit_seconds: int = 20) -> Optional[Dict[str, Any]]:
        """
        Solve the VRP problem.

        Args:
            time_limit_seconds: Maximum solve time

        Returns:
            Solution dictionary or None if no solution found
        """
        logger.info("Starting OR-Tools solver...")

        # Create data model
        data = self.create_data_model()

        # Create routing index manager
        manager = pywrapcp.RoutingIndexManager(
            len(data["distance_matrix"]),
            data["num_vehicles"],
            data["depot"]
        )

        # Create routing model
        routing = pywrapcp.RoutingModel(manager)

        # Create distance callback
        def distance_callback(from_index: int, to_index: int) -> int:
            """Returns the distance between two nodes."""
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return int(data["distance_matrix"][from_node][to_node] * 100)  # Scale for precision

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)

        # Define cost of each arc
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Add capacity constraint
        def demand_callback(from_index: int) -> int:
            """Returns the demand of the node."""
            from_node = manager.IndexToNode(from_index)
            return int(data["demands"][from_node] * 10)  # Scale for precision

        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)

        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            [int(cap * 10) for cap in data["vehicle_capacities"]],  # vehicle maximum capacities
            True,  # start cumul to zero
            "Capacity"
        )

        # Add time window constraint
        def time_callback(from_index: int, to_index: int) -> int:
            """Returns the travel time plus service time."""
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            travel_time = data["time_matrix"][from_node][to_node]
            service_time = data["service_times"][from_node]
            return travel_time + service_time

        time_callback_index = routing.RegisterTransitCallback(time_callback)

        # Parse constraints for max route time (used for validation later)
        self.max_route_time = 480  # Default: 8 hours (driver overtime limit)
        if hasattr(self, 'constraints') and self.constraints:
            self.max_route_time = self.constraints.get('max_route_time_minutes', 480)

        # Calculate dimension capacity: must be at least as large as max time window
        max_time_window = max(tw[1] for tw in data["time_windows"])
        dimension_capacity = max(max_time_window, self.max_route_time)

        routing.AddDimension(
            time_callback_index,
            30,  # allow waiting time (30 minutes slack)
            dimension_capacity,  # large enough to accommodate time windows
            False,  # don't force start cumul to zero
            "Time"
        )

        # Add time window constraints for each location
        time_dimension = routing.GetDimensionOrDie("Time")
        for location_idx, time_window in enumerate(data["time_windows"]):
            if location_idx == data["depot"]:
                continue  # Skip depot
            index = manager.NodeToIndex(location_idx)
            time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])

        # Add time window constraints for depot (vehicles must return)
        depot_idx = data["depot"]
        for vehicle_id in range(data["num_vehicles"]):
            index = routing.Start(vehicle_id)
            time_dimension.CumulVar(index).SetRange(
                data["time_windows"][depot_idx][0],
                data["time_windows"][depot_idx][1]
            )

        # Handle excluded locations (route avoidance)
        if self.excluded_order_ids:
            logger.info(f"Excluding {len(self.excluded_order_ids)} locations from routes")
            for order_idx, order in enumerate(self.orders):
                if order["order_id"] in self.excluded_order_ids:
                    # Node index in routing model (depot=0, so orders start at index 1)
                    node_index = order_idx + 1
                    routing_index = manager.NodeToIndex(node_index)

                    # Make this node optional (can be dropped from routes)
                    # Penalty for dropping = very high to prefer visiting if possible
                    # But still allows avoidance if explicitly requested
                    penalty = 1000000  # Very high penalty
                    routing.AddDisjunction([routing_index], penalty)
                    logger.info(f"Order {order['order_id']} marked as optional (excluded)")

        # Set first solution strategy
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )

        # Set local search metaheuristic
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )

        # Set time limit
        search_parameters.time_limit.seconds = time_limit_seconds

        logger.info(f"Solving with time limit: {time_limit_seconds}s")

        # Solve the problem
        solution = routing.SolveWithParameters(search_parameters)

        if solution:
            logger.info("Solution found!")
            return self.extract_solution(data, manager, routing, solution)
        else:
            logger.warning("No solution found within time limit")
            return None

    def extract_solution(
        self,
        data: Dict[str, Any],
        manager: pywrapcp.RoutingIndexManager,
        routing: pywrapcp.RoutingModel,
        solution: pywrapcp.Assignment
    ) -> Dict[str, Any]:
        """
        Extract solution from OR-Tools result.

        Args:
            data: Data model
            manager: Routing index manager
            routing: Routing model
            solution: Solution assignment

        Returns:
            Dictionary with routes and metrics
        """
        routes = []
        total_distance = 0
        total_time = 0
        total_load = 0

        time_dimension = routing.GetDimensionOrDie("Time")
        capacity_dimension = routing.GetDimensionOrDie("Capacity")

        for vehicle_id in range(data["num_vehicles"]):
            index = routing.Start(vehicle_id)
            route_distance = 0
            route_time = 0
            route_load = 0

            stops = []
            load_sequence = []
            time_sequence = []

            # Follow the route
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)

                # Get current load and time
                load_var = capacity_dimension.CumulVar(index)
                time_var = time_dimension.CumulVar(index)

                current_load = solution.Value(load_var) / 10.0  # Unscale
                current_time = solution.Value(time_var)

                # Add to route
                if node_index == 0:
                    stops.append(self.depot["depot_id"])
                else:
                    stops.append(self.orders[node_index - 1]["order_id"])

                load_sequence.append(current_load)
                time_sequence.append(current_time)

                # Move to next node
                previous_index = index
                index = solution.Value(routing.NextVar(index))

                # Accumulate distance
                from_node = manager.IndexToNode(previous_index)
                to_node = manager.IndexToNode(index)
                route_distance += data["distance_matrix"][from_node][to_node]

            # Add final depot visit
            node_index = manager.IndexToNode(index)
            load_var = capacity_dimension.CumulVar(index)
            time_var = time_dimension.CumulVar(index)

            stops.append(self.depot["depot_id"])
            load_sequence.append(solution.Value(load_var) / 10.0)
            time_sequence.append(solution.Value(time_var))

            # Calculate route time (end time - start time)
            route_time = time_sequence[-1] - time_sequence[0]

            # Only include routes that visit customers
            if len(stops) > 2:  # More than just depot->depot
                route_info = {
                    "vehicle_id": self.vehicles[vehicle_id]["vehicle_id"],
                    "stops": stops,
                    "distance_km": round(route_distance, 2),
                    "time_minutes": int(route_time),
                    "num_stops": len(stops),
                    "load_sequence": [round(l, 1) for l in load_sequence],
                    "time_sequence": time_sequence,
                    "max_load": round(max(load_sequence), 1),
                    "vehicle_info": self.vehicles[vehicle_id]
                }

                routes.append(route_info)

                total_distance += route_distance
                total_time += route_time
                total_load += max(load_sequence)

        result = {
            "routes": routes,
            "num_routes": len(routes),
            "total_distance_km": round(total_distance, 2),
            "total_time_minutes": int(total_time),
            "objective_value": solution.ObjectiveValue() / 100.0,  # Unscale
            "solver_status": "OPTIMAL" if routing.status() == 1 else "FEASIBLE"  # 1 = ROUTING_OPTIMAL
        }

        # Validate constraints
        violations = self.validate_constraints(routes)
        result["constraint_violations"] = violations
        result["all_constraints_satisfied"] = len(violations) == 0

        logger.info(
            f"Solution: {len(routes)} routes, "
            f"distance={total_distance:.1f}km, "
            f"time={total_time:.0f}min"
        )

        if violations:
            logger.warning(f"Constraint violations detected: {len(violations)} issues")

        return result

    def validate_constraints(self, routes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate routes against operational constraints.

        Args:
            routes: List of route dictionaries

        Returns:
            List of constraint violations
        """
        violations = []

        # Get constraint limits
        max_driver_time = self.max_route_time if hasattr(self, 'max_route_time') else 480  # 8 hours
        cold_chain_limit = self.constraints.get('cold_chain_time_limit_minutes', 120) if hasattr(self, 'constraints') and self.constraints else 120  # 2 hours

        for route in routes:
            vehicle_id = route["vehicle_id"]
            route_time = route["time_minutes"]
            stops = route["stops"]
            time_sequence = route["time_sequence"]

            # Check 1: Driver overtime violation
            if route_time > max_driver_time:
                overtime = route_time - max_driver_time
                violations.append({
                    "type": "driver_overtime",
                    "severity": "high",
                    "vehicle_id": vehicle_id,
                    "route_time_minutes": route_time,
                    "max_allowed_minutes": max_driver_time,
                    "overtime_minutes": overtime,
                    "message": f"Route exceeds {max_driver_time/60:.1f}-hour driver limit by {overtime} minutes ({overtime/60:.1f} hours)"
                })

            # Check 2: Cold-chain delivery time violations
            for i, stop in enumerate(stops):
                if stop == self.depot["depot_id"]:
                    continue  # Skip depot

                # Find the order
                order_idx = None
                for j, order in enumerate(self.orders):
                    if order["order_id"] == stop:
                        order_idx = j
                        break

                if order_idx is not None:
                    order = self.orders[order_idx]

                    # Check if this is a cold-chain order
                    if order.get("is_cold_chain", False):
                        delivery_time = time_sequence[i]  # Time when arriving at this stop

                        if delivery_time > cold_chain_limit:
                            violations.append({
                                "type": "cold_chain_violation",
                                "severity": "critical",
                                "vehicle_id": vehicle_id,
                                "order_id": stop,
                                "delivery_time_minutes": delivery_time,
                                "max_allowed_minutes": cold_chain_limit,
                                "excess_time_minutes": delivery_time - cold_chain_limit,
                                "message": f"Cold-chain order {stop} delivered after {delivery_time} min (limit: {cold_chain_limit} min = {cold_chain_limit/60:.1f} hours)"
                            })

        return violations


@tool
def solve_vrp(
    order_ids: str,
    vehicle_ids: str,
    constraints: Optional[str] = None,
    objective: str = "minimize_cost"
) -> str:
    """
    Solve Vehicle Routing Problem using OR-Tools.

    This tool optimizes vehicle routes to minimize cost while respecting
    capacity and time window constraints.

    Args:
        order_ids: JSON string of order IDs to route.
                  Format: '["O001", "O002", "O003"]'
        vehicle_ids: JSON string of vehicle IDs to use.
                    Format: '["V001", "V002"]'
        constraints: Optional JSON string of constraints including:
                    - max_route_time_minutes: Max route duration (default 480)
                    - cold_chain_time_limit_minutes: Max cold-chain time (default 120)
                    - excluded_order_ids: List of order IDs to avoid
                    Format: '{"max_route_time_minutes": 480, "excluded_order_ids": ["O003"]}'
        objective: Optimization objective.
                  Options: "minimize_cost", "minimize_distance",
                          "minimize_time", "minimize_emissions"
                  Default: "minimize_cost"

    Returns:
        JSON string with routes and performance metrics.
        Format: {
            "routes": [
                {
                    "vehicle_id": "V001",
                    "stops": ["D001", "C012", "C005", "D001"],
                    "distance_km": 85.3,
                    "time_minutes": 245,
                    ...
                }
            ],
            "total_distance_km": 245.0,
            "total_time_minutes": 750,
            "solver_status": "OPTIMAL"
        }

    Example:
        >>> result = solve_vrp.invoke({
        ...     "order_ids": '["O001", "O002", "O003"]',
        ...     "vehicle_ids": '["V001", "V002"]',
        ...     "objective": "minimize_distance"
        ... })
    """
    logger.info(f"Solving VRP (objective={objective})")

    try:
        # Parse input
        order_ids_list = json.loads(order_ids)
        vehicle_ids_list = json.loads(vehicle_ids)

        if constraints:
            constraints_dict = json.loads(constraints)
        else:
            constraints_dict = {}

        logger.debug(f"Orders: {len(order_ids_list)}, Vehicles: {len(vehicle_ids_list)}")

        # Get database session
        db = next(get_db())

        try:
            # Fetch orders from database
            orders_db = db.query(OrderDB).filter(OrderDB.order_id.in_(order_ids_list)).all()

            if len(orders_db) != len(order_ids_list):
                logger.warning(f"Found {len(orders_db)} orders, expected {len(order_ids_list)}")

            orders = []
            for order_db in orders_db:
                orders.append({
                    "order_id": order_db.order_id,
                    "customer_id": order_db.customer_id,
                    "demand": order_db.demand,
                    "service_time": order_db.service_time,
                    "time_window_start": order_db.time_window_start,
                    "time_window_end": order_db.time_window_end,
                    "latitude": order_db.latitude,
                    "longitude": order_db.longitude,
                    "is_cold_chain": order_db.is_cold_chain,
                    "priority": order_db.priority
                })

            # Fetch vehicles from database
            vehicles_db = db.query(VehicleDB).filter(VehicleDB.vehicle_id.in_(vehicle_ids_list)).all()

            if len(vehicles_db) != len(vehicle_ids_list):
                logger.warning(f"Found {len(vehicles_db)} vehicles, expected {len(vehicle_ids_list)}")

            vehicles = []
            for vehicle_db in vehicles_db:
                vehicles.append({
                    "vehicle_id": vehicle_db.vehicle_id,
                    "capacity": vehicle_db.capacity,
                    "max_working_hours": vehicle_db.max_working_hours,
                    "cost_per_km": vehicle_db.cost_per_km,
                    "fixed_cost": vehicle_db.fixed_cost,
                    "emissions_factor": vehicle_db.emissions_factor,
                    "speed_kmh": vehicle_db.speed_kmh
                })

            # Fetch depot
            depot_db = db.query(DepotDB).first()

            if not depot_db:
                raise ValueError("No depot found in database")

            depot = {
                "depot_id": depot_db.depot_id,
                "name": depot_db.name,
                "latitude": depot_db.latitude,
                "longitude": depot_db.longitude,
                "time_window_start": depot_db.time_window_start,
                "time_window_end": depot_db.time_window_end
            }

            # Build location list for distance calculation
            locations = [[depot["latitude"], depot["longitude"]]]
            for order in orders:
                locations.append([order["latitude"], order["longitude"]])

            # Calculate distance matrix (using Euclidean for now)
            from src.tools.routing_tool import calculate_distance_matrix as calc_dist
            dist_result = calc_dist.invoke({
                "locations": json.dumps(locations),
                "mode": "euclidean"
            })

            dist_data = json.loads(dist_result)

            if "error" in dist_data:
                raise ValueError(f"Distance calculation failed: {dist_data['error']}")

            distance_matrix = dist_data["distance_matrix"]
            time_matrix = dist_data["time_matrix"]

            # Create solver
            solver = VRPSolver(
                orders=orders,
                vehicles=vehicles,
                depot=depot,
                distance_matrix=distance_matrix,
                time_matrix=time_matrix,
                objective=objective,
                constraints=constraints_dict
            )

            # Solve
            settings = get_settings()
            time_limit = constraints_dict.get("time_limit", settings.ortools_time_limit_seconds)

            solution = solver.solve(time_limit_seconds=time_limit)

            if solution:
                return json.dumps(solution)
            else:
                return json.dumps({
                    "error": "No solution found within time limit",
                    "routes": [],
                    "solver_status": "INFEASIBLE"
                })

        finally:
            db.close()

    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON format: {e}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg, "routes": []})

    except Exception as e:
        error_msg = f"Error solving VRP: {e}"
        logger.error(error_msg)
        import traceback
        logger.error(traceback.format_exc())
        return json.dumps({"error": error_msg, "routes": []})
