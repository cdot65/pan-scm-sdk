"""Test models for Aggregate Interface."""

from uuid import UUID

import pytest
from pydantic import ValidationError

from scm.models.network.aggregate_interface import (
    AggregateInterfaceCreateModel,
    AggregateInterfaceResponseModel,
    AggregateInterfaceUpdateModel,
    AggregateLayer2,
    AggregateLayer3,
)


class TestAggregateInterfaceModels:
    """Test Aggregate Interface Pydantic models."""

    def test_aggregate_interface_base_model_validation(self):
        """Test validation of AggregateInterfaceBaseModel through the Create model."""
        valid_data = {
            "name": "ae1",
            "folder": "Test Folder",
            "comment": "Test aggregate interface",
            "layer3": {
                "ip": [{"name": "192.168.1.1/24"}],
                "mtu": 1500,
            },
        }
        model = AggregateInterfaceCreateModel(**valid_data)
        assert model.name == "ae1"
        assert model.folder == "Test Folder"
        assert model.layer3 is not None
        assert model.layer3.mtu == 1500

    def test_aggregate_interface_layer2_mode(self):
        """Test layer2 mode configuration."""
        valid_data = {
            "name": "ae1",
            "folder": "Test Folder",
            "layer2": {
                "vlan_tag": "100",
                "lacp": {"enable": True, "mode": "active"},
            },
        }
        model = AggregateInterfaceCreateModel(**valid_data)
        assert model.layer2 is not None
        assert model.layer2.vlan_tag == "100"
        assert model.layer2.lacp.enable is True
        assert model.layer2.lacp.mode == "active"

    def test_aggregate_interface_layer3_mode(self):
        """Test layer3 mode configuration."""
        valid_data = {
            "name": "ae1",
            "folder": "Test Folder",
            "layer3": {
                "ip": [{"name": "10.0.0.1/24"}],
                "mtu": 9000,
                "lacp": {"enable": True, "fast_failover": True},
            },
        }
        model = AggregateInterfaceCreateModel(**valid_data)
        assert model.layer3 is not None
        assert model.layer3.mtu == 9000
        assert model.layer3.lacp.enable is True

    def test_aggregate_interface_mode_validation(self):
        """Test that only one interface mode can be configured."""
        # Invalid with both layer2 and layer3
        with pytest.raises(ValueError) as exc_info:
            AggregateInterfaceCreateModel(
                name="ae1",
                folder="Test Folder",
                layer2={"vlan_tag": "100"},
                layer3={"ip": [{"name": "10.0.0.1/24"}]},
            )
        assert "Only one interface mode allowed" in str(exc_info.value)

    def test_aggregate_layer3_ip_mode_validation(self):
        """Test that only one IP mode can be configured in layer3."""
        # Invalid with both static IP and DHCP
        with pytest.raises(ValueError) as exc_info:
            AggregateLayer3(
                ip=[{"name": "10.0.0.1/24"}],
                dhcp_client={"enable": True},
            )
        assert "Only one IP addressing mode allowed" in str(exc_info.value)

    def test_aggregate_interface_create_model_container_validation(self):
        """Test container validation on create model."""
        # Valid with folder
        model = AggregateInterfaceCreateModel(name="ae1", folder="Test")
        assert model.folder == "Test"

        # Invalid with no container
        with pytest.raises(ValueError):
            AggregateInterfaceCreateModel(name="ae1")

        # Invalid with multiple containers
        with pytest.raises(ValueError):
            AggregateInterfaceCreateModel(name="ae1", folder="Test", snippet="Snip")

    def test_aggregate_interface_lacp_config(self):
        """Test LACP configuration options."""
        valid_data = {
            "name": "ae1",
            "folder": "Test",
            "layer3": {
                "lacp": {
                    "enable": True,
                    "fast_failover": True,
                    "mode": "active",
                    "transmission_rate": "fast",
                    "system_priority": 1000,
                    "max_ports": 4,
                },
            },
        }
        model = AggregateInterfaceCreateModel(**valid_data)
        lacp = model.layer3.lacp
        assert lacp.enable is True
        assert lacp.fast_failover is True
        assert lacp.mode == "active"
        assert lacp.transmission_rate == "fast"
        assert lacp.system_priority == 1000
        assert lacp.max_ports == 4

    def test_aggregate_interface_update_model(self):
        """Test AggregateInterfaceUpdateModel."""
        valid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "ae1",
            "folder": "Test",
        }
        model = AggregateInterfaceUpdateModel(**valid_data)
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")

    def test_aggregate_interface_response_model(self):
        """Test AggregateInterfaceResponseModel."""
        valid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "ae1",
            "folder": "Test",
        }
        model = AggregateInterfaceResponseModel(**valid_data)
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")


class TestExtraFieldsForbidden:
    """Tests for extra='forbid' validation."""

    def test_create_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        data = {"name": "ae1", "folder": "Test", "unknown": "fail"}
        with pytest.raises(ValidationError) as exc_info:
            AggregateInterfaceCreateModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)
