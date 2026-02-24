# tests/scm/config/security/test_authentication_rule.py

"""Tests for authentication rule configuration."""

# Standard library imports
from unittest.mock import MagicMock
import uuid

from pydantic import ValidationError

# External libraries
import pytest
from requests.exceptions import HTTPError

# Local SDK imports
from scm.config.security import AuthenticationRule
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.security.authentication_rules import (
    AuthenticationRuleResponseModel,
    AuthenticationRuleUpdateModel,
)
from tests.utils import raise_mock_http_error


@pytest.mark.usefixtures("load_env")
class TestAuthenticationRuleBase:
    """Base class for Authentication Rule tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm  # noqa
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = AuthenticationRule(self.mock_scm, max_limit=5000)  # noqa


# -------------------- Test Classes Grouped by Functionality --------------------


class TestAuthenticationRuleMaxLimit(TestAuthenticationRuleBase):
    """Tests for max_limit functionality."""

    def test_default_max_limit(self):
        """Test that default max_limit is set correctly."""
        client = AuthenticationRule(self.mock_scm)  # noqa
        assert client.max_limit == AuthenticationRule.DEFAULT_MAX_LIMIT
        assert client.max_limit == 2500

    def test_custom_max_limit(self):
        """Test setting a custom max_limit."""
        client = AuthenticationRule(self.mock_scm, max_limit=1000)  # noqa
        assert client.max_limit == 1000

    def test_max_limit_setter(self):
        """Test the max_limit property setter."""
        client = AuthenticationRule(self.mock_scm)  # noqa
        client.max_limit = 3000
        assert client.max_limit == 3000

    def test_invalid_max_limit_type(self):
        """Test that invalid max_limit type raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            AuthenticationRule(self.mock_scm, max_limit="invalid")  # noqa
        assert "{'error': 'Invalid max_limit type'} - HTTP error: 400 - API error: E003" in str(
            exc_info.value
        )

    def test_max_limit_too_low(self):
        """Test that max_limit below 1 raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            AuthenticationRule(self.mock_scm, max_limit=0)  # noqa
        assert "{'error': 'Invalid max_limit value'} - HTTP error: 400 - API error: E003" in str(
            exc_info.value
        )

    def test_max_limit_too_high(self):
        """Test that max_limit above ABSOLUTE_MAX_LIMIT raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            AuthenticationRule(self.mock_scm, max_limit=6000)  # noqa
        assert "max_limit exceeds maximum allowed value" in str(exc_info.value)


class TestAuthenticationRuleCreate(TestAuthenticationRuleBase):
    """Tests for creating Authentication Rule objects."""

    def test_create_valid_object(self):
        """Test creating an object with valid data."""
        test_data = {
            "name": "test-auth-rule",
            "folder": "Texas",
            "from": ["trust"],
            "to": ["untrust"],
            "source": ["any"],
            "destination": ["any"],
        }

        mock_response = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-auth-rule",
            "folder": "Texas",
            "from": ["trust"],
            "to": ["untrust"],
            "source": ["any"],
            "destination": ["any"],
        }

        self.mock_scm.post.return_value = mock_response  # noqa
        created_object = self.client.create(test_data)

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/identity/v1/authentication-rules",
            params={"position": "pre"},
            json={
                "name": "test-auth-rule",
                "folder": "Texas",
                "from": ["trust"],
                "to": ["untrust"],
                "source": ["any"],
                "destination": ["any"],
            },
        )
        assert isinstance(created_object, AuthenticationRuleResponseModel)
        assert created_object.name == "test-auth-rule"

    def test_create_http_error_no_content(self):
        """Test creation with HTTPError without content."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.post.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.create(
                {
                    "name": "test",
                    "folder": "Texas",
                }
            )

    def test_create_http_error_with_response(self):
        """Test that HTTPError with response content triggers proper error handling."""
        test_data = {
            "name": "test-rule",
            "folder": "Texas",
            "from": ["any"],
            "to": ["any"],
        }

        self.mock_scm.post.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="API_I00013",
            message="Create failed",
            error_type="Malformed Command",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.create(test_data)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Create failed"
        assert error_response["_errors"][0]["details"]["errorType"] == "Malformed Command"

    def test_create_generic_exception_handling(self):
        """Test handling of a generic exception during create."""
        self.mock_scm.post.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.create(
                {
                    "name": "test-rule",
                    "folder": "Texas",
                }
            )
        assert str(exc_info.value) == "Generic error"

    def test_create_invalid_rulebase(self):
        """Test that create method raises InvalidObjectError when rulebase is invalid."""
        data = {
            "name": "test-rule",
            "folder": "Texas",
            "source": ["any"],
            "destination": ["any"],
        }
        with pytest.raises(InvalidObjectError):
            self.client.create(data, rulebase="invalid")

    @pytest.mark.parametrize("rulebase", ["pre", "post"])
    def test_create_rulebase(self, rulebase):
        """Test that create method is called with correct rulebase value."""
        test_data = {
            "name": "test-auth-rule",
            "folder": "Texas",
        }

        mock_response = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-auth-rule",
            "folder": "Texas",
        }

        self.mock_scm.post.return_value = mock_response  # noqa
        self.client.create(test_data, rulebase=rulebase)

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/identity/v1/authentication-rules",
            params={"position": rulebase},
            json={
                "name": "test-auth-rule",
                "folder": "Texas",
            },
        )


class TestAuthenticationRuleGet(TestAuthenticationRuleBase):
    """Tests for retrieving a specific Authentication Rule object."""

    def test_get_valid_object(self):
        """Test retrieving a specific object."""
        mock_response = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-auth-rule",
            "folder": "Texas",
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        retrieved_object = self.client.get("123e4567-e89b-12d3-a456-426655440000")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/identity/v1/authentication-rules/123e4567-e89b-12d3-a456-426655440000"
        )
        assert isinstance(retrieved_object, AuthenticationRuleResponseModel)
        assert retrieved_object.name == "test-auth-rule"

    def test_get_object_not_present_error(self):
        """Test error handling when object is not present."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.get("123e4567-e89b-12d3-a456-426655440000")
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Object not found"

    def test_get_generic_exception_handling(self):
        """Test generic exception handling in get method."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"
        self.mock_scm.get.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.get(object_id)
        assert str(exc_info.value) == "Generic error"

    def test_get_http_error_no_response_content(self):
        """Test get method when HTTP error has no response content."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.get(object_id)

    def test_get_server_error(self):
        """Test handling of server errors during get method."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.get(object_id)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "An internal error occurred"

    def test_get_invalid_rulebase(self):
        """Test that get method raises InvalidObjectError when rulebase is invalid."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"
        with pytest.raises(InvalidObjectError):
            self.client.get(object_id, rulebase="invalid")

    @pytest.mark.parametrize("rulebase", ["pre", "post"])
    def test_get_rulebase(self, rulebase):
        """Test that get method works with valid rulebase values."""
        mock_response = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-auth-rule",
            "folder": "Texas",
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        self.client.get("123e4567-e89b-12d3-a456-426655440000", rulebase=rulebase)

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/identity/v1/authentication-rules/123e4567-e89b-12d3-a456-426655440000"
        )


