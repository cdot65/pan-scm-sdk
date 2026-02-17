"""Test models for Ethernet Interface."""

from uuid import UUID

import pytest
from pydantic import ValidationError

from scm.models.network.ethernet_interface import (
    EthernetInterfaceCreateModel,
    EthernetInterfaceResponseModel,
    EthernetInterfaceUpdateModel,
    EthernetLayer2,
    EthernetLayer3,
    EthernetTap,
)


class TestEthernetInterfaceModels:
    """Test Ethernet Interface Pydantic models."""

    def test_ethernet_interface_base_model_validation(self):
        """Test validation of EthernetInterfaceBaseModel through the Create model."""
        valid_data = {
            "name": "$wan-interface",
            "default_value": "ethernet1/1",
            "folder": "Test Folder",
            "comment": "Test ethernet interface",
            "layer3": {
                "ip": [{"name": "192.168.1.1/24"}],
                "mtu": 1500,
            },
        }
        model = EthernetInterfaceCreateModel(**valid_data)
        assert model.name == "$wan-interface"
        assert model.default_value == "ethernet1/1"
        assert model.folder == "Test Folder"
        assert model.layer3 is not None
        assert model.layer3.mtu == 1500

    def test_ethernet_interface_name_pattern_validation(self):
        """Test that interface name must start with $."""
        # Valid names with $ prefix
        for name in ["$wan", "$lan-interface", "$eth1_1", "$test123"]:
            model = EthernetInterfaceCreateModel(name=name, folder="Test")
            assert model.name == name

        # Invalid names without $ prefix
        for invalid_name in ["ethernet1/1", "wan-interface", "test"]:
            with pytest.raises(ValidationError):
                EthernetInterfaceCreateModel(name=invalid_name, folder="Test")

    def test_ethernet_interface_default_value_pattern(self):
        """Test default_value pattern validation for physical interface."""
        # Valid default values
        for default in ["ethernet1/1", "ethernet1/2", "ethernet2/1", "ethernet1/1.100"]:
            model = EthernetInterfaceCreateModel(
                name="$test", default_value=default, folder="Test"
            )
            assert model.default_value == default

        # Invalid default values
        for invalid_default in ["eth1/1", "interface1", "1/1"]:
            with pytest.raises(ValidationError):
                EthernetInterfaceCreateModel(
                    name="$test", default_value=invalid_default, folder="Test"
                )

    def test_ethernet_interface_layer2_mode(self):
        """Test layer2 mode configuration."""
        valid_data = {
            "name": "$layer2-interface",
            "folder": "Test Folder",
            "layer2": {
                "vlan_tag": "100",
                "lldp": {"enable": True},
            },
        }
        model = EthernetInterfaceCreateModel(**valid_data)
        assert model.layer2 is not None
        assert model.layer2.vlan_tag == "100"
        assert model.layer2.lldp.enable is True

    def test_ethernet_interface_layer3_static_mode(self):
        """Test layer3 mode with static IP configuration."""
        valid_data = {
            "name": "$static-interface",
            "folder": "Test Folder",
            "layer3": {
                "ip": [{"name": "10.0.0.1/24"}, {"name": "10.0.0.2/24"}],
                "mtu": 9000,
                "interface_management_profile": "mgmt-profile",
            },
        }
        model = EthernetInterfaceCreateModel(**valid_data)
        assert model.layer3 is not None
        assert model.layer3.mtu == 9000
        assert len(model.layer3.ip) == 2
        assert model.layer3.interface_management_profile == "mgmt-profile"

    def test_ethernet_interface_layer3_dhcp_mode(self):
        """Test layer3 mode with DHCP configuration."""
        valid_data = {
            "name": "$dhcp-interface",
            "folder": "Test Folder",
            "layer3": {
                "dhcp_client": {
                    "enable": True,
                    "create_default_route": True,
                    "default_route_metric": 10,
                },
            },
        }
        model = EthernetInterfaceCreateModel(**valid_data)
        assert model.layer3 is not None
        assert model.layer3.dhcp_client is not None
        assert model.layer3.dhcp_client.enable is True

    def test_ethernet_interface_layer3_pppoe_mode(self):
        """Test layer3 mode with PPPoE configuration."""
        valid_data = {
            "name": "$pppoe-interface",
            "folder": "Test Folder",
            "layer3": {
                "pppoe": {
                    "enable": True,
                    "username": "user@isp.com",
                    "password": "secret123",
                    "authentication": "auto",
                },
            },
        }
        model = EthernetInterfaceCreateModel(**valid_data)
        assert model.layer3 is not None
        assert model.layer3.pppoe is not None
        assert model.layer3.pppoe.username == "user@isp.com"
        assert model.layer3.pppoe.authentication == "auto"

    def test_ethernet_interface_tap_mode(self):
        """Test TAP mode configuration."""
        valid_data = {
            "name": "$tap-interface",
            "folder": "Test Folder",
            "tap": {},
        }
        model = EthernetInterfaceCreateModel(**valid_data)
        assert model.tap is not None

    def test_ethernet_interface_mode_validation(self):
        """Test that only one interface mode can be configured."""
        # Invalid with both layer2 and layer3
        with pytest.raises(ValueError) as exc_info:
            EthernetInterfaceCreateModel(
                name="$test",
                folder="Test Folder",
                layer2={"vlan_tag": "100"},
                layer3={"ip": [{"name": "10.0.0.1/24"}]},
            )
        assert "Only one interface mode allowed" in str(exc_info.value)

        # Invalid with layer2 and tap
        with pytest.raises(ValueError) as exc_info:
            EthernetInterfaceCreateModel(
                name="$test",
                folder="Test Folder",
                layer2={"vlan_tag": "100"},
                tap={},
            )
        assert "Only one interface mode allowed" in str(exc_info.value)

        # Invalid with all three
        with pytest.raises(ValueError) as exc_info:
            EthernetInterfaceCreateModel(
                name="$test",
                folder="Test Folder",
                layer2={"vlan_tag": "100"},
                layer3={"ip": [{"name": "10.0.0.1/24"}]},
                tap={},
            )
        assert "Only one interface mode allowed" in str(exc_info.value)

    def test_ethernet_layer3_ip_mode_validation(self):
        """Test that only one IP mode can be configured in layer3."""
        # Invalid with both static IP and DHCP
        with pytest.raises(ValueError) as exc_info:
            EthernetLayer3(
                ip=[{"name": "10.0.0.1/24"}],
                dhcp_client={"enable": True},
            )
        assert "Only one IP addressing mode allowed" in str(exc_info.value)

        # Invalid with DHCP and PPPoE
        with pytest.raises(ValueError) as exc_info:
            EthernetLayer3(
                dhcp_client={"enable": True},
                pppoe={"username": "user", "password": "pass"},
            )
        assert "Only one IP addressing mode allowed" in str(exc_info.value)

        # Invalid with all three
        with pytest.raises(ValueError) as exc_info:
            EthernetLayer3(
                ip=[{"name": "10.0.0.1/24"}],
                dhcp_client={"enable": True},
                pppoe={"username": "user", "password": "pass"},
            )
        assert "Only one IP addressing mode allowed" in str(exc_info.value)

    def test_ethernet_interface_create_model_container_validation(self):
        """Test container validation on create model."""
        # Valid with folder
        model = EthernetInterfaceCreateModel(name="$test", folder="Test")
        assert model.folder == "Test"

        # Invalid with no container
        with pytest.raises(ValueError):
            EthernetInterfaceCreateModel(name="$test")

        # Invalid with multiple containers
        with pytest.raises(ValueError):
            EthernetInterfaceCreateModel(name="$test", folder="Test", snippet="Snip")

    def test_ethernet_interface_link_settings(self):
        """Test link speed, duplex, and state settings."""
        valid_data = {
            "name": "$link-test",
            "folder": "Test",
            "link_speed": "1000",
            "link_duplex": "full",
            "link_state": "up",
        }
        model = EthernetInterfaceCreateModel(**valid_data)
        assert model.link_speed == "1000"
        assert model.link_duplex == "full"
        assert model.link_state == "up"

    def test_ethernet_interface_poe_config(self):
        """Test Power over Ethernet configuration."""
        valid_data = {
            "name": "$poe-interface",
            "folder": "Test",
            "poe": {
                "poe_enabled": True,
                "poe_rsvd_pwr": 30,
            },
        }
        model = EthernetInterfaceCreateModel(**valid_data)
        assert model.poe is not None
        assert model.poe.poe_enabled is True
        assert model.poe.poe_rsvd_pwr == 30

    def test_ethernet_interface_layer3_arp(self):
        """Test layer3 ARP configuration."""
        valid_data = {
            "name": "$arp-interface",
            "folder": "Test",
            "layer3": {
                "ip": [{"name": "10.0.0.1/24"}],
                "arp": [
                    {"name": "10.0.0.100", "hw_address": "00:11:22:33:44:55"},
                    {"name": "10.0.0.101", "hw_address": "00:11:22:33:44:56"},
                ],
            },
        }
        model = EthernetInterfaceCreateModel(**valid_data)
        assert model.layer3 is not None
        assert len(model.layer3.arp) == 2
        assert model.layer3.arp[0].hw_address == "00:11:22:33:44:55"

    def test_ethernet_interface_layer3_ddns(self):
        """Test layer3 DDNS configuration."""
        valid_data = {
            "name": "$ddns-interface",
            "folder": "Test",
            "layer3": {
                "dhcp_client": {"enable": True},
                "ddns_config": {
                    "ddns_enabled": True,
                    "ddns_vendor": "dyndns",
                    "ddns_hostname": "myhost.example.com",
                },
            },
        }
        model = EthernetInterfaceCreateModel(**valid_data)
        assert model.layer3 is not None
        assert model.layer3.ddns_config is not None
        assert model.layer3.ddns_config.ddns_enabled is True

    def test_ethernet_interface_update_model(self):
        """Test EthernetInterfaceUpdateModel."""
        valid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "$update-interface",
            "folder": "Test",
        }
        model = EthernetInterfaceUpdateModel(**valid_data)
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")

    def test_ethernet_interface_response_model(self):
        """Test EthernetInterfaceResponseModel."""
        valid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "$response-interface",
            "folder": "Test",
        }
        model = EthernetInterfaceResponseModel(**valid_data)
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")

    def test_ethernet_layer2_vlan_pattern(self):
        """Test VLAN tag pattern validation in layer2."""
        # Valid VLAN tags
        for vlan in ["1", "100", "1000", "4096"]:
            model = EthernetLayer2(vlan_tag=vlan)
            assert model.vlan_tag == vlan

        # Invalid VLAN tag (0)
        with pytest.raises(ValidationError):
            EthernetLayer2(vlan_tag="0")

        # Invalid VLAN tag (too high)
        with pytest.raises(ValidationError):
            EthernetLayer2(vlan_tag="4097")


class TestExtraFieldsForbidden:
    """Tests for extra='forbid' validation."""

    def test_create_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        data = {"name": "$test", "folder": "Test", "unknown": "fail"}
        with pytest.raises(ValidationError) as exc_info:
            EthernetInterfaceCreateModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_layer2_extra_fields_forbidden(self):
        """Test that extra fields are rejected in layer2."""
        with pytest.raises(ValidationError) as exc_info:
            EthernetLayer2(vlan_tag="100", unknown_field="value")
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_layer3_extra_fields_forbidden(self):
        """Test that extra fields are rejected in layer3."""
        with pytest.raises(ValidationError) as exc_info:
            EthernetLayer3(mtu=1500, unknown_field="value")
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_tap_extra_fields_forbidden(self):
        """Test that extra fields are rejected in tap."""
        with pytest.raises(ValidationError) as exc_info:
            EthernetTap(unknown_field="value")
        assert "Extra inputs are not permitted" in str(exc_info.value)
