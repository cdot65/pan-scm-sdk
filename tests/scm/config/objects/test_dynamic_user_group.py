# tests/scm/config/objects/test_dynamic_user_group.py

# Standard library imports
from unittest.mock import MagicMock

# External libraries
import pytest
from requests.exceptions import HTTPError

# Local SDK imports
from scm.config.objects import DynamicUserGroup
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.objects import DynamicUserGroupResponseModel, DynamicUserGroupUpdateModel
from tests.utils import raise_mock_http_error


# Define test factories for DynamicUserGroup
class DynamicUserGroupCreateApiFactory:
    """Factory for creating dynamic user group data for API tests."""

    @staticmethod
    def with_folder(name="test_group", folder="Texas", **kwargs):
        """Create a dynamic user group with folder."""
        data = {
            "name": name,
            "filter": "'tag.criticality.high'",
            "folder": folder,
            **kwargs,
        }
        return data

    @staticmethod
    def with_snippet(name="test_group", snippet="TestSnippet", **kwargs):
        """Create a dynamic user group with snippet."""
        data = {
            "name": name,
            "filter": "'tag.criticality.high'",
            "snippet": snippet,
            **kwargs,
        }
        return data

    @staticmethod
    def with_device(name="test_group", device="TestDevice", **kwargs):
        """Create a dynamic user group with device."""
        data = {
            "name": name,
            "filter": "'tag.criticality.high'",
            "device": device,
            **kwargs,
        }
        return data


class DynamicUserGroupUpdateApiFactory:
    """Factory for creating dynamic user group update data for API tests."""

    @staticmethod
    def with_folder(
        group_id="123e4567-e89b-12d3-a456-426655440000", name="updated_group", **kwargs
    ):
        """Create update data for a dynamic user group."""
        # Create a Pydantic model instead of a dict
        data = {
            "id": group_id,
            "name": name,
            "filter": "'tag.criticality.medium'",
            **kwargs,
        }
        return DynamicUserGroupUpdateModel(**data)


class DynamicUserGroupResponseFactory:
    """Factory for creating dynamic user group response data."""

    @staticmethod
    def with_folder(
        group_id="123e4567-e89b-12d3-a456-426655440000",
        name="test_group",
        folder="Texas",
        **kwargs,
    ):
        """Create a response model with folder container."""
        data = {
            "id": group_id,
            "name": name,
            "filter": "'tag.criticality.high'",
            "folder": folder,
            **kwargs,
        }
        return data

    @staticmethod
    def with_snippet(
        group_id="123e4567-e89b-12d3-a456-426655440000",
        name="test_group",
        snippet="TestSnippet",
        **kwargs,
    ):
        """Create a response model with snippet container."""
        data = {
            "id": group_id,
            "name": name,
            "filter": "'tag.criticality.high'",
            "snippet": snippet,
            **kwargs,
        }
        return data

    @staticmethod
    def with_device(
        group_id="123e4567-e89b-12d3-a456-426655440000",
        name="test_group",
        device="TestDevice",
        **kwargs,
    ):
        """Create a response model with device container."""
        data = {
            "id": group_id,
            "name": name,
            "filter": "'tag.criticality.high'",
            "device": device,
            **kwargs,
        }
        return data

    @staticmethod
    def from_request(request_data):
        """Create a response model based on a request data."""
        # Create a new dict to avoid modifying the original
        if isinstance(request_data, DynamicUserGroupUpdateModel):
            data = request_data.model_dump()
        else:
            data = request_data.copy()

        if "id" not in data:
            data["id"] = "123e4567-e89b-12d3-a456-426655440000"
        return data


@pytest.mark.usefixtures("load_env")
class TestDynamicUserGroupBase:
    """Base class for Dynamic User Group tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm  # noqa
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = DynamicUserGroup(self.mock_scm, max_limit=5000)  # noqa


# -------------------- Test Classes Grouped by Functionality --------------------


class TestDynamicUserGroupMaxLimit(TestDynamicUserGroupBase):
    """Tests for max_limit functionality."""

    def test_default_max_limit(self):
        """Test that default max_limit is set correctly."""
        client = DynamicUserGroup(self.mock_scm)  # noqa
        assert client.max_limit == DynamicUserGroup.DEFAULT_MAX_LIMIT
        assert client.max_limit == 2500

    def test_custom_max_limit(self):
        """Test setting a custom max_limit."""
        client = DynamicUserGroup(self.mock_scm, max_limit=1000)  # noqa
        assert client.max_limit == 1000

    def test_max_limit_setter(self):
        """Test the max_limit property setter."""
        client = DynamicUserGroup(self.mock_scm)  # noqa
        client.max_limit = 3000
        assert client.max_limit == 3000

    def test_invalid_max_limit_type(self):
        """Test that invalid max_limit type raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            DynamicUserGroup(self.mock_scm, max_limit="invalid")  # noqa
        assert "{'error': 'Invalid max_limit type'} - HTTP error: 400 - API error: E003" in str(
            exc_info.value
        )

    def test_max_limit_too_low(self):
        """Test that max_limit below 1 raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            DynamicUserGroup(self.mock_scm, max_limit=0)  # noqa
        assert "{'error': 'Invalid max_limit value'} - HTTP error: 400 - API error: E003" in str(
            exc_info.value
        )

    def test_max_limit_too_high(self):
        """Test that max_limit above ABSOLUTE_MAX_LIMIT raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            DynamicUserGroup(self.mock_scm, max_limit=6000)  # noqa
        assert "max_limit exceeds maximum allowed value" in str(exc_info.value)


