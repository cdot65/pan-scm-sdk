"""Unit tests for the Security Zone class."""

import json
import uuid
from unittest.mock import MagicMock, patch

import pytest

from scm.config.network import SecurityZone
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.network import (
    SecurityZoneCreateModel,
    SecurityZoneResponseModel,
    SecurityZoneUpdateModel,
    NetworkConfig,
)


@pytest.fixture
def sample_security_zone_dict():
    """Return a sample security zone dictionary."""
    return {
        "id": str(uuid.uuid4()),
        "name": "test-zone",
        "folder": "Test Folder",
        "enable_user_identification": True,
        "enable_device_identification": False,
        "network": {
            "layer3": ["ethernet1/1", "ethernet1/2"],
            "zone_protection_profile": "default",
            "enable_packet_buffer_protection": True,
        }
    }


@pytest.fixture
def sample_security_zone_response(sample_security_zone_dict):
    """Return a sample SecurityZoneResponseModel."""
    return SecurityZoneResponseModel(**sample_security_zone_dict)


@pytest.mark.usefixtures("load_env")
class TestSecurityZoneBase:
    """Base class for SecurityZone tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = SecurityZone(self.mock_scm, max_limit=5000)


class TestSecurityZone(TestSecurityZoneBase):
    """Test suite for SecurityZone class."""

    def test_init(self):
        """Test initialization of SecurityZone class."""
        security_zone = SecurityZone(self.mock_scm)
        assert security_zone.api_client == self.mock_scm
        assert security_zone.ENDPOINT == "/config/network/v1/zones"
        assert security_zone.max_limit == security_zone.DEFAULT_MAX_LIMIT

    def test_init_with_custom_max_limit(self):
        """Test initialization with custom max_limit."""
        security_zone = SecurityZone(self.mock_scm, max_limit=1000)
        assert security_zone.max_limit == 1000

    def test_init_with_invalid_max_limit(self):
        """Test initialization with invalid max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            SecurityZone(self.mock_scm, max_limit="invalid")
        assert "Invalid max_limit type" in str(excinfo.value)

    def test_init_with_negative_max_limit(self):
        """Test initialization with negative max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            SecurityZone(self.mock_scm, max_limit=-1)
        assert "Invalid max_limit value" in str(excinfo.value)

    def test_init_with_excessive_max_limit(self):
        """Test initialization with excessive max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            security_zone = SecurityZone(self.mock_scm)
            security_zone.max_limit = 10000
        assert "max_limit exceeds maximum allowed value" in str(excinfo.value)

    def test_create(self, sample_security_zone_dict):
        """Test create method."""
        self.mock_scm.post.return_value = sample_security_zone_dict
        
        # Create a copy without the ID for create operation
        create_data = sample_security_zone_dict.copy()
        create_data.pop("id")

        result = self.client.create(create_data)

        # Check that correct API call was made
        self.mock_scm.post.assert_called_once()
        call_args = self.mock_scm.post.call_args
        assert call_args[0][0] == self.client.ENDPOINT
        
        # Check payload validation
        payload = call_args[1]["json"]
        # Should be deserialized from a SecurityZoneCreateModel
        SecurityZoneCreateModel(**payload)
        
        # Check result
        assert isinstance(result, SecurityZoneResponseModel)
        assert result.name == sample_security_zone_dict["name"]
        assert result.folder == sample_security_zone_dict["folder"]

    def test_get(self, sample_security_zone_dict):
        """Test get method."""
        self.mock_scm.get.return_value = sample_security_zone_dict
        object_id = sample_security_zone_dict["id"]

        result = self.client.get(object_id)

        # Check that correct API call was made
        expected_endpoint = f"{self.client.ENDPOINT}/{object_id}"
        self.mock_scm.get.assert_called_once_with(expected_endpoint)
        
        # Check result
        assert isinstance(result, SecurityZoneResponseModel)
        assert result.id == uuid.UUID(object_id)
        assert result.name == sample_security_zone_dict["name"]

    def test_update(self, sample_security_zone_dict):
        """Test update method."""
        self.mock_scm.put.return_value = sample_security_zone_dict
        object_id = sample_security_zone_dict["id"]

        # Create update model
        update_model = SecurityZoneUpdateModel(**sample_security_zone_dict)

        result = self.client.update(update_model)

        # Check that correct API call was made
        expected_endpoint = f"{self.client.ENDPOINT}/{object_id}"
        self.mock_scm.put.assert_called_once()
        call_args = self.mock_scm.put.call_args
        assert call_args[0][0] == expected_endpoint
        
        # ID should not be in the payload since it's in the URL
        assert "id" not in call_args[1]["json"]
        
        # Check result
        assert isinstance(result, SecurityZoneResponseModel)
        assert result.id == uuid.UUID(object_id)
        assert result.name == sample_security_zone_dict["name"]

    def test_delete(self, sample_security_zone_dict):
        """Test delete method."""
        object_id = sample_security_zone_dict["id"]

        self.client.delete(object_id)

        # Check that correct API call was made
        expected_endpoint = f"{self.client.ENDPOINT}/{object_id}"
        self.mock_scm.delete.assert_called_once_with(expected_endpoint)

    def test_list(self, sample_security_zone_dict):
        """Test list method."""
        self.mock_scm.get.return_value = {
            "data": [sample_security_zone_dict],
            "limit": 20,
            "offset": 0,
            "total": 1
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
        assert isinstance(result[0], SecurityZoneResponseModel)
        assert result[0].name == sample_security_zone_dict["name"]
        
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
        assert "\"data\" field missing in the response" in str(excinfo.value)
        
        # Test data field not a list
        self.mock_scm.get.return_value = {"data": "not a list"}
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(folder="Test Folder")
        assert "\"data\" field must be a list" in str(excinfo.value)
        
    def test_list_pagination(self, sample_security_zone_dict):
        """Test list method pagination."""
        # Create multiple pages of data
        zone1 = sample_security_zone_dict.copy()
        zone1["id"] = str(uuid.uuid4())
        zone1["name"] = "zone1"
        
        zone2 = sample_security_zone_dict.copy()
        zone2["id"] = str(uuid.uuid4())
        zone2["name"] = "zone2"
        
        # Mock responses for pagination
        self.mock_scm.get.side_effect = [
            # First page
            {
                "data": [zone1],
                "limit": 1,
                "offset": 0,
                "total": 2
            },
            # Second page
            {
                "data": [zone2],
                "limit": 1,
                "offset": 1,
                "total": 2
            },
            # Empty page (to end pagination)
            {
                "data": [],
                "limit": 1,
                "offset": 2,
                "total": 2
            }
        ]
        
        # Set a small limit to force pagination
        self.client.max_limit = 1
        result = self.client.list(folder="Test Folder")
        
        # Should have made 3 calls (2 pages + 1 empty page to end pagination)
        assert self.mock_scm.get.call_count == 3
        
        # We should get both zones in the result
        assert len(result) == 2
        zone_names = [zone.name for zone in result]
        assert "zone1" in zone_names
        assert "zone2" in zone_names
        
    def test_list_with_exclusions(self, sample_security_zone_dict):
        """Test list method with exclusion filters."""
        # Create multiple zones with different containers
        zone1 = sample_security_zone_dict.copy()
        zone1["id"] = str(uuid.uuid4())
        zone1["name"] = "zone1"
        zone1["folder"] = "Folder1"
        
        zone2 = sample_security_zone_dict.copy()
        zone2["id"] = str(uuid.uuid4())
        zone2["name"] = "zone2"
        zone2["folder"] = "Folder2"
        
        zone3 = sample_security_zone_dict.copy()
        zone3["id"] = str(uuid.uuid4())
        zone3["name"] = "zone3"
        zone3["folder"] = "Folder1"
        zone3["snippet"] = "Snippet1"
        
        zone4 = sample_security_zone_dict.copy()
        zone4["id"] = str(uuid.uuid4())
        zone4["name"] = "zone4"
        zone4["folder"] = "Folder1"
        zone4["device"] = "Device1"
        
        self.mock_scm.get.return_value = {
            "data": [zone1, zone2, zone3, zone4],
            "limit": 100,
            "offset": 0,
            "total": 4
        }
        
        # Test exact_match filter
        result = self.client.list(folder="Folder1", exact_match=True)
        assert len(result) == 3  # Should match zone1, zone3, zone4
        
        # Test exclude_folders filter
        result = self.client.list(folder="Folder1", exclude_folders=["Folder2"])
        assert len(result) == 3  # Should exclude only zone2
        
        # Test exclude_snippets filter
        result = self.client.list(folder="Folder1", exclude_snippets=["Snippet1"])
        assert len(result) == 3  # Should exclude zone3
        
        # Test exclude_devices filter
        result = self.client.list(folder="Folder1", exclude_devices=["Device1"])
        assert len(result) == 3  # Should exclude zone4
        
        # Test combining multiple exclusions
        result = self.client.list(
            folder="Folder1",
            exclude_snippets=["Snippet1"],
            exclude_devices=["Device1"]
        )
        assert len(result) == 2  # Should exclude zone3 and zone4

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

    def test_list_filtering(self, sample_security_zone_dict):
        """Test list method with filtering."""
        # Create two zone objects for filtering tests
        zone1 = sample_security_zone_dict.copy()
        zone1["id"] = str(uuid.uuid4())
        zone1["name"] = "zone1"
        zone1["enable_user_identification"] = True
        zone1["enable_device_identification"] = True
        zone1["network"] = {"layer3": ["ethernet1/1"], "zone_protection_profile": "default"}
        
        zone2 = sample_security_zone_dict.copy()
        zone2["id"] = str(uuid.uuid4())
        zone2["name"] = "zone2"
        zone2["enable_user_identification"] = False
        zone2["enable_device_identification"] = False
        zone2["network"] = {"layer2": ["ethernet1/2"]}
        
        self.mock_scm.get.return_value = {
            "data": [zone1, zone2],
            "limit": 20,
            "offset": 0,
            "total": 2
        }
        
        # Test filtering by enable_user_identification
        result = self.client.list(
            folder="Test Folder", 
            enable_user_identification=True
        )
        
        assert len(result) == 1
        assert result[0].name == "zone1"
        
        # Test filtering by enable_device_identification
        result = self.client.list(
            folder="Test Folder", 
            enable_device_identification=True
        )
        
        assert len(result) == 1
        assert result[0].name == "zone1"
        
        # Test filtering by network_type
        result = self.client.list(
            folder="Test Folder", 
            network_type=["layer3"]
        )
        
        assert len(result) == 1
        assert result[0].name == "zone1"
        
        # Test with invalid filter type for enable_user_identification
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(
                folder="Test Folder", 
                enable_user_identification="not-a-boolean"
            )
        assert "Invalid Object" in str(excinfo.value)
        
        # Test with invalid filter type for enable_device_identification
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(
                folder="Test Folder", 
                enable_device_identification="not-a-boolean"
            )
        assert "Invalid Object" in str(excinfo.value)
        
        # Test with invalid filter type for network_type
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(
                folder="Test Folder", 
                network_type="layer3"  # Should be a list
            )
        assert "Invalid Object" in str(excinfo.value)

    def test_fetch(self, sample_security_zone_dict):
        """Test fetch method."""
        self.mock_scm.get.return_value = sample_security_zone_dict
        
        result = self.client.fetch(name="test-zone", folder="Test Folder")
        
        # Check that correct API call was made
        self.mock_scm.get.assert_called_once()
        call_args = self.mock_scm.get.call_args
        assert call_args[0][0] == self.client.ENDPOINT
        assert call_args[1]["params"]["name"] == "test-zone"
        assert call_args[1]["params"]["folder"] == "Test Folder"
        
        # Check result
        assert isinstance(result, SecurityZoneResponseModel)
        assert result.name == sample_security_zone_dict["name"]
    
    def test_fetch_with_empty_name(self):
        """Test fetch method with empty name parameter."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            self.client.fetch(name="", folder="Test Folder")
            
        assert '"name" is not allowed to be empty' in str(excinfo.value)
        
    def test_fetch_with_empty_folder(self):
        """Test fetch method with empty folder parameter."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            self.client.fetch(name="test-zone", folder="")
            
        assert '"folder" is not allowed to be empty' in str(excinfo.value)
    
    def test_fetch_with_missing_container(self):
        """Test fetch method with missing container parameter."""
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-zone")
            
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(excinfo.value)
        
    def test_fetch_with_invalid_response(self):
        """Test fetch method with invalid response."""
        # Response without an ID field
        self.mock_scm.get.return_value = {"name": "test-zone"}
        
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-zone", folder="Test Folder")
            
        assert "Response missing 'id' field" in str(excinfo.value)
        
    def test_fetch_response_errors(self):
        """Test fetch method error handling for invalid responses."""
        # Test non-dictionary response
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-zone", folder="Test Folder")
        assert "Response is not a dictionary" in str(excinfo.value)
        
        # Test list-style response (should have direct object, not list)
        self.mock_scm.get.return_value = {
            "data": [{"id": "123", "name": "test-zone"}]
        }
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-zone", folder="Test Folder")
        assert "Response missing 'id' field" in str(excinfo.value)
        
