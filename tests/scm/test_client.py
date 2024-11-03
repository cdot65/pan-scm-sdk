# tests/test_client.py

import pytest
from unittest.mock import patch, MagicMock
from scm.client import Scm
from scm.exceptions import (
    APIError,
    ObjectAlreadyExistsError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    MethodNotAllowedError,
    ConflictError,
    ReferenceNotZeroError,
    VersionNotSupportedError,
    SessionTimeoutError,
    BadRequestError,
    ObjectNotPresentError,
    FolderNotFoundError,
    MalformedRequestError,
    EmptyFieldError,
)
from requests.exceptions import HTTPError, RequestException


def test_scm_init_value_error():
    # Provide invalid parameters to trigger ValueError
    with pytest.raises(APIError) as exc_info:
        Scm(
            client_id="test_client_id",
            client_secret="test_client_secret",
            tsg_id=None,  # noqa # This will cause ValueError in AuthRequestModel
        )
    assert "Authentication initialization failed" in str(exc_info.value)


def test_request_http_error(mock_scm):
    scm = mock_scm
    mock_session = scm.session

    # Mock the response to raise HTTPError
    mock_response = MagicMock()
    mock_response.status_code = 400  # Set the status code to 400 Bad Request
    mock_response.raise_for_status.side_effect = HTTPError("Mocked HTTPError")
    mock_response.content = b'{"_errors":[{"message":"Error message","details":{"errorType":"Invalid Object"}}]}'
    mock_response.json.return_value = {
        "_errors": [
            {"message": "Error message", "details": {"errorType": "Invalid Object"}}
        ]
    }
    mock_session.request.return_value = mock_response

    with pytest.raises(ValidationError) as exc_info:
        scm.request("GET", "/test-endpoint")

    assert "Error message" in str(exc_info.value)


def test_request_general_exception(mock_scm):
    scm = mock_scm
    mock_session = scm.session

    mock_session.request.side_effect = RequestException("Mocked Exception")

    with pytest.raises(APIError) as exc_info:
        scm.request("GET", "/test-endpoint")

    assert "API request failed" in str(exc_info.value)


def test_handle_api_error():
    # Define different test cases
    test_cases = [
        {
            "status_code": 400,
            "error_content": {
                "_errors": [
                    {
                        "message": "Object already exists",
                        "details": {"errorType": "Object Already Exists"},
                    }
                ],
                "_request_id": "req-210",
            },
            "expected_exception": ObjectAlreadyExistsError,
            "expected_message": "Object already exists",
        },
        {
            "status_code": 400,
            "error_content": {
                "_errors": [
                    {
                        "message": "Bad request error",
                        "details": {"errorType": "Some Error Type"},
                    }
                ],
                "_request_id": "req-200",
            },
            "expected_exception": BadRequestError,
            "expected_message": "Bad request error",
        },
        {
            "status_code": 401,
            "error_content": {
                "_errors": [{"message": "Unauthorized access"}],
                "_request_id": "req-201",
            },
            "expected_exception": AuthenticationError,
            "expected_message": "Unauthorized access",
        },
        {
            "status_code": 403,
            "error_content": {
                "_errors": [{"message": "Forbidden access"}],
                "_request_id": "req-202",
            },
            "expected_exception": AuthorizationError,
            "expected_message": "Forbidden access",
        },
        {
            "status_code": 404,
            "error_content": {
                "_errors": [{"message": "Resource not found"}],
                "_request_id": "req-203",
            },
            "expected_exception": NotFoundError,
            "expected_message": "Resource not found",
        },
        {
            "status_code": 405,
            "error_content": {
                "_errors": [{"message": "Method not allowed"}],
                "_request_id": "req-204",
            },
            "expected_exception": MethodNotAllowedError,
            "expected_message": "Method not allowed",
        },
        {
            "status_code": 409,
            "error_content": {
                "_errors": [
                    {
                        "message": "Reference not zero",
                        "details": {"errorType": "Reference Not Zero"},
                    }
                ],
                "_request_id": "req-211",
            },
            "expected_exception": ReferenceNotZeroError,
            "expected_message": "Reference not zero",
        },
        {
            "status_code": 409,
            "error_content": {
                "_errors": [
                    {
                        "message": "Name not unique",
                        "details": {"errorType": "Name Not Unique"},
                    }
                ],
                "_request_id": "req-205",
            },
            "expected_exception": ConflictError,
            "expected_message": "Name not unique",
        },
        {
            "status_code": 409,
            "error_content": {
                "_errors": [
                    {
                        "message": "Some conflict",
                        "details": {"errorType": "Unknown Conflict"},
                    }
                ],
                "_request_id": "req-212",
            },
            "expected_exception": ConflictError,
            "expected_message": "Some conflict",
        },
        {
            "status_code": 501,
            "error_content": {
                "_errors": [{"message": "Version not supported"}],
                "_request_id": "req-206",
            },
            "expected_exception": VersionNotSupportedError,
            "expected_message": "Version not supported",
        },
        {
            "status_code": 504,
            "error_content": {
                "_errors": [{"message": "Session timed out"}],
                "_request_id": "req-207",
            },
            "expected_exception": SessionTimeoutError,
            "expected_message": "Session timed out",
        },
    ]

    for case in test_cases:
        response = MagicMock()
        response.status_code = case["status_code"]
        error_content = case["error_content"]

        exception = Scm._handle_api_error(response, error_content)
        assert isinstance(exception, case["expected_exception"])
        # assert str(exception) == case["expected_message"]
        assert exception.request_id == error_content.get("_request_id")


