"""Test models for IPsec Tunnels."""

from uuid import UUID

from pydantic import ValidationError
import pytest

from scm.models.network import (
    AutoKey,
    IkeGatewayRef,
    IPsecTunnelCreateModel,
    IPsecTunnelResponseModel,
    IPsecTunnelUpdateModel,
    PortPair,
    ProxyId,
    ProxyIdProtocol,
    TunnelMonitor,
)


class TestIPsecTunnelModels:
    """Test IPsec Tunnel Pydantic models."""

    def test_ipsec_tunnel_base_model_validation(self):
        """Test validation of IPsecTunnelBaseModel through the Create model."""
        # Test valid model
        valid_data = {
            "name": "test-tunnel",
            "folder": "Test Folder",
            "auto_key": {
                "ike_gateway": [{"name": "gw1"}],
                "ipsec_crypto_profile": "default-profile",
            },
        }
        model = IPsecTunnelCreateModel(**valid_data)
        assert model.name == "test-tunnel"
        assert model.folder == "Test Folder"
        assert model.auto_key.ipsec_crypto_profile == "default-profile"
        assert len(model.auto_key.ike_gateway) == 1
        assert model.auto_key.ike_gateway[0].name == "gw1"

        # Test with all optional fields
        full_data = {
            "name": "full-tunnel",
            "folder": "Test Folder",
            "auto_key": {
                "ike_gateway": [{"name": "gw1"}, {"name": "gw2"}],
                "ipsec_crypto_profile": "profile1",
                "proxy_id": [
                    {
                        "name": "proxy1",
                        "local": "10.0.0.0/24",
                        "remote": "192.168.0.0/24",
                        "protocol": {"tcp": {"local_port": 80, "remote_port": 443}},
                    }
                ],
                "proxy_id_v6": [
                    {
                        "name": "proxy_v6_1",
                        "local": "fd00::/64",
                        "remote": "fd01::/64",
                    }
                ],
            },
            "anti_replay": True,
            "copy_tos": True,
            "enable_gre_encapsulation": True,
            "tunnel_monitor": {
                "enable": True,
                "destination_ip": "10.0.0.1",
                "proxy_id": "proxy1",
            },
        }
        model = IPsecTunnelCreateModel(**full_data)
        assert model.name == "full-tunnel"
        assert model.anti_replay is True
        assert model.copy_tos is True
        assert model.enable_gre_encapsulation is True
        assert model.tunnel_monitor.enable is True
        assert model.tunnel_monitor.destination_ip == "10.0.0.1"
        assert model.tunnel_monitor.proxy_id == "proxy1"
        assert len(model.auto_key.ike_gateway) == 2
        assert model.auto_key.proxy_id[0].name == "proxy1"
        assert model.auto_key.proxy_id[0].protocol.tcp.local_port == 80
        assert model.auto_key.proxy_id_v6[0].name == "proxy_v6_1"

        # Test invalid name (too long)
        invalid_name = valid_data.copy()
        invalid_name["name"] = "A" * 64  # Max length is 63
        with pytest.raises(ValidationError) as exc_info:
            IPsecTunnelCreateModel(**invalid_name)
        assert "should have at most 63 characters" in str(exc_info.value).lower()

    def test_ipsec_tunnel_create_model_container_validation(self):
        """Test validation of container fields in IPsecTunnelCreateModel."""
        base_data = {
            "name": "test-tunnel",
            "auto_key": {
                "ike_gateway": [{"name": "gw1"}],
                "ipsec_crypto_profile": "default-profile",
            },
        }

        # Test with folder container
        valid_data = {**base_data, "folder": "Test Folder"}
        model = IPsecTunnelCreateModel(**valid_data)
        assert model.folder == "Test Folder"
        assert model.snippet is None
        assert model.device is None

        # Test with snippet container
        valid_with_snippet = {**base_data, "snippet": "Test Snippet"}
        model = IPsecTunnelCreateModel(**valid_with_snippet)
        assert model.snippet == "Test Snippet"
        assert model.folder is None
        assert model.device is None

        # Test with device container
        valid_with_device = {**base_data, "device": "Test Device"}
        model = IPsecTunnelCreateModel(**valid_with_device)
        assert model.device == "Test Device"
        assert model.folder is None
        assert model.snippet is None

        # Test with no container
        with pytest.raises(ValueError) as exc_info:
            IPsecTunnelCreateModel(**base_data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

        # Test with multiple containers
        invalid_multiple = {**base_data, "folder": "Test Folder", "snippet": "Test Snippet"}
        with pytest.raises(ValueError) as exc_info:
            IPsecTunnelCreateModel(**invalid_multiple)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_ike_gateway_ref_model(self):
        """Test validation of IkeGatewayRef model."""
        # Test valid reference
        ref = IkeGatewayRef(name="gw1")
        assert ref.name == "gw1"

        # Test missing required name
        with pytest.raises(ValidationError):
            IkeGatewayRef()

    def test_port_pair_model(self):
        """Test validation of PortPair model."""
        # Test default values
        port_pair = PortPair()
        assert port_pair.local_port == 0
        assert port_pair.remote_port == 0

        # Test with values
        port_pair = PortPair(local_port=80, remote_port=443)
        assert port_pair.local_port == 80
        assert port_pair.remote_port == 443

        # Test invalid port (too high)
        with pytest.raises(ValidationError):
            PortPair(local_port=70000)

        # Test invalid port (negative)
        with pytest.raises(ValidationError):
            PortPair(local_port=-1)

    def test_proxy_id_protocol_model(self):
        """Test validation of ProxyIdProtocol model."""
        # Test with number
        proto = ProxyIdProtocol(number=6)
        assert proto.number == 6
        assert proto.tcp is None
        assert proto.udp is None

        # Test with tcp
        proto = ProxyIdProtocol(tcp=PortPair(local_port=80, remote_port=443))
        assert proto.number is None
        assert proto.tcp.local_port == 80
        assert proto.udp is None

        # Test with udp
        proto = ProxyIdProtocol(udp=PortPair(local_port=53, remote_port=53))
        assert proto.number is None
        assert proto.tcp is None
        assert proto.udp.local_port == 53

        # Test with no protocol (should be valid)
        proto = ProxyIdProtocol()
        assert proto.number is None
        assert proto.tcp is None
        assert proto.udp is None

        # Test invalid: multiple protocols set
        with pytest.raises(ValueError) as exc_info:
            ProxyIdProtocol(number=6, tcp=PortPair())
        assert "At most one of 'number', 'tcp', or 'udp' can be set" in str(exc_info.value)

        with pytest.raises(ValueError) as exc_info:
            ProxyIdProtocol(tcp=PortPair(), udp=PortPair())
        assert "At most one of 'number', 'tcp', or 'udp' can be set" in str(exc_info.value)

        # Test invalid number range
        with pytest.raises(ValidationError):
            ProxyIdProtocol(number=0)

        with pytest.raises(ValidationError):
            ProxyIdProtocol(number=255)

    def test_proxy_id_model(self):
        """Test validation of ProxyId model."""
        # Test minimal proxy ID
        proxy = ProxyId(name="proxy1")
        assert proxy.name == "proxy1"
        assert proxy.local is None
        assert proxy.remote is None
        assert proxy.protocol is None

        # Test full proxy ID
        proxy = ProxyId(
            name="proxy1",
            local="10.0.0.0/24",
            remote="192.168.0.0/24",
            protocol=ProxyIdProtocol(number=6),
        )
        assert proxy.name == "proxy1"
        assert proxy.local == "10.0.0.0/24"
        assert proxy.remote == "192.168.0.0/24"
        assert proxy.protocol.number == 6

    def test_auto_key_model(self):
        """Test validation of AutoKey model."""
        # Test valid auto key
        auto_key = AutoKey(
            ike_gateway=[IkeGatewayRef(name="gw1")],
            ipsec_crypto_profile="default-profile",
        )
        assert len(auto_key.ike_gateway) == 1
        assert auto_key.ipsec_crypto_profile == "default-profile"
        assert auto_key.proxy_id is None
        assert auto_key.proxy_id_v6 is None

        # Test with proxy IDs
        auto_key = AutoKey(
            ike_gateway=[IkeGatewayRef(name="gw1")],
            ipsec_crypto_profile="profile1",
            proxy_id=[ProxyId(name="proxy1")],
            proxy_id_v6=[ProxyId(name="proxy_v6_1")],
        )
        assert len(auto_key.proxy_id) == 1
        assert len(auto_key.proxy_id_v6) == 1

        # Test missing required fields
        with pytest.raises(ValidationError):
            AutoKey(ike_gateway=[IkeGatewayRef(name="gw1")])

        with pytest.raises(ValidationError):
            AutoKey(ipsec_crypto_profile="default-profile")

    def test_tunnel_monitor_model(self):
        """Test validation of TunnelMonitor model."""
        # Test valid tunnel monitor
        monitor = TunnelMonitor(destination_ip="10.0.0.1")
        assert monitor.enable is True  # Default
        assert monitor.destination_ip == "10.0.0.1"
        assert monitor.proxy_id is None

        # Test with all fields
        monitor = TunnelMonitor(
            enable=False,
            destination_ip="10.0.0.1",
            proxy_id="proxy1",
        )
        assert monitor.enable is False
        assert monitor.destination_ip == "10.0.0.1"
        assert monitor.proxy_id == "proxy1"

        # Test missing required destination_ip
        with pytest.raises(ValidationError):
            TunnelMonitor()

    def test_ipsec_tunnel_update_model(self):
        """Test validation of IPsecTunnelUpdateModel."""
        # Test valid update model
        valid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "updated-tunnel",
            "folder": "Test Folder",
            "auto_key": {
                "ike_gateway": [{"name": "gw1"}],
                "ipsec_crypto_profile": "updated-profile",
            },
        }
        model = IPsecTunnelUpdateModel(**valid_data)
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "updated-tunnel"
        assert model.folder == "Test Folder"
        assert model.auto_key.ipsec_crypto_profile == "updated-profile"

        # Test invalid UUID
        invalid_id = valid_data.copy()
        invalid_id["id"] = "not-a-uuid"
        with pytest.raises(ValidationError):
            IPsecTunnelUpdateModel(**invalid_id)

    def test_ipsec_tunnel_response_model(self):
        """Test validation of IPsecTunnelResponseModel."""
        # Test valid response model
        valid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "response-tunnel",
            "folder": "Test Folder",
            "auto_key": {
                "ike_gateway": [{"name": "gw1"}],
                "ipsec_crypto_profile": "default-profile",
            },
        }
        model = IPsecTunnelResponseModel(**valid_data)
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "response-tunnel"
        assert model.folder == "Test Folder"

        # Test missing required ID
        invalid_data = valid_data.copy()
        del invalid_data["id"]
        with pytest.raises(ValidationError):
            IPsecTunnelResponseModel(**invalid_data)


