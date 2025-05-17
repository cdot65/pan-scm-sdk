"""Test module for Address Group configuration service.

This module contains unit tests for the Address Group configuration service and its related models.
"""
# tests/scm/config/objects/test_address_group.py

# Standard library imports
from unittest.mock import MagicMock
import uuid

# External libraries
import pytest
from requests.exceptions import HTTPError

# Local SDK imports
from scm.config.objects import AddressGroup
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.objects import AddressGroupResponseModel
from tests.factories import (
    AddressGroupCreateApiFactory,
    AddressGroupResponseFactory,
    AddressGroupUpdateApiFactory,
)
from tests.utils import raise_mock_http_error


@pytest.mark.usefixtures("load_env")
class TestAddressGroupBase:
    """Base class for Address Group tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm  # noqa
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = AddressGroup(self.mock_scm, max_limit=5000)  # noqa
        yield
        # Reset mock methods after each test
        self.mock_scm.get.reset_mock()
        self.mock_scm.post.reset_mock()
        self.mock_scm.put.reset_mock()
        self.mock_scm.delete.reset_mock()


# -------------------- Unit Tests --------------------


@pytest.mark.unit
class TestAddressGroupMaxLimit(TestAddressGroupBase):
    """Tests for max_limit functionality."""

    def test_default_max_limit(self):
        """Test that default max_limit is set correctly."""
        client = AddressGroup(self.mock_scm)  # noqa
        assert client.max_limit == AddressGroup.DEFAULT_MAX_LIMIT
        assert client.max_limit == 2500

    def test_custom_max_limit(self):
        """Test setting a custom max_limit."""
        client = AddressGroup(self.mock_scm, max_limit=1000)  # noqa
        assert client.max_limit == 1000

    def test_max_limit_setter(self):
        """Test the max_limit property setter."""
        client = AddressGroup(self.mock_scm)  # noqa
        client.max_limit = 3000
        assert client.max_limit == 3000

    def test_invalid_max_limit_type(self):
        """Test that invalid max_limit type raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            AddressGroup(self.mock_scm, max_limit="invalid")  # noqa
        assert "{'error': 'Invalid max_limit type'} - HTTP error: 400 - API error: E003" in str(
            exc_info.value
        )

    def test_max_limit_too_low(self):
        """Test that max_limit below 1 raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            AddressGroup(self.mock_scm, max_limit=0)  # noqa
        assert "{'error': 'Invalid max_limit value'} - HTTP error: 400 - API error: E003" in str(
            exc_info.value
        )

    def test_max_limit_too_high(self):
        """Test that max_limit above ABSOLUTE_MAX_LIMIT raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            AddressGroup(self.mock_scm, max_limit=6000)  # noqa
        assert "max_limit exceeds maximum allowed value" in str(exc_info.value)


# -------------------- Integration Tests --------------------


