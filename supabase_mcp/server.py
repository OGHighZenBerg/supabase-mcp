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
from typing import Dict, List, Any, Optional, Union
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass

from dotenv import load_dotenv
from supabase import create_client, Client
from mcp.server.fastmcp import FastMCP, Context

# Load environment variables
load_dotenv()

# Create a dataclass for our application context
@dataclass
class SupabaseContext:
    """Context for the Supabase MCP server."""
    client: Client


@asynccontextmanager
async def supabase_lifespan(server: FastMCP) -> AsyncIterator[SupabaseContext]:
    """
    Manages the Supabase client lifecycle.
    
    Args:
        server: The FastMCP server instance
        
    Yields:
        SupabaseContext: The context containing the Supabase client
    """
    # Get environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError(
            "Missing environment variables. Please set SUPABASE_URL and SUPABASE_SERVICE_KEY."
        )
    
    # Initialize Supabase client
    supabase_client = create_client(supabase_url, supabase_key)
    
    try:
        yield SupabaseContext(client=supabase_client)
    finally:
        # No explicit cleanup needed for Supabase client
        pass


# Create the MCP server
mcp = FastMCP(
    "Supabase Database",
    description="MCP server for interacting with Supabase databases",
    lifespan=supabase_lifespan
)


@mcp.tool()
def read_table_rows(
    ctx: Context,
    table_name: str,
    columns: str = "*",
    filters: Optional[Dict[str, Any]] = None,
    limit: Optional[int] = None,
    order_by: Optional[str] = None,
    ascending: bool = True
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
        
    Example:
        To get all users: read_table_rows(table_name="users")
        To get specific columns: read_table_rows(table_name="users", columns="id,name,email")
        To filter rows: read_table_rows(table_name="users", filters={"is_active": True})
        To limit results: read_table_rows(table_name="users", limit=10)
        To order results: read_table_rows(table_name="users", order_by="created_at", ascending=False)
    """
    supabase = ctx.request_context.lifespan_context.client
    
    # Start building the query
    query = supabase.table(table_name).select(columns)
    
    # Apply filters if provided
    if filters:
        for column, value in filters.items():
            query = query.eq(column, value)
    
    # Apply ordering if provided
    if order_by:
        query = query.order(order_by, ascending=ascending)
    
    # Apply limit if provided
    if limit:
        query = query.limit(limit)
    
    # Execute the query
    response = query.execute()
    
    # Return the data
    return response.data


@mcp.tool()
def create_table_records(
    ctx: Context,
    table_name: str,
    records: Union[Dict[str, Any], List[Dict[str, Any]]]
) -> Dict[str, Any]:
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
    supabase = ctx.request_context.lifespan_context.client
    
    # Insert the records
    response = supabase.table(table_name).insert(records).execute()
    
    # Return the response
    return {
        "data": response.data,
        "count": len(response.data) if response.data else 0,
        "status": "success" if response.data else "error"
    }


@mcp.tool()
def update_table_records(
    ctx: Context,
    table_name: str,
    updates: Dict[str, Any],
    filters: Dict[str, Any]
) -> Dict[str, Any]:
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
        
    Example:
        To update all active users' status:
            update_table_records(
                table_name="users",
                updates={"status": "premium"},
                filters={"is_active": True}
            )
    """
    supabase = ctx.request_context.lifespan_context.client
    
    # Start building the query
    query = supabase.table(table_name).update(updates)
    
    # Apply filters
    for column, value in filters.items():
        query = query.eq(column, value)
    
    # Execute the query
    response = query.execute()
    
    # Return the response
    return {
        "data": response.data,
        "count": len(response.data) if response.data else 0,
        "status": "success" if response.data else "error"
    }


@mcp.tool()
def delete_table_records(
    ctx: Context,
    table_name: str,
    filters: Dict[str, Any]
) -> Dict[str, Any]:
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
        
    Example:
        To delete inactive users:
            delete_table_records(
                table_name="users",
                filters={"is_active": False}
            )
    """
    supabase = ctx.request_context.lifespan_context.client
    
    # Start building the query
    query = supabase.table(table_name).delete()
    
    # Apply filters
    for column, value in filters.items():
        query = query.eq(column, value)
    
    # Execute the query
    response = query.execute()
    
    # Return the response
    return {
        "data": response.data,
        "count": len(response.data) if response.data else 0,
        "status": "success" if response.data else "error"
    }


if __name__ == "__main__":
    # Run the server with stdio transport
    mcp.run()
