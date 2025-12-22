"""Test models for VLAN Interface."""

from uuid import UUID

import pytest
from pydantic import ValidationError

from scm.models.network.vlan_interface import (
    VlanInterfaceCreateModel,
    VlanInterfaceResponseModel,
    VlanInterfaceUpdateModel,
)


class TestVlanInterfaceModels:
    """Test VLAN Interface Pydantic models."""

    def test_vlan_interface_base_model_validation(self):
        """Test validation of VlanInterfaceBaseModel through the Create model."""
        valid_data = {
            "name": "vlan.100",
            "default_value": "vlan.100",
            "vlan_tag": "100",
            "folder": "Test Folder",
            "comment": "Test VLAN interface",
            "mtu": 1500,
            "ip": [{"name": "192.168.1.1/24"}],
        }
        model = VlanInterfaceCreateModel(**valid_data)
        assert model.name == "vlan.100"
        assert model.vlan_tag == "100"
        assert model.folder == "Test Folder"
        assert model.mtu == 1500

    def test_vlan_interface_default_value_pattern(self):
        """Test default_value pattern validation."""
        # Valid default values
        model = VlanInterfaceCreateModel(name="vlan.1", folder="Test", default_value="vlan.1")
        assert model.default_value == "vlan.1"

        model = VlanInterfaceCreateModel(name="vlan.100", folder="Test", default_value="vlan.100")
        assert model.default_value == "vlan.100"

        # Invalid default value (0)
        with pytest.raises(ValidationError):
            VlanInterfaceCreateModel(name="vlan.0", folder="Test", default_value="vlan.0")

    def test_vlan_interface_vlan_tag_validation(self):
        """Test VLAN tag pattern validation."""
        # Valid VLAN tags
        for vlan in ["1", "100", "4096"]:
            model = VlanInterfaceCreateModel(name="vlan.1", vlan_tag=vlan, folder="Test")
            assert model.vlan_tag == vlan

        # Invalid VLAN tag (0)
        with pytest.raises(ValidationError):
            VlanInterfaceCreateModel(name="vlan.1", vlan_tag="0", folder="Test")

    def test_vlan_interface_mtu_validation(self):
        """Test MTU value constraints."""
        # Valid MTU
        model = VlanInterfaceCreateModel(name="vlan.1", folder="Test", mtu=1500)
        assert model.mtu == 1500

        # MTU too low
        with pytest.raises(ValidationError):
            VlanInterfaceCreateModel(name="vlan.1", folder="Test", mtu=500)

        # MTU too high
        with pytest.raises(ValidationError):
            VlanInterfaceCreateModel(name="vlan.1", folder="Test", mtu=10000)

    def test_vlan_interface_ip_mode_validation(self):
        """Test that only one IP mode can be configured."""
        # Valid with static IP only
        model = VlanInterfaceCreateModel(
            name="vlan.1",
            folder="Test",
            ip=[{"name": "192.168.1.1/24"}],
        )
        assert model.ip is not None

        # Valid with DHCP only
        model = VlanInterfaceCreateModel(
            name="vlan.1",
            folder="Test",
            dhcp_client={"enable": True},
        )
        assert model.dhcp_client is not None

        # Invalid with both static IP and DHCP
        with pytest.raises(ValueError) as exc_info:
            VlanInterfaceCreateModel(
                name="vlan.1",
                folder="Test",
                ip=[{"name": "192.168.1.1/24"}],
                dhcp_client={"enable": True},
            )
        assert "Only one IP addressing mode allowed" in str(exc_info.value)

    def test_vlan_interface_create_model_container_validation(self):
        """Test container validation on create model."""
        # Valid with folder
        model = VlanInterfaceCreateModel(name="vlan.1", folder="Test")
        assert model.folder == "Test"

        # Invalid with no container
        with pytest.raises(ValueError):
            VlanInterfaceCreateModel(name="vlan.1")

        # Invalid with multiple containers
        with pytest.raises(ValueError):
            VlanInterfaceCreateModel(name="vlan.1", folder="Test", snippet="Snip")

    def test_vlan_interface_update_model(self):
        """Test VlanInterfaceUpdateModel."""
        valid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "vlan.1",
            "folder": "Test",
        }
        model = VlanInterfaceUpdateModel(**valid_data)
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")

    def test_vlan_interface_response_model(self):
        """Test VlanInterfaceResponseModel."""
        valid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "vlan.1",
            "folder": "Test",
        }
        model = VlanInterfaceResponseModel(**valid_data)
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")


class TestExtraFieldsForbidden:
    """Tests for extra='forbid' validation."""

    def test_create_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        data = {"name": "vlan.1", "folder": "Test", "unknown": "fail"}
        with pytest.raises(ValidationError) as exc_info:
            VlanInterfaceCreateModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)
