"""
Route data model for vehicle routing solutions.

This module defines the Route model representing a vehicle's delivery
route with stops, costs, and constraint satisfaction status.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class Route(BaseModel):
    """
    Represents a vehicle route with stops and performance metrics.

    Attributes:
        vehicle_id: Assigned vehicle identifier
        stops: Ordered list of customer/depot IDs
        total_distance_km: Total route distance (km)
        total_time_minutes: Total route duration (minutes)
        total_cost_usd: Total route cost (USD)
        emissions_kg: Total CO2 emissions (kg)
        load_sequence: Cumulative load at each stop
        time_sequence: Arrival time at each stop (minutes from midnight)
        constraints_satisfied: Whether all constraints are met
        constraint_violations: List of violated constraints

    Example:
        >>> route = Route(
        ...     vehicle_id="V001",
        ...     stops=["D001", "C012", "C005", "D001"],
        ...     total_distance_km=85.3,
        ...     total_time_minutes=245,
        ...     total_cost_usd=127.50,
        ...     emissions_kg=21.3,
        ...     load_sequence=[0, 15, 30, 0],
        ...     time_sequence=[480, 510, 550, 725],
        ...     constraints_satisfied=True,
        ...     constraint_violations=[]
        ... )
    """

    vehicle_id: str = Field(
        ...,
        description="Assigned vehicle identifier",
        min_length=1,
        max_length=50
    )

    stops: List[str] = Field(
        ...,
        description="Ordered list of stop IDs (includes depot)",
        min_length=2  # At minimum: depot -> depot
    )

    total_distance_km: float = Field(
        ...,
        description="Total route distance (km)",
        ge=0.0
    )

    total_time_minutes: float = Field(
        ...,
        description="Total route duration (minutes)",
        ge=0.0
    )

    total_cost_usd: float = Field(
        ...,
        description="Total route cost (USD)",
        ge=0.0
    )

    emissions_kg: float = Field(
        ...,
        description="Total CO2 emissions (kg)",
        ge=0.0
    )

    load_sequence: List[float] = Field(
        ...,
        description="Cumulative load at each stop"
    )

    time_sequence: List[int] = Field(
        ...,
        description="Arrival time at each stop (minutes from midnight)"
    )

    constraints_satisfied: bool = Field(
        ...,
        description="Whether all hard constraints are satisfied"
    )

    constraint_violations: List[str] = Field(
        default_factory=list,
        description="List of violated constraint descriptions"
    )

    num_customers: Optional[int] = Field(
        default=None,
        description="Number of customers served (excluding depot)"
    )

    @field_validator("load_sequence")
    @classmethod
    def validate_load_sequence_length(cls, v: List[float], info) -> List[float]:
        """Ensure load sequence matches stops length."""
        if "stops" in info.data:
            if len(v) != len(info.data["stops"]):
                raise ValueError(
                    f"load_sequence length ({len(v)}) must match "
                    f"stops length ({len(info.data['stops'])})"
                )
        return v

    @field_validator("time_sequence")
    @classmethod
    def validate_time_sequence_length(cls, v: List[int], info) -> List[int]:
        """Ensure time sequence matches stops length."""
        if "stops" in info.data:
            if len(v) != len(info.data["stops"]):
                raise ValueError(
                    f"time_sequence length ({len(v)}) must match "
                    f"stops length ({len(info.data['stops'])})"
                )
        return v

    def num_stops(self) -> int:
        """Get total number of stops (including depot)."""
        return len(self.stops)

    def num_deliveries(self) -> int:
        """Get number of delivery stops (excluding depot stops)."""
        # Count stops that are not depot (assuming depot IDs start with 'D')
        return sum(1 for stop in self.stops if not stop.startswith('D'))

    def avg_distance_per_stop(self) -> float:
        """Calculate average distance per customer stop."""
        deliveries = self.num_deliveries()
        if deliveries == 0:
            return 0.0
        return self.total_distance_km / deliveries

    def is_feasible(self) -> bool:
        """Check if route is feasible (no constraint violations)."""
        return self.constraints_satisfied and len(self.constraint_violations) == 0

    def max_load(self) -> float:
        """Get maximum load on this route."""
        return max(self.load_sequence) if self.load_sequence else 0.0

    def route_duration_hours(self) -> float:
        """Get route duration in hours."""
        return self.total_time_minutes / 60.0

    def __str__(self) -> str:
        """Human-readable string representation."""
        feasible = "✓" if self.is_feasible() else "✗"
        return (
            f"Route {self.vehicle_id} {feasible}: "
            f"{self.num_stops()} stops, "
            f"{self.total_distance_km:.1f}km, "
            f"{self.total_cost_usd:.2f}USD"
        )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "vehicle_id": "V001",
                "stops": ["D001", "C012", "C005", "C018", "D001"],
                "total_distance_km": 85.3,
                "total_time_minutes": 245.0,
                "total_cost_usd": 127.50,
                "emissions_kg": 21.3,
                "load_sequence": [0, 15, 30, 45, 0],
                "time_sequence": [480, 510, 550, 590, 725],
                "constraints_satisfied": True,
                "constraint_violations": []
            }
        }