class TestAuthenticationRuleUpdate(TestAuthenticationRuleBase):
    """Tests for updating Authentication Rule objects."""

    def test_update_valid_object(self):
        """Test updating an object with valid data."""
        update_data = AuthenticationRuleUpdateModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="updated-rule",
            source=["10.0.0.0/8"],
            destination=["192.168.1.0/24"],
        )

        mock_response = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "updated-rule",
            "folder": "Texas",
            "source": ["10.0.0.0/8"],
            "destination": ["192.168.1.0/24"],
        }

        self.mock_scm.put.return_value = mock_response  # noqa
        updated_object = self.client.update(update_data)

        self.mock_scm.put.assert_called_once()  # noqa
        call_args = self.mock_scm.put.call_args  # noqa
        assert (
            call_args[0][0]
            == "/config/identity/v1/authentication-rules/123e4567-e89b-12d3-a456-426655440000"
        )
        payload = call_args[1]["json"]
        assert payload["name"] == "updated-rule"
        assert "id" not in payload

        assert isinstance(updated_object, AuthenticationRuleResponseModel)
        assert updated_object.name == "updated-rule"

    def test_update_malformed_command_error(self):
        """Test error handling when update fails due to malformed command."""
        update_data = AuthenticationRuleUpdateModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-rule",
        )

        self.mock_scm.put.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="API_I00013",
            message="Update failed",
            error_type="Malformed Command",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.update(update_data)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Update failed"

    def test_update_object_not_present_error(self):
        """Test error handling when the object to update is not present."""
        update_data = AuthenticationRuleUpdateModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-rule",
        )

        self.mock_scm.put.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.update(update_data)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Object not found"

    def test_update_http_error_no_response_content(self):
        """Test update method when HTTP error has no response content."""
        update_data = AuthenticationRuleUpdateModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-rule",
        )

        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.put.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.update(update_data)

    def test_update_generic_exception_handling(self):
        """Test handling of a generic exception during update."""
        update_data = AuthenticationRuleUpdateModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-rule",
        )

        self.mock_scm.put.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.update(update_data)
        assert str(exc_info.value) == "Generic error"

    def test_update_server_error(self):
        """Test handling of server errors during update."""
        update_data = AuthenticationRuleUpdateModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-rule",
        )

        self.mock_scm.put.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.update(update_data)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "An internal error occurred"

    def test_update_invalid_rulebase(self):
        """Test that update method raises InvalidObjectError when rulebase is invalid."""
        update_data = AuthenticationRuleUpdateModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-rule",
        )

        with pytest.raises(InvalidObjectError):
            self.client.update(update_data, rulebase="invalid")

    @pytest.mark.parametrize("rulebase", ["pre", "post"])
    def test_update_rulebase(self, rulebase):
        """Test that update method is called with correct rulebase value."""
        update_data = AuthenticationRuleUpdateModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-rule",
        )

        mock_response = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-rule",
            "folder": "Texas",
        }

        self.mock_scm.put.return_value = mock_response  # noqa
        self.client.update(update_data, rulebase=rulebase)

        call_args = self.mock_scm.put.call_args  # noqa
        assert call_args[1]["params"] == {"position": rulebase}


