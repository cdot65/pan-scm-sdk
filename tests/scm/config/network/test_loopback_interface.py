"""Unit tests for the Loopback Interface class."""

import uuid
from unittest.mock import MagicMock

import pytest

from scm.config.network.loopback_interface import LoopbackInterface
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.network.loopback_interface import (
    LoopbackInterfaceCreateModel,
    LoopbackInterfaceResponseModel,
    LoopbackInterfaceUpdateModel,
)


@pytest.fixture
def sample_loopback_dict():
    """Return a sample loopback interface dictionary."""
    return {
        "id": str(uuid.uuid4()),
        "name": "$test-loopback",
        "folder": "Test Folder",
        "default_value": "loopback.1",
        "comment": "Test loopback interface",
        "mtu": 1500,
        "interface_management_profile": "default-mgmt",
        "ip": [{"name": "192.168.1.1/24"}],
    }


@pytest.fixture
def sample_loopback_response(sample_loopback_dict):
    """Return a sample LoopbackInterfaceResponseModel."""
    return LoopbackInterfaceResponseModel(**sample_loopback_dict)


@pytest.mark.usefixtures("load_env")
class TestLoopbackInterfaceBase:
    """Base class for LoopbackInterface tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = LoopbackInterface(self.mock_scm, max_limit=5000)


class TestLoopbackInterface(TestLoopbackInterfaceBase):
    """Test suite for LoopbackInterface class."""

    def test_init(self):
        """Test initialization of LoopbackInterface class."""
        loopback = LoopbackInterface(self.mock_scm)
        assert loopback.api_client == self.mock_scm
        assert loopback.ENDPOINT == "/config/network/v1/loopback-interfaces"
        assert loopback.max_limit == loopback.DEFAULT_MAX_LIMIT

    def test_init_with_custom_max_limit(self):
        """Test initialization with custom max_limit."""
        loopback = LoopbackInterface(self.mock_scm, max_limit=1000)
        assert loopback.max_limit == 1000

    def test_init_with_invalid_max_limit(self):
        """Test initialization with invalid max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            LoopbackInterface(self.mock_scm, max_limit="invalid")
        assert "Invalid max_limit type" in str(excinfo.value)

    def test_init_with_negative_max_limit(self):
        """Test initialization with negative max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            LoopbackInterface(self.mock_scm, max_limit=-1)
        assert "Invalid max_limit value" in str(excinfo.value)

    def test_init_with_excessive_max_limit(self):
        """Test initialization with excessive max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            loopback = LoopbackInterface(self.mock_scm)
            loopback.max_limit = 10000
        assert "max_limit exceeds maximum allowed value" in str(excinfo.value)

    def test_create(self, sample_loopback_dict):
        """Test create method."""
        self.mock_scm.post.return_value = sample_loopback_dict

        create_data = sample_loopback_dict.copy()
        create_data.pop("id")

        result = self.client.create(create_data)

        self.mock_scm.post.assert_called_once()
        call_args = self.mock_scm.post.call_args
        assert call_args[0][0] == self.client.ENDPOINT

        payload = call_args[1]["json"]
        LoopbackInterfaceCreateModel(**payload)

        assert isinstance(result, LoopbackInterfaceResponseModel)
        assert result.name == sample_loopback_dict["name"]
        assert result.folder == sample_loopback_dict["folder"]

    def test_get(self, sample_loopback_dict):
        """Test get method."""
        self.mock_scm.get.return_value = sample_loopback_dict
        object_id = sample_loopback_dict["id"]

        result = self.client.get(object_id)

        expected_endpoint = f"{self.client.ENDPOINT}/{object_id}"
        self.mock_scm.get.assert_called_once_with(expected_endpoint)

        assert isinstance(result, LoopbackInterfaceResponseModel)
        assert result.id == uuid.UUID(object_id)
        assert result.name == sample_loopback_dict["name"]

    def test_update(self, sample_loopback_dict):
        """Test update method."""
        self.mock_scm.put.return_value = sample_loopback_dict
        object_id = sample_loopback_dict["id"]

        update_model = LoopbackInterfaceUpdateModel(**sample_loopback_dict)

        result = self.client.update(update_model)

        expected_endpoint = f"{self.client.ENDPOINT}/{object_id}"
        self.mock_scm.put.assert_called_once()
        call_args = self.mock_scm.put.call_args
        assert call_args[0][0] == expected_endpoint

        assert "id" not in call_args[1]["json"]

        assert isinstance(result, LoopbackInterfaceResponseModel)
        assert result.id == uuid.UUID(object_id)
        assert result.name == sample_loopback_dict["name"]

    def test_delete(self, sample_loopback_dict):
        """Test delete method."""
        object_id = sample_loopback_dict["id"]

        self.client.delete(object_id)

        expected_endpoint = f"{self.client.ENDPOINT}/{object_id}"
        self.mock_scm.delete.assert_called_once_with(expected_endpoint)

    def test_list(self, sample_loopback_dict):
        """Test list method."""
        self.mock_scm.get.return_value = {
            "data": [sample_loopback_dict],
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
        assert isinstance(result[0], LoopbackInterfaceResponseModel)
        assert result[0].name == sample_loopback_dict["name"]

    def test_list_response_errors(self):
        """Test list method error handling for invalid responses."""
        # Test non-dictionary response
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(folder="Test Folder")
        assert "Response is not a dictionary" in str(excinfo.value)

        # Test missing data field
        self.mock_scm.get.return_value = {"no_data": "field"}
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(folder="Test Folder")
        assert '"data" field missing in the response' in str(excinfo.value)

        # Test data field not a list
        self.mock_scm.get.return_value = {"data": "not a list"}
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(folder="Test Folder")
        assert '"data" field must be a list' in str(excinfo.value)

    def test_list_pagination(self, sample_loopback_dict):
        """Test list method pagination."""
        loopback1 = sample_loopback_dict.copy()
        loopback1["id"] = str(uuid.uuid4())
        loopback1["name"] = "$loopback1"

        loopback2 = sample_loopback_dict.copy()
        loopback2["id"] = str(uuid.uuid4())
        loopback2["name"] = "$loopback2"

        self.mock_scm.get.side_effect = [
            {"data": [loopback1], "limit": 1, "offset": 0, "total": 2},
            {"data": [loopback2], "limit": 1, "offset": 1, "total": 2},
            {"data": [], "limit": 1, "offset": 2, "total": 2},
        ]

        self.client.max_limit = 1
        result = self.client.list(folder="Test Folder")

        assert self.mock_scm.get.call_count == 3

        assert len(result) == 2
        names = [iface.name for iface in result]
        assert "$loopback1" in names
        assert "$loopback2" in names

    def test_list_with_exclusions(self, sample_loopback_dict):
        """Test list method with exclusion filters."""
        loopback1 = sample_loopback_dict.copy()
        loopback1["id"] = str(uuid.uuid4())
        loopback1["name"] = "$loopback1"
        loopback1["folder"] = "Folder1"

        loopback2 = sample_loopback_dict.copy()
        loopback2["id"] = str(uuid.uuid4())
        loopback2["name"] = "$loopback2"
        loopback2["folder"] = "Folder2"

        self.mock_scm.get.return_value = {
            "data": [loopback1, loopback2],
            "limit": 100,
            "offset": 0,
            "total": 2,
        }

        result = self.client.list(folder="Folder1", exact_match=True)
        assert len(result) == 1

        result = self.client.list(folder="Folder1", exclude_folders=["Folder2"])
        assert len(result) == 1

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

    def test_list_filtering(self, sample_loopback_dict):
        """Test list method with filtering."""
        loopback1 = sample_loopback_dict.copy()
        loopback1["id"] = str(uuid.uuid4())
        loopback1["name"] = "$loopback1"
        loopback1["mtu"] = 1500
        loopback1["interface_management_profile"] = "profile1"

        loopback2 = sample_loopback_dict.copy()
        loopback2["id"] = str(uuid.uuid4())
        loopback2["name"] = "$loopback2"
        loopback2["mtu"] = 9000
        loopback2["interface_management_profile"] = "profile2"

        self.mock_scm.get.return_value = {
            "data": [loopback1, loopback2],
            "limit": 20,
            "offset": 0,
            "total": 2,
        }

        # Filter by MTU
        result = self.client.list(folder="Test Folder", mtu=1500)
        assert len(result) == 1
        assert result[0].name == "$loopback1"

        # Filter by interface_management_profile
        result = self.client.list(folder="Test Folder", interface_management_profile="profile2")
        assert len(result) == 1
        assert result[0].name == "$loopback2"

        # Invalid MTU filter type
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(folder="Test Folder", mtu="not-an-int")
        assert "Invalid Object" in str(excinfo.value)

        # Invalid interface_management_profile filter type
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(folder="Test Folder", interface_management_profile=123)
        assert "Invalid Object" in str(excinfo.value)

    def test_fetch(self, sample_loopback_dict):
        """Test fetch method."""
        self.mock_scm.get.return_value = sample_loopback_dict

        result = self.client.fetch(name="$test-loopback", folder="Test Folder")

        self.mock_scm.get.assert_called_once()
        call_args = self.mock_scm.get.call_args
        assert call_args[0][0] == self.client.ENDPOINT
        assert call_args[1]["params"]["name"] == "$test-loopback"
        assert call_args[1]["params"]["folder"] == "Test Folder"

        assert isinstance(result, LoopbackInterfaceResponseModel)
        assert result.name == sample_loopback_dict["name"]

    def test_fetch_with_empty_name(self):
        """Test fetch method with empty name parameter."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            self.client.fetch(name="", folder="Test Folder")
        assert '"name" is not allowed to be empty' in str(excinfo.value)

    def test_fetch_with_empty_folder(self):
        """Test fetch method with empty folder parameter."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            self.client.fetch(name="$test-loopback", folder="")
        assert '"folder" is not allowed to be empty' in str(excinfo.value)

    def test_fetch_with_missing_container(self):
        """Test fetch method with missing container parameter."""
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="$test-loopback")
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            excinfo.value
        )

    def test_fetch_with_invalid_response(self):
        """Test fetch method with invalid response."""
        self.mock_scm.get.return_value = {"name": "$test-loopback"}

        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="$test-loopback", folder="Test Folder")
        assert "Response has invalid structure" in str(excinfo.value)

    def test_fetch_response_errors(self):
        """Test fetch method error handling for invalid responses."""
        # Test non-dictionary response
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="$test-loopback", folder="Test Folder")
        assert "Response is not a dictionary" in str(excinfo.value)

        # Test valid data list-style response
        valid_uuid = str(uuid.uuid4())
        self.mock_scm.get.return_value = {"data": [{"id": valid_uuid, "name": "$test-loopback"}]}

        result = self.client.fetch(name="$test-loopback", folder="Test Folder")
        assert isinstance(result, LoopbackInterfaceResponseModel)
        assert result.id == uuid.UUID(valid_uuid)

        # Test empty data list
        self.mock_scm.get.return_value = {"data": []}
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="$test-loopback", folder="Test Folder")
        assert "No matching loopback interface found" in str(excinfo.value)

        # Test data item without id field
        self.mock_scm.get.return_value = {"data": [{"name": "$test-loopback", "folder": "Test Folder"}]}
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="$test-loopback", folder="Test Folder")
        assert "Response data item missing 'id' field" in str(excinfo.value)

    def test_fetch_with_original_response_format(self, sample_loopback_dict):
        """Test fetch method with original response format (direct object with id field)."""
        self.mock_scm.get.return_value = sample_loopback_dict

        result = self.client.fetch(
            name=sample_loopback_dict["name"], folder=sample_loopback_dict["folder"]
        )

        assert isinstance(result, LoopbackInterfaceResponseModel)
        assert result.id == uuid.UUID(sample_loopback_dict["id"])
        assert result.name == sample_loopback_dict["name"]
        assert result.folder == sample_loopback_dict["folder"]

    def test_fetch_with_list_response_format(self, sample_loopback_dict):
        """Test fetch method with list response format (data array with objects)."""
        loopback_data = sample_loopback_dict.copy()

        self.mock_scm.get.return_value = {
            "data": [loopback_data],
            "limit": 20,
            "offset": 0,
            "total": 1,
        }

        result = self.client.fetch(name=loopback_data["name"], folder=loopback_data["folder"])

        assert isinstance(result, LoopbackInterfaceResponseModel)
        assert result.id == uuid.UUID(loopback_data["id"])
        assert result.name == loopback_data["name"]
        assert result.folder == loopback_data["folder"]

    def test_fetch_with_multiple_objects_in_data(self, sample_loopback_dict, monkeypatch):
        """Test fetch method when data array contains multiple objects."""
        from unittest.mock import MagicMock

        loopback1 = sample_loopback_dict.copy()
        loopback1["id"] = str(uuid.uuid4())
        loopback1["name"] = "$loopback1"

        loopback2 = sample_loopback_dict.copy()
        loopback2["id"] = str(uuid.uuid4())
        loopback2["name"] = "$loopback2"

        self.mock_scm.get.return_value = {
            "data": [loopback1, loopback2],
            "limit": 20,
            "offset": 0,
            "total": 2,
        }

        mock_warning = MagicMock()
        monkeypatch.setattr(self.client.logger, "warning", mock_warning)

        result = self.client.fetch(name=loopback1["name"], folder=loopback1["folder"])

        assert isinstance(result, LoopbackInterfaceResponseModel)
        assert result.id == uuid.UUID(loopback1["id"])
        assert result.name == loopback1["name"]

        mock_warning.assert_called_once()
        call_args = mock_warning.call_args[0][0]
        assert "Multiple loopback interfaces found" in call_args
