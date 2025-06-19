"""
Constants and configuration for the Supabase MCP server.
"""

from enum import Enum
from typing import Final

# Environment variable names
ENV_SUPABASE_URL: Final[str] = "SUPABASE_URL"
ENV_SUPABASE_SERVICE_KEY: Final[str] = "SUPABASE_SERVICE_KEY"

# Default values
DEFAULT_COLUMNS: Final[str] = "*"
DEFAULT_ASCENDING: Final[bool] = True

# Response status constants
class ResponseStatus(str, Enum):
    """Response status enumeration."""
    SUCCESS = "success"
    ERROR = "error"

# Error messages
class ErrorMessages:
    """Centralized error messages."""
    MISSING_ENV_VARS = "Missing environment variables. Please set SUPABASE_URL and SUPABASE_SERVICE_KEY."
    INVALID_TABLE_NAME = "Table name cannot be empty"
    INVALID_LIMIT = "Limit must be a positive integer"
    INVALID_FILTERS = "Filters must be a non-empty dictionary"
    INVALID_UPDATES = "Updates must be a non-empty dictionary"
    QUERY_EXECUTION_FAILED = "Failed to execute query"
    SUPABASE_CONNECTION_FAILED = "Failed to connect to Supabase"

# Server configuration
class ServerConfig:
    """Server configuration constants."""
    NAME = "Supabase Database"
    DESCRIPTION = "MCP server for interacting with Supabase databases"
    VERSION = "0.1.0"
