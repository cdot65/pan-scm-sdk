"""Test models for Loopback Interface."""

from uuid import UUID

import pytest
from pydantic import ValidationError

from scm.models.network.loopback_interface import (
    LoopbackInterfaceCreateModel,
    LoopbackInterfaceResponseModel,
    LoopbackInterfaceUpdateModel,
)


class TestLoopbackInterfaceModels:
    """Test Loopback Interface Pydantic models."""

    def test_loopback_interface_base_model_validation(self):
        """Test validation of LoopbackInterfaceBaseModel through the Create model."""
        valid_data = {
            "name": "$loopback1",
            "folder": "Test Folder",
            "default_value": "loopback.1",
            "comment": "Test loopback interface",
            "mtu": 1500,
            "interface_management_profile": "default-mgmt",
            "ip": [{"name": "192.168.1.1/24"}],
        }
        model = LoopbackInterfaceCreateModel(**valid_data)
        assert model.name == "$loopback1"
        assert model.folder == "Test Folder"
        assert model.default_value == "loopback.1"
        assert model.comment == "Test loopback interface"
        assert model.mtu == 1500
        assert model.interface_management_profile == "default-mgmt"
        assert len(model.ip) == 1
        assert model.ip[0].name == "192.168.1.1/24"

    def test_loopback_interface_name_pattern_validation(self):
        """Test that name must start with $ symbol."""
        # Valid name starting with $
        valid_data = {
            "name": "$my-loopback",
            "folder": "Test Folder",
        }
        model = LoopbackInterfaceCreateModel(**valid_data)
        assert model.name == "$my-loopback"

        # Invalid name not starting with $
        invalid_data = {
            "name": "loopback1",
            "folder": "Test Folder",
        }
        with pytest.raises(ValidationError) as exc_info:
            LoopbackInterfaceCreateModel(**invalid_data)
        assert "String should match pattern" in str(exc_info.value)

    def test_loopback_interface_default_value_pattern(self):
        """Test default_value pattern validation."""
        # Valid default value
        valid_data = {
            "name": "$loopback",
            "folder": "Test Folder",
            "default_value": "loopback.123",
        }
        model = LoopbackInterfaceCreateModel(**valid_data)
        assert model.default_value == "loopback.123"

        # Invalid default value
        invalid_data = {
            "name": "$loopback",
            "folder": "Test Folder",
            "default_value": "loopback.0",  # Must start from 1
        }
        with pytest.raises(ValidationError) as exc_info:
            LoopbackInterfaceCreateModel(**invalid_data)
        assert "String should match pattern" in str(exc_info.value)

    def test_loopback_interface_mtu_validation(self):
        """Test MTU value constraints."""
        # Valid MTU
        valid_data = {
            "name": "$loopback",
            "folder": "Test Folder",
            "mtu": 1500,
        }
        model = LoopbackInterfaceCreateModel(**valid_data)
        assert model.mtu == 1500

        # MTU too low
        invalid_data = {
            "name": "$loopback",
            "folder": "Test Folder",
            "mtu": 500,  # Min is 576
        }
        with pytest.raises(ValidationError) as exc_info:
            LoopbackInterfaceCreateModel(**invalid_data)
        assert "greater than or equal to 576" in str(exc_info.value)

        # MTU too high
        invalid_data = {
            "name": "$loopback",
            "folder": "Test Folder",
            "mtu": 10000,  # Max is 9216
        }
        with pytest.raises(ValidationError) as exc_info:
            LoopbackInterfaceCreateModel(**invalid_data)
        assert "less than or equal to 9216" in str(exc_info.value)

    def test_loopback_interface_create_model_container_validation(self):
        """Test validation of container fields in LoopbackInterfaceCreateModel."""
        # Valid with folder
        valid_data = {
            "name": "$loopback",
            "folder": "Test Folder",
        }
        model = LoopbackInterfaceCreateModel(**valid_data)
        assert model.folder == "Test Folder"
        assert model.snippet is None
        assert model.device is None

        # Valid with snippet
        valid_with_snippet = {
            "name": "$loopback",
            "snippet": "Test Snippet",
        }
        model = LoopbackInterfaceCreateModel(**valid_with_snippet)
        assert model.snippet == "Test Snippet"
        assert model.folder is None
        assert model.device is None

        # Valid with device
        valid_with_device = {
            "name": "$loopback",
            "device": "Test Device",
        }
        model = LoopbackInterfaceCreateModel(**valid_with_device)
        assert model.device == "Test Device"
        assert model.folder is None
        assert model.snippet is None

        # Invalid with no container
        invalid_no_container = {
            "name": "$loopback",
        }
        with pytest.raises(ValueError) as exc_info:
            LoopbackInterfaceCreateModel(**invalid_no_container)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

        # Invalid with multiple containers
        invalid_multiple_containers = {
            "name": "$loopback",
            "folder": "Test Folder",
            "snippet": "Test Snippet",
        }
        with pytest.raises(ValueError) as exc_info:
            LoopbackInterfaceCreateModel(**invalid_multiple_containers)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_loopback_interface_ipv6_config(self):
        """Test IPv6 configuration."""
        valid_data = {
            "name": "$loopback",
            "folder": "Test Folder",
            "ipv6": {
                "enabled": True,
                "address": [
                    {"name": "2001:DB8::1/128", "enable_on_interface": True},
                ],
            },
        }
        model = LoopbackInterfaceCreateModel(**valid_data)
        assert model.ipv6.enabled is True
        assert len(model.ipv6.address) == 1
        assert model.ipv6.address[0].name == "2001:DB8::1/128"

    def test_loopback_interface_update_model(self):
        """Test validation of LoopbackInterfaceUpdateModel."""
        valid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "$loopback-updated",
            "folder": "Test Folder",
            "mtu": 9000,
        }
        model = LoopbackInterfaceUpdateModel(**valid_data)
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "$loopback-updated"
        assert model.mtu == 9000

        # Invalid UUID
        invalid_id = valid_data.copy()
        invalid_id["id"] = "not-a-uuid"
        with pytest.raises(ValidationError):
            LoopbackInterfaceUpdateModel(**invalid_id)

    def test_loopback_interface_response_model(self):
        """Test validation of LoopbackInterfaceResponseModel."""
        valid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "$loopback-response",
            "folder": "Test Folder",
            "mtu": 1500,
            "ip": [{"name": "10.0.0.1/32"}],
        }
        model = LoopbackInterfaceResponseModel(**valid_data)
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "$loopback-response"
        assert model.folder == "Test Folder"
        assert len(model.ip) == 1

        # Missing required ID
        invalid_data = valid_data.copy()
        del invalid_data["id"]
        with pytest.raises(ValidationError):
            LoopbackInterfaceResponseModel(**invalid_data)


class TestExtraFieldsForbidden:
    """Tests for extra='forbid' validation on Loopback Interface models."""

    def test_create_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on LoopbackInterfaceCreateModel."""
        data = {
            "name": "$loopback",
            "folder": "Test Folder",
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            LoopbackInterfaceCreateModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_update_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on LoopbackInterfaceUpdateModel."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "$loopback",
            "folder": "Test Folder",
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            LoopbackInterfaceUpdateModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_response_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on LoopbackInterfaceResponseModel."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "$loopback",
            "folder": "Test Folder",
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            LoopbackInterfaceResponseModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)
