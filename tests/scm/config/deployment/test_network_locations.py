"""
Test module for Network Locations configuration service.

This module contains unit tests for the Network Locations configuration service and its related models.
"""
# tests/scm/config/deployment/test_network_locations.py

# Standard library imports
from unittest.mock import MagicMock, patch

# External libraries
import pytest

# Local SDK imports
from scm.config.deployment.network_locations import NetworkLocations
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.deployment import NetworkLocationModel


@pytest.mark.usefixtures("load_env")
class TestNetworkLocationsBase:
    """Base class for NetworkLocations tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm  # noqa
        self.mock_scm.get = MagicMock()
        self.client = NetworkLocations(self.mock_scm, max_limit=500)  # noqa
        yield
        # Reset mock methods after each test
        self.mock_scm.get.reset_mock()


# -------------------- Unit Tests --------------------


@pytest.mark.unit
class TestNetworkLocationsMaxLimit(TestNetworkLocationsBase):
    """Unit tests for max_limit functionality."""

    def test_default_max_limit(self):
        """Test that default max_limit is set correctly."""
        client = NetworkLocations(self.mock_scm)  # noqa
        assert client.max_limit == NetworkLocations.DEFAULT_MAX_LIMIT
        assert client.max_limit == 200

    def test_custom_max_limit(self):
        """Test setting a custom max_limit."""
        client = NetworkLocations(self.mock_scm, max_limit=500)  # noqa
        assert client.max_limit == 500

    def test_max_limit_setter(self):
        """Test the max_limit property setter."""
        client = NetworkLocations(self.mock_scm)  # noqa
        client.max_limit = 300
        assert client.max_limit == 300

    def test_invalid_max_limit_type(self):
        """Test that invalid max_limit type raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            NetworkLocations(self.mock_scm, max_limit="invalid")  # noqa
        assert "{'error': 'Invalid max_limit type'} - HTTP error: 400 - API error: E003" in str(
            exc_info.value
        )

    def test_max_limit_too_low(self):
        """Test that max_limit below 1 raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            NetworkLocations(self.mock_scm, max_limit=0)  # noqa
        assert "{'error': 'Invalid max_limit value'} - HTTP error: 400 - API error: E003" in str(
            exc_info.value
        )

    def test_max_limit_too_high(self):
        """Test that max_limit above ABSOLUTE_MAX_LIMIT raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            NetworkLocations(self.mock_scm, max_limit=2000)  # noqa
        assert "max_limit exceeds maximum allowed value" in str(exc_info.value)


