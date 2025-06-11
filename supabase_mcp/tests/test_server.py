"""
Tests for the Supabase MCP server functionality.

This module contains tests for:
- The Supabase lifespan context manager
- MCP tools for interacting with Supabase tables:
  - read_table_rows
  - create_table_records
  - update_table_records
  - delete_table_records
"""

import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, List, Any

from mcp.server.fastmcp import FastMCP, Context
from supabase_mcp.server import (
    supabase_lifespan,
    SupabaseContext,
    read_table_rows,
    create_table_records,
    update_table_records,
    delete_table_records,
)


class TestSupabaseLifespan:
    """Tests for the Supabase lifespan context manager."""

    @pytest.mark.asyncio
    async def test_lifespan_with_valid_env_vars(self):
        """Test that lifespan correctly initializes with valid environment variables."""
        # Mock environment variables
        with patch.dict(os.environ, {
            "SUPABASE_URL": "https://example.supabase.co",
            "SUPABASE_SERVICE_KEY": "mock-service-key"
        }):
            # Mock the create_client function
            with patch("supabase_mcp.server.create_client") as mock_create_client:
                mock_client = MagicMock()
                mock_create_client.return_value = mock_client
                
                # Mock FastMCP server
                mock_server = MagicMock(spec=FastMCP)
                
                # Use the lifespan context manager
                async with supabase_lifespan(mock_server) as context:
                    # Check that context is correctly initialized
                    assert isinstance(context, SupabaseContext)
                    assert context.client == mock_client
                    
                # Verify create_client was called with correct parameters
                mock_create_client.assert_called_once_with(
                    "https://example.supabase.co", 
                    "mock-service-key"
                )

    @pytest.mark.asyncio
    async def test_lifespan_missing_env_vars(self):
        """Test that lifespan raises ValueError when environment variables are missing."""
        # Mock environment variables with missing values
        with patch.dict(os.environ, {
            "SUPABASE_URL": "",
            "SUPABASE_SERVICE_KEY": ""
        }, clear=True):
            # Mock FastMCP server
            mock_server = MagicMock(spec=FastMCP)
            
            # Verify ValueError is raised
            with pytest.raises(ValueError) as excinfo:
                async with supabase_lifespan(mock_server):
                    pass
            
            # Check error message
            assert "Missing environment variables" in str(excinfo.value)


class TestReadTableRows:
    """Tests for the read_table_rows MCP tool."""

    def test_read_table_rows_basic(self):
        """Test basic functionality of read_table_rows."""
        # Create mock context
        mock_context = MagicMock(spec=Context)
        mock_supabase = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_supabase
        
        # Mock the Supabase query builder
        mock_query = MagicMock()
        mock_supabase.table.return_value.select.return_value = mock_query
        mock_query.execute.return_value.data = [{"id": 1, "name": "Test"}]
        
        # Call the function
        result = read_table_rows(
            ctx=mock_context,
            table_name="users",
            columns="id,name"
        )
        
        # Verify the result
        assert result == [{"id": 1, "name": "Test"}]
        
        # Verify the query was built correctly
        mock_supabase.table.assert_called_once_with("users")
        mock_supabase.table.return_value.select.assert_called_once_with("id,name")
        mock_query.execute.assert_called_once()

    def test_read_table_rows_with_filters(self):
        """Test read_table_rows with filters applied."""
        # Create mock context
        mock_context = MagicMock(spec=Context)
        mock_supabase = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_supabase
        
        # Mock the Supabase query builder
        mock_query = MagicMock()
        mock_supabase.table.return_value.select.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.execute.return_value.data = [{"id": 1, "name": "Test", "active": True}]
        
        # Call the function with filters
        result = read_table_rows(
            ctx=mock_context,
            table_name="users",
            filters={"active": True}
        )
        
        # Verify the result
        assert result == [{"id": 1, "name": "Test", "active": True}]
        
        # Verify the query was built correctly
        mock_supabase.table.assert_called_once_with("users")
        mock_query.eq.assert_called_once_with("active", True)
        mock_query.execute.assert_called_once()

    def test_read_table_rows_with_ordering_and_limit(self):
        """Test read_table_rows with ordering and limit."""
        # Create mock context
        mock_context = MagicMock(spec=Context)
        mock_supabase = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_supabase
        
        # Mock the Supabase query builder
        mock_query = MagicMock()
        mock_supabase.table.return_value.select.return_value = mock_query
        mock_query.order.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.execute.return_value.data = [
            {"id": 1, "created_at": "2023-01-01"},
            {"id": 2, "created_at": "2023-01-02"}
        ]
        
        # Call the function with ordering and limit
        result = read_table_rows(
            ctx=mock_context,
            table_name="users",
            order_by="created_at",
            ascending=True,
            limit=2
        )
        
        # Verify the result
        assert result == [
            {"id": 1, "created_at": "2023-01-01"},
            {"id": 2, "created_at": "2023-01-02"}
        ]
        
        # Verify the query was built correctly
        mock_supabase.table.assert_called_once_with("users")
        mock_query.order.assert_called_once_with("created_at", ascending=True)
        mock_query.limit.assert_called_once_with(2)
        mock_query.execute.assert_called_once()

    def test_read_table_rows_with_descending_order(self):
        """Test read_table_rows with descending order."""
        # Create mock context
        mock_context = MagicMock(spec=Context)
        mock_supabase = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_supabase

        # Mock the Supabase query builder
        mock_query = MagicMock()
        mock_supabase.table.return_value.select.return_value = mock_query
        mock_query.order.return_value = mock_query
        mock_query.execute.return_value.data = [
            {"id": 2, "created_at": "2023-01-02"},
            {"id": 1, "created_at": "2023-01-01"}
        ]

        # Call the function with descending order
        result = read_table_rows(
            ctx=mock_context,
            table_name="users",
            order_by="created_at",
            ascending=False
        )

        # Verify the result
        assert result == [
            {"id": 2, "created_at": "2023-01-02"},
            {"id": 1, "created_at": "2023-01-01"}
        ]

        # Verify the query was built correctly with descending order
        mock_supabase.table.assert_called_once_with("users")
        mock_query.order.assert_called_once_with("created_at", ascending=False)
        mock_query.execute.assert_called_once()


