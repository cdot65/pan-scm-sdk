# tests/scm/config/objects/test_hip_profile.py

# Standard library imports
from unittest.mock import MagicMock

# External libraries
import pytest
from requests.exceptions import HTTPError

# Local SDK imports
from scm.config.objects import HIPProfile
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.objects import HIPProfileResponseModel
from tests.factories import (
    HIPProfileCreateApiFactory,
    HIPProfileResponseFactory,
    HIPProfileUpdateApiFactory,
)
from tests.utils import raise_mock_http_error


@pytest.mark.usefixtures("load_env")
class TestHIPProfileBase:
    """Base class for HIPProfile tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm  # noqa
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = HIPProfile(self.mock_scm, max_limit=5000)  # noqa


class TestHIPProfileMaxLimit(TestHIPProfileBase):
    """Tests for max_limit functionality in HIPProfile class."""

    def test_default_max_limit(self):
        """Test that default max_limit is set correctly."""
        client = HIPProfile(self.mock_scm)  # noqa
        assert client.max_limit == HIPProfile.DEFAULT_MAX_LIMIT
        assert client.max_limit == 2500

    def test_custom_max_limit(self):
        """Test setting a custom max_limit."""
        client = HIPProfile(self.mock_scm, max_limit=1000)  # noqa
        assert client.max_limit == 1000

    def test_max_limit_setter(self):
        """Test the max_limit property setter."""
        client = HIPProfile(self.mock_scm)  # noqa
        client.max_limit = 3000
        assert client.max_limit == 3000

    def test_invalid_max_limit_type(self):
        """Test that invalid max_limit type raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            HIPProfile(self.mock_scm, max_limit="invalid")  # noqa
        assert "{'error': 'Invalid max_limit type'} - HTTP error: 400 - API error: E003" in str(
            exc_info.value
        )

    def test_max_limit_too_low(self):
        """Test that max_limit below 1 raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            HIPProfile(self.mock_scm, max_limit=0)  # noqa
        assert "{'error': 'Invalid max_limit value'} - HTTP error: 400 - API error: E003" in str(
            exc_info.value
        )

    def test_max_limit_too_high(self):
        """Test that max_limit above ABSOLUTE_MAX_LIMIT raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            HIPProfile(self.mock_scm, max_limit=6000)  # noqa
        assert "max_limit exceeds maximum allowed value" in str(exc_info.value)


