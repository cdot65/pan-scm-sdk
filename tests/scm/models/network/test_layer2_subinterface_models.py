"""Test models for Layer2 Subinterface."""

from uuid import UUID

import pytest
from pydantic import ValidationError

from scm.models.network.layer2_subinterface import (
    Layer2SubinterfaceCreateModel,
    Layer2SubinterfaceResponseModel,
    Layer2SubinterfaceUpdateModel,
)


class TestLayer2SubinterfaceModels:
    """Test Layer2 Subinterface Pydantic models."""

    def test_layer2_subinterface_base_model_validation(self):
        """Test validation of Layer2SubinterfaceBaseModel through the Create model."""
        valid_data = {
            "name": "ethernet1/1.100",
            "vlan_tag": "100",
            "folder": "Test Folder",
            "parent_interface": "ethernet1/1",
            "comment": "Test layer2 subinterface",
        }
        model = Layer2SubinterfaceCreateModel(**valid_data)
        assert model.name == "ethernet1/1.100"
        assert model.vlan_tag == "100"
        assert model.folder == "Test Folder"
        assert model.parent_interface == "ethernet1/1"

    def test_layer2_subinterface_vlan_tag_validation(self):
        """Test VLAN tag pattern validation."""
        # Valid VLAN tags
        for vlan in ["1", "100", "4096"]:
            valid_data = {"name": "eth1.1", "vlan_tag": vlan, "folder": "Test"}
            model = Layer2SubinterfaceCreateModel(**valid_data)
            assert model.vlan_tag == vlan

        # Invalid VLAN tag (0)
        invalid_data = {"name": "eth1.0", "vlan_tag": "0", "folder": "Test"}
        with pytest.raises(ValidationError):
            Layer2SubinterfaceCreateModel(**invalid_data)

    def test_layer2_subinterface_create_model_container_validation(self):
        """Test container validation on create model."""
        # Valid with folder
        model = Layer2SubinterfaceCreateModel(name="eth1.1", vlan_tag="100", folder="Test")
        assert model.folder == "Test"

        # Invalid with no container
        with pytest.raises(ValueError) as exc_info:
            Layer2SubinterfaceCreateModel(name="eth1.1", vlan_tag="100")
        assert "Exactly one of 'folder', 'snippet', or 'device'" in str(exc_info.value)

        # Invalid with multiple containers
        with pytest.raises(ValueError):
            Layer2SubinterfaceCreateModel(name="eth1.1", vlan_tag="100", folder="Test", snippet="Snip")

    def test_layer2_subinterface_update_model(self):
        """Test Layer2SubinterfaceUpdateModel."""
        valid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "eth1.1",
            "vlan_tag": "100",
            "folder": "Test",
        }
        model = Layer2SubinterfaceUpdateModel(**valid_data)
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")

    def test_layer2_subinterface_response_model(self):
        """Test Layer2SubinterfaceResponseModel."""
        valid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "eth1.1",
            "vlan_tag": "100",
            "folder": "Test",
        }
        model = Layer2SubinterfaceResponseModel(**valid_data)
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")


class TestExtraFieldsForbidden:
    """Tests for extra='forbid' validation."""

    def test_create_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        data = {"name": "eth1.1", "vlan_tag": "100", "folder": "Test", "unknown": "fail"}
        with pytest.raises(ValidationError) as exc_info:
            Layer2SubinterfaceCreateModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)
