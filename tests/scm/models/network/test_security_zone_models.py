"""Test models for Security Zones."""

from uuid import UUID

import pytest
from pydantic import ValidationError

from scm.models.network import (
    DeviceAcl,
    NetworkConfig,
    SecurityZoneCreateModel,
    SecurityZoneResponseModel,
    SecurityZoneUpdateModel,
    UserAcl,
)


class TestSecurityZoneModels:
    """Test Security Zone Pydantic models."""

    def test_security_zone_base_model_validation(self):
        """Test validation of SecurityZoneBaseModel through the Create model."""
        # Test valid model
        valid_data = {
            "name": "test-zone",
            "folder": "Test Folder",
            "enable_user_identification": True,
            "enable_device_identification": False,
            "network": {
                "layer3": ["ethernet1/1", "ethernet1/2"],
                "zone_protection_profile": "default",
                "enable_packet_buffer_protection": True,
            },
        }
        model = SecurityZoneCreateModel(**valid_data)
        assert model.name == "test-zone"
        assert model.folder == "Test Folder"
        assert model.enable_user_identification is True
        assert model.enable_device_identification is False
        assert model.network.layer3 == ["ethernet1/1", "ethernet1/2"]
        assert model.network.zone_protection_profile == "default"
        assert model.network.enable_packet_buffer_protection is True

        # Test with whitespace in name
        valid_with_whitespace = valid_data.copy()
        valid_with_whitespace["name"] = "DMZ ZONE"
        model = SecurityZoneCreateModel(**valid_with_whitespace)
        assert model.name == "DMZ ZONE"

        # Test with multiple words and special characters
        valid_with_special_chars = valid_data.copy()
        valid_with_special_chars["name"] = "External DMZ Zone-1"
        model = SecurityZoneCreateModel(**valid_with_special_chars)
        assert model.name == "External DMZ Zone-1"

        # Test invalid name with invalid characters
        invalid_name = valid_data.copy()
        invalid_name["name"] = "DMZ ZONE!@#"
        with pytest.raises(ValidationError) as exc_info:
            SecurityZoneCreateModel(**invalid_name)
        assert "String should match pattern" in str(exc_info.value)

        # Test invalid name (too long)
        invalid_name = valid_data.copy()
        invalid_name["name"] = "A" * 64  # Max length is 63
        with pytest.raises(ValidationError) as exc_info:
            SecurityZoneCreateModel(**invalid_name)
        assert "should have at most 63 characters" in str(exc_info.value).lower()

    def test_security_zone_create_model_container_validation(self):
        """Test validation of container fields in SecurityZoneCreateModel."""
        valid_data = {
            "name": "test-zone",
            "folder": "Test Folder",
        }
        model = SecurityZoneCreateModel(**valid_data)
        assert model.folder == "Test Folder"
        assert model.snippet is None
        assert model.device is None

        # Test with snippet container
        valid_with_snippet = {
            "name": "test-zone",
            "snippet": "Test Snippet",
        }
        model = SecurityZoneCreateModel(**valid_with_snippet)
        assert model.snippet == "Test Snippet"
        assert model.folder is None
        assert model.device is None

        # Test with device container
        valid_with_device = {
            "name": "test-zone",
            "device": "Test Device",
        }
        model = SecurityZoneCreateModel(**valid_with_device)
        assert model.device == "Test Device"
        assert model.folder is None
        assert model.snippet is None

        # Test with no container
        invalid_no_container = {
            "name": "test-zone",
        }
        with pytest.raises(ValueError) as exc_info:
            SecurityZoneCreateModel(**invalid_no_container)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

        # Test with multiple containers
        invalid_multiple_containers = {
            "name": "test-zone",
            "folder": "Test Folder",
            "snippet": "Test Snippet",
        }
        with pytest.raises(ValueError) as exc_info:
            SecurityZoneCreateModel(**invalid_multiple_containers)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_network_config_validation(self):
        """Test validation of NetworkConfig to ensure only one network type is configured."""
        # Valid configuration with one network type
        valid_config = NetworkConfig(layer3=["ethernet1/1"])
        assert valid_config.layer3 == ["ethernet1/1"]

        # Valid configuration with log setting
        valid_config = NetworkConfig(layer3=["ethernet1/1"], log_setting="default-log-setting")
        assert valid_config.layer3 == ["ethernet1/1"]
        assert valid_config.log_setting == "default-log-setting"

        # Invalid configuration with multiple network types
        with pytest.raises(ValueError) as exc_info:
            NetworkConfig(layer3=["ethernet1/1"], layer2=["ethernet1/2"])
        assert "Only one network interface type can be configured at a time" in str(exc_info.value)

    def test_user_acl_model(self):
        """Test validation of UserAcl model."""
        # Test default empty lists
        user_acl = UserAcl()
        assert user_acl.include_list == []
        assert user_acl.exclude_list == []

        # Test with values
        user_acl = UserAcl(include_list=["user1", "user2"], exclude_list=["user3"])
        assert user_acl.include_list == ["user1", "user2"]
        assert user_acl.exclude_list == ["user3"]

    def test_device_acl_model(self):
        """Test validation of DeviceAcl model."""
        # Test default empty lists
        device_acl = DeviceAcl()
        assert device_acl.include_list == []
        assert device_acl.exclude_list == []

        # Test with values
        device_acl = DeviceAcl(include_list=["device1", "device2"], exclude_list=["device3"])
        assert device_acl.include_list == ["device1", "device2"]
        assert device_acl.exclude_list == ["device3"]

    def test_security_zone_update_model(self):
        """Test validation of SecurityZoneUpdateModel."""
        # Test valid update model
        valid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "updated-zone",
            "folder": "Test Folder",
            "enable_user_identification": True,
            "network": {
                "layer3": ["ethernet1/1", "ethernet1/2"],
            },
        }
        model = SecurityZoneUpdateModel(**valid_data)
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "updated-zone"
        assert model.folder == "Test Folder"
        assert model.enable_user_identification is True
        assert model.network.layer3 == ["ethernet1/1", "ethernet1/2"]

        # Test with whitespace in name on update
        valid_with_whitespace = valid_data.copy()
        valid_with_whitespace["name"] = "DMZ ZONE"
        model = SecurityZoneUpdateModel(**valid_with_whitespace)
        assert model.name == "DMZ ZONE"

        # Test invalid UUID
        invalid_id = valid_data.copy()
        invalid_id["id"] = "not-a-uuid"
        with pytest.raises(ValidationError):
            SecurityZoneUpdateModel(**invalid_id)

    def test_security_zone_response_model(self):
        """Test validation of SecurityZoneResponseModel."""
        # Test valid response model
        valid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "response-zone",
            "folder": "Test Folder",
            "enable_user_identification": True,
            "network": {
                "layer3": ["ethernet1/1", "ethernet1/2"],
            },
        }
        model = SecurityZoneResponseModel(**valid_data)
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "response-zone"
        assert model.folder == "Test Folder"
        assert model.enable_user_identification is True
        assert model.network.layer3 == ["ethernet1/1", "ethernet1/2"]

        # Test with whitespace in name in response
        valid_with_whitespace = valid_data.copy()
        valid_with_whitespace["name"] = "DMZ ZONE"
        model = SecurityZoneResponseModel(**valid_with_whitespace)
        assert model.name == "DMZ ZONE"

        # Test missing required ID
        invalid_data = valid_data.copy()
        del invalid_data["id"]
        with pytest.raises(ValidationError):
            SecurityZoneResponseModel(**invalid_data)
