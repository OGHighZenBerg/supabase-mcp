"""
Tests for utility functions.
"""

import pytest
from unittest.mock import MagicMock
from supabase_mcp.utils import (
    validate_table_name,
    validate_limit,
    validate_filters,
    validate_updates,
    create_response,
    apply_filters_to_query,
    safe_execute_query
)
from supabase_mcp.exceptions import ValidationError, QueryExecutionError
from supabase_mcp.constants import ResponseStatus


class TestValidationFunctions:
    """Tests for validation utility functions."""

    def test_validate_table_name_valid(self):
        """Test table name validation with valid input."""
        # Should not raise any exception
        validate_table_name("users")
        validate_table_name("user_profiles")
        validate_table_name("table123")

    def test_validate_table_name_invalid(self):
        """Test table name validation with invalid input."""
        with pytest.raises(ValidationError):
            validate_table_name("")
        
        with pytest.raises(ValidationError):
            validate_table_name("   ")
        
        with pytest.raises(ValidationError):
            validate_table_name(None)

    def test_validate_limit_valid(self):
        """Test limit validation with valid input."""
        # Should not raise any exception
        validate_limit(None)
        validate_limit(10)
        validate_limit(1)
        validate_limit(1000)

    def test_validate_limit_invalid(self):
        """Test limit validation with invalid input."""
        with pytest.raises(ValidationError):
            validate_limit(0)
        
        with pytest.raises(ValidationError):
            validate_limit(-1)
        
        with pytest.raises(ValidationError):
            validate_limit("10")

    def test_validate_filters_valid(self):
        """Test filters validation with valid input."""
        # Should not raise any exception
        validate_filters(None)
        validate_filters({"active": True})
        validate_filters({"id": 1, "name": "test"})

    def test_validate_filters_invalid(self):
        """Test filters validation with invalid input."""
        with pytest.raises(ValidationError):
            validate_filters({})
        
        with pytest.raises(ValidationError):
            validate_filters("invalid")
        
        with pytest.raises(ValidationError):
            validate_filters([])

    def test_validate_updates_valid(self):
        """Test updates validation with valid input."""
        # Should not raise any exception
        validate_updates({"name": "updated"})
        validate_updates({"id": 1, "name": "test", "active": False})

    def test_validate_updates_invalid(self):
        """Test updates validation with invalid input."""
        with pytest.raises(ValidationError):
            validate_updates({})
        
        with pytest.raises(ValidationError):
            validate_updates("invalid")
        
        with pytest.raises(ValidationError):
            validate_updates([])


class TestUtilityFunctions:
    """Tests for other utility functions."""

    def test_create_response_success(self):
        """Test creating a successful response."""
        data = [{"id": 1, "name": "test"}]
        response = create_response(data, ResponseStatus.SUCCESS, "Success message")
        
        assert response["data"] == data
        assert response["count"] == 1
        assert response["status"] == "success"
        assert response["message"] == "Success message"

    def test_create_response_error(self):
        """Test creating an error response."""
        response = create_response(None, ResponseStatus.ERROR, "Error message")
        
        assert response["data"] is None
        assert response["count"] == 0
        assert response["status"] == "error"
        assert response["message"] == "Error message"

    def test_create_response_empty_data(self):
        """Test creating a response with empty data."""
        response = create_response([], ResponseStatus.SUCCESS)
        
        assert response["data"] == []
        assert response["count"] == 0
        assert response["status"] == "success"
        assert response["message"] is None

    def test_apply_filters_to_query_with_filters(self):
        """Test applying filters to a query."""
        mock_query = MagicMock()
        mock_query.eq.return_value = mock_query
        
        filters = {"active": True, "role": "admin"}
        result = apply_filters_to_query(mock_query, filters)
        
        # Should return the query object
        assert result == mock_query
        
        # Should call eq for each filter
        assert mock_query.eq.call_count == 2
        mock_query.eq.assert_any_call("active", True)
        mock_query.eq.assert_any_call("role", "admin")

    def test_apply_filters_to_query_no_filters(self):
        """Test applying no filters to a query."""
        mock_query = MagicMock()
        
        result = apply_filters_to_query(mock_query, None)
        
        # Should return the original query object
        assert result == mock_query
        
        # Should not call eq
        mock_query.eq.assert_not_called()

    def test_safe_execute_query_success(self):
        """Test successful query execution."""
        mock_query = MagicMock()
        mock_response = MagicMock()
        mock_query.execute.return_value = mock_response
        
        result = safe_execute_query(mock_query, "read", "users")
        
        assert result == mock_response
        mock_query.execute.assert_called_once()

    def test_safe_execute_query_failure(self):
        """Test failed query execution."""
        mock_query = MagicMock()
        mock_query.execute.side_effect = Exception("Database error")
        
        with pytest.raises(QueryExecutionError) as excinfo:
            safe_execute_query(mock_query, "read", "users")
        
        assert "Failed to execute read on table 'users'" in str(excinfo.value)
        assert excinfo.value.table_name == "users"
        assert excinfo.value.operation == "read"
