# tests/utils.py

"""Utility functions for tests."""

from unittest.mock import MagicMock

from requests.exceptions import HTTPError


def raise_mock_http_error(status_code, error_code, message, error_type):
    """Create and raise a mock HTTP error for testing.
    
    Args:
        status_code: HTTP status code for the error
        error_code: Application-specific error code
        message: Error message
        error_type: Type of error
        
    Raises:
        HTTPError: A mock HTTP error with the specified parameters
    """
    mock_error_response = {
        "_errors": [
            {
                "code": error_code,
                "message": message,
                "details": {"errorType": error_type},
            }
        ],
        "_request_id": "test-request-id",
    }
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.content = True
    mock_response.json.return_value = mock_error_response
    return HTTPError(response=mock_response)
