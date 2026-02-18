"""Unit tests for the RoutePrefixList class."""

from unittest.mock import MagicMock
import uuid

import pytest

from scm.config.network import RoutePrefixList
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.network import (
    RoutePrefixListResponseModel,
    RoutePrefixListUpdateModel,
)


@pytest.fixture
def sample_route_prefix_list_dict():
    """Return a sample route prefix list dictionary."""
    return {
        "id": str(uuid.uuid4()),
        "name": "test-prefix-list",
        "folder": "Test Folder",
        "description": "Test route prefix list",
        "ipv4": {
            "ipv4_entry": [
                {
                    "name": 10,
                    "action": "permit",
                    "prefix": {
                        "entry": {
                            "network": "10.0.0.0/8",
                            "greater_than_or_equal": 16,
                            "less_than_or_equal": 24,
                        }
                    },
                }
            ]
        },
    }


@pytest.fixture
def sample_route_prefix_list_response(sample_route_prefix_list_dict):
    """Return a sample RoutePrefixListResponseModel."""
    return RoutePrefixListResponseModel(**sample_route_prefix_list_dict)


@pytest.mark.usefixtures("load_env")
class TestRoutePrefixListBase:
    """Base class for RoutePrefixList tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = RoutePrefixList(self.mock_scm, max_limit=5000)


class TestRoutePrefixList(TestRoutePrefixListBase):
    """Test suite for RoutePrefixList class."""

    def test_init(self):
        """Test initialization of RoutePrefixList class."""
        client = RoutePrefixList(self.mock_scm)
        assert client.api_client == self.mock_scm
        assert client.ENDPOINT == "/config/network/v1/route-prefix-lists"
        assert client.max_limit == client.DEFAULT_MAX_LIMIT

    def test_init_with_custom_max_limit(self):
        """Test initialization with custom max_limit."""
        client = RoutePrefixList(self.mock_scm, max_limit=1000)
        assert client.max_limit == 1000

    def test_init_with_invalid_max_limit(self):
        """Test initialization with invalid max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            RoutePrefixList(self.mock_scm, max_limit="invalid")
        assert "Invalid max_limit type" in str(excinfo.value)

    def test_init_with_negative_max_limit(self):
        """Test initialization with negative max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            RoutePrefixList(self.mock_scm, max_limit=-1)
        assert "Invalid max_limit value" in str(excinfo.value)

    def test_init_with_excessive_max_limit(self):
        """Test initialization with excessive max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            client = RoutePrefixList(self.mock_scm)
            client.max_limit = 10000
        assert "max_limit exceeds maximum allowed value" in str(excinfo.value)

    def test_get(self, sample_route_prefix_list_dict):
        """Test get method."""
        self.mock_scm.get.return_value = sample_route_prefix_list_dict
        object_id = sample_route_prefix_list_dict["id"]

        result = self.client.get(object_id)

        expected_endpoint = f"{self.client.ENDPOINT}/{object_id}"
        self.mock_scm.get.assert_called_once_with(expected_endpoint)

        assert isinstance(result, RoutePrefixListResponseModel)
        assert result.id == uuid.UUID(object_id)
        assert result.name == sample_route_prefix_list_dict["name"]

    def test_update(self, sample_route_prefix_list_dict):
        """Test update method."""
        self.mock_scm.put.return_value = sample_route_prefix_list_dict
        object_id = sample_route_prefix_list_dict["id"]

        update_model = RoutePrefixListUpdateModel(**sample_route_prefix_list_dict)
        result = self.client.update(update_model)

        expected_endpoint = f"{self.client.ENDPOINT}/{object_id}"
        self.mock_scm.put.assert_called_once()
        call_args = self.mock_scm.put.call_args
        assert call_args[0][0] == expected_endpoint
        assert "id" not in call_args[1]["json"]

        assert isinstance(result, RoutePrefixListResponseModel)
        assert result.id == uuid.UUID(object_id)
        assert result.name == sample_route_prefix_list_dict["name"]

    def test_list(self, sample_route_prefix_list_dict):
        """Test list method."""
        self.mock_scm.get.return_value = {
            "data": [sample_route_prefix_list_dict],
            "limit": 20,
            "offset": 0,
            "total": 1,
        }

        result = self.client.list(folder="Test Folder")

        self.mock_scm.get.assert_called_once()
        call_args = self.mock_scm.get.call_args
        assert call_args[0][0] == self.client.ENDPOINT
        assert call_args[1]["params"]["folder"] == "Test Folder"

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], RoutePrefixListResponseModel)
        assert result[0].name == sample_route_prefix_list_dict["name"]

    def test_list_response_errors(self):
        """Test list method error handling for invalid responses."""
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(folder="Test Folder")
        assert "Response is not a dictionary" in str(excinfo.value)

        self.mock_scm.get.return_value = {"no_data": "field"}
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(folder="Test Folder")
        assert '"data" field missing in the response' in str(excinfo.value)

        self.mock_scm.get.return_value = {"data": "not a list"}
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(folder="Test Folder")
        assert '"data" field must be a list' in str(excinfo.value)

    def test_list_pagination(self, sample_route_prefix_list_dict):
        """Test list method pagination."""
        pl1 = sample_route_prefix_list_dict.copy()
        pl1["id"] = str(uuid.uuid4())
        pl1["name"] = "pl1"

        pl2 = sample_route_prefix_list_dict.copy()
        pl2["id"] = str(uuid.uuid4())
        pl2["name"] = "pl2"

        self.mock_scm.get.side_effect = [
            {"data": [pl1], "limit": 1, "offset": 0, "total": 2},
            {"data": [pl2], "limit": 1, "offset": 1, "total": 2},
            {"data": [], "limit": 1, "offset": 2, "total": 2},
        ]

        self.client.max_limit = 1
        result = self.client.list(folder="Test Folder")

        assert self.mock_scm.get.call_count == 3
        assert len(result) == 2
        pl_names = [p.name for p in result]
        assert "pl1" in pl_names
        assert "pl2" in pl_names

    def test_list_with_exclusions(self, sample_route_prefix_list_dict):
        """Test list method with exclusion filters."""
        # Create multiple prefix lists with different containers
        pl1 = sample_route_prefix_list_dict.copy()
        pl1["id"] = str(uuid.uuid4())
        pl1["name"] = "pl1"
        pl1["folder"] = "Folder1"

        pl2 = sample_route_prefix_list_dict.copy()
        pl2["id"] = str(uuid.uuid4())
        pl2["name"] = "pl2"
        pl2["folder"] = "Folder2"

        pl3 = sample_route_prefix_list_dict.copy()
        pl3["id"] = str(uuid.uuid4())
        pl3["name"] = "pl3"
        pl3["folder"] = "Folder1"
        pl3["snippet"] = "Snippet1"

        pl4 = sample_route_prefix_list_dict.copy()
        pl4["id"] = str(uuid.uuid4())
        pl4["name"] = "pl4"
        pl4["folder"] = "Folder1"
        pl4["device"] = "Device1"

        self.mock_scm.get.return_value = {
            "data": [pl1, pl2, pl3, pl4],
            "limit": 100,
            "offset": 0,
            "total": 4,
        }

        # Test exact_match filter
        result = self.client.list(folder="Folder1", exact_match=True)
        assert len(result) == 3  # Should match pl1, pl3, pl4

        # Test exclude_folders filter
        result = self.client.list(folder="Folder1", exclude_folders=["Folder2"])
        assert len(result) == 3  # Should exclude only pl2

        # Test exclude_snippets filter
        result = self.client.list(folder="Folder1", exclude_snippets=["Snippet1"])
        assert len(result) == 3  # Should exclude pl3

        # Test exclude_devices filter
        result = self.client.list(folder="Folder1", exclude_devices=["Device1"])
        assert len(result) == 3  # Should exclude pl4

        # Test combining multiple exclusions
        result = self.client.list(
            folder="Folder1", exclude_snippets=["Snippet1"], exclude_devices=["Device1"]
        )
        assert len(result) == 2  # Should exclude pl3 and pl4

    def test_list_with_empty_folder(self):
        """Test list method with empty folder parameter."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            self.client.list(folder="")
        assert '"folder" is not allowed to be empty' in str(excinfo.value)

    def test_list_with_missing_container(self):
        """Test list method with missing container parameter."""
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list()
        assert "Invalid container parameters" in str(excinfo.value)

    def test_list_with_multiple_containers(self):
        """Test list method with multiple container parameters."""
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(folder="Test Folder", snippet="Test Snippet")
        assert "Invalid container parameters" in str(excinfo.value)

    def test_fetch(self, sample_route_prefix_list_dict):
        """Test fetch method."""
        self.mock_scm.get.return_value = sample_route_prefix_list_dict

        result = self.client.fetch(name="test-prefix-list", folder="Test Folder")

        self.mock_scm.get.assert_called_once()
        call_args = self.mock_scm.get.call_args
        assert call_args[0][0] == self.client.ENDPOINT
        assert call_args[1]["params"]["name"] == "test-prefix-list"
        assert call_args[1]["params"]["folder"] == "Test Folder"

        assert isinstance(result, RoutePrefixListResponseModel)
        assert result.name == sample_route_prefix_list_dict["name"]

    def test_fetch_with_empty_name(self):
        """Test fetch method with empty name parameter."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            self.client.fetch(name="", folder="Test Folder")
        assert '"name" is not allowed to be empty' in str(excinfo.value)

    def test_fetch_with_empty_folder(self):
        """Test fetch method with empty folder parameter."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            self.client.fetch(name="test-prefix-list", folder="")
        assert '"folder" is not allowed to be empty' in str(excinfo.value)

    def test_fetch_with_missing_container(self):
        """Test fetch method with missing container parameter."""
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-prefix-list")
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            excinfo.value
        )

    def test_fetch_with_invalid_response(self):
        """Test fetch method with invalid response."""
        self.mock_scm.get.return_value = {"name": "test-prefix-list"}

        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-prefix-list", folder="Test Folder")
        assert "Response has invalid structure" in str(excinfo.value)

    def test_fetch_response_errors(self):
        """Test fetch method error handling for invalid responses."""
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-prefix-list", folder="Test Folder")
        assert "Response is not a dictionary" in str(excinfo.value)

        valid_uuid = str(uuid.uuid4())
        self.mock_scm.get.return_value = {"data": [{"id": valid_uuid, "name": "test-prefix-list"}]}
        result = self.client.fetch(name="test-prefix-list", folder="Test Folder")
        assert isinstance(result, RoutePrefixListResponseModel)
        assert result.id == uuid.UUID(valid_uuid)

        self.mock_scm.get.return_value = {"data": []}
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-prefix-list", folder="Test Folder")
        assert "No matching route prefix list found" in str(excinfo.value)

        self.mock_scm.get.return_value = {
            "data": [{"name": "test-prefix-list", "folder": "Test Folder"}]
        }
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-prefix-list", folder="Test Folder")
        assert "Response data item missing 'id' field" in str(excinfo.value)

    def test_fetch_with_original_response_format(self, sample_route_prefix_list_dict):
        """Test fetch method with original response format (direct object with id field)."""
        self.mock_scm.get.return_value = sample_route_prefix_list_dict

        result = self.client.fetch(
            name=sample_route_prefix_list_dict["name"],
            folder=sample_route_prefix_list_dict["folder"],
        )

        assert isinstance(result, RoutePrefixListResponseModel)
        assert result.id == uuid.UUID(sample_route_prefix_list_dict["id"])
        assert result.name == sample_route_prefix_list_dict["name"]

    def test_fetch_with_list_response_format(self, sample_route_prefix_list_dict):
        """Test fetch method with list response format (data array with objects)."""
        pl_data = sample_route_prefix_list_dict.copy()

        self.mock_scm.get.return_value = {
            "data": [pl_data],
            "limit": 20,
            "offset": 0,
            "total": 1,
        }

        result = self.client.fetch(name=pl_data["name"], folder=pl_data["folder"])

        assert isinstance(result, RoutePrefixListResponseModel)
        assert result.id == uuid.UUID(pl_data["id"])

    def test_fetch_with_multiple_objects_in_data(self, sample_route_prefix_list_dict, monkeypatch):
        """Test fetch method when data array contains multiple objects."""
        from unittest.mock import MagicMock

        pl1 = sample_route_prefix_list_dict.copy()
        pl1["id"] = str(uuid.uuid4())
        pl1["name"] = "pl1"

        pl2 = sample_route_prefix_list_dict.copy()
        pl2["id"] = str(uuid.uuid4())
        pl2["name"] = "pl2"

        self.mock_scm.get.return_value = {
            "data": [pl1, pl2],
            "limit": 20,
            "offset": 0,
            "total": 2,
        }

        mock_warning = MagicMock()
        monkeypatch.setattr(self.client.logger, "warning", mock_warning)

        result = self.client.fetch(name=pl1["name"], folder=pl1["folder"])

        assert isinstance(result, RoutePrefixListResponseModel)
        assert result.id == uuid.UUID(pl1["id"])

        mock_warning.assert_called_once()
        call_args = mock_warning.call_args[0][0]
        assert "Multiple route prefix lists found" in call_args
