"""
Database operations for the Supabase MCP server.

This module contains the core business logic for database operations,
separated from the MCP tool definitions for better maintainability.
"""

import logging
from typing import Optional, Union, Dict, Any, List
from supabase import Client

from .types import (
    TableName, TableData, Filters, Updates, Records,
    OperationResponse, SingleRecord, MultipleRecords
)
from .constants import DEFAULT_COLUMNS, DEFAULT_ASCENDING, ResponseStatus
from .exceptions import ValidationError, QueryExecutionError
from .utils import (
    validate_table_name, validate_limit, validate_filters, validate_updates,
    create_response, apply_filters_to_query, safe_execute_query
)

logger = logging.getLogger("supabase_mcp.database")


class DatabaseOperations:
    """
    Handles all database operations for the Supabase MCP server.
    
    This class encapsulates the business logic for database operations,
    providing a clean interface that can be easily tested and maintained.
    """
    
    def __init__(self, client: Client):
        """
        Initialize database operations with a Supabase client.
        
        Args:
            client: Supabase client instance
        """
        self.client = client
    
    def read_table_rows(
        self,
        table_name: TableName,
        columns: str = DEFAULT_COLUMNS,
        filters: Optional[Filters] = None,
        limit: Optional[int] = None,
        order_by: Optional[str] = None,
        ascending: bool = DEFAULT_ASCENDING
    ) -> TableData:
        """
        Read rows from a Supabase table with optional filtering, ordering, and limiting.
        
        Args:
            table_name: Name of the table to read from
            columns: Comma-separated list of columns to select
            filters: Dictionary of column-value pairs to filter rows
            limit: Maximum number of rows to return
            order_by: Column to order results by
            ascending: Whether to sort in ascending order
            
        Returns:
            List of dictionaries, each representing a row from the table
            
        Raises:
            ValidationError: If input parameters are invalid
            QueryExecutionError: If query execution fails
        """
        # Validate inputs
        validate_table_name(table_name)
        validate_limit(limit)
        validate_filters(filters)
        
        logger.info(f"Reading rows from table '{table_name}' with filters: {filters}")
        
        try:
            # Start building the query
            query = self.client.table(table_name).select(columns)
            
            # Apply filters if provided
            query = apply_filters_to_query(query, filters)
            
            # Apply ordering if provided
            if order_by:
                query = query.order(order_by, ascending=ascending)
            
            # Apply limit if provided
            if limit:
                query = query.limit(limit)
            
            # Execute the query
            response = safe_execute_query(query, "read", table_name)
            
            logger.info(f"Successfully read {len(response.data)} rows from table '{table_name}'")
            return response.data
            
        except Exception as e:
            logger.error(f"Failed to read from table '{table_name}': {str(e)}")
            raise
    
    def create_table_records(
        self,
        table_name: TableName,
        records: Records
    ) -> OperationResponse:
        """
        Create one or multiple records in a Supabase table.
        
        Args:
            table_name: Name of the table to insert records into
            records: A dictionary for a single record or a list of dictionaries for multiple records
            
        Returns:
            Dictionary containing the created records and metadata
            
        Raises:
            ValidationError: If input parameters are invalid
            QueryExecutionError: If query execution fails
        """
        # Validate inputs
        validate_table_name(table_name)
        
        if not records:
            raise ValidationError("Records cannot be empty")
        
        record_count = 1 if isinstance(records, dict) else len(records)
        logger.info(f"Creating {record_count} record(s) in table '{table_name}'")
        
        try:
            # Insert the records
            query = self.client.table(table_name).insert(records)
            response = safe_execute_query(query, "create", table_name)
            
            success = response.data is not None and len(response.data) > 0
            status = ResponseStatus.SUCCESS if success else ResponseStatus.ERROR
            
            logger.info(f"Successfully created {len(response.data or [])} record(s) in table '{table_name}'")
            
            return create_response(
                data=response.data,
                status=status,
                message=f"Created {len(response.data or [])} record(s)" if success else "No records were created"
            )
            
        except Exception as e:
            logger.error(f"Failed to create records in table '{table_name}': {str(e)}")
            raise

    def update_table_records(
        self,
        table_name: TableName,
        updates: Updates,
        filters: Filters
    ) -> OperationResponse:
        """
        Update records in a Supabase table that match the specified filters.

        Args:
            table_name: Name of the table to update records in
            updates: Dictionary of column-value pairs with the new values
            filters: Dictionary of column-value pairs to filter which rows to update

        Returns:
            Dictionary containing the updated records and metadata

        Raises:
            ValidationError: If input parameters are invalid
            QueryExecutionError: If query execution fails
        """
        # Validate inputs
        validate_table_name(table_name)
        validate_updates(updates)
        validate_filters(filters)

        logger.info(f"Updating records in table '{table_name}' with filters: {filters}")

        try:
            # Start building the query
            query = self.client.table(table_name).update(updates)

            # Apply filters
            query = apply_filters_to_query(query, filters)

            # Execute the query
            response = safe_execute_query(query, "update", table_name)

            success = response.data is not None and len(response.data) > 0
            status = ResponseStatus.SUCCESS if success else ResponseStatus.ERROR

            logger.info(f"Successfully updated {len(response.data or [])} record(s) in table '{table_name}'")

            return create_response(
                data=response.data,
                status=status,
                message=f"Updated {len(response.data or [])} record(s)" if success else "No records were updated"
            )

        except Exception as e:
            logger.error(f"Failed to update records in table '{table_name}': {str(e)}")
            raise

    def delete_table_records(
        self,
        table_name: TableName,
        filters: Filters
    ) -> OperationResponse:
        """
        Delete records from a Supabase table that match the specified filters.

        Args:
            table_name: Name of the table to delete records from
            filters: Dictionary of column-value pairs to filter which rows to delete

        Returns:
            Dictionary containing the deleted records and metadata

        Raises:
            ValidationError: If input parameters are invalid
            QueryExecutionError: If query execution fails
        """
        # Validate inputs
        validate_table_name(table_name)
        validate_filters(filters)

        logger.info(f"Deleting records from table '{table_name}' with filters: {filters}")

        try:
            # Start building the query
            query = self.client.table(table_name).delete()

            # Apply filters
            query = apply_filters_to_query(query, filters)

            # Execute the query
            response = safe_execute_query(query, "delete", table_name)

            success = response.data is not None and len(response.data) > 0
            status = ResponseStatus.SUCCESS if success else ResponseStatus.ERROR

            logger.info(f"Successfully deleted {len(response.data or [])} record(s) from table '{table_name}'")

            return create_response(
                data=response.data,
                status=status,
                message=f"Deleted {len(response.data or [])} record(s)" if success else "No records were deleted"
            )

        except Exception as e:
            logger.error(f"Failed to delete records from table '{table_name}': {str(e)}")
            raise
