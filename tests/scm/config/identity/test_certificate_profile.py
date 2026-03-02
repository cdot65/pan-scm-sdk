# tests/scm/config/identity/test_certificate_profile.py

"""Tests for certificate profile identity configuration."""

from unittest.mock import MagicMock
import pytest
from requests.exceptions import HTTPError

from scm.config.identity import CertificateProfile
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.identity.certificate_profiles import CertificateProfileResponseModel
from tests.factories.identity.certificate_profile import (
    CertificateProfileCreateApiFactory,
    CertificateProfileResponseFactory,
    CertificateProfileUpdateApiFactory,
)
from tests.utils import raise_mock_http_error


@pytest.mark.usefixtures("load_env")
class TestCertificateProfileBase:
    """Base class for Certificate Profile tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = CertificateProfile(self.mock_scm, max_limit=5000)


class TestCertificateProfileMaxLimit(TestCertificateProfileBase):
    """Tests for Certificate Profile max_limit functionality."""

    def test_default_max_limit(self):
        """Test that default max_limit is set correctly."""
        client = CertificateProfile(self.mock_scm)
        assert client.max_limit == CertificateProfile.DEFAULT_MAX_LIMIT
        assert client.max_limit == 2500

    def test_custom_max_limit(self):
        """Test setting a custom max_limit."""
        client = CertificateProfile(self.mock_scm, max_limit=1000)
        assert client.max_limit == 1000

    def test_max_limit_setter(self):
        """Test the max_limit property setter."""
        client = CertificateProfile(self.mock_scm)
        client.max_limit = 3000
        assert client.max_limit == 3000

    def test_invalid_max_limit_type(self):
        """Test that invalid max_limit type raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            CertificateProfile(self.mock_scm, max_limit="invalid")
        assert "{'error': 'Invalid max_limit type'} - HTTP error: 400 - API error: E003" in str(
            exc_info.value
        )

    def test_max_limit_too_low(self):
        """Test that max_limit below 1 raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            CertificateProfile(self.mock_scm, max_limit=0)
        assert "{'error': 'Invalid max_limit value'} - HTTP error: 400 - API error: E003" in str(
            exc_info.value
        )

    def test_max_limit_too_high(self):
        """Test that max_limit above ABSOLUTE_MAX_LIMIT raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            CertificateProfile(self.mock_scm, max_limit=6000)
        assert "max_limit exceeds maximum allowed value" in str(exc_info.value)


class TestCertificateProfileList(TestCertificateProfileBase):
    """Tests for listing Certificate Profile objects."""

    def test_list_valid(self):
        """Test listing all objects successfully."""
        mock_response = {
            "data": [
                CertificateProfileResponseFactory(name="profile1", folder="Texas").model_dump(),
                CertificateProfileResponseFactory(name="profile2", folder="Texas").model_dump(),
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }
        self.mock_scm.get.return_value = mock_response
        existing_objects = self.client.list(folder="Texas")
        self.mock_scm.get.assert_called_once_with(
            "/config/identity/v1/certificate-profiles",
            params={"limit": 5000, "folder": "Texas", "offset": 0},
        )
        assert len(existing_objects) == 2
        assert isinstance(existing_objects[0], CertificateProfileResponseModel)

    def test_list_folder_empty_error(self):
        """Test that an empty folder raises appropriate error."""
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=400,
            error_code="E003",
            message='"folder" is not allowed to be empty',
            error_type="Missing Query Parameter",
        )
        with pytest.raises(MissingQueryParameterError):
            self.client.list(folder="")

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
        with pytest.raises(InvalidObjectError):
            self.client.list()

    def test_list_container_multiple_error(self):
        """Test that InvalidObjectError is raised with multiple containers."""
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=400,
            error_code="E003",
            message="Multiple container types provided",
            error_type="Invalid Object",
        )
        with pytest.raises(InvalidObjectError):
            self.client.list(folder="folder1", snippet="snippet1")

    def test_list_response_invalid_format(self):
        """Test that InvalidObjectError is raised when response is not a dictionary."""
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Texas")
        assert exc_info.value.error_code == "E003"

    def test_list_response_invalid_data_field_missing(self):
        """Test that InvalidObjectError is raised when data field is missing."""
        self.mock_scm.get.return_value = {"wrong_field": "value"}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Texas")
        assert exc_info.value.error_code == "E003"

    def test_list_response_invalid_data_field_type(self):
        """Test that InvalidObjectError is raised when data field is not a list."""
        self.mock_scm.get.return_value = {"data": "not a list"}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Texas")
        assert exc_info.value.error_code == "E003"

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
                CertificateProfileResponseFactory(name="p_texas", folder="Texas").model_dump(),
                CertificateProfileResponseFactory(name="p_all", folder="All").model_dump(),
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
                CertificateProfileResponseFactory(name="p1", folder="Texas").model_dump(),
                CertificateProfileResponseFactory(name="p2", folder="All").model_dump(),
            ]
        }
        self.mock_scm.get.return_value = mock_response
        filtered = self.client.list(folder="Texas", exclude_folders=["All"])
        assert len(filtered) == 1

    def test_list_exclude_snippets(self):
        """Test that exclude_snippets removes objects from specified snippets."""
        mock_response = {
            "data": [
                CertificateProfileResponseFactory(name="p1", folder="Texas").model_dump(),
                CertificateProfileResponseFactory.with_snippet(
                    name="p2", snippet="default"
                ).model_dump(),
            ]
        }
        self.mock_scm.get.return_value = mock_response
        filtered = self.client.list(folder="Texas", exclude_snippets=["default"])
        assert len(filtered) == 1
        assert filtered[0].name == "p1"

    def test_list_exclude_devices(self):
        """Test that exclude_devices removes objects from specified devices."""
        mock_response = {
            "data": [
                CertificateProfileResponseFactory(name="p1", folder="Texas").model_dump(),
                CertificateProfileResponseFactory.with_device(
                    name="p2", device="DeviceA"
                ).model_dump(),
            ]
        }
        self.mock_scm.get.return_value = mock_response
        filtered = self.client.list(folder="Texas", exclude_devices=["DeviceA"])
        assert len(filtered) == 1
        assert filtered[0].name == "p1"

    def test_list_pagination_multiple_pages(self):
        """Test that pagination aggregates data from multiple pages."""
        client = CertificateProfile(self.mock_scm, max_limit=2500)
        first_page = [
            CertificateProfileResponseFactory(name=f"p1-{i}", folder="Texas").model_dump()
            for i in range(2500)
        ]
        second_page = [
            CertificateProfileResponseFactory(name=f"p2-{i}", folder="Texas").model_dump()
            for i in range(2500)
        ]
        self.mock_scm.get.side_effect = [{"data": first_page}, {"data": second_page}, {"data": []}]
        results = client.list(folder="Texas")
        assert len(results) == 5000


