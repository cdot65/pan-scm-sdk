# tests/scm/exceptions/test_exceptions.py

"""Tests for SCM exception handling."""

from unittest.mock import MagicMock

import pytest

from scm.exceptions import (
    ActionNotSupportedError,
    APIError,
    APINotImplementedError,
    AuthenticationError,
    AuthorizationError,
    BadRequestError,
    BadXPathError,
    ClientError,
    ConflictError,
    ErrorHandler,
    ErrorResponse,
    GatewayTimeoutError,
    InputFormatMismatchError,
    InvalidCommandError,
    InvalidCredentialError,
    InvalidObjectError,
    InvalidQueryParameterError,
    KeyExpiredError,
    KeyTooLongError,
    MalformedCommandError,
    MethodAPINotSupportedError,
    MethodNotAllowedError,
    MissingBodyError,
    MissingQueryParameterError,
    NameNotUniqueError,
    NotAuthenticatedError,
    NotFoundError,
    ObjectNotPresentError,
    ObjectNotUniqueError,
    OutputFormatMismatchError,
    PasswordChangeRequiredError,
    ReferenceNotZeroError,
    ServerError,
    SessionTimeoutError,
    UnauthorizedError,
    VersionAPINotSupportedError,
)


@pytest.mark.usefixtures("load_env")
class TestExceptionsBase:
    """Base class for Exception tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm  # noqa
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()


# -------------------- Test Classes Grouped by Functionality --------------------


class TestErrorResponseValidation(TestExceptionsBase):
    """Tests for ErrorResponse validation."""

    def test_error_response_from_response(self):
        """Test creating ErrorResponse from API response."""
        response_data = {
            "_errors": [
                {
                    "code": "API_I00013",
                    "message": "Test error message",
                    "details": {"errorType": "Test Error"},
                }
            ],
            "_request_id": "test-request-id",
        }

        error_response = ErrorResponse.from_response(response_data)
        assert error_response.code == "API_I00013"
        assert error_response.message == "Test error message"
        assert error_response.details == {"errorType": "Test Error"}

    def test_error_response_invalid_format(self):
        """Test validation when response format is invalid."""
        invalid_data = {"not_errors": []}
        with pytest.raises(ValueError) as exc_info:
            ErrorResponse.from_response(invalid_data)
        assert str(exc_info.value) == "Invalid error response format"

    def test_error_response_empty_errors(self):
        """Test validation when errors list is empty."""
        invalid_data = {"_errors": []}
        with pytest.raises(ValueError) as exc_info:
            ErrorResponse.from_response(invalid_data)
        assert str(exc_info.value) == "Invalid error response format"


class TestAPIErrorBase(TestExceptionsBase):
    """Tests for base APIError class."""

    def test_api_error_str_representation(self):
        """Test string representation of APIError."""
        error = APIError(
            message="Test error",
            error_code="TEST001",
            http_status_code=400,
            details={"type": "test"},
        )
        error_str = str(error)
        assert "{'type': 'test'} - HTTP error: 400 - API error: TEST001" in error_str

    def test_api_error_minimal_str(self):
        """Test string representation with minimal fields."""
        APIError(message="Test error")


class TestErrorHandlerValidation(TestExceptionsBase):
    """Tests for ErrorHandler validation."""

    def test_error_handler_status_code_mapping(self):
        """Test HTTP status code to exception class mapping."""
        response_data = {
            "_errors": [
                {
                    "code": "TEST001",
                    "message": "Test error",
                }
            ]
        }

        # Test 400 maps to BadRequestError
        with pytest.raises(BadRequestError):
            ErrorHandler.raise_for_error(response_data, 400)

        # Test 401 maps to AuthenticationError
        with pytest.raises(AuthenticationError):
            ErrorHandler.raise_for_error(response_data, 401)

        # Test 403 maps to AuthorizationError
        with pytest.raises(AuthorizationError):
            ErrorHandler.raise_for_error(response_data, 403)

    def test_error_handler_code_mapping(self):
        """Test error code to specific exception mapping."""
        # Test E016 Not Authenticated
        response_data = {
            "_errors": [
                {
                    "code": "E016",
                    "message": "Not Authenticated",
                }
            ]
        }
        with pytest.raises(AuthenticationError):
            ErrorHandler.raise_for_error(response_data, 401)

        # Test E007 Unauthorized
        response_data["_errors"][0].update({"code": "E007", "message": "Unauthorized"})
        with pytest.raises(UnauthorizedError):
            ErrorHandler.raise_for_error(response_data, 403)

    def test_error_handler_fallback(self):
        """Test fallback to base exception class."""
        response_data = {
            "_errors": [
                {
                    "code": "UNKNOWN",
                    "message": "Unknown error",
                }
            ]
        }
        with pytest.raises(APIError):
            ErrorHandler.raise_for_error(response_data, 418)


class TestSpecificExceptions(TestExceptionsBase):
    """Tests for specific exception classes."""

    def test_client_error_inheritance(self):
        """Test ClientError class inheritance."""
        error = ClientError("Test client error")
        assert isinstance(error, APIError)
        assert isinstance(error, ClientError)

    def test_server_error_inheritance(self):
        """Test ServerError class inheritance."""
        error = ServerError("Test server error")
        assert isinstance(error, APIError)
        assert isinstance(error, ServerError)

    def test_authentication_error_inheritance(self):
        """Test authentication error inheritance chain."""
        error = NotAuthenticatedError("Not authenticated")
        assert isinstance(error, APIError)
        assert isinstance(error, ClientError)
        assert isinstance(error, AuthenticationError)
        assert isinstance(error, NotAuthenticatedError)

    def test_invalid_credential_error_inheritance(self):
        """Test InvalidCredentialError class inheritance."""
        error = InvalidCredentialError("Invalid credentials")
        assert isinstance(error, APIError)
        assert isinstance(error, ClientError)
        assert isinstance(error, AuthenticationError)
        assert isinstance(error, InvalidCredentialError)

    def test_key_too_long_error_inheritance(self):
        """Test KeyTooLongError class inheritance."""
        error = KeyTooLongError("Key too long")
        assert isinstance(error, APIError)
        assert isinstance(error, ClientError)
        assert isinstance(error, AuthenticationError)
        assert isinstance(error, KeyTooLongError)

    def test_key_expired_error_inheritance(self):
        """Test KeyExpiredError class inheritance."""
        error = KeyExpiredError("Key expired")
        assert isinstance(error, APIError)
        assert isinstance(error, ClientError)
        assert isinstance(error, AuthenticationError)
        assert isinstance(error, KeyExpiredError)

    def test_password_change_required_error_inheritance(self):
        """Test PasswordChangeRequiredError class inheritance."""
        error = PasswordChangeRequiredError("Password change required")
        assert isinstance(error, APIError)
        assert isinstance(error, ClientError)
        assert isinstance(error, AuthenticationError)
        assert isinstance(error, PasswordChangeRequiredError)

    def test_authorization_error_inheritance(self):
        """Test authorization error inheritance chain."""
        error = UnauthorizedError("Unauthorized")
        assert isinstance(error, APIError)
        assert isinstance(error, ClientError)
        assert isinstance(error, AuthorizationError)
        assert isinstance(error, UnauthorizedError)

    def test_bad_request_error_inheritance(self):
        """Test BadRequestError class inheritance."""
        error = BadRequestError("Bad request")
        assert isinstance(error, APIError)
        assert isinstance(error, ClientError)
        assert isinstance(error, BadRequestError)

    def test_input_format_mismatch_error_inheritance(self):
        """Test InputFormatMismatchError class inheritance."""
        error = InputFormatMismatchError("Input format mismatch")
        assert isinstance(error, APIError)
        assert isinstance(error, ClientError)
        assert isinstance(error, BadRequestError)
        assert isinstance(error, InputFormatMismatchError)

    def test_output_format_mismatch_error_inheritance(self):
        """Test OutputFormatMismatchError class inheritance."""
        error = OutputFormatMismatchError("Output format mismatch")
        assert isinstance(error, APIError)
        assert isinstance(error, ClientError)
        assert isinstance(error, BadRequestError)
        assert isinstance(error, OutputFormatMismatchError)

    def test_missing_query_parameter_error_inheritance(self):
        """Test MissingQueryParameterError class inheritance."""
        error = MissingQueryParameterError("Missing query parameter")
        assert isinstance(error, APIError)
        assert isinstance(error, ClientError)
        assert isinstance(error, BadRequestError)
        assert isinstance(error, MissingQueryParameterError)

    def test_invalid_query_parameter_error_inheritance(self):
        """Test InvalidQueryParameterError class inheritance."""
        error = InvalidQueryParameterError("Invalid query parameter")
        assert isinstance(error, APIError)
        assert isinstance(error, ClientError)
        assert isinstance(error, BadRequestError)
        assert isinstance(error, InvalidQueryParameterError)

    def test_missing_body_error_inheritance(self):
        """Test MissingBodyError class inheritance."""
        error = MissingBodyError("Missing body")
        assert isinstance(error, APIError)
        assert isinstance(error, ClientError)
        assert isinstance(error, BadRequestError)
        assert isinstance(error, MissingBodyError)

    def test_invalid_object_error_inheritance(self):
        """Test InvalidObjectError class inheritance."""
        error = InvalidObjectError("Invalid object")
        assert isinstance(error, APIError)
        assert isinstance(error, ClientError)
        assert isinstance(error, BadRequestError)
        assert isinstance(error, InvalidObjectError)

    def test_invalid_command_error_inheritance(self):
        """Test InvalidCommandError class inheritance."""
        error = InvalidCommandError("Invalid command")
        assert isinstance(error, APIError)
        assert isinstance(error, ClientError)
        assert isinstance(error, BadRequestError)
        assert isinstance(error, InvalidCommandError)

    def test_malformed_command_error_inheritance(self):
        """Test MalformedCommandError class inheritance."""
        error = MalformedCommandError("Malformed command")
        assert isinstance(error, APIError)
        assert isinstance(error, ClientError)
        assert isinstance(error, BadRequestError)
        assert isinstance(error, MalformedCommandError)

    def test_bad_xpath_error_inheritance(self):
        """Test BadXPathError class inheritance."""
        error = BadXPathError("Bad XPath")
        assert isinstance(error, APIError)
        assert isinstance(error, ClientError)
        assert isinstance(error, BadRequestError)
        assert isinstance(error, BadXPathError)

    def test_not_found_error_inheritance(self):
        """Test NotFoundError class inheritance."""
        error = NotFoundError("Not found")
        assert isinstance(error, APIError)
        assert isinstance(error, ClientError)
        assert isinstance(error, NotFoundError)

    def test_object_not_present_error_inheritance(self):
        """Test ObjectNotPresentError class inheritance."""
        error = ObjectNotPresentError("Object not present")
        assert isinstance(error, APIError)
        assert isinstance(error, ClientError)
        assert isinstance(error, NotFoundError)
        assert isinstance(error, ObjectNotPresentError)

    def test_conflict_error_inheritance(self):
        """Test ConflictError class inheritance."""
        error = ConflictError("Conflict")
        assert isinstance(error, APIError)
        assert isinstance(error, ClientError)
        assert isinstance(error, ConflictError)

    def test_object_not_unique_error_inheritance(self):
        """Test ObjectNotUniqueError class inheritance."""
        error = ObjectNotUniqueError("Object not unique")
        assert isinstance(error, APIError)
        assert isinstance(error, ClientError)
        assert isinstance(error, ConflictError)
        assert isinstance(error, ObjectNotUniqueError)

    def test_name_not_unique_error_inheritance(self):
        """Test NameNotUniqueError class inheritance."""
        error = NameNotUniqueError("Name not unique")
        assert isinstance(error, APIError)
        assert isinstance(error, ClientError)
        assert isinstance(error, ConflictError)
        assert isinstance(error, NameNotUniqueError)

    def test_reference_not_zero_error_inheritance(self):
        """Test ReferenceNotZeroError class inheritance."""
        error = ReferenceNotZeroError("Reference not zero")
        assert isinstance(error, APIError)
        assert isinstance(error, ClientError)
        assert isinstance(error, ConflictError)
        assert isinstance(error, ReferenceNotZeroError)

    def test_method_not_allowed_error_inheritance(self):
        """Test MethodNotAllowedError class inheritance."""
        error = MethodNotAllowedError("Method not allowed")
        assert isinstance(error, APIError)
        assert isinstance(error, ClientError)
        assert isinstance(error, MethodNotAllowedError)

    def test_action_not_supported_error_inheritance(self):
        """Test ActionNotSupportedError class inheritance."""
        error = ActionNotSupportedError("Action not supported")
        assert isinstance(error, APIError)
        assert isinstance(error, ClientError)
        assert isinstance(error, MethodNotAllowedError)
        assert isinstance(error, ActionNotSupportedError)

    def test_api_not_implemented_error_inheritance(self):
        """Test APINotImplementedError class inheritance."""
        error = APINotImplementedError("Not implemented")
        assert isinstance(error, APIError)
        assert isinstance(error, ServerError)
        assert isinstance(error, APINotImplementedError)

    def test_version_not_supported_error_inheritance(self):
        """Test VersionAPINotSupportedError class inheritance."""
        error = VersionAPINotSupportedError("Version not supported")
        assert isinstance(error, APIError)
        assert isinstance(error, ServerError)
        assert isinstance(error, APINotImplementedError)
        assert isinstance(error, VersionAPINotSupportedError)

    def test_method_not_supported_error_inheritance(self):
        """Test MethodAPINotSupportedError class inheritance."""
        error = MethodAPINotSupportedError("Method not supported")
        assert isinstance(error, APIError)
        assert isinstance(error, ServerError)
        assert isinstance(error, APINotImplementedError)
        assert isinstance(error, MethodAPINotSupportedError)

    def test_gateway_timeout_error_inheritance(self):
        """Test GatewayTimeoutError class inheritance."""
        error = GatewayTimeoutError("Gateway timeout")
        assert isinstance(error, APIError)
        assert isinstance(error, ServerError)
        assert isinstance(error, GatewayTimeoutError)

    def test_session_timeout_error_inheritance(self):
        """Test SessionTimeoutError class inheritance."""
        error = SessionTimeoutError("Session timeout")
        assert isinstance(error, APIError)
        assert isinstance(error, ServerError)
        assert isinstance(error, GatewayTimeoutError)
        assert isinstance(error, SessionTimeoutError)


class TestErrorHandlerMessageMapping(TestExceptionsBase):
    """Test for ErrorHandler when message matches but errorType does not."""

    def test_error_handler_message_mapping(self):
        """Test exception mapping when message matches but errorType does not."""
        response_data = {
            "_errors": [
                {
                    "code": "E003",
                    "message": "Invalid Command",
                    "details": {"errorType": "Some Unknown Error Type"},
                }
            ]
        }
        with pytest.raises(InvalidCommandError) as exc_info:
            ErrorHandler.raise_for_error(response_data, 400)
        exception = exc_info.value
        assert exception.error_code == "E003"
        assert exception.http_status_code == 400
        assert exception.message == "Invalid Command"
        assert exception.details == {"errorType": "Some Unknown Error Type"}


class TestErrorHandlerNestedErrorType(TestExceptionsBase):
    """Test for ErrorHandler when errorType is in error_details['errors'][0]['type']."""

    def test_error_handler_error_type_in_errors_list(self):
        """Test error_type extraction from error_details['errors'][0]['type']."""
        response_data = {
            "_errors": [
                {
                    "code": "E003",
                    "message": "Invalid Query Parameter",
                    "details": {
                        "errors": [
                            {
                                "type": "Invalid Query Parameter",
                                "message": "Invalid parameter 'foo'",
                            }
                        ]
                    },
                }
            ]
        }
        with pytest.raises(InvalidQueryParameterError) as exc_info:
            ErrorHandler.raise_for_error(response_data, 400)
        exception = exc_info.value
        assert exception.error_code == "E003"
        assert exception.http_status_code == 400
        assert exception.message == "Invalid Query Parameter"
        assert exception.details == response_data["_errors"][0]["details"]


# -------------------- End of Test Classes --------------------
