"""
Tests for the database operations module.
"""

import pytest
from unittest.mock import MagicMock, patch
from supabase_mcp.database import DatabaseOperations
from supabase_mcp.exceptions import ValidationError, QueryExecutionError
from supabase_mcp.constants import ResponseStatus


class TestDatabaseOperations:
    """Tests for the DatabaseOperations class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_client = MagicMock()
        self.db_ops = DatabaseOperations(self.mock_client)

    def test_read_table_rows_basic(self):
        """Test basic read operation."""
        # Mock the Supabase response
        mock_response = MagicMock()
        mock_response.data = [{"id": 1, "name": "Test"}]
        
        # Mock the query chain
        mock_query = MagicMock()
        self.mock_client.table.return_value.select.return_value = mock_query
        mock_query.execute.return_value = mock_response
        
        # Call the method
        result = self.db_ops.read_table_rows("users", columns="id,name")
        
        # Verify the result
        assert result == [{"id": 1, "name": "Test"}]
        
        # Verify the query was built correctly
        self.mock_client.table.assert_called_once_with("users")
        self.mock_client.table.return_value.select.assert_called_once_with("id,name")

    def test_read_table_rows_with_filters(self):
        """Test read operation with filters."""
        # Mock the Supabase response
        mock_response = MagicMock()
        mock_response.data = [{"id": 1, "name": "Test", "active": True}]
        
        # Mock the query chain
        mock_query = MagicMock()
        self.mock_client.table.return_value.select.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.execute.return_value = mock_response
        
        # Call the method with filters
        result = self.db_ops.read_table_rows("users", filters={"active": True})
        
        # Verify the result
        assert result == [{"id": 1, "name": "Test", "active": True}]
        
        # Verify the query was built correctly
        mock_query.eq.assert_called_once_with("active", True)

    def test_read_table_rows_with_ordering(self):
        """Test read operation with ordering."""
        # Mock the Supabase response
        mock_response = MagicMock()
        mock_response.data = [{"id": 1, "created_at": "2023-01-01"}]
        
        # Mock the query chain
        mock_query = MagicMock()
        self.mock_client.table.return_value.select.return_value = mock_query
        mock_query.order.return_value = mock_query
        mock_query.execute.return_value = mock_response
        
        # Call the method with ordering
        result = self.db_ops.read_table_rows("users", order_by="created_at", ascending=False)
        
        # Verify the result
        assert result == [{"id": 1, "created_at": "2023-01-01"}]
        
        # Verify the query was built correctly
        mock_query.order.assert_called_once_with("created_at", ascending=False)

    def test_read_table_rows_invalid_table_name(self):
        """Test read operation with invalid table name."""
        with pytest.raises(ValidationError) as excinfo:
            self.db_ops.read_table_rows("")
        
        assert "Table name cannot be empty" in str(excinfo.value)

    def test_read_table_rows_invalid_limit(self):
        """Test read operation with invalid limit."""
        with pytest.raises(ValidationError) as excinfo:
            self.db_ops.read_table_rows("users", limit=-1)
        
        assert "Limit must be a positive integer" in str(excinfo.value)

    def test_create_table_records_single(self):
        """Test creating a single record."""
        # Mock the Supabase response
        mock_response = MagicMock()
        mock_response.data = [{"id": 1, "name": "John"}]
        
        # Mock the query chain
        mock_query = MagicMock()
        self.mock_client.table.return_value.insert.return_value = mock_query
        mock_query.execute.return_value = mock_response
        
        # Call the method
        result = self.db_ops.create_table_records("users", {"name": "John"})
        
        # Verify the result
        assert result["data"] == [{"id": 1, "name": "John"}]
        assert result["count"] == 1
        assert result["status"] == ResponseStatus.SUCCESS.value
        
        # Verify the query was built correctly
        self.mock_client.table.assert_called_once_with("users")
        self.mock_client.table.return_value.insert.assert_called_once_with({"name": "John"})

    def test_create_table_records_multiple(self):
        """Test creating multiple records."""
        # Mock the Supabase response
        mock_response = MagicMock()
        mock_response.data = [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}]
        
        # Mock the query chain
        mock_query = MagicMock()
        self.mock_client.table.return_value.insert.return_value = mock_query
        mock_query.execute.return_value = mock_response
        
        records = [{"name": "John"}, {"name": "Jane"}]
        
        # Call the method
        result = self.db_ops.create_table_records("users", records)
        
        # Verify the result
        assert result["count"] == 2
        assert result["status"] == ResponseStatus.SUCCESS.value
        
        # Verify the query was built correctly
        self.mock_client.table.return_value.insert.assert_called_once_with(records)

    def test_create_table_records_empty(self):
        """Test creating records with empty input."""
        with pytest.raises(ValidationError) as excinfo:
            self.db_ops.create_table_records("users", {})
        
        assert "Records cannot be empty" in str(excinfo.value)

    def test_update_table_records(self):
        """Test updating records."""
        # Mock the Supabase response
        mock_response = MagicMock()
        mock_response.data = [{"id": 1, "name": "John Updated"}]
        
        # Mock the query chain
        mock_query = MagicMock()
        self.mock_client.table.return_value.update.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.execute.return_value = mock_response
        
        # Call the method
        result = self.db_ops.update_table_records(
            "users", 
            {"name": "John Updated"}, 
            {"id": 1}
        )
        
        # Verify the result
        assert result["data"] == [{"id": 1, "name": "John Updated"}]
        assert result["count"] == 1
        assert result["status"] == ResponseStatus.SUCCESS.value
        
        # Verify the query was built correctly
        self.mock_client.table.assert_called_once_with("users")
        self.mock_client.table.return_value.update.assert_called_once_with({"name": "John Updated"})
        mock_query.eq.assert_called_once_with("id", 1)

    def test_delete_table_records(self):
        """Test deleting records."""
        # Mock the Supabase response
        mock_response = MagicMock()
        mock_response.data = [{"id": 1, "name": "John"}]
        
        # Mock the query chain
        mock_query = MagicMock()
        self.mock_client.table.return_value.delete.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.execute.return_value = mock_response
        
        # Call the method
        result = self.db_ops.delete_table_records("users", {"id": 1})
        
        # Verify the result
        assert result["data"] == [{"id": 1, "name": "John"}]
        assert result["count"] == 1
        assert result["status"] == ResponseStatus.SUCCESS.value
        
        # Verify the query was built correctly
        self.mock_client.table.assert_called_once_with("users")
        self.mock_client.table.return_value.delete.assert_called_once()
        mock_query.eq.assert_called_once_with("id", 1)