@pytest.mark.unit
class TestNetworkLocationsFilters(TestNetworkLocationsBase):
    """Unit tests for filter application."""

    @pytest.fixture
    def sample_locations(self):
        """Return sample network location data for testing."""
        return [
            NetworkLocationModel(
                value="us-west-1",
                display="US West",
                continent="North America",
                latitude=37.7749,
                longitude=-122.4194,
                region="us-west2",
                aggregate_region="us-southwest",
            ),
            NetworkLocationModel(
                value="us-east-1",
                display="US East",
                continent="North America",
                latitude=37.45244,
                longitude=-76.41686,
                region="us-east4",
                aggregate_region="us-east",
            ),
            NetworkLocationModel(
                value="eu-central-1",
                display="Germany Central",
                continent="Europe",
                latitude=50.11208,
                longitude=8.68342,
                region="europe-west3",
                aggregate_region="europe-central",
            ),
        ]

    def test_apply_filters_no_filters(self, sample_locations):
        """Test _apply_filters with no filters."""
        result = self.client._apply_filters(sample_locations, {})
        assert len(result) == len(sample_locations)
        assert all(isinstance(loc, NetworkLocationModel) for loc in result)

    def test_apply_filters_value_string(self, sample_locations):
        """Test _apply_filters with value filter as string."""
        result = self.client._apply_filters(sample_locations, {"value": "us-west-1"})
        assert len(result) == 1
        assert result[0].value == "us-west-1"

    def test_apply_filters_value_list(self, sample_locations):
        """Test _apply_filters with value filter as list."""
        result = self.client._apply_filters(sample_locations, {"value": ["us-west-1", "us-east-1"]})
        assert len(result) == 2
        assert {loc.value for loc in result} == {"us-west-1", "us-east-1"}

    def test_apply_filters_value_list_empty(self, sample_locations):
        """Test _apply_filters with empty value filter list."""
        result = self.client._apply_filters(sample_locations, {"value": []})
        assert len(result) == 0

    def test_apply_filters_display_string(self, sample_locations):
        """Test _apply_filters with display filter as string."""
        result = self.client._apply_filters(sample_locations, {"display": "US West"})
        assert len(result) == 1
        assert result[0].display == "US West"

    def test_apply_filters_display_list(self, sample_locations):
        """Test _apply_filters with display filter as list."""
        result = self.client._apply_filters(sample_locations, {"display": ["US West", "US East"]})
        assert len(result) == 2
        assert {loc.display for loc in result} == {"US West", "US East"}

    def test_apply_filters_display_list_empty(self, sample_locations):
        """Test _apply_filters with empty display filter list."""
        result = self.client._apply_filters(sample_locations, {"display": []})
        assert len(result) == 0

    def test_apply_filters_region_string(self, sample_locations):
        """Test _apply_filters with region filter as string."""
        result = self.client._apply_filters(sample_locations, {"region": "us-west2"})
        assert len(result) == 1
        assert result[0].region == "us-west2"

    def test_apply_filters_region_list(self, sample_locations):
        """Test _apply_filters with region filter as list."""
        result = self.client._apply_filters(sample_locations, {"region": ["us-west2", "us-east4"]})
        assert len(result) == 2
        assert {loc.region for loc in result} == {"us-west2", "us-east4"}

    def test_apply_filters_region_list_empty(self, sample_locations):
        """Test _apply_filters with empty region filter list."""
        result = self.client._apply_filters(sample_locations, {"region": []})
        assert len(result) == 0

    def test_apply_filters_continent_string(self, sample_locations):
        """Test _apply_filters with continent filter as string."""
        result = self.client._apply_filters(sample_locations, {"continent": "North America"})
        assert len(result) == 2
        assert all(loc.continent == "North America" for loc in result)

    def test_apply_filters_continent_list(self, sample_locations):
        """Test _apply_filters with continent filter as list."""
        result = self.client._apply_filters(
            sample_locations, {"continent": ["North America", "Europe"]}
        )
        assert len(result) == 3
        assert {loc.continent for loc in result} == {"North America", "Europe"}

    def test_apply_filters_continent_list_empty(self, sample_locations):
        """Test _apply_filters with empty continent filter list."""
        result = self.client._apply_filters(sample_locations, {"continent": []})
        assert len(result) == 0

    def test_apply_filters_aggregate_region_string(self, sample_locations):
        """Test _apply_filters with aggregate_region filter as string."""
        result = self.client._apply_filters(sample_locations, {"aggregate_region": "us-southwest"})
        assert len(result) == 1
        assert result[0].aggregate_region == "us-southwest"

    def test_apply_filters_aggregate_region_list(self, sample_locations):
        """Test _apply_filters with aggregate_region filter as list."""
        result = self.client._apply_filters(
            sample_locations, {"aggregate_region": ["us-southwest", "us-east"]}
        )
        assert len(result) == 2
        assert {loc.aggregate_region for loc in result} == {"us-southwest", "us-east"}

    def test_apply_filters_aggregate_region_list_empty(self, sample_locations):
        """Test _apply_filters with empty aggregate_region filter list."""
        result = self.client._apply_filters(sample_locations, {"aggregate_region": []})
        assert len(result) == 0

    def test_apply_filters_multiple_filters(self, sample_locations):
        """Test _apply_filters with multiple filters."""
        result = self.client._apply_filters(
            sample_locations,
            {
                "continent": "North America",
                "region": "us-west2",
            },
        )
        assert len(result) == 1
        assert result[0].continent == "North America"
        assert result[0].region == "us-west2"

    def test_apply_filters_case_insensitive(self, sample_locations):
        """Test _apply_filters case insensitivity."""
        result = self.client._apply_filters(sample_locations, {"continent": "north america"})
        assert len(result) == 2
        assert all(loc.continent == "North America" for loc in result)


# -------------------- Integration Tests --------------------