class TestDynamicUserGroupList(TestDynamicUserGroupBase):
    """Tests for listing Dynamic User Group objects."""

    def test_list_valid(self):
        """Test listing all dynamic user groups successfully."""
        mock_response = {
            "data": [
                DynamicUserGroupResponseFactory.with_folder(),
                DynamicUserGroupResponseFactory.with_folder(name="test_group2"),
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        existing_objects = self.client.list(folder="Texas")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/dynamic-user-groups",
            params={
                "limit": 5000,
                "folder": "Texas",
                "offset": 0,
            },
        )
        assert isinstance(existing_objects, list)
        assert isinstance(existing_objects[0], DynamicUserGroupResponseModel)
        assert len(existing_objects) == 2

    def test_list_folder_empty_error(self):
        """Test that an empty 'folder' parameter raises an error."""
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.list(folder="")

        error_msg = str(exc_info.value)
        assert (
            "{'field': 'folder', 'error': '\"folder\" is not allowed to be empty'} - HTTP error: 400 - API error: E003"
            in error_msg
        )

    def test_list_folder_nonexistent_error(self):
        """Test error handling when listing in a nonexistent folder."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Listing failed",
            error_type="Operation Impossible",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.list(folder="NonexistentFolder")
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Listing failed"
        assert error_response["_errors"][0]["details"]["errorType"] == "Operation Impossible"

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

    def test_list_filters_valid(self):
        """Test that valid filters are processed correctly."""
        filters = {
            "filters": ["tag.criticality.high"],
            "tags": ["tag1"],
        }

        mock_response = {
            "data": [
                DynamicUserGroupResponseFactory.with_folder(
                    id="123e4567-e89b-12d3-a456-426655440000",
                    name="high_criticality_group",
                    folder="Texas",
                    filter="'tag.criticality.high'",
                    description="High criticality group",
                    tag=["tag1"],
                ),
            ],
            "offset": 0,
            "total": 1,
            "limit": 200,
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        result = self.client.list(folder="Texas", **filters)

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/dynamic-user-groups",
            params={
                "limit": 5000,
                "folder": "Texas",
                "offset": 0,
            },
        )
        assert len(result) == 1
        assert result[0].name == "high_criticality_group"

    def test_list_filters_lists_empty(self):
        """Test behavior with empty filter lists."""
        mock_response = {
            "data": [
                DynamicUserGroupResponseFactory.with_folder(),
                DynamicUserGroupResponseFactory.with_folder(name="test_group2"),
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Empty lists should result in no matches
        filtered_objects = self.client.list(
            folder="Texas",
            filters=[],
        )
        assert len(filtered_objects) == 0

        filtered_objects = self.client.list(
            folder="Texas",
            tags=[],
        )
        assert len(filtered_objects) == 0

    def test_list_filters_tags_validation(self):
        """Test validation of 'tags' filter specifically."""
        mock_objects = []

        # Test with string instead of list
        invalid_filters = {"tags": "tag1"}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_objects, invalid_filters)

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        assert error.error_code == "E003"
        assert "{'errorType': 'Invalid Object'}" in str(error)

    def test_list_filters_filters_validation(self):
        """Test validation of 'filters' filter specifically."""
        mock_objects = []

        # Test with string instead of list
        invalid_filters = {"filters": "tag.criticality.high"}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_objects, invalid_filters)

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        assert error.error_code == "E003"
        assert error.http_status_code == 400
        assert "{'errorType': 'Invalid Object'}" in str(error)

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
        assert "HTTP error: 500 - API error: E003" in str(error)

    def test_list_response_no_content(self):
        """Test that an HTTPError without response content in list() re-raises the exception."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.list(folder="Texas")

    # -------------------- Tests for exact_match and Exclusions --------------------

    def test_list_exact_match(self):
        """
        Test that exact_match=True returns only dynamic user groups that match the container exactly.
        """
        mock_response = {
            "data": [
                DynamicUserGroupResponseFactory.with_folder(
                    name="group_in_texas",
                    folder="Texas",
                    filter="'tag.criticality.high'",
                ),
                DynamicUserGroupResponseFactory.with_folder(
                    name="group_in_all", folder="All", filter="'tag.criticality.medium'"
                ),
            ]
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        filtered = self.client.list(folder="Texas", exact_match=True)
        # exact_match should exclude the one from "All"
        assert len(filtered) == 1
        assert filtered[0].folder == "Texas"
        assert filtered[0].name == "group_in_texas"

    def test_list_exclude_folders(self):
        """
        Test that exclude_folders removes dynamic user groups from those folders.
        """
        mock_response = {
            "data": [
                DynamicUserGroupResponseFactory.with_folder(
                    name="group_in_texas",
                    folder="Texas",
                    filter="'tag.criticality.high'",
                ),
                DynamicUserGroupResponseFactory.with_folder(
                    name="group_in_all", folder="All", filter="'tag.criticality.medium'"
                ),
            ]
        }
        self.mock_scm.get.return_value = mock_response

        filtered = self.client.list(folder="Texas", exclude_folders=["All"])
        assert len(filtered) == 1
        assert all(g.folder != "All" for g in filtered)

    def test_list_exclude_snippets(self):
        """
        Test that exclude_snippets removes dynamic user groups with those snippets.
        """
        mock_response = {
            "data": [
                DynamicUserGroupResponseFactory.with_snippet(
                    name="group_default_snippet",
                    folder=None,
                    snippet="default",
                    filter="'tag.criticality.high'",
                ),
                DynamicUserGroupResponseFactory.with_snippet(
                    name="group_special_snippet",
                    folder=None,
                    snippet="special",
                    filter="'tag.criticality.medium'",
                ),
            ]
        }
        self.mock_scm.get.return_value = mock_response

        filtered = self.client.list(snippet="default", exclude_snippets=["default"])
        assert len(filtered) == 1
        assert all(g.snippet != "default" for g in filtered)

    def test_list_exclude_devices(self):
        """
        Test that exclude_devices removes dynamic user groups from those devices.
        """
        mock_response = {
            "data": [
                DynamicUserGroupResponseFactory.with_device(
                    name="group_deviceA",
                    folder=None,
                    device="DeviceA",
                    filter="'tag.criticality.high'",
                ),
                DynamicUserGroupResponseFactory.with_device(
                    name="group_deviceB",
                    folder=None,
                    device="DeviceB",
                    filter="'tag.criticality.medium'",
                ),
            ]
        }
        self.mock_scm.get.return_value = mock_response

        filtered = self.client.list(device="DeviceB", exclude_devices=["DeviceA"])
        assert len(filtered) == 1
        assert all(g.device != "DeviceA" for g in filtered)

    def test_list_exact_match_and_exclusions(self):
        """
        Test combining exact_match with exclusions.
        """
        mock_response = {
            "data": [
                DynamicUserGroupResponseFactory.with_folder(
                    name="group_texas_default_deviceA",
                    folder="Texas",
                    snippet="default",
                    device="DeviceA",
                    filter="'tag.criticality.high'",
                ),
                DynamicUserGroupResponseFactory.with_folder(
                    name="group_texas_special_deviceB",
                    folder="Texas",
                    snippet="special",
                    device="DeviceB",
                    filter="'tag.criticality.medium'",
                ),
                DynamicUserGroupResponseFactory.with_folder(
                    name="group_all_default_deviceA",
                    folder="All",
                    snippet="default",
                    device="DeviceA",
                    filter="'tag.criticality.low'",
                ),
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

        # Only group_texas_special_deviceB should remain after all filters
        assert len(filtered) == 1
        obj = filtered[0]
        assert obj.folder == "Texas"
        assert obj.snippet != "default"
        assert obj.device != "DeviceA"

    def test_list_pagination_multiple_pages(self):
        """Test pagination with multiple pages of results."""
        client = DynamicUserGroup(self.mock_scm, max_limit=2500)  # noqa

        # Create test data for three pages
        first_page = [
            DynamicUserGroupResponseFactory.with_folder(
                name=f"group-page1-{i}", folder="Texas", filter=f"'tag.criticality.{i}'"
            )
            for i in range(2500)
        ]

        second_page = [
            DynamicUserGroupResponseFactory.with_folder(
                name=f"group-page2-{i}", folder="Texas", filter=f"'tag.criticality.{i}'"
            )
            for i in range(2500)
        ]

        third_page = [
            DynamicUserGroupResponseFactory.with_folder(
                name=f"group-page3-{i}", folder="Texas", filter=f"'tag.criticality.{i}'"
            )
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
        assert isinstance(results[0], DynamicUserGroupResponseModel)
        assert all(isinstance(obj, DynamicUserGroupResponseModel) for obj in results)

        # Verify the number of API calls
        assert self.mock_scm.get.call_count == 4  # noqa # Three pages + one final check

        # Verify first API call parameters
        self.mock_scm.get.assert_any_call(  # noqa
            "/config/objects/v1/dynamic-user-groups",
            params={"folder": "Texas", "limit": 2500, "offset": 0},
        )

        # Verify second API call parameters (offset should be 2500)
        self.mock_scm.get.assert_any_call(  # noqa
            "/config/objects/v1/dynamic-user-groups",
            params={"folder": "Texas", "limit": 2500, "offset": 2500},
        )

        # Verify third API call parameters (offset should be 5000)
        self.mock_scm.get.assert_any_call(  # noqa
            "/config/objects/v1/dynamic-user-groups",
            params={"folder": "Texas", "limit": 2500, "offset": 5000},
        )

        # Verify content from each page is present
        assert results[0].name == "group-page1-0"
        assert results[2500].name == "group-page2-0"
        assert results[5000].name == "group-page3-0"


class TestDynamicUserGroupCreate(TestDynamicUserGroupBase):
    """Tests for creating Dynamic User Group objects."""

    def test_create_valid(self):
        """Test creating a dynamic user group successfully."""
        test_data = DynamicUserGroupCreateApiFactory.with_folder()
        mock_response = DynamicUserGroupResponseFactory.from_request(test_data)

        self.mock_scm.post.return_value = mock_response  # noqa
        created_object = self.client.create(test_data)

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/dynamic-user-groups",
            json=test_data,
        )
        assert str(created_object.id) == mock_response["id"]
        assert created_object.name == test_data["name"]
        assert created_object.filter == test_data["filter"]
        assert created_object.folder == test_data["folder"]

    def test_create_http_error_no_response_content(self):
        """Test create method when HTTP error has no response content."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.post.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.create(
                {"name": "test", "filter": "'tag.criticality.high'", "folder": "test"}
            )

    def test_create_http_error_with_response(self):
        """Test that HTTPError with response content triggers proper error handling."""
        test_data = DynamicUserGroupCreateApiFactory.with_folder()

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


class TestDynamicUserGroupGet(TestDynamicUserGroupBase):
    """Tests for retrieving a specific Dynamic User Group object."""

    def test_get_valid_object(self):
        """Test retrieving a specific dynamic user group."""
        mock_response = DynamicUserGroupResponseFactory.with_folder(
            group_id="123e4567-e89b-12d3-a456-426655440000",
            name="test-group",
            folder="Texas",
            filter="'tag.criticality.high'",
        )

        self.mock_scm.get.return_value = mock_response  # noqa
        object_id = mock_response["id"]

        retrieved_object = self.client.get(object_id)

        self.mock_scm.get.assert_called_once_with(  # noqa
            f"/config/objects/v1/dynamic-user-groups/{object_id}"
        )
        assert isinstance(retrieved_object, DynamicUserGroupResponseModel)
        assert str(retrieved_object.id) == mock_response["id"]
        assert retrieved_object.name == mock_response["name"]
        assert retrieved_object.filter == mock_response["filter"]
        assert retrieved_object.folder == mock_response["folder"]

    def test_get_object_not_present_error(self):
        """Test error handling when the dynamic user group is not present."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
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


class TestDynamicUserGroupUpdate(TestDynamicUserGroupBase):
    """Tests for updating Dynamic User Group objects."""

    def test_update_valid_object(self):
        """Test updating a dynamic user group with valid data."""
        update_data = DynamicUserGroupUpdateApiFactory.with_folder()

        # Include a tag in the mock response to avoid validation error
        mock_response = DynamicUserGroupResponseFactory.from_request(update_data)
        mock_response["tag"] = ["test-tag"]  # Add tag to avoid validation error
        self.mock_scm.put.return_value = mock_response  # noqa

        updated_object = self.client.update(update_data)

        self.mock_scm.put.assert_called_once()  # noqa
        call_args = self.mock_scm.put.call_args  # noqa
        assert call_args[0][0] == f"/config/objects/v1/dynamic-user-groups/{update_data.id}"

        payload = call_args[1]["json"]
        assert payload["name"] == "updated_group"
        assert payload["filter"] == "'tag.criticality.medium'"

        assert isinstance(updated_object, DynamicUserGroupResponseModel)
        assert str(updated_object.id) == str(
            mock_response["id"]
        )  # Convert both to string for comparison
        assert updated_object.name == mock_response["name"]
        assert updated_object.filter == mock_response["filter"]
        assert updated_object.tag == ["test-tag"]

    def test_update_malformed_command_error(self):
        """Test error handling when update fails due to malformed command."""
        update_data = DynamicUserGroupUpdateApiFactory.with_folder()

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

    def test_update_http_error_no_response_content(self):
        """Test update method when HTTP error has no response content."""
        update_data = DynamicUserGroupUpdateApiFactory.with_folder()

        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.put.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.update(update_data)


class TestDynamicUserGroupDelete(TestDynamicUserGroupBase):
    """Tests for deleting Dynamic User Group objects."""

    def test_delete_success(self):
        """Test successful deletion of a dynamic user group."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.return_value = None  # noqa

        self.client.delete(object_id)

        self.mock_scm.delete.assert_called_once_with(  # noqa
            f"/config/objects/v1/dynamic-user-groups/{object_id}"
        )

    def test_delete_object_not_present_error(self):
        """Test error handling when the dynamic user group to delete is not present."""
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


class TestDynamicUserGroupFetch(TestDynamicUserGroupBase):
    """Tests for fetching Dynamic User Group objects by name."""

    def test_fetch_valid_object(self):
        """Test retrieving a dynamic user group by its name."""
        mock_response = DynamicUserGroupResponseFactory.with_folder(
            group_id="123e4567-e89b-12d3-a456-426655440000",
            name="test-group",
            folder="Texas",
            filter="'tag.criticality.high'",
            description="Test dynamic user group",
        )

        self.mock_scm.get.return_value = mock_response  # noqa

        fetched_object = self.client.fetch(
            name=mock_response["name"],
            folder=mock_response["folder"],
        )

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/dynamic-user-groups",
            params={
                "folder": mock_response["folder"],
                "name": mock_response["name"],
            },
        )

        assert isinstance(fetched_object, DynamicUserGroupResponseModel)
        assert str(fetched_object.id) == mock_response["id"]
        assert fetched_object.name == mock_response["name"]
        assert fetched_object.filter == mock_response["filter"]
        assert fetched_object.description == mock_response["description"]
        assert fetched_object.folder == mock_response["folder"]

    def test_fetch_empty_name_error(self):
        """Test fetching with an empty name parameter."""
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="", folder="Texas")

        error_msg = str(exc_info.value)
        assert (
            "{'field': 'name', 'error': '\"name\" is not allowed to be empty'} - HTTP error: 400 - API error: E003"
            in error_msg
        )

    def test_fetch_empty_folder_error(self):
        """Test fetching with an empty folder parameter."""
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="test-group", folder="")

        error_msg = str(exc_info.value)
        assert (
            "{'field': 'folder', 'error': '\"folder\" is not allowed to be empty'} - HTTP error: 400 - API error: E003"
            in error_msg
        )

    def test_fetch_no_container_provided_error(self):
        """Test that InvalidObjectError is raised when no container parameter is provided."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-group")

        error_msg = str(exc_info.value)
        assert "HTTP error: 400 - API error: E003" in error_msg

    def test_fetch_multiple_containers_provided_error(self):
        """Test that InvalidObjectError is raised when multiple container parameters are provided."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(
                name="test-group",
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
            self.client.fetch(name="test-group", folder="Texas")

    def test_fetch_invalid_response_type_error(self):
        """Test that InvalidObjectError is raised when the response is not a dictionary."""
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-group", folder="Texas")

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        assert error.error_code == "E003"
        assert error.http_status_code == 500
        assert "HTTP error: 500 - API error: E003" in str(error)

    def test_fetch_missing_id_field_error(self):
        """Test that InvalidObjectError is raised when the response is missing 'id' field."""
        mock_response = {
            "name": "test-group",
            "folder": "Texas",
            "filter": "'tag.criticality.high'",
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-group", folder="Texas")

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        assert error.error_code == "E003"
        assert error.http_status_code == 500
        assert "HTTP error: 500 - API error: E003" in str(error)

    def test_fetch_error_handler(self):
        """Test that ErrorHandler.raise_for_error is called with appropriate arguments."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.fetch(name="test-group", folder="Texas")
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "An internal error occurred"
        assert error_response["_errors"][0]["details"]["errorType"] == "Internal Error"


# -------------------- End of Test Classes --------------------