def test_handle_api_error_unknown_status():
    response = MagicMock()
    response.status_code = 418  # I'm a teapot
    error_content = {
        "_errors": [
            {
                "message": "Unknown error",
            }
        ],
        "_request_id": "req-999",
    }

    exception = Scm._handle_api_error(response, error_content)
    assert isinstance(exception, APIError)
    assert str(exception) == "HTTP 418: Unknown error"
    assert exception.request_id == "req-999"


def test_get_method(mock_scm):
    scm = mock_scm
    mock_oauth2client_instance = scm.oauth_client

    mock_oauth2client_instance.is_expired = False

    with patch.object(scm, "request", return_value={"data": "test"}) as mock_request:
        response = scm.get("/test-endpoint", params={"param1": "value1"})
        mock_request.assert_called_once_with(
            "GET", "/test-endpoint", params={"param1": "value1"}
        )
        assert response == {"data": "test"}


def test_post_method_token_refresh(mock_scm):
    scm = mock_scm
    mock_oauth2client_instance = scm.oauth_client

    mock_oauth2client_instance.is_expired = True
    mock_oauth2client_instance.refresh_token = MagicMock()

    with patch.object(scm, "request", return_value={"data": "test"}) as mock_request:
        response = scm.post("/test-endpoint", json={"key": "value"})
        mock_oauth2client_instance.refresh_token.assert_called_once()
        mock_request.assert_called_once_with(
            "POST", "/test-endpoint", json={"key": "value"}
        )
        assert response == {"data": "test"}


def test_request_http_error_no_content(mock_scm):
    scm = mock_scm
    mock_session = scm.session

    # Mock the response to raise HTTPError with no content
    mock_response = MagicMock()
    mock_response.status_code = 500  # Set status code to 500 Internal Server Error
    mock_response.raise_for_status.side_effect = HTTPError("Mocked HTTPError")
    mock_response.content = b""
    mock_response.json.side_effect = ValueError("No JSON content")
    mock_session.request.return_value = mock_response

    with pytest.raises(APIError) as exc_info:
        scm.request("GET", "/test-endpoint")

    assert "An error occurred." in str(exc_info.value)


def test_request_success(mock_scm):
    scm = mock_scm
    mock_session = scm.session

    # Mock the response to simulate a successful request
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None  # No exception raised
    mock_response.json.return_value = {"key": "value"}
    mock_session.request.return_value = mock_response

    result = scm.request("GET", "/test-endpoint")

    # Assertions
    mock_response.raise_for_status.assert_called_once()
    mock_response.json.assert_called_once()
    assert result == {"key": "value"}


def test_get_method_token_refresh(mock_scm):
    scm = mock_scm
    mock_oauth2client_instance = scm.oauth_client

    mock_oauth2client_instance.is_expired = True
    mock_oauth2client_instance.refresh_token = MagicMock()

    with patch.object(scm, "request", return_value={"data": "test"}) as mock_request:
        response = scm.get("/test-endpoint", params={"param1": "value1"})
        mock_oauth2client_instance.refresh_token.assert_called_once()
        mock_request.assert_called_once_with(
            "GET", "/test-endpoint", params={"param1": "value1"}
        )
        assert response == {"data": "test"}


def test_put_method_token_refresh(mock_scm):
    scm = mock_scm
    mock_oauth2client_instance = scm.oauth_client

    mock_oauth2client_instance.is_expired = True
    mock_oauth2client_instance.refresh_token = MagicMock()

    with patch.object(scm, "request", return_value={"data": "test"}) as mock_request:
        response = scm.put("/test-endpoint", json={"key": "value"})
        mock_oauth2client_instance.refresh_token.assert_called_once()
        mock_request.assert_called_once_with(
            "PUT", "/test-endpoint", json={"key": "value"}
        )
        assert response == {"data": "test"}


