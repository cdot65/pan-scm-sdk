# tests/scm/config/objects/test_tag.py

# Standard library imports
from unittest.mock import MagicMock

# External libraries
import pytest
from pydantic import ValidationError
from requests.exceptions import HTTPError

# Local SDK imports
from scm.config.objects import Tag
from scm.exceptions import (
    APIError,
    InvalidObjectError,
    MissingQueryParameterError,
    ObjectNotPresentError,
    ReferenceNotZeroError,
)
from scm.models.objects import TagResponseModel

# Import factories
from tests.factories import (
    TagCreateApiFactory,
    TagUpdateApiFactory,
    TagResponseFactory,
)
from tests.utils import raise_mock_http_error


@pytest.mark.usefixtures("load_env")
class TestTagBase:
    """Base class for Tag tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm  # noqa
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = Tag(self.mock_scm)  # noqa


class TestTagList(TestTagBase):
    """Tests for listing Tag objects."""

    def test_list_valid(self):
        """Test listing all tags."""
        mock_response = {
            "data": [
                TagResponseFactory.with_color(
                    name="TestTag1",
                    color="Red",
                    folder="Shared",
                    comments="First test tag",
                ).model_dump(),
                TagResponseFactory.with_color(
                    name="TestTag2",
                    color="Blue",
                    folder="Shared",
                    comments="Second test tag",
                ).model_dump(),
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        existing_tags = self.client.list(folder="Shared")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/tags",
            params={
                "limit": 10000,
                "folder": "Shared",
            },
        )
        assert isinstance(existing_tags, list)
        assert isinstance(existing_tags[0], TagResponseModel)
        assert len(existing_tags) == 2
        assert existing_tags[0].name == "TestTag1"
        assert existing_tags[0].color == "Red"

    def test_list_filters_valid(self):
        """Test listing tags with valid filters."""
        filters = {
            "colors": ["Red", "Blue"],
        }

        mock_response = {
            "data": [
                TagResponseFactory.with_color(
                    name="TestTag1",
                    color="Red",
                    folder="Shared",
                ).model_dump(),
                TagResponseFactory.with_color(
                    name="TestTag2",
                    color="Blue",
                    folder="Shared",
                ).model_dump(),
                TagResponseFactory.with_color(
                    name="TestTag3",
                    color="Green",
                    folder="Shared",
                ).model_dump(),
            ],
            "offset": 0,
            "total": 3,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        filtered_tags = self.client.list(folder="Shared", **filters)

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/tags",
            params={
                "limit": 10000,
                "folder": "Shared",
            },
        )

        assert len(filtered_tags) == 2
        assert all(tag.color in ["Red", "Blue"] for tag in filtered_tags)

    def test_list_filters_invalid_colors_not_list(self):
        """Test listing tags with 'colors' filter that is not a list."""
        filters = {
            "colors": "Red",  # Should be a list
        }

        # Don't set up any mock response so validation runs first
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Shared", **filters)

        assert exc_info.value.message == "'colors' filter must be a list"
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500
        assert exc_info.value.details == {"errorType": "Invalid Object"}

    def test_list_filters_invalid_colors_type(self):
        """Test that color filter must be a list."""
        # Mock minimum valid API response
        mock_response = {"data": []}
        self.mock_scm.get.return_value = mock_response  # noqa

        filters = {"colors": "Red"}  # String instead of list

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Shared", **filters)

        assert exc_info.value.message == "'colors' filter must be a list"
        assert exc_info.value.http_status_code == 500
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.details == {"errorType": "Invalid Object"}

    def test_list_empty_folder_error(self):
        """Test that empty folder raises appropriate error."""
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.list(folder="")

        error_msg = str(exc_info.value)
        assert "HTTP error: 400 - API error: E003" in error_msg

    def test_list_container_missing_error(self):
        """Test that InvalidObjectError is raised when no container parameter is provided."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list()

        error_msg = str(exc_info.value)
        assert "HTTP error: 400 - API error: E003" in error_msg

    def test_list_container_multiple_error(self):
        """Test validation of container parameters."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Shared", snippet="TestSnippet")

        error_msg = str(exc_info.value)
        assert "HTTP error: 400 - API error: E003" in error_msg

    def test_list_response_invalid_format(self):
        """Test that InvalidObjectError is raised when the response is not a dictionary."""
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Shared")

        assert "HTTP error: 500 - API error: E003" in str(exc_info.value)

    def test_list_response_invalid_data_field_missing(self):
        """Test that InvalidObjectError is raised when API returns response with missing data field."""
        self.mock_scm.get.return_value = {"wrong_field": "value"}  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Shared")

        assert "HTTP error: 500 - API error: E003" in str(exc_info.value)

    def test_list_response_invalid_data_field_type(self):
        """Test that InvalidObjectError is raised when API returns non-list data field."""
        self.mock_scm.get.return_value = {"data": "not a list"}  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Shared")

        assert "HTTP error: 500 - API error: E003" in str(exc_info.value)

    def test_list_http_error_no_response_content(self):
        """Test list method when HTTP error has no response content."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.list(folder="Shared")

    def test_list_filters_invalid_color_value(self):
        """Test listing tags with an invalid color value in the 'colors' filter."""
        filters = {
            "colors": ["Red", "InvalidColor"],
        }

        # Mock the response from the API
        mock_response = {
            "data": [
                TagResponseFactory.with_color(
                    name="TestTag1",
                    color="Red",
                    folder="Shared",
                ).model_dump(),
                TagResponseFactory.with_color(
                    name="TestTag2",
                    color="Blue",
                    folder="Shared",
                ).model_dump(),
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Shared", **filters)

        error_msg = exc_info.value.message
        assert "Invalid color 'InvalidColor'" in error_msg
        assert exc_info.value.http_status_code == 400
        assert exc_info.value.error_code == "E003"

    def test_list_api_error_handling(self):
        """Test that API errors during list are properly handled."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="E400",
            message="Bad Request",
            error_type="Invalid Request",
        )

        with pytest.raises(APIError) as exc_info:
            self.client.list(folder="Shared")

        error_msg = str(exc_info.value)
        assert "{'errorType': 'Invalid Request'}" in error_msg
        assert "HTTP error: 400" in error_msg
        assert "API error: E400" in error_msg


class TestTagCreate(TestTagBase):
    """Tests for creating Tag objects."""

    def test_create_valid_tag(self):
        """Test creating a tag with valid data."""
        test_tag = TagCreateApiFactory.with_color(color="Red", folder="Shared")
        mock_response = TagResponseFactory.from_request(test_tag)

        self.mock_scm.post.return_value = mock_response.model_dump()  # noqa
        created_tag = self.client.create(test_tag.model_dump(exclude_unset=True))

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/tags",
            json=test_tag.model_dump(exclude_unset=True),
        )
        assert str(created_tag.id) == str(mock_response.id)
        assert created_tag.name == test_tag.name
        assert created_tag.color == test_tag.color
        assert created_tag.folder == test_tag.folder

    def test_create_invalid_color(self):
        """Test creating a tag with an invalid color."""
        test_tag_data = TagCreateApiFactory.build().model_dump()
        test_tag_data["color"] = "InvalidColor"

        with pytest.raises(ValidationError) as exc_info:
            self.client.create(test_tag_data)

        assert "Color must be one of" in str(exc_info.value)

    def test_create_multiple_containers(self):
        """Test creating a tag with multiple containers."""
        test_tag_data = TagCreateApiFactory.build().model_dump()
        test_tag_data["folder"] = "Shared"
        test_tag_data["snippet"] = "TestSnippet"

        with pytest.raises(ValidationError) as exc_info:
            self.client.create(test_tag_data)

        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_create_no_container(self):
        """Test creating a tag without a container."""
        test_tag_data = TagCreateApiFactory.build().model_dump()
        test_tag_data.pop("folder", None)

        with pytest.raises(ValidationError) as exc_info:
            self.client.create(test_tag_data)

        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_create_http_error_no_response_content(self):
        """Test create method when HTTP error has no response content."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.post.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.create({"name": "TestTag", "color": "Red", "folder": "Shared"})

    def test_create_server_error(self):
        """Test generic exception handling in create method."""
        self.mock_scm.post.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )

        with pytest.raises(APIError) as exc_info:
            self.client.create({"name": "TestTag", "color": "Red", "folder": "Shared"})

        error_msg = str(exc_info.value)
        assert "{'errorType': 'Internal Error'}" in error_msg
        assert "HTTP error: 500" in error_msg
        assert "API error: E003" in error_msg


class TestTagGet(TestTagBase):
    """Tests for retrieving a specific Tag object."""

    def test_get_valid_tag(self):
        """Test retrieving a specific tag by ID."""
        mock_response = TagResponseFactory.with_color(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="TestTag",
            color="Red",
            folder="Shared",
        )

        self.mock_scm.get.return_value = mock_response.model_dump()  # noqa
        tag_id = mock_response.id

        retrieved_tag = self.client.get(tag_id)

        self.mock_scm.get.assert_called_once_with(  # noqa
            f"/config/objects/v1/tags/{tag_id}"
        )
        assert isinstance(retrieved_tag, TagResponseModel)
        assert retrieved_tag.id == mock_response.id
        assert retrieved_tag.name == mock_response.name
        assert retrieved_tag.color == mock_response.color
        assert retrieved_tag.folder == mock_response.folder

    def test_get_tag_not_present_error(self):
        """Test error handling when the tag is not present."""
        tag_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Tag not found",
            error_type="Object Not Present",
        )

        with pytest.raises(ObjectNotPresentError) as exc_info:
            self.client.get(tag_id)

        error_msg = str(exc_info.value)
        assert "{'errorType': 'Object Not Present'}" in error_msg
        assert "HTTP error: 404" in error_msg
        assert "API error: API_I00013" in error_msg

    def test_get_http_error_no_response_content(self):
        """Test get method when HTTP error has no response content."""
        tag_id = "123e4567-e89b-12d3-a456-426655440000"

        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.get(tag_id)


