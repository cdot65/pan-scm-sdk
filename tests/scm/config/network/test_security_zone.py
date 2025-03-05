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
        
        zone2 = sample_security_zone_dict.copy()
        zone2["id"] = str(uuid.uuid4())
        zone2["name"] = "zone2"
        zone2["enable_user_identification"] = False
        
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
        
        # Test with invalid filter type
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(
                folder="Test Folder", 
                enable_user_identification="not-a-boolean"
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