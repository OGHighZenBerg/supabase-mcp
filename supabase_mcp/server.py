"""
Supabase MCP Server - A Model Context Protocol server for Supabase database operations.

This server provides tools for interacting with a Supabase database, including:
- Reading rows from tables
- Creating records in tables
- Updating records in tables
- Deleting records from tables

Environment variables:
- SUPABASE_URL: The URL of your Supabase project
- SUPABASE_SERVICE_KEY: The service role key for your Supabase project
"""

import os
import logging
from typing import Dict, List, Any, Optional, Union
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass

from dotenv import load_dotenv
from supabase import create_client, Client
from mcp.server.fastmcp import FastMCP, Context

from .constants import (
    ENV_SUPABASE_URL, ENV_SUPABASE_SERVICE_KEY,
    ServerConfig, ErrorMessages, DEFAULT_COLUMNS, DEFAULT_ASCENDING
)
from .types import TableName, Filters, Updates, Records, OperationResponse
from .exceptions import ConfigurationError, ValidationError, QueryExecutionError
from .database import DatabaseOperations
from .utils import setup_logging, get_supabase_client

# Load environment variables
load_dotenv()

# Set up logging
logger = setup_logging()

# Create a dataclass for our application context
@dataclass
class SupabaseContext:
    """Context for the Supabase MCP server."""
    client: Client
    db_ops: DatabaseOperations


@asynccontextmanager
async def supabase_lifespan(server: FastMCP) -> AsyncIterator[SupabaseContext]:
    """
    Manages the Supabase client lifecycle.

    Args:
        server: The FastMCP server instance

    Yields:
        SupabaseContext: The context containing the Supabase client and database operations

    Raises:
        ConfigurationError: If environment variables are missing or invalid
    """
    logger.info("Initializing Supabase MCP server")

    # Get environment variables
    supabase_url = os.getenv(ENV_SUPABASE_URL)
    supabase_key = os.getenv(ENV_SUPABASE_SERVICE_KEY)

    if not supabase_url or not supabase_key:
        raise ConfigurationError(ErrorMessages.MISSING_ENV_VARS)

    try:
        # Initialize Supabase client
        supabase_client = create_client(supabase_url, supabase_key)

        # Initialize database operations
        db_ops = DatabaseOperations(supabase_client)

        logger.info("Successfully initialized Supabase client and database operations")

        yield SupabaseContext(client=supabase_client, db_ops=db_ops)

    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {str(e)}")
        raise ConfigurationError(f"Failed to initialize Supabase client: {str(e)}")
    finally:
        logger.info("Cleaning up Supabase MCP server")


# Create the MCP server
mcp = FastMCP(
    ServerConfig.NAME,
    description=ServerConfig.DESCRIPTION,
    lifespan=supabase_lifespan
)


@mcp.tool()
def read_table_rows(
    ctx: Context,
    table_name: TableName,
    columns: str = DEFAULT_COLUMNS,
    filters: Optional[Filters] = None,
    limit: Optional[int] = None,
    order_by: Optional[str] = None,
    ascending: bool = DEFAULT_ASCENDING
) -> List[Dict[str, Any]]:
    """
    Read rows from a Supabase table with optional filtering, ordering, and limiting.

    Use this tool to query data from a specific table in the Supabase database.
    You can select specific columns, filter rows based on conditions, limit the number
    of results, and order the results.

    Args:
        ctx: The MCP context
        table_name: Name of the table to read from
        columns: Comma-separated list of columns to select (default: "*" for all columns)
        filters: Dictionary of column-value pairs to filter rows (default: None)
        limit: Maximum number of rows to return (default: None)
        order_by: Column to order results by (default: None)
        ascending: Whether to sort in ascending order (default: True)

    Returns:
        List of dictionaries, each representing a row from the table

    Raises:
        ValidationError: If input parameters are invalid
        QueryExecutionError: If query execution fails

    Example:
        To get all users: read_table_rows(table_name="users")
        To get specific columns: read_table_rows(table_name="users", columns="id,name,email")
        To filter rows: read_table_rows(table_name="users", filters={"is_active": True})
        To limit results: read_table_rows(table_name="users", limit=10)
        To order results: read_table_rows(table_name="users", order_by="created_at", ascending=False)
    """
    try:
        db_ops = ctx.request_context.lifespan_context.db_ops
        return db_ops.read_table_rows(
            table_name=table_name,
            columns=columns,
            filters=filters,
            limit=limit,
            order_by=order_by,
            ascending=ascending
        )
    except (ValidationError, QueryExecutionError) as e:
        logger.error(f"Error in read_table_rows: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in read_table_rows: {str(e)}")
        raise QueryExecutionError(f"Unexpected error: {str(e)}", table_name, "read")


