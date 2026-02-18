"""Test models for DHCP Interface."""

from uuid import UUID

from pydantic import ValidationError
import pytest

from scm.models.network import (
    DhcpDualServer,
    DhcpInheritance,
    DhcpInterfaceCreateModel,
    DhcpInterfaceResponseModel,
    DhcpInterfaceUpdateModel,
    DhcpLease,
    DhcpRelay,
    DhcpRelayIp,
    DhcpReserved,
    DhcpServer,
    DhcpServerOption,
)


class TestDhcpInterfaceModels:
    """Test DHCP Interface Pydantic models."""

    def test_dhcp_interface_base_model_with_server(self):
        """Test validation of DhcpInterfaceBaseModel through the Create model with server config."""
        valid_data = {
            "name": "ethernet1/1",
            "folder": "Test Folder",
            "server": {
                "mode": "auto",
                "probe_ip": True,
                "ip_pool": ["10.0.0.10-10.0.0.100"],
                "option": {
                    "lease": {"timeout": 120},
                    "gateway": "10.0.0.1",
                    "subnet_mask": "255.255.255.0",
                    "dns": {"primary": "8.8.8.8", "secondary": "8.8.4.4"},
                },
            },
        }
        model = DhcpInterfaceCreateModel(**valid_data)
        assert model.name == "ethernet1/1"
        assert model.folder == "Test Folder"
        assert model.server.mode.value == "auto"
        assert model.server.probe_ip is True
        assert model.server.ip_pool == ["10.0.0.10-10.0.0.100"]
        assert model.server.option.lease.timeout == 120
        assert model.server.option.gateway == "10.0.0.1"
        assert model.server.option.subnet_mask == "255.255.255.0"
        assert model.server.option.dns.primary == "8.8.8.8"
        assert model.server.option.dns.secondary == "8.8.4.4"

    def test_dhcp_interface_base_model_with_relay(self):
        """Test validation of DhcpInterfaceBaseModel through the Create model with relay config."""
        valid_data = {
            "name": "ethernet1/2",
            "folder": "Test Folder",
            "relay": {
                "ip": {
                    "enabled": True,
                    "server": ["10.0.0.1", "10.0.0.2"],
                },
            },
        }
        model = DhcpInterfaceCreateModel(**valid_data)
        assert model.name == "ethernet1/2"
        assert model.relay.ip.enabled is True
        assert model.relay.ip.server == ["10.0.0.1", "10.0.0.2"]

    def test_server_relay_mutual_exclusivity(self):
        """Test that server and relay cannot both be specified."""
        invalid_data = {
            "name": "ethernet1/1",
            "folder": "Test Folder",
            "server": {
                "mode": "auto",
            },
            "relay": {
                "ip": {
                    "server": ["10.0.0.1"],
                },
            },
        }
        with pytest.raises(ValueError) as exc_info:
            DhcpInterfaceCreateModel(**invalid_data)
        assert "Only one of 'server' or 'relay' can be specified" in str(exc_info.value)

    def test_dhcp_interface_create_model_container_validation(self):
        """Test validation of container fields in DhcpInterfaceCreateModel."""
        valid_data = {
            "name": "ethernet1/1",
            "folder": "Test Folder",
        }
        model = DhcpInterfaceCreateModel(**valid_data)
        assert model.folder == "Test Folder"
        assert model.snippet is None
        assert model.device is None

        # Test with snippet container
        valid_with_snippet = {
            "name": "ethernet1/1",
            "snippet": "Test Snippet",
        }
        model = DhcpInterfaceCreateModel(**valid_with_snippet)
        assert model.snippet == "Test Snippet"
        assert model.folder is None
        assert model.device is None

        # Test with device container
        valid_with_device = {
            "name": "ethernet1/1",
            "device": "Test Device",
        }
        model = DhcpInterfaceCreateModel(**valid_with_device)
        assert model.device == "Test Device"
        assert model.folder is None
        assert model.snippet is None

        # Test with no container
        invalid_no_container = {
            "name": "ethernet1/1",
        }
        with pytest.raises(ValueError) as exc_info:
            DhcpInterfaceCreateModel(**invalid_no_container)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

        # Test with multiple containers
        invalid_multiple_containers = {
            "name": "ethernet1/1",
            "folder": "Test Folder",
            "snippet": "Test Snippet",
        }
        with pytest.raises(ValueError) as exc_info:
            DhcpInterfaceCreateModel(**invalid_multiple_containers)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_dhcp_interface_update_model(self):
        """Test validation of DhcpInterfaceUpdateModel."""
        valid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "ethernet1/1",
            "folder": "Test Folder",
            "server": {
                "mode": "enabled",
                "ip_pool": ["10.0.0.10-10.0.0.100"],
            },
        }
        model = DhcpInterfaceUpdateModel(**valid_data)
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "ethernet1/1"
        assert model.folder == "Test Folder"
        assert model.server.mode.value == "enabled"

        # Test invalid UUID
        invalid_id = valid_data.copy()
        invalid_id["id"] = "not-a-uuid"
        with pytest.raises(ValidationError):
            DhcpInterfaceUpdateModel(**invalid_id)

    def test_dhcp_interface_response_model(self):
        """Test validation of DhcpInterfaceResponseModel."""
        valid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "ethernet1/1",
            "folder": "Test Folder",
            "server": {
                "mode": "auto",
                "ip_pool": ["10.0.0.10-10.0.0.100"],
            },
        }
        model = DhcpInterfaceResponseModel(**valid_data)
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "ethernet1/1"
        assert model.folder == "Test Folder"
        assert model.server.mode.value == "auto"

        # Test missing required ID
        invalid_data = valid_data.copy()
        del invalid_data["id"]
        with pytest.raises(ValidationError):
            DhcpInterfaceResponseModel(**invalid_data)


