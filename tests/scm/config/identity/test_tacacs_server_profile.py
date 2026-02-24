# tests/scm/config/identity/test_tacacs_server_profile.py

"""Tests for TACACS+ server profile identity configuration."""

# Standard library imports
from unittest.mock import MagicMock

# External libraries
import pytest
from requests.exceptions import HTTPError

# Local SDK imports
from scm.config.identity import TacacsServerProfile
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.identity.tacacs_server_profiles import TacacsServerProfileResponseModel
from tests.factories.identity.tacacs_server_profile import (
    TacacsServerProfileCreateApiFactory,
    TacacsServerProfileResponseFactory,
    TacacsServerProfileUpdateApiFactory,
)
from tests.utils import raise_mock_http_error


@pytest.mark.usefixtures("load_env")
class TestTacacsServerProfileBase:
    """Base class for TACACS+ Server Profile tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm  # noqa
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = TacacsServerProfile(self.mock_scm, max_limit=5000)  # noqa


class TestTacacsServerProfileMaxLimit(TestTacacsServerProfileBase):
    """Tests for max_limit functionality."""

    def test_default_max_limit(self):
        """Test that default max_limit is set correctly."""
        client = TacacsServerProfile(self.mock_scm)
        assert client.max_limit == TacacsServerProfile.DEFAULT_MAX_LIMIT
        assert client.max_limit == 2500

    def test_custom_max_limit(self):
        """Test setting a custom max_limit."""
        client = TacacsServerProfile(self.mock_scm, max_limit=1000)
        assert client.max_limit == 1000

    def test_max_limit_setter(self):
        """Test the max_limit property setter."""
        client = TacacsServerProfile(self.mock_scm)
        client.max_limit = 3000
        assert client.max_limit == 3000

    def test_invalid_max_limit_type(self):
        """Test that invalid max_limit type raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            TacacsServerProfile(self.mock_scm, max_limit="invalid")
        assert "{'error': 'Invalid max_limit type'} - HTTP error: 400 - API error: E003" in str(
            exc_info.value
        )

    def test_max_limit_too_low(self):
        """Test that max_limit below 1 raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            TacacsServerProfile(self.mock_scm, max_limit=0)
        assert "{'error': 'Invalid max_limit value'} - HTTP error: 400 - API error: E003" in str(
            exc_info.value
        )

    def test_max_limit_too_high(self):
        """Test that max_limit above ABSOLUTE_MAX_LIMIT raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            TacacsServerProfile(self.mock_scm, max_limit=6000)
        assert "max_limit exceeds maximum allowed value" in str(exc_info.value)


