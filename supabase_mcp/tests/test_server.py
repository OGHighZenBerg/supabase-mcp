"""
Updated tests for the refactored Supabase MCP server functionality.

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
from supabase_mcp.exceptions import ConfigurationError


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
                    assert context.db_ops is not None
                    
                # Verify create_client was called with correct parameters
                mock_create_client.assert_called_once_with(
                    "https://example.supabase.co", 
                    "mock-service-key"
                )

    @pytest.mark.asyncio
    async def test_lifespan_missing_env_vars(self):
        """Test that lifespan raises ConfigurationError when environment variables are missing."""
        # Mock environment variables with missing values
        with patch.dict(os.environ, {
            "SUPABASE_URL": "",
            "SUPABASE_SERVICE_KEY": ""
        }, clear=True):
            # Mock FastMCP server
            mock_server = MagicMock(spec=FastMCP)
            
            # Verify ConfigurationError is raised
            with pytest.raises(ConfigurationError) as excinfo:
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
        mock_db_ops = MagicMock()
        mock_context.request_context.lifespan_context.db_ops = mock_db_ops
        
        # Mock the database operations response
        expected_data = [{"id": 1, "name": "Test"}]
        mock_db_ops.read_table_rows.return_value = expected_data
        
        # Call the function
        result = read_table_rows(
            ctx=mock_context,
            table_name="users",
            columns="id,name"
        )
        
        # Verify the result
        assert result == expected_data
        
        # Verify the database operations were called correctly
        mock_db_ops.read_table_rows.assert_called_once_with(
            table_name="users",
            columns="id,name",
            filters=None,
            limit=None,
            order_by=None,
            ascending=True
        )

    def test_read_table_rows_with_filters(self):
        """Test read_table_rows with filters applied."""
        # Create mock context
        mock_context = MagicMock(spec=Context)
        mock_db_ops = MagicMock()
        mock_context.request_context.lifespan_context.db_ops = mock_db_ops
        
        # Mock the database operations response
        expected_data = [{"id": 1, "name": "Test", "active": True}]
        mock_db_ops.read_table_rows.return_value = expected_data
        
        # Call the function with filters
        result = read_table_rows(
            ctx=mock_context,
            table_name="users",
            filters={"active": True}
        )
        
        # Verify the result
        assert result == expected_data
        
        # Verify the database operations were called correctly
        mock_db_ops.read_table_rows.assert_called_once_with(
            table_name="users",
            columns="*",
            filters={"active": True},
            limit=None,
            order_by=None,
            ascending=True
        )

    def test_read_table_rows_with_ordering_and_limit(self):
        """Test read_table_rows with ordering and limit."""
        # Create mock context
        mock_context = MagicMock(spec=Context)
        mock_db_ops = MagicMock()
        mock_context.request_context.lifespan_context.db_ops = mock_db_ops
        
        # Mock the database operations response
        expected_data = [
            {"id": 1, "created_at": "2023-01-01"},
            {"id": 2, "created_at": "2023-01-02"}
        ]
        mock_db_ops.read_table_rows.return_value = expected_data
        
        # Call the function with ordering and limit
        result = read_table_rows(
            ctx=mock_context,
            table_name="users",
            order_by="created_at",
            ascending=True,
            limit=2
        )
        
        # Verify the result
        assert result == expected_data
        
        # Verify the database operations were called correctly
        mock_db_ops.read_table_rows.assert_called_once_with(
            table_name="users",
            columns="*",
            filters=None,
            limit=2,
            order_by="created_at",
            ascending=True
        )

    def test_read_table_rows_with_descending_order(self):
        """Test read_table_rows with descending order."""
        # Create mock context
        mock_context = MagicMock(spec=Context)
        mock_db_ops = MagicMock()
        mock_context.request_context.lifespan_context.db_ops = mock_db_ops
        
        # Mock the database operations response
        expected_data = [
            {"id": 2, "created_at": "2023-01-02"},
            {"id": 1, "created_at": "2023-01-01"}
        ]
        mock_db_ops.read_table_rows.return_value = expected_data
        
        # Call the function with descending order
        result = read_table_rows(
            ctx=mock_context,
            table_name="users",
            order_by="created_at",
            ascending=False
        )
        
        # Verify the result
        assert result == expected_data
        
        # Verify the database operations were called correctly with descending order
        mock_db_ops.read_table_rows.assert_called_once_with(
            table_name="users",
            columns="*",
            filters=None,
            limit=None,
            order_by="created_at",
            ascending=False
        )


class TestCreateTableRecords:
    """Tests for the create_table_records MCP tool."""

    def test_create_single_record(self):
        """Test creating a single record."""
        # Create mock context
        mock_context = MagicMock(spec=Context)
        mock_db_ops = MagicMock()
        mock_context.request_context.lifespan_context.db_ops = mock_db_ops
        
        # Mock the database operations response
        expected_response = {
            "data": [{"id": 1, "name": "John", "email": "john@example.com"}],
            "count": 1,
            "status": "success",
            "message": "Created 1 record(s)"
        }
        mock_db_ops.create_table_records.return_value = expected_response
        
        # Call the function with a single record
        result = create_table_records(
            ctx=mock_context,
            table_name="users",
            records={"name": "John", "email": "john@example.com"}
        )
        
        # Verify the result
        assert result == expected_response
        
        # Verify the database operations were called correctly
        mock_db_ops.create_table_records.assert_called_once_with(
            table_name="users",
            records={"name": "John", "email": "john@example.com"}
        )

    def test_create_multiple_records(self):
        """Test creating multiple records."""
        # Create mock context
        mock_context = MagicMock(spec=Context)
        mock_db_ops = MagicMock()
        mock_context.request_context.lifespan_context.db_ops = mock_db_ops

        # Mock the database operations response
        expected_response = {
            "data": [
                {"id": 1, "name": "John", "email": "john@example.com"},
                {"id": 2, "name": "Jane", "email": "jane@example.com"}
            ],
            "count": 2,
            "status": "success",
            "message": "Created 2 record(s)"
        }
        mock_db_ops.create_table_records.return_value = expected_response

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
        assert result == expected_response

        # Verify the database operations were called correctly
        mock_db_ops.create_table_records.assert_called_once_with(
            table_name="users",
            records=records
        )

    def test_create_record_error_handling(self):
        """Test error handling when creating records."""
        # Create mock context
        mock_context = MagicMock(spec=Context)
        mock_db_ops = MagicMock()
        mock_context.request_context.lifespan_context.db_ops = mock_db_ops

        # Mock the database operations response for error case
        expected_response = {
            "data": None,
            "count": 0,
            "status": "error",
            "message": "No records were created"
        }
        mock_db_ops.create_table_records.return_value = expected_response

        # Call the function
        result = create_table_records(
            ctx=mock_context,
            table_name="users",
            records={"name": "John", "email": "john@example.com"}
        )

        # Verify the result indicates an error
        assert result == expected_response


class TestUpdateTableRecords:
    """Tests for the update_table_records MCP tool."""

    def test_update_records(self):
        """Test updating records with filters."""
        # Create mock context
        mock_context = MagicMock(spec=Context)
        mock_db_ops = MagicMock()
        mock_context.request_context.lifespan_context.db_ops = mock_db_ops

        # Mock the database operations response
        expected_response = {
            "data": [{"id": 1, "name": "John Updated", "is_active": True}],
            "count": 1,
            "status": "success",
            "message": "Updated 1 record(s)"
        }
        mock_db_ops.update_table_records.return_value = expected_response

        # Call the function
        result = update_table_records(
            ctx=mock_context,
            table_name="users",
            updates={"name": "John Updated"},
            filters={"id": 1}
        )

        # Verify the result
        assert result == expected_response

        # Verify the database operations were called correctly
        mock_db_ops.update_table_records.assert_called_once_with(
            table_name="users",
            updates={"name": "John Updated"},
            filters={"id": 1}
        )

    def test_update_records_multiple_filters(self):
        """Test updating records with multiple filters."""
        # Create mock context
        mock_context = MagicMock(spec=Context)
        mock_db_ops = MagicMock()
        mock_context.request_context.lifespan_context.db_ops = mock_db_ops

        # Mock the database operations response
        expected_response = {
            "data": [{"id": 1, "name": "John Updated", "is_active": True, "role": "admin"}],
            "count": 1,
            "status": "success",
            "message": "Updated 1 record(s)"
        }
        mock_db_ops.update_table_records.return_value = expected_response

        # Call the function with multiple filters
        result = update_table_records(
            ctx=mock_context,
            table_name="users",
            updates={"name": "John Updated"},
            filters={"is_active": True, "role": "admin"}
        )

        # Verify the result
        assert result == expected_response

        # Verify the database operations were called correctly
        mock_db_ops.update_table_records.assert_called_once_with(
            table_name="users",
            updates={"name": "John Updated"},
            filters={"is_active": True, "role": "admin"}
        )

    def test_update_records_no_matches(self):
        """Test updating records when no records match the filters."""
        # Create mock context
        mock_context = MagicMock(spec=Context)
        mock_db_ops = MagicMock()
        mock_context.request_context.lifespan_context.db_ops = mock_db_ops

        # Mock the database operations response for no matches
        expected_response = {
            "data": [],
            "count": 0,
            "status": "error",
            "message": "No records were updated"
        }
        mock_db_ops.update_table_records.return_value = expected_response

        # Call the function
        result = update_table_records(
            ctx=mock_context,
            table_name="users",
            updates={"name": "John Updated"},
            filters={"id": 999}  # Non-existent ID
        )

        # Verify the result indicates no records were updated
        assert result == expected_response


class TestDeleteTableRecords:
    """Tests for the delete_table_records MCP tool."""

    def test_delete_records(self):
        """Test deleting records with filters."""
        # Create mock context
        mock_context = MagicMock(spec=Context)
        mock_db_ops = MagicMock()
        mock_context.request_context.lifespan_context.db_ops = mock_db_ops

        # Mock the database operations response
        expected_response = {
            "data": [{"id": 1, "name": "John", "is_active": False}],
            "count": 1,
            "status": "success",
            "message": "Deleted 1 record(s)"
        }
        mock_db_ops.delete_table_records.return_value = expected_response

        # Call the function
        result = delete_table_records(
            ctx=mock_context,
            table_name="users",
            filters={"id": 1}
        )

        # Verify the result
        assert result == expected_response

        # Verify the database operations were called correctly
        mock_db_ops.delete_table_records.assert_called_once_with(
            table_name="users",
            filters={"id": 1}
        )

    def test_delete_records_multiple_filters(self):
        """Test deleting records with multiple filters."""
        # Create mock context
        mock_context = MagicMock(spec=Context)
        mock_db_ops = MagicMock()
        mock_context.request_context.lifespan_context.db_ops = mock_db_ops

        # Mock the database operations response
        expected_response = {
            "data": [
                {"id": 1, "name": "John", "is_active": False, "role": "user"},
                {"id": 2, "name": "Jane", "is_active": False, "role": "user"}
            ],
            "count": 2,
            "status": "success",
            "message": "Deleted 2 record(s)"
        }
        mock_db_ops.delete_table_records.return_value = expected_response

        # Call the function with multiple filters
        result = delete_table_records(
            ctx=mock_context,
            table_name="users",
            filters={"is_active": False, "role": "user"}
        )

        # Verify the result
        assert result == expected_response

        # Verify the database operations were called correctly
        mock_db_ops.delete_table_records.assert_called_once_with(
            table_name="users",
            filters={"is_active": False, "role": "user"}
        )

    def test_delete_records_no_matches(self):
        """Test deleting records when no records match the filters."""
        # Create mock context
        mock_context = MagicMock(spec=Context)
        mock_db_ops = MagicMock()
        mock_context.request_context.lifespan_context.db_ops = mock_db_ops

        # Mock the database operations response for no matches
        expected_response = {
            "data": [],
            "count": 0,
            "status": "error",
            "message": "No records were deleted"
        }
        mock_db_ops.delete_table_records.return_value = expected_response

        # Call the function
        result = delete_table_records(
            ctx=mock_context,
            table_name="users",
            filters={"id": 999}  # Non-existent ID
        )

        # Verify the result indicates no records were deleted
        assert result == expected_response
