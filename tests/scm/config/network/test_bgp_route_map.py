"""Unit tests for the BgpRouteMap class."""

from unittest.mock import MagicMock
import uuid

import pytest

from scm.config.network import BgpRouteMap
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.network import (
    BgpRouteMapCreateModel,
    BgpRouteMapResponseModel,
    BgpRouteMapUpdateModel,
)


@pytest.fixture
def sample_bgp_route_map_dict():
    """Return a sample BGP route map dictionary."""
    return {
        "id": str(uuid.uuid4()),
        "name": "test-bgp-route-map",
        "folder": "Test Folder",
        "route_map": [
            {
                "name": 10,
                "action": "permit",
                "match": {"as_path_access_list": "my-as-path", "metric": 100},
                "set": {"local_preference": 200, "weight": 100},
            },
        ],
    }


@pytest.fixture
def sample_bgp_route_map_response(sample_bgp_route_map_dict):
    """Return a sample BgpRouteMapResponseModel."""
    return BgpRouteMapResponseModel(**sample_bgp_route_map_dict)


@pytest.mark.usefixtures("load_env")
class TestBgpRouteMapBase:
    """Base class for BgpRouteMap tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = BgpRouteMap(self.mock_scm, max_limit=5000)


class TestBgpRouteMap(TestBgpRouteMapBase):
    """Test suite for BgpRouteMap class."""

    def test_init(self):
        """Test initialization of BgpRouteMap class."""
        client = BgpRouteMap(self.mock_scm)
        assert client.api_client == self.mock_scm
        assert client.ENDPOINT == "/config/network/v1/bgp-route-maps"
        assert client.max_limit == client.DEFAULT_MAX_LIMIT

    def test_init_with_custom_max_limit(self):
        """Test initialization with custom max_limit."""
        client = BgpRouteMap(self.mock_scm, max_limit=1000)
        assert client.max_limit == 1000

    def test_init_with_invalid_max_limit(self):
        """Test initialization with invalid max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            BgpRouteMap(self.mock_scm, max_limit="invalid")
        assert "Invalid max_limit type" in str(excinfo.value)

    def test_init_with_negative_max_limit(self):
        """Test initialization with negative max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            BgpRouteMap(self.mock_scm, max_limit=-1)
        assert "Invalid max_limit value" in str(excinfo.value)

    def test_init_with_excessive_max_limit(self):
        """Test initialization with excessive max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            client = BgpRouteMap(self.mock_scm)
            client.max_limit = 10000
        assert "max_limit exceeds maximum allowed value" in str(excinfo.value)

    def test_create(self, sample_bgp_route_map_dict):
        """Test create method."""
        self.mock_scm.post.return_value = sample_bgp_route_map_dict

        # Create a copy without the ID for create operation
        create_data = sample_bgp_route_map_dict.copy()
        create_data.pop("id")

        result = self.client.create(create_data)

        # Check that correct API call was made
        self.mock_scm.post.assert_called_once()
        call_args = self.mock_scm.post.call_args
        assert call_args[0][0] == self.client.ENDPOINT

        # Check payload validation
        payload = call_args[1]["json"]
        BgpRouteMapCreateModel(**payload)

        # Check result
        assert isinstance(result, BgpRouteMapResponseModel)
        assert result.name == sample_bgp_route_map_dict["name"]
        assert result.folder == sample_bgp_route_map_dict["folder"]

    def test_get(self, sample_bgp_route_map_dict):
        """Test get method."""
        self.mock_scm.get.return_value = sample_bgp_route_map_dict
        object_id = sample_bgp_route_map_dict["id"]

        result = self.client.get(object_id)

        expected_endpoint = f"{self.client.ENDPOINT}/{object_id}"
        self.mock_scm.get.assert_called_once_with(expected_endpoint)

        assert isinstance(result, BgpRouteMapResponseModel)
        assert result.id == uuid.UUID(object_id)
        assert result.name == sample_bgp_route_map_dict["name"]

    def test_update(self, sample_bgp_route_map_dict):
        """Test update method."""
        self.mock_scm.put.return_value = sample_bgp_route_map_dict
        object_id = sample_bgp_route_map_dict["id"]

        update_model = BgpRouteMapUpdateModel(**sample_bgp_route_map_dict)
        result = self.client.update(update_model)

        expected_endpoint = f"{self.client.ENDPOINT}/{object_id}"
        self.mock_scm.put.assert_called_once()
        call_args = self.mock_scm.put.call_args
        assert call_args[0][0] == expected_endpoint
        assert "id" not in call_args[1]["json"]

        assert isinstance(result, BgpRouteMapResponseModel)
        assert result.id == uuid.UUID(object_id)
        assert result.name == sample_bgp_route_map_dict["name"]

    def test_list(self, sample_bgp_route_map_dict):
        """Test list method."""
        self.mock_scm.get.return_value = {
            "data": [sample_bgp_route_map_dict],
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
        assert isinstance(result[0], BgpRouteMapResponseModel)
        assert result[0].name == sample_bgp_route_map_dict["name"]

    def test_list_response_errors(self):
        """Test list method error handling for invalid responses."""
        # Test non-list, non-dictionary response
        self.mock_scm.get.return_value = "not a dictionary"
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

    def test_list_pagination(self, sample_bgp_route_map_dict):
        """Test list method pagination."""
        profile1 = sample_bgp_route_map_dict.copy()
        profile1["id"] = str(uuid.uuid4())
        profile1["name"] = "profile1"

        profile2 = sample_bgp_route_map_dict.copy()
        profile2["id"] = str(uuid.uuid4())
        profile2["name"] = "profile2"

        self.mock_scm.get.side_effect = [
            {"data": [profile1], "limit": 1, "offset": 0, "total": 2},
            {"data": [profile2], "limit": 1, "offset": 1, "total": 2},
            {"data": [], "limit": 1, "offset": 2, "total": 2},
        ]

        self.client.max_limit = 1
        result = self.client.list(folder="Test Folder")

        assert self.mock_scm.get.call_count == 3
        assert len(result) == 2
        profile_names = [p.name for p in result]
        assert "profile1" in profile_names
        assert "profile2" in profile_names

    def test_list_with_exclusions(self, sample_bgp_route_map_dict):
        """Test list method with exclusion filters."""
        # Create multiple profiles with different containers
        profile1 = sample_bgp_route_map_dict.copy()
        profile1["id"] = str(uuid.uuid4())
        profile1["name"] = "profile1"
        profile1["folder"] = "Folder1"

        profile2 = sample_bgp_route_map_dict.copy()
        profile2["id"] = str(uuid.uuid4())
        profile2["name"] = "profile2"
        profile2["folder"] = "Folder2"

        profile3 = sample_bgp_route_map_dict.copy()
        profile3["id"] = str(uuid.uuid4())
        profile3["name"] = "profile3"
        profile3["folder"] = "Folder1"
        profile3["snippet"] = "Snippet1"

        profile4 = sample_bgp_route_map_dict.copy()
        profile4["id"] = str(uuid.uuid4())
        profile4["name"] = "profile4"
        profile4["folder"] = "Folder1"
        profile4["device"] = "Device1"

        self.mock_scm.get.return_value = {
            "data": [profile1, profile2, profile3, profile4],
            "limit": 100,
            "offset": 0,
            "total": 4,
        }

        # Test exact_match filter
        result = self.client.list(folder="Folder1", exact_match=True)
        assert len(result) == 3  # Should match profile1, profile3, profile4

        # Test exclude_folders filter
        result = self.client.list(folder="Folder1", exclude_folders=["Folder2"])
        assert len(result) == 3  # Should exclude only profile2

        # Test exclude_snippets filter
        result = self.client.list(folder="Folder1", exclude_snippets=["Snippet1"])
        assert len(result) == 3  # Should exclude profile3

        # Test exclude_devices filter
        result = self.client.list(folder="Folder1", exclude_devices=["Device1"])
        assert len(result) == 3  # Should exclude profile4

        # Test combining multiple exclusions
        result = self.client.list(
            folder="Folder1", exclude_snippets=["Snippet1"], exclude_devices=["Device1"]
        )
        assert len(result) == 2  # Should exclude profile3 and profile4

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

    def test_fetch(self, sample_bgp_route_map_dict):
        """Test fetch method."""
        self.mock_scm.get.return_value = sample_bgp_route_map_dict

        result = self.client.fetch(name="test-bgp-route-map", folder="Test Folder")

        self.mock_scm.get.assert_called_once()
        call_args = self.mock_scm.get.call_args
        assert call_args[0][0] == self.client.ENDPOINT
        assert call_args[1]["params"]["name"] == "test-bgp-route-map"
        assert call_args[1]["params"]["folder"] == "Test Folder"

        assert isinstance(result, BgpRouteMapResponseModel)
        assert result.name == sample_bgp_route_map_dict["name"]

    def test_fetch_with_empty_name(self):
        """Test fetch method with empty name parameter."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            self.client.fetch(name="", folder="Test Folder")
        assert '"name" is not allowed to be empty' in str(excinfo.value)

    def test_fetch_with_empty_folder(self):
        """Test fetch method with empty folder parameter."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            self.client.fetch(name="test-bgp-route-map", folder="")
        assert '"folder" is not allowed to be empty' in str(excinfo.value)

    def test_fetch_with_missing_container(self):
        """Test fetch method with missing container parameter."""
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-bgp-route-map")
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            excinfo.value
        )

    def test_fetch_with_invalid_response(self):
        """Test fetch method with invalid response."""
        self.mock_scm.get.return_value = {"name": "test-bgp-route-map"}

        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-bgp-route-map", folder="Test Folder")
        assert "Response has invalid structure" in str(excinfo.value)

    def test_fetch_response_errors(self):
        """Test fetch method error handling for invalid responses."""
        # Test non-list, non-dictionary response
        self.mock_scm.get.return_value = "not a dictionary"
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-bgp-route-map", folder="Test Folder")
        assert "Response is not a dictionary" in str(excinfo.value)

        valid_uuid = str(uuid.uuid4())
        self.mock_scm.get.return_value = {
            "data": [{"id": valid_uuid, "name": "test-bgp-route-map"}]
        }
        result = self.client.fetch(name="test-bgp-route-map", folder="Test Folder")
        assert isinstance(result, BgpRouteMapResponseModel)
        assert result.id == uuid.UUID(valid_uuid)

        self.mock_scm.get.return_value = {"data": []}
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-bgp-route-map", folder="Test Folder")
        assert "No matching BGP route map found" in str(excinfo.value)

        self.mock_scm.get.return_value = {
            "data": [{"name": "test-bgp-route-map", "folder": "Test Folder"}]
        }
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-bgp-route-map", folder="Test Folder")
        assert "Response data item missing 'id' field" in str(excinfo.value)

    def test_fetch_with_original_response_format(self, sample_bgp_route_map_dict):
        """Test fetch method with original response format (direct object with id field)."""
        self.mock_scm.get.return_value = sample_bgp_route_map_dict

        result = self.client.fetch(
            name=sample_bgp_route_map_dict["name"],
            folder=sample_bgp_route_map_dict["folder"],
        )

        assert isinstance(result, BgpRouteMapResponseModel)
        assert result.id == uuid.UUID(sample_bgp_route_map_dict["id"])
        assert result.name == sample_bgp_route_map_dict["name"]

    def test_fetch_with_list_response_format(self, sample_bgp_route_map_dict):
        """Test fetch method with list response format (data array with objects)."""
        profile_data = sample_bgp_route_map_dict.copy()

        self.mock_scm.get.return_value = {
            "data": [profile_data],
            "limit": 20,
            "offset": 0,
            "total": 1,
        }

        result = self.client.fetch(name=profile_data["name"], folder=profile_data["folder"])

        assert isinstance(result, BgpRouteMapResponseModel)
        assert result.id == uuid.UUID(profile_data["id"])

    def test_fetch_with_multiple_objects_in_data(self, sample_bgp_route_map_dict, monkeypatch):
        """Test fetch method when data array contains multiple objects."""
        from unittest.mock import MagicMock

        profile1 = sample_bgp_route_map_dict.copy()
        profile1["id"] = str(uuid.uuid4())
        profile1["name"] = "profile1"

        profile2 = sample_bgp_route_map_dict.copy()
        profile2["id"] = str(uuid.uuid4())
        profile2["name"] = "profile2"

        self.mock_scm.get.return_value = {
            "data": [profile1, profile2],
            "limit": 20,
            "offset": 0,
            "total": 2,
        }

        mock_warning = MagicMock()
        monkeypatch.setattr(self.client.logger, "warning", mock_warning)

        result = self.client.fetch(name=profile1["name"], folder=profile1["folder"])

        assert isinstance(result, BgpRouteMapResponseModel)
        assert result.id == uuid.UUID(profile1["id"])

        mock_warning.assert_called_once()
        call_args = mock_warning.call_args[0][0]
        assert "Multiple BGP route maps found" in call_args

    def test_fetch_with_raw_list_response(self, sample_bgp_route_map_dict):
        """Test fetch method when API returns raw list instead of dict."""
        profile_data = sample_bgp_route_map_dict.copy()
        self.mock_scm.get.return_value = [profile_data]

        result = self.client.fetch(name=profile_data["name"], folder=profile_data["folder"])

        assert isinstance(result, BgpRouteMapResponseModel)
        assert result.id == uuid.UUID(profile_data["id"])
        assert result.name == profile_data["name"]

    def test_fetch_with_raw_list_response_empty(self):
        """Test fetch method when API returns empty raw list."""
        self.mock_scm.get.return_value = []

        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="nonexistent", folder="Test Folder")
        assert "No matching resource found" in str(excinfo.value)

    def test_fetch_with_raw_list_response_multiple(self, sample_bgp_route_map_dict, monkeypatch):
        """Test fetch method when API returns raw list with multiple items."""
        profile1 = sample_bgp_route_map_dict.copy()
        profile1["id"] = str(uuid.uuid4())
        profile1["name"] = "profile1"

        profile2 = sample_bgp_route_map_dict.copy()
        profile2["id"] = str(uuid.uuid4())
        profile2["name"] = "profile2"

        self.mock_scm.get.return_value = [profile1, profile2]

        mock_warning = MagicMock()
        monkeypatch.setattr(self.client.logger, "warning", mock_warning)

        result = self.client.fetch(name="profile1", folder="Test Folder")

        assert isinstance(result, BgpRouteMapResponseModel)
        assert result.id == uuid.UUID(profile1["id"])
        mock_warning.assert_called_once()

    def test_list_with_raw_list_response(self, sample_bgp_route_map_dict):
        """Test list method when API returns raw list instead of dict with data wrapper."""
        profile1 = sample_bgp_route_map_dict.copy()
        profile1["id"] = str(uuid.uuid4())
        profile1["name"] = "profile1"

        profile2 = sample_bgp_route_map_dict.copy()
        profile2["id"] = str(uuid.uuid4())
        profile2["name"] = "profile2"

        self.mock_scm.get.return_value = [profile1, profile2]

        result = self.client.list(folder="Test Folder")

        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(r, BgpRouteMapResponseModel) for r in result)

    def test_delete(self, sample_bgp_route_map_dict):
        """Test delete method."""
        object_id = sample_bgp_route_map_dict["id"]

        self.client.delete(object_id)

        # Check that correct API call was made
        expected_endpoint = f"{self.client.ENDPOINT}/{object_id}"
        self.mock_scm.delete.assert_called_once_with(expected_endpoint)
