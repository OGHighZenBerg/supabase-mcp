"""
Type definitions for the Supabase MCP server.
"""

from typing import Dict, List, Any, Union, Optional, TypedDict
from dataclasses import dataclass

# Type aliases for better readability
TableName = str
ColumnName = str
ColumnValue = Any
Filters = Dict[ColumnName, ColumnValue]
Updates = Dict[ColumnName, ColumnValue]
TableRow = Dict[ColumnName, ColumnValue]
TableData = List[TableRow]

# Record types for database operations
SingleRecord = Dict[str, Any]
MultipleRecords = List[Dict[str, Any]]
Records = Union[SingleRecord, MultipleRecords]

# Response types
class OperationResponse(TypedDict):
    """Standard response format for database operations."""
    data: Optional[TableData]
    count: int
    status: str
    message: Optional[str]

class QueryParams(TypedDict, total=False):
    """Parameters for database queries."""
    columns: str
    filters: Optional[Filters]
    limit: Optional[int]
    order_by: Optional[str]
    ascending: bool

@dataclass
class DatabaseError:
    """Structured error information."""
    operation: str
    table_name: str
    error_type: str
    message: str
    details: Optional[Dict[str, Any]] = None