class TestTacacsServerProfileList(TestTacacsServerProfileBase):
    """Tests for listing TACACS+ Server Profile objects."""

    def test_list_valid(self):
        """Test listing all objects successfully."""
        mock_response = {
            "data": [
                TacacsServerProfileResponseFactory(name="profile1", folder="Texas").model_dump(),
                TacacsServerProfileResponseFactory(name="profile2", folder="Texas").model_dump(),
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }
        self.mock_scm.get.return_value = mock_response
        existing_objects = self.client.list(folder="Texas")
        self.mock_scm.get.assert_called_once_with(
            "/config/identity/v1/tacacs-server-profiles",
            params={"limit": 5000, "folder": "Texas", "offset": 0},
        )
        assert isinstance(existing_objects, list)
        assert isinstance(existing_objects[0], TacacsServerProfileResponseModel)
        assert len(existing_objects) == 2

    def test_list_folder_empty_error(self):
        """Test that an empty folder raises appropriate error."""
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=400,
            error_code="E003",
            message='"folder" is not allowed to be empty',
            error_type="Missing Query Parameter",
        )
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.list(folder="")
        assert '"folder" is not allowed to be empty' in str(exc_info.value)

    def test_list_folder_nonexistent_error(self):
        """Test error handling when folder does not exist."""
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=404,
            error_code="API_I00013",
            message="Listing failed",
            error_type="Operation Impossible",
        )
        with pytest.raises(HTTPError):
            self.client.list(folder="NonexistentFolder")

    def test_list_container_missing_error(self):
        """Test that InvalidObjectError is raised when no container is provided."""
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=400,
            error_code="E003",
            message="Exactly one of 'folder', 'snippet', or 'device' must be provided.",
            error_type="Invalid Object",
        )
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list()
        assert "HTTP error: 400 - API error: E003" in str(exc_info.value)

    def test_list_container_multiple_error(self):
        """Test that InvalidObjectError is raised with multiple containers."""
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=400,
            error_code="E003",
            message="Multiple container types provided",
            error_type="Invalid Object",
        )
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="folder1", snippet="snippet1")
        assert "HTTP error: 400 - API error: E003" in str(exc_info.value)

    def test_list_response_invalid_format(self):
        """Test that InvalidObjectError is raised when response is not a dictionary."""
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Texas")
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500

    def test_list_response_invalid_data_field_missing(self):
        """Test that InvalidObjectError is raised when data field is missing."""
        self.mock_scm.get.return_value = {"wrong_field": "value"}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Texas")
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500

    def test_list_response_invalid_data_field_type(self):
        """Test that InvalidObjectError is raised when data field is not a list."""
        self.mock_scm.get.return_value = {"data": "not a list"}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Texas")
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500

    def test_list_http_error_no_content(self):
        """Test handling of HTTPError without content."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500
        self.mock_scm.get.side_effect = HTTPError(response=mock_response)
        with pytest.raises(HTTPError):
            self.client.list(folder="Texas")

    def test_list_exact_match(self):
        """Test that exact_match filters objects correctly."""
        mock_response = {
            "data": [
                TacacsServerProfileResponseFactory(name="p_texas", folder="Texas").model_dump(),
                TacacsServerProfileResponseFactory(name="p_all", folder="All").model_dump(),
            ]
        }
        self.mock_scm.get.return_value = mock_response
        filtered = self.client.list(folder="Texas", exact_match=True)
        assert len(filtered) == 1
        assert filtered[0].folder == "Texas"

    def test_list_exclude_folders(self):
        """Test that exclude_folders removes objects from specified folders."""
        mock_response = {
            "data": [
                TacacsServerProfileResponseFactory(name="p_texas", folder="Texas").model_dump(),
                TacacsServerProfileResponseFactory(name="p_all", folder="All").model_dump(),
            ]
        }
        self.mock_scm.get.return_value = mock_response
        filtered = self.client.list(folder="Texas", exclude_folders=["All"])
        assert len(filtered) == 1
        assert all(a.folder != "All" for a in filtered)

    def test_list_exclude_snippets(self):
        """Test that exclude_snippets removes objects with specified snippets."""
        mock_response = {
            "data": [
                TacacsServerProfileResponseFactory(
                    name="p1", folder="Texas", snippet="default"
                ).model_dump(),
                TacacsServerProfileResponseFactory(
                    name="p2", folder="Texas", snippet="special"
                ).model_dump(),
            ]
        }
        self.mock_scm.get.return_value = mock_response
        filtered = self.client.list(folder="Texas", exclude_snippets=["default"])
        assert len(filtered) == 1

    def test_list_exclude_devices(self):
        """Test that exclude_devices removes objects with specified devices."""
        mock_response = {
            "data": [
                TacacsServerProfileResponseFactory(
                    name="p1", folder="Texas", device="DeviceA"
                ).model_dump(),
                TacacsServerProfileResponseFactory(
                    name="p2", folder="Texas", device="DeviceB"
                ).model_dump(),
            ]
        }
        self.mock_scm.get.return_value = mock_response
        filtered = self.client.list(folder="Texas", exclude_devices=["DeviceA"])
        assert len(filtered) == 1

    def test_list_pagination_multiple_pages(self):
        """Test that pagination aggregates data from multiple pages."""
        client = TacacsServerProfile(self.mock_scm, max_limit=2500)
        first_page = [
            TacacsServerProfileResponseFactory(name=f"p1-{i}", folder="Texas").model_dump()
            for i in range(2500)
        ]
        second_page = [
            TacacsServerProfileResponseFactory(name=f"p2-{i}", folder="Texas").model_dump()
            for i in range(2500)
        ]
        mock_responses = [{"data": first_page}, {"data": second_page}, {"data": []}]
        self.mock_scm.get.side_effect = mock_responses
        results = client.list(folder="Texas")
        assert len(results) == 5000
        assert self.mock_scm.get.call_count == 3


class TestTacacsServerProfileCreate(TestTacacsServerProfileBase):
    """Tests for creating TACACS+ Server Profile objects."""

    def test_create_valid_object(self):
        """Test creating an object with valid data."""
        test_object = TacacsServerProfileCreateApiFactory.build()
        mock_response = TacacsServerProfileResponseFactory.from_request(test_object)
        self.mock_scm.post.return_value = mock_response.model_dump()
        created_object = self.client.create(test_object.model_dump())
        self.mock_scm.post.assert_called_once_with(
            "/config/identity/v1/tacacs-server-profiles",
            json=test_object.model_dump(),
        )
        assert isinstance(created_object, TacacsServerProfileResponseModel)
        assert created_object.name == test_object.name

    def test_create_http_error_no_content(self):
        """Test creation with HTTPError without content."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500
        self.mock_scm.post.side_effect = HTTPError(response=mock_response)
        with pytest.raises(HTTPError):
            self.client.create({"name": "test", "folder": "Texas"})

    def test_create_http_error_with_response(self):
        """Test that HTTPError with response content triggers proper error handling."""
        self.mock_scm.post.side_effect = raise_mock_http_error(
            status_code=400,
            error_code="API_I00013",
            message="Create failed",
            error_type="Malformed Command",
        )
        with pytest.raises(HTTPError) as exc_info:
            self.client.create({"name": "test", "folder": "Texas", "server": []})
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Create failed"

    def test_create_generic_exception_handling(self):
        """Test handling of a generic exception during create."""
        self.mock_scm.post.side_effect = Exception("Generic error")
        with pytest.raises(Exception) as exc_info:
            self.client.create({"name": "test", "folder": "Texas"})
        assert str(exc_info.value) == "Generic error"


