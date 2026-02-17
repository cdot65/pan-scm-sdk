"""Test models for Layer3 Subinterface."""

from uuid import UUID

import pytest
from pydantic import ValidationError

from scm.models.network.layer3_subinterface import (
    Layer3SubinterfaceCreateModel,
    Layer3SubinterfaceResponseModel,
    Layer3SubinterfaceUpdateModel,
)


class TestLayer3SubinterfaceModels:
    """Test Layer3 Subinterface Pydantic models."""

    def test_layer3_subinterface_base_model_validation(self):
        """Test validation of Layer3SubinterfaceBaseModel through the Create model."""
        valid_data = {
            "name": "ethernet1/1.100",
            "tag": 100,
            "folder": "Test Folder",
            "parent_interface": "ethernet1/1",
            "comment": "Test layer3 subinterface",
            "mtu": 1500,
            "ip": [{"name": "192.168.1.1/24"}],
        }
        model = Layer3SubinterfaceCreateModel(**valid_data)
        assert model.name == "ethernet1/1.100"
        assert model.tag == 100
        assert model.folder == "Test Folder"
        assert model.mtu == 1500
        assert len(model.ip) == 1

    def test_layer3_subinterface_tag_validation(self):
        """Test VLAN tag value validation."""
        # Valid tags
        model = Layer3SubinterfaceCreateModel(name="eth1.1", tag=1, folder="Test")
        assert model.tag == 1

        model = Layer3SubinterfaceCreateModel(name="eth1.1", tag=4096, folder="Test")
        assert model.tag == 4096

        # Invalid tag (0)
        with pytest.raises(ValidationError):
            Layer3SubinterfaceCreateModel(name="eth1.1", tag=0, folder="Test")

        # Invalid tag (>4096)
        with pytest.raises(ValidationError):
            Layer3SubinterfaceCreateModel(name="eth1.1", tag=4097, folder="Test")

    def test_layer3_subinterface_mtu_validation(self):
        """Test MTU value constraints."""
        # Valid MTU
        model = Layer3SubinterfaceCreateModel(name="eth1.1", folder="Test", mtu=1500)
        assert model.mtu == 1500

        # MTU too low
        with pytest.raises(ValidationError):
            Layer3SubinterfaceCreateModel(name="eth1.1", folder="Test", mtu=500)

        # MTU too high
        with pytest.raises(ValidationError):
            Layer3SubinterfaceCreateModel(name="eth1.1", folder="Test", mtu=10000)

    def test_layer3_subinterface_ip_mode_validation(self):
        """Test that only one IP mode can be configured."""
        # Valid with static IP only
        model = Layer3SubinterfaceCreateModel(
            name="eth1.1",
            folder="Test",
            ip=[{"name": "192.168.1.1/24"}],
        )
        assert model.ip is not None

        # Valid with DHCP only
        model = Layer3SubinterfaceCreateModel(
            name="eth1.1",
            folder="Test",
            dhcp_client={"enable": True},
        )
        assert model.dhcp_client is not None

        # Invalid with both static IP and DHCP
        with pytest.raises(ValueError) as exc_info:
            Layer3SubinterfaceCreateModel(
                name="eth1.1",
                folder="Test",
                ip=[{"name": "192.168.1.1/24"}],
                dhcp_client={"enable": True},
            )
        assert "Only one IP addressing mode allowed" in str(exc_info.value)

    def test_layer3_subinterface_create_model_container_validation(self):
        """Test container validation on create model."""
        # Invalid with no container
        with pytest.raises(ValueError):
            Layer3SubinterfaceCreateModel(name="eth1.1")

        # Invalid with multiple containers
        with pytest.raises(ValueError):
            Layer3SubinterfaceCreateModel(name="eth1.1", folder="Test", snippet="Snip")

    def test_layer3_subinterface_update_model(self):
        """Test Layer3SubinterfaceUpdateModel."""
        valid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "eth1.1",
            "folder": "Test",
        }
        model = Layer3SubinterfaceUpdateModel(**valid_data)
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")

    def test_layer3_subinterface_response_model(self):
        """Test Layer3SubinterfaceResponseModel."""
        valid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "eth1.1",
            "folder": "Test",
        }
        model = Layer3SubinterfaceResponseModel(**valid_data)
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")


class TestExtraFieldsForbidden:
    """Tests for extra='forbid' validation."""

    def test_create_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        data = {"name": "eth1.1", "folder": "Test", "unknown": "fail"}
        with pytest.raises(ValidationError) as exc_info:
            Layer3SubinterfaceCreateModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)
