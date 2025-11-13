"""
Depot data model for logistics operations.

This module defines the Depot model representing a distribution center
or warehouse where vehicles start and end their routes.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class Depot(BaseModel):
    """
    Represents a depot/warehouse location.

    Attributes:
        depot_id: Unique depot identifier
        name: Depot name
        latitude: Depot latitude coordinate
        longitude: Depot longitude coordinate
        time_window_start: Depot opening time (minutes from midnight)
        time_window_end: Depot closing time (minutes from midnight)
        address: Optional physical address

    Example:
        >>> depot = Depot(
        ...     depot_id="D001",
        ...     name="Main Distribution Center",
        ...     latitude=40.7580,
        ...     longitude=-73.9855,
        ...     time_window_start=0,     # Midnight
        ...     time_window_end=1440,    # Next midnight
        ...     address="123 Warehouse St, New York, NY"
        ... )
    """

    depot_id: str = Field(
        ...,
        description="Unique depot identifier",
        min_length=1,
        max_length=50
    )

    name: str = Field(
        ...,
        description="Depot name",
        min_length=1,
        max_length=200
    )

    latitude: float = Field(
        ...,
        description="Depot latitude",
        ge=-90.0,
        le=90.0
    )

    longitude: float = Field(
        ...,
        description="Depot longitude",
        ge=-180.0,
        le=180.0
    )

    time_window_start: int = Field(
        default=0,
        description="Opening time (minutes from midnight)",
        ge=0,
        lt=1440
    )

    time_window_end: int = Field(
        default=1440,
        description="Closing time (minutes from midnight)",
        ge=0,
        le=1440
    )

    address: Optional[str] = Field(
        default=None,
        description="Physical address",
        max_length=500
    )

    created_at: Optional[datetime] = Field(
        default=None,
        description="Depot registration timestamp"
    )

    @field_validator("time_window_end")
    @classmethod
    def validate_time_window(cls, v: int, info) -> int:
        """Ensure closing time is after opening time."""
        if "time_window_start" in info.data:
            if v <= info.data["time_window_start"]:
                raise ValueError(
                    f"time_window_end ({v}) must be greater than "
                    f"time_window_start ({info.data['time_window_start']})"
                )
        return v

    def operating_hours(self) -> float:
        """Calculate daily operating hours."""
        return (self.time_window_end - self.time_window_start) / 60.0

    def is_24_7(self) -> bool:
        """Check if depot operates 24/7."""
        return self.time_window_start == 0 and self.time_window_end == 1440

    def __str__(self) -> str:
        """Human-readable string representation."""
        return (
            f"Depot {self.depot_id} ({self.name}): "
            f"hours={self.time_window_start}-{self.time_window_end}min"
        )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "depot_id": "D001",
                "name": "Main Distribution Center",
                "latitude": 40.7580,
                "longitude": -73.9855,
                "time_window_start": 0,
                "time_window_end": 1440,
                "address": "123 Warehouse St, New York, NY"
            }
        }