class TestCreateTableRecords:
    """Tests for the create_table_records MCP tool."""

    def test_create_single_record(self):
        """Test creating a single record."""
        # Create mock context
        mock_context = MagicMock(spec=Context)
        mock_supabase = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_supabase
        
        # Mock the Supabase insert operation
        mock_response = MagicMock()
        mock_response.data = [{"id": 1, "name": "John", "email": "john@example.com"}]
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response
        
        # Call the function with a single record
        result = create_table_records(
            ctx=mock_context,
            table_name="users",
            records={"name": "John", "email": "john@example.com"}
        )
        
        # Verify the result
        assert result == {
            "data": [{"id": 1, "name": "John", "email": "john@example.com"}],
            "count": 1,
            "status": "success"
        }
        
        # Verify the query was built correctly
        mock_supabase.table.assert_called_once_with("users")
        mock_supabase.table.return_value.insert.assert_called_once_with(
            {"name": "John", "email": "john@example.com"}
        )

    def test_create_multiple_records(self):
        """Test creating multiple records."""
        # Create mock context
        mock_context = MagicMock(spec=Context)
        mock_supabase = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_supabase
        
        # Mock the Supabase insert operation
        mock_response = MagicMock()
        mock_response.data = [
            {"id": 1, "name": "John", "email": "john@example.com"},
            {"id": 2, "name": "Jane", "email": "jane@example.com"}
        ]
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response
        
        # Records to insert
        records = [
            {"name": "John", "email": "john@example.com"},
            {"name": "Jane", "email": "jane@example.com"}
        ]
        
        # Call the function with multiple records
        result = create_table_records(
            ctx=mock_context,
            table_name="users",
            records=records
        )
        
        # Verify the result
        assert result == {
            "data": [
                {"id": 1, "name": "John", "email": "john@example.com"},
                {"id": 2, "name": "Jane", "email": "jane@example.com"}
            ],
            "count": 2,
            "status": "success"
        }
        
        # Verify the query was built correctly
        mock_supabase.table.assert_called_once_with("users")
        mock_supabase.table.return_value.insert.assert_called_once_with(records)

    def test_create_record_error_handling(self):
        """Test error handling when creating records."""
        # Create mock context
        mock_context = MagicMock(spec=Context)
        mock_supabase = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_supabase
        
        # Mock the Supabase insert operation with empty data (error case)
        mock_response = MagicMock()
        mock_response.data = None
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response
        
        # Call the function
        result = create_table_records(
            ctx=mock_context,
            table_name="users",
            records={"name": "John", "email": "john@example.com"}
        )
        
        # Verify the result indicates an error
        assert result == {
            "data": None,
            "count": 0,
            "status": "error"
        }


