"""
Order data model for logistics operations.

This module defines the Order model representing a customer delivery request
with spatial, temporal, and capacity constraints.
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class Order(BaseModel):
    """
    Represents a delivery order with constraints.

    Attributes:
        order_id: Unique identifier for the order
        customer_id: Customer identifier
        demand: Quantity to deliver (kg, packages, units)
        service_time: Time required at delivery location (minutes)
        time_window_start: Earliest delivery time (minutes from midnight)
        time_window_end: Latest delivery time (minutes from midnight)
        latitude: Delivery latitude coordinate
        longitude: Delivery longitude coordinate
        is_cold_chain: Whether order requires refrigeration
        priority: Delivery priority level

    Example:
        >>> order = Order(
        ...     order_id="O001",
        ...     customer_id="C001",
        ...     demand=15.5,
        ...     service_time=10,
        ...     time_window_start=480,  # 8:00 AM
        ...     time_window_end=720,    # 12:00 PM
        ...     latitude=40.7128,
        ...     longitude=-74.0060,
        ...     is_cold_chain=True,
        ...     priority="high"
        ... )
    """

    order_id: str = Field(
        ...,
        description="Unique order identifier",
        min_length=1,
        max_length=50
    )

    customer_id: str = Field(
        ...,
        description="Customer identifier",
        min_length=1,
        max_length=50
    )

    demand: float = Field(
        ...,
        description="Demand quantity (kg, packages, units)",
        gt=0.0,
        le=10000.0
    )

    service_time: int = Field(
        ...,
        description="Service time at location (minutes)",
        ge=0,
        le=480  # Max 8 hours service time
    )

    time_window_start: int = Field(
        ...,
        description="Earliest delivery time (minutes from midnight, 0-1439)",
        ge=0,
        lt=1440
    )

    time_window_end: int = Field(
        ...,
        description="Latest delivery time (minutes from midnight, 0-1440)",
        ge=0,
        le=1440
    )

    latitude: float = Field(
        ...,
        description="Delivery location latitude",
        ge=-90.0,
        le=90.0
    )

    longitude: float = Field(
        ...,
        description="Delivery location longitude",
        ge=-180.0,
        le=180.0
    )

    is_cold_chain: bool = Field(
        default=False,
        description="Requires refrigerated transport"
    )

    priority: Literal["low", "medium", "high"] = Field(
        default="medium",
        description="Delivery priority level"
    )

    created_at: Optional[datetime] = Field(
        default=None,
        description="Order creation timestamp"
    )

    @field_validator("time_window_end")
    @classmethod
    def validate_time_window(cls, v: int, info) -> int:
        """Ensure time window end is after start."""
        if "time_window_start" in info.data:
            if v <= info.data["time_window_start"]:
                raise ValueError(
                    f"time_window_end ({v}) must be greater than "
                    f"time_window_start ({info.data['time_window_start']})"
                )
        return v

    def time_window_duration(self) -> int:
        """Calculate time window duration in minutes."""
        return self.time_window_end - self.time_window_start

    def is_flexible(self) -> bool:
        """Check if order has flexible time window (> 4 hours)."""
        return self.time_window_duration() > 240

    def __str__(self) -> str:
        """Human-readable string representation."""
        return (
            f"Order {self.order_id} for {self.customer_id}: "
            f"{self.demand} units, "
            f"TW: {self.time_window_start}-{self.time_window_end}min"
        )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "order_id": "O001",
                "customer_id": "C001",
                "demand": 15.5,
                "service_time": 10,
                "time_window_start": 480,
                "time_window_end": 720,
                "latitude": 40.7128,
                "longitude": -74.0060,
                "is_cold_chain": True,
                "priority": "high"
            }
        }
