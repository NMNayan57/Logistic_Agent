"""
Database models and connection management.

This module provides SQLAlchemy ORM models for persistent storage
of orders, vehicles, depots, and route history.
"""

import os
from typing import Generator
from datetime import datetime
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Text,
    JSON,
    DateTime,
    Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URL from environment or default to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./logistics.db")

# Create engine
# For SQLite, we need check_same_thread=False to allow multi-threading
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,  # Set to True for SQL logging during development
    pool_pre_ping=True  # Verify connections before using them
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for ORM models
Base = declarative_base()


# ============================================================================
# ORM Models
# ============================================================================

class OrderDB(Base):
    """
    SQLAlchemy model for orders table.

    Stores customer delivery orders with spatial and temporal constraints.
    """
    __tablename__ = "orders"

    # Primary key
    order_id = Column(String(50), primary_key=True, index=True)

    # Customer information
    customer_id = Column(String(50), nullable=False, index=True)

    # Demand and service
    demand = Column(Float, nullable=False)
    service_time = Column(Integer, nullable=False)

    # Time windows (minutes from midnight)
    time_window_start = Column(Integer, nullable=False)
    time_window_end = Column(Integer, nullable=False)

    # Location
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    # Special requirements
    is_cold_chain = Column(Boolean, default=False, index=True)
    priority = Column(String(20), default="medium", index=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Additional indexes for common queries
    __table_args__ = (
        Index('idx_time_window', 'time_window_start', 'time_window_end'),
        Index('idx_location', 'latitude', 'longitude'),
    )

    def __repr__(self) -> str:
        return f"<OrderDB(order_id={self.order_id}, customer={self.customer_id})>"


class VehicleDB(Base):
    """
    SQLAlchemy model for vehicles table.

    Stores fleet vehicle information with capacity and cost parameters.
    """
    __tablename__ = "vehicles"

    # Primary key
    vehicle_id = Column(String(50), primary_key=True, index=True)

    # Capacity constraints
    capacity = Column(Float, nullable=False)
    max_working_hours = Column(Float, nullable=False)

    # Cost parameters
    cost_per_km = Column(Float, nullable=False)
    fixed_cost = Column(Float, nullable=False)

    # Environmental impact
    emissions_factor = Column(Float, nullable=False)

    # Operational parameters
    speed_kmh = Column(Float, default=50.0, nullable=False)
    available = Column(Boolean, default=True, index=True)

    # Additional info
    vehicle_type = Column(String(50), nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<VehicleDB(vehicle_id={self.vehicle_id}, available={self.available})>"


class DepotDB(Base):
    """
    SQLAlchemy model for depots table.

    Stores distribution center locations and operating hours.
    """
    __tablename__ = "depots"

    # Primary key
    depot_id = Column(String(50), primary_key=True, index=True)

    # Basic information
    name = Column(String(200), nullable=False)

    # Location
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    # Operating hours (minutes from midnight)
    time_window_start = Column(Integer, default=0, nullable=False)
    time_window_end = Column(Integer, default=1440, nullable=False)

    # Additional info
    address = Column(String(500), nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<DepotDB(depot_id={self.depot_id}, name={self.name})>"


class RouteHistoryDB(Base):
    """
    SQLAlchemy model for routes_history table.

    Stores historical routing solutions for analysis and comparison.
    """
    __tablename__ = "routes_history"

    # Primary key
    route_id = Column(String(50), primary_key=True, index=True)

    # Query information
    query = Column(Text, nullable=False)

    # Solution data (stored as JSON)
    solution = Column(JSON, nullable=False)

    # Performance metrics
    total_cost = Column(Float, nullable=False, index=True)
    total_distance = Column(Float, nullable=False)
    total_emissions = Column(Float, nullable=False)
    execution_time = Column(Float, nullable=False)

    # Agent metadata (stored as JSON)
    agent_metadata = Column(JSON, nullable=True)

    # Tools used (stored as JSON array)
    tools_called = Column(JSON, nullable=True)

    # Success indicator
    success = Column(Boolean, default=True, index=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<RouteHistoryDB(route_id={self.route_id}, cost={self.total_cost})>"


# ============================================================================
# Database Utilities
# ============================================================================

def init_database() -> None:
    """
    Initialize database by creating all tables.

    This should be called once during application setup.
    """
    Base.metadata.create_all(bind=engine)
    print(f"[OK] Database initialized at: {DATABASE_URL}")


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.

    Yields a database session and ensures it's properly closed.

    Usage:
        >>> from fastapi import Depends
        >>> def my_endpoint(db: Session = Depends(get_db)):
        ...     orders = db.query(OrderDB).all()

    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def drop_all_tables() -> None:
    """
    Drop all tables from the database.

    WARNING: This will delete all data! Use only for testing/development.
    """
    print("[WARNING] Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("[OK] All tables dropped")


def reset_database() -> None:
    """
    Reset database by dropping and recreating all tables.

    WARNING: This will delete all data! Use only for testing/development.
    """
    print("[INFO] Resetting database...")
    drop_all_tables()
    init_database()
    print("[OK] Database reset complete")


# ============================================================================
# Conversion Utilities (Pydantic ↔ SQLAlchemy)
# ============================================================================

def order_to_dict(order_db: OrderDB) -> dict:
    """
    Convert OrderDB instance to dictionary.

    Args:
        order_db: SQLAlchemy OrderDB instance

    Returns:
        Dictionary representation
    """
    return {
        "order_id": order_db.order_id,
        "customer_id": order_db.customer_id,
        "demand": order_db.demand,
        "service_time": order_db.service_time,
        "time_window_start": order_db.time_window_start,
        "time_window_end": order_db.time_window_end,
        "latitude": order_db.latitude,
        "longitude": order_db.longitude,
        "is_cold_chain": order_db.is_cold_chain,
        "priority": order_db.priority,
        "created_at": order_db.created_at.isoformat() if order_db.created_at else None
    }


def vehicle_to_dict(vehicle_db: VehicleDB) -> dict:
    """
    Convert VehicleDB instance to dictionary.

    Args:
        vehicle_db: SQLAlchemy VehicleDB instance

    Returns:
        Dictionary representation
    """
    return {
        "vehicle_id": vehicle_db.vehicle_id,
        "capacity": vehicle_db.capacity,
        "max_working_hours": vehicle_db.max_working_hours,
        "cost_per_km": vehicle_db.cost_per_km,
        "fixed_cost": vehicle_db.fixed_cost,
        "emissions_factor": vehicle_db.emissions_factor,
        "speed_kmh": vehicle_db.speed_kmh,
        "available": vehicle_db.available,
        "vehicle_type": vehicle_db.vehicle_type,
        "created_at": vehicle_db.created_at.isoformat() if vehicle_db.created_at else None
    }


def depot_to_dict(depot_db: DepotDB) -> dict:
    """
    Convert DepotDB instance to dictionary.

    Args:
        depot_db: SQLAlchemy DepotDB instance

    Returns:
        Dictionary representation
    """
    return {
        "depot_id": depot_db.depot_id,
        "name": depot_db.name,
        "latitude": depot_db.latitude,
        "longitude": depot_db.longitude,
        "time_window_start": depot_db.time_window_start,
        "time_window_end": depot_db.time_window_end,
        "address": depot_db.address,
        "created_at": depot_db.created_at.isoformat() if depot_db.created_at else None
    }


# ============================================================================
# Database Information
# ============================================================================

def get_database_stats(db: Session) -> dict:
    """
    Get database statistics.

    Args:
        db: Database session

    Returns:
        Dictionary with counts of each table
    """
    return {
        "orders_count": db.query(OrderDB).count(),
        "vehicles_count": db.query(VehicleDB).count(),
        "depots_count": db.query(DepotDB).count(),
        "routes_history_count": db.query(RouteHistoryDB).count(),
        "database_url": DATABASE_URL
    }


# Initialize database on module import (creates tables if they don't exist)
if __name__ != "__main__":
    # Only auto-initialize if not running as script
    try:
        init_database()
    except Exception as e:
        print(f"[WARNING] Database initialization warning: {e}")
