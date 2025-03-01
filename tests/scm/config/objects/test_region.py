# tests/scm/config/objects/test_region.py

# Standard library imports
from unittest.mock import MagicMock

# External libraries
import pytest
from requests.exceptions import HTTPError

# Local SDK imports
from scm.config.objects import Region
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
)
from scm.models.objects import (
    RegionResponseModel,
)
from tests.factories import (
    RegionResponseFactory,
    RegionCreateApiFactory,
    RegionUpdateApiFactory,
)
from tests.utils import raise_mock_http_error


@pytest.mark.usefixtures("load_env")
class TestRegionBase:
    """Base class for Region tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm  # noqa
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = Region(self.mock_scm, max_limit=5000)  # noqa


# -------------------- Test Classes Grouped by Functionality --------------------


class TestRegionMaxLimit(TestRegionBase):
    """Tests for max_limit functionality."""

    def test_default_max_limit(self):
        """Test that default max_limit is set correctly."""
        client = Region(self.mock_scm)  # noqa
        assert client.max_limit == Region.DEFAULT_MAX_LIMIT
        assert client.max_limit == 2500

    def test_custom_max_limit(self):
        """Test setting a custom max_limit."""
        client = Region(self.mock_scm, max_limit=1000)  # noqa
        assert client.max_limit == 1000

    def test_max_limit_setter(self):
        """Test the max_limit property setter."""
        client = Region(self.mock_scm)  # noqa
        client.max_limit = 3000
        assert client.max_limit == 3000

    def test_invalid_max_limit_type(self):
        """Test that invalid max_limit type raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            Region(self.mock_scm, max_limit="invalid")  # noqa
        assert (
            "{'error': 'Invalid max_limit type'} - HTTP error: 400 - API error: E003"
            in str(exc_info.value)
        )

    def test_max_limit_too_low(self):
        """Test that max_limit below 1 raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            Region(self.mock_scm, max_limit=0)  # noqa
        assert (
            "{'error': 'Invalid max_limit value'} - HTTP error: 400 - API error: E003"
            in str(exc_info.value)
        )

    def test_max_limit_too_high(self):
        """Test that max_limit above ABSOLUTE_MAX_LIMIT raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            Region(self.mock_scm, max_limit=6000)  # noqa
        assert "max_limit exceeds maximum allowed value" in str(exc_info.value)


