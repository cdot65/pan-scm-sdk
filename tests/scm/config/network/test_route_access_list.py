"""Unit tests for the RouteAccessList class."""

from unittest.mock import MagicMock
import uuid

import pytest

from scm.config.network import RouteAccessList
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.network import (
    RouteAccessListCreateModel,
    RouteAccessListResponseModel,
    RouteAccessListUpdateModel,
)


@pytest.fixture
def sample_route_access_list_dict():
    """Return a sample route access list dictionary."""
    return {
        "id": str(uuid.uuid4()),
        "name": "test-acl",
        "folder": "Test Folder",
        "description": "Test route access list",
        "type": {
            "ipv4": {
                "ipv4_entry": [
                    {
                        "name": 10,
                        "action": "permit",
                        "source_address": {
                            "address": "10.0.0.0",
                            "wildcard": "0.0.255.255",
                        },
                    }
                ]
            }
        },
    }


@pytest.fixture
def sample_route_access_list_response(sample_route_access_list_dict):
    """Return a sample RouteAccessListResponseModel."""
    return RouteAccessListResponseModel(**sample_route_access_list_dict)


@pytest.mark.usefixtures("load_env")
class TestRouteAccessListBase:
    """Base class for RouteAccessList tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = RouteAccessList(self.mock_scm, max_limit=5000)


class TestRouteAccessList(TestRouteAccessListBase):
    """Test suite for RouteAccessList class."""

    def test_init(self):
        """Test initialization of RouteAccessList class."""
        client = RouteAccessList(self.mock_scm)
        assert client.api_client == self.mock_scm
        assert client.ENDPOINT == "/config/network/v1/route-access-lists"
        assert client.max_limit == client.DEFAULT_MAX_LIMIT

    def test_init_with_custom_max_limit(self):
        """Test initialization with custom max_limit."""
        client = RouteAccessList(self.mock_scm, max_limit=1000)
        assert client.max_limit == 1000

    def test_init_with_invalid_max_limit(self):
        """Test initialization with invalid max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            RouteAccessList(self.mock_scm, max_limit="invalid")
        assert "Invalid max_limit type" in str(excinfo.value)

    def test_init_with_negative_max_limit(self):
        """Test initialization with negative max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            RouteAccessList(self.mock_scm, max_limit=-1)
        assert "Invalid max_limit value" in str(excinfo.value)

    def test_init_with_excessive_max_limit(self):
        """Test initialization with excessive max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            client = RouteAccessList(self.mock_scm)
            client.max_limit = 10000
        assert "max_limit exceeds maximum allowed value" in str(excinfo.value)

    def test_create(self, sample_route_access_list_dict):
        """Test create method."""
        self.mock_scm.post.return_value = sample_route_access_list_dict

        # Create a copy without the ID for create operation
        create_data = sample_route_access_list_dict.copy()
        create_data.pop("id")

        result = self.client.create(create_data)

        # Check that correct API call was made
        self.mock_scm.post.assert_called_once()
        call_args = self.mock_scm.post.call_args
        assert call_args[0][0] == self.client.ENDPOINT

        # Check payload validation
        payload = call_args[1]["json"]
        RouteAccessListCreateModel(**payload)

        # Check result
        assert isinstance(result, RouteAccessListResponseModel)
        assert result.name == sample_route_access_list_dict["name"]
        assert result.folder == sample_route_access_list_dict["folder"]

    def test_get(self, sample_route_access_list_dict):
        """Test get method."""
        self.mock_scm.get.return_value = sample_route_access_list_dict
        object_id = sample_route_access_list_dict["id"]

        result = self.client.get(object_id)

        expected_endpoint = f"{self.client.ENDPOINT}/{object_id}"
        self.mock_scm.get.assert_called_once_with(expected_endpoint)

        assert isinstance(result, RouteAccessListResponseModel)
        assert result.id == uuid.UUID(object_id)
        assert result.name == sample_route_access_list_dict["name"]

    def test_update(self, sample_route_access_list_dict):
        """Test update method."""
        self.mock_scm.put.return_value = sample_route_access_list_dict
        object_id = sample_route_access_list_dict["id"]

        update_model = RouteAccessListUpdateModel(**sample_route_access_list_dict)
        result = self.client.update(update_model)

        expected_endpoint = f"{self.client.ENDPOINT}/{object_id}"
        self.mock_scm.put.assert_called_once()
        call_args = self.mock_scm.put.call_args
        assert call_args[0][0] == expected_endpoint
        assert "id" not in call_args[1]["json"]

        assert isinstance(result, RouteAccessListResponseModel)
        assert result.id == uuid.UUID(object_id)
        assert result.name == sample_route_access_list_dict["name"]

    def test_list(self, sample_route_access_list_dict):
        """Test list method."""
        self.mock_scm.get.return_value = {
            "data": [sample_route_access_list_dict],
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
        assert isinstance(result[0], RouteAccessListResponseModel)
        assert result[0].name == sample_route_access_list_dict["name"]

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

    def test_list_pagination(self, sample_route_access_list_dict):
        """Test list method pagination."""
        acl1 = sample_route_access_list_dict.copy()
        acl1["id"] = str(uuid.uuid4())
        acl1["name"] = "acl1"

        acl2 = sample_route_access_list_dict.copy()
        acl2["id"] = str(uuid.uuid4())
        acl2["name"] = "acl2"

        self.mock_scm.get.side_effect = [
            {"data": [acl1], "limit": 1, "offset": 0, "total": 2},
            {"data": [acl2], "limit": 1, "offset": 1, "total": 2},
            {"data": [], "limit": 1, "offset": 2, "total": 2},
        ]

        self.client.max_limit = 1
        result = self.client.list(folder="Test Folder")

        assert self.mock_scm.get.call_count == 3
        assert len(result) == 2
        acl_names = [a.name for a in result]
        assert "acl1" in acl_names
        assert "acl2" in acl_names

    def test_list_with_exclusions(self, sample_route_access_list_dict):
        """Test list method with exclusion filters."""
        # Create multiple ACLs with different containers
        acl1 = sample_route_access_list_dict.copy()
        acl1["id"] = str(uuid.uuid4())
        acl1["name"] = "acl1"
        acl1["folder"] = "Folder1"

        acl2 = sample_route_access_list_dict.copy()
        acl2["id"] = str(uuid.uuid4())
        acl2["name"] = "acl2"
        acl2["folder"] = "Folder2"

        acl3 = sample_route_access_list_dict.copy()
        acl3["id"] = str(uuid.uuid4())
        acl3["name"] = "acl3"
        acl3["folder"] = "Folder1"
        acl3["snippet"] = "Snippet1"

        acl4 = sample_route_access_list_dict.copy()
        acl4["id"] = str(uuid.uuid4())
        acl4["name"] = "acl4"
        acl4["folder"] = "Folder1"
        acl4["device"] = "Device1"

        self.mock_scm.get.return_value = {
            "data": [acl1, acl2, acl3, acl4],
            "limit": 100,
            "offset": 0,
            "total": 4,
        }

        # Test exact_match filter
        result = self.client.list(folder="Folder1", exact_match=True)
        assert len(result) == 3  # Should match acl1, acl3, acl4

        # Test exclude_folders filter
        result = self.client.list(folder="Folder1", exclude_folders=["Folder2"])
        assert len(result) == 3  # Should exclude only acl2

        # Test exclude_snippets filter
        result = self.client.list(folder="Folder1", exclude_snippets=["Snippet1"])
        assert len(result) == 3  # Should exclude acl3

        # Test exclude_devices filter
        result = self.client.list(folder="Folder1", exclude_devices=["Device1"])
        assert len(result) == 3  # Should exclude acl4

        # Test combining multiple exclusions
        result = self.client.list(
            folder="Folder1", exclude_snippets=["Snippet1"], exclude_devices=["Device1"]
        )
        assert len(result) == 2  # Should exclude acl3 and acl4

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

    def test_fetch(self, sample_route_access_list_dict):
        """Test fetch method."""
        self.mock_scm.get.return_value = sample_route_access_list_dict

        result = self.client.fetch(name="test-acl", folder="Test Folder")

        self.mock_scm.get.assert_called_once()
        call_args = self.mock_scm.get.call_args
        assert call_args[0][0] == self.client.ENDPOINT
        assert call_args[1]["params"]["name"] == "test-acl"
        assert call_args[1]["params"]["folder"] == "Test Folder"

        assert isinstance(result, RouteAccessListResponseModel)
        assert result.name == sample_route_access_list_dict["name"]

    def test_fetch_with_empty_name(self):
        """Test fetch method with empty name parameter."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            self.client.fetch(name="", folder="Test Folder")
        assert '"name" is not allowed to be empty' in str(excinfo.value)

    def test_fetch_with_empty_folder(self):
        """Test fetch method with empty folder parameter."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            self.client.fetch(name="test-acl", folder="")
        assert '"folder" is not allowed to be empty' in str(excinfo.value)

    def test_fetch_with_missing_container(self):
        """Test fetch method with missing container parameter."""
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-acl")
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            excinfo.value
        )

    def test_fetch_with_invalid_response(self):
        """Test fetch method with invalid response."""
        self.mock_scm.get.return_value = {"name": "test-acl"}

        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-acl", folder="Test Folder")
        assert "Response has invalid structure" in str(excinfo.value)

    def test_fetch_response_errors(self):
        """Test fetch method error handling for invalid responses."""
        # Test non-list, non-dictionary response
        self.mock_scm.get.return_value = "not a dictionary"
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-acl", folder="Test Folder")
        assert "Response is not a dictionary" in str(excinfo.value)

        valid_uuid = str(uuid.uuid4())
        self.mock_scm.get.return_value = {"data": [{"id": valid_uuid, "name": "test-acl"}]}
        result = self.client.fetch(name="test-acl", folder="Test Folder")
        assert isinstance(result, RouteAccessListResponseModel)
        assert result.id == uuid.UUID(valid_uuid)

        self.mock_scm.get.return_value = {"data": []}
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-acl", folder="Test Folder")
        assert "No matching route access list found" in str(excinfo.value)

        self.mock_scm.get.return_value = {"data": [{"name": "test-acl", "folder": "Test Folder"}]}
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-acl", folder="Test Folder")
        assert "Response data item missing 'id' field" in str(excinfo.value)

    def test_fetch_with_original_response_format(self, sample_route_access_list_dict):
        """Test fetch method with original response format (direct object with id field)."""
        self.mock_scm.get.return_value = sample_route_access_list_dict

        result = self.client.fetch(
            name=sample_route_access_list_dict["name"],
            folder=sample_route_access_list_dict["folder"],
        )

        assert isinstance(result, RouteAccessListResponseModel)
        assert result.id == uuid.UUID(sample_route_access_list_dict["id"])
        assert result.name == sample_route_access_list_dict["name"]

    def test_fetch_with_list_response_format(self, sample_route_access_list_dict):
        """Test fetch method with list response format (data array with objects)."""
        acl_data = sample_route_access_list_dict.copy()

        self.mock_scm.get.return_value = {
            "data": [acl_data],
            "limit": 20,
            "offset": 0,
            "total": 1,
        }

        result = self.client.fetch(name=acl_data["name"], folder=acl_data["folder"])

        assert isinstance(result, RouteAccessListResponseModel)
        assert result.id == uuid.UUID(acl_data["id"])

    def test_fetch_with_multiple_objects_in_data(self, sample_route_access_list_dict, monkeypatch):
        """Test fetch method when data array contains multiple objects."""
        from unittest.mock import MagicMock

        acl1 = sample_route_access_list_dict.copy()
        acl1["id"] = str(uuid.uuid4())
        acl1["name"] = "acl1"

        acl2 = sample_route_access_list_dict.copy()
        acl2["id"] = str(uuid.uuid4())
        acl2["name"] = "acl2"

        self.mock_scm.get.return_value = {
            "data": [acl1, acl2],
            "limit": 20,
            "offset": 0,
            "total": 2,
        }

        mock_warning = MagicMock()
        monkeypatch.setattr(self.client.logger, "warning", mock_warning)

        result = self.client.fetch(name=acl1["name"], folder=acl1["folder"])

        assert isinstance(result, RouteAccessListResponseModel)
        assert result.id == uuid.UUID(acl1["id"])

        mock_warning.assert_called_once()
        call_args = mock_warning.call_args[0][0]
        assert "Multiple route access lists found" in call_args

    def test_fetch_with_raw_list_response(self, sample_route_access_list_dict):
        """Test fetch method when API returns raw list instead of dict."""
        acl_data = sample_route_access_list_dict.copy()
        self.mock_scm.get.return_value = [acl_data]

        result = self.client.fetch(name=acl_data["name"], folder=acl_data["folder"])

        assert isinstance(result, RouteAccessListResponseModel)
        assert result.id == uuid.UUID(acl_data["id"])
        assert result.name == acl_data["name"]

    def test_fetch_with_raw_list_response_empty(self):
        """Test fetch method when API returns empty raw list."""
        self.mock_scm.get.return_value = []

        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="nonexistent", folder="Test Folder")
        assert "No matching resource found" in str(excinfo.value)

    def test_fetch_with_raw_list_response_multiple(
        self, sample_route_access_list_dict, monkeypatch
    ):
        """Test fetch method when API returns raw list with multiple items."""
        acl1 = sample_route_access_list_dict.copy()
        acl1["id"] = str(uuid.uuid4())
        acl1["name"] = "acl1"

        acl2 = sample_route_access_list_dict.copy()
        acl2["id"] = str(uuid.uuid4())
        acl2["name"] = "acl2"

        self.mock_scm.get.return_value = [acl1, acl2]

        mock_warning = MagicMock()
        monkeypatch.setattr(self.client.logger, "warning", mock_warning)

        result = self.client.fetch(name="acl1", folder="Test Folder")

        assert isinstance(result, RouteAccessListResponseModel)
        assert result.id == uuid.UUID(acl1["id"])
        mock_warning.assert_called_once()

    def test_list_with_raw_list_response(self, sample_route_access_list_dict):
        """Test list method when API returns raw list instead of dict with data wrapper."""
        acl1 = sample_route_access_list_dict.copy()
        acl1["id"] = str(uuid.uuid4())
        acl1["name"] = "acl1"

        acl2 = sample_route_access_list_dict.copy()
        acl2["id"] = str(uuid.uuid4())
        acl2["name"] = "acl2"

        self.mock_scm.get.return_value = [acl1, acl2]

        result = self.client.list(folder="Test Folder")

        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(r, RouteAccessListResponseModel) for r in result)

    def test_delete(self, sample_route_access_list_dict):
        """Test delete method."""
        object_id = sample_route_access_list_dict["id"]

        self.client.delete(object_id)

        # Check that correct API call was made
        expected_endpoint = f"{self.client.ENDPOINT}/{object_id}"
        self.mock_scm.delete.assert_called_once_with(expected_endpoint)
