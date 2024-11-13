# tests/test_client.py

import pytest
from unittest.mock import patch, MagicMock
from scm.client import Scm
from scm.exceptions import (
    APIError,
    InvalidObjectError,
    BadRequestError,
    ObjectNotPresentError,
    ConflictError,
    MalformedCommandError,
    ErrorHandler,
)
from requests.exceptions import HTTPError, RequestException


class TestClientBase:
    """Base class for Client tests."""

    @pytest.fixture(autouse=True)
    @patch("scm.client.OAuth2Client")
    def setup_method(self, mock_oauth2client):
        """Setup method that runs before each test."""
        # Create a mock OAuth2Client instance
        mock_oauth_client = mock_oauth2client.return_value
        mock_oauth_client.session = MagicMock()
        mock_oauth_client.is_expired = False
        mock_oauth_client.refresh_token = MagicMock()
        mock_oauth_client.signing_key = MagicMock(key="mocked_key")

        self.client = Scm(
            client_id="test_client_id",
            client_secret="test_client_secret",
            tsg_id="test_tsg_id",
        )
        # Assign the mocked session to self.session for convenience
        self.session = self.client.session


class TestClientInit:
    """Tests for Client initialization."""

    @patch("scm.client.OAuth2Client")
    def test_init_value_error(self, mock_oauth2client):
        """Test initialization with invalid parameters."""
        # Mock the OAuth2Client to prevent actual network calls
        mock_oauth_client = mock_oauth2client.return_value
        mock_oauth_client.session = MagicMock()
        mock_oauth_client.is_expired = False
        mock_oauth_client.refresh_token = MagicMock()
        mock_oauth_client.signing_key = MagicMock(key="mocked_key")

        with pytest.raises(APIError) as exc_info:
            Scm(
                client_id="test_client_id",
                client_secret="test_client_secret",
                tsg_id=None,  # This should cause a ValidationError or ValueError
            )
        assert "Authentication initialization failed" in str(exc_info.value)


class TestClientRequest(TestClientBase):
    """Tests for Client request handling."""

    def test_request_http_error(self):
        """Test handling of HTTP errors."""
        mock_session = self.session

        # Mock the response to raise HTTPError
        mock_response = MagicMock()
        mock_response.status_code = 400  # Set the status code to 400 Bad Request
        mock_response.raise_for_status.side_effect = HTTPError("Mocked HTTPError")
        mock_response.content = b'{"_errors":[{"message":"Error message","code":"API_I00035","details":{"errorType":"Invalid Object"}}]}'
        mock_response.json.return_value = {
            "_errors": [
                {
                    "message": "Error message",
                    "code": "API_I00035",
                    "details": {"errorType": "Invalid Object"},
                }
            ]
        }
        mock_session.request.return_value = mock_response

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.request("GET", "/test-endpoint")

        assert "Error message" in str(exc_info.value)

    def test_request_general_exception(self):
        """Test handling of general request exceptions."""
        mock_session = self.session

        mock_session.request.side_effect = RequestException("Mocked Exception")

        with pytest.raises(APIError) as exc_info:
            self.client.request("GET", "/test-endpoint")

        assert "API request failed" in str(exc_info.value)

    def test_request_success(self):
        """Test successful request handling."""
        mock_session = self.session

        # Mock the response to simulate a successful request
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None  # No exception raised
        mock_response.json.return_value = {"key": "value"}
        mock_session.request.return_value = mock_response

        result = self.client.request("GET", "/test-endpoint")

        # Assertions
        mock_response.raise_for_status.assert_called_once()
        mock_response.json.assert_called_once()
        assert result == {"key": "value"}

    def test_request_http_error_no_content(self):
        """Test handling of HTTP errors with no content."""
        mock_session = self.session

        # Mock the response to raise HTTPError with no content
        mock_response = MagicMock()
        mock_response.status_code = 500  # Set status code to 500 Internal Server Error
        mock_response.raise_for_status.side_effect = HTTPError("Mocked HTTPError")
        mock_response.content = b""
        mock_response.json.side_effect = ValueError("No JSON content")
        mock_session.request.return_value = mock_response

        with pytest.raises(APIError) as exc_info:
            self.client.request("GET", "/test-endpoint")

        assert "An error occurred." in str(exc_info.value)

    def test_request_json_exception(self):
        """Test handling of JSON parsing errors."""
        mock_session = self.session

        # Mock the response to simulate a successful status but json() raises an exception
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None  # No exception raised
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_session.request.return_value = mock_response

        with pytest.raises(APIError) as exc_info:
            self.client.request("GET", "/test-endpoint")

        assert "API request failed: Invalid JSON" in str(exc_info.value)

    def test_request_empty_response(self):
        """Test handling of empty responses."""
        mock_session = self.session

        # Mock the response to simulate a successful request with empty content
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None  # No exception raised
        mock_response.content = b""  # Empty content
        mock_session.request.return_value = mock_response

        result = self.client.request("GET", "/test-endpoint")

        # Assertions
        mock_response.raise_for_status.assert_called_once()
        mock_response.json.assert_not_called()  # json() should not be called for empty content
        assert result is None  # The method should return None for empty content


