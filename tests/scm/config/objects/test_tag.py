# tests/scm/config/objects/test_tag.py

# Standard library imports
from unittest.mock import MagicMock

from pydantic import ValidationError

# External libraries
import pytest
from requests.exceptions import HTTPError

# Local SDK imports
from scm.config.objects import Tag
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.objects import TagResponseModel, TagUpdateModel

# Import factories
from tests.factories.objects.tag import (
    TagCreateApiFactory,
    TagResponseFactory,
    TagUpdateApiFactory,
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
        self.client = Tag(self.mock_scm, max_limit=5000)  # noqa


class TestTagMaxLimit(TestTagBase):
    """Tests for max_limit functionality."""

    def test_default_max_limit(self):
        """Test that default max_limit is set correctly."""
        client = Tag(self.mock_scm)  # noqa
        assert client.max_limit == Tag.DEFAULT_MAX_LIMIT
        assert client.max_limit == 2500

    def test_custom_max_limit(self):
        """Test setting a custom max_limit."""
        client = Tag(self.mock_scm, max_limit=1000)  # noqa
        assert client.max_limit == 1000

    def test_max_limit_setter(self):
        """Test the max_limit property setter."""
        client = Tag(self.mock_scm)  # noqa
        client.max_limit = 3000
        assert client.max_limit == 3000

    def test_invalid_max_limit_type(self):
        """Test that invalid max_limit type raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            Tag(self.mock_scm, max_limit="invalid")  # noqa
        assert "{'error': 'Invalid max_limit type'} - HTTP error: 400 - API error: E003" in str(
            exc_info.value
        )

    def test_max_limit_too_low(self):
        """Test that max_limit below 1 raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            Tag(self.mock_scm, max_limit=0)  # noqa
        assert "{'error': 'Invalid max_limit value'} - HTTP error: 400 - API error: E003" in str(
            exc_info.value
        )

    def test_max_limit_too_high(self):
        """Test that max_limit above ABSOLUTE_MAX_LIMIT raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            Tag(self.mock_scm, max_limit=6000)  # noqa
        assert "max_limit exceeds maximum allowed value" in str(exc_info.value)


class TestTagList(TestTagBase):
    """Tests for listing Tag objects with new filtering logic."""

    def test_list_valid(self):
        """Test listing all tags without filters."""
        mock_response = {
            "data": [
                TagResponseFactory.with_color(
                    name="TestTag1",
                    color="Red",
                    folder="Texas",
                ).model_dump(),
                TagResponseFactory.with_color(
                    name="TestTag2",
                    color="Blue",
                    folder="Texas",
                ).model_dump(),
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response
        existing_tags = self.client.list(folder="Texas")

        self.mock_scm.get.assert_called_once_with(
            "/config/objects/v1/tags",
            params={
                "limit": 5000,
                "folder": "Texas",
                "offset": 0,
            },
        )
        assert isinstance(existing_tags, list)
        assert len(existing_tags) == 2
        assert existing_tags[0].name == "TestTag1"
        assert existing_tags[1].name == "TestTag2"

    def test_list_exact_match(self):
        """Test exact_match=True ensures only tags with the exact folder match are returned."""
        mock_response = {
            "data": [
                TagResponseFactory.build(name="ExactMatchTag", folder="Texas").model_dump(),
                TagResponseFactory.build(name="InheritedTag", folder="All").model_dump(),
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response

        tags = self.client.list(folder="Texas", exact_match=True)
        assert len(tags) == 1
        assert tags[0].name == "ExactMatchTag"
        assert tags[0].folder == "Texas"

    def test_list_exact_match_false(self):
        """Test exact_match=False returns tags from the specified folder and potentially others."""
        mock_response = {
            "data": [
                TagResponseFactory.build(name="ExactMatchTag", folder="Texas").model_dump(),
                TagResponseFactory.build(name="InheritedTag", folder="All").model_dump(),
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response

        tags = self.client.list(folder="Texas", exact_match=False)
        # Both tags should be returned since exact_match is False
        assert len(tags) == 2
        assert any(t.name == "ExactMatchTag" for t in tags)
        assert any(t.name == "InheritedTag" for t in tags)

    def test_list_exclude_folders(self):
        """Test excluding certain folders from the returned results."""
        mock_response = {
            "data": [
                TagResponseFactory.build(name="TagTexas", folder="Texas").model_dump(),
                TagResponseFactory.build(name="TagAll", folder="All").model_dump(),
                TagResponseFactory.build(name="TagGlobal", folder="Global").model_dump(),
            ],
            "offset": 0,
            "total": 3,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response

        tags = self.client.list(folder="Texas", exclude_folders=["All", "Global"])
        # Only the Texas folder tag should remain
        assert len(tags) == 1
        assert tags[0].name == "TagTexas"

    def test_list_exclude_snippets(self):
        """Test excluding objects by snippet values."""
        mock_response = {
            "data": [
                TagResponseFactory.build(
                    name="NoSnippet", folder="Texas", snippet=None
                ).model_dump(),
                TagResponseFactory.build(
                    name="PredefinedTag", folder="Texas", snippet="predefined"
                ).model_dump(),
                TagResponseFactory.build(
                    name="CustomSnippetTag",
                    folder="Texas",
                    snippet="custom-snippet",
                ).model_dump(),
            ],
            "offset": 0,
            "total": 3,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response

        # Exclude 'predefined' and 'custom-snippet'
        tags = self.client.list(folder="Texas", exclude_snippets=["predefined", "custom-snippet"])
        # Only NoSnippet should remain
        assert len(tags) == 1
        assert tags[0].name == "NoSnippet"

    def test_list_exclude_devices(self):
        """Test excluding objects by device values."""
        mock_response = {
            "data": [
                TagResponseFactory.build(
                    name="TagOnDeviceA",
                    folder="Texas",
                    snippet=None,
                    device="DeviceA",
                ).model_dump(),
                TagResponseFactory.build(
                    name="TagOnDeviceB",
                    folder="Texas",
                    snippet=None,
                    device="DeviceB",
                ).model_dump(),
                TagResponseFactory.build(
                    name="TagOnDeviceC",
                    folder="Texas",
                    snippet=None,
                    device="DeviceC",
                ).model_dump(),
            ],
            "offset": 0,
            "total": 3,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response

        # Exclude 'DeviceB' and 'DeviceC'
        tags = self.client.list(folder="Texas", exclude_devices=["DeviceB", "DeviceC"])
        # Only the tag on DeviceA should remain
        assert len(tags) == 1
        assert tags[0].name == "TagOnDeviceA"
        assert tags[0].device == "DeviceA"

    def test_list_with_colors_and_exclusions(self):
        """Test combining color filter with exclude_folders and exclude_snippets."""
        mock_response = {
            "data": [
                TagResponseFactory.build(
                    name="RedTexas", folder="Texas", snippet=None, color="Red"
                ).model_dump(),
                TagResponseFactory.build(
                    name="BlueAll", folder="All", snippet=None, color="Blue"
                ).model_dump(),
                TagResponseFactory.build(
                    name="RedPredefined",
                    folder="Texas",
                    snippet="predefined",
                    color="Red",
                ).model_dump(),
            ],
            "offset": 0,
            "total": 3,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response

        tags = self.client.list(
            folder="Texas",
            colors=["Red", "Blue"],
            exclude_folders=["All"],
            exclude_snippets=["predefined"],
        )
        # Should exclude folder=All and snippet=predefined
        # RedTexas matches colors and folder, and snippet is None
        assert len(tags) == 1
        assert tags[0].name == "RedTexas"

    def test_list_no_container_provided(self):
        """Test that InvalidObjectError is raised when no container parameter is provided."""
        with pytest.raises(InvalidObjectError):
            self.client.list()

    def test_list_multiple_containers_provided(self):
        """Test that providing multiple containers is invalid."""
        with pytest.raises(InvalidObjectError):
            self.client.list(folder="Texas", snippet="TestSnippet")

    def test_list_empty_folder_error(self):
        """Test that empty folder raises the appropriate error."""
        with pytest.raises(MissingQueryParameterError):
            self.client.list(folder="")

    def test_list_api_format_errors(self):
        """Test responses that do not meet the expected format."""
        # Not a dictionary response
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]
        with pytest.raises(InvalidObjectError):
            self.client.list(folder="Texas")

        # Missing 'data' field
        self.mock_scm.get.return_value = {"wrong_field": "value"}
        with pytest.raises(InvalidObjectError):
            self.client.list(folder="Texas")

        # 'data' not a list
        self.mock_scm.get.return_value = {"data": "not a list"}
        with pytest.raises(InvalidObjectError):
            self.client.list(folder="Texas")

    def test_list_colors_invalid_type(self):
        """Test invalid colors filter."""
        mock_response = {"data": []}
        self.mock_scm.get.return_value = mock_response

        with pytest.raises(InvalidObjectError):
            self.client.list(folder="Texas", colors="Red")  # Not a list

    def test_list_colors_invalid_color_value(self):
        """Test invalid color value in the colors filter."""
        mock_response = {
            "data": [
                TagResponseFactory.with_color(
                    name="RedTag", color="Red", folder="Texas"
                ).model_dump()
            ],
            "offset": 0,
            "total": 1,
            "limit": 200,
        }
        self.mock_scm.get.return_value = mock_response

        with pytest.raises(InvalidObjectError):
            self.client.list(folder="Texas", colors=["InvalidColor"])

    def test_list_http_error_handling(self):
        """Test HTTP errors during list."""
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=400,
            error_code="E400",
            message="Bad Request",
            error_type="Invalid Request",
        )

        with pytest.raises(HTTPError):
            self.client.list(folder="Texas")

    def test_list_pagination_multiple_pages(self):
        """Test that the list method correctly aggregates data from multiple pages.
        Using a custom client with max_limit=2500 to test pagination.
        """
        client = Tag(self.mock_scm, max_limit=2500)  # noqa

        # Create test data for three pages
        first_page = [
            TagResponseFactory.with_color(
                name=f"tag-page1-{i}",
                folder="Texas",
                color="Red",
            ).model_dump()
            for i in range(2500)
        ]

        second_page = [
            TagResponseFactory.with_color(
                name=f"tag-page2-{i}",
                folder="Texas",
                color="Blue",
            ).model_dump()
            for i in range(2500)
        ]

        third_page = [
            TagResponseFactory.with_color(
                name=f"tag-page3-{i}",
                folder="Texas",
                color="Green",
            ).model_dump()
            for i in range(2500)
        ]

        # Mock API responses for pagination
        mock_responses = [
            {"data": first_page},
            {"data": second_page},
            {"data": third_page},
            {"data": []},  # Empty response to end pagination
        ]
        self.mock_scm.get.side_effect = mock_responses  # noqa

        # Get results
        results = client.list(folder="Texas")

        # Verify results
        assert len(results) == 7500  # Total objects across all pages
        assert isinstance(results[0], TagResponseModel)
        assert all(isinstance(obj, TagResponseModel) for obj in results)

        # Verify API calls
        assert self.mock_scm.get.call_count == 4  # noqa # Three pages + one final check

        # Verify API calls were made with correct offset values
        self.mock_scm.get.assert_any_call(  # noqa
            "/config/objects/v1/tags",
            params={"folder": "Texas", "limit": 2500, "offset": 0},
        )

        self.mock_scm.get.assert_any_call(  # noqa
            "/config/objects/v1/tags",
            params={"folder": "Texas", "limit": 2500, "offset": 2500},
        )

        self.mock_scm.get.assert_any_call(  # noqa
            "/config/objects/v1/tags",
            params={"folder": "Texas", "limit": 2500, "offset": 5000},
        )

        # Verify content ordering
        assert results[0].name == "tag-page1-0"
        assert results[2500].name == "tag-page2-0"
        assert results[5000].name == "tag-page3-0"

        # Verify colors were maintained
        assert results[0].color == "Red"
        assert results[2500].color == "Blue"
        assert results[5000].color == "Green"


class TestTagCreate(TestTagBase):
    """Tests for creating Tag objects."""

    def test_create_valid_tag(self):
        """Test creating a tag with valid data."""
        test_tag = TagCreateApiFactory.with_color(color="Red", folder="Texas")
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
        test_tag_data["folder"] = "Texas"
        test_tag_data["snippet"] = "TestSnippet"

        with pytest.raises(ValidationError) as exc_info:
            self.client.create(test_tag_data)

        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_create_no_container(self):
        """Test creating a tag without a container."""
        test_tag_data = TagCreateApiFactory.build().model_dump()
        test_tag_data.pop("folder", None)

        with pytest.raises(ValidationError) as exc_info:
            self.client.create(test_tag_data)

        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_create_http_error_no_response_content(self):
        """Test create method when HTTP error has no response content."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.post.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.create({"name": "TestTag", "color": "Red", "folder": "Texas"})

    def test_create_server_error(self):
        """Test generic exception handling in create method."""
        self.mock_scm.post.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.create({"name": "TestTag", "color": "Red", "folder": "Texas"})
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "An internal error occurred"
        assert error_response["_errors"][0]["details"]["errorType"] == "Internal Error"


class TestTagGet(TestTagBase):
    """Tests for retrieving a specific Tag object."""

    def test_get_valid_tag(self):
        """Test retrieving a specific tag by ID."""
        mock_response = TagResponseFactory.with_color(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="TestTag",
            color="Red",
            folder="Texas",
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

        with pytest.raises(HTTPError) as exc_info:
            self.client.get(tag_id)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Tag not found"
        assert error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"

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

    def test_update_valid_object(self):
        """Test updating a tag with valid data."""
        update_data = TagUpdateApiFactory.with_color(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedTag",
            color="Blue",
            comments="Updated comments",
        )

        # Create mock response
        mock_response = TagResponseFactory.from_request(update_data)
        self.mock_scm.put.return_value = mock_response.model_dump()  # noqa

        # Perform update with Pydantic model directly
        updated_tag = self.client.update(update_data)

        # Verify call was made once
        self.mock_scm.put.assert_called_once()  # noqa

        # Get the actual call arguments
        call_args = self.mock_scm.put.call_args  # noqa

        # Check endpoint
        assert call_args[0][0] == f"/config/objects/v1/tags/{update_data.id}"

        # Check important payload fields
        payload = call_args[1]["json"]
        assert payload["name"] == "UpdatedTag"
        assert payload["color"] == "Blue"
        assert payload["comments"] == "Updated comments"

        # Assert the updated object matches the mock response
        assert isinstance(updated_tag, TagResponseModel)
        assert updated_tag.id == mock_response.id
        assert updated_tag.name == mock_response.name
        assert updated_tag.color == mock_response.color
        assert updated_tag.comments == mock_response.comments

    def test_update_invalid_color(self):
        """Test updating a tag with an invalid color."""
        # Instead of modifying after creation, build with invalid data
        tag_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-tag",
            "color": "InvalidColor",
        }

        with pytest.raises(ValidationError) as exc_info:
            # Try to create the model with invalid data
            TagUpdateModel(**tag_data)

        assert "Color must be one of" in str(exc_info.value)

    def test_update_http_error_no_response_content(self):
        """Test update method when HTTP error has no response content."""
        # Create test data as Pydantic model
        update_data = TagUpdateApiFactory.with_color(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test",
            with_color="asdf",
        )

        # Create a mock response object without content
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        # Create an HTTPError with the mock response
        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.put.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.update(update_data)

    def test_update_server_error(self):
        """Test handling of server errors during update."""
        update_data = TagUpdateApiFactory.build()

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

        with pytest.raises(HTTPError) as exc_info:
            self.client.delete(tag_id)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Tag is referenced by other objects."
        assert error_response["_errors"][0]["details"]["errorType"] == "Reference Not Zero"

    def test_delete_tag_not_present_error(self):
        """Test error handling when the tag to delete is not present."""
        tag_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Tag not found",
            error_type="Object Not Present",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.delete(tag_id)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Tag not found"
        assert error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"

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

    def test_fetch_valid_object(self):
        """Test fetching a tag by name."""
        mock_response_model = TagResponseFactory.with_color(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="TestTag",
            color="Red",
            folder="Texas",
        )

        mock_response_data = mock_response_model.model_dump()

        # Set the mock to return the response data directly
        self.mock_scm.get.return_value = mock_response_data  # noqa

        # Call the fetch method
        fetched_object = self.client.fetch(
            name=mock_response_model.name,
            folder=mock_response_model.folder,
        )

        # Assert that the GET request was made with the correct parameters
        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/tags",
            params={
                "folder": mock_response_model.folder,
                "name": mock_response_model.name,
            },
        )

        # Validate the returned object is a Pydantic model
        assert isinstance(fetched_object, TagResponseModel)

        # Validate the object attributes match the mock response
        assert str(fetched_object.id) == str(mock_response_model.id)
        assert fetched_object.name == mock_response_model.name
        assert fetched_object.color == mock_response_model.color
        assert fetched_object.folder == mock_response_model.folder

    def test_fetch_tag_not_present_error(self):
        """Test fetching a tag that does not exist."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Tag not found",
            error_type="Object Not Present",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.fetch(name="NonexistentTag", folder="Texas")
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Tag not found"
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
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in error_msg

    def test_fetch_multiple_containers_provided_error(self):
        """Test fetching when multiple container parameters are provided."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="TestTag", folder="Texas", snippet="TestSnippet")

        error_msg = exc_info.value.message
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in error_msg

    def test_fetch_invalid_response_format_error(self):
        """Test fetching when the API returns an unexpected format."""
        self.mock_scm.get.return_value = {"unexpected": "format"}  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="TestTag", folder="Texas")

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
            self.client.fetch(name="TestTag", folder="Texas")

    def test_fetch_response_invalid_format(self):
        """Test fetching when the API returns a response that is not a dictionary."""
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="TestTag", folder="Texas")

        error_msg = exc_info.value.message
        assert "Invalid response format: expected dictionary" in error_msg
        assert exc_info.value.http_status_code == 500
        assert exc_info.value.error_code == "E003"