class TestHIPProfileList(TestHIPProfileBase):
    """Tests for listing HIP profiles."""

    def test_list_valid(self):
        """Test listing all HIP profiles successfully."""
        mock_response = {
            "data": [
                HIPProfileResponseFactory(
                    name="hip_profile1",
                    folder="Shared",
                    match="Any of the members of (hipobject1)",
                ).model_dump(),
                HIPProfileResponseFactory(
                    name="hip_profile2",
                    folder="Shared",
                    match="All of the members of (hipobject2)",
                ).model_dump(),
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        existing_objects = self.client.list(folder="Shared")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/hip-profiles",
            params={
                "folder": "Shared",
                "limit": 5000,
                "offset": 0,
            },
        )
        assert isinstance(existing_objects, list)
        assert isinstance(existing_objects[0], HIPProfileResponseModel)
        assert len(existing_objects) == 2
        assert existing_objects[0].name == "hip_profile1"

    def test_list_folder_empty_error(self):
        """Test that empty folder raises appropriate error."""
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.list(folder="")

        error_msg = str(exc_info.value)
        assert (
            "{'field': 'folder', 'error': '\"folder\" is not allowed to be empty'} - HTTP error: 400 - API error: E003"
            in error_msg
        )

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

    def test_list_no_container(self):
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=400,
            error_code="E003",
            message="Exactly one of 'folder', 'snippet', or 'device' must be provided.",
            error_type="Invalid Object",
        )
        with pytest.raises(InvalidObjectError):
            self.client.list()

    def test_list_multiple_containers(self):
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=400,
            error_code="E003",
            message="Multiple containers provided",
            error_type="Invalid Object",
        )
        with pytest.raises(InvalidObjectError):
            self.client.list(folder="FolderA", snippet="SnippetA")

    def test_list_response_invalid_format(self):
        """Test that InvalidObjectError is raised when the response is not a dictionary."""
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Shared")

        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500
        assert "HTTP error: 500 - API error: E003" in str(exc_info.value)

    def test_list_response_invalid_data_field_missing(self):
        """Test that InvalidObjectError is raised when API returns response with missing data field."""
        self.mock_scm.get.return_value = {"wrong_field": "value"}  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Shared")

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        assert error.error_code == "E003"
        assert error.http_status_code == 500
        assert "HTTP error: 500 - API error: E003" in str(exc_info.value)

    def test_list_response_invalid_data_field_type(self):
        """Test that InvalidObjectError is raised when API returns non-list data field."""
        self.mock_scm.get.return_value = {"data": "not a list"}  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Shared")

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
        self.mock_scm.get.side_effect = mock_http_error

        with pytest.raises(HTTPError):
            self.client.list(folder="Shared")

    def test_list_pagination(self):
        """Test list pagination when results exceed max_limit."""
        # Create mock responses for pagination
        page1 = {
            "data": [
                HIPProfileResponseFactory(
                    name=f"hip_profile{i}", folder="All", match="Any of the members of (hipobject1)"
                ).model_dump()
                for i in range(5000)  # max_limit worth of objects
            ],
            "offset": 0,
            "total": 7500,
            "limit": 5000,
        }

        page2 = {
            "data": [
                HIPProfileResponseFactory(
                    name=f"hip_profile{i}", folder="All", match="Any of the members of (hipobject1)"
                ).model_dump()
                for i in range(5000, 7500)  # Remaining 2500 objects
            ],
            "offset": 5000,
            "total": 7500,
            "limit": 5000,
        }

        self.mock_scm.get.side_effect = [page1, page2]

        objects = self.client.list(folder="All")

        assert len(objects) == 7500
        assert self.mock_scm.get.call_count == 2
        assert self.mock_scm.get.call_args_list[0][1]["params"]["offset"] == 0
        assert self.mock_scm.get.call_args_list[1][1]["params"]["offset"] == 5000

    def test_list_with_exact_match_filter(self):
        """Test filtering objects with exact container match."""
        mock_response = {
            "data": [
                HIPProfileResponseFactory(
                    name="hip1", folder="Exact", match="Any (hip1)"
                ).model_dump(),
                HIPProfileResponseFactory(
                    name="hip2", folder="Different", match="Any (hip2)"
                ).model_dump(),
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response
        objects = self.client.list(folder="Exact", exact_match=True)

        assert len(objects) == 1
        assert objects[0].name == "hip1"
        assert objects[0].folder == "Exact"

    def test_list_with_exclude_folders(self):
        """Test excluding objects from specific folders."""
        mock_response = {
            "data": [
                HIPProfileResponseFactory(
                    name="hip1", folder="Keep", match="Any (hip1)"
                ).model_dump(),
                HIPProfileResponseFactory(
                    name="hip2", folder="Exclude", match="Any (hip2)"
                ).model_dump(),
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response
        objects = self.client.list(folder="All", exclude_folders=["Exclude"])

        assert len(objects) == 1
        assert objects[0].name == "hip1"
        assert objects[0].folder == "Keep"

    def test_list_with_exclude_snippets(self):
        """Test excluding objects from specific snippets."""
        mock_response = {
            "data": [
                HIPProfileResponseFactory(
                    name="hip1", snippet="Keep", match="Any (hip1)"
                ).model_dump(),
                HIPProfileResponseFactory(
                    name="hip2", snippet="Exclude", match="Any (hip2)"
                ).model_dump(),
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response
        objects = self.client.list(folder="All", exclude_snippets=["Exclude"])

        assert len(objects) == 1
        assert objects[0].name == "hip1"
        assert objects[0].snippet == "Keep"

    def test_list_with_exclude_devices(self):
        """Test excluding objects from specific devices."""
        mock_response = {
            "data": [
                HIPProfileResponseFactory(
                    name="hip1", device="Keep", match="Any (hip1)"
                ).model_dump(),
                HIPProfileResponseFactory(
                    name="hip2", device="Exclude", match="Any (hip2)"
                ).model_dump(),
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response
        objects = self.client.list(folder="All", exclude_devices=["Exclude"])

        assert len(objects) == 1
        assert objects[0].name == "hip1"
        assert objects[0].device == "Keep"


class TestHIPProfileCreate(TestHIPProfileBase):
    """Tests for creating HIP profiles."""

    def test_create_valid_object(self):
        """Test creating an object with valid data."""
        test_object = HIPProfileCreateApiFactory.build()
        mock_response = HIPProfileResponseFactory.from_request(test_object)

        self.mock_scm.post.return_value = mock_response.model_dump()
        created_object = self.client.create(test_object.model_dump())

        self.mock_scm.post.assert_called_once_with(
            "/config/objects/v1/hip-profiles",
            json=test_object.model_dump(),
        )
        assert isinstance(created_object, HIPProfileResponseModel)
        assert created_object.name == test_object.name
        assert created_object.match == test_object.match

    def test_create_http_error_no_content(self):
        """Test creation with HTTPError without content."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.post.side_effect = mock_http_error

        with pytest.raises(HTTPError):
            self.client.create(
                {
                    "name": "test",
                    "folder": "Shared",
                    "match": "Any of the members of (hipobject1)",
                }
            )

    def test_create_with_complex_match(self):
        """Test creating object with complex match expression."""
        test_object = HIPProfileCreateApiFactory.with_complex_match()
        mock_response = HIPProfileResponseFactory.from_request(test_object)
        self.mock_scm.post.return_value = mock_response.model_dump()

        created_object = self.client.create(test_object.model_dump())

        assert isinstance(created_object, HIPProfileResponseModel)
        assert created_object.match == test_object.match

    def test_create_http_error_with_response(self):
        """Test that HTTPError with response content triggers proper error handling."""
        test_data = {
            "name": "test-hip-profile",
            "folder": "Shared",
            "match": "Any of the members of (hipobject1)",
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
                    "name": "test",
                    "folder": "Shared",
                    "match": "Any of the members of (hipobject1)",
                }
            )
        assert str(exc_info.value) == "Generic error"

    def test_create_multiple_containers_error(self):
        """Test that ValueError is raised when multiple containers are provided."""
        with pytest.raises(ValueError) as exc_info:
            self.client.create(
                {
                    "name": "test-hip-profile",
                    "folder": "FolderA",
                    "snippet": "SnippetA",  # This should trigger the validation error
                    "match": "Any of the members of (hipobject1)",
                }
            )

        assert (
            "1 validation error for HIPProfileCreateModel\n  Value error, Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_create_no_container_error(self):
        """Test that ValueError is raised when no container is provided."""
        with pytest.raises(ValueError) as exc_info:
            self.client.create(
                {
                    "name": "test-hip-profile",
                    "match": "Any of the members of (hipobject1)",
                    # No container provided - should trigger validation error
                }
            )

        assert (
            "1 validation error for HIPProfileCreateModel\n  Value error, Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )


class TestHIPProfileGet(TestHIPProfileBase):
    """Tests for retrieving a specific HIP profile."""

    def test_get_valid_object(self):
        """Test retrieving a specific object."""
        mock_response = HIPProfileResponseFactory.build()

        self.mock_scm.get.return_value = mock_response.model_dump()
        retrieved_object = self.client.get(str(mock_response.id))

        self.mock_scm.get.assert_called_once_with(
            f"/config/objects/v1/hip-profiles/{mock_response.id}"
        )
        assert isinstance(retrieved_object, HIPProfileResponseModel)
        assert retrieved_object.name == mock_response.name
        assert retrieved_object.match == mock_response.match

    def test_get_object_not_present_error(self):
        """Test error handling when object is not present."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.get(object_id)

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


class TestHIPProfileUpdate(TestHIPProfileBase):
    """Tests for updating HIP profiles."""

    def test_update_valid_object(self):
        """Test updating an object with valid data."""
        update_data = HIPProfileUpdateApiFactory.with_updated_match(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="updated-hip-profile",
            description="Updated HIP profile",
        )

        mock_response = HIPProfileResponseFactory.from_request(update_data)
        self.mock_scm.put.return_value = mock_response.model_dump()  # noqa

        updated_object = self.client.update(update_data)

        # Exclude fields that are unset/None in the assertion
        expected_json = update_data.model_dump(exclude={"id"}, exclude_unset=True)

        self.mock_scm.put.assert_called_once_with(  # noqa
            f"/config/objects/v1/hip-profiles/{update_data.id}",
            json=expected_json,
        )

        assert isinstance(updated_object, HIPProfileResponseModel)
        assert updated_object.id == mock_response.id
        assert updated_object.name == mock_response.name
        assert updated_object.description == mock_response.description
        assert updated_object.match == mock_response.match

    def test_update_malformed_command_error(self):
        """Test error handling when update fails due to malformed command."""
        update_data = HIPProfileUpdateApiFactory(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-hip-profile",
            match="Any of the members of (hipobject1)",
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
        update_data = HIPProfileUpdateApiFactory(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-hip-profile",
            match="Any of the members of (hipobject1)",
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
        update_data = HIPProfileUpdateApiFactory(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-hip-profile",
            match="Any of the members of (hipobject1)",
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
        update_data = HIPProfileUpdateApiFactory(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-hip-profile",
            match="Any of the members of (hipobject1)",
        )

        self.mock_scm.put.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.update(update_data)
        assert str(exc_info.value) == "Generic error"

    def test_update_server_error(self):
        """Test handling of server errors during update."""
        update_data = HIPProfileUpdateApiFactory(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-hip-profile",
            match="Any of the members of (hipobject1)",
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

    def test_update_multiple_containers_error(self):
        """Test that providing multiple containers raises InvalidObjectError."""
        update_data = HIPProfileUpdateApiFactory(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-hip-profile",
            folder="Shared",
            snippet="test-snippet",
            match="Any of the members of (hipobject1)",
        )

        # Match the pattern used in test_list_multiple_containers
        self.mock_scm.put.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="E003",
            message="Multiple containers provided",
            error_type="Invalid Object",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.update(update_data)

        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Multiple containers provided"
        assert error_response["_errors"][0]["details"]["errorType"] == "Invalid Object"


class TestHIPProfileDelete(TestHIPProfileBase):
    """Tests for deleting HIP profiles."""

    def test_delete_success(self):
        """Test successful deletion of an object."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.return_value = None
        self.client.delete(object_id)

        self.mock_scm.delete.assert_called_once_with(f"/config/objects/v1/hip-profiles/{object_id}")

    def test_delete_referenced_object(self):
        """Test deleting an object that is referenced."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.side_effect = raise_mock_http_error(
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


class TestHIPProfileFetch(TestHIPProfileBase):
    """Tests for fetching HIP profiles by name."""

    def test_fetch_valid_object(self):
        """Test retrieving an object by its name using the `fetch` method."""
        mock_response_model = HIPProfileResponseFactory.build()
        mock_response_data = mock_response_model.model_dump()

        self.mock_scm.get.return_value = mock_response_data  # noqa

        fetched_object = self.client.fetch(
            name=mock_response_model.name,
            folder=mock_response_model.folder,
        )

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/hip-profiles",
            params={
                "folder": mock_response_model.folder,
                "name": mock_response_model.name,
            },
        )

        assert isinstance(fetched_object, HIPProfileResponseModel)
        assert fetched_object.id == mock_response_model.id
        assert fetched_object.name == mock_response_model.name
        assert fetched_object.match == mock_response_model.match

    def test_fetch_object_not_present_error(self):
        """Test fetching an object that does not exist."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.fetch(name="nonexistent", folder="Shared")

        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Object not found"
        assert error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"

    def test_fetch_empty_name_error(self):
        """Test fetching with an empty name parameter."""
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="", folder="Shared")

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

    def test_fetch_invalid_response_format_error(self):
        """Test fetching an object when the API returns an unexpected format."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="E003",
            message="Invalid response format",
            error_type="Invalid Object",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.fetch(name="test", folder="Shared")
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Invalid response format"
        assert error_response["_errors"][0]["details"]["errorType"] == "Invalid Object"

    def test_fetch_generic_exception_handling(self):
        """Test generic exception handling during fetch."""
        self.mock_scm.get.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.fetch(name="test", folder="Shared")

        assert str(exc_info.value) == "Generic error"

    def test_fetch_http_error_no_response_content(self):
        """Test that an HTTPError without response content in fetch() re-raises the exception."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500
        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.fetch(name="test-hip-profile", folder="Shared")

    def test_fetch_server_error(self):
        """Test handling of server errors during fetch."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.fetch(name="test", folder="Shared")
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "An internal error occurred"
        assert error_response["_errors"][0]["details"]["errorType"] == "Internal Error"

    def test_fetch_missing_id_field_error(self):
        """Test that InvalidObjectError is raised when the response is missing 'id' field."""
        mock_response = {
            "name": "test-hip-profile",
            "folder": "Shared",
            "match": "Any of the members of (hipobject1)",
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-hip-profile", folder="Shared")

        error_msg = str(exc_info.value)
        assert "HTTP error: 500 - API error: E003" in error_msg
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500

    def test_fetch_no_container_provided_error(self):
        """Test that InvalidObjectError is raised when no container parameter is provided."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-hip-profile")

        error_msg = str(exc_info.value)
        assert "HTTP error: 400 - API error: E003" in error_msg
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 400

    def test_fetch_multiple_containers_provided_error(self):
        """Test that InvalidObjectError is raised when multiple container parameters are provided."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(
                name="test-hip-profile",
                folder="Shared",
                snippet="TestSnippet",
            )

        error_msg = str(exc_info.value)
        assert "HTTP error: 400 - API error: E003" in error_msg
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 400

    def test_fetch_invalid_response_type_error(self):
        """Test that InvalidObjectError is raised when the response is not a dictionary."""
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test123", folder="Shared")

        error_msg = str(exc_info.value)
        assert "HTTP error: 500 - API error: E003" in error_msg
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500
