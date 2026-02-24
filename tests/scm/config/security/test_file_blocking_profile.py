# tests/scm/config/security/test_file_blocking_profile.py

"""Tests for file blocking profile service."""

# Standard library imports
from unittest.mock import MagicMock

# External libraries
import pytest
from requests.exceptions import HTTPError

# Local SDK imports
from scm.config.security.file_blocking_profile import FileBlockingProfile
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.security.file_blocking_profiles import (
    FileBlockingProfileResponseModel,
)
from tests.factories.security.file_blocking_profile import (
    FileBlockingProfileCreateApiFactory,
    FileBlockingProfileResponseFactory,
    FileBlockingProfileUpdateApiFactory,
    FileBlockingRuleDictFactory,
)
from tests.utils import raise_mock_http_error


@pytest.mark.usefixtures("load_env")
class TestFileBlockingProfileBase:
    """Base class for File Blocking Profile tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = FileBlockingProfile(self.mock_scm)


# -------------------- Test Max Limit --------------------


class TestFileBlockingProfileMaxLimit(TestFileBlockingProfileBase):
    """Tests for max_limit validation in FileBlockingProfile."""

    def test_default_max_limit(self):
        """Test that default max_limit is set correctly."""
        client = FileBlockingProfile(self.mock_scm)
        assert client.max_limit == FileBlockingProfile.DEFAULT_MAX_LIMIT

    def test_custom_max_limit(self):
        """Test that a custom max_limit is set correctly."""
        client = FileBlockingProfile(self.mock_scm, max_limit=1000)
        assert client.max_limit == 1000

    def test_max_limit_setter(self):
        """Test setting max_limit using the setter."""
        client = FileBlockingProfile(self.mock_scm)
        client.max_limit = 3000
        assert client.max_limit == 3000

    def test_max_limit_too_low(self):
        """Test validation when max_limit is below 1."""
        with pytest.raises(InvalidObjectError):
            FileBlockingProfile(self.mock_scm, max_limit=0)

    def test_max_limit_too_high(self):
        """Test validation when max_limit exceeds absolute maximum."""
        with pytest.raises(InvalidObjectError):
            FileBlockingProfile(self.mock_scm, max_limit=10000)

    def test_max_limit_invalid_type(self):
        """Test validation when max_limit is not an integer."""
        with pytest.raises(InvalidObjectError):
            FileBlockingProfile(self.mock_scm, max_limit="invalid")


# -------------------- Test List --------------------


class TestFileBlockingProfileList(TestFileBlockingProfileBase):
    """Tests for listing File Blocking Profile objects."""

    def test_list_valid(self):
        """Test listing all objects with valid response."""
        mock_response = {
            "data": [
                FileBlockingProfileResponseFactory(
                    name="profile1",
                    folder="Texas",
                ).model_dump(),
                FileBlockingProfileResponseFactory(
                    name="profile2",
                    folder="Texas",
                ).model_dump(),
            ],
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        existing_objects = self.client.list(folder="Texas")
        assert len(existing_objects) == 2
        assert isinstance(existing_objects[0], FileBlockingProfileResponseModel)
        assert existing_objects[0].name == "profile1"

    def test_list_folder_empty_error(self):
        """Test that empty folder raises MissingQueryParameterError."""
        with pytest.raises(MissingQueryParameterError):
            self.client.list(folder="")

    def test_list_no_container_error(self):
        """Test that no container raises InvalidObjectError."""
        with pytest.raises(InvalidObjectError):
            self.client.list()

    def test_list_multiple_containers_error(self):
        """Test that multiple containers raise InvalidObjectError."""
        with pytest.raises(InvalidObjectError):
            self.client.list(folder="Texas", snippet="TestSnippet")

    def test_list_filters_rules_validation(self):
        """Test validation of filter specific fields."""
        mock_rules = []

        # Test with string instead of list
        invalid_filters = {"rules": "rules"}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_rules, invalid_filters)

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)

        # Test with dict instead of list
        invalid_filters = {"rules": {"value": "rules"}}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_rules, invalid_filters)

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)

    def test_list_response_invalid_format(self):
        """Test that InvalidObjectError is raised when the response is not a dictionary."""
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Texas")

        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500
        assert "HTTP error: 500 - API error: E003" in str(exc_info.value)

    def test_list_response_invalid_data_field_missing(self):
        """Test that InvalidObjectError is raised when API returns response with missing data field."""
        self.mock_scm.get.return_value = {"wrong_field": "value"}  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Texas")

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        assert error.error_code == "E003"
        assert error.http_status_code == 500
        assert "HTTP error: 500 - API error: E003" in str(error)

    def test_list_response_invalid_data_field_type(self):
        """Test that InvalidObjectError is raised when API returns non-list data field."""
        self.mock_scm.get.return_value = {"data": "not a list"}  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Texas")

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
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

    # -------------------- Tests for exact_match and Exclusions --------------------

    def test_list_exact_match(self):
        """Test that exact_match=True returns only objects that match the container exactly."""
        mock_response = {
            "data": [
                FileBlockingProfileResponseFactory(
                    name="profile_in_texas",
                    folder="Texas",
                ).model_dump(),
                FileBlockingProfileResponseFactory(
                    name="profile_in_all",
                    folder="All",
                ).model_dump(),
            ]
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        filtered = self.client.list(folder="Texas", exact_match=True)
        assert len(filtered) == 1
        assert filtered[0].folder == "Texas"
        assert filtered[0].name == "profile_in_texas"

    def test_list_exclude_folders(self):
        """Test that exclude_folders removes objects from those folders."""
        mock_response = {
            "data": [
                FileBlockingProfileResponseFactory(
                    name="profile_in_texas",
                    folder="Texas",
                ).model_dump(),
                FileBlockingProfileResponseFactory(
                    name="profile_in_all",
                    folder="All",
                ).model_dump(),
            ]
        }
        self.mock_scm.get.return_value = mock_response

        filtered = self.client.list(folder="Texas", exclude_folders=["All"])
        assert len(filtered) == 1
        assert all(a.folder != "All" for a in filtered)

    def test_list_exclude_snippets(self):
        """Test that exclude_snippets removes objects with those snippets."""
        mock_response = {
            "data": [
                FileBlockingProfileResponseFactory(
                    name="profile_with_default_snippet",
                    folder="Texas",
                    snippet="default",
                ).model_dump(),
                FileBlockingProfileResponseFactory(
                    name="profile_with_special_snippet",
                    folder="Texas",
                    snippet="special",
                ).model_dump(),
            ]
        }
        self.mock_scm.get.return_value = mock_response

        filtered = self.client.list(folder="Texas", exclude_snippets=["default"])
        assert len(filtered) == 1
        assert all(a.snippet != "default" for a in filtered)

    def test_list_exclude_devices(self):
        """Test that exclude_devices removes objects with those devices."""
        mock_response = {
            "data": [
                FileBlockingProfileResponseFactory(
                    name="profile_with_device_a",
                    folder="Texas",
                    snippet="default",
                    device="DeviceA",
                ).model_dump(),
                FileBlockingProfileResponseFactory(
                    name="profile_with_device_b",
                    folder="Texas",
                    snippet="special",
                    device="DeviceB",
                ).model_dump(),
            ]
        }
        self.mock_scm.get.return_value = mock_response

        filtered = self.client.list(folder="Texas", exclude_devices=["DeviceA"])
        assert len(filtered) == 1
        assert all(a.device != "DeviceA" for a in filtered)

    def test_list_exact_match_and_exclusions(self):
        """Test combining exact_match with exclusions."""
        mock_response = {
            "data": [
                FileBlockingProfileResponseFactory(
                    name="profile_with_default_snippet",
                    folder="Texas",
                    snippet="default",
                ).model_dump(),
                FileBlockingProfileResponseFactory(
                    name="profile_with_special_snippet",
                    folder="Texas",
                    snippet="special",
                ).model_dump(),
            ]
        }
        self.mock_scm.get.return_value = mock_response

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
        assert obj.device != "DeviceA"

    def test_list_pagination_multiple_pages(self):
        """Test that the list method correctly aggregates data from multiple pages."""
        client = FileBlockingProfile(self.mock_scm, max_limit=2500)  # noqa

        first_page = [
            FileBlockingProfileResponseFactory(
                name=f"profile-page1-{i}",
                folder="Texas",
                rules=[],
            ).model_dump()
            for i in range(2500)
        ]

        second_page = [
            FileBlockingProfileResponseFactory(
                name=f"profile-page2-{i}",
                folder="Texas",
                rules=[],
            ).model_dump()
            for i in range(2500)
        ]

        third_page = [
            FileBlockingProfileResponseFactory(
                name=f"profile-page3-{i}",
                folder="Texas",
                rules=[],
            ).model_dump()
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
        assert isinstance(results[0], FileBlockingProfileResponseModel)
        assert all(isinstance(obj, FileBlockingProfileResponseModel) for obj in results)

        assert self.mock_scm.get.call_count == 4  # noqa

        self.mock_scm.get.assert_any_call(  # noqa
            "/config/security/v1/file-blocking-profiles",
            params={
                "folder": "Texas",
                "limit": 2500,
                "offset": 0,
            },
        )

        self.mock_scm.get.assert_any_call(  # noqa
            "/config/security/v1/file-blocking-profiles",
            params={
                "folder": "Texas",
                "limit": 2500,
                "offset": 2500,
            },
        )

        self.mock_scm.get.assert_any_call(  # noqa
            "/config/security/v1/file-blocking-profiles",
            params={
                "folder": "Texas",
                "limit": 2500,
                "offset": 5000,
            },
        )

        assert results[0].name == "profile-page1-0"
        assert results[2500].name == "profile-page2-0"
        assert results[5000].name == "profile-page3-0"


# -------------------- Test Create --------------------


class TestFileBlockingProfileCreate(TestFileBlockingProfileBase):
    """Tests for creating File Blocking Profile objects."""

    def test_create_valid_object(self):
        """Test creating an object with valid data."""
        test_object = FileBlockingProfileCreateApiFactory.build()
        mock_response = FileBlockingProfileResponseFactory.from_request(test_object)

        self.mock_scm.post.return_value = mock_response.model_dump()  # noqa
        created_object = self.client.create(test_object.model_dump())

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/security/v1/file-blocking-profiles",
            json=test_object.model_dump(),
        )
        assert isinstance(created_object, FileBlockingProfileResponseModel)
        assert created_object.name == test_object.name

    def test_create_http_error_no_content(self):
        """Test creation with HTTPError without content."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.post.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.create({"name": "test", "folder": "Texas"})

    def test_create_with_rules(self):
        """Test creating profile with specific rules configuration."""
        test_object = FileBlockingProfileCreateApiFactory.build(
            rules=[FileBlockingRuleDictFactory.build_valid()],
        )

        mock_response = FileBlockingProfileResponseFactory.from_request(test_object)
        self.mock_scm.post.return_value = mock_response.model_dump()  # noqa

        created_object = self.client.create(test_object.model_dump())

        assert isinstance(created_object, FileBlockingProfileResponseModel)
        assert len(created_object.rules) == 1

    def test_create_http_error_with_response(self):
        """Test that HTTPError with response content triggers proper error handling."""
        test_data = {
            "name": "test-profile",
            "folder": "Texas",
            "rules": [
                {
                    "name": "block-exe",
                    "action": "block",
                    "file_type": ["exe"],
                }
            ],
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
                    "name": "test-profile",
                    "folder": "Texas",
                }
            )
        assert str(exc_info.value) == "Generic error"


