# tests/utils.py

"""Utility functions for tests."""

from unittest.mock import MagicMock

from requests.exceptions import HTTPError


def raise_mock_http_error(status_code, error_code, message, error_type):
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