@pytest.mark.integration
class TestAddressGroupList(TestAddressGroupBase):
    """Tests for listing Address Group objects."""

    def test_list_valid(self):
        """Test listing all address groups successfully."""
        mock_response = {
            "data": [
                AddressGroupResponseFactory.with_static().model_dump(),
                AddressGroupResponseFactory.with_dynamic().model_dump(),
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        existing_objects = self.client.list(folder="Texas")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/address-groups",
            params={
                "limit": 5000,
                "folder": "Texas",
                "offset": 0,
            },
        )
        assert isinstance(existing_objects, list)
        assert isinstance(existing_objects[0], AddressGroupResponseModel)
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

    def test_list_filters_with_valid_data(self):
        """Test the filtering functionality with different types of objects."""
        mock_address_groups = [
            AddressGroupResponseModel(
                id=uuid.uuid4(),
                name="group1",
                folder="test",
                static=["address1", "address2"],
                tag=["tag1", "tag2"],
            ),
            AddressGroupResponseModel(
                id=uuid.uuid4(),
                name="group2",
                folder="test",
                dynamic={"filter": "tag = 'test'"},
                tag=["tag2"],
            ),
            AddressGroupResponseModel(
                id=uuid.uuid4(),
                name="group3",
                folder="test",
                static=["address3", "address4"],
                tag=["tag3"],
            ),
        ]

        # Test types filter
        filters = {"types": ["static"]}
        filtered = self.client._apply_filters(mock_address_groups, filters)
        assert len(filtered) == 2
        assert set(obj.name for obj in filtered) == {"group1", "group3"}

        # Test values filter
        filters = {"values": ["address2"]}
        filtered = self.client._apply_filters(mock_address_groups, filters)
        assert len(filtered) == 1
        assert filtered[0].name == "group1"

        # Test tags filter
        filters = {"tags": ["tag2"]}
        filtered = self.client._apply_filters(mock_address_groups, filters)
        assert len(filtered) == 2
        assert set(obj.name for obj in filtered) == {"group1", "group2"}

    def test_list_filters_lists_empty(self):
        """Test behavior with empty filter lists."""
        mock_response = {
            "data": [
                AddressGroupResponseFactory.with_static().model_dump(),
                AddressGroupResponseFactory.with_dynamic().model_dump(),
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Empty lists should result in no matches
        filtered_objects = self.client.list(
            folder="Texas",
            types=[],
        )
        assert len(filtered_objects) == 0

        filtered_objects = self.client.list(
            folder="Texas",
            values=[],
        )
        assert len(filtered_objects) == 0

        filtered_objects = self.client.list(
            folder="Texas",
            tags=[],
        )
        assert len(filtered_objects) == 0

    def test_list_filters_types_validation(self):
        """Test validation of 'types' filter specifically."""
        mock_address_groups = []

        # Test with string instead of list
        invalid_filters = {"types": "type1"}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_address_groups, invalid_filters)

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        assert error.error_code == "E003"
        assert "{'errorType': 'Invalid Object'}" in str(error)

    def test_list_filters_tags_validation(self):
        """Test validation of 'tags' filter specifically."""
        mock_address_groups = []

        # Test with string instead of list
        invalid_filters = {"tags": "tag1"}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_address_groups, invalid_filters)

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        assert error.error_code == "E003"
        assert "{'errorType': 'Invalid Object'}" in str(error)

    def test_list_filters_values_validation(self):
        """Test validation of 'values' filter specifically."""
        mock_address_groups = []

        # Test with string instead of list
        invalid_filters = {"values": "value1"}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_address_groups, invalid_filters)

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

    # -------------------- New Tests for exact_match and Exclusions --------------------

    def test_list_exact_match(self):
        """Test that exact_match=True returns only address groups that match the container exactly."""
        mock_response = {
            "data": [
                AddressGroupResponseFactory.with_static(
                    name="group_in_texas", folder="Texas", static=["address1"]
                ).model_dump(),
                AddressGroupResponseFactory.with_static(
                    name="group_in_all", folder="All", static=["address2"]
                ).model_dump(),
            ]
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        filtered = self.client.list(folder="Texas", exact_match=True)
        # exact_match should exclude the one from "All"
        assert len(filtered) == 1
        assert filtered[0].folder == "Texas"
        assert filtered[0].name == "group_in_texas"

    def test_list_exclude_folders(self):
        """Test that exclude_folders removes address groups from those folders."""
        mock_response = {
            "data": [
                AddressGroupResponseFactory.with_static(
                    name="group_in_texas", folder="Texas", static=["address1"]
                ).model_dump(),
                AddressGroupResponseFactory.with_static(
                    name="group_in_all", folder="All", static=["address2"]
                ).model_dump(),
            ]
        }
        self.mock_scm.get.return_value = mock_response

        filtered = self.client.list(folder="Texas", exclude_folders=["All"])
        assert len(filtered) == 1
        assert all(g.folder != "All" for g in filtered)

    def test_list_exclude_snippets(self):
        """Test that exclude_snippets removes address groups with those snippets."""
        mock_response = {
            "data": [
                AddressGroupResponseFactory.with_static(
                    name="group_default_snippet",
                    folder="Texas",
                    snippet="default",
                    static=["address1"],
                ).model_dump(),
                AddressGroupResponseFactory.with_static(
                    name="group_special_snippet",
                    folder="Texas",
                    snippet="special",
                    static=["address2"],
                ).model_dump(),
            ]
        }
        self.mock_scm.get.return_value = mock_response

        filtered = self.client.list(folder="Texas", exclude_snippets=["default"])
        assert len(filtered) == 1
        assert all(g.snippet != "default" for g in filtered)

    def test_list_exclude_devices(self):
        """Test that exclude_devices removes address groups from those devices."""
        mock_response = {
            "data": [
                AddressGroupResponseFactory.with_static(
                    name="group_deviceA",
                    folder="Texas",
                    device="DeviceA",
                    static=["address1"],
                ).model_dump(),
                AddressGroupResponseFactory.with_static(
                    name="group_deviceB",
                    folder="Texas",
                    device="DeviceB",
                    static=["address2"],
                ).model_dump(),
            ]
        }
        self.mock_scm.get.return_value = mock_response

        filtered = self.client.list(folder="Texas", exclude_devices=["DeviceA"])
        assert len(filtered) == 1
        assert all(g.device != "DeviceA" for g in filtered)

    def test_list_exact_match_and_exclusions(self):
        """Test combining exact_match with exclusions."""
        mock_response = {
            "data": [
                AddressGroupResponseFactory.with_static(
                    name="group_texas_default_deviceA",
                    folder="Texas",
                    snippet="default",
                    device="DeviceA",
                    static=["addr1"],
                ).model_dump(),
                AddressGroupResponseFactory.with_static(
                    name="group_texas_special_deviceB",
                    folder="Texas",
                    snippet="special",
                    device="DeviceB",
                    static=["addr2"],
                ).model_dump(),
                AddressGroupResponseFactory.with_static(
                    name="group_all_default_deviceA",
                    folder="All",
                    snippet="default",
                    device="DeviceA",
                    static=["addr3"],
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

        # Only group_texas_special_deviceB should remain after all filters
        assert len(filtered) == 1
        obj = filtered[0]
        assert obj.folder == "Texas"
        assert obj.snippet != "default"
        assert obj.device != "DeviceA"

    def test_list_pagination_multiple_pages(self):
        """Test pagination with multiple pages of results."""
        client = AddressGroup(self.mock_scm, max_limit=2500)  # noqa

        # Create test data for three pages
        first_page = [
            AddressGroupResponseFactory.with_static(
                name=f"group-page1-{i}", folder="Texas", static=[f"address{i}"]
            ).model_dump()
            for i in range(2500)
        ]

        second_page = [
            AddressGroupResponseFactory.with_static(
                name=f"group-page2-{i}", folder="Texas", static=[f"address{i}"]
            ).model_dump()
            for i in range(2500)
        ]

        third_page = [
            AddressGroupResponseFactory.with_static(
                name=f"group-page3-{i}", folder="Texas", static=[f"address{i}"]
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
        assert isinstance(results[0], AddressGroupResponseModel)
        assert all(isinstance(obj, AddressGroupResponseModel) for obj in results)

        # Verify the number of API calls
        assert self.mock_scm.get.call_count == 4  # noqa # Three pages + one final check

        # Verify first API call parameters
        self.mock_scm.get.assert_any_call(  # noqa
            "/config/objects/v1/address-groups",
            params={"folder": "Texas", "limit": 2500, "offset": 0},
        )

        # Verify second API call parameters (offset should be 2500)
        self.mock_scm.get.assert_any_call(  # noqa
            "/config/objects/v1/address-groups",
            params={"folder": "Texas", "limit": 2500, "offset": 2500},
        )

        # Verify third API call parameters (offset should be 5000)
        self.mock_scm.get.assert_any_call(  # noqa
            "/config/objects/v1/address-groups",
            params={"folder": "Texas", "limit": 2500, "offset": 5000},
        )

        # Verify content from each page is present
        assert results[0].name == "group-page1-0"
        assert results[2500].name == "group-page2-0"
        assert results[5000].name == "group-page3-0"


@pytest.mark.integration
class TestAddressGroupCreate(TestAddressGroupBase):
    """Integration tests for creating Address Group objects."""

    def test_create_valid_type_static(self):
        """Test creating an address group with static type."""
        test_object = AddressGroupCreateApiFactory.with_static()
        mock_response = AddressGroupResponseFactory.from_request(test_object)

        self.mock_scm.post.return_value = mock_response.model_dump()  # noqa
        created_object = self.client.create(test_object.model_dump(exclude_unset=True))

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/address-groups",
            json=test_object.model_dump(exclude_unset=True),
        )
        assert str(created_object.id) == str(mock_response.id)
        assert created_object.name == test_object.name
        assert created_object.static == test_object.static
        assert created_object.folder == test_object.folder

    def test_create_valid_type_dynamic(self):
        """Test creating an address group with dynamic type."""
        test_object = AddressGroupCreateApiFactory.with_dynamic()
        mock_response = AddressGroupResponseFactory.from_request(test_object)

        self.mock_scm.post.return_value = mock_response.model_dump()  # noqa
        created_object = self.client.create(test_object.model_dump(exclude_unset=True))

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/address-groups",
            json=test_object.model_dump(exclude_unset=True),
        )
        assert str(created_object.id) == str(mock_response.id)
        assert created_object.name == test_object.name
        assert created_object.dynamic == test_object.dynamic
        assert created_object.folder == test_object.folder


@pytest.mark.integration
class TestAddressGroupGet(TestAddressGroupBase):
    """Integration tests for retrieving a specific Address Group object."""

    def test_get_valid_object(self):
        """Test retrieving a specific address group."""
        mock_response = AddressGroupResponseFactory.with_static(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-group",
            folder="Texas",
            static=["address1", "address2"],
        ).model_dump()

        self.mock_scm.get.return_value = mock_response  # noqa
        object_id = mock_response["id"]

        retrieved_object = self.client.get(object_id)

        self.mock_scm.get.assert_called_once_with(  # noqa
            f"/config/objects/v1/address-groups/{object_id}"
        )
        assert isinstance(retrieved_object, AddressGroupResponseModel)
        assert retrieved_object.id == mock_response["id"]
        assert retrieved_object.name == mock_response["name"]
        assert retrieved_object.static == mock_response["static"]
        assert retrieved_object.folder == mock_response["folder"]


@pytest.mark.integration
class TestAddressGroupUpdate(TestAddressGroupBase):
    """Integration tests for updating Address Group objects."""

    def test_update_valid_object(self):
        """Test updating an address group with valid data."""
        update_data = AddressGroupUpdateApiFactory.with_static(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="updated-group",
            static=["address3", "address4"],
            description="Updated description",
            folder="Texas",
        )

        mock_response = AddressGroupResponseFactory.from_request(update_data)
        self.mock_scm.put.return_value = mock_response.model_dump()  # noqa

        updated_object = self.client.update(update_data)

        self.mock_scm.put.assert_called_once()  # noqa
        call_args = self.mock_scm.put.call_args  # noqa
        assert call_args[0][0] == f"/config/objects/v1/address-groups/{update_data.id}"

        payload = call_args[1]["json"]
        assert payload["name"] == "updated-group"
        assert payload["static"] == ["address3", "address4"]
        assert payload["description"] == "Updated description"
        assert payload["folder"] == "Texas"

        assert isinstance(updated_object, AddressGroupResponseModel)
        assert str(updated_object.id) == str(mock_response.id)
        assert updated_object.name == mock_response.name
        assert updated_object.static == mock_response.static
        assert updated_object.description == mock_response.description
        assert updated_object.folder == mock_response.folder


@pytest.mark.integration
class TestAddressGroupDelete(TestAddressGroupBase):
    """Integration tests for deleting Address Group objects."""

    def test_delete_success(self):
        """Test successful deletion of an address group."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.return_value = None  # noqa

        self.client.delete(object_id)

        self.mock_scm.delete.assert_called_once_with(  # noqa
            f"/config/objects/v1/address-groups/{object_id}"
        )


@pytest.mark.integration
class TestAddressGroupFetch(TestAddressGroupBase):
    """Integration tests for fetching Address Group objects by name."""

    def test_fetch_valid_object(self):
        """Test retrieving an address group by its name."""
        mock_response_model = AddressGroupResponseFactory.with_static(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-group",
            folder="Texas",
            static=["address1", "address2"],
            description="Test address group",
        )
        mock_response_data = mock_response_model.model_dump()

        self.mock_scm.get.return_value = mock_response_data  # noqa

        fetched_object = self.client.fetch(
            name=mock_response_model.name,
            folder=mock_response_model.folder,
        )

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/address-groups",
            params={
                "folder": mock_response_model.folder,
                "name": mock_response_model.name,
            },
        )

        assert isinstance(fetched_object, AddressGroupResponseModel)
        assert str(fetched_object.id) == str(mock_response_model.id)
        assert fetched_object.name == mock_response_model.name
        assert fetched_object.static == mock_response_model.static
        assert fetched_object.description == mock_response_model.description
        assert fetched_object.folder == mock_response_model.folder

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
            "static": ["address1", "address2"],
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


# -------------------- Mock Tests --------------------


@pytest.mark.mock
class TestAddressGroupCreateErrorHandling(TestAddressGroupBase):
    """Mock tests for error handling in create operations."""

    def test_create_http_error_no_response_content(self):
        """Test create method when HTTP error has no response content."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.post.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.create(
                {"name": "test", "static": ["address1", "address2"], "folder": "test"}
            )

    def test_create_http_error_with_response(self):
        """Test that HTTPError with response content triggers proper error handling."""
        test_data = {
            "name": "test-address-group",
            "folder": "Texas",
            "static": ["address1", "address2"],
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


@pytest.mark.mock
class TestAddressGroupGetErrorHandling(TestAddressGroupBase):
    """Mock tests for error handling in get operations."""

    def test_get_object_not_present_error(self):
        """Test error handling when the address group is not present."""
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


@pytest.mark.mock
class TestAddressGroupUpdateErrorHandling(TestAddressGroupBase):
    """Mock tests for error handling in update operations."""

    def test_update_malformed_command_error(self):
        """Test error handling when update fails due to malformed command."""
        update_data = AddressGroupUpdateApiFactory.with_static(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-group",
            folder="Texas",
            static=["address1", "address2"],
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

    def test_update_http_error_no_response_content(self):
        """Test update method when HTTP error has no response content."""
        update_data = AddressGroupUpdateApiFactory.with_static(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test",
            static=["address1", "address2"],
        )

        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.put.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.update(update_data)


@pytest.mark.mock
class TestAddressGroupDeleteErrorHandling(TestAddressGroupBase):
    """Mock tests for error handling in delete operations."""

    def test_delete_object_not_present_error(self):
        """Test error handling when the address group to delete is not present."""
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


# -------------------- Parametrized Tests --------------------


@pytest.mark.parametrized
class TestAddressGroupParametrized(TestAddressGroupBase):
    """Parametrized tests for Address Group functionality."""

    @pytest.mark.parametrize(
        "create_factory,group_type,expected_value",
        [
            (AddressGroupCreateApiFactory.with_static, "static", ["address1"]),
            (AddressGroupCreateApiFactory.with_dynamic, "dynamic", {"filter": "tag = 'tag1'"}),
        ],
    )
    def test_create_address_group_types(self, create_factory, group_type, expected_value):
        """Test creating address groups with different types."""
        test_object = create_factory()

        # Ensure expected value is present in the object
        if group_type == "static":
            test_object.static = expected_value

        mock_response = AddressGroupResponseFactory.from_request(test_object)

        self.mock_scm.post.return_value = mock_response.model_dump()  # noqa
        created_object = self.client.create(test_object.model_dump(exclude_unset=True))

        # Verify the group type attribute exists and matches the expected pattern
        if group_type == "static":
            assert getattr(created_object, group_type) == expected_value
        else:
            # For dynamic objects, just check that dynamic attribute exists and is a DynamicFilter
            assert hasattr(created_object, group_type)
            assert created_object.dynamic is not None


# -------------------- Functional Tests --------------------


@pytest.mark.functional
def test_address_group_lifecycle(mock_scm):
    """Functional test for complete address group object lifecycle (CRUD)."""
    # Setup
    mock_scm.get = MagicMock()
    mock_scm.post = MagicMock()
    mock_scm.put = MagicMock()
    mock_scm.delete = MagicMock()
    client = AddressGroup(mock_scm, max_limit=5000)

    # 1. Create address group
    create_data = {
        "name": "test-address-group-lifecycle",
        "folder": "Texas",
        "static": ["address1", "address2"],
        "description": "Lifecycle test address group",
    }

    group_id = "123e4567-e89b-12d3-a456-426655440000"
    mock_create_response = {
        "id": group_id,
        "name": "test-address-group-lifecycle",
        "folder": "Texas",
        "static": ["address1", "address2"],
        "description": "Lifecycle test address group",
    }
    mock_scm.post.return_value = mock_create_response

    created = client.create(create_data)
    assert str(created.id) == group_id
    assert created.name == "test-address-group-lifecycle"

    # 2. List address groups
    mock_list_response = {"data": [mock_create_response], "offset": 0, "total": 1, "limit": 100}
    mock_scm.get.return_value = mock_list_response

    groups = client.list(folder="Texas")
    assert len(groups) == 1
    assert str(groups[0].id) == group_id

    # 3. Get specific address group
    mock_scm.get.return_value = mock_create_response

    retrieved = client.get(group_id)
    assert str(retrieved.id) == group_id

    # 4. Update address group
    update_data = AddressGroupUpdateApiFactory.with_static(
        id=group_id,
        name="test-address-group-lifecycle",
        folder="Texas",
        static=["address1", "address2", "address3"],
        description="Updated lifecycle test address group",
    )

    mock_update_response = {
        "id": group_id,
        "name": "test-address-group-lifecycle",
        "folder": "Texas",
        "static": ["address1", "address2", "address3"],
        "description": "Updated lifecycle test address group",
    }
    mock_scm.put.return_value = mock_update_response

    updated = client.update(update_data)
    assert updated.description == "Updated lifecycle test address group"
    assert updated.static == ["address1", "address2", "address3"]

    # 5. Delete address group
    mock_scm.delete.return_value = None

    # Should not raise any exceptions
    client.delete(group_id)
    mock_scm.delete.assert_called_once_with(f"/config/objects/v1/address-groups/{group_id}")


# -------------------- End of Test Classes --------------------
