# tests/test_client.py

"""Tests for SCM client functionality."""

from unittest.mock import ANY, MagicMock, Mock, patch

import pytest
from requests import Session
from requests.exceptions import HTTPError

from scm.client import Scm, ScmClient
from scm.exceptions import (
    APIError,
    BadRequestError,
    ConflictError,
    ErrorHandler,
    InvalidObjectError,
    MalformedCommandError,
    ObjectNotPresentError,
    ServerError,
)
from scm.models.operations import (
    CandidatePushResponseModel,
    JobListResponse,
    JobStatusResponse,
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

    def test_logger_handler_block_coverage(self):
        """Ensure the logger handler creation block (lines 120-124) is executed."""
        import logging
        import sys

        from scm.client import Scm

        logger = logging.getLogger("scm")
        # Remove all handlers
        logger.handlers.clear()
        assert not logger.handlers, "Logger should have no handlers before test"

        # Instantiate Scm (should trigger the handler block)
        Scm(access_token="dummy")

        # Now there should be exactly one handler, and it should be a StreamHandler to sys.stdout
        assert len(logger.handlers) == 1, "Handler block was not executed"
        handler = logger.handlers[0]
        assert isinstance(handler, logging.StreamHandler)
        assert handler.stream == sys.stdout
        assert isinstance(handler.formatter, logging.Formatter)
        assert "%(asctime)s" in handler.formatter._fmt

    @patch("requests.Session")
    def test_verify_ssl_flag_bearer_token(self, mock_session):
        """Test that verify_ssl is respected for bearer token mode."""
        mock_instance = mock_session.return_value
        Scm(
            access_token="dummy",
            verify_ssl=False,
        )
        assert mock_instance.verify is False
        Scm(
            access_token="dummy",
            verify_ssl=True,
        )
        assert mock_instance.verify is True

    def test_insecure_warning_logged_scm(self):
        """Test that disabling TLS verification logs a warning in Scm."""
        from unittest.mock import patch

        with patch("scm.client.logging.getLogger") as mock_get_logger:
            mock_logger = mock_get_logger.return_value
            Scm(access_token="dummy", verify_ssl=False)
            mock_logger.warning.assert_any_call(
                "TLS certificate verification is disabled (verify_ssl=False). "
                "This is insecure and exposes you to man-in-the-middle attacks. "
                "See: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#tls-warnings"
            )

    def test_insecure_warning_logged_oauth2(self, caplog):
        """Test that disabling TLS verification logs a warning in OAuth2Client."""
        from unittest.mock import patch

        with patch(
            "requests_oauthlib.OAuth2Session.fetch_token",
            return_value={"access_token": "dummy", "token_type": "bearer"},
        ):
            with caplog.at_level("WARNING", logger="scm.auth"):
                Scm(client_id="id", client_secret="secret", tsg_id="tsg", verify_ssl=False)
        assert any("TLS certificate verification is disabled" in r for r in caplog.messages)

    @patch("scm.client.OAuth2Client")
    def test_verify_ssl_flag_oauth2(self, mock_oauth2client):
        """Test that verify_ssl is passed to OAuth2Client."""
        Scm(
            client_id="id",
            client_secret="secret",
            tsg_id="tsg",
            verify_ssl=False,
        )
        mock_oauth2client.assert_called_with(ANY, verify_ssl=False)

    def test_logger_and_services_initialization(self):
        """Test that logger and _services are initialized as expected (covers lines 114, 122-126)."""
        import logging

        from scm.client import Scm

        # Remove all handlers from the 'scm' logger to force handler creation
        logger = logging.getLogger("scm")
        logger.handlers.clear()
        # Instantiate Scm
        client = Scm(access_token="dummy")
        # Check that a handler was added
        assert len(logger.handlers) > 0
        # Check that the handler has a formatter
        assert logger.handlers[0].formatter is not None
        # Check that _services is initialized as an empty dict
        assert hasattr(client, "_services")
        assert isinstance(client._services, dict)
        assert client._services == {}

    def test_logger_handler_creation(self):
        """Test that the logger handler block (lines 120-124) is executed if no handlers exist."""
        import logging
        import sys

        from scm.client import Scm

        logger = logging.getLogger("scm")
        # Remove all handlers to guarantee block is executed
        logger.handlers.clear()
        # Instantiate Scm
        client = Scm(access_token="dummy")
        # There should now be a handler
        assert len(logger.handlers) == 1
        handler = logger.handlers[0]
        # Handler should be a StreamHandler and output to sys.stdout
        assert isinstance(handler, logging.StreamHandler)
        assert handler.stream == sys.stdout
        # Handler should have the correct formatter
        assert isinstance(handler.formatter, logging.Formatter)
        assert "%(asctime)s" in handler.formatter._fmt
        # Handler should have the correct level
        assert handler.level == logger.level
        # _services should be initialized
        assert hasattr(client, "_services")
        assert isinstance(client._services, dict)
        assert client._services == {}

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

    def test_client_init_with_bearer_token(self):
        """Test that client initializes correctly with a bearer token."""
        token = "test_token_12345"
        client = Scm(access_token=token)

        # Verify oauth_client is None when using bearer token
        assert client.oauth_client is None

        # Verify session was created and has correct auth header
        assert client.session is not None
        assert isinstance(client.session, Session)
        assert client.session.headers["Authorization"] == f"Bearer {token}"

    def test_client_init_requires_credentials_or_token(self):
        """Test that client initialization requires either credentials or token."""
        # No credentials or token should raise error
        with pytest.raises(APIError):
            Scm()

        # Partial credentials should raise error
        with pytest.raises(APIError):
            Scm(client_id="test_id")

        with pytest.raises(APIError):
            Scm(client_id="test_id", client_secret="test_secret")

    def test_scm_client_alias_with_bearer_token(self):
        """Test that ScmClient alias works with bearer token."""
        token = "test_token_12345"
        client = ScmClient(access_token=token)

        # Verify oauth_client is None when using bearer token
        assert client.oauth_client is None

        # Verify session was created and has correct auth header
        assert client.session is not None
        assert isinstance(client.session, Session)
        assert client.session.headers["Authorization"] == f"Bearer {token}"

    def test_getattr_service_cache(self):
        """Test that __getattr__ returns cached service instances if they exist."""
        client = Scm(access_token="dummy_token")
        # Manually populate the service cache
        mock_service = object()
        client._services["address"] = mock_service
        # Accessing the service should return the cached instance
        assert client.address is mock_service

    def test_getattr_unknown_service(self):
        """Test that __getattr__ raises AttributeError for unknown services."""
        client = Scm(access_token="dummy_token")
        with pytest.raises(AttributeError) as excinfo:
            client.nonexistent_service
        assert "'Scm' object has no attribute 'nonexistent_service'" in str(excinfo.value)

    @patch("importlib.import_module")
    def test_getattr_import_error(self, mock_import_module):
        """Test that __getattr__ handles import errors."""
        mock_import_module.side_effect = ImportError("Module not found")
        client = Scm(access_token="dummy_token")
        with pytest.raises(AttributeError) as excinfo:
            client.address
        assert "Failed to load service 'address'" in str(excinfo.value)


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
        with pytest.raises(APIError):
            self.client.request("GET", "/test-endpoint")


class TestClientMethods(TestClientBase):
    """Tests for Client HTTP methods."""

    def test_get_method(self):
        """Test GET method."""
        mock_oauth2client_instance = self.client.oauth_client

        mock_oauth2client_instance.is_expired = False

        with patch.object(self.client, "request", return_value={"data": "test"}) as mock_request:
            response = self.client.get("/test-endpoint", params={"param1": "value1"})
            mock_request.assert_called_once_with(
                "GET", "/test-endpoint", params={"param1": "value1"}
            )
            assert response == {"data": "test"}

    def test_get_method_with_bearer_token(self):
        """Test GET method with bearer token."""
        # Create client with bearer token
        client = Scm(access_token="test_token")

        # Setup mock for the request method
        with patch.object(client, "request", return_value={"data": "test"}) as mock_request:
            response = client.get("/test-endpoint", params={"param1": "value1"})
            mock_request.assert_called_once_with(
                "GET", "/test-endpoint", params={"param1": "value1"}
            )
            assert response == {"data": "test"}

    @patch("requests.Session.request")
    def test_api_methods_skip_token_refresh(self, mock_request):
        """Test that API methods skip token refresh when using bearer token."""
        # Setup mock response
        mock_response = Mock()
        mock_response.content = b'{"test": "response"}'
        mock_response.json.return_value = {"test": "response"}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Initialize client with bearer token
        client = Scm(access_token="test_token")

        # Call API methods - no oauth_client means no refresh check should occur
        client.get("/test")
        client.post("/test")
        client.put("/test")
        client.delete("/test")

        # Verify request was called for each method
        assert mock_request.call_count == 4

    def test_get_method_token_refresh(self):
        """Test GET method with token refresh."""
        mock_oauth2client_instance = self.client.oauth_client

        mock_oauth2client_instance.is_expired = True
        mock_oauth2client_instance.refresh_token = MagicMock()

        with patch.object(self.client, "request", return_value={"data": "test"}) as mock_request:
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

        with patch.object(self.client, "request", return_value={"data": "test"}) as mock_request:
            response = self.client.post("/test-endpoint", json={"key": "value"})
            mock_oauth2client_instance.refresh_token.assert_called_once()
            mock_request.assert_called_once_with("POST", "/test-endpoint", json={"key": "value"})
            assert response == {"data": "test"}

    def test_put_method_token_refresh(self):
        """Test PUT method with token refresh."""
        mock_oauth2client_instance = self.client.oauth_client

        mock_oauth2client_instance.is_expired = True
        mock_oauth2client_instance.refresh_token = MagicMock()

        with patch.object(self.client, "request", return_value={"data": "test"}) as mock_request:
            response = self.client.put("/test-endpoint", json={"key": "value"})
            mock_oauth2client_instance.refresh_token.assert_called_once()
            mock_request.assert_called_once_with("PUT", "/test-endpoint", json={"key": "value"})
            assert response == {"data": "test"}

    def test_delete_method_token_refresh(self):
        """Test DELETE method with token refresh."""
        mock_oauth2client_instance = self.client.oauth_client

        mock_oauth2client_instance.is_expired = True
        mock_oauth2client_instance.refresh_token = MagicMock()

        with patch.object(self.client, "request", return_value={"data": "test"}) as mock_request:
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


class TestClientJobMethods(TestClientBase):
    """Tests for job-related client methods."""

    def test_list_jobs_basic(self):
        """Test basic job listing without filtering."""
        mock_response = {
            "data": [
                {
                    "device_name": "device1",
                    "id": "1",
                    "job_result": "2",
                    "job_status": "2",
                    "job_type": "53",
                    "parent_id": "0",
                    "result_str": "OK",
                    "start_ts": "2024-11-30T10:00:00",
                    "status_str": "FIN",
                    "type_str": "CommitAndPush",
                    "uname": "test@example.com",
                }
            ],
            "total": 1,
            "limit": 100,
            "offset": 0,
        }
        self.session.request.return_value.json.return_value = mock_response

        result = self.client.list_jobs(limit=100, offset=0)

        assert isinstance(result, JobListResponse)
        assert len(result.data) == 1
        assert result.total == 1
        assert result.limit == 100
        self.session.request.assert_called_once()

    def test_list_jobs_with_parent_filter(self):
        """Test job listing with parent_id filtering."""
        mock_response = {
            "data": [
                {
                    "id": "1",
                    "parent_id": "parent1",
                    "job_result": "2",
                    "job_status": "2",
                    "job_type": "53",
                    "result_str": "OK",
                    "start_ts": "2024-11-30T10:00:00",
                    "status_str": "FIN",
                    "type_str": "CommitAndPush",
                    "uname": "test@example.com",
                },
                {
                    "id": "2",
                    "parent_id": "parent2",
                    "job_result": "2",
                    "job_status": "2",
                    "job_type": "53",
                    "result_str": "OK",
                    "start_ts": "2024-11-30T10:00:00",
                    "status_str": "FIN",
                    "type_str": "CommitAndPush",
                    "uname": "test@example.com",
                },
            ],
            "total": 2,
            "limit": 100,
            "offset": 0,
        }
        self.session.request.return_value.json.return_value = mock_response

        result = self.client.list_jobs(parent_id="parent1")

        assert isinstance(result, JobListResponse)
        assert len(result.data) == 1
        assert result.data[0].parent_id == "parent1"
        assert result.total == 1  # Total should be updated for filtered results

    def test_get_job_status(self):
        """Test getting status of a specific job."""
        mock_response = {
            "data": [
                {
                    "cfg_id": "",
                    "details": '{"info":["Partial changes to commit: changes to configuration by administrators: pan-scm-sdk@1821351705.iam.panserviceaccount.com","Configuration committed successfully"],"errors":[],"warnings":[],"description":"this is a test"}',
                    "dev_serial": "",
                    "dev_uuid": "",
                    "device_name": "",
                    "device_type": "",
                    "end_ts": "2024-11-30 10:25:21",
                    "id": "1595",
                    "insert_ts": "2024-11-30 10:24:50",
                    "job_result": "2",
                    "job_status": "2",
                    "job_type": "53",
                    "last_update": "2024-11-30 10:25:22",
                    "opaque_int": "0",
                    "opaque_str": "",
                    "owner": "cfgserv",
                    "parent_id": "0",
                    "percent": "100",
                    "result_i": "2",
                    "result_str": "OK",
                    "session_id": "",
                    "start_ts": "2024-11-30 10:24:50",
                    "status_i": "2",
                    "status_str": "FIN",
                    "summary": "",
                    "type_i": "53",
                    "type_str": "CommitAndPush",
                    "uname": "pan-scm-sdk@1821351705.iam.panserviceaccount.com",
                }
            ]
        }
        self.session.request.return_value.json.return_value = mock_response

        result = self.client.get_job_status("1595")

        assert isinstance(result, JobStatusResponse)
        assert len(result.data) == 1
        assert result.data[0].id == "1595"
        self.session.request.assert_called_once_with(
            "GET",
            "https://api.strata.paloaltonetworks.com/config/operations/v1/jobs/1595",
            params=None,
            verify=ANY,
        )

    def test_wait_for_job_success(self):
        """Test waiting for job completion - successful case."""
        with patch("time.time", side_effect=[0, 10, 20]):
            with patch("time.sleep") as mock_sleep:
                # First call returns running status, second call returns completed
                self.session.request.return_value.json.side_effect = [
                    {
                        "data": [
                            {
                                "id": "test_job",
                                "status_str": "RUN",
                                "status_i": "1",
                                "start_ts": "2024-11-30T10:00:00",
                                "insert_ts": "2024-11-30T10:00:00",
                                "last_update": "2024-11-30T10:01:00",
                                "job_status": "1",
                                "job_type": "53",
                                "job_result": "0",
                                "details": "running",
                                "owner": "test",
                                "percent": "50",
                                "result_i": "0",
                                "result_str": "PENDING",
                                "type_i": "53",
                                "type_str": "CommitAndPush",
                                "uname": "test-user",
                            }
                        ]
                    },
                    {
                        "data": [
                            {
                                "id": "test_job",
                                "status_str": "FIN",
                                "status_i": "2",
                                "start_ts": "2024-11-30T10:00:00",
                                "insert_ts": "2024-11-30T10:00:00",
                                "last_update": "2024-11-30T10:02:00",
                                "job_status": "2",
                                "job_type": "53",
                                "job_result": "2",
                                "details": "completed",
                                "owner": "test",
                                "percent": "100",
                                "result_i": "2",
                                "result_str": "OK",
                                "type_i": "53",
                                "type_str": "CommitAndPush",
                                "uname": "test-user",
                            }
                        ]
                    },
                ]

                result = self.client.wait_for_job("test_job", timeout=30, poll_interval=10)

                assert isinstance(result, JobStatusResponse)
                assert result.data[0].status_str == "FIN"
                mock_sleep.assert_called_once_with(10)

    def test_wait_for_job_timeout(self):
        """Test waiting for job completion - timeout case."""
        with patch("time.time", side_effect=[0, 301, 302]):  # Simulate timeout
            with patch("time.sleep"):
                self.session.request.return_value.json.return_value = {
                    "data": [
                        {
                            "id": "test_job",
                            "status_str": "RUN",
                            "start_ts": "2024-11-30T10:00:00",
                            "insert_ts": "2024-11-30T10:00:00",
                            "last_update": "2024-11-30T10:01:00",
                            "job_status": "1",
                            "job_type": "53",
                            "job_result": "0",
                            "details": "running",
                            "owner": "test",
                        }
                    ]
                }

                with pytest.raises(TimeoutError) as exc_info:
                    self.client.wait_for_job("test_job", timeout=300)

                assert "did not complete within 300 seconds" in str(exc_info.value)

    def test_wait_for_job_empty_response(self):
        """Test waiting for job completion - empty response handling."""
        with patch("time.time", side_effect=[0, 10, 20]):
            with patch("time.sleep") as mock_sleep:
                self.session.request.return_value.json.return_value = {"data": []}

                with pytest.raises(TimeoutError):
                    self.client.wait_for_job("test_job", timeout=15, poll_interval=5)

                assert mock_sleep.call_count > 0


class TestClientCommitMethods(TestClientBase):
    """Tests for client commit methods."""

    @patch("requests.Session.request")
    def test_commit_with_bearer_token(self, mock_request):
        """Test commit method requires admin when using bearer token."""
        # Setup mock response
        mock_response = Mock()
        mock_response.content = (
            b'{"success": true, "job_id": "123", "message": "Commit job created"}'
        )
        mock_response.json.return_value = {
            "success": True,
            "job_id": "123",
            "message": "Commit job created",
        }
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Initialize client with bearer token
        client = Scm(access_token="test_token")

        # Commit with no admin should raise error
        with pytest.raises(APIError) as exc_info:
            client.commit(folders=["test"], description="test commit")

        # Verify error message
        error = exc_info.value
        expected_message = (
            "When using bearer token authentication, 'admin' must be provided for commit operations"
        )
        assert error.message == expected_message

        # Commit with admin should work
        response = client.commit(
            folders=["test"], description="test commit", admin=["test@example.com"]
        )

        assert response.success is True
        assert response.job_id == "123"

    @patch("requests.Session.request")
    def test_dynamic_service_access_with_bearer_token(self, mock_request):
        """Test that dynamic service access works with bearer token."""
        # Setup mock response
        mock_response = Mock()
        mock_response.content = b'{"data": []}'
        mock_response.json.return_value = {"data": []}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # Initialize client with bearer token
        client = Scm(access_token="test_token")

        # Access a service dynamically
        address_service = client.address

        # Verify the service was created and properly initialized
        assert address_service is not None
        assert address_service.api_client == client

        # Call a method to ensure it works
        result = address_service.list(folder="test")
        assert result == []

    def test_commit_basic(self):
        """Test basic commit functionality without sync."""
        mock_response = {
            "success": True,
            "job_id": "1586",
            "message": "CommitAndPush job enqueued with jobid 1586",
        }
        self.session.request.return_value.json.return_value = mock_response

        result = self.client.commit(
            folders=["folder1", "folder2"],
            description="Test commit",
            admin=["admin@example.com"],
        )

        assert isinstance(result, CandidatePushResponseModel)
        assert result.success is True
        assert result.job_id == "1586"
        self.session.request.assert_called_once_with(
            "POST",
            "https://api.strata.paloaltonetworks.com/config/operations/v1/config-versions/candidate:push",
            json={
                "folders": ["folder1", "folder2"],
                "description": "Test commit",
                "admin": ["admin@example.com"],
            },
            verify=ANY,
        )

    def test_commit_with_sync(self):
        """Test commit with sync enabled."""
        # Mock the client_id to return a string
        self.client.oauth_client.auth_request.client_id = "test@example.com"

        # Mock the initial commit response
        commit_response = {
            "success": True,
            "job_id": "1586",
            "message": "CommitAndPush job enqueued with jobid 1586",
        }

        # Mock the job status responses for wait_for_job
        job_status_response = {
            "data": [
                {
                    "id": "1586",
                    "status_str": "FIN",
                    "status_i": "2",
                    "start_ts": "2024-11-30T10:00:00",
                    "insert_ts": "2024-11-30T10:00:00",
                    "last_update": "2024-11-30T10:02:00",
                    "job_status": "2",
                    "job_type": "53",
                    "job_result": "2",
                    "result_i": "2",
                    "result_str": "OK",
                    "details": "completed",
                    "owner": "test",
                    "percent": "100",
                    "type_i": "53",
                    "type_str": "CommitAndPush",
                    "uname": "test-user",
                }
            ]
        }

        # Setup mock responses
        self.session.request.return_value.json.side_effect = [
            commit_response,
            job_status_response,
        ]

        with patch("time.sleep"):  # Mock sleep to speed up test
            result = self.client.commit(
                folders=["folder1"],
                description="Test commit with sync",
                sync=True,
                timeout=30,
            )

        assert isinstance(result, CandidatePushResponseModel)
        assert result.success is True
        assert result.job_id == "1586"
        assert self.session.request.call_count == 2  # One for commit, one for status check

    def test_commit_sync_timeout(self):
        """Test commit with sync that times out."""
        # Mock the client_id to return a string
        self.client.oauth_client.auth_request.client_id = "test@example.com"

        # Mock the initial commit response
        commit_response = {
            "success": True,
            "job_id": "1586",
            "message": "CommitAndPush job enqueued with jobid 1586",
        }

        # Mock the job status response for a running job
        job_status_response = {
            "data": [
                {
                    "id": "1586",
                    "status_str": "RUN",
                    "status_i": "1",
                    "start_ts": "2024-11-30T10:00:00",
                    "insert_ts": "2024-11-30T10:00:00",
                    "last_update": "2024-11-30T10:01:00",
                    "job_status": "1",
                    "job_type": "53",
                    "job_result": "0",
                    "details": "running",
                    "owner": "test",
                    "percent": "50",
                    "result_i": "0",
                    "result_str": "PENDING",
                    "type_i": "53",
                    "type_str": "CommitAndPush",
                    "uname": "test-user",
                }
            ]
        }

        self.session.request.return_value.json.side_effect = [
            commit_response,
            job_status_response,
            job_status_response,  # Multiple status checks that show it's still running
        ]

        with patch("time.sleep"), patch("time.time", side_effect=[0, 31, 32]):
            with pytest.raises(TimeoutError) as exc_info:
                self.client.commit(
                    folders=["folder1"],
                    description="Test commit timeout",
                    sync=True,
                    timeout=30,
                )

            assert "did not complete within 30 seconds" in str(exc_info.value)

    def test_commit_default_admin(self):
        """Test commit using default admin (client_id)."""
        # Mock the client_id to return a string instead of a MagicMock
        self.client.oauth_client.auth_request.client_id = "test@example.com"

        mock_response = {
            "success": True,
            "job_id": "1586",
            "message": "CommitAndPush job enqueued with jobid 1586",
        }
        self.session.request.return_value.json.return_value = mock_response

        result = self.client.commit(
            folders=["folder1"], description="Test commit with default admin"
        )

        assert isinstance(result, CandidatePushResponseModel)
        assert result.success is True

        # Verify the admin field defaulted to client_id
        self.session.request.assert_called_once_with(
            "POST",
            "https://api.strata.paloaltonetworks.com/config/operations/v1/config-versions/candidate:push",
            json={
                "folders": ["folder1"],
                "description": "Test commit with default admin",
                "admin": ["test@example.com"],
            },
            verify=ANY,
        )

    def test_commit_validation_error(self):
        """Test commit with invalid parameters."""
        # Mock the client_id to return a string
        self.client.oauth_client.auth_request.client_id = "test@example.com"

        with pytest.raises(ValueError) as exc_info:
            self.client.commit(
                folders=[],  # Empty folders list should raise validation error
                description="Test commit validation",
            )

        # Updated to match Pydantic's actual error message
        assert "List should have at least 1 item after validation" in str(exc_info.value)

    def test_commit_with_all_admin(self):
        """Test commit using 'all' as admin value."""
        # Mock the client_id to return a string
        self.client.oauth_client.auth_request.client_id = "test@example.com"

        mock_response = {
            "success": True,
            "job_id": "1587",
            "message": "CommitAndPush job enqueued with jobid 1587",
        }
        self.session.request.return_value.json.return_value = mock_response

        # Test with 'all' as a string
        result = self.client.commit(
            folders=["folder1"],
            description="Test commit with 'all' admin",
            admin=["all"],
        )

        assert isinstance(result, CandidatePushResponseModel)
        assert result.success is True
        assert result.job_id == "1587"

        # Verify the admin field was processed correctly
        self.session.request.assert_called_with(
            "POST",
            "https://api.strata.paloaltonetworks.com/config/operations/v1/config-versions/candidate:push",
            json={
                "folders": ["folder1"],
                "description": "Test commit with 'all' admin",
                "admin": ["all"],
            },
            verify=ANY,
        )

        # Reset mock for the next test
        self.session.request.reset_mock()

        # Test with 'all' in a list
        result = self.client.commit(
            folders=["folder1"],
            description="Test commit with 'all' admin in list",
            admin=["all"],
        )

        assert isinstance(result, CandidatePushResponseModel)
        assert result.success is True

        # Verify the admin field was processed correctly
        self.session.request.assert_called_with(
            "POST",
            "https://api.strata.paloaltonetworks.com/config/operations/v1/config-versions/candidate:push",
            json={
                "folders": ["folder1"],
                "description": "Test commit with 'all' admin in list",
                "admin": ["all"],
            },
            verify=ANY,
        )
