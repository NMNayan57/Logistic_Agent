"""
Routing tool for distance and time matrix calculations.

This module provides distance calculation functions using various methods:
- Euclidean: Fast approximate distance for small regions
- Manhattan: Grid-based distance (useful for city blocks)
- OSRM: Realistic road network routing (requires OSRM server)
"""

from typing import List, Tuple, Literal, Dict, Any
import numpy as np
import json
import httpx
from langchain.tools import tool
from src.utils.logger import setup_logger
from src.config import get_settings

logger = setup_logger(__name__)


def calculate_euclidean_distance(
    coord1: Tuple[float, float],
    coord2: Tuple[float, float]
) -> float:
    """
    Calculate Euclidean distance between two coordinates.

    Uses the Haversine-approximation for lat/lon coordinates.
    Accurate for small distances (<100km).

    Args:
        coord1: (latitude, longitude) tuple
        coord2: (latitude, longitude) tuple

    Returns:
        Distance in kilometers
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    # Simple Euclidean distance with lat/lon scaling
    # ~111 km per degree at equator
    lat_diff = (lat2 - lat1) * 111.0
    lon_diff = (lon2 - lon1) * 111.0 * np.cos(np.radians((lat1 + lat2) / 2))

    distance = np.sqrt(lat_diff**2 + lon_diff**2)
    return float(distance)


def calculate_manhattan_distance(
    coord1: Tuple[float, float],
    coord2: Tuple[float, float]
) -> float:
    """
    Calculate Manhattan (grid) distance between two coordinates.

    Useful for city grid layouts where diagonal travel is restricted.

    Args:
        coord1: (latitude, longitude) tuple
        coord2: (latitude, longitude) tuple

    Returns:
        Distance in kilometers
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    # Manhattan distance with lat/lon scaling
    lat_diff = abs(lat2 - lat1) * 111.0
    lon_diff = abs(lon2 - lon1) * 111.0 * np.cos(np.radians((lat1 + lat2) / 2))

    distance = lat_diff + lon_diff
    return float(distance)


async def calculate_osrm_distance(
    coord1: Tuple[float, float],
    coord2: Tuple[float, float],
    osrm_server_url: str = "http://router.project-osrm.org"
) -> Tuple[float, float]:
    """
    Calculate realistic road distance using OSRM API.

    Requires OSRM server (local or public).

    Args:
        coord1: (latitude, longitude) tuple
        coord2: (latitude, longitude) tuple
        osrm_server_url: OSRM server URL

    Returns:
        Tuple of (distance_km, duration_minutes)

    Raises:
        httpx.HTTPError: If OSRM server is unreachable
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    # OSRM expects lon,lat format
    url = f"{osrm_server_url}/route/v1/driving/{lon1},{lat1};{lon2},{lat2}"
    params = {"overview": "false", "alternatives": "false"}

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    if data.get("code") != "Ok":
        raise ValueError(f"OSRM routing failed: {data.get('message')}")

    route = data["routes"][0]
    distance_km = route["distance"] / 1000.0  # meters to km
    duration_minutes = route["duration"] / 60.0  # seconds to minutes

    return distance_km, duration_minutes


@tool
def calculate_distance_matrix(
    locations: str,
    mode: str = "euclidean"
) -> str:
    """
    Calculate distance and time matrices between locations.

    This tool computes pairwise distances and travel times for a set of
    coordinates. Used by the VRP solver to build routing solutions.

    Args:
        locations: JSON string of location coordinates.
                  Format: [[lat1, lon1], [lat2, lon2], ...]
                  Example: "[[40.7128, -74.0060], [40.7580, -73.9855]]"
        mode: Distance calculation method.
              Options: "euclidean", "manhattan", "osrm"
              Default: "euclidean"

    Returns:
        JSON string with distance_matrix (km) and time_matrix (minutes).
        Format: {
            "distance_matrix": [[0, d12, ...], [d21, 0, ...], ...],
            "time_matrix": [[0, t12, ...], [t21, 0, ...], ...],
            "mode": "euclidean",
            "num_locations": 10
        }

    Example:
        >>> locations = "[[40.7128, -74.0060], [40.7580, -73.9855]]"
        >>> result = calculate_distance_matrix.invoke({"locations": locations})
        >>> data = json.loads(result)
        >>> print(data["distance_matrix"])
        [[0.0, 5.82], [5.82, 0.0]]
    """
    logger.info(f"Calculating distance matrix (mode={mode})")

    try:
        # Parse locations
        locations_list = json.loads(locations)
        n = len(locations_list)

        if n < 2:
            raise ValueError("Need at least 2 locations to calculate distance matrix")

        logger.debug(f"Processing {n} locations")

        # Initialize matrices
        distance_matrix = np.zeros((n, n))
        time_matrix = np.zeros((n, n))

        # Get settings
        settings = get_settings()
        avg_speed_kmh = 50.0  # Default speed

        # Calculate pairwise distances
        if mode.lower() == "euclidean":
            for i in range(n):
                for j in range(n):
                    if i != j:
                        coord1 = tuple(locations_list[i])
                        coord2 = tuple(locations_list[j])
                        distance = calculate_euclidean_distance(coord1, coord2)
                        distance_matrix[i, j] = distance

        elif mode.lower() == "manhattan":
            for i in range(n):
                for j in range(n):
                    if i != j:
                        coord1 = tuple(locations_list[i])
                        coord2 = tuple(locations_list[j])
                        distance = calculate_manhattan_distance(coord1, coord2)
                        distance_matrix[i, j] = distance

        elif mode.lower() == "osrm":
            raise NotImplementedError(
                "OSRM mode requires async support. "
                "Use 'euclidean' or 'manhattan' for now."
            )

        else:
            raise ValueError(
                f"Invalid mode: {mode}. Must be 'euclidean', 'manhattan', or 'osrm'"
            )

        # Calculate time matrix (distance / speed)
        time_matrix = (distance_matrix / avg_speed_kmh * 60).astype(int)

        # Build result
        result = {
            "distance_matrix": distance_matrix.tolist(),
            "time_matrix": time_matrix.tolist(),
            "mode": mode.lower(),
            "num_locations": n,
            "avg_speed_kmh": avg_speed_kmh
        }

        logger.info(f"Distance matrix calculated: {n}x{n} locations")
        return json.dumps(result)

    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON format for locations: {e}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})

    except Exception as e:
        error_msg = f"Error calculating distance matrix: {e}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})


def extract_locations_from_orders(orders: List[Dict[str, Any]]) -> List[List[float]]:
    """
    Extract location coordinates from order dictionaries.

    Args:
        orders: List of order dictionaries with 'latitude' and 'longitude' keys

    Returns:
        List of [latitude, longitude] pairs
    """
    locations = []
    for order in orders:
        lat = order.get("latitude")
        lon = order.get("longitude")
        if lat is not None and lon is not None:
            locations.append([lat, lon])
    return locations


def get_distance_between_points(
    matrix: List[List[float]],
    from_idx: int,
    to_idx: int
) -> float:
    """
    Get distance between two points from a distance matrix.

    Args:
        matrix: Distance matrix
        from_idx: Starting point index
        to_idx: Destination point index

    Returns:
        Distance value
    """
    return matrix[from_idx][to_idx]