class TestClientMethods(TestClientBase):
    """Tests for Client HTTP methods."""

    def test_get_method(self):
        """Test GET method."""
        mock_oauth2client_instance = self.client.oauth_client

        mock_oauth2client_instance.is_expired = False

        with patch.object(
            self.client, "request", return_value={"data": "test"}
        ) as mock_request:
            response = self.client.get("/test-endpoint", params={"param1": "value1"})
            mock_request.assert_called_once_with(
                "GET", "/test-endpoint", params={"param1": "value1"}
            )
            assert response == {"data": "test"}

    def test_get_method_token_refresh(self):
        """Test GET method with token refresh."""
        mock_oauth2client_instance = self.client.oauth_client

        mock_oauth2client_instance.is_expired = True
        mock_oauth2client_instance.refresh_token = MagicMock()

        with patch.object(
            self.client, "request", return_value={"data": "test"}
        ) as mock_request:
            response = self.client.get("/test-endpoint", params={"param1": "value1"})
            mock_oauth2client_instance.refresh_token.assert_called_once()
            mock_request.assert_called_once_with(
                "GET", "/test-endpoint", params={"param1": "value1"}
            )
            assert response == {"data": "test"}

    def test_post_method_token_refresh(self):
        """Test POST method with token refresh."""
        mock_oauth2client_instance = self.client.oauth_client

        mock_oauth2client_instance.is_expired = True
        mock_oauth2client_instance.refresh_token = MagicMock()

        with patch.object(
            self.client, "request", return_value={"data": "test"}
        ) as mock_request:
            response = self.client.post("/test-endpoint", json={"key": "value"})
            mock_oauth2client_instance.refresh_token.assert_called_once()
            mock_request.assert_called_once_with(
                "POST", "/test-endpoint", json={"key": "value"}
            )
            assert response == {"data": "test"}

    def test_put_method_token_refresh(self):
        """Test PUT method with token refresh."""
        mock_oauth2client_instance = self.client.oauth_client

        mock_oauth2client_instance.is_expired = True
        mock_oauth2client_instance.refresh_token = MagicMock()

        with patch.object(
            self.client, "request", return_value={"data": "test"}
        ) as mock_request:
            response = self.client.put("/test-endpoint", json={"key": "value"})
            mock_oauth2client_instance.refresh_token.assert_called_once()
            mock_request.assert_called_once_with(
                "PUT", "/test-endpoint", json={"key": "value"}
            )
            assert response == {"data": "test"}

    def test_delete_method_token_refresh(self):
        """Test DELETE method with token refresh."""
        mock_oauth2client_instance = self.client.oauth_client

        mock_oauth2client_instance.is_expired = True
        mock_oauth2client_instance.refresh_token = MagicMock()

        with patch.object(
            self.client, "request", return_value={"data": "test"}
        ) as mock_request:
            response = self.client.delete("/test-endpoint")
            mock_oauth2client_instance.refresh_token.assert_called_once()
            mock_request.assert_called_once_with("DELETE", "/test-endpoint")
            assert response == {"data": "test"}


class TestClientErrorHandling(TestClientBase):
    """Tests for Client error handling."""

    def test_handle_api_error_unknown_status(self):
        """Test handling of unknown status codes."""
        response = MagicMock()
        response.status_code = 418  # I'm a teapot
        error_content = {
            "_errors": [
                {
                    "message": "Unknown error",
                    "code": "UnknownCode",  # Added code field
                }
            ],
            "_request_id": "req-999",
        }

        with pytest.raises(APIError) as exc_info:
            ErrorHandler.raise_for_error(error_content, response.status_code)
        assert isinstance(exc_info.value, APIError)
        assert "Unknown error" in str(exc_info.value)
        assert exc_info.value.request_id == "req-999"

    def test_handle_api_error_details_list(self):
        """Test error handling when details is a list."""
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

        with pytest.raises(BadRequestError) as exc_info:
            ErrorHandler.raise_for_error(error_content, response.status_code)
        assert isinstance(exc_info.value, BadRequestError)
        assert exc_info.value.request_id == "req-list-1"

    def test_handle_api_error_object_not_present(self):
        """Test API_I00013 error code with Object Not Present error type."""
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

        with pytest.raises(ObjectNotPresentError) as exc_info:
            ErrorHandler.raise_for_error(error_content, response.status_code)
        assert exc_info.value.error_code == "API_I00013"
        assert exc_info.value.request_id == "req-onp-1"

    def test_handle_api_error_operation_impossible(self):
        """Test API_I00013 error code with Operation Impossible error type."""
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

        with pytest.raises(ObjectNotPresentError) as exc_info:
            ErrorHandler.raise_for_error(error_content, response.status_code)
        assert exc_info.value.error_code == "API_I00013"
        assert exc_info.value.request_id == "req-oi-1"

    def test_handle_api_error_object_already_exists(self):
        """Test API_I00013 error code with Object Already Exists error type."""
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

        with pytest.raises(ConflictError) as exc_info:
            ErrorHandler.raise_for_error(error_content, response.status_code)
        assert exc_info.value.error_code == "API_I00013"
        assert exc_info.value.request_id == "req-oae-1"

    def test_handle_api_error_malformed_command(self):
        """Test API_I00013 error code with Malformed Command error type."""
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

        with pytest.raises(MalformedCommandError) as exc_info:
            ErrorHandler.raise_for_error(error_content, response.status_code)
        assert exc_info.value.error_code == "API_I00013"
        assert exc_info.value.request_id == "req-mc-1"

    def test_handle_api_error_empty_field(self):
        """Test API_I00035 error code with empty field validation error."""
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

        with pytest.raises(InvalidObjectError) as exc_info:
            ErrorHandler.raise_for_error(error_content, response.status_code)
        assert exc_info.value.error_code == "API_I00035"
        assert exc_info.value.request_id == "req-ef-1"