def test_delete_method_token_refresh(mock_scm):
    scm = mock_scm
    mock_oauth2client_instance = scm.oauth_client

    mock_oauth2client_instance.is_expired = True
    mock_oauth2client_instance.refresh_token = MagicMock()

    with patch.object(scm, "request", return_value={"data": "test"}) as mock_request:
        response = scm.delete("/test-endpoint")
        mock_oauth2client_instance.refresh_token.assert_called_once()
        mock_request.assert_called_once_with("DELETE", "/test-endpoint")
        assert response == {"data": "test"}


def test_request_json_exception(mock_scm):
    scm = mock_scm
    mock_session = scm.session

    # Mock the response to simulate a successful status but json() raises an exception
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None  # No exception raised
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_session.request.return_value = mock_response

    with pytest.raises(APIError) as exc_info:
        scm.request("GET", "/test-endpoint")

    assert "API request failed: Invalid JSON" in str(exc_info.value)


def test_request_empty_response(mock_scm):
    scm = mock_scm
    mock_session = scm.session

    # Mock the response to simulate a successful request with empty content
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None  # No exception raised
    mock_response.content = b""  # Empty content
    mock_session.request.return_value = mock_response

    result = scm.request("GET", "/test-endpoint")

    # Assertions
    mock_response.raise_for_status.assert_called_once()
    mock_response.json.assert_not_called()  # json() should not be called for empty content
    assert result is None  # The method should return None for empty content


def test_handle_api_error_details_list():
    """Test error handling when details is a list"""
    response = MagicMock()
    response.status_code = 400
    error_content = {
        "_errors": [
            {
                "message": "Multiple validation errors",
                "details": ["Error 1", "Error 2", "Error 3"],
                "code": "API_I00013",
            }
        ],
        "_request_id": "req-list-1",
    }

    exception = Scm._handle_api_error(response, error_content)
    assert isinstance(exception, APIError)
    # assert exception.details == ["Error 1", "Error 2", "Error 3"]
    # assert exception.error_type == "Error 1; Error 2; Error 3"


def test_handle_api_error_object_not_present():
    """Test API_I00013 error code with Object Not Present error type"""
    response = MagicMock()
    response.status_code = 404
    error_content = {
        "_errors": [
            {
                "message": "Object not found",
                "code": "API_I00013",
                "details": {"errorType": "Object Not Present"},
            }
        ],
        "_request_id": "req-onp-1",
    }

    exception = Scm._handle_api_error(response, error_content)
    assert isinstance(exception, ObjectNotPresentError)
    assert exception.error_code == "API_I00013"


def test_handle_api_error_operation_impossible():
    """Test API_I00013 error code with Operation Impossible error type"""
    response = MagicMock()
    response.status_code = 404
    error_content = {
        "_errors": [
            {
                "message": "Folder not found",
                "code": "API_I00013",
                "details": {"errorType": "Operation Impossible"},
            }
        ],
        "_request_id": "req-oi-1",
    }

    exception = Scm._handle_api_error(response, error_content)
    assert isinstance(exception, FolderNotFoundError)
    assert exception.error_code == "API_I00013"


def test_handle_api_error_object_already_exists():
    """Test API_I00013 error code with Object Already Exists error type"""
    response = MagicMock()
    response.status_code = 409
    error_content = {
        "_errors": [
            {
                "message": "Object already exists",
                "code": "API_I00013",
                "details": {"errorType": "Object Already Exists"},
            }
        ],
        "_request_id": "req-oae-1",
    }

    exception = Scm._handle_api_error(response, error_content)
    assert isinstance(exception, ObjectAlreadyExistsError)
    assert exception.error_code == "API_I00013"


def test_handle_api_error_malformed_command():
    """Test API_I00013 error code with Malformed Command error type"""
    response = MagicMock()
    response.status_code = 400
    error_content = {
        "_errors": [
            {
                "message": "Malformed request",
                "code": "API_I00013",
                "details": {"errorType": "Malformed Command"},
            }
        ],
        "_request_id": "req-mc-1",
    }

    exception = Scm._handle_api_error(response, error_content)
    assert isinstance(exception, MalformedRequestError)
    assert exception.error_code == "API_I00013"


def test_handle_api_error_empty_field():
    """Test API_I00035 error code with empty field validation error"""
    response = MagicMock()
    response.status_code = 400
    error_content = {
        "_errors": [
            {
                "message": "Validation error",
                "code": "API_I00035",
                "details": [
                    "Field 'name' is not allowed to be empty",
                    "Field 'description' is not allowed to be empty",
                ],
            }
        ],
        "_request_id": "req-ef-1",
    }

    exception = Scm._handle_api_error(response, error_content)
    assert isinstance(exception, EmptyFieldError)
    assert exception.error_code == "API_I00035"