class TestUpdateTableRecords:
    """Tests for the update_table_records MCP tool."""

    def test_update_records(self):
        """Test updating records with filters."""
        # Create mock context
        mock_context = MagicMock(spec=Context)
        mock_supabase = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_supabase
        
        # Mock the Supabase update operation
        mock_query = MagicMock()
        mock_supabase.table.return_value.update.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.execute.return_value.data = [
            {"id": 1, "name": "John Updated", "is_active": True}
        ]
        
        # Call the function
        result = update_table_records(
            ctx=mock_context,
            table_name="users",
            updates={"name": "John Updated"},
            filters={"id": 1}
        )
        
        # Verify the result
        assert result == {
            "data": [{"id": 1, "name": "John Updated", "is_active": True}],
            "count": 1,
            "status": "success"
        }
        
        # Verify the query was built correctly
        mock_supabase.table.assert_called_once_with("users")
        mock_supabase.table.return_value.update.assert_called_once_with({"name": "John Updated"})
        mock_query.eq.assert_called_once_with("id", 1)
        mock_query.execute.assert_called_once()

    def test_update_records_multiple_filters(self):
        """Test updating records with multiple filters."""
        # Create mock context
        mock_context = MagicMock(spec=Context)
        mock_supabase = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_supabase
        
        # Mock the Supabase update operation
        mock_query = MagicMock()
        mock_supabase.table.return_value.update.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.execute.return_value.data = [
            {"id": 1, "name": "John Updated", "is_active": True, "role": "admin"}
        ]
        
        # Call the function with multiple filters
        result = update_table_records(
            ctx=mock_context,
            table_name="users",
            updates={"name": "John Updated"},
            filters={"is_active": True, "role": "admin"}
        )
        
        # Verify the result
        assert result == {
            "data": [{"id": 1, "name": "John Updated", "is_active": True, "role": "admin"}],
            "count": 1,
            "status": "success"
        }
        
        # Verify the query was built correctly
        mock_supabase.table.assert_called_once_with("users")
        mock_supabase.table.return_value.update.assert_called_once_with({"name": "John Updated"})
        assert mock_query.eq.call_count == 2
        mock_query.execute.assert_called_once()

    def test_update_records_no_matches(self):
        """Test updating records when no records match the filters."""
        # Create mock context
        mock_context = MagicMock(spec=Context)
        mock_supabase = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_supabase
        
        # Mock the Supabase update operation with empty data
        mock_query = MagicMock()
        mock_supabase.table.return_value.update.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.execute.return_value.data = []
        
        # Call the function
        result = update_table_records(
            ctx=mock_context,
            table_name="users",
            updates={"name": "John Updated"},
            filters={"id": 999}  # Non-existent ID
        )
        
        # Verify the result indicates no records were updated
        assert result == {
            "data": [],
            "count": 0,
            "status": "error"
        }


class TestDeleteTableRecords:
    """Tests for the delete_table_records MCP tool."""

    def test_delete_records(self):
        """Test deleting records with filters."""
        # Create mock context
        mock_context = MagicMock(spec=Context)
        mock_supabase = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_supabase
        
        # Mock the Supabase delete operation
        mock_query = MagicMock()
        mock_supabase.table.return_value.delete.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.execute.return_value.data = [
            {"id": 1, "name": "John", "is_active": False}
        ]
        
        # Call the function
        result = delete_table_records(
            ctx=mock_context,
            table_name="users",
            filters={"id": 1}
        )
        
        # Verify the result
        assert result == {
            "data": [{"id": 1, "name": "John", "is_active": False}],
            "count": 1,
            "status": "success"
        }
        
        # Verify the query was built correctly
        mock_supabase.table.assert_called_once_with("users")
        mock_supabase.table.return_value.delete.assert_called_once()
        mock_query.eq.assert_called_once_with("id", 1)
        mock_query.execute.assert_called_once()

    def test_delete_records_multiple_filters(self):
        """Test deleting records with multiple filters."""
        # Create mock context
        mock_context = MagicMock(spec=Context)
        mock_supabase = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_supabase
        
        # Mock the Supabase delete operation
        mock_query = MagicMock()
        mock_supabase.table.return_value.delete.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.execute.return_value.data = [
            {"id": 1, "name": "John", "is_active": False, "role": "user"},
            {"id": 2, "name": "Jane", "is_active": False, "role": "user"}
        ]
        
        # Call the function with multiple filters
        result = delete_table_records(
            ctx=mock_context,
            table_name="users",
            filters={"is_active": False, "role": "user"}
        )
        
        # Verify the result
        assert result == {
            "data": [
                {"id": 1, "name": "John", "is_active": False, "role": "user"},
                {"id": 2, "name": "Jane", "is_active": False, "role": "user"}
            ],
            "count": 2,
            "status": "success"
        }
        
        # Verify the query was built correctly
        mock_supabase.table.assert_called_once_with("users")
        mock_supabase.table.return_value.delete.assert_called_once()
        assert mock_query.eq.call_count == 2
        mock_query.execute.assert_called_once()

    def test_delete_records_no_matches(self):
        """Test deleting records when no records match the filters."""
        # Create mock context
        mock_context = MagicMock(spec=Context)
        mock_supabase = MagicMock()
        mock_context.request_context.lifespan_context.client = mock_supabase
        
        # Mock the Supabase delete operation with empty data
        mock_query = MagicMock()
        mock_supabase.table.return_value.delete.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.execute.return_value.data = []
        
        # Call the function
        result = delete_table_records(
            ctx=mock_context,
            table_name="users",
            filters={"id": 999}  # Non-existent ID
        )
        
        # Verify the result indicates no records were deleted
        assert result == {
            "data": [],
            "count": 0,
            "status": "error"
        }