class TestTacacsServerProfileGet(TestTacacsServerProfileBase):
    """Tests for retrieving a specific TACACS+ Server Profile object."""

    def test_get_valid_object(self):
        """Test retrieving a specific object."""
        mock_response = TacacsServerProfileResponseFactory.build()
        self.mock_scm.get.return_value = mock_response.model_dump()
        retrieved_object = self.client.get(str(mock_response.id))
        self.mock_scm.get.assert_called_once_with(
            f"/config/identity/v1/tacacs-server-profiles/{mock_response.id}"
        )
        assert isinstance(retrieved_object, TacacsServerProfileResponseModel)
        assert retrieved_object.name == mock_response.name

    def test_get_object_not_present_error(self):
        """Test error handling when object is not present."""
        self.mock_scm.get.side_effect = raise_mock_http_error(
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
        self.mock_scm.get.side_effect = Exception("Generic error")
        with pytest.raises(Exception) as exc_info:
            self.client.get("123e4567-e89b-12d3-a456-426655440000")
        assert str(exc_info.value) == "Generic error"

    def test_get_http_error_no_response_content(self):
        """Test get method when HTTP error has no response content."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500
        self.mock_scm.get.side_effect = HTTPError(response=mock_response)
        with pytest.raises(HTTPError):
            self.client.get("123e4567-e89b-12d3-a456-426655440000")

    def test_get_server_error(self):
        """Test handling of server errors during get method."""
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )
        with pytest.raises(HTTPError) as exc_info:
            self.client.get("123e4567-e89b-12d3-a456-426655440000")
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "An internal error occurred"


class TestTacacsServerProfileUpdate(TestTacacsServerProfileBase):
    """Tests for updating TACACS+ Server Profile objects."""

    def test_update_valid_object(self):
        """Test updating an object with valid data."""
        update_data = TacacsServerProfileUpdateApiFactory(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="updated-profile",
        )
        mock_response = TacacsServerProfileResponseFactory.from_request(update_data)
        self.mock_scm.put.return_value = mock_response.model_dump()
        updated_object = self.client.update(update_data)
        self.mock_scm.put.assert_called_once()
        call_args = self.mock_scm.put.call_args
        assert call_args[0][0] == f"/config/identity/v1/tacacs-server-profiles/{update_data.id}"
        assert isinstance(updated_object, TacacsServerProfileResponseModel)

    def test_update_malformed_command_error(self):
        """Test error handling when update fails due to malformed command."""
        update_data = TacacsServerProfileUpdateApiFactory(
            id="123e4567-e89b-12d3-a456-426655440000", name="test"
        )
        self.mock_scm.put.side_effect = raise_mock_http_error(
            status_code=400,
            error_code="API_I00013",
            message="Update failed",
            error_type="Malformed Command",
        )
        with pytest.raises(HTTPError) as exc_info:
            self.client.update(update_data)
        assert exc_info.value.response.json()["_errors"][0]["message"] == "Update failed"

    def test_update_object_not_present_error(self):
        """Test error handling when the object to update is not present."""
        update_data = TacacsServerProfileUpdateApiFactory(
            id="123e4567-e89b-12d3-a456-426655440000", name="test"
        )
        self.mock_scm.put.side_effect = raise_mock_http_error(
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )
        with pytest.raises(HTTPError) as exc_info:
            self.client.update(update_data)
        assert exc_info.value.response.json()["_errors"][0]["message"] == "Object not found"

    def test_update_http_error_no_response_content(self):
        """Test update method when HTTP error has no response content."""
        update_data = TacacsServerProfileUpdateApiFactory(
            id="123e4567-e89b-12d3-a456-426655440000", name="test"
        )
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500
        self.mock_scm.put.side_effect = HTTPError(response=mock_response)
        with pytest.raises(HTTPError):
            self.client.update(update_data)

    def test_update_generic_exception_handling(self):
        """Test handling of a generic exception during update."""
        update_data = TacacsServerProfileUpdateApiFactory(
            id="123e4567-e89b-12d3-a456-426655440000", name="test"
        )
        self.mock_scm.put.side_effect = Exception("Generic error")
        with pytest.raises(Exception) as exc_info:
            self.client.update(update_data)
        assert str(exc_info.value) == "Generic error"

    def test_update_server_error(self):
        """Test handling of server errors during update."""
        update_data = TacacsServerProfileUpdateApiFactory(
            id="123e4567-e89b-12d3-a456-426655440000", name="test"
        )
        self.mock_scm.put.side_effect = raise_mock_http_error(
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )
        with pytest.raises(HTTPError) as exc_info:
            self.client.update(update_data)
        assert (
            exc_info.value.response.json()["_errors"][0]["message"] == "An internal error occurred"
        )


class TestTacacsServerProfileDelete(TestTacacsServerProfileBase):
    """Tests for deleting TACACS+ Server Profile objects."""

    def test_delete_success(self):
        """Test successful deletion of an object."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"
        self.mock_scm.delete.return_value = None
        self.client.delete(object_id)
        self.mock_scm.delete.assert_called_once_with(
            f"/config/identity/v1/tacacs-server-profiles/{object_id}"
        )

    def test_delete_referenced_object(self):
        """Test deleting an object that is referenced."""
        self.mock_scm.delete.side_effect = raise_mock_http_error(
            status_code=409,
            error_code="E009",
            message="Reference not zero",
            error_type="Reference Not Zero",
        )
        with pytest.raises(HTTPError) as exc_info:
            self.client.delete("123e4567-e89b-12d3-a456-426655440000")
        assert exc_info.value.response.json()["_errors"][0]["message"] == "Reference not zero"

    def test_delete_object_not_present_error(self):
        """Test error handling when the object to delete is not present."""
        self.mock_scm.delete.side_effect = raise_mock_http_error(
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )
        with pytest.raises(HTTPError) as exc_info:
            self.client.delete("123e4567-e89b-12d3-a456-426655440000")
        assert exc_info.value.response.json()["_errors"][0]["message"] == "Object not found"

    def test_delete_http_error_no_response_content(self):
        """Test delete method when HTTP error has no response content."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500
        self.mock_scm.delete.side_effect = HTTPError(response=mock_response)
        with pytest.raises(HTTPError):
            self.client.delete("123e4567-e89b-12d3-a456-426655440000")

    def test_delete_generic_exception_handling(self):
        """Test handling of a generic exception during delete."""
        self.mock_scm.delete.side_effect = Exception("Generic error")
        with pytest.raises(Exception) as exc_info:
            self.client.delete("abcdefg")
        assert str(exc_info.value) == "Generic error"

    def test_delete_server_error(self):
        """Test handling of server errors during delete."""
        self.mock_scm.delete.side_effect = raise_mock_http_error(
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )
        with pytest.raises(HTTPError) as exc_info:
            self.client.delete("123e4567-e89b-12d3-a456-426655440000")
        assert (
            exc_info.value.response.json()["_errors"][0]["message"] == "An internal error occurred"
        )


class TestTacacsServerProfileFetch(TestTacacsServerProfileBase):
    """Tests for fetching TACACS+ Server Profile objects by name."""

    def test_fetch_valid_object(self):
        """Test retrieving an object by its name using the fetch method."""
        mock_response_model = TacacsServerProfileResponseFactory.build()
        self.mock_scm.get.return_value = mock_response_model.model_dump()
        fetched_object = self.client.fetch(
            name=mock_response_model.name, folder=mock_response_model.folder
        )
        self.mock_scm.get.assert_called_once_with(
            "/config/identity/v1/tacacs-server-profiles",
            params={"folder": mock_response_model.folder, "name": mock_response_model.name},
        )
        assert isinstance(fetched_object, TacacsServerProfileResponseModel)
        assert str(fetched_object.id) == str(mock_response_model.id)

    def test_fetch_empty_name_error(self):
        """Test fetching with an empty name parameter."""
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="", folder="Texas")
        assert '"name" is not allowed to be empty' in str(exc_info.value)

    def test_fetch_empty_container_error(self):
        """Test fetching with an empty folder parameter."""
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="test", folder="")
        assert '"folder" is not allowed to be empty' in str(exc_info.value)

    def test_fetch_no_container_provided_error(self):
        """Test that InvalidObjectError is raised when no container is provided."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-profile")
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 400

    def test_fetch_multiple_containers_provided_error(self):
        """Test that InvalidObjectError is raised with multiple containers."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test", folder="Texas", snippet="TestSnippet")
        assert exc_info.value.error_code == "E003"

    def test_fetch_missing_id_field_error(self):
        """Test that InvalidObjectError is raised when response is missing id field."""
        self.mock_scm.get.return_value = {"name": "test", "folder": "Texas"}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test", folder="Texas")
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500

    def test_fetch_invalid_response_type_error(self):
        """Test that InvalidObjectError is raised when response is not a dictionary."""
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test123", folder="Texas")
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500

    def test_fetch_http_error_no_response_content(self):
        """Test that HTTPError without response content re-raises the exception."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500
        self.mock_scm.get.side_effect = HTTPError(response=mock_response)
        with pytest.raises(HTTPError):
            self.client.fetch(name="test", folder="Texas")

    def test_fetch_server_error(self):
        """Test handling of server errors during fetch."""
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )
        with pytest.raises(HTTPError) as exc_info:
            self.client.fetch(name="test", folder="Texas")
        assert (
            exc_info.value.response.json()["_errors"][0]["message"] == "An internal error occurred"
        )

    def test_fetch_generic_exception_handling(self):
        """Test generic exception handling during fetch."""
        self.mock_scm.get.side_effect = Exception("Generic error")
        with pytest.raises(Exception) as exc_info:
            self.client.fetch(name="test", folder="Texas")
        assert str(exc_info.value) == "Generic error"