class TestDhcpLeaseModel:
    """Test DhcpLease model."""

    def test_lease_with_timeout(self):
        """Test lease with timeout."""
        lease = DhcpLease(timeout=120)
        assert lease.timeout == 120
        assert lease.unlimited is None

    def test_lease_with_unlimited(self):
        """Test lease with unlimited."""
        lease = DhcpLease(unlimited={})
        assert lease.unlimited == {}
        assert lease.timeout is None

    def test_lease_mutual_exclusivity(self):
        """Test that unlimited and timeout are mutually exclusive."""
        with pytest.raises(ValueError) as exc_info:
            DhcpLease(unlimited={}, timeout=120)
        assert "Only one of 'unlimited' or 'timeout' can be specified" in str(exc_info.value)

    def test_lease_empty(self):
        """Test lease with no values."""
        lease = DhcpLease()
        assert lease.unlimited is None
        assert lease.timeout is None


class TestDhcpDualServerModel:
    """Test DhcpDualServer model."""

    def test_dual_server_both(self):
        """Test dual server with both primary and secondary."""
        server = DhcpDualServer(primary="8.8.8.8", secondary="8.8.4.4")
        assert server.primary == "8.8.8.8"
        assert server.secondary == "8.8.4.4"

    def test_dual_server_primary_only(self):
        """Test dual server with primary only."""
        server = DhcpDualServer(primary="8.8.8.8")
        assert server.primary == "8.8.8.8"
        assert server.secondary is None

    def test_dual_server_empty(self):
        """Test dual server with no values."""
        server = DhcpDualServer()
        assert server.primary is None
        assert server.secondary is None


class TestDhcpInheritanceModel:
    """Test DhcpInheritance model."""

    def test_inheritance_with_source(self):
        """Test inheritance with source."""
        inheritance = DhcpInheritance(source="parent-interface")
        assert inheritance.source == "parent-interface"

    def test_inheritance_empty(self):
        """Test inheritance with no source."""
        inheritance = DhcpInheritance()
        assert inheritance.source is None


class TestDhcpReservedModel:
    """Test DhcpReserved model."""

    def test_reserved_valid(self):
        """Test valid reserved entry."""
        reserved = DhcpReserved(name="server1", mac="00:11:22:33:44:55")
        assert reserved.name == "server1"
        assert reserved.mac == "00:11:22:33:44:55"
        assert reserved.description is None

    def test_reserved_with_description(self):
        """Test reserved entry with description."""
        reserved = DhcpReserved(
            name="server1",
            mac="00:11:22:33:44:55",
            description="Main server",
        )
        assert reserved.description == "Main server"

    def test_reserved_missing_required(self):
        """Test reserved entry missing required fields."""
        with pytest.raises(ValidationError):
            DhcpReserved(name="server1")  # Missing mac

        with pytest.raises(ValidationError):
            DhcpReserved(mac="00:11:22:33:44:55")  # Missing name


class TestDhcpServerOptionModel:
    """Test DhcpServerOption model."""

    def test_server_option_full(self):
        """Test server option with all fields."""
        option = DhcpServerOption(
            lease=DhcpLease(timeout=120),
            inheritance=DhcpInheritance(source="parent"),
            gateway="10.0.0.1",
            subnet_mask="255.255.255.0",
            dns=DhcpDualServer(primary="8.8.8.8", secondary="8.8.4.4"),
            wins=DhcpDualServer(primary="10.0.0.5"),
            nis=DhcpDualServer(primary="10.0.0.6"),
            ntp=DhcpDualServer(primary="10.0.0.7"),
            pop3_server="mail.example.com",
            smtp_server="smtp.example.com",
            dns_suffix="example.com",
        )
        assert option.lease.timeout == 120
        assert option.gateway == "10.0.0.1"
        assert option.subnet_mask == "255.255.255.0"
        assert option.dns.primary == "8.8.8.8"
        assert option.wins.primary == "10.0.0.5"
        assert option.nis.primary == "10.0.0.6"
        assert option.ntp.primary == "10.0.0.7"
        assert option.pop3_server == "mail.example.com"
        assert option.smtp_server == "smtp.example.com"
        assert option.dns_suffix == "example.com"


