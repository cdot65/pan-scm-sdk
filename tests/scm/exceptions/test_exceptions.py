import pytest
from scm.exceptions import (
    ErrorResponse,
    APIError,
    ErrorHandler,
    ValidationError,
    ReferenceNotZeroError,
)


class TestErrorResponse:
    def test_from_response_raises_value_error(self):
        """Test that from_response raises ValueError for invalid response data."""
        # Test with missing _errors key
        with pytest.raises(ValueError, match="Invalid error response format"):
            ErrorResponse.from_response({})

        # Test with empty _errors list
        with pytest.raises(ValueError, match="Invalid error response format"):
            ErrorResponse.from_response({"_errors": []})

        # Test with None _errors
        with pytest.raises(ValueError, match="Invalid error response format"):
            ErrorResponse.from_response({"_errors": None})

    def test_from_response_success(self):
        """Test successful creation of ErrorResponse from response data."""
        response_data = {
            "_errors": [
                {
                    "code": "TEST001",
                    "message": "Test error message",
                    "details": {"key": "value"},
                }
            ],
            "_request_id": "req123",
        }

        error_response = ErrorResponse.from_response(response_data)

        assert error_response.code == "TEST001"
        assert error_response.message == "Test error message"
        assert error_response.details == {"key": "value"}
        assert error_response.request_id == "req123"


class TestAPIError:
    def test_from_error_response(self):
        """Test creation of APIError from ErrorResponse."""
        error_response = ErrorResponse(
            code="TEST001",
            message="Test message",
            details={"test": "details"},
            request_id="req123",
        )

        api_error = APIError.from_error_response(error_response)

        assert api_error.message == "Test message"
        assert api_error.error_code == "TEST001"
        assert api_error.details == {"test": "details"}
        assert api_error.request_id == "req123"
        assert api_error.references == []

    def test_api_error_initialization(self):
        """Test APIError initialization with different parameters."""
        # Test with minimal parameters
        error1 = APIError("Test message")
        assert str(error1) == "Test message"
        assert error1.details == {}
        assert error1.references == []

        # Test with all parameters
        error2 = APIError(
            message="Full test",
            error_code="TEST001",
            details={"key": "value"},
            request_id="req123",
            references=["ref1"],
        )
        assert error2.message == "Full test"
        assert error2.error_code == "TEST001"
        assert error2.details == {"key": "value"}
        assert error2.request_id == "req123"
        assert error2.references == ["ref1"]


class TestErrorHandler:
    def test_raise_for_error_invalid_format(self):
        """Test ErrorHandler raises APIError for invalid format."""
        with pytest.raises(APIError, match="Invalid error response format"):
            ErrorHandler.raise_for_error({})

    def test_raise_for_error_no_exception_class(self):
        """Test fallback to generic APIError when no specific exception class matches."""
        response_data = {
            "_errors": [
                {
                    "code": "UNKNOWN",
                    "message": "Unknown error",
                }
            ]
        }

        with pytest.raises(APIError) as exc_info:
            ErrorHandler.raise_for_error(response_data)

        assert exc_info.value.message == "Unknown error"
        assert isinstance(exc_info.value, APIError)
        assert not isinstance(
            exc_info.value, ValidationError
        )  # Ensure it's the base class

    def test_raise_for_error_with_details_message(self):
        """Test error handler uses details message when available."""
        response_data = {
            "_errors": [
                {
                    "code": "TEST001",
                    "message": "General message",
                    "details": {"message": "Detailed error message"},
                }
            ]
        }

        with pytest.raises(APIError) as exc_info:
            ErrorHandler.raise_for_error(response_data)

        assert exc_info.value.message == "Detailed error message"

    def test_raise_for_error_fallback_message(self):
        """Test error handler falls back to error message when details message is not available."""
        response_data = {
            "_errors": [
                {"code": "TEST001", "message": "Fallback message", "details": {}}
            ]
        }

        with pytest.raises(APIError) as exc_info:
            ErrorHandler.raise_for_error(response_data)

        assert exc_info.value.message == "Fallback message"

    def test_reference_not_zero_error_handling(self):
        """Test handling of Reference Not Zero errors."""
        response_data = {
            "_errors": [
                {
                    "code": "API_I00013",
                    "message": "Cannot delete",
                    "details": {
                        "errorType": "Reference Not Zero",
                        "errors": [{"params": ["ref1"], "extra": ["path1"]}],
                        "message": ["Additional path info"],
                    },
                }
            ],
            "_request_id": "req123",
        }

        with pytest.raises(ReferenceNotZeroError) as exc_info:
            ErrorHandler.raise_for_error(response_data)

        assert exc_info.value.references == ["ref1"]
        assert "path1" in exc_info.value.reference_paths
        assert "Additional path info" in exc_info.value.reference_paths