@pytest.mark.integration
class TestNetworkLocationsList(TestNetworkLocationsBase):
    """Integration tests for listing NetworkLocations."""

    @pytest.fixture
    def sample_api_response(self):
        """Return a sample API response for network locations."""
        return [
            {
                "value": "us-west-1",
                "display": "US West",
                "continent": "North America",
                "latitude": 37.7749,
                "longitude": -122.4194,
                "region": "us-west2",
                "aggregate_region": "us-southwest",
            },
            {
                "value": "us-east-1",
                "display": "US East",
                "continent": "North America",
                "latitude": 37.45244,
                "longitude": -76.41686,
                "region": "us-east4",
                "aggregate_region": "us-east",
            },
            {
                "value": "eu-central-1",
                "display": "Germany Central",
                "continent": "Europe",
                "latitude": 50.11208,
                "longitude": 8.68342,
                "region": "europe-west3",
                "aggregate_region": "europe-central",
            },
        ]

    def test_list_success(self, sample_api_response):
        """Test list method success."""
        self.mock_scm.get.return_value = sample_api_response
        result = self.client.list()

        self.mock_scm.get.assert_called_once_with(
            NetworkLocations.ENDPOINT,
        )
        assert len(result) == len(sample_api_response)
        assert all(isinstance(loc, NetworkLocationModel) for loc in result)
        assert result[0].value == "us-west-1"

    def test_list_invalid_response_not_list(self):
        """Test list method with invalid response (not a list)."""
        self.mock_scm.get.return_value = {"data": []}  # Not a list
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list()
        assert "Response is not a list" in str(excinfo.value)

    def test_list_with_filters(self, sample_api_response):
        """Test list method with filters."""
        self.mock_scm.get.return_value = sample_api_response
        result = self.client.list(continent="North America")
        assert len(result) == 2
        assert all(loc.continent == "North America" for loc in result)


@pytest.mark.integration
class TestNetworkLocationsFetch(TestNetworkLocationsBase):
    """Integration tests for fetching NetworkLocations."""

    @pytest.fixture
    def sample_api_response(self):
        """Return a sample API response for network locations."""
        return [
            {
                "value": "us-west-1",
                "display": "US West",
                "continent": "North America",
                "latitude": 37.7749,
                "longitude": -122.4194,
                "region": "us-west2",
                "aggregate_region": "us-southwest",
            },
            {
                "value": "us-east-1",
                "display": "US East",
                "continent": "North America",
                "latitude": 37.45244,
                "longitude": -76.41686,
                "region": "us-east4",
                "aggregate_region": "us-east",
            },
            {
                "value": "eu-central-1",
                "display": "Germany Central",
                "continent": "Europe",
                "latitude": 50.11208,
                "longitude": 8.68342,
                "region": "europe-west3",
                "aggregate_region": "europe-central",
            },
        ]

    def test_fetch_success(self, sample_api_response):
        """Test fetch method success."""
        self.mock_scm.get.return_value = sample_api_response
        result = self.client.fetch("us-west-1")

        self.mock_scm.get.assert_called_once_with(
            NetworkLocations.ENDPOINT,
        )
        assert result.value == "us-west-1"
        assert result.display == "US West"

    def test_fetch_empty_value(self):
        """Test fetch method with empty value."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            self.client.fetch("")
        assert '"value" is not allowed to be empty' in str(excinfo.value)

    def test_fetch_not_found(self, sample_api_response):
        """Test fetch method with non-existent value."""
        self.mock_scm.get.return_value = sample_api_response
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch("non-existent-value")
        assert "Object not found" in str(excinfo.value)

    @patch("logging.Logger.warning")
    def test_fetch_multiple_matches(self, mock_warning):
        """Test fetch method with multiple matching values."""
        # Create duplicate entries with the same value but different display names
        duplicate_locations = [
            {
                "value": "duplicate-value",
                "display": "Display 1",
                "continent": "North America",
                "latitude": 37.7749,
                "longitude": -122.4194,
                "region": "us-west2",
                "aggregate_region": "us-southwest",
            },
            {
                "value": "duplicate-value",
                "display": "Display 2",
                "continent": "North America",
                "latitude": 37.7749,
                "longitude": -122.4194,
                "region": "us-west2",
                "aggregate_region": "us-southwest",
            },
        ]
        self.mock_scm.get.return_value = duplicate_locations
        result = self.client.fetch("duplicate-value")

        assert result.value == "duplicate-value"
        assert result.display == "Display 1"  # First match should be returned
        mock_warning.assert_called_once()
        assert "Multiple network locations found with value 'duplicate-value'" in str(
            mock_warning.call_args
        )
