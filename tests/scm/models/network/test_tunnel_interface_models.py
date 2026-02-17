"""Test models for Tunnel Interface."""

from uuid import UUID

import pytest
from pydantic import ValidationError

from scm.models.network.tunnel_interface import (
    TunnelInterfaceCreateModel,
    TunnelInterfaceResponseModel,
    TunnelInterfaceUpdateModel,
)


class TestTunnelInterfaceModels:
    """Test Tunnel Interface Pydantic models."""

    def test_tunnel_interface_base_model_validation(self):
        """Test validation of TunnelInterfaceBaseModel through the Create model."""
        valid_data = {
            "name": "tunnel.1",
            "folder": "Test Folder",
            "default_value": "tunnel.1",
            "comment": "Test tunnel interface",
            "mtu": 1500,
            "interface_management_profile": "default-mgmt",
            "ip": [{"name": "192.168.1.1/24"}],
        }
        model = TunnelInterfaceCreateModel(**valid_data)
        assert model.name == "tunnel.1"
        assert model.folder == "Test Folder"
        assert model.default_value == "tunnel.1"
        assert model.comment == "Test tunnel interface"
        assert model.mtu == 1500
        assert model.interface_management_profile == "default-mgmt"
        assert len(model.ip) == 1
        assert model.ip[0].name == "192.168.1.1/24"

    def test_tunnel_interface_default_value_pattern(self):
        """Test default_value pattern validation."""
        # Valid default value
        valid_data = {
            "name": "tunnel.123",
            "folder": "Test Folder",
            "default_value": "tunnel.123",
        }
        model = TunnelInterfaceCreateModel(**valid_data)
        assert model.default_value == "tunnel.123"

        # Invalid default value
        invalid_data = {
            "name": "tunnel.0",
            "folder": "Test Folder",
            "default_value": "tunnel.0",  # Must start from 1
        }
        with pytest.raises(ValidationError) as exc_info:
            TunnelInterfaceCreateModel(**invalid_data)
        assert "String should match pattern" in str(exc_info.value)

    def test_tunnel_interface_mtu_validation(self):
        """Test MTU value constraints."""
        # Valid MTU
        valid_data = {
            "name": "tunnel.1",
            "folder": "Test Folder",
            "mtu": 1500,
        }
        model = TunnelInterfaceCreateModel(**valid_data)
        assert model.mtu == 1500

        # MTU too low
        invalid_data = {
            "name": "tunnel.1",
            "folder": "Test Folder",
            "mtu": 500,  # Min is 576
        }
        with pytest.raises(ValidationError) as exc_info:
            TunnelInterfaceCreateModel(**invalid_data)
        assert "greater than or equal to 576" in str(exc_info.value)

        # MTU too high
        invalid_data = {
            "name": "tunnel.1",
            "folder": "Test Folder",
            "mtu": 10000,  # Max is 9216
        }
        with pytest.raises(ValidationError) as exc_info:
            TunnelInterfaceCreateModel(**invalid_data)
        assert "less than or equal to 9216" in str(exc_info.value)

    def test_tunnel_interface_create_model_container_validation(self):
        """Test validation of container fields in TunnelInterfaceCreateModel."""
        # Valid with folder
        valid_data = {
            "name": "tunnel.1",
            "folder": "Test Folder",
        }
        model = TunnelInterfaceCreateModel(**valid_data)
        assert model.folder == "Test Folder"
        assert model.snippet is None
        assert model.device is None

        # Valid with snippet
        valid_with_snippet = {
            "name": "tunnel.1",
            "snippet": "Test Snippet",
        }
        model = TunnelInterfaceCreateModel(**valid_with_snippet)
        assert model.snippet == "Test Snippet"
        assert model.folder is None
        assert model.device is None

        # Valid with device
        valid_with_device = {
            "name": "tunnel.1",
            "device": "Test Device",
        }
        model = TunnelInterfaceCreateModel(**valid_with_device)
        assert model.device == "Test Device"
        assert model.folder is None
        assert model.snippet is None

        # Invalid with no container
        invalid_no_container = {
            "name": "tunnel.1",
        }
        with pytest.raises(ValueError) as exc_info:
            TunnelInterfaceCreateModel(**invalid_no_container)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

        # Invalid with multiple containers
        invalid_multiple_containers = {
            "name": "tunnel.1",
            "folder": "Test Folder",
            "snippet": "Test Snippet",
        }
        with pytest.raises(ValueError) as exc_info:
            TunnelInterfaceCreateModel(**invalid_multiple_containers)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_tunnel_interface_update_model(self):
        """Test validation of TunnelInterfaceUpdateModel."""
        valid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "tunnel.1-updated",
            "folder": "Test Folder",
            "mtu": 9000,
        }
        model = TunnelInterfaceUpdateModel(**valid_data)
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "tunnel.1-updated"
        assert model.mtu == 9000

        # Invalid UUID
        invalid_id = valid_data.copy()
        invalid_id["id"] = "not-a-uuid"
        with pytest.raises(ValidationError):
            TunnelInterfaceUpdateModel(**invalid_id)

    def test_tunnel_interface_response_model(self):
        """Test validation of TunnelInterfaceResponseModel."""
        valid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "tunnel.1-response",
            "folder": "Test Folder",
            "mtu": 1500,
            "ip": [{"name": "10.0.0.1/32"}],
        }
        model = TunnelInterfaceResponseModel(**valid_data)
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "tunnel.1-response"
        assert model.folder == "Test Folder"
        assert len(model.ip) == 1

        # Missing required ID
        invalid_data = valid_data.copy()
        del invalid_data["id"]
        with pytest.raises(ValidationError):
            TunnelInterfaceResponseModel(**invalid_data)


class TestExtraFieldsForbidden:
    """Tests for extra='forbid' validation on Tunnel Interface models."""

    def test_create_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on TunnelInterfaceCreateModel."""
        data = {
            "name": "tunnel.1",
            "folder": "Test Folder",
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            TunnelInterfaceCreateModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_update_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on TunnelInterfaceUpdateModel."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "tunnel.1",
            "folder": "Test Folder",
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            TunnelInterfaceUpdateModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_response_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on TunnelInterfaceResponseModel."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "tunnel.1",
            "folder": "Test Folder",
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            TunnelInterfaceResponseModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)
