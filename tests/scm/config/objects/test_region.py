# tests/scm/config/objects/test_region.py

# Standard library imports
from unittest.mock import MagicMock

# External libraries
import pytest
from requests.exceptions import HTTPError

# Local SDK imports
from scm.config.objects import Region
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.objects import RegionResponseModel
from tests.factories.objects.region import (
    RegionCreateApiFactory,
    RegionResponseFactory,
    RegionUpdateApiFactory,
)
from tests.utils import raise_mock_http_error


@pytest.mark.usefixtures("load_env")
class TestRegionBase:
    """Base class for Region tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = Region(self.mock_scm, max_limit=5000)

    # -------------------- Test Classes Grouped by Functionality --------------------


class TestRegionMaxLimit(TestRegionBase):
    """Tests for max_limit functionality."""

    def test_default_max_limit(self):
        """Test that default max_limit is set correctly."""
        client = Region(self.mock_scm)
        assert client.max_limit == Region.DEFAULT_MAX_LIMIT
        assert client.max_limit == 2500

    def test_custom_max_limit(self):
        """Test setting a custom max_limit."""
        client = Region(self.mock_scm, max_limit=1000)
        assert client.max_limit == 1000

    def test_max_limit_setter(self):
        """Test the max_limit property setter."""
        client = Region(self.mock_scm)
        client.max_limit = 3000
        assert client.max_limit == 3000

    def test_invalid_max_limit_type(self):
        """Test that invalid max_limit type raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            Region(self.mock_scm, max_limit="invalid")
        assert "{'error': 'Invalid max_limit type'} - HTTP error: 400 - API error: E003" in str(
            exc_info.value
        )

    def test_max_limit_too_low(self):
        """Test that max_limit below 1 raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            Region(self.mock_scm, max_limit=0)
        assert "{'error': 'Invalid max_limit value'} - HTTP error: 400 - API error: E003" in str(
            exc_info.value
        )

    def test_max_limit_too_high(self):
        """Test that max_limit above ABSOLUTE_MAX_LIMIT raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            Region(self.mock_scm, max_limit=6000)
        assert "max_limit exceeds maximum allowed value" in str(exc_info.value)


