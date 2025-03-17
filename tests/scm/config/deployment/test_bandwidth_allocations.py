# tests/scm/config/deployment/test_bandwidth_allocations.py

# Standard library imports
from unittest.mock import MagicMock

# External libraries
import pytest
from requests.exceptions import HTTPError

# Local SDK imports
from scm.config.deployment import BandwidthAllocations
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
)
from scm.models.deployment import (
    BandwidthAllocationResponseModel,
)
from tests.utils import raise_mock_http_error


# Create factories for our tests
class BandwidthAllocationFactory:
    """Factory for creating bandwidth allocation test data."""

    @classmethod
    def create_model_data(cls, **kwargs):
        """Create data for create model."""
        data = {
            "name": "test-region",
            "allocated_bandwidth": 100,
            "spn_name_list": ["spn1", "spn2"],
        }
        data.update(kwargs)
        return data

    @classmethod
    def update_model_data(cls, **kwargs):
        """Create data for update model."""
        data = {
            "name": "test-region",
            "allocated_bandwidth": 200,
            "spn_name_list": ["spn3", "spn4"],
        }
        data.update(kwargs)
        return data

    @classmethod
    def response_model_data(cls, **kwargs):
        """Create data for response model."""
        data = {
            "name": "test-region",
            "allocated_bandwidth": 100,
            "spn_name_list": ["spn1", "spn2"],
        }
        data.update(kwargs)
        return data

    @classmethod
    def list_response_data(cls, items=None, limit=200, offset=0, total=None):
        """Create data for list response."""
        if items is None:
            items = [cls.response_model_data(), cls.response_model_data(name="test-region-2")]

        if total is None:
            total = len(items)

        return {"data": items, "limit": limit, "offset": offset, "total": total}


@pytest.mark.usefixtures("load_env")
class TestBandwidthAllocationBase:
    """Base class for BandwidthAllocation tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = BandwidthAllocations(self.mock_scm, max_limit=200)


class TestBandwidthAllocationMaxLimit(TestBandwidthAllocationBase):
    """Tests for max_limit functionality."""

    def test_default_max_limit(self):
        """Test that default max_limit is set correctly."""
        client = BandwidthAllocations(self.mock_scm)
        assert client.max_limit == BandwidthAllocations.DEFAULT_MAX_LIMIT
        assert client.max_limit == 200

    def test_custom_max_limit(self):
        """Test setting a custom max_limit."""
        client = BandwidthAllocations(self.mock_scm, max_limit=500)
        assert client.max_limit == 500

    def test_max_limit_setter(self):
        """Test the max_limit property setter."""
        client = BandwidthAllocations(self.mock_scm)
        client.max_limit = 300
        assert client.max_limit == 300

    def test_invalid_max_limit_type(self):
        """Test that invalid max_limit type raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            BandwidthAllocations(self.mock_scm, max_limit="invalid")
        assert "{'error': 'Invalid max_limit type'} - HTTP error: 400 - API error: E003" in str(
            exc_info.value
        )

    def test_max_limit_too_low(self):
        """Test that max_limit below 1 raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            BandwidthAllocations(self.mock_scm, max_limit=0)
        assert "{'error': 'Invalid max_limit value'} - HTTP error: 400 - API error: E003" in str(
            exc_info.value
        )

    def test_max_limit_too_high(self):
        """Test that max_limit above ABSOLUTE_MAX_LIMIT raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            BandwidthAllocations(self.mock_scm, max_limit=2000)
        assert "max_limit exceeds maximum allowed value" in str(exc_info.value)