class TestAuthenticationRuleDelete(TestAuthenticationRuleBase):
    """Tests for deleting Authentication Rule objects."""

    def test_delete_success(self):
        """Test successful deletion of an object."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.return_value = None  # noqa
        self.client.delete(object_id)

        self.mock_scm.delete.assert_called_once_with(  # noqa
            f"/config/identity/v1/authentication-rules/{object_id}",
            params={"position": "pre"},
        )

    def test_delete_referenced_object(self):
        """Test deleting an object that is referenced."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.side_effect = raise_mock_http_error(  # noqa
            status_code=409,
            error_code="E009",
            message="Reference not zero",
            error_type="Reference Not Zero",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.delete(object_id)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Reference not zero"

    def test_delete_object_not_present_error(self):
        """Test error handling when the object to delete is not present."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.delete(object_id)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Object not found"

    def test_delete_http_error_no_response_content(self):
        """Test delete method when HTTP error has no response content."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.delete.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.delete(object_id)

    def test_delete_generic_exception_handling(self):
        """Test handling of a generic exception during delete."""
        self.mock_scm.delete.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.delete("abcdefg")
        assert str(exc_info.value) == "Generic error"

    def test_delete_server_error(self):
        """Test handling of server errors during delete."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.delete(object_id)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "An internal error occurred"

    def test_delete_invalid_rulebase(self):
        """Test that delete method raises InvalidObjectError when rulebase is invalid."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"
        with pytest.raises(InvalidObjectError):
            self.client.delete(object_id, rulebase="invalid")

    @pytest.mark.parametrize("rulebase", ["pre", "post"])
    def test_delete_rulebase(self, rulebase):
        """Test that delete method is called with correct rulebase value."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.return_value = None  # noqa
        self.client.delete(object_id, rulebase=rulebase)

        self.mock_scm.delete.assert_called_once_with(  # noqa
            f"/config/identity/v1/authentication-rules/{object_id}",
            params={"position": rulebase},
        )


class TestAuthenticationRuleList(TestAuthenticationRuleBase):
    """Tests for listing Authentication Rule objects."""

    def test_list_valid(self):
        """Test listing all objects successfully."""
        mock_response = {
            "data": [
                {
                    "id": "123e4567-e89b-12d3-a456-426655440000",
                    "name": "rule1",
                    "folder": "Texas",
                    "from": ["trust"],
                    "to": ["untrust"],
                    "source": ["any"],
                    "destination": ["any"],
                },
                {
                    "id": "223e4567-e89b-12d3-a456-426655440000",
                    "name": "rule2",
                    "folder": "Texas",
                    "from": ["untrust"],
                    "to": ["trust"],
                    "source": ["any"],
                    "destination": ["any"],
                },
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        existing_objects = self.client.list(folder="Texas")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/identity/v1/authentication-rules",
            params={
                "folder": "Texas",
                "limit": 5000,
                "offset": 0,
                "position": "pre",
            },
        )
        assert isinstance(existing_objects, list)
        assert isinstance(existing_objects[0], AuthenticationRuleResponseModel)
        assert len(existing_objects) == 2
        assert existing_objects[0].name == "rule1"

    def test_list_folder_empty_error(self):
        """Test that an empty folder raises appropriate error."""
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.list(folder="")

        error_msg = str(exc_info.value)
        assert (
            "{'field': 'folder', 'error': '\"folder\" is not allowed to be empty'} - HTTP error: 400 - API error: E003"
            in error_msg
        )

    def test_list_folder_nonexistent_error(self):
        """Test error handling in list operation."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Listing failed",
            error_type="Operation Impossible",
        )

        with pytest.raises(HTTPError):
            self.client.list(folder="NonexistentFolder")

    def test_list_container_missing_error(self):
        """Test that InvalidObjectError is raised when no container parameter is provided."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list()

        error_msg = str(exc_info.value)
        assert "HTTP error: 400 - API error: E003" in error_msg

    def test_list_container_multiple_error(self):
        """Test validation of container parameters."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="folder1", snippet="snippet1")

        error_msg = str(exc_info.value)
        assert "HTTP error: 400 - API error: E003" in error_msg

    def test_list_response_invalid_format(self):
        """Test that InvalidObjectError is raised when the response is not a dictionary."""
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Texas")

        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500

    def test_list_response_invalid_data_field_missing(self):
        """Test that InvalidObjectError is raised when response missing data field."""
        self.mock_scm.get.return_value = {"wrong_field": "value"}  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Texas")

        error = exc_info.value
        assert error.error_code == "E003"
        assert error.http_status_code == 500

    def test_list_response_invalid_data_field_type(self):
        """Test that InvalidObjectError is raised when data field is not a list."""
        self.mock_scm.get.return_value = {"data": "not a list"}  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Texas")

        error = exc_info.value
        assert error.error_code == "E003"
        assert error.http_status_code == 500

    def test_list_http_error_no_content(self):
        """Test handling of HTTPError without content."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.list(folder="Texas")

    def test_list_invalid_rulebase(self):
        """Test that list method raises InvalidObjectError when rulebase is invalid."""
        with pytest.raises(InvalidObjectError):
            self.client.list(folder="Texas", rulebase="invalid")

    @pytest.mark.parametrize("rulebase", ["pre", "post"])
    def test_list_rulebase(self, rulebase):
        """Test that list method is called with correct rulebase value."""
        mock_response = {
            "data": [
                {
                    "id": "123e4567-e89b-12d3-a456-426655440000",
                    "name": "rule1",
                    "folder": "Texas",
                },
            ],
            "offset": 0,
            "total": 1,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        self.client.list(folder="Texas", rulebase=rulebase)

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/identity/v1/authentication-rules",
            params={
                "folder": "Texas",
                "limit": 5000,
                "offset": 0,
                "position": rulebase,
            },
        )

    def test_list_exact_match(self):
        """Test that exact_match=True returns only objects that match the container exactly."""
        mock_response = {
            "data": [
                {
                    "id": "12345678-1234-5678-1234-567812345678",
                    "name": "rule_in_texas",
                    "folder": "Texas",
                },
                {
                    "id": "12345678-1234-5678-1234-567812345671",
                    "name": "rule_in_all",
                    "folder": "All",
                },
            ]
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        filtered = self.client.list(folder="Texas", exact_match=True)
        assert len(filtered) == 1
        assert filtered[0].folder == "Texas"
        assert filtered[0].name == "rule_in_texas"

    def test_list_exclude_folders(self):
        """Test that exclude_folders removes objects from those folders."""
        mock_response = {
            "data": [
                {
                    "id": "12345678-1234-5678-1234-567812345678",
                    "name": "rule_in_texas",
                    "folder": "Texas",
                },
                {
                    "id": "12345678-1234-5678-1234-567812345671",
                    "name": "rule_in_all",
                    "folder": "All",
                },
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        filtered = self.client.list(folder="Texas", exclude_folders=["All"])
        assert len(filtered) == 1
        assert all(a.folder != "All" for a in filtered)

    def test_list_exclude_snippets(self):
        """Test that exclude_snippets removes objects with those snippets."""
        mock_response = {
            "data": [
                {
                    "id": "12345678-1234-5678-1234-567812345678",
                    "name": "rule_with_default_snippet",
                    "folder": "Texas",
                    "snippet": "default",
                },
                {
                    "id": "12345678-1234-5678-1234-567812345671",
                    "name": "rule_with_special_snippet",
                    "folder": "Texas",
                    "snippet": "special",
                },
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        filtered = self.client.list(folder="Texas", exclude_snippets=["default"])
        assert len(filtered) == 1
        assert all(a.snippet != "default" for a in filtered)

    def test_list_exclude_devices(self):
        """Test that exclude_devices removes objects with those devices."""
        mock_response = {
            "data": [
                {
                    "id": "12345678-1234-5678-1234-567812345678",
                    "name": "rule_device_a",
                    "folder": "Texas",
                    "device": "DeviceA",
                },
                {
                    "id": "12345678-1234-5678-1234-567812345671",
                    "name": "rule_device_b",
                    "folder": "Texas",
                    "device": "DeviceB",
                },
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        filtered = self.client.list(folder="Texas", exclude_devices=["DeviceA"])
        assert len(filtered) == 1
        assert all(a.device != "DeviceA" for a in filtered)

    def test_list_exact_match_and_exclusions(self):
        """Test combining exact_match with exclusions."""
        mock_response = {
            "data": [
                {
                    "id": "12345678-1234-5678-1234-567812345678",
                    "name": "rule_with_default_snippet",
                    "folder": "Texas",
                    "snippet": "default",
                },
                {
                    "id": "12345678-1234-5678-1234-567812345671",
                    "name": "rule_with_special_snippet",
                    "folder": "Texas",
                    "snippet": "special",
                },
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        filtered = self.client.list(
            folder="Texas",
            exact_match=True,
            exclude_folders=["All"],
            exclude_snippets=["default"],
            exclude_devices=["DeviceA"],
        )
        assert len(filtered) == 1
        obj = filtered[0]
        assert obj.folder == "Texas"
        assert obj.snippet != "default"

    def test_list_pagination_multiple_pages(self):
        """Test that the list method correctly aggregates data from multiple pages."""
        client = AuthenticationRule(self.mock_scm, max_limit=2500)  # noqa

        first_page = [
            {
                "id": str(uuid.uuid4()),
                "name": f"rule-page1-{i}",
                "folder": "Texas",
                "from": ["trust"],
                "to": ["untrust"],
            }
            for i in range(2500)
        ]

        second_page = [
            {
                "id": str(uuid.uuid4()),
                "name": f"rule-page2-{i}",
                "folder": "Texas",
                "from": ["untrust"],
                "to": ["trust"],
            }
            for i in range(2500)
        ]

        third_page = [
            {
                "id": str(uuid.uuid4()),
                "name": f"rule-page3-{i}",
                "folder": "Texas",
                "from": ["dmz"],
                "to": ["trust"],
            }
            for i in range(2500)
        ]

        mock_responses = [
            {"data": first_page},
            {"data": second_page},
            {"data": third_page},
            {"data": []},
        ]
        self.mock_scm.get.side_effect = mock_responses  # noqa

        results = client.list(folder="Texas")

        assert len(results) == 7500
        assert isinstance(results[0], AuthenticationRuleResponseModel)
        assert all(isinstance(obj, AuthenticationRuleResponseModel) for obj in results)
        assert self.mock_scm.get.call_count == 4  # noqa

        self.mock_scm.get.assert_any_call(  # noqa
            "/config/identity/v1/authentication-rules",
            params={"folder": "Texas", "limit": 2500, "offset": 0, "position": "pre"},
        )
        self.mock_scm.get.assert_any_call(  # noqa
            "/config/identity/v1/authentication-rules",
            params={"folder": "Texas", "limit": 2500, "offset": 2500, "position": "pre"},
        )
        self.mock_scm.get.assert_any_call(  # noqa
            "/config/identity/v1/authentication-rules",
            params={"folder": "Texas", "limit": 2500, "offset": 5000, "position": "pre"},
        )

        assert results[0].name == "rule-page1-0"
        assert results[2500].name == "rule-page2-0"
        assert results[5000].name == "rule-page3-0"


class TestAuthenticationRuleListFilters(TestAuthenticationRuleBase):
    """Tests for Authentication Rule list filtering."""

    def test_list_filter_by_category(self):
        """Test filtering by category."""
        mock_response = {
            "data": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "rule1",
                    "folder": "Texas",
                    "category": ["social-networking"],
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "rule2",
                    "folder": "Texas",
                    "category": ["news"],
                },
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        filtered = self.client.list(folder="Texas", category=["social-networking"])
        assert len(filtered) == 1
        assert filtered[0].name == "rule1"

    def test_list_filter_by_category_invalid_type(self):
        """Test that category filter must be a list."""
        mock_rules = []
        with pytest.raises(InvalidObjectError):
            self.client._apply_filters(mock_rules, {"category": "social-networking"})

    def test_list_filter_by_service(self):
        """Test filtering by service."""
        mock_response = {
            "data": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "rule1",
                    "folder": "Texas",
                    "service": ["tcp/443"],
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "rule2",
                    "folder": "Texas",
                    "service": ["tcp/80"],
                },
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        filtered = self.client.list(folder="Texas", service=["tcp/443"])
        assert len(filtered) == 1
        assert filtered[0].name == "rule1"

    def test_list_filter_by_service_invalid_type(self):
        """Test that service filter must be a list."""
        mock_rules = []
        with pytest.raises(InvalidObjectError):
            self.client._apply_filters(mock_rules, {"service": "tcp/443"})

    def test_list_filter_by_destination(self):
        """Test filtering by destination."""
        mock_response = {
            "data": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "rule1",
                    "folder": "Texas",
                    "destination": ["10.0.0.0/8"],
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "rule2",
                    "folder": "Texas",
                    "destination": ["192.168.1.0/24"],
                },
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        filtered = self.client.list(folder="Texas", destination=["10.0.0.0/8"])
        assert len(filtered) == 1
        assert filtered[0].name == "rule1"

    def test_list_filter_by_destination_invalid_type(self):
        """Test that destination filter must be a list."""
        mock_rules = []
        with pytest.raises(InvalidObjectError):
            self.client._apply_filters(mock_rules, {"destination": "10.0.0.0/8"})

    def test_list_filter_by_to(self):
        """Test filtering by to_ zones."""
        mock_response = {
            "data": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "rule1",
                    "folder": "Texas",
                    "to": ["untrust"],
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "rule2",
                    "folder": "Texas",
                    "to": ["trust"],
                },
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        filtered = self.client.list(folder="Texas", to_=["untrust"])
        assert len(filtered) == 1
        assert filtered[0].name == "rule1"

    def test_list_filter_by_to_invalid_type(self):
        """Test that to_ filter must be a list."""
        mock_rules = []
        with pytest.raises(InvalidObjectError):
            self.client._apply_filters(mock_rules, {"to_": "untrust"})

    def test_list_filter_by_source(self):
        """Test filtering by source."""
        mock_response = {
            "data": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "rule1",
                    "folder": "Texas",
                    "source": ["10.0.0.0/24"],
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "rule2",
                    "folder": "Texas",
                    "source": ["any"],
                },
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        filtered = self.client.list(folder="Texas", source=["10.0.0.0/24"])
        assert len(filtered) == 1
        assert filtered[0].name == "rule1"

    def test_list_filter_by_source_invalid_type(self):
        """Test that source filter must be a list."""
        mock_rules = []
        with pytest.raises(InvalidObjectError):
            self.client._apply_filters(mock_rules, {"source": "10.0.0.0/24"})

    def test_list_filter_by_from(self):
        """Test filtering by from_ zones."""
        mock_response = {
            "data": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "rule1",
                    "folder": "Texas",
                    "from": ["trust"],
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "rule2",
                    "folder": "Texas",
                    "from": ["untrust"],
                },
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        filtered = self.client.list(folder="Texas", from_=["trust"])
        assert len(filtered) == 1
        assert filtered[0].name == "rule1"

    def test_list_filter_by_from_invalid_type(self):
        """Test that from_ filter must be a list."""
        mock_rules = []
        with pytest.raises(InvalidObjectError):
            self.client._apply_filters(mock_rules, {"from_": "trust"})

    def test_list_filter_by_tag(self):
        """Test filtering by tag."""
        mock_response = {
            "data": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "rule1",
                    "folder": "Texas",
                    "tag": ["tag1", "tag2"],
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "rule2",
                    "folder": "Texas",
                    "tag": ["tag3"],
                },
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        filtered = self.client.list(folder="Texas", tag=["tag1"])
        assert len(filtered) == 1
        assert filtered[0].name == "rule1"

    def test_list_filter_by_tag_no_match_empty_tag(self):
        """Test that tag filter excludes rules with no tags."""
        mock_response = {
            "data": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "rule1",
                    "folder": "Texas",
                    "tag": [],
                },
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        filtered = self.client.list(folder="Texas", tag=["tag1"])
        assert len(filtered) == 0

    def test_list_filter_by_tag_invalid_type(self):
        """Test that tag filter must be a list."""
        mock_rules = []
        with pytest.raises(InvalidObjectError):
            self.client._apply_filters(mock_rules, {"tag": "tag1"})

    def test_list_filter_by_disabled(self):
        """Test filtering by disabled status."""
        mock_response = {
            "data": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "rule1",
                    "folder": "Texas",
                    "disabled": True,
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "rule2",
                    "folder": "Texas",
                    "disabled": False,
                },
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test filtering disabled rules
        filtered = self.client.list(folder="Texas", disabled=True)
        assert len(filtered) == 1
        assert filtered[0].name == "rule1"
        assert filtered[0].disabled is True

        # Test filtering enabled rules
        self.mock_scm.get.return_value = mock_response  # noqa
        filtered = self.client.list(folder="Texas", disabled=False)
        assert len(filtered) == 1
        assert filtered[0].name == "rule2"
        assert filtered[0].disabled is False

    def test_list_filter_by_disabled_invalid_type_string(self):
        """Test that disabled filter must be a boolean (string)."""
        mock_rules = []
        with pytest.raises(InvalidObjectError):
            self.client._apply_filters(mock_rules, {"disabled": "true"})

    def test_list_filter_by_disabled_invalid_type_int(self):
        """Test that disabled filter must be a boolean (int)."""
        mock_rules = []
        with pytest.raises(InvalidObjectError):
            self.client._apply_filters(mock_rules, {"disabled": 1})

    def test_list_filter_by_disabled_invalid_type_list(self):
        """Test that disabled filter must be a boolean (list)."""
        mock_rules = []
        with pytest.raises(InvalidObjectError):
            self.client._apply_filters(mock_rules, {"disabled": [True]})

    def test_list_filter_by_log_setting(self):
        """Test filtering by log_setting."""
        mock_response = {
            "data": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "rule1",
                    "folder": "Texas",
                    "log_setting": "default-logging",
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "rule2",
                    "folder": "Texas",
                    "log_setting": "custom-logging",
                },
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        filtered = self.client.list(folder="Texas", log_setting=["default-logging"])
        assert len(filtered) == 1
        assert filtered[0].name == "rule1"
        assert filtered[0].log_setting == "default-logging"

        # Test filtering by multiple log settings
        self.mock_scm.get.return_value = mock_response  # noqa
        filtered = self.client.list(
            folder="Texas", log_setting=["default-logging", "custom-logging"]
        )
        assert len(filtered) == 2

    def test_list_filter_by_log_setting_invalid_type_string(self):
        """Test that log_setting filter must be a list (string)."""
        mock_rules = []
        with pytest.raises(InvalidObjectError):
            self.client._apply_filters(mock_rules, {"log_setting": "default-logging"})

    def test_list_filter_by_log_setting_invalid_type_int(self):
        """Test that log_setting filter must be a list (int)."""
        mock_rules = []
        with pytest.raises(InvalidObjectError):
            self.client._apply_filters(mock_rules, {"log_setting": 1})

    def test_list_filter_by_log_setting_invalid_type_dict(self):
        """Test that log_setting filter must be a list (dict)."""
        mock_rules = []
        with pytest.raises(InvalidObjectError):
            self.client._apply_filters(mock_rules, {"log_setting": {"setting": "default"}})

    def test_list_filters_empty_lists(self):
        """Test behavior with empty filter lists."""
        mock_response = {
            "data": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "rule1",
                    "folder": "Texas",
                },
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Empty category should result in no matches
        filtered = self.client.list(folder="Texas", category=[])
        assert len(filtered) == 0

        self.mock_scm.get.return_value = mock_response  # noqa
        filtered = self.client.list(folder="Texas", service=[])
        assert len(filtered) == 0

        self.mock_scm.get.return_value = mock_response  # noqa
        filtered = self.client.list(folder="Texas", log_setting=[])
        assert len(filtered) == 0

    def test_list_complex_filtering(self):
        """Test multiple filters combined."""
        mock_response = {
            "data": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "rule1",
                    "folder": "Texas",
                    "source": ["10.0.0.0/24"],
                    "destination": ["any"],
                    "from": ["trust"],
                    "to": ["untrust"],
                    "tag": ["tag1", "tag2"],
                    "category": ["any"],
                    "service": ["any"],
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "rule2",
                    "folder": "Texas",
                    "source": ["10.0.0.0/24"],
                    "destination": ["any"],
                    "from": ["trust"],
                    "to": ["untrust"],
                    "tag": ["tag2"],
                    "category": ["any"],
                    "service": ["any"],
                },
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        filtered = self.client.list(
            folder="Texas",
            source=["10.0.0.0/24"],
            from_=["trust"],
            tag=["tag1"],
        )

        assert len(filtered) == 1
        assert filtered[0].name == "rule1"


class TestAuthenticationRuleFetch(TestAuthenticationRuleBase):
    """Tests for fetching Authentication Rule objects by name."""

    def test_fetch_valid_object(self):
        """Test retrieving an object by its name using the fetch method."""
        mock_response = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-auth-rule",
            "folder": "Texas",
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        fetched_object = self.client.fetch(
            name="test-auth-rule",
            folder="Texas",
        )

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/identity/v1/authentication-rules",
            params={
                "folder": "Texas",
                "name": "test-auth-rule",
                "position": "pre",
            },
        )

        assert isinstance(fetched_object, AuthenticationRuleResponseModel)
        assert fetched_object.name == "test-auth-rule"
        assert str(fetched_object.id) == "123e4567-e89b-12d3-a456-426655440000"

    def test_fetch_valid_object_with_position(self):
        """Test retrieving an object using the fetch method with explicit position."""
        mock_response = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-auth-rule",
            "folder": "Texas",
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        fetched_object = self.client.fetch(
            name="test-auth-rule",
            folder="Texas",
            rulebase="post",
        )

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/identity/v1/authentication-rules",
            params={
                "folder": "Texas",
                "name": "test-auth-rule",
                "position": "post",
            },
        )

        assert isinstance(fetched_object, AuthenticationRuleResponseModel)

    def test_fetch_object_not_present_error(self):
        """Test fetching an object that does not exist."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.fetch(name="nonexistent", folder="Texas")
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Object not found"

    def test_fetch_empty_name_error(self):
        """Test fetching with an empty name parameter."""
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="", folder="Texas")

        error_msg = str(exc_info.value)
        assert '"name" is not allowed to be empty' in error_msg
        assert "HTTP error: 400" in error_msg
        assert "API error: E003" in error_msg

    def test_fetch_empty_container_error(self):
        """Test fetching with an empty folder parameter."""
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="test", folder="")

        error_msg = str(exc_info.value)
        assert '"folder" is not allowed to be empty' in error_msg
        assert "HTTP error: 400" in error_msg
        assert "API error: E003" in error_msg

    def test_fetch_no_container_provided_error(self):
        """Test that InvalidObjectError is raised when no container is provided."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-rule")

        error_msg = str(exc_info.value)
        assert "HTTP error: 400 - API error: E003" in error_msg

    def test_fetch_multiple_containers_provided_error(self):
        """Test that InvalidObjectError is raised when multiple containers are provided."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(
                name="test-rule",
                folder="Texas",
                snippet="TestSnippet",
            )

        error_msg = str(exc_info.value)
        assert "HTTP error: 400 - API error: E003" in error_msg

    def test_fetch_http_error_no_response_content(self):
        """Test that an HTTPError without response content re-raises the exception."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.fetch(name="test-rule", folder="Texas")

    def test_fetch_server_error(self):
        """Test handling of server errors during fetch."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.fetch(name="test", folder="Texas")
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "An internal error occurred"

    def test_fetch_missing_id_field_error(self):
        """Test that InvalidObjectError is raised when response missing 'id' field."""
        mock_response = {
            "name": "test-rule",
            "folder": "Texas",
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-rule", folder="Texas")

        error_msg = str(exc_info.value)
        assert "HTTP error: 500 - API error: E003" in error_msg

    def test_fetch_invalid_response_type_error(self):
        """Test that InvalidObjectError is raised when response is not a dictionary."""
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test123", folder="Texas")

        error_msg = str(exc_info.value)
        assert "HTTP error: 500 - API error: E003" in error_msg

    def test_fetch_invalid_rulebase(self):
        """Test that fetch raises InvalidObjectError when rulebase is invalid."""
        with pytest.raises(InvalidObjectError):
            self.client.fetch(name="test-rule", folder="Texas", rulebase="invalid")


class TestAuthenticationRuleMove(TestAuthenticationRuleBase):
    """Tests for moving Authentication Rule objects."""

    def test_move_valid_top(self):
        """Test moving a rule successfully to the top."""
        rule_id = "123e4567-e89b-12d3-a456-426655440000"
        move_data = {
            "destination": "top",
            "rulebase": "pre",
        }

        self.mock_scm.post.return_value = None  # noqa
        self.client.move(rule_id, move_data)

        self.mock_scm.post.assert_called_once_with(  # noqa
            f"/config/identity/v1/authentication-rules/{rule_id}:move",
            json=move_data,
        )

    def test_move_valid_bottom(self):
        """Test moving a rule successfully to the bottom."""
        rule_id = "123e4567-e89b-12d3-a456-426655440000"
        move_data = {
            "destination": "bottom",
            "rulebase": "post",
        }

        self.mock_scm.post.return_value = None  # noqa
        self.client.move(rule_id, move_data)

        self.mock_scm.post.assert_called_once_with(  # noqa
            f"/config/identity/v1/authentication-rules/{rule_id}:move",
            json=move_data,
        )

    def test_move_before_rule(self):
        """Test moving a rule before another rule."""
        source_rule = "123e4567-e89b-12d3-a456-426655440000"
        dest_rule_id = "987fcdeb-54ba-3210-9876-fedcba098765"
        move_data = {
            "destination": "before",
            "rulebase": "pre",
            "destination_rule": dest_rule_id,
        }

        expected_data = {
            "destination": "before",
            "rulebase": "pre",
            "destination_rule": dest_rule_id,
        }

        self.mock_scm.post.return_value = None  # noqa
        self.client.move(source_rule, move_data)

        self.mock_scm.post.assert_called_once_with(  # noqa
            f"/config/identity/v1/authentication-rules/{source_rule}:move",
            json=expected_data,
        )

    def test_move_after_rule(self):
        """Test moving a rule after another rule."""
        source_rule = "123e4567-e89b-12d3-a456-426655440000"
        dest_rule_id = "987fcdeb-54ba-3210-9876-fedcba098765"
        move_data = {
            "destination": "after",
            "rulebase": "pre",
            "destination_rule": dest_rule_id,
        }

        expected_data = {
            "destination": "after",
            "rulebase": "pre",
            "destination_rule": dest_rule_id,
        }

        self.mock_scm.post.return_value = None  # noqa
        self.client.move(source_rule, move_data)

        self.mock_scm.post.assert_called_once_with(  # noqa
            f"/config/identity/v1/authentication-rules/{source_rule}:move",
            json=expected_data,
        )

    def test_move_invalid_destination_error(self):
        """Test error handling when move destination is invalid."""
        source_rule = str(uuid.uuid4())
        move_data = {
            "destination": "invalid",
            "destination_rule": str(uuid.uuid4()),
            "rulebase": "pre",
        }

        with pytest.raises(ValidationError) as exc_info:
            self.client.move(source_rule, move_data)

        assert "Input should be 'top', 'bottom', 'before' or 'after'" in str(exc_info.value)

    def test_move_missing_destination_rule_error(self):
        """Test error handling when destination_rule is missing for before/after moves."""
        source_rule = str(uuid.uuid4())
        move_data = {
            "destination": "before",
            "rulebase": "pre",
        }

        with pytest.raises(ValidationError) as exc_info:
            self.client.move(source_rule, move_data)

        assert "destination_rule is required when destination is 'before'" in str(exc_info.value)

    def test_move_rule_not_found_error(self):
        """Test error handling when source or destination rule is not found."""
        rule_id = "123e4567-e89b-12d3-a456-426655440000"
        move_data = {
            "destination": "top",
            "rulebase": "pre",
        }

        self.mock_scm.post.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Rule not found",
            error_type="Object Not Present",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.move(rule_id, move_data)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Rule not found"

    def test_move_http_error_no_response_content(self):
        """Test move method when HTTP error has no response content."""
        rule_id = "123e4567-e89b-12d3-a456-426655440000"
        move_data = {
            "destination": "top",
            "rulebase": "pre",
        }

        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.post.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.move(rule_id, move_data)

    def test_move_generic_exception_handling(self):
        """Test handling of a generic exception during move."""
        rule_id = "123e4567-e89b-12d3-a456-426655440000"
        move_data = {
            "destination": "top",
            "rulebase": "pre",
        }

        self.mock_scm.post.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.move(rule_id, move_data)
        assert str(exc_info.value) == "Generic error"

    def test_move_server_error(self):
        """Test handling of server errors during move."""
        rule_id = "123e4567-e89b-12d3-a456-426655440000"
        move_data = {
            "destination": "top",
            "rulebase": "pre",
        }

        self.mock_scm.post.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.move(rule_id, move_data)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "An internal error occurred"


# -------------------- End of Test Classes --------------------