class TestRegionList(TestRegionBase):
    """Tests for listing Region objects."""

    def test_list_valid(self):
        """**Objective:** Test listing all objects.
        """
        mock_response = {
            "data": [
                RegionResponseFactory(
                    name="North America Region",
                    folder="Global",
                    geo_location={"latitude": 37.7749, "longitude": -122.4194},
                    address=["192.168.1.0/24", "10.0.0.0/8"],
                ).model_dump(),
                RegionResponseFactory(
                    name="Europe Region",
                    folder="Global",
                    geo_location={"latitude": 51.5074, "longitude": -0.1278},
                    address=["172.16.0.0/16"],
                ).model_dump(),
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response
        existing_objects = self.client.list(folder="Global")

        self.mock_scm.get.assert_called_once_with(
            "/config/objects/v1/regions",
            params={
                "folder": "Global",
                "limit": 5000,
                "offset": 0,
            },
        )
        assert isinstance(existing_objects, list)
        assert isinstance(existing_objects[0], RegionResponseModel)
        assert len(existing_objects) == 2
        assert existing_objects[0].name == "North America Region"

    def test_list_folder_empty_error(self):
        """Test that empty folder raises appropriate error."""
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=400,
            error_code="E003",
            message='"folder" is not allowed to be empty',
            error_type="Missing Query Parameter",
        )

        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.list(folder="")

        error_msg = str(exc_info.value)
        assert (
            "{'field': 'folder', 'error': '\"folder\" is not allowed to be empty'} - HTTP error: 400 - API error: E003"
            in error_msg
        )

    def test_list_folder_nonexistent_error(self):
        """Test error handling in list operation."""
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=404,
            error_code="API_I00013",
            message="Listing failed",
            error_type="Operation Impossible",
        )

        with pytest.raises(HTTPError):
            self.client.list(folder="NonexistentFolder")

    def test_list_container_missing_error(self):
        """Test that InvalidObjectError is raised when no container parameter is provided.
        """
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=400,
            error_code="E003",
            message="Exactly one of 'folder', 'snippet', or 'device' must be provided.",
            error_type="Invalid Object",
        )

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list()
        error_msg = str(exc_info.value)
        assert "HTTP error: 400 - API error: E003" in error_msg

    def test_list_container_multiple_error(self):
        """Test validation of container parameters."""
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=400,
            error_code="E003",
            message="Multiple container types provided",
            error_type="Invalid Object",
        )

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="folder1", snippet="snippet1")

        error_msg = str(exc_info.value)
        assert "HTTP error: 400 - API error: E003" in error_msg

    def test_list_filters_valid(self):
        """Test that filters are properly added to parameters."""
        filters = {
            "geo_location": {
                "latitude": {"min": 30, "max": 40},
                "longitude": {"min": -130, "max": -120},
            },
            "addresses": ["10.0.0.0/8", "192.168.1.0/24"],
        }

        mock_response = {"data": []}
        self.mock_scm.get.return_value = mock_response

        self.client.list(folder="Global", **filters)

        self.mock_scm.get.assert_called_once_with(
            "/config/objects/v1/regions",
            params={
                "folder": "Global",
                "limit": 5000,
                "offset": 0,
            },
        )

    def test_list_filters_geo_location(self):
        """Test geo_location filter in list method."""
        mock_response = {
            "data": [
                RegionResponseFactory(
                    name="North America Region",
                    folder="Global",
                    geo_location={
                        "latitude": 37.7749,
                        "longitude": -122.4194,
                    },
                    address=["10.0.0.0/8"],
                ).model_dump(),
                RegionResponseFactory(
                    name="Europe Region",
                    folder="Global",
                    geo_location={
                        "latitude": 51.5074,
                        "longitude": -0.1278,
                    },
                    address=["172.16.0.0/16"],
                ).model_dump(),
            ]
        }
        self.mock_scm.get.return_value = mock_response

        # Filter for only North America region by latitude
        regions = self.client.list(
            folder="Global",
            geo_location={
                "latitude": {"min": 30, "max": 40},
            },
        )
        assert len(regions) == 1
        assert regions[0].name == "North America Region"

        # Filter for only Europe region by longitude
        regions = self.client.list(
            folder="Global",
            geo_location={
                "longitude": {"min": -5, "max": 5},
            },
        )
        assert len(regions) == 1
        assert regions[0].name == "Europe Region"

        # Filter for no regions (no match)
        regions = self.client.list(
            folder="Global",
            geo_location={
                "latitude": {"min": 0, "max": 10},
                "longitude": {"min": 0, "max": 10},
            },
        )
        assert len(regions) == 0

    def test_list_filters_geo_location_validation(self):
        """Test validation of 'geo_location' filter specifically."""
        mock_addresses = []

        # Test with string instead of dict
        invalid_filters = {"geo_location": "invalid"}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_addresses, invalid_filters)

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        assert error.error_code == "E003"
        assert "{'errorType': 'Invalid Object'}" in str(error)

    def test_list_filters_addresses(self):
        """Test addresses filter in list method."""
        mock_response = {
            "data": [
                RegionResponseFactory(
                    name="Region_10",
                    folder="Global",
                    address=["10.0.0.0/8"],
                ).model_dump(),
                RegionResponseFactory(
                    name="Region_192",
                    folder="Global",
                    address=["192.168.1.0/24"],
                ).model_dump(),
            ]
        }
        self.mock_scm.get.return_value = mock_response

        # Filter for specific address
        regions = self.client.list(folder="Global", addresses=["10.0.0.0/8"])
        assert len(regions) == 1
        assert regions[0].name == "Region_10"

    def test_list_filters_addresses_validation(self):
        """Test validation of 'addresses' filter specifically."""
        mock_regions = []

        # Test with string instead of list
        invalid_filters = {"addresses": "10.0.0.0/8"}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_regions, invalid_filters)

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        assert error.error_code == "E003"
        assert "{'errorType': 'Invalid Object'}" in str(error)

        # Test with dict instead of list
        invalid_filters = {"addresses": {"address": "10.0.0.0/8"}}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_regions, invalid_filters)

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        assert error.error_code == "E003"
        assert "{'errorType': 'Invalid Object'}" in str(error)

    def test_list_filters_combinations(self):
        """Test different combinations of valid filters."""
        mock_response = {
            "data": [
                RegionResponseFactory(
                    name="West Coast US",
                    folder="Global",
                    geo_location={
                        "latitude": 37.7749,
                        "longitude": -122.4194,
                    },
                    address=["10.0.0.0/8", "192.168.1.0/24"],
                ).model_dump(),
                RegionResponseFactory(
                    name="East Coast US",
                    folder="Global",
                    geo_location={
                        "latitude": 40.7128,
                        "longitude": -74.0060,
                    },
                    address=["172.16.0.0/16"],
                ).model_dump(),
                RegionResponseFactory(
                    name="Europe",
                    folder="Global",
                    geo_location={
                        "latitude": 51.5074,
                        "longitude": -0.1278,
                    },
                    address=["10.0.0.0/8"],
                ).model_dump(),
            ]
        }
        self.mock_scm.get.return_value = mock_response

        # Test combining geo_location and addresses filters
        filtered_objects = self.client.list(
            folder="Global",
            geo_location={
                "latitude": {"min": 30, "max": 45},
            },
            addresses=["10.0.0.0/8"],
        )
        assert len(filtered_objects) == 1
        assert filtered_objects[0].name == "West Coast US"

    def test_list_response_invalid_format(self):
        """Test that InvalidObjectError is raised when the response is not a dictionary.
        """
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Global")

        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500
        assert "HTTP error: 500 - API error: E003" in str(exc_info.value)

    def test_list_response_invalid_data_field_missing(self):
        """Test that InvalidObjectError is raised when API returns response with missing data field.
        """
        self.mock_scm.get.return_value = {"wrong_field": "value"}

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Global")

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        assert error.error_code == "E003"
        assert error.http_status_code == 500
        assert "HTTP error: 500 - API error: E003" in str(exc_info.value)

    def test_list_response_invalid_data_field_type(self):
        """Test that InvalidObjectError is raised when API returns non-list data field.
        """
        self.mock_scm.get.return_value = {"data": "not a list"}

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Global")

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        assert error.error_code == "E003"
        assert error.http_status_code == 500

    def test_list_response_no_content(self):
        """Test that an HTTPError without response content in list() re-raises the exception."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_http_error

        with pytest.raises(HTTPError):
            self.client.list(folder="Global")

    def test_list_server_error(self):
        """Test generic exception handling in list method."""
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.list(folder="Global")
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "An internal error occurred"
        assert error_response["_errors"][0]["details"]["errorType"] == "Internal Error"

    def test_list_pagination_multiple_pages(self):
        """Test that the list method correctly aggregates data from multiple pages.
        Using a custom client with max_limit=2500 to test pagination.
        """
        client = Region(self.mock_scm, max_limit=2500)

        # Create test data
        total_objects = 7500
        first_batch = [RegionResponseFactory(name=f"Region_{i}") for i in range(2500)]
        second_batch = [RegionResponseFactory(name=f"Region_{i}") for i in range(2500, 5000)]
        third_batch = [RegionResponseFactory(name=f"Region_{i}") for i in range(5000, 7500)]

        # Set up mock responses
        mock_responses = [
            {"data": [obj.model_dump() for obj in first_batch]},
            {"data": [obj.model_dump() for obj in second_batch]},
            {"data": [obj.model_dump() for obj in third_batch]},
            {"data": []},
        ]
        self.mock_scm.get.side_effect = mock_responses

        # Get results
        results = client.list(folder="Global")

        # Verify results
        assert len(results) == total_objects
        assert isinstance(results[0], RegionResponseModel)
        assert all(isinstance(r, RegionResponseModel) for r in results)

        # Verify the number of API calls
        assert self.mock_scm.get.call_count == 4

        # Verify first API call used correct parameters
        self.mock_scm.get.assert_any_call(
            "/config/objects/v1/regions",
            params={
                "folder": "Global",
                "limit": 2500,
                "offset": 0,
            },
        )

    def test_list_with_invalid_items(self):
        """Test that the list method correctly handles invalid items in the response.
        This tests the logging code in Region.list() that handles invalid items.
        """
        # Create mock response with some invalid items (missing ID)
        mock_response = {
            "data": [
                # Valid items
                RegionResponseFactory(
                    name="Valid Region 1",
                    folder="Global",
                ).model_dump(),
                RegionResponseFactory(
                    name="Valid Region 2",
                    folder="Global",
                ).model_dump(),
                # Invalid items (no ID)
                {"name": "Invalid Region 1", "folder": "Global"},
                {"name": "Invalid Region 2", "folder": "Global"},
                {"name": "Invalid Region 3", "folder": "Global"},
                {"name": "Invalid Region 4", "folder": "Global"},
            ]
        }

        self.mock_scm.get.return_value = mock_response

        # Get results - should only include valid items
        results = self.client.list(folder="Global")

        # Verify results
        assert len(results) == 2
        assert all(isinstance(r, RegionResponseModel) for r in results)
        assert results[0].name == "Valid Region 1"
        assert results[1].name == "Valid Region 2"

    # -------------------- New Tests for exact_match and Exclusions --------------------

    def test_list_exact_match(self):
        """Test that exact_match=True returns only objects that match the container exactly.
        """
        mock_response = {
            "data": [
                RegionResponseFactory(
                    name="region_in_global",
                    folder="Global",
                ).model_dump(),
                RegionResponseFactory(
                    name="region_in_shared",
                    folder="Shared",
                ).model_dump(),
            ]
        }

        self.mock_scm.get.return_value = mock_response

        # exact_match should exclude the one from "Shared"
        filtered = self.client.list(folder="Global", exact_match=True)
        assert len(filtered) == 1
        assert filtered[0].folder == "Global"
        assert filtered[0].name == "region_in_global"

    def test_list_exclude_folders(self):
        """Test that exclude_folders removes objects from those folders.
        """
        mock_response = {
            "data": [
                RegionResponseFactory(
                    name="region_in_global",
                    folder="Global",
                ).model_dump(),
                RegionResponseFactory(
                    name="region_in_shared",
                    folder="Shared",
                ).model_dump(),
            ]
        }
        self.mock_scm.get.return_value = mock_response

        filtered = self.client.list(folder="Global", exclude_folders=["Shared"])
        assert len(filtered) == 1
        assert all(a.folder != "Shared" for a in filtered)

    def test_list_exclude_snippets(self):
        """Test that exclude_snippets removes objects with those snippets.
        """
        mock_response = {
            "data": [
                RegionResponseFactory(
                    name="region_with_default_snippet",
                    folder="Global",
                    snippet="default",
                ).model_dump(),
                RegionResponseFactory(
                    name="region_with_special_snippet",
                    folder="Global",
                    snippet="special",
                ).model_dump(),
            ]
        }
        self.mock_scm.get.return_value = mock_response

        filtered = self.client.list(folder="Global", exclude_snippets=["default"])
        assert len(filtered) == 1
        assert all(a.snippet != "default" for a in filtered)

    def test_list_exclude_devices(self):
        """Test that exclude_devices removes objects with those devices.
        """
        mock_response = {
            "data": [
                {
                    "id": "223e4567-e89b-12d3-a456-426655440000",
                    "name": "region_deviceA",
                    "folder": "Global",
                    "device": "DeviceA",
                },
                {
                    "id": "334e4567-e89b-12d3-a456-426655440000",
                    "name": "region_deviceB",
                    "folder": "Global",
                    "device": "DeviceB",
                },
            ]
        }
        self.mock_scm.get.return_value = mock_response

        filtered = self.client.list(folder="Global", exclude_devices=["DeviceA"])
        assert len(filtered) == 1
        assert all(a.device != "DeviceA" for a in filtered)

    def test_list_exact_match_and_exclusions(self):
        """Test combining exact_match with exclusions.
        """
        mock_response = {
            "data": [
                {
                    "id": "223e4567-e89b-12d3-a456-426655440000",
                    "name": "region_in_global_default",
                    "folder": "Global",
                    "snippet": "default",
                    "device": "DeviceA",
                },
                {
                    "id": "334e4567-e89b-12d3-a456-426655440000",
                    "name": "region_in_global_special",
                    "folder": "Global",
                    "snippet": "special",
                    "device": "DeviceB",
                },
                {
                    "id": "434e4567-e89b-12d3-a456-426655440000",
                    "name": "region_in_shared",
                    "folder": "Shared",
                    "snippet": "default",
                    "device": "DeviceA",
                },
            ]
        }
        self.mock_scm.get.return_value = mock_response

        filtered = self.client.list(
            folder="Global",
            exact_match=True,
            exclude_folders=["Shared"],
            exclude_snippets=["default"],
            exclude_devices=["DeviceA"],
        )
        # Only region_in_global_special should remain
        assert len(filtered) == 1
        obj = filtered[0]
        assert obj.folder == "Global"
        assert obj.snippet != "default"
        assert obj.device != "DeviceA"


class TestRegionCreate(TestRegionBase):
    """Tests for creating Region objects."""

    def test_create_valid(self):
        """Test creating a valid region object."""
        request_data = RegionCreateApiFactory.build_valid()
        response_data = RegionResponseFactory.from_request(request_data)

        self.mock_scm.post.return_value = response_data.model_dump(exclude_none=False)

        # Pass a dictionary for the create method
        request_dict = request_data.model_dump(exclude_none=False)
        created_object = self.client.create(request_dict)

        # From the SCM API docs, description and tag are excluded from the payload
        payload = request_dict.copy()
        payload.pop("description", None)
        payload.pop("tag", None)

        self.mock_scm.post.assert_called_once_with(
            "/config/objects/v1/regions",
            json=payload,
        )
        assert isinstance(created_object, RegionResponseModel)
        assert created_object.name == request_data.name
        assert created_object.folder == request_data.folder

    def test_create_with_snippet(self):
        """Test creating a region with snippet container."""
        request_data = RegionCreateApiFactory.with_snippet()
        response_data = RegionResponseFactory.from_request(request_data)

        self.mock_scm.post.return_value = response_data.model_dump(exclude_none=False)

        # Pass a dictionary for the create method
        request_dict = request_data.model_dump(exclude_none=False)
        created_object = self.client.create(request_dict)

        # From the SCM API docs, description and tag are excluded from the payload
        payload = request_dict.copy()
        payload.pop("description", None)
        payload.pop("tag", None)

        self.mock_scm.post.assert_called_once_with(
            "/config/objects/v1/regions",
            json=payload,
        )
        assert isinstance(created_object, RegionResponseModel)
        assert created_object.name == request_data.name
        assert created_object.snippet == request_data.snippet

    def test_create_with_device(self):
        """Test creating a region with device container."""
        request_data = RegionCreateApiFactory.with_device()
        response_data = RegionResponseFactory.from_request(request_data)

        self.mock_scm.post.return_value = response_data.model_dump(exclude_none=False)

        # Pass a dictionary for the create method
        request_dict = request_data.model_dump(exclude_none=False)
        created_object = self.client.create(request_dict)

        # From the SCM API docs, description and tag are excluded from the payload
        payload = request_dict.copy()
        payload.pop("description", None)
        payload.pop("tag", None)

        self.mock_scm.post.assert_called_once_with(
            "/config/objects/v1/regions",
            json=payload,
        )
        assert isinstance(created_object, RegionResponseModel)
        assert created_object.name == request_data.name
        assert created_object.device == request_data.device

    def test_create_http_error_no_response_content(self):
        """Test create method when HTTP error has no response content."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500
        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.post.side_effect = mock_http_error

        with pytest.raises(HTTPError):
            self.client.create({"name": "test", "folder": "Global"})

    def test_create_http_error_with_response(self):
        """Test that HTTPError with response content triggers proper error handling."""
        test_data = {
            "name": "test-region",
            "folder": "Global",
        }

        self.mock_scm.post.side_effect = raise_mock_http_error(
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
        self.mock_scm.post.side_effect = Exception("Generic error")

        with pytest.raises(Exception) as exc_info:
            self.client.create({"name": "test", "folder": "Global"})
        assert str(exc_info.value) == "Generic error"


class TestRegionUpdate(TestRegionBase):
    """Tests for updating Region objects."""

    def test_update_valid_object(self):
        """Test updating an object with valid data."""
        request_data = RegionUpdateApiFactory.build_valid()
        response_data = RegionResponseFactory.from_request(request_data)

        self.mock_scm.put.return_value = response_data.model_dump(exclude_none=False)
        updated_object = self.client.update(request_data)

        # The Region client does two things to the payload:
        # 1. Excludes tag and description as they're not supported by the API
        # 2. Removes the ID since it's used in the URL
        expected_payload = request_data.model_dump(exclude_unset=True)
        expected_payload.pop("id", None)
        expected_payload.pop("tag", None)
        expected_payload.pop("description", None)

        self.mock_scm.put.assert_called_once_with(
            f"/config/objects/v1/regions/{request_data.id}",
            json=expected_payload,
        )
        assert isinstance(updated_object, RegionResponseModel)
        assert updated_object.name == request_data.name
        assert updated_object.id == request_data.id

    def test_update_malformed_command_error(self):
        """Test error handling when update fails due to malformed command."""
        request_data = RegionUpdateApiFactory.build_valid(
            id="123e4567-e89b-12d3-a456-426655440000", name="test-region"
        )

        self.mock_scm.put.side_effect = raise_mock_http_error(
            status_code=400,
            error_code="API_I00013",
            message="Update failed",
            error_type="Malformed Command",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.update(request_data)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Update failed"
        assert error_response["_errors"][0]["details"]["errorType"] == "Malformed Command"

    def test_update_object_not_present_error(self):
        """Test error handling when the object to update is not present."""
        request_data = RegionUpdateApiFactory.build_valid(
            id="123e4567-e89b-12d3-a456-426655440000", name="test-region"
        )

        self.mock_scm.put.side_effect = raise_mock_http_error(
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.update(request_data)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Object not found"
        assert error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"

    def test_update_http_error_no_response_content(self):
        """Test update method when HTTP error has no response content."""
        request_data = RegionUpdateApiFactory.build_valid(
            id="123e4567-e89b-12d3-a456-426655440000", name="test"
        )

        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.put.side_effect = mock_http_error

        with pytest.raises(HTTPError):
            self.client.update(request_data)

    def test_update_generic_exception_handling(self):
        """Test handling of a generic exception during update."""
        request_data = RegionUpdateApiFactory.build_valid(
            id="123e4567-e89b-12d3-a456-426655440000", name="test"
        )

        self.mock_scm.put.side_effect = Exception("Generic error")

        with pytest.raises(Exception) as exc_info:
            self.client.update(request_data)
        assert str(exc_info.value) == "Generic error"

    def test_update_server_error(self):
        """Test handling of server errors during update."""
        request_data = RegionUpdateApiFactory.build_valid(
            id="123e4567-e89b-12d3-a456-426655440000", name="test-region"
        )

        self.mock_scm.put.side_effect = raise_mock_http_error(
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.update(request_data)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "An internal error occurred"
        assert error_response["_errors"][0]["details"]["errorType"] == "Internal Error"


class TestRegionGet(TestRegionBase):
    """Tests for retrieving a specific Region object."""

    def test_get_valid_object(self):
        """Test retrieving a specific object."""
        response_data = RegionResponseFactory.build_valid()
        self.mock_scm.get.return_value = response_data.model_dump()

        retrieved_object = self.client.get(str(response_data.id))

        self.mock_scm.get.assert_called_once_with(
            f"/config/objects/v1/regions/{response_data.id}",
        )
        assert isinstance(retrieved_object, RegionResponseModel)
        assert retrieved_object.id == response_data.id
        assert retrieved_object.name == response_data.name

    def test_get_object_not_present_error(self):
        """Test error handling when the object is not present."""
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

        self.mock_scm.get.side_effect = Exception("Generic error")

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
        self.mock_scm.get.side_effect = mock_http_error

        with pytest.raises(HTTPError):
            self.client.get(object_id)

    def test_get_server_error(self):
        """Test handling of server errors during get method."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.get.side_effect = raise_mock_http_error(
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


class TestRegionDelete(TestRegionBase):
    """Tests for deleting Region objects."""

    def test_delete_success(self):
        """Test successful deletion of an object."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.return_value = None

        # Should not raise any exception
        self.client.delete(object_id)

        self.mock_scm.delete.assert_called_once_with(f"/config/objects/v1/regions/{object_id}")

    def test_delete_referenced_object(self):
        """Test deleting an object that is referenced elsewhere."""
        object_id = "3fecfe58-af0c-472b-85cf-437bb6df2929"

        self.mock_scm.delete.side_effect = raise_mock_http_error(
            status_code=409,
            error_code="E009",
            message="Your configuration is not valid.",
            error_type="Reference Not Zero",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.delete(object_id)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Your configuration is not valid."
        assert error_response["_errors"][0]["details"]["errorType"] == "Reference Not Zero"

    def test_delete_object_not_present_error(self):
        """Test error handling when the object to delete is not present."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.side_effect = raise_mock_http_error(
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
        self.mock_scm.delete.side_effect = mock_http_error

        with pytest.raises(HTTPError):
            self.client.delete(object_id)

    def test_delete_generic_exception_handling(self):
        """Test handling of a generic exception during delete."""
        self.mock_scm.delete.side_effect = Exception("Generic error")

        with pytest.raises(Exception) as exc_info:
            self.client.delete("abcdefg")

        assert str(exc_info.value) == "Generic error"

    def test_delete_server_error(self):
        """Test handling of server errors during delete."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.side_effect = raise_mock_http_error(
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


class TestRegionFetch(TestRegionBase):
    """Tests for fetching Region objects by name."""

    def test_fetch_valid_object(self):
        """Test retrieving an object by its name using the `fetch` method."""
        response_data = RegionResponseFactory.build_valid()

        # Fetch should work like address.fetch - a single API call returning the object
        self.mock_scm.get.return_value = response_data.model_dump(exclude_none=False)

        fetched_object = self.client.fetch(name=response_data.name, folder=response_data.folder)

        # Verify the API was called with correct params
        self.mock_scm.get.assert_called_once_with(
            "/config/objects/v1/regions",
            params={
                "name": response_data.name,
                "folder": response_data.folder,
            },
        )

        assert isinstance(fetched_object, RegionResponseModel)
        assert fetched_object.name == response_data.name
        assert fetched_object.folder == response_data.folder
        assert str(fetched_object.id) == str(response_data.id)

    def test_fetch_object_not_present_error(self):
        """Test fetching an object that does not exist."""
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.fetch(name="nonexistent", folder="Global")
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Object not found"
        assert error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"

    def test_fetch_empty_name_error(self):
        """Test fetching with an empty name parameter."""
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=400,
            error_code="E003",
            message='"name" is not allowed to be empty',
            error_type="Missing Query Parameter",
        )

        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="", folder="Global")

        error_msg = str(exc_info.value)
        assert '"name" is not allowed to be empty' in error_msg
        assert "HTTP error: 400" in error_msg
        assert "API error: E003" in error_msg

    def test_fetch_empty_container_error(self):
        """Test fetching with an empty folder parameter."""
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=400,
            error_code="E003",
            message='"folder" is not allowed to be empty',
            error_type="Missing Query Parameter",
        )

        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="test", folder="")

        error_msg = str(exc_info.value)
        assert '"folder" is not allowed to be empty' in error_msg
        assert "HTTP error: 400" in error_msg
        assert "API error: E003" in error_msg

    def test_fetch_invalid_response_format_error(self):
        """Test fetching an object when the API returns an unexpected format."""
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=500,
            error_code="E003",
            message="Invalid response format",
            error_type="Invalid Object",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.fetch(name="test", folder="Global")
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Invalid response format"
        assert error_response["_errors"][0]["details"]["errorType"] == "Invalid Object"

    def test_fetch_generic_exception_handling(self):
        """Test generic exception handling during fetch."""
        self.mock_scm.get.side_effect = Exception("Generic error")

        with pytest.raises(Exception) as exc_info:
            self.client.fetch(name="test", folder="Global")

        assert str(exc_info.value) == "Generic error"

    def test_fetch_http_error_no_response_content(self):
        """Test that an HTTPError without response content in fetch() re-raises the exception."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500
        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_http_error

        with pytest.raises(HTTPError):
            self.client.fetch(name="test-region", folder="Global")

    def test_fetch_server_error(self):
        """Test handling of server errors during fetch."""
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.fetch(name="test", folder="Global")
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "An internal error occurred"
        assert error_response["_errors"][0]["details"]["errorType"] == "Internal Error"

    def test_fetch_missing_id_field_error(self):
        """Test that InvalidObjectError is raised when the response is missing 'id' field."""
        mock_response = {
            "name": "test-region",
            "folder": "Global",
        }

        self.mock_scm.get.return_value = mock_response

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-region", folder="Global")

        error_msg = str(exc_info.value)
        assert "HTTP error: 500 - API error: E003" in error_msg
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500

    def test_fetch_no_container_provided_error(self):
        """Test that InvalidObjectError is raised when no container parameter is provided."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-region")

        error_msg = str(exc_info.value)
        assert "HTTP error: 400 - API error: E003" in error_msg
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 400

    def test_fetch_multiple_containers_provided_error(self):
        """Test that InvalidObjectError is raised when multiple container parameters are provided."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(
                name="test-region",
                folder="Global",
                snippet="TestSnippet",
            )

        error_msg = str(exc_info.value)
        assert "HTTP error: 400 - API error: E003" in error_msg
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 400

    def test_fetch_invalid_response_type_error(self):
        """Test that InvalidObjectError is raised when the response is not a dictionary."""
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test123", folder="Global")

        error_msg = str(exc_info.value)
        assert "HTTP error: 500 - API error: E003" in error_msg
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500
