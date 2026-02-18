"""Unit tests for the InterfaceManagementProfile class."""

from unittest.mock import MagicMock
import uuid

import pytest

from scm.config.network import InterfaceManagementProfile
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.network import (
    InterfaceManagementProfileResponseModel,
    InterfaceManagementProfileUpdateModel,
)


@pytest.fixture
def sample_profile_dict():
    """Return a sample interface management profile dictionary."""
    return {
        "id": str(uuid.uuid4()),
        "name": "test-profile",
        "folder": "Test Folder",
        "http": True,
        "https": True,
        "ssh": True,
        "ping": True,
        "telnet": False,
        "http-ocsp": False,
        "response-pages": True,
        "userid-service": False,
        "userid-syslog-listener-ssl": False,
        "userid-syslog-listener-udp": False,
        "permitted-ip": ["10.0.0.0/8", "192.168.1.0/24"],
    }


@pytest.fixture
def sample_profile_response(sample_profile_dict):
    """Return a sample InterfaceManagementProfileResponseModel."""
    return InterfaceManagementProfileResponseModel(**sample_profile_dict)


@pytest.mark.usefixtures("load_env")
class TestInterfaceManagementProfileBase:
    """Base class for InterfaceManagementProfile tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = InterfaceManagementProfile(self.mock_scm, max_limit=5000)


class TestInterfaceManagementProfile(TestInterfaceManagementProfileBase):
    """Test suite for InterfaceManagementProfile class."""

    def test_init(self):
        """Test initialization of InterfaceManagementProfile class."""
        profile = InterfaceManagementProfile(self.mock_scm)
        assert profile.api_client == self.mock_scm
        assert profile.ENDPOINT == "/config/network/v1/interface-management-profiles"
        assert profile.max_limit == profile.DEFAULT_MAX_LIMIT

    def test_init_with_custom_max_limit(self):
        """Test initialization with custom max_limit."""
        profile = InterfaceManagementProfile(self.mock_scm, max_limit=1000)
        assert profile.max_limit == 1000

    def test_init_with_invalid_max_limit(self):
        """Test initialization with invalid max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            InterfaceManagementProfile(self.mock_scm, max_limit="invalid")
        assert "Invalid max_limit type" in str(excinfo.value)

    def test_init_with_negative_max_limit(self):
        """Test initialization with negative max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            InterfaceManagementProfile(self.mock_scm, max_limit=-1)
        assert "Invalid max_limit value" in str(excinfo.value)

    def test_init_with_excessive_max_limit(self):
        """Test initialization with excessive max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            profile = InterfaceManagementProfile(self.mock_scm)
            profile.max_limit = 10000
        assert "max_limit exceeds maximum allowed value" in str(excinfo.value)

    def test_create(self, sample_profile_dict):
        """Test create method."""
        self.mock_scm.post.return_value = sample_profile_dict

        # Create a copy without the ID for create operation
        create_data = sample_profile_dict.copy()
        create_data.pop("id")

        result = self.client.create(create_data)

        # Check that correct API call was made
        self.mock_scm.post.assert_called_once()
        call_args = self.mock_scm.post.call_args
        assert call_args[0][0] == self.client.ENDPOINT

        # Check result
        assert isinstance(result, InterfaceManagementProfileResponseModel)
        assert result.name == sample_profile_dict["name"]
        assert result.folder == sample_profile_dict["folder"]

    def test_get(self, sample_profile_dict):
        """Test get method."""
        self.mock_scm.get.return_value = sample_profile_dict
        object_id = sample_profile_dict["id"]

        result = self.client.get(object_id)

        # Check that correct API call was made
        expected_endpoint = f"{self.client.ENDPOINT}/{object_id}"
        self.mock_scm.get.assert_called_once_with(expected_endpoint)

        # Check result
        assert isinstance(result, InterfaceManagementProfileResponseModel)
        assert result.id == uuid.UUID(object_id)
        assert result.name == sample_profile_dict["name"]

    def test_update(self, sample_profile_dict):
        """Test update method."""
        self.mock_scm.put.return_value = sample_profile_dict
        object_id = sample_profile_dict["id"]

        # Create update model
        update_model = InterfaceManagementProfileUpdateModel(**sample_profile_dict)

        result = self.client.update(update_model)

        # Check that correct API call was made
        expected_endpoint = f"{self.client.ENDPOINT}/{object_id}"
        self.mock_scm.put.assert_called_once()
        call_args = self.mock_scm.put.call_args
        assert call_args[0][0] == expected_endpoint

        # ID should not be in the payload since it's in the URL
        assert "id" not in call_args[1]["json"]

        # Check result
        assert isinstance(result, InterfaceManagementProfileResponseModel)
        assert result.id == uuid.UUID(object_id)
        assert result.name == sample_profile_dict["name"]

    def test_delete(self, sample_profile_dict):
        """Test delete method."""
        object_id = sample_profile_dict["id"]

        self.client.delete(object_id)

        # Check that correct API call was made
        expected_endpoint = f"{self.client.ENDPOINT}/{object_id}"
        self.mock_scm.delete.assert_called_once_with(expected_endpoint)

    def test_list(self, sample_profile_dict):
        """Test list method."""
        self.mock_scm.get.return_value = {
            "data": [sample_profile_dict],
            "limit": 20,
            "offset": 0,
            "total": 1,
        }

        result = self.client.list(folder="Test Folder")

        # Check that correct API call was made
        self.mock_scm.get.assert_called_once()
        call_args = self.mock_scm.get.call_args
        assert call_args[0][0] == self.client.ENDPOINT
        assert call_args[1]["params"]["folder"] == "Test Folder"

        # Check result
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], InterfaceManagementProfileResponseModel)
        assert result[0].name == sample_profile_dict["name"]

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

    def test_list_pagination(self, sample_profile_dict):
        """Test list method pagination."""
        # Create multiple pages of data
        profile1 = sample_profile_dict.copy()
        profile1["id"] = str(uuid.uuid4())
        profile1["name"] = "profile1"

        profile2 = sample_profile_dict.copy()
        profile2["id"] = str(uuid.uuid4())
        profile2["name"] = "profile2"

        # Mock responses for pagination
        self.mock_scm.get.side_effect = [
            # First page
            {"data": [profile1], "limit": 1, "offset": 0, "total": 2},
            # Second page
            {"data": [profile2], "limit": 1, "offset": 1, "total": 2},
            # Empty page (to end pagination)
            {"data": [], "limit": 1, "offset": 2, "total": 2},
        ]

        # Set a small limit to force pagination
        self.client.max_limit = 1
        result = self.client.list(folder="Test Folder")

        # Should have made 3 calls (2 pages + 1 empty page to end pagination)
        assert self.mock_scm.get.call_count == 3

        # We should get both profiles in the result
        assert len(result) == 2
        profile_names = [p.name for p in result]
        assert "profile1" in profile_names
        assert "profile2" in profile_names

    def test_list_with_exclusions(self, sample_profile_dict):
        """Test list method with exclusion filters."""
        # Create multiple profiles with different containers
        profile1 = sample_profile_dict.copy()
        profile1["id"] = str(uuid.uuid4())
        profile1["name"] = "profile1"
        profile1["folder"] = "Folder1"

        profile2 = sample_profile_dict.copy()
        profile2["id"] = str(uuid.uuid4())
        profile2["name"] = "profile2"
        profile2["folder"] = "Folder2"

        profile3 = sample_profile_dict.copy()
        profile3["id"] = str(uuid.uuid4())
        profile3["name"] = "profile3"
        profile3["folder"] = "Folder1"
        profile3["snippet"] = "Snippet1"

        profile4 = sample_profile_dict.copy()
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

    def test_list_filtering(self, sample_profile_dict):
        """Test list method with filtering."""
        # Create two profile objects for filtering tests
        profile1 = sample_profile_dict.copy()
        profile1["id"] = str(uuid.uuid4())
        profile1["name"] = "profile1"
        profile1["http"] = True
        profile1["ssh"] = True
        profile1["ping"] = True

        profile2 = sample_profile_dict.copy()
        profile2["id"] = str(uuid.uuid4())
        profile2["name"] = "profile2"
        profile2["http"] = False
        profile2["ssh"] = False
        profile2["ping"] = False

        self.mock_scm.get.return_value = {
            "data": [profile1, profile2],
            "limit": 20,
            "offset": 0,
            "total": 2,
        }

        # Test filtering by http
        result = self.client.list(folder="Test Folder", http=True)
        assert len(result) == 1
        assert result[0].name == "profile1"

        # Test filtering by ssh
        result = self.client.list(folder="Test Folder", ssh=True)
        assert len(result) == 1
        assert result[0].name == "profile1"

        # Test filtering by ping
        result = self.client.list(folder="Test Folder", ping=False)
        assert len(result) == 1
        assert result[0].name == "profile2"

        # Test with invalid filter type for http
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(folder="Test Folder", http="not-a-boolean")
        assert "Invalid Object" in str(excinfo.value)

        # Test with invalid filter type for ssh
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(folder="Test Folder", ssh="not-a-boolean")
        assert "Invalid Object" in str(excinfo.value)

        # Test with invalid filter type for ping
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(folder="Test Folder", ping="not-a-boolean")
        assert "Invalid Object" in str(excinfo.value)

    def test_fetch(self, sample_profile_dict):
        """Test fetch method."""
        self.mock_scm.get.return_value = sample_profile_dict

        result = self.client.fetch(name="test-profile", folder="Test Folder")

        # Check that correct API call was made
        self.mock_scm.get.assert_called_once()
        call_args = self.mock_scm.get.call_args
        assert call_args[0][0] == self.client.ENDPOINT
        assert call_args[1]["params"]["name"] == "test-profile"
        assert call_args[1]["params"]["folder"] == "Test Folder"

        # Check result
        assert isinstance(result, InterfaceManagementProfileResponseModel)
        assert result.name == sample_profile_dict["name"]

    def test_fetch_with_empty_name(self):
        """Test fetch method with empty name parameter."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            self.client.fetch(name="", folder="Test Folder")

        assert '"name" is not allowed to be empty' in str(excinfo.value)

    def test_fetch_with_empty_folder(self):
        """Test fetch method with empty folder parameter."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            self.client.fetch(name="test-profile", folder="")

        assert '"folder" is not allowed to be empty' in str(excinfo.value)

    def test_fetch_with_missing_container(self):
        """Test fetch method with missing container parameter."""
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-profile")

        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            excinfo.value
        )

    def test_fetch_with_invalid_response(self):
        """Test fetch method with invalid response."""
        # Response without an ID field or data field
        self.mock_scm.get.return_value = {"name": "test-profile"}

        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-profile", folder="Test Folder")

        assert "Response has invalid structure" in str(excinfo.value)

    def test_fetch_response_errors(self):
        """Test fetch method error handling for invalid responses."""
        # Test non-dictionary response
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-profile", folder="Test Folder")
        assert "Response is not a dictionary" in str(excinfo.value)

        # Test valid data list-style response
        valid_uuid = str(uuid.uuid4())
        self.mock_scm.get.return_value = {"data": [{"id": valid_uuid, "name": "test-profile"}]}

        # Should now parse the first object in the data array without raising an exception
        result = self.client.fetch(name="test-profile", folder="Test Folder")
        assert isinstance(result, InterfaceManagementProfileResponseModel)
        assert result.id == uuid.UUID(valid_uuid)
        assert result.name == "test-profile"

        # Test empty data list
        self.mock_scm.get.return_value = {"data": []}
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-profile", folder="Test Folder")
        assert "No matching interface management profile found" in str(excinfo.value)

        # Test data item without id field
        self.mock_scm.get.return_value = {
            "data": [{"name": "test-profile", "folder": "Test Folder"}]
        }
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-profile", folder="Test Folder")
        assert "Response data item missing 'id' field" in str(excinfo.value)

    def test_fetch_with_original_response_format(self, sample_profile_dict):
        """Test fetch method with original response format (direct object with id field)."""
        # Set up the mock response in the original format
        self.mock_scm.get.return_value = sample_profile_dict

        # Call fetch and verify the result
        result = self.client.fetch(
            name=sample_profile_dict["name"], folder=sample_profile_dict["folder"]
        )

        # Verify that the response was correctly processed
        assert isinstance(result, InterfaceManagementProfileResponseModel)
        assert result.id == uuid.UUID(sample_profile_dict["id"])
        assert result.name == sample_profile_dict["name"]
        assert result.folder == sample_profile_dict["folder"]

        # Verify API call parameters
        self.mock_scm.get.assert_called_once()
        call_args = self.mock_scm.get.call_args
        assert call_args[0][0] == self.client.ENDPOINT
        assert call_args[1]["params"]["name"] == sample_profile_dict["name"]
        assert call_args[1]["params"]["folder"] == sample_profile_dict["folder"]

    def test_fetch_with_list_response_format(self, sample_profile_dict):
        """Test fetch method with list response format (data array with objects)."""
        # Create a deep copy to avoid modifying the original
        profile_data = sample_profile_dict.copy()

        # Set up the mock response in the list format (like list() method returns)
        self.mock_scm.get.return_value = {
            "data": [profile_data],
            "limit": 20,
            "offset": 0,
            "total": 1,
        }

        # Call fetch and verify the result
        result = self.client.fetch(name=profile_data["name"], folder=profile_data["folder"])

        # Verify that the response was correctly processed from the data array
        assert isinstance(result, InterfaceManagementProfileResponseModel)
        assert result.id == uuid.UUID(profile_data["id"])
        assert result.name == profile_data["name"]
        assert result.folder == profile_data["folder"]

        # Verify API call parameters
        self.mock_scm.get.assert_called_once()
        call_args = self.mock_scm.get.call_args
        assert call_args[0][0] == self.client.ENDPOINT
        assert call_args[1]["params"]["name"] == profile_data["name"]
        assert call_args[1]["params"]["folder"] == profile_data["folder"]

    def test_fetch_with_multiple_objects_in_data(self, sample_profile_dict, monkeypatch):
        """Test fetch method when data array contains multiple objects."""
        from unittest.mock import MagicMock

        # Create two profile dictionaries with different IDs and names
        profile1 = sample_profile_dict.copy()
        profile1["id"] = str(uuid.uuid4())
        profile1["name"] = "profile1"

        profile2 = sample_profile_dict.copy()
        profile2["id"] = str(uuid.uuid4())
        profile2["name"] = "profile2"

        # Set up the mock response with multiple objects in data array
        self.mock_scm.get.return_value = {
            "data": [profile1, profile2],
            "limit": 20,
            "offset": 0,
            "total": 2,
        }

        # Mock the logger.warning method
        mock_warning = MagicMock()
        monkeypatch.setattr(self.client.logger, "warning", mock_warning)

        # Call fetch and verify the result
        result = self.client.fetch(name=profile1["name"], folder=profile1["folder"])

        # Verify that ONLY the first object in the data array was used
        assert isinstance(result, InterfaceManagementProfileResponseModel)
        assert result.id == uuid.UUID(profile1["id"])
        assert result.name == profile1["name"]
        assert result.folder == profile1["folder"]

        # Ensure we didn't get the second object
        assert result.name != profile2["name"]
        assert result.id != uuid.UUID(profile2["id"])

        # Verify that the warning was logged
        mock_warning.assert_called_once()
        call_args = mock_warning.call_args[0][0]
        assert "Multiple interface management profiles found" in call_args
