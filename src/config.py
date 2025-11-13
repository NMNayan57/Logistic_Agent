"""
Configuration management for Logistics AI Agent.

This module provides centralized configuration using pydantic-settings
for environment variable management and validation.
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings can be overridden via .env file or environment variables.

    Attributes:
        openai_api_key: OpenAI API key for GPT-4
        openai_model: OpenAI model name
        openai_temperature: LLM temperature (0.0 = deterministic)
        database_url: Database connection string
        log_level: Logging level
        max_agent_iterations: Maximum agent reasoning iterations
        agent_timeout: Agent timeout in seconds
        api_host: API server host
        api_port: API server port
        default_fuel_price_per_liter: Default fuel price
        default_driver_wage_per_hour: Default driver wage
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # OpenAI Configuration
    openai_api_key: str = Field(
        ...,
        description="OpenAI API key (required)",
        min_length=20
    )

    openai_model: str = Field(
        default="gpt-4-turbo-preview",
        description="OpenAI model name"
    )

    openai_temperature: float = Field(
        default=0.0,
        description="LLM temperature (0.0-2.0)",
        ge=0.0,
        le=2.0
    )

    # Database Configuration
    database_url: str = Field(
        default="sqlite:///./logistics.db",
        description="Database connection URL"
    )

    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )

    # Agent Configuration
    max_agent_iterations: int = Field(
        default=10,
        description="Maximum agent reasoning iterations",
        ge=1,
        le=15
    )

    agent_timeout: float = Field(
        default=120.0,
        description="Agent timeout in seconds",
        gt=0.0,
        le=300.0
    )

    # API Configuration
    api_host: str = Field(
        default="0.0.0.0",
        description="API server host"
    )

    api_port: int = Field(
        default=8000,
        description="API server port",
        ge=1,
        le=65535
    )

    # Cost Parameters
    default_fuel_price_per_liter: float = Field(
        default=1.5,
        description="Default fuel price (USD per liter)",
        ge=0.0,
        le=100.0
    )

    default_driver_wage_per_hour: float = Field(
        default=15.0,
        description="Default driver wage (USD per hour)",
        ge=0.0,
        le=1000.0
    )

    # OR-Tools Configuration
    ortools_time_limit_seconds: int = Field(
        default=20,
        description="OR-Tools solver time limit",
        ge=1,
        le=300
    )

    ortools_solution_limit: int = Field(
        default=1,
        description="Number of solutions to find",
        ge=1,
        le=10
    )

    # Distance Calculation
    distance_mode: str = Field(
        default="euclidean",
        description="Distance calculation mode (euclidean, manhattan, osrm)"
    )

    # OSRM Configuration (Optional)
    osrm_server_url: Optional[str] = Field(
        default=None,
        description="OSRM server URL for realistic routing"
    )

    # Development Mode
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )

    # CORS Configuration
    cors_allow_origins: list[str] = Field(
        default=["*"],
        description="CORS allowed origins"
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is a valid Python logging level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(
                f"Invalid log level: {v}. Must be one of {valid_levels}"
            )
        return v_upper

    @field_validator("distance_mode")
    @classmethod
    def validate_distance_mode(cls, v: str) -> str:
        """Validate distance mode is supported."""
        valid_modes = ["euclidean", "manhattan", "osrm"]
        v_lower = v.lower()
        if v_lower not in valid_modes:
            raise ValueError(
                f"Invalid distance mode: {v}. Must be one of {valid_modes}"
            )
        return v_lower

    def get_openai_config(self) -> dict:
        """Get OpenAI client configuration."""
        return {
            "api_key": self.openai_api_key,
            "model": self.openai_model,
            "temperature": self.openai_temperature
        }

    def get_agent_config(self) -> dict:
        """Get agent configuration."""
        return {
            "max_iterations": self.max_agent_iterations,
            "max_execution_time": self.agent_timeout,
            "verbose": self.debug
        }

    def get_solver_config(self) -> dict:
        """Get OR-Tools solver configuration."""
        return {
            "time_limit_seconds": self.ortools_time_limit_seconds,
            "solution_limit": self.ortools_solution_limit
        }

    def get_cost_params(self) -> dict:
        """Get default cost parameters."""
        return {
            "fuel_price_per_liter": self.default_fuel_price_per_liter,
            "driver_wage_per_hour": self.default_driver_wage_per_hour
        }

    def __repr__(self) -> str:
        """Safe string representation (hides API key)."""
        return (
            f"Settings("
            f"model={self.openai_model}, "
            f"database={self.database_url}, "
            f"log_level={self.log_level}, "
            f"debug={self.debug}"
            f")"
        )


# Global settings instance
# This will be loaded once and reused throughout the application
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get application settings (singleton pattern).

    Returns:
        Settings instance

    Example:
        >>> from src.config import get_settings
        >>> settings = get_settings()
        >>> print(settings.openai_model)
        'gpt-4-turbo-preview'
    """
    global _settings
    if _settings is None:
        _settings = Settings()  # type: ignore
    return _settings


def reload_settings() -> Settings:
    """
    Reload settings from environment (useful for testing).

    Returns:
        New Settings instance
    """
    global _settings
    _settings = Settings()  # type: ignore
    return _settings


# Convenience function for FastAPI Depends
def get_settings_dependency() -> Settings:
    """
    FastAPI dependency for injecting settings.

    Usage:
        >>> from fastapi import Depends
        >>> def my_endpoint(settings: Settings = Depends(get_settings_dependency)):
        ...     api_key = settings.openai_api_key
    """
    return get_settings()