class TestRegionList(TestRegionBase):
    """Tests for listing Region objects."""

    def test_list_valid(self):
        """
        **Objective:** Test listing all objects.
        """
        mock_response = {
            "data": [
                RegionResponseFactory(
                    name="North America Region",
                    folder="Global",
                    geo_location={
                        "latitude": 37.7749,
                        "longitude": -122.4194,
                    },
                    address=["192.168.1.0/24", "10.0.0.0/8"],
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
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        existing_objects = self.client.list(folder="Global")

        self.mock_scm.get.assert_called_once_with(  # noqa
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
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
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
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Listing failed",
            error_type="Operation Impossible",
        )

        with pytest.raises(HTTPError):
            self.client.list(folder="NonexistentFolder")

    def test_list_container_missing_error(self):
        """
        Test that InvalidObjectError is raised when no container parameter is provided.
        """
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
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
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
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
                "longitude": {"min": -130, "max": -120}
            },
            "addresses": ["10.0.0.0/8", "192.168.1.0/24"],
        }

        mock_response = {"data": []}
        self.mock_scm.get.return_value = mock_response  # noqa

        self.client.list(folder="Global", **filters)

        self.mock_scm.get.assert_called_once_with(  # noqa
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
        self.mock_scm.get.return_value = mock_response  # noqa

        # Filter for only North America region by latitude
        regions = self.client.list(
            folder="Global",
            geo_location={
                "latitude": {"min": 30, "max": 40},
            }
        )
        assert len(regions) == 1
        assert regions[0].name == "North America Region"

        # Filter for only Europe region by longitude
        regions = self.client.list(
            folder="Global",
            geo_location={
                "longitude": {"min": -5, "max": 5},
            }
        )
        assert len(regions) == 1
        assert regions[0].name == "Europe Region"

        # Filter for no regions (no match)
        regions = self.client.list(
            folder="Global",
            geo_location={
                "latitude": {"min": 0, "max": 10},
                "longitude": {"min": 0, "max": 10},
            }
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
        self.mock_scm.get.return_value = mock_response  # noqa

        # Filter for specific address
        regions = self.client.list(
            folder="Global",
            addresses=["10.0.0.0/8"]
        )
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
        self.mock_scm.get.return_value = mock_response  # noqa

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
        """
        Test that InvalidObjectError is raised when the response is not a dictionary.
        """
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Global")

        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500
        assert "HTTP error: 500 - API error: E003" in str(exc_info.value)

    def test_list_response_invalid_data_field_missing(self):
        """
        Test that InvalidObjectError is raised when API returns response with missing data field.
        """
        self.mock_scm.get.return_value = {"wrong_field": "value"}  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Global")

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        assert error.error_code == "E003"
        assert error.http_status_code == 500
        assert "HTTP error: 500 - API error: E003" in str(exc_info.value)

    def test_list_response_invalid_data_field_type(self):
        """
        Test that InvalidObjectError is raised when API returns non-list data field.
        """
        self.mock_scm.get.return_value = {"data": "not a list"}  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Global")

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        assert error.error_code == "E003"
        assert error.http_status_code == 500

    def test_list_response_no_content(self):
        """Test that an HTTPError without response content in list() re-raises the exception."""
        mock_response = MagicMock()
        mock_response.content = None  # Simulate no content
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.list(folder="Global")

    def test_list_server_error(self):
        """Test generic exception handling in list method."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
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
        """
        Test that the list method correctly aggregates data from multiple pages.
        Using a custom client with max_limit=2500 to test pagination.
        """
        client = Region(self.mock_scm, max_limit=2500)  # noqa

        # Create test data
        total_objects = 7500  # Three pages worth
        first_batch = [
            RegionResponseFactory(name=f"Region_{i}")
            for i in range(2500)
        ]
        second_batch = [
            RegionResponseFactory(name=f"Region_{i}")
            for i in range(2500, 5000)
        ]
        third_batch = [
            RegionResponseFactory(name=f"Region_{i}")
            for i in range(5000, 7500)
        ]

        # Set up mock responses
        mock_responses = [
            {"data": [obj.model_dump() for obj in first_batch]},
            {"data": [obj.model_dump() for obj in second_batch]},
            {"data": [obj.model_dump() for obj in third_batch]},
            {"data": []},  # Empty response to end pagination
        ]
        self.mock_scm.get.side_effect = mock_responses  # noqa

        # Get results
        results = client.list(folder="Global")

        # Verify results
        assert len(results) == total_objects
        assert isinstance(results[0], RegionResponseModel)
        assert all(isinstance(r, RegionResponseModel) for r in results)

        # Verify the number of API calls
        assert self.mock_scm.get.call_count == 4  # noqa # Three pages + one final check

        # Verify first API call used correct parameters
        self.mock_scm.get.assert_any_call(  # noqa
            "/config/objects/v1/regions",
            params={
                "folder": "Global",
                "limit": 2500,
                "offset": 0,
            },
        )

    # -------------------- New Tests for exact_match and Exclusions --------------------

    def test_list_exact_match(self):
        """
        Test that exact_match=True returns only objects that match the container exactly.
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

        self.mock_scm.get.return_value = mock_response  # noqa

        # exact_match should exclude the one from "Shared"
        filtered = self.client.list(folder="Global", exact_match=True)
        assert len(filtered) == 1
        assert filtered[0].folder == "Global"
        assert filtered[0].name == "region_in_global"

    def test_list_exclude_folders(self):
        """
        Test that exclude_folders removes objects from those folders.
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
        self.mock_scm.get.return_value = mock_response  # noqa

        filtered = self.client.list(folder="Global", exclude_folders=["Shared"])
        assert len(filtered) == 1
        assert all(a.folder != "Shared" for a in filtered)

    def test_list_exclude_snippets(self):
        """
        Test that exclude_snippets removes objects with those snippets.
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
        self.mock_scm.get.return_value = mock_response  # noqa

        filtered = self.client.list(folder="Global", exclude_snippets=["default"])
        assert len(filtered) == 1
        assert all(a.snippet != "default" for a in filtered)

    def test_list_exclude_devices(self):
        """
        Test that exclude_devices removes objects with those devices.
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
        self.mock_scm.get.return_value = mock_response  # noqa

        filtered = self.client.list(folder="Global", exclude_devices=["DeviceA"])
        assert len(filtered) == 1
        assert all(a.device != "DeviceA" for a in filtered)

    def test_list_exact_match_and_exclusions(self):
        """
        Test combining exact_match with exclusions.
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
        self.mock_scm.get.return_value = mock_response  # noqa

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
        test_object = RegionCreateApiFactory()
        mock_response = RegionResponseFactory.from_request(test_object)

        self.mock_scm.post.return_value = mock_response.model_dump()  # noqa
        created_object = self.client.create(test_object.model_dump(exclude_unset=True))

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/regions",
            json=test_object.model_dump(exclude_unset=True),
        )
        assert str(created_object.id) == str(mock_response.id)
        assert created_object.name == test_object.name
        assert created_object.folder == test_object.folder
        
        # Different access pattern for model objects vs dictionaries
        geo_location_dict = test_object.model_dump()["geo_location"]
        assert created_object.geo_location.latitude == geo_location_dict["latitude"]
        assert created_object.geo_location.longitude == geo_location_dict["longitude"]

    def test_create_with_snippet(self):
        """Test creating a region with snippet container."""
        test_object = RegionCreateApiFactory.with_snippet()
        mock_response = RegionResponseFactory.from_request(test_object)

        self.mock_scm.post.return_value = mock_response.model_dump()  # noqa
        created_object = self.client.create(test_object.model_dump(exclude_unset=True))

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/regions",
            json=test_object.model_dump(exclude_unset=True),
        )
        assert created_object.snippet == test_object.snippet
        assert created_object.folder is None

    def test_create_with_device(self):
        """Test creating a region with device container."""
        test_object = RegionCreateApiFactory.with_device()
        mock_response = RegionResponseFactory.from_request(test_object)

        self.mock_scm.post.return_value = mock_response.model_dump()  # noqa
        created_object = self.client.create(test_object.model_dump(exclude_unset=True))

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/regions",
            json=test_object.model_dump(exclude_unset=True),
        )
        assert created_object.device == test_object.device
        assert created_object.folder is None

    def test_create_http_error_no_response_content(self):
        """Test create method when HTTP error has no response content."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500
        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.post.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.create(
                {"name": "test", "folder": "Global"}
            )

    def test_create_http_error_with_response(self):
        """Test that HTTPError with response content triggers proper error handling."""
        test_data = {
            "name": "test-region",
            "folder": "Global",
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
        assert (
            error_response["_errors"][0]["details"]["errorType"] == "Malformed Command"
        )

    def test_create_generic_exception_handling(self):
        """Test handling of a generic exception during create."""
        self.mock_scm.post.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.create(
                {"name": "test", "folder": "Global"}
            )
        assert str(exc_info.value) == "Generic error"


class TestRegionGet(TestRegionBase):
    """Tests for retrieving a specific Region object."""

    def test_get_valid_object(self):
        """Test retrieving a specific object."""
        mock_response = RegionResponseFactory(
            id="b44a8c00-7555-4021-96f0-d59deecd54e8",
            name="TestRegion",
            folder="Global",
        )

        self.mock_scm.get.return_value = mock_response.model_dump()  # noqa
        object_id = mock_response.id

        retrieved_object = self.client.get(object_id)

        self.mock_scm.get.assert_called_once_with(  # noqa
            f"/config/objects/v1/regions/{object_id}"
        )
        assert isinstance(retrieved_object, RegionResponseModel)
        assert retrieved_object.id == mock_response.id
        assert retrieved_object.name == mock_response.name
        assert retrieved_object.folder == mock_response.folder

    def test_get_object_not_present_error(self):
        """Test error handling when the object is not present."""
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
        assert (
            error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"
        )

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


class TestRegionUpdate(TestRegionBase):
    """Tests for updating Region objects."""

    def test_update_valid_object(self):
        """Test updating an object with valid data."""
        update_data = RegionUpdateApiFactory(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="TestRegion",
            geo_location={
                "latitude": 40.7128,
                "longitude": -74.0060,
            },
            address=["192.168.1.0/24", "10.0.0.0/8"],
        )

        mock_response = RegionResponseFactory.from_request(update_data)
        self.mock_scm.put.return_value = mock_response.model_dump()  # noqa

        updated_object = self.client.update(update_data)

        self.mock_scm.put.assert_called_once()  # noqa
        call_args = self.mock_scm.put.call_args  # noqa
        assert call_args[0][0] == f"/config/objects/v1/regions/{update_data.id}"

        payload = call_args[1]["json"]
        assert payload["name"] == "TestRegion"
        assert payload["geo_location"]["latitude"] == 40.7128
        assert payload["geo_location"]["longitude"] == -74.0060
        assert payload["address"] == ["192.168.1.0/24", "10.0.0.0/8"]

        assert isinstance(updated_object, RegionResponseModel)
        assert str(updated_object.id) == str(mock_response.id)
        assert updated_object.name == mock_response.name
        assert updated_object.geo_location.latitude == mock_response.geo_location.latitude
        assert updated_object.geo_location.longitude == mock_response.geo_location.longitude
        assert updated_object.address == mock_response.address

    def test_update_malformed_command_error(self):
        """Test error handling when update fails due to malformed command."""
        update_data = RegionUpdateApiFactory(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-region",
            folder="Global",
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
        assert (
            error_response["_errors"][0]["details"]["errorType"] == "Malformed Command"
        )

    def test_update_object_not_present_error(self):
        """Test error handling when the object to update is not present."""
        update_data = RegionUpdateApiFactory(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-region",
            folder="Global",
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
        assert (
            error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"
        )

    def test_update_http_error_no_response_content(self):
        """Test update method when HTTP error has no response content."""
        update_data = RegionUpdateApiFactory(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test",
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
        update_data = RegionUpdateApiFactory(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test",
        )

        self.mock_scm.put.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.update(update_data)
        assert str(exc_info.value) == "Generic error"

    def test_update_server_error(self):
        """Test handling of server errors during update."""
        update_data = RegionUpdateApiFactory(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-region",
            folder="Global",
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


class TestRegionDelete(TestRegionBase):
    """Tests for deleting Region objects."""

    def test_delete_success(self):
        """Test successful deletion of an object."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.return_value = None  # noqa

        # Should not raise any exception
        self.client.delete(object_id)

        self.mock_scm.delete.assert_called_once_with(  # noqa
            f"/config/objects/v1/regions/{object_id}"
        )

    def test_delete_referenced_object(self):
        """Test deleting an object that is referenced elsewhere."""
        object_id = "3fecfe58-af0c-472b-85cf-437bb6df2929"

        self.mock_scm.delete.side_effect = raise_mock_http_error(  # noqa
            status_code=409,
            error_code="E009",
            message="Your configuration is not valid.",
            error_type="Reference Not Zero",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.delete(object_id)
        error_response = exc_info.value.response.json()
        assert (
            error_response["_errors"][0]["message"]
            == "Your configuration is not valid."
        )
        assert (
            error_response["_errors"][0]["details"]["errorType"] == "Reference Not Zero"
        )

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
        assert (
            error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"
        )

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


class TestRegionFetch(TestRegionBase):
    """Tests for fetching Region objects by name."""

    def test_fetch_valid_object(self):
        """Test retrieving an object by its name using the `fetch` method."""
        mock_response_model = RegionResponseFactory(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="Global Region",
            folder="Global",
            geo_location={
                "latitude": 37.7749,
                "longitude": -122.4194,
            },
            address=["10.0.0.0/8"],
        )
        mock_response_data = mock_response_model.model_dump()

        self.mock_scm.get.return_value = mock_response_data  # noqa

        fetched_object = self.client.fetch(
            name=mock_response_model.name,
            folder=mock_response_model.folder,
        )

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/regions",
            params={
                "folder": mock_response_model.folder,
                "name": mock_response_model.name,
            },
        )

        assert isinstance(fetched_object, RegionResponseModel)
        assert str(fetched_object.id) == str(mock_response_model.id)
        assert fetched_object.name == mock_response_model.name
        assert fetched_object.folder == mock_response_model.folder
        assert fetched_object.geo_location.latitude == mock_response_model.geo_location.latitude
        assert fetched_object.geo_location.longitude == mock_response_model.geo_location.longitude
        assert fetched_object.address == mock_response_model.address

    def test_fetch_object_not_present_error(self):
        """Test fetching an object that does not exist."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.fetch(name="nonexistent", folder="Global")
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Object not found"
        assert (
            error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"
        )

    def test_fetch_empty_name_error(self):
        """Test fetching with an empty name parameter."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
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
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
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
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
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
        self.mock_scm.get.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.fetch(name="test", folder="Global")

        assert str(exc_info.value) == "Generic error"

    def test_fetch_http_error_no_response_content(self):
        """Test that an HTTPError without response content in fetch() re-raises the exception."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500
        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.fetch(name="test-region", folder="Global")

    def test_fetch_server_error(self):
        """Test handling of server errors during fetch."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
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

        self.mock_scm.get.return_value = mock_response  # noqa

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
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test123", folder="Global")

        error_msg = str(exc_info.value)
        assert "HTTP error: 500 - API error: E003" in error_msg
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500


# -------------------- End of Test Classes --------------------