# -------------------- Test Get --------------------


class TestFileBlockingProfileGet(TestFileBlockingProfileBase):
    """Tests for retrieving a specific File Blocking Profile object."""

    def test_get_valid_object(self):
        """Test retrieving a specific object."""
        mock_response = FileBlockingProfileResponseFactory.build()

        self.mock_scm.get.return_value = mock_response.model_dump()  # noqa
        retrieved_object = self.client.get(str(mock_response.id))

        self.mock_scm.get.assert_called_once_with(  # noqa
            f"/config/security/v1/file-blocking-profiles/{mock_response.id}"
        )
        assert isinstance(retrieved_object, FileBlockingProfileResponseModel)
        assert retrieved_object.name == mock_response.name

    def test_get_object_not_present_error(self):
        """Test error handling when object is not present."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.list(folder="Texas")
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Object not found"
        assert error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"

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
        assert error_response["_errors"][0]["details"]["errorType"] == "Internal Error"


# -------------------- Test Update --------------------


class TestFileBlockingProfileUpdate(TestFileBlockingProfileBase):
    """Tests for updating File Blocking Profile objects."""

    def test_update_valid_object(self):
        """Test updating an object with valid data."""
        update_data = FileBlockingProfileUpdateApiFactory(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="updated-profile",
            description="Updated description",
            folder="Texas",
            rules=[],
        )

        mock_response = FileBlockingProfileResponseFactory.from_request(update_data)
        self.mock_scm.put.return_value = mock_response.model_dump()  # noqa

        updated_object = self.client.update(update_data)

        self.mock_scm.put.assert_called_once()  # noqa

        call_args = self.mock_scm.put.call_args  # noqa

        assert call_args[0][0] == f"/config/security/v1/file-blocking-profiles/{update_data.id}"

        payload = call_args[1]["json"]
        assert payload["name"] == "updated-profile"

        assert isinstance(updated_object, FileBlockingProfileResponseModel)
        assert updated_object.id == mock_response.id
        assert updated_object.name == mock_response.name

    def test_update_malformed_command_error(self):
        """Test error handling when update fails due to malformed command."""
        update_data = FileBlockingProfileUpdateApiFactory(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-profile",
            folder="Texas",
            rules=[],
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
        assert error_response["_errors"][0]["details"]["errorType"] == "Malformed Command"

    def test_update_object_not_present_error(self):
        """Test error handling when the object to update is not present."""
        update_data = FileBlockingProfileUpdateApiFactory(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-profile",
            folder="Texas",
            rules=[],
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
        assert error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"

    def test_update_http_error_no_response_content(self):
        """Test update method when HTTP error has no response content."""
        update_data = FileBlockingProfileUpdateApiFactory(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-profile",
            folder="Texas",
            rules=[],
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
        update_data = FileBlockingProfileUpdateApiFactory(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-profile",
            folder="Texas",
            rules=[],
        )

        self.mock_scm.put.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.update(update_data)
        assert str(exc_info.value) == "Generic error"

    def test_update_server_error(self):
        """Test handling of server errors during update."""
        update_data = FileBlockingProfileUpdateApiFactory(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-profile",
            folder="Texas",
            rules=[],
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
        assert error_response["_errors"][0]["details"]["errorType"] == "Internal Error"


# -------------------- Test Delete --------------------


class TestFileBlockingProfileDelete(TestFileBlockingProfileBase):
    """Tests for deleting File Blocking Profile objects."""

    def test_delete_success(self):
        """Test successful deletion of an object."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.return_value = None  # noqa
        self.client.delete(object_id)

        self.mock_scm.delete.assert_called_once_with(  # noqa
            f"/config/security/v1/file-blocking-profiles/{object_id}"
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
        assert error_response["_errors"][0]["details"]["errorType"] == "Reference Not Zero"

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
        assert error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"

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
        assert error_response["_errors"][0]["details"]["errorType"] == "Internal Error"


# -------------------- Test Fetch --------------------


class TestFileBlockingProfileFetch(TestFileBlockingProfileBase):
    """Tests for fetching File Blocking Profile objects by name."""

    def test_fetch_valid_object(self):
        """Test retrieving an object by its name using the `fetch` method."""
        mock_response_model = FileBlockingProfileResponseFactory.build()
        mock_response_data = mock_response_model.model_dump()

        self.mock_scm.get.return_value = mock_response_data  # noqa

        fetched_object = self.client.fetch(
            name=mock_response_model.name,
            folder=mock_response_model.folder,
        )

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/security/v1/file-blocking-profiles",
            params={
                "folder": mock_response_model.folder,
                "name": mock_response_model.name,
            },
        )

        assert isinstance(fetched_object, FileBlockingProfileResponseModel)

        assert str(fetched_object.id) == str(mock_response_model.id)
        assert fetched_object.name == mock_response_model.name
        assert fetched_object.description == mock_response_model.description
        assert fetched_object.folder == mock_response_model.folder

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
        assert error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"

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
        """Test that InvalidObjectError is raised when no container parameter is provided."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-profile")

        error_msg = str(exc_info.value)
        assert "HTTP error: 400 - API error: E003" in error_msg

    def test_fetch_multiple_containers_provided_error(self):
        """Test that InvalidObjectError is raised when multiple container parameters are provided."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(
                name="test-profile",
                folder="Texas",
                snippet="TestSnippet",
            )

        error_msg = str(exc_info.value)
        assert "HTTP error: 400 - API error: E003" in error_msg

    def test_fetch_http_error_no_response_content(self):
        """Test that an HTTPError without response content in fetch() re-raises the exception."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.fetch(name="test-profile", folder="Texas")

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
        assert error_response["_errors"][0]["details"]["errorType"] == "Internal Error"

    def test_fetch_missing_id_field_error(self):
        """Test that InvalidObjectError is raised when the response is missing 'id' field."""
        mock_response = {
            "name": "test-profile",
            "folder": "Texas",
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-profile", folder="Texas")

        error_msg = str(exc_info.value)
        assert "HTTP error: 500 - API error: E003" in error_msg
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500

    def test_fetch_invalid_response_type_error(self):
        """Test that InvalidObjectError is raised when the response is not a dictionary."""
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test123", folder="Texas")

        error_msg = str(exc_info.value)
        assert "HTTP error: 500 - API error: E003" in error_msg
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500


# -------------------- End of Test Classes --------------------
