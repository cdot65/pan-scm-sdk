# tests/test_client.py
from unittest.mock import patch, MagicMock

import pytest
from requests.exceptions import HTTPError

from scm.client import Scm
from scm.exceptions import (
    APIError,
    InvalidObjectError,
    BadRequestError,
    ObjectNotPresentError,
    ConflictError,
    MalformedCommandError,
    ErrorHandler,
    ServerError,
)
from tests.utils import raise_mock_http_error


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

        with pytest.raises(APIError):
            Scm(
                client_id="test_client_id",
                client_secret="test_client_secret",
                tsg_id=None,
            )


class TestClientRequest(TestClientBase):
    """Tests for Client request handling."""

    def test_request_http_error(self):
        """Test handling of HTTP errors."""
        self.session.request.side_effect = raise_mock_http_error(
            status_code=400,
            error_code="API_I00035",
            message="Error message",
            error_type="Invalid Object",
        )

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.request("GET", "/test-endpoint")

        assert "{'errorType': 'Invalid Object'}" in str(exc_info.value)
        assert "HTTP error: 400" in str(exc_info.value)
        assert "API error: API_I00035" in str(exc_info.value)

    def test_request_general_exception(self):
        """Test handling of general request exceptions."""
        self.session.request.side_effect = raise_mock_http_error(
            status_code=500,
            error_code="E003",
            message="API request failed",
            error_type="Internal Error",
        )

        with pytest.raises(ServerError) as exc_info:
            self.client.request("GET", "/test-endpoint")

        assert "{'errorType': 'Internal Error'}" in str(exc_info.value)
        assert "HTTP error: 500" in str(exc_info.value)
        assert "API error: E003" in str(exc_info.value)

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

    # def test_request_http_error_no_content(self):
    #     """Test handling of HTTP errors with no content."""
    #     mock_session = self.session
    #
    #     # Mock the response to raise HTTPError with no content
    #     mock_response = MagicMock()
    #     mock_response.status_code = 500  # Set status code to 500 Internal Server Error
    #     mock_response.raise_for_status.side_effect = HTTPError("Mocked HTTPError")
    #     mock_response.content = b""
    #     mock_response.json.side_effect = ValueError("No JSON content")
    #     mock_session.request.return_value = mock_response
    #
    #     with pytest.raises(APIError):
    #         self.client.request("GET", "/test-endpoint")

    # def test_request_json_exception(self):
    #     """Test handling of JSON parsing errors."""
    #     mock_session = self.session
    #
    #     # Mock the response to simulate a successful status but json() raises an exception
    #     mock_response = MagicMock()
    #     mock_response.raise_for_status.return_value = None  # No exception raised
    #     mock_response.json.side_effect = ValueError("Invalid JSON")
    #     mock_session.request.return_value = mock_response
    #
    #     with pytest.raises(APIError) as exc_info:
    #         self.client.request("GET", "/test-endpoint")
    #
    #     assert "API request failed: Invalid JSON" in str(exc_info.value)

    # def test_request_http_error_invalid_json(self):
    #     """Test handling of HTTP errors with invalid JSON response."""
    #     mock_session = self.session
    #
    #     # Mock the response to raise HTTPError with invalid JSON content
    #     mock_response = MagicMock()
    #     mock_response.status_code = 400
    #     mock_response.raise_for_status.side_effect = HTTPError("Mocked HTTPError")
    #     mock_response.content = b"Invalid JSON Content"
    #     mock_response.json.side_effect = ValueError("Invalid JSON")
    #     mock_session.request.return_value = mock_response
    #
    #     with pytest.raises(APIError):
    #         self.client.request("GET", "/test-endpoint")

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

    def test_init_invalid_log_level(self):
        """Test initialization with invalid log level."""
        with pytest.raises(ValueError) as exc_info:
            Scm(
                client_id="test_client_id",
                client_secret="test_client_secret",
                tsg_id="test_tsg_id",
                log_level="INVALID_LEVEL",  # Invalid log level
            )
        assert "Invalid log level: INVALID_LEVEL" in str(exc_info.value)

    def test_request_http_error_invalid_json(self):
        """Test handling of HTTP error with invalid JSON response."""
        # Create a mock response with invalid JSON
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.content = b"Invalid JSON Content"
        mock_response.json.side_effect = ValueError("Invalid JSON")

        # Create HTTPError with our mock response
        mock_http_error = HTTPError(response=mock_response)
        mock_http_error.response = mock_response

        # Configure the session's request to raise our HTTPError
        self.session.request.side_effect = mock_http_error

        # Test request with invalid JSON response
        with pytest.raises(ValueError) as exc_info:
            self.client.request("GET", "/test-endpoint")

        # Verify error details
        error = exc_info.value
        assert error.__str__() == "Invalid JSON"

    def test_request_http_error_invalid_error_format(self):
        """Test handling of HTTP error with invalid error response format."""
        # Create a mock response with invalid error format
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.content = b"Some content"
        mock_response.json.return_value = {"not_errors": "invalid format"}

        # Create HTTPError with our mock response
        mock_http_error = HTTPError(response=mock_response)
        mock_http_error.response = mock_response

        # Configure the session's request to raise our HTTPError
        self.session.request.side_effect = mock_http_error

        # Test request with invalid error format
        with pytest.raises(ValueError) as exc_info:
            self.client.request("GET", "/test-endpoint")

        # Verify error details
        error = exc_info.value
        assert error.__str__() == "Invalid error response format"

    def test_request_http_error_no_response(self):
        """Test handling of HTTP error without response."""
        # Create HTTPError without response
        mock_http_error = HTTPError()
        mock_http_error.response = None

        # Configure the session's request to raise our HTTPError
        self.session.request.side_effect = mock_http_error

        # Test request with no response
        with pytest.raises(APIError):
            self.client.request("GET", "/test-endpoint")

    def test_request_http_error_no_content(self):
        """Test handling of HTTP error with empty content."""
        # Create a mock response with empty content
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.content = b""

        # Create HTTPError with our mock response
        mock_http_error = HTTPError(response=mock_response)
        mock_http_error.response = mock_response

        # Configure the session's request to raise our HTTPError
        self.session.request.side_effect = mock_http_error

        # Test request with empty content
        with pytest.raises(APIError) as exc_info:
            self.client.request("GET", "/test-endpoint")


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
        self.session.request.side_effect = raise_mock_http_error(
            status_code=418,  # I'm a teapot
            error_code="UnknownCode",
            message="Unknown error",
            error_type="Unknown",
        )

        with pytest.raises(APIError) as exc_info:
            self.client.request("GET", "/test-endpoint")

        assert "{'errorType': 'Unknown'}" in str(exc_info.value)
        assert "HTTP error: 418" in str(exc_info.value)
        assert "API error: UnknownCode" in str(exc_info.value)

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

    def test_handle_api_error_object_not_present(self):
        """Test API_I00013 error code with Object Not Present error type."""
        self.session.request.side_effect = raise_mock_http_error(
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(ObjectNotPresentError) as exc_info:
            self.client.request("GET", "/test-endpoint")

        assert "{'errorType': 'Object Not Present'}" in str(exc_info.value)
        assert "HTTP error: 404" in str(exc_info.value)
        assert "API error: API_I00013" in str(exc_info.value)

    def test_handle_api_error_operation_impossible(self):
        """Test API_I00013 error code with Operation Impossible error type."""
        self.session.request.side_effect = raise_mock_http_error(
            status_code=404,
            error_code="API_I00013",
            message="Folder not found",
            error_type="Operation Impossible",
        )

        with pytest.raises(ObjectNotPresentError) as exc_info:
            self.client.request("GET", "/test-endpoint")

        assert "{'errorType': 'Operation Impossible'}" in str(exc_info.value)
        assert "HTTP error: 404" in str(exc_info.value)
        assert "API error: API_I00013" in str(exc_info.value)

    def test_handle_api_error_object_already_exists(self):
        """Test API_I00013 error code with Object Already Exists error type."""
        self.session.request.side_effect = raise_mock_http_error(
            status_code=409,
            error_code="API_I00013",
            message="Object already exists",
            error_type="Object Already Exists",
        )

        with pytest.raises(ConflictError) as exc_info:
            self.client.request("GET", "/test-endpoint")

        assert "{'errorType': 'Object Already Exists'}" in str(exc_info.value)
        assert "HTTP error: 409" in str(exc_info.value)
        assert "API error: API_I00013" in str(exc_info.value)

    def test_handle_api_error_malformed_command(self):
        """Test API_I00013 error code with Malformed Command error type."""
        self.session.request.side_effect = raise_mock_http_error(
            status_code=400,
            error_code="API_I00013",
            message="Malformed request",
            error_type="Malformed Command",
        )

        with pytest.raises(MalformedCommandError) as exc_info:
            self.client.request("GET", "/test-endpoint")

        assert "{'errorType': 'Malformed Command'}" in str(exc_info.value)
        assert "HTTP error: 400" in str(exc_info.value)
        assert "API error: API_I00013" in str(exc_info.value)

    def test_handle_api_error_empty_field(self):
        """Test API_I00035 error code with empty field validation error."""
        self.session.request.side_effect = raise_mock_http_error(
            status_code=400,
            error_code="API_I00035",
            message="Validation error",
            error_type="Invalid Object",
        )

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.request("GET", "/test-endpoint")

        assert "{'errorType': 'Invalid Object'}" in str(exc_info.value)
        assert "HTTP error: 400" in str(exc_info.value)
        assert "API error: API_I00035" in str(exc_info.value)