class TestBandwidthAllocationCreate(TestBandwidthAllocationBase):
    """Tests for creating BandwidthAllocation objects."""

    def test_create_valid(self):
        """Test creating a valid bandwidth allocation."""
        test_data = BandwidthAllocationFactory.create_model_data()
        mock_response = BandwidthAllocationFactory.response_model_data()

        self.mock_scm.post.return_value = mock_response
        created_object = self.client.create(test_data)

        self.mock_scm.post.assert_called_once_with(
            "/config/deployment/v1/bandwidth-allocations",
            json=test_data,
        )
        assert isinstance(created_object, BandwidthAllocationResponseModel)
        assert created_object.name == mock_response["name"]
        assert created_object.allocated_bandwidth == mock_response["allocated_bandwidth"]
        assert created_object.spn_name_list == mock_response["spn_name_list"]

    def test_create_with_qos(self):
        """Test creating a bandwidth allocation with QoS settings."""
        test_data = BandwidthAllocationFactory.create_model_data(
            qos={
                "enabled": True,
                "customized": True,
                "profile": "test-profile",
                "guaranteed_ratio": 0.5,
            }
        )
        mock_response = BandwidthAllocationFactory.response_model_data(
            qos={
                "enabled": True,
                "customized": True,
                "profile": "test-profile",
                "guaranteed_ratio": 0.5,
            }
        )

        self.mock_scm.post.return_value = mock_response
        created_object = self.client.create(test_data)

        self.mock_scm.post.assert_called_once_with(
            "/config/deployment/v1/bandwidth-allocations",
            json=test_data,
        )
        assert isinstance(created_object, BandwidthAllocationResponseModel)
        assert created_object.qos.enabled == mock_response["qos"]["enabled"]
        assert created_object.qos.profile == mock_response["qos"]["profile"]

    def test_create_error(self):
        """Test error handling during creation."""
        test_data = BandwidthAllocationFactory.create_model_data()

        self.mock_scm.post.side_effect = raise_mock_http_error(
            status_code=400,
            error_code="E003",
            message="Create failed",
            error_type="Malformed Command",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.create(test_data)

        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Create failed"
        assert error_response["_errors"][0]["details"]["errorType"] == "Malformed Command"


class TestBandwidthAllocationUpdate(TestBandwidthAllocationBase):
    """Tests for updating BandwidthAllocation objects."""

    def test_update_valid(self):
        """Test updating a valid bandwidth allocation."""
        test_data = BandwidthAllocationFactory.update_model_data()
        mock_response = BandwidthAllocationFactory.response_model_data(
            name=test_data["name"],
            allocated_bandwidth=test_data["allocated_bandwidth"],
            spn_name_list=test_data["spn_name_list"],
        )

        self.mock_scm.put.return_value = mock_response
        updated_object = self.client.update(test_data)

        self.mock_scm.put.assert_called_once_with(
            "/config/deployment/v1/bandwidth-allocations",
            json=test_data,
        )
        assert isinstance(updated_object, BandwidthAllocationResponseModel)
        assert updated_object.name == mock_response["name"]
        assert updated_object.allocated_bandwidth == mock_response["allocated_bandwidth"]
        assert updated_object.spn_name_list == mock_response["spn_name_list"]

    def test_update_with_qos(self):
        """Test updating a bandwidth allocation with QoS settings."""
        test_data = BandwidthAllocationFactory.update_model_data(
            qos={
                "enabled": True,
                "customized": False,
                "profile": "updated-profile",
                "guaranteed_ratio": 0.7,
            }
        )
        mock_response = BandwidthAllocationFactory.response_model_data(
            name=test_data["name"],
            allocated_bandwidth=test_data["allocated_bandwidth"],
            spn_name_list=test_data["spn_name_list"],
            qos={
                "enabled": True,
                "customized": False,
                "profile": "updated-profile",
                "guaranteed_ratio": 0.7,
            },
        )

        self.mock_scm.put.return_value = mock_response
        updated_object = self.client.update(test_data)

        self.mock_scm.put.assert_called_once_with(
            "/config/deployment/v1/bandwidth-allocations",
            json=test_data,
        )
        assert isinstance(updated_object, BandwidthAllocationResponseModel)
        assert updated_object.qos.enabled == mock_response["qos"]["enabled"]
        assert updated_object.qos.profile == mock_response["qos"]["profile"]
        assert updated_object.qos.guaranteed_ratio == mock_response["qos"]["guaranteed_ratio"]

    def test_update_error(self):
        """Test error handling during update."""
        test_data = BandwidthAllocationFactory.update_model_data()

        self.mock_scm.put.side_effect = raise_mock_http_error(
            status_code=400,
            error_code="E003",
            message="Update failed",
            error_type="Malformed Command",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.update(test_data)

        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Update failed"
        assert error_response["_errors"][0]["details"]["errorType"] == "Malformed Command"


class TestBandwidthAllocationList(TestBandwidthAllocationBase):
    """Tests for listing BandwidthAllocation objects."""

    def test_list_valid(self):
        """Test listing bandwidth allocations."""
        mock_response = BandwidthAllocationFactory.list_response_data()

        self.mock_scm.get.return_value = mock_response
        allocations = self.client.list()

        self.mock_scm.get.assert_called_once_with(
            "/config/deployment/v1/bandwidth-allocations",
            params={
                "limit": 200,
                "offset": 0,
            },
        )
        assert isinstance(allocations, list)
        assert len(allocations) == 2
        assert isinstance(allocations[0], BandwidthAllocationResponseModel)
        assert allocations[0].name == mock_response["data"][0]["name"]
        assert allocations[1].name == mock_response["data"][1]["name"]

    def test_list_with_pagination(self):
        """Test listing with pagination."""
        # Create responses for two pages
        page1 = BandwidthAllocationFactory.list_response_data(
            items=[BandwidthAllocationFactory.response_model_data(name="region1")], total=2
        )

        # Set up mock to return page1 first, then empty page to stop pagination
        self.mock_scm.get.side_effect = [page1, {"data": [], "limit": 1, "offset": 1, "total": 2}]

        # Set a small max_limit to force pagination
        self.client.max_limit = 1
        allocations = self.client.list()

        # Should only return items from the first page since the second page is empty
        assert len(allocations) == 1
        assert allocations[0].name == "region1"

        # Check call parameters
        call_args_1 = self.mock_scm.get.call_args_list[0][1]
        assert call_args_1["params"]["limit"] == 1
        assert call_args_1["params"]["offset"] == 0

    def test_list_response_not_dict(self):
        """Test handling when response is not a dictionary."""
        self.mock_scm.get.return_value = "not a dictionary"

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list()

        assert "Response is not a dictionary" in str(exc_info.value)

    def test_list_empty(self):
        """Test listing with no results."""
        mock_response = BandwidthAllocationFactory.list_response_data(items=[], total=0)

        self.mock_scm.get.return_value = mock_response
        allocations = self.client.list()

        assert len(allocations) == 0

    def test_list_with_filters(self):
        """Test listing with filters applied."""
        # Create sample data
        allocation1 = BandwidthAllocationFactory.response_model_data(
            name="region1", allocated_bandwidth=100, spn_name_list=["spn1", "spn2"]
        )
        allocation2 = BandwidthAllocationFactory.response_model_data(
            name="region2", allocated_bandwidth=200, spn_name_list=["spn3"]
        )
        mock_response = BandwidthAllocationFactory.list_response_data(
            items=[allocation1, allocation2]
        )

        self.mock_scm.get.return_value = mock_response

        # Test name filter
        filtered = self.client.list(name="region1")
        assert len(filtered) == 1
        assert filtered[0].name == "region1"

        # Test allocated_bandwidth filter
        filtered = self.client.list(allocated_bandwidth=200)
        assert len(filtered) == 1
        assert filtered[0].name == "region2"

        # Test spn_name_list filter
        filtered = self.client.list(spn_name_list="spn1")
        assert len(filtered) == 1
        assert filtered[0].name == "region1"

        # Test with no matches
        filtered = self.client.list(name="nonexistent")
        assert len(filtered) == 0

    def test_list_error(self):
        """Test error handling during list operation."""
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=500,
            error_code="E003",
            message="Internal Error",
            error_type="Server Error",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.list()

        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Internal Error"
        assert error_response["_errors"][0]["details"]["errorType"] == "Server Error"

    def test_case_insensitive_name_filter_single(self):
        """Test case-insensitive name filtering with a single value."""
        # Create sample data with mixed case
        allocation1 = BandwidthAllocationFactory.response_model_data(
            name="Region1", allocated_bandwidth=100
        )
        allocation2 = BandwidthAllocationFactory.response_model_data(
            name="REGION2", allocated_bandwidth=200
        )
        mock_response = BandwidthAllocationFactory.list_response_data(
            items=[allocation1, allocation2]
        )

        self.mock_scm.get.return_value = mock_response

        # Test case-insensitive filtering
        filtered = self.client.list(name="region1")
        assert len(filtered) == 1
        assert filtered[0].name == "Region1"

        # Test another case variation
        filtered = self.client.list(name="REGION1")
        assert len(filtered) == 1
        assert filtered[0].name == "Region1"

    def test_case_insensitive_name_filter_list(self):
        """Test case-insensitive name filtering with a list of values."""
        # Create sample data with mixed case
        allocation1 = BandwidthAllocationFactory.response_model_data(
            name="Region1", allocated_bandwidth=100
        )
        allocation2 = BandwidthAllocationFactory.response_model_data(
            name="REGION2", allocated_bandwidth=200
        )
        mock_response = BandwidthAllocationFactory.list_response_data(
            items=[allocation1, allocation2]
        )

        self.mock_scm.get.return_value = mock_response

        # Test case-insensitive filtering with list
        filtered = self.client.list(name=["region1", "region2"])
        assert len(filtered) == 2

        # Mixed case in filter values
        filtered = self.client.list(name=["REGION1", "Region2"])
        assert len(filtered) == 2


class TestBandwidthAllocationGet(TestBandwidthAllocationBase):
    """Tests for getting a single BandwidthAllocation object."""

    def test_get_valid(self):
        """Test getting a bandwidth allocation by name."""
        allocation_name = "test-region"
        mock_response = BandwidthAllocationFactory.list_response_data(
            items=[BandwidthAllocationFactory.response_model_data(name=allocation_name)]
        )

        self.mock_scm.get.return_value = mock_response
        allocation = self.client.get(allocation_name)

        self.mock_scm.get.assert_called_once_with(
            "/config/deployment/v1/bandwidth-allocations",
            params={"name": allocation_name},
        )
        assert isinstance(allocation, BandwidthAllocationResponseModel)
        assert allocation.name == allocation_name

    def test_get_not_found(self):
        """Test getting a nonexistent bandwidth allocation."""
        allocation_name = "nonexistent-region"
        mock_response = BandwidthAllocationFactory.list_response_data(items=[])

        self.mock_scm.get.return_value = mock_response
        allocation = self.client.get(allocation_name)

        assert allocation is None

    def test_get_empty_name(self):
        """Test getting with empty name parameter."""
        with pytest.raises(MissingQueryParameterError):
            self.client.get("")

        # No need to check exact error message as it's raising the error from the underlying implementation

    def test_get_response_not_dict(self):
        """Test handling when response is not a dictionary."""
        allocation_name = "test-region"
        self.mock_scm.get.return_value = "not a dictionary"

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.get(allocation_name)

        assert "Response is not a dictionary" in str(exc_info.value)

    def test_get_error(self):
        """Test error handling during get operation."""
        allocation_name = "test-region"

        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=500,
            error_code="E003",
            message="Internal Error",
            error_type="Server Error",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.get(allocation_name)

        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Internal Error"
        assert error_response["_errors"][0]["details"]["errorType"] == "Server Error"


class TestBandwidthAllocationFetch(TestBandwidthAllocationBase):
    """Tests for fetching a single BandwidthAllocation object."""

    def test_fetch_valid(self):
        """Test fetching a bandwidth allocation by name."""
        allocation_name = "test-region"
        mock_response = BandwidthAllocationFactory.list_response_data(
            items=[BandwidthAllocationFactory.response_model_data(name=allocation_name)]
        )

        self.mock_scm.get.return_value = mock_response
        allocation = self.client.fetch(allocation_name)

        self.mock_scm.get.assert_called_once_with(
            "/config/deployment/v1/bandwidth-allocations",
            params={"name": allocation_name},
        )
        assert isinstance(allocation, BandwidthAllocationResponseModel)
        assert allocation.name == allocation_name

    def test_fetch_not_found(self):
        """Test fetching a nonexistent bandwidth allocation."""
        allocation_name = "nonexistent-region"
        mock_response = BandwidthAllocationFactory.list_response_data(items=[])

        self.mock_scm.get.return_value = mock_response

        with pytest.raises(InvalidObjectError):
            self.client.fetch(allocation_name)

        # No need to check exact error message as it's raising the error from the underlying implementation

    def test_fetch_empty_name(self):
        """Test fetching with empty name parameter."""
        with pytest.raises(MissingQueryParameterError):
            self.client.fetch("")

        # No need to check exact error message as it's raising the error from the underlying implementation


class TestBandwidthAllocationDelete(TestBandwidthAllocationBase):
    """Tests for deleting BandwidthAllocation objects."""

    def test_delete_valid(self):
        """Test deleting a bandwidth allocation."""
        name = "test-region"
        spn_name_list = "spn1,spn2"

        self.mock_scm.delete.return_value = None
        self.client.delete(name, spn_name_list)

        self.mock_scm.delete.assert_called_once_with(
            "/config/deployment/v1/bandwidth-allocations",
            params={
                "name": name,
                "spn_name_list": spn_name_list,
            },
        )

    def test_delete_empty_name(self):
        """Test deleting with empty name parameter."""
        with pytest.raises(MissingQueryParameterError):
            self.client.delete("", "spn1,spn2")

        # No need to check exact error message as it's raising the error from the underlying implementation

    def test_delete_empty_spn_list(self):
        """Test deleting with empty spn_name_list parameter."""
        with pytest.raises(MissingQueryParameterError):
            self.client.delete("test-region", "")

        # No need to check exact error message as it's raising the error from the underlying implementation

    def test_delete_invalid_spn_list_format(self):
        """Test deleting with invalid spn_name_list format (empty items)."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.delete("test-region", "spn1,,spn2")

        assert "spn_name_list must be a non-empty" in str(exc_info.value)

    def test_delete_invalid_spn_list_format_whitespace(self):
        """Test deleting with invalid spn_name_list format (only whitespace)."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.delete("test-region", "spn1,  ,spn2")

        assert "spn_name_list must be a non-empty" in str(exc_info.value)

    def test_delete_error(self):
        """Test error handling during delete operation."""
        self.mock_scm.delete.side_effect = raise_mock_http_error(
            status_code=404,
            error_code="E005",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.delete("test-region", "spn1,spn2")

        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Object not found"
        assert error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"


class TestBandwidthAllocationFilters(TestBandwidthAllocationBase):
    """Tests for BandwidthAllocation filtering functionality."""

    def test_filter_by_name(self):
        """Test filtering by name."""
        allocations = [
            BandwidthAllocationResponseModel(
                **BandwidthAllocationFactory.response_model_data(name="region1")
            ),
            BandwidthAllocationResponseModel(
                **BandwidthAllocationFactory.response_model_data(name="region2")
            ),
        ]

        # Single string filter
        filtered = self.client._apply_filters(allocations, {"name": "region1"})
        assert len(filtered) == 1
        assert filtered[0].name == "region1"

        # List filter
        filtered = self.client._apply_filters(allocations, {"name": ["region1", "region2"]})
        assert len(filtered) == 2

        # Empty list filter
        filtered = self.client._apply_filters(allocations, {"name": []})
        assert len(filtered) == 0

        # Non-matching filter
        filtered = self.client._apply_filters(allocations, {"name": "nonexistent"})
        assert len(filtered) == 0

    def test_filter_by_allocated_bandwidth(self):
        """Test filtering by allocated_bandwidth."""
        allocations = [
            BandwidthAllocationResponseModel(
                **BandwidthAllocationFactory.response_model_data(
                    name="region1", allocated_bandwidth=100
                )
            ),
            BandwidthAllocationResponseModel(
                **BandwidthAllocationFactory.response_model_data(
                    name="region2", allocated_bandwidth=200
                )
            ),
        ]

        # Single value filter
        filtered = self.client._apply_filters(allocations, {"allocated_bandwidth": 100})
        assert len(filtered) == 1
        assert filtered[0].name == "region1"

        # List filter
        filtered = self.client._apply_filters(allocations, {"allocated_bandwidth": [100, 200]})
        assert len(filtered) == 2

        # Empty list filter
        filtered = self.client._apply_filters(allocations, {"allocated_bandwidth": []})
        assert len(filtered) == 0

        # Non-matching filter
        filtered = self.client._apply_filters(allocations, {"allocated_bandwidth": 300})
        assert len(filtered) == 0

    def test_filter_by_spn_name_list(self):
        """Test filtering by spn_name_list."""
        allocations = [
            BandwidthAllocationResponseModel(
                **BandwidthAllocationFactory.response_model_data(
                    name="region1", spn_name_list=["spn1", "spn2"]
                )
            ),
            BandwidthAllocationResponseModel(
                **BandwidthAllocationFactory.response_model_data(
                    name="region2", spn_name_list=["spn3"]
                )
            ),
        ]

        # Single string filter
        filtered = self.client._apply_filters(allocations, {"spn_name_list": "spn1"})
        assert len(filtered) == 1
        assert filtered[0].name == "region1"

        # List filter
        filtered = self.client._apply_filters(allocations, {"spn_name_list": ["spn1", "spn3"]})
        assert len(filtered) == 2

        # Empty list filter
        filtered = self.client._apply_filters(allocations, {"spn_name_list": []})
        assert len(filtered) == 0

        # Non-matching filter
        filtered = self.client._apply_filters(allocations, {"spn_name_list": "nonexistent"})
        assert len(filtered) == 0

    def test_filter_by_qos_enabled(self):
        """Test filtering by qos_enabled."""
        allocations = [
            BandwidthAllocationResponseModel(
                **BandwidthAllocationFactory.response_model_data(
                    name="region1", qos={"enabled": True, "profile": "profile1"}
                )
            ),
            BandwidthAllocationResponseModel(
                **BandwidthAllocationFactory.response_model_data(
                    name="region2", qos={"enabled": False, "profile": "profile2"}
                )
            ),
            BandwidthAllocationResponseModel(
                **BandwidthAllocationFactory.response_model_data(name="region3", qos=None)
            ),
        ]

        # Filter by enabled=True
        filtered = self.client._apply_filters(allocations, {"qos_enabled": True})
        assert len(filtered) == 1
        assert filtered[0].name == "region1"

        # Filter by enabled=False
        filtered = self.client._apply_filters(allocations, {"qos_enabled": False})
        assert len(filtered) == 1
        assert filtered[0].name == "region2"

        # Invalid filter type
        with pytest.raises(InvalidObjectError):
            self.client._apply_filters(allocations, {"qos_enabled": "not-a-boolean"})

    def test_multiple_filters(self):
        """Test applying multiple filters simultaneously."""
        allocations = [
            BandwidthAllocationResponseModel(
                **BandwidthAllocationFactory.response_model_data(
                    name="region1",
                    allocated_bandwidth=100,
                    spn_name_list=["spn1", "spn2"],
                    qos={"enabled": True, "profile": "profile1"},
                )
            ),
            BandwidthAllocationResponseModel(
                **BandwidthAllocationFactory.response_model_data(
                    name="region2",
                    allocated_bandwidth=200,
                    spn_name_list=["spn3"],
                    qos={"enabled": False, "profile": "profile2"},
                )
            ),
        ]

        # Apply multiple filters
        filtered = self.client._apply_filters(
            allocations,
            {
                "name": "region1",
                "allocated_bandwidth": 100,
                "spn_name_list": "spn1",
                "qos_enabled": True,
            },
        )
        assert len(filtered) == 1
        assert filtered[0].name == "region1"

        # Apply non-matching filters
        filtered = self.client._apply_filters(
            allocations,
            {
                "name": "region1",
                "allocated_bandwidth": 200,  # This doesn't match region1
            },
        )
        assert len(filtered) == 0

    def test_filter_with_none_values(self):
        """Test filtering when some allocations have None for optional fields."""
        allocations = [
            BandwidthAllocationResponseModel(
                **BandwidthAllocationFactory.response_model_data(name="region1", spn_name_list=None)
            ),
            BandwidthAllocationResponseModel(
                **BandwidthAllocationFactory.response_model_data(
                    name="region2", spn_name_list=["spn3"]
                )
            ),
        ]

        # Filter by spn_name_list when some allocations have None
        filtered = self.client._apply_filters(allocations, {"spn_name_list": "spn3"})
        assert len(filtered) == 1
        assert filtered[0].name == "region2"
