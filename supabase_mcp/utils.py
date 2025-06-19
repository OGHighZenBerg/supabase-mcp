"""
Utility functions for the Supabase MCP server.
"""

import logging
from typing import Optional, Dict, Any
from supabase import Client

from .types import OperationResponse, TableData, Filters
from .constants import ResponseStatus
from .exceptions import ValidationError, QueryExecutionError


def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Set up structured logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("supabase_mcp")
    logger.setLevel(getattr(logging, level.upper()))
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def validate_table_name(table_name: str) -> None:
    """
    Validate table name input.
    
    Args:
        table_name: Name of the table to validate
        
    Raises:
        ValidationError: If table name is invalid
    """
    if not table_name or not isinstance(table_name, str) or not table_name.strip():
        raise ValidationError("Table name cannot be empty")


def validate_limit(limit: Optional[int]) -> None:
    """
    Validate limit parameter.
    
    Args:
        limit: Limit value to validate
        
    Raises:
        ValidationError: If limit is invalid
    """
    if limit is not None and (not isinstance(limit, int) or limit <= 0):
        raise ValidationError("Limit must be a positive integer")


def validate_filters(filters: Optional[Filters]) -> None:
    """
    Validate filters parameter.
    
    Args:
        filters: Filters to validate
        
    Raises:
        ValidationError: If filters are invalid
    """
    if filters is not None:
        if not isinstance(filters, dict):
            raise ValidationError("Filters must be a dictionary")
        if not filters:
            raise ValidationError("Filters dictionary cannot be empty")


def validate_updates(updates: Dict[str, Any]) -> None:
    """
    Validate updates parameter.
    
    Args:
        updates: Updates to validate
        
    Raises:
        ValidationError: If updates are invalid
    """
    if not isinstance(updates, dict):
        raise ValidationError("Updates must be a dictionary")
    if not updates:
        raise ValidationError("Updates dictionary cannot be empty")


def create_response(
    data: Optional[TableData] = None,
    status: ResponseStatus = ResponseStatus.SUCCESS,
    message: Optional[str] = None
) -> OperationResponse:
    """
    Create a standardized response object.
    
    Args:
        data: The data to include in the response
        status: Response status
        message: Optional message
        
    Returns:
        Standardized response dictionary
    """
    return {
        "data": data,
        "count": len(data) if data else 0,
        "status": status.value,
        "message": message
    }


def get_supabase_client(ctx) -> Client:
    """
    Extract Supabase client from MCP context.
    
    Args:
        ctx: MCP context object
        
    Returns:
        Supabase client instance
    """
    return ctx.request_context.lifespan_context.client


def apply_filters_to_query(query, filters: Optional[Filters]):
    """
    Apply filters to a Supabase query.
    
    Args:
        query: Supabase query object
        filters: Dictionary of filters to apply
        
    Returns:
        Query object with filters applied
    """
    if filters:
        for column, value in filters.items():
            query = query.eq(column, value)
    return query


def safe_execute_query(query, operation: str, table_name: str) -> Any:
    """
    Safely execute a Supabase query with error handling.
    
    Args:
        query: Supabase query to execute
        operation: Name of the operation being performed
        table_name: Name of the table being queried
        
    Returns:
        Query response
        
    Raises:
        QueryExecutionError: If query execution fails
    """
    try:
        return query.execute()
    except Exception as e:
        raise QueryExecutionError(
            f"Failed to execute {operation} on table '{table_name}': {str(e)}",
            table_name=table_name,
            operation=operation,
            details={"original_error": str(e)}
        )