class TestExtraFieldsForbidden:
    """Tests for extra='forbid' validation on all IPsec Tunnel models."""

    def test_create_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on IPsecTunnelCreateModel."""
        data = {
            "name": "test-tunnel",
            "folder": "Test Folder",
            "auto_key": {
                "ike_gateway": [{"name": "gw1"}],
                "ipsec_crypto_profile": "default-profile",
            },
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            IPsecTunnelCreateModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_update_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on IPsecTunnelUpdateModel."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-tunnel",
            "folder": "Test Folder",
            "auto_key": {
                "ike_gateway": [{"name": "gw1"}],
                "ipsec_crypto_profile": "default-profile",
            },
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            IPsecTunnelUpdateModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_response_model_extra_fields_ignored(self):
        """Test that extra fields are silently ignored on IPsecTunnelResponseModel."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-tunnel",
            "folder": "Test Folder",
            "auto_key": {
                "ike_gateway": [{"name": "gw1"}],
                "ipsec_crypto_profile": "default-profile",
            },
            "unknown_field": "should_be_ignored",
        }
        model = IPsecTunnelResponseModel(**data)
        assert not hasattr(model, "unknown_field")

    def test_ike_gateway_ref_extra_fields_forbidden(self):
        """Test that extra fields are rejected on IkeGatewayRef."""
        data = {
            "name": "gw1",
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            IkeGatewayRef(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_port_pair_extra_fields_forbidden(self):
        """Test that extra fields are rejected on PortPair."""
        data = {
            "local_port": 80,
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            PortPair(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_proxy_id_protocol_extra_fields_forbidden(self):
        """Test that extra fields are rejected on ProxyIdProtocol."""
        data = {
            "number": 6,
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            ProxyIdProtocol(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_proxy_id_extra_fields_forbidden(self):
        """Test that extra fields are rejected on ProxyId."""
        data = {
            "name": "proxy1",
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            ProxyId(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_auto_key_extra_fields_forbidden(self):
        """Test that extra fields are rejected on AutoKey."""
        data = {
            "ike_gateway": [{"name": "gw1"}],
            "ipsec_crypto_profile": "default-profile",
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            AutoKey(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_tunnel_monitor_extra_fields_forbidden(self):
        """Test that extra fields are rejected on TunnelMonitor."""
        data = {
            "destination_ip": "10.0.0.1",
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            TunnelMonitor(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)