class TestTagUpdate(TestTagBase):
    """Tests for updating Tag objects."""

    def test_update_valid_tag(self):
        """Test updating a tag with valid data."""
        update_data = TagUpdateApiFactory.with_color(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedTag",
            color="Blue",
            comments="Updated comments",
        )
        input_data = update_data.model_dump()

        mock_response = TagResponseFactory.from_request(update_data)
        self.mock_scm.put.return_value = mock_response.model_dump()  # noqa

        updated_tag = self.client.update(input_data)

        self.mock_scm.put.assert_called_once_with(  # noqa
            f"/config/objects/v1/tags/{update_data.id}",
            json=input_data,
        )

        assert isinstance(updated_tag, TagResponseModel)
        assert updated_tag.id == mock_response.id
        assert updated_tag.name == mock_response.name
        assert updated_tag.color == mock_response.color
        assert updated_tag.comments == mock_response.comments

    def test_update_invalid_color(self):
        """Test updating a tag with an invalid color."""
        update_data = TagUpdateApiFactory.build().model_dump()
        update_data["color"] = "InvalidColor"

        with pytest.raises(ValidationError) as exc_info:
            self.client.update(update_data)

        assert "Color must be one of" in str(exc_info.value)

    def test_update_http_error_no_response_content(self):
        """Test update method when HTTP error has no response content."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.put.side_effect = mock_http_error  # noqa

        # Provide valid data to avoid ValidationError
        valid_id = "123e4567-e89b-12d3-a456-426655440000"
        update_data = {"id": valid_id, "name": "TestTag", "color": "Red"}

        with pytest.raises(HTTPError):
            self.client.update(update_data)
            self.client.update(update_data)

    def test_update_server_error(self):
        """Test handling of server errors during update."""
        update_data = TagUpdateApiFactory.build().model_dump()

        self.mock_scm.put.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )

        with pytest.raises(APIError) as exc_info:
            self.client.update(update_data)

        error_msg = str(exc_info.value)
        assert "{'errorType': 'Internal Error'}" in error_msg
        assert "HTTP error: 500" in error_msg
        assert "API error: E003" in error_msg


class TestTagDelete(TestTagBase):
    """Tests for deleting Tag objects."""

    def test_delete_success(self):
        """Test successful deletion of a tag."""
        tag_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.return_value = None  # noqa

        # Should not raise any exception
        self.client.delete(tag_id)

        self.mock_scm.delete.assert_called_once_with(  # noqa
            f"/config/objects/v1/tags/{tag_id}"
        )

    def test_delete_referenced_tag(self):
        """Test deleting a tag that is referenced elsewhere."""
        tag_id = "abcdefg"
        self.mock_scm.delete.side_effect = raise_mock_http_error(  # noqa
            status_code=409,
            error_code="E009",
            message="Tag is referenced by other objects.",
            error_type="Reference Not Zero",
        )

        with pytest.raises(ReferenceNotZeroError) as exc_info:
            self.client.delete(tag_id)

        error_message = str(exc_info.value)
        assert "{'errorType': 'Reference Not Zero'}" in error_message
        assert "HTTP error: 409" in error_message
        assert "API error: E009" in error_message

    def test_delete_tag_not_present_error(self):
        """Test error handling when the tag to delete is not present."""
        tag_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Tag not found",
            error_type="Object Not Present",
        )

        with pytest.raises(ObjectNotPresentError) as exc_info:
            self.client.delete(tag_id)

        error_message = str(exc_info.value)
        assert "{'errorType': 'Object Not Present'}" in error_message
        assert "HTTP error: 404" in error_message
        assert "API error: API_I00013" in error_message

    def test_delete_http_error_no_response_content(self):
        """Test delete method when HTTP error has no response content."""
        tag_id = "123e4567-e89b-12d3-a456-426655440000"

        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.delete.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.delete(tag_id)


class TestTagFetch(TestTagBase):
    """Tests for fetching Tag objects by name."""

    def test_fetch_valid_tag(self):
        """Test fetching a tag by name."""
        mock_response = TagResponseFactory.with_color(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="TestTag",
            color="Red",
            folder="Shared",
        ).model_dump()

        self.mock_scm.get.return_value = mock_response  # noqa

        fetched_tag = self.client.fetch(name="TestTag", folder="Shared")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/tags",
            params={
                "folder": "Shared",
                "name": "TestTag",
            },
        )

        assert isinstance(fetched_tag, dict)
        assert fetched_tag["id"] == mock_response["id"]
        assert fetched_tag["name"] == mock_response["name"]
        assert fetched_tag["color"] == mock_response["color"]
        assert fetched_tag["folder"] == mock_response["folder"]

    def test_fetch_tag_not_present_error(self):
        """Test fetching a tag that does not exist."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Tag not found",
            error_type="Object Not Present",
        )

        with pytest.raises(ObjectNotPresentError) as exc_info:
            self.client.fetch(name="NonexistentTag", folder="Shared")

        error_msg = str(exc_info.value)
        assert "{'errorType': 'Object Not Present'}" in error_msg
        assert "HTTP error: 404" in error_msg
        assert "API error: API_I00013" in error_msg

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
            self.client.fetch(name="TestTag", folder="")

        error_msg = str(exc_info.value)
        assert '"folder" is not allowed to be empty' in error_msg
        assert "HTTP error: 400" in error_msg
        assert "API error: E003" in error_msg

    def test_fetch_no_container_provided_error(self):
        """Test fetching when no container parameter is provided."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="TestTag")

        error_msg = exc_info.value.message
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in error_msg
        )

    def test_fetch_multiple_containers_provided_error(self):
        """Test fetching when multiple container parameters are provided."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="TestTag", folder="Shared", snippet="TestSnippet")

        error_msg = exc_info.value.message
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in error_msg
        )

    def test_fetch_invalid_response_format_error(self):
        """Test fetching when the API returns an unexpected format."""
        self.mock_scm.get.return_value = {"unexpected": "format"}  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="TestTag", folder="Shared")

        error_msg = exc_info.value.message
        assert "Invalid response format: missing 'id' field" in error_msg

    def test_fetch_http_error_no_response_content(self):
        """Test that an HTTPError without response content in fetch() re-raises the exception."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.fetch(name="TestTag", folder="Shared")

    def test_fetch_response_invalid_format(self):
        """Test fetching when the API returns a response that is not a dictionary."""
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="TestTag", folder="Shared")

        error_msg = exc_info.value.message
        assert "Invalid response format: expected dictionary" in error_msg
        assert exc_info.value.http_status_code == 500
        assert exc_info.value.error_code == "E003"
