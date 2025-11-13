"""
Vehicle data model for fleet management.

This module defines the Vehicle model representing a delivery vehicle
with capacity, cost, and operational constraints.
"""

from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class Vehicle(BaseModel):
    """
    Represents a delivery vehicle with operational constraints.

    Attributes:
        vehicle_id: Unique vehicle identifier
        capacity: Maximum load capacity (same units as order demand)
        max_working_hours: Maximum shift duration (hours)
        cost_per_km: Variable cost per kilometer (USD)
        fixed_cost: Fixed daily cost (USD)
        emissions_factor: CO2 emissions per km (kg CO2/km)
        speed_kmh: Average speed (km/h)
        available: Whether vehicle is available for assignment

    Example:
        >>> vehicle = Vehicle(
        ...     vehicle_id="V001",
        ...     capacity=100.0,
        ...     max_working_hours=8.0,
        ...     cost_per_km=2.50,
        ...     fixed_cost=50.0,
        ...     emissions_factor=0.25,
        ...     speed_kmh=50.0,
        ...     available=True
        ... )
    """

    vehicle_id: str = Field(
        ...,
        description="Unique vehicle identifier",
        min_length=1,
        max_length=50
    )

    capacity: float = Field(
        ...,
        description="Maximum load capacity (units)",
        gt=0.0,
        le=50000.0  # Max 50 tons
    )

    max_working_hours: float = Field(
        ...,
        description="Maximum working hours per shift",
        gt=0.0,
        le=24.0
    )

    cost_per_km: float = Field(
        ...,
        description="Variable cost per kilometer (USD)",
        ge=0.0,
        le=100.0
    )

    fixed_cost: float = Field(
        ...,
        description="Fixed daily cost (USD)",
        ge=0.0,
        le=10000.0
    )

    emissions_factor: float = Field(
        ...,
        description="CO2 emissions per km (kg CO2/km)",
        ge=0.0,
        le=10.0
    )

    speed_kmh: float = Field(
        default=50.0,
        description="Average speed (km/h)",
        gt=0.0,
        le=120.0
    )

    available: bool = Field(
        default=True,
        description="Vehicle availability status"
    )

    vehicle_type: Optional[str] = Field(
        default=None,
        description="Vehicle type (e.g., 'van', 'truck', 'refrigerated')"
    )

    created_at: Optional[datetime] = Field(
        default=None,
        description="Vehicle registration timestamp"
    )

    def calculate_travel_time(self, distance_km: float) -> float:
        """
        Calculate travel time for given distance.

        Args:
            distance_km: Distance to travel (km)

        Returns:
            Travel time in minutes
        """
        return (distance_km / self.speed_kmh) * 60.0

    def calculate_variable_cost(self, distance_km: float) -> float:
        """
        Calculate variable cost for given distance.

        Args:
            distance_km: Distance traveled (km)

        Returns:
            Variable cost in USD
        """
        return distance_km * self.cost_per_km

    def calculate_emissions(self, distance_km: float) -> float:
        """
        Calculate CO2 emissions for given distance.

        Args:
            distance_km: Distance traveled (km)

        Returns:
            CO2 emissions in kg
        """
        return distance_km * self.emissions_factor

    def max_working_minutes(self) -> float:
        """Get maximum working time in minutes."""
        return self.max_working_hours * 60.0

    def __str__(self) -> str:
        """Human-readable string representation."""
        status = "Available" if self.available else "Unavailable"
        return (
            f"Vehicle {self.vehicle_id}: "
            f"capacity={self.capacity}, "
            f"max_hours={self.max_working_hours}, "
            f"status={status}"
        )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "vehicle_id": "V001",
                "capacity": 100.0,
                "max_working_hours": 8.0,
                "cost_per_km": 2.50,
                "fixed_cost": 50.0,
                "emissions_factor": 0.25,
                "speed_kmh": 50.0,
                "available": True,
                "vehicle_type": "van"
            }
        }