@mcp.tool()
def create_table_records(
    ctx: Context,
    table_name: TableName,
    records: Records
) -> OperationResponse:
    """
    Create one or multiple records in a Supabase table.

    Use this tool to insert new data into a specific table in the Supabase database.
    You can insert a single record or multiple records at once.

    Args:
        ctx: The MCP context
        table_name: Name of the table to insert records into
        records: A dictionary for a single record or a list of dictionaries for multiple records

    Returns:
        Dictionary containing the created records and metadata

    Raises:
        ValidationError: If input parameters are invalid
        QueryExecutionError: If query execution fails

    Example:
        To create a single record:
            create_table_records(
                table_name="users",
                records={"name": "John Doe", "email": "john@example.com"}
            )

        To create multiple records:
            create_table_records(
                table_name="users",
                records=[
                    {"name": "John Doe", "email": "john@example.com"},
                    {"name": "Jane Smith", "email": "jane@example.com"}
                ]
            )
    """
    try:
        db_ops = ctx.request_context.lifespan_context.db_ops
        return db_ops.create_table_records(table_name=table_name, records=records)
    except (ValidationError, QueryExecutionError) as e:
        logger.error(f"Error in create_table_records: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in create_table_records: {str(e)}")
        raise QueryExecutionError(f"Unexpected error: {str(e)}", table_name, "create")


@mcp.tool()
def update_table_records(
    ctx: Context,
    table_name: TableName,
    updates: Updates,
    filters: Filters
) -> OperationResponse:
    """
    Update records in a Supabase table that match the specified filters.

    Use this tool to modify existing data in a specific table in the Supabase database.
    You provide the new values and filter conditions to identify which records to update.

    Args:
        ctx: The MCP context
        table_name: Name of the table to update records in
        updates: Dictionary of column-value pairs with the new values
        filters: Dictionary of column-value pairs to filter which rows to update

    Returns:
        Dictionary containing the updated records and metadata

    Raises:
        ValidationError: If input parameters are invalid
        QueryExecutionError: If query execution fails

    Example:
        To update all active users' status:
            update_table_records(
                table_name="users",
                updates={"status": "premium"},
                filters={"is_active": True}
            )
    """
    try:
        db_ops = ctx.request_context.lifespan_context.db_ops
        return db_ops.update_table_records(
            table_name=table_name,
            updates=updates,
            filters=filters
        )
    except (ValidationError, QueryExecutionError) as e:
        logger.error(f"Error in update_table_records: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in update_table_records: {str(e)}")
        raise QueryExecutionError(f"Unexpected error: {str(e)}", table_name, "update")


@mcp.tool()
def delete_table_records(
    ctx: Context,
    table_name: TableName,
    filters: Filters
) -> OperationResponse:
    """
    Delete records from a Supabase table that match the specified filters.

    Use this tool to remove data from a specific table in the Supabase database.
    You provide filter conditions to identify which records to delete.

    Args:
        ctx: The MCP context
        table_name: Name of the table to delete records from
        filters: Dictionary of column-value pairs to filter which rows to delete

    Returns:
        Dictionary containing the deleted records and metadata

    Raises:
        ValidationError: If input parameters are invalid
        QueryExecutionError: If query execution fails

    Example:
        To delete inactive users:
            delete_table_records(
                table_name="users",
                filters={"is_active": False}
            )
    """
    try:
        db_ops = ctx.request_context.lifespan_context.db_ops
        return db_ops.delete_table_records(table_name=table_name, filters=filters)
    except (ValidationError, QueryExecutionError) as e:
        logger.error(f"Error in delete_table_records: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in delete_table_records: {str(e)}")
        raise QueryExecutionError(f"Unexpected error: {str(e)}", table_name, "delete")


if __name__ == "__main__":
    # Run the server with stdio transport
    mcp.run()
