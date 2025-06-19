"""
Custom exceptions for the Supabase MCP server.
"""

from typing import Optional, Dict, Any


class SupabaseMCPError(Exception):
    """Base exception for Supabase MCP server errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConfigurationError(SupabaseMCPError):
    """Raised when there are configuration issues."""
    pass


class ValidationError(SupabaseMCPError):
    """Raised when input validation fails."""
    pass


class DatabaseConnectionError(SupabaseMCPError):
    """Raised when database connection fails."""
    pass


class QueryExecutionError(SupabaseMCPError):
    """Raised when query execution fails."""
    
    def __init__(self, message: str, table_name: str, operation: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.table_name = table_name
        self.operation = operation


class TableNotFoundError(QueryExecutionError):
    """Raised when a table is not found."""
    pass


class InvalidFilterError(ValidationError):
    """Raised when filters are invalid."""
    pass


class InvalidUpdateError(ValidationError):
    """Raised when update data is invalid."""
    pass