class TestCertificateProfileCreate(TestCertificateProfileBase):
    """Tests for creating Certificate Profile objects."""

    def test_create_valid_object(self):
        """Test creating an object with valid data."""
        test_object = CertificateProfileCreateApiFactory.build()
        mock_response = CertificateProfileResponseFactory.from_request(test_object)
        self.mock_scm.post.return_value = mock_response.model_dump()
        created_object = self.client.create(test_object.model_dump())
        self.mock_scm.post.assert_called_once_with(
            "/config/identity/v1/certificate-profiles", json=test_object.model_dump()
        )
        assert isinstance(created_object, CertificateProfileResponseModel)
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
            self.client.create({"name": "test", "folder": "Texas"})
        assert exc_info.value.response.json()["_errors"][0]["message"] == "Create failed"

    def test_create_generic_exception_handling(self):
        """Test handling of a generic exception during create."""
        self.mock_scm.post.side_effect = Exception("Generic error")
        with pytest.raises(Exception) as exc_info:
            self.client.create({"name": "test", "folder": "Texas"})
        assert str(exc_info.value) == "Generic error"


class TestCertificateProfileGet(TestCertificateProfileBase):
    """Tests for retrieving Certificate Profile objects."""

    def test_get_valid_object(self):
        """Test retrieving a specific object."""
        mock_response = CertificateProfileResponseFactory.build()
        self.mock_scm.get.return_value = mock_response.model_dump()
        retrieved_object = self.client.get(str(mock_response.id))
        self.mock_scm.get.assert_called_once_with(
            f"/config/identity/v1/certificate-profiles/{mock_response.id}"
        )
        assert isinstance(retrieved_object, CertificateProfileResponseModel)

    def test_get_object_not_present_error(self):
        """Test error handling when object is not present."""
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )
        with pytest.raises(HTTPError):
            self.client.get("123e4567-e89b-12d3-a456-426655440000")

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
        with pytest.raises(HTTPError):
            self.client.get("123e4567-e89b-12d3-a456-426655440000")