class TestDhcpServerModel:
    """Test DhcpServer model."""

    def test_server_full(self):
        """Test server with all fields."""
        server = DhcpServer(
            probe_ip=True,
            mode="auto",
            ip_pool=["10.0.0.10-10.0.0.100"],
            reserved=[
                DhcpReserved(name="server1", mac="00:11:22:33:44:55"),
            ],
            option=DhcpServerOption(
                gateway="10.0.0.1",
                subnet_mask="255.255.255.0",
            ),
        )
        assert server.probe_ip is True
        assert server.mode.value == "auto"
        assert server.ip_pool == ["10.0.0.10-10.0.0.100"]
        assert len(server.reserved) == 1
        assert server.reserved[0].name == "server1"

    def test_server_mode_enum(self):
        """Test server mode enum values."""
        for mode in ["auto", "enabled", "disabled"]:
            server = DhcpServer(mode=mode)
            assert server.mode.value == mode

        with pytest.raises(ValidationError):
            DhcpServer(mode="invalid_mode")


class TestDhcpRelayModel:
    """Test DhcpRelay and DhcpRelayIp models."""

    def test_relay_ip_valid(self):
        """Test valid relay IP configuration."""
        relay_ip = DhcpRelayIp(enabled=True, server=["10.0.0.1", "10.0.0.2"])
        assert relay_ip.enabled is True
        assert relay_ip.server == ["10.0.0.1", "10.0.0.2"]

    def test_relay_ip_default_enabled(self):
        """Test relay IP default enabled value."""
        relay_ip = DhcpRelayIp(server=["10.0.0.1"])
        assert relay_ip.enabled is True

    def test_relay_ip_missing_server(self):
        """Test relay IP missing required server field."""
        with pytest.raises(ValidationError):
            DhcpRelayIp(enabled=True)

    def test_relay_valid(self):
        """Test valid relay configuration."""
        relay = DhcpRelay(ip=DhcpRelayIp(server=["10.0.0.1"]))
        assert relay.ip.server == ["10.0.0.1"]

    def test_relay_missing_ip(self):
        """Test relay missing required ip field."""
        with pytest.raises(ValidationError):
            DhcpRelay()


class TestExtraFieldsForbidden:
    """Tests for extra='forbid' validation on all DHCP Interface models."""

    def test_create_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on DhcpInterfaceCreateModel."""
        data = {
            "name": "ethernet1/1",
            "folder": "Test Folder",
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            DhcpInterfaceCreateModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_update_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on DhcpInterfaceUpdateModel."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "ethernet1/1",
            "folder": "Test Folder",
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            DhcpInterfaceUpdateModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_response_model_extra_fields_ignored(self):
        """Test that extra fields are silently ignored on DhcpInterfaceResponseModel."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "ethernet1/1",
            "folder": "Test Folder",
            "unknown_field": "should_be_ignored",
        }
        model = DhcpInterfaceResponseModel(**data)
        assert not hasattr(model, "unknown_field")

    def test_dhcp_dual_server_extra_fields_forbidden(self):
        """Test that extra fields are rejected on DhcpDualServer."""
        data = {
            "primary": "8.8.8.8",
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            DhcpDualServer(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_dhcp_lease_extra_fields_forbidden(self):
        """Test that extra fields are rejected on DhcpLease."""
        data = {
            "timeout": 120,
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            DhcpLease(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_dhcp_reserved_extra_fields_forbidden(self):
        """Test that extra fields are rejected on DhcpReserved."""
        data = {
            "name": "server1",
            "mac": "00:11:22:33:44:55",
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            DhcpReserved(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_dhcp_server_option_extra_fields_forbidden(self):
        """Test that extra fields are rejected on DhcpServerOption."""
        data = {
            "gateway": "10.0.0.1",
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            DhcpServerOption(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_dhcp_server_extra_fields_forbidden(self):
        """Test that extra fields are rejected on DhcpServer."""
        data = {
            "mode": "auto",
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            DhcpServer(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_dhcp_relay_ip_extra_fields_forbidden(self):
        """Test that extra fields are rejected on DhcpRelayIp."""
        data = {
            "server": ["10.0.0.1"],
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            DhcpRelayIp(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_dhcp_relay_extra_fields_forbidden(self):
        """Test that extra fields are rejected on DhcpRelay."""
        data = {
            "ip": {"server": ["10.0.0.1"]},
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            DhcpRelay(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)