class TestCertificateProfileUpdate(TestCertificateProfileBase):
    """Tests for updating Certificate Profile objects."""

    def test_update_valid_object(self):
        """Test updating an object with valid data."""
        update_data = CertificateProfileUpdateApiFactory(
            id="123e4567-e89b-12d3-a456-426655440000", name="updated-profile"
        )
        mock_response = CertificateProfileResponseFactory.from_request(update_data)
        self.mock_scm.put.return_value = mock_response.model_dump()
        updated_object = self.client.update(update_data)
        self.mock_scm.put.assert_called_once()
        assert isinstance(updated_object, CertificateProfileResponseModel)

    def test_update_malformed_command_error(self):
        """Test error handling when update fails due to malformed command."""
        update_data = CertificateProfileUpdateApiFactory(
            id="123e4567-e89b-12d3-a456-426655440000", name="test"
        )
        self.mock_scm.put.side_effect = raise_mock_http_error(
            status_code=400,
            error_code="API_I00013",
            message="Update failed",
            error_type="Malformed Command",
        )
        with pytest.raises(HTTPError):
            self.client.update(update_data)

    def test_update_object_not_present_error(self):
        """Test error handling when the object to update is not present."""
        update_data = CertificateProfileUpdateApiFactory(
            id="123e4567-e89b-12d3-a456-426655440000", name="test"
        )
        self.mock_scm.put.side_effect = raise_mock_http_error(
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )
        with pytest.raises(HTTPError):
            self.client.update(update_data)

    def test_update_http_error_no_response_content(self):
        """Test update method when HTTP error has no response content."""
        update_data = CertificateProfileUpdateApiFactory(
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
        update_data = CertificateProfileUpdateApiFactory(
            id="123e4567-e89b-12d3-a456-426655440000", name="test"
        )
        self.mock_scm.put.side_effect = Exception("Generic error")
        with pytest.raises(Exception) as exc_info:
            self.client.update(update_data)
        assert str(exc_info.value) == "Generic error"

    def test_update_server_error(self):
        """Test handling of server errors during update."""
        update_data = CertificateProfileUpdateApiFactory(
            id="123e4567-e89b-12d3-a456-426655440000", name="test"
        )
        self.mock_scm.put.side_effect = raise_mock_http_error(
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )
        with pytest.raises(HTTPError):
            self.client.update(update_data)


class TestCertificateProfileDelete(TestCertificateProfileBase):
    """Tests for deleting Certificate Profile objects."""

    def test_delete_success(self):
        """Test successful deletion of an object."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"
        self.mock_scm.delete.return_value = None
        self.client.delete(object_id)
        self.mock_scm.delete.assert_called_once_with(
            f"/config/identity/v1/certificate-profiles/{object_id}"
        )

    def test_delete_referenced_object(self):
        """Test deleting an object that is referenced."""
        self.mock_scm.delete.side_effect = raise_mock_http_error(
            status_code=409,
            error_code="E009",
            message="Reference not zero",
            error_type="Reference Not Zero",
        )
        with pytest.raises(HTTPError):
            self.client.delete("123e4567-e89b-12d3-a456-426655440000")

    def test_delete_object_not_present_error(self):
        """Test error handling when the object to delete is not present."""
        self.mock_scm.delete.side_effect = raise_mock_http_error(
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )
        with pytest.raises(HTTPError):
            self.client.delete("123e4567-e89b-12d3-a456-426655440000")

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
        with pytest.raises(HTTPError):
            self.client.delete("123e4567-e89b-12d3-a456-426655440000")


class TestCertificateProfileFetch(TestCertificateProfileBase):
    """Tests for fetching Certificate Profile objects by name."""

    def test_fetch_valid_object(self):
        """Test retrieving an object by its name using the fetch method."""
        mock_response_model = CertificateProfileResponseFactory.build()
        self.mock_scm.get.return_value = mock_response_model.model_dump()
        fetched_object = self.client.fetch(
            name=mock_response_model.name, folder=mock_response_model.folder
        )
        self.mock_scm.get.assert_called_once_with(
            "/config/identity/v1/certificate-profiles",
            params={"folder": mock_response_model.folder, "name": mock_response_model.name},
        )
        assert isinstance(fetched_object, CertificateProfileResponseModel)

    def test_fetch_empty_name_error(self):
        """Test fetching with an empty name parameter."""
        with pytest.raises(MissingQueryParameterError):
            self.client.fetch(name="", folder="Texas")

    def test_fetch_empty_container_error(self):
        """Test fetching with an empty folder parameter."""
        with pytest.raises(MissingQueryParameterError):
            self.client.fetch(name="test", folder="")

    def test_fetch_no_container_provided_error(self):
        """Test that InvalidObjectError is raised when no container is provided."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-profile")
        assert exc_info.value.error_code == "E003"

    def test_fetch_multiple_containers_provided_error(self):
        """Test that InvalidObjectError is raised with multiple containers."""
        with pytest.raises(InvalidObjectError):
            self.client.fetch(name="test", folder="Texas", snippet="TestSnippet")

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
        with pytest.raises(HTTPError):
            self.client.fetch(name="test", folder="Texas")

    def test_fetch_generic_exception_handling(self):
        """Test generic exception handling during fetch."""
        self.mock_scm.get.side_effect = Exception("Generic error")
        with pytest.raises(Exception) as exc_info:
            self.client.fetch(name="test", folder="Texas")
        assert str(exc_info.value) == "Generic error"
