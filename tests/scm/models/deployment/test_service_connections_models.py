"""Test models for Service Connections."""
from uuid import UUID

import pytest
from pydantic import ValidationError

from scm.models.deployment import (
    ServiceConnectionCreateModel,
    ServiceConnectionUpdateModel,
    ServiceConnectionResponseModel,
    OnboardingType,
    NoExportCommunity,
    BgpPeerModel,
    BgpProtocolModel,
    ProtocolModel,
    QosModel,
)


class TestServiceConnectionModels:
    """Test Service Connection Pydantic models."""

    def test_service_connection_base_model_validation(self):
        """Test validation of ServiceConnectionBaseModel through the Create model."""
        # Test valid model
        valid_data = {
            "name": "test-connection",
            "ipsec_tunnel": "test-tunnel",
            "region": "us-east-1",
            "onboarding_type": "classic",
            "backup_SC": "backup-connection",
            "subnets": ["10.0.0.0/24", "192.168.1.0/24"],
            "source_nat": True,
        }
        model = ServiceConnectionCreateModel(**valid_data)
        assert model.name == "test-connection"
        assert model.folder == "Service Connections"  # Default value
        assert model.ipsec_tunnel == "test-tunnel"
        assert model.region == "us-east-1"
        assert model.onboarding_type == OnboardingType.CLASSIC
        assert model.backup_SC == "backup-connection"
        assert model.subnets == ["10.0.0.0/24", "192.168.1.0/24"]
        assert model.source_nat is True

        # Test with whitespace in name
        valid_with_whitespace = valid_data.copy()
        valid_with_whitespace["name"] = "My Test Connection"
        model = ServiceConnectionCreateModel(**valid_with_whitespace)
        assert model.name == "My Test Connection"

        # Test with multiple words and special characters
        valid_with_special_chars = valid_data.copy()
        valid_with_special_chars["name"] = "AWS-Connection-1"
        model = ServiceConnectionCreateModel(**valid_with_special_chars)
        assert model.name == "AWS-Connection-1"

        # Test invalid name with invalid characters
        invalid_name = valid_data.copy()
        invalid_name["name"] = "Invalid@Connection!"
        with pytest.raises(ValidationError) as exc_info:
            ServiceConnectionCreateModel(**invalid_name)
        assert "String should match pattern" in str(exc_info.value)

        # Test invalid name (too long)
        invalid_name = valid_data.copy()
        invalid_name["name"] = "A" * 64  # Max length is 63
        with pytest.raises(ValidationError) as exc_info:
            ServiceConnectionCreateModel(**invalid_name)
        assert "should have at most 63 characters" in str(exc_info.value).lower()

    def test_bgp_peer_model(self):
        """Test BgpPeerModel validation."""
        # Test with all fields
        valid_data = {
            "local_ip_address": "192.168.1.1",
            "local_ipv6_address": "2001:db8::1",
            "peer_ip_address": "192.168.1.2",
            "peer_ipv6_address": "2001:db8::2",
            "secret": "secretpassword",
        }
        model = BgpPeerModel(**valid_data)
        assert model.local_ip_address == "192.168.1.1"
        assert model.local_ipv6_address == "2001:db8::1"
        assert model.peer_ip_address == "192.168.1.2"
        assert model.peer_ipv6_address == "2001:db8::2"
        assert model.secret == "secretpassword"

        # Test with minimal fields
        minimal_data = {
            "local_ip_address": "192.168.1.1",
            "peer_ip_address": "192.168.1.2",
        }
        model = BgpPeerModel(**minimal_data)
        assert model.local_ip_address == "192.168.1.1"
        assert model.peer_ip_address == "192.168.1.2"
        assert model.local_ipv6_address is None
        assert model.peer_ipv6_address is None
        assert model.secret is None

    def test_bgp_protocol_model(self):
        """Test BgpProtocolModel validation."""
        # Test with all fields
        valid_data = {
            "do_not_export_routes": True,
            "enable": True,
            "fast_failover": True,
            "local_ip_address": "192.168.1.1",
            "originate_default_route": True,
            "peer_as": "65000",
            "peer_ip_address": "192.168.1.2",
            "secret": "secretpassword",
            "summarize_mobile_user_routes": True,
        }
        model = BgpProtocolModel(**valid_data)
        assert model.do_not_export_routes is True
        assert model.enable is True
        assert model.fast_failover is True
        assert model.local_ip_address == "192.168.1.1"
        assert model.originate_default_route is True
        assert model.peer_as == "65000"
        assert model.peer_ip_address == "192.168.1.2"
        assert model.secret == "secretpassword"
        assert model.summarize_mobile_user_routes is True

        # Test with minimal fields
        minimal_data = {
            "enable": True,
            "peer_as": "65000",
        }
        model = BgpProtocolModel(**minimal_data)
        assert model.enable is True
        assert model.peer_as == "65000"
        assert model.do_not_export_routes is None
        assert model.fast_failover is None
        assert model.local_ip_address is None
        assert model.originate_default_route is None
        assert model.peer_ip_address is None
        assert model.secret is None
        assert model.summarize_mobile_user_routes is None

    def test_protocol_model(self):
        """Test ProtocolModel validation."""
        # Test with BGP protocol
        valid_data = {
            "bgp": {
                "enable": True,
                "peer_as": "65000",
                "peer_ip_address": "192.168.1.2",
                "local_ip_address": "192.168.1.1",
            }
        }
        model = ProtocolModel(**valid_data)
        assert model.bgp is not None
        assert model.bgp.enable is True
        assert model.bgp.peer_as == "65000"
        assert model.bgp.peer_ip_address == "192.168.1.2"
        assert model.bgp.local_ip_address == "192.168.1.1"

        # Test without BGP protocol
        minimal_data = {}
        model = ProtocolModel(**minimal_data)
        assert model.bgp is None

    def test_qos_model(self):
        """Test QosModel validation."""
        # Test with all fields
        valid_data = {
            "enable": True,
            "qos_profile": "high-priority",
        }
        model = QosModel(**valid_data)
        assert model.enable is True
        assert model.qos_profile == "high-priority"

        # Test with minimal fields
        minimal_data = {
            "enable": True,
        }
        model = QosModel(**minimal_data)
        assert model.enable is True
        assert model.qos_profile is None

    def test_no_export_community_enum(self):
        """Test NoExportCommunity enum validation."""
        # Test valid values
        assert NoExportCommunity.DISABLED == "Disabled"
        assert NoExportCommunity.ENABLED_IN == "Enabled-In"
        assert NoExportCommunity.ENABLED_OUT == "Enabled-Out"
        assert NoExportCommunity.ENABLED_BOTH == "Enabled-Both"

        # Test valid assignment in model
        valid_data = {
            "name": "test-connection",
            "ipsec_tunnel": "test-tunnel",
            "region": "us-east-1",
            "no_export_community": "Enabled-Both",
        }
        model = ServiceConnectionCreateModel(**valid_data)
        assert model.no_export_community == NoExportCommunity.ENABLED_BOTH

        # Test invalid value
        invalid_data = {
            "name": "test-connection",
            "ipsec_tunnel": "test-tunnel",
            "region": "us-east-1",
            "no_export_community": "Invalid-Value",
        }
        with pytest.raises(ValidationError) as exc_info:
            ServiceConnectionCreateModel(**invalid_data)
        assert "Input should be 'Disabled'" in str(exc_info.value)

    def test_service_connection_create_model(self):
        """Test ServiceConnectionCreateModel validation."""
        # Test complete model
        valid_data = {
            "name": "test-create-connection",
            "ipsec_tunnel": "test-tunnel",
            "region": "us-east-1",
            "bgp_peer": {
                "local_ip_address": "192.168.1.1",
                "peer_ip_address": "192.168.1.2",
            },
            "protocol": {
                "bgp": {
                    "enable": True,
                    "peer_as": "65000",
                }
            },
            "qos": {
                "enable": True,
                "qos_profile": "high-priority",
            },
            "source_nat": True,
        }
        model = ServiceConnectionCreateModel(**valid_data)
        assert model.name == "test-create-connection"
        assert model.ipsec_tunnel == "test-tunnel"
        assert model.region == "us-east-1"
        assert model.bgp_peer is not None
        assert model.bgp_peer.local_ip_address == "192.168.1.1"
        assert model.protocol is not None
        assert model.protocol.bgp is not None
        assert model.protocol.bgp.enable is True
        assert model.qos is not None
        assert model.qos.enable is True
        assert model.qos.qos_profile == "high-priority"
        assert model.source_nat is True

        # Test minimal required fields
        minimal_data = {
            "name": "test-minimal-connection",
            "ipsec_tunnel": "test-tunnel",
            "region": "us-east-1",
        }
        model = ServiceConnectionCreateModel(**minimal_data)
        assert model.name == "test-minimal-connection"
        assert model.ipsec_tunnel == "test-tunnel"
        assert model.region == "us-east-1"
        assert model.onboarding_type == OnboardingType.CLASSIC  # Default value
        assert model.folder == "Service Connections"  # Default value

        # Test missing required field (ipsec_tunnel)
        invalid_data = {
            "name": "test-connection",
            "region": "us-east-1",
        }
        with pytest.raises(ValidationError) as exc_info:
            ServiceConnectionCreateModel(**invalid_data)
        assert "Field required" in str(exc_info.value)
        assert "ipsec_tunnel" in str(exc_info.value)

    def test_service_connection_update_model(self):
        """Test ServiceConnectionUpdateModel validation."""
        # Test valid update model
        valid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "updated-connection",
            "ipsec_tunnel": "updated-tunnel",
            "region": "us-west-2",
        }
        model = ServiceConnectionUpdateModel(**valid_data)
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "updated-connection"
        assert model.ipsec_tunnel == "updated-tunnel"
        assert model.region == "us-west-2"

        # Test with complex objects
        complex_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "complex-connection",
            "ipsec_tunnel": "test-tunnel",
            "region": "us-east-1",
            "bgp_peer": {
                "local_ip_address": "192.168.1.1",
                "peer_ip_address": "192.168.1.2",
            },
            "protocol": {
                "bgp": {
                    "enable": True,
                    "peer_as": "65000",
                }
            },
        }
        model = ServiceConnectionUpdateModel(**complex_data)
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "complex-connection"
        assert model.bgp_peer is not None
        assert model.bgp_peer.local_ip_address == "192.168.1.1"
        assert model.protocol is not None
        assert model.protocol.bgp is not None
        assert model.protocol.bgp.enable is True

        # Test with invalid UUID
        invalid_uuid = valid_data.copy()
        invalid_uuid["id"] = "not-a-uuid"
        with pytest.raises(ValidationError):
            ServiceConnectionUpdateModel(**invalid_uuid)

        # Test missing required ID
        missing_id = valid_data.copy()
        missing_id.pop("id")
        with pytest.raises(ValidationError) as exc_info:
            ServiceConnectionUpdateModel(**missing_id)
        assert "Field required" in str(exc_info.value)
        assert "id" in str(exc_info.value)

    def test_service_connection_response_model(self):
        """Test ServiceConnectionResponseModel validation."""
        # Test valid response model
        valid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "response-connection",
            "ipsec_tunnel": "test-tunnel",
            "region": "us-east-1",
            "onboarding_type": "classic",
            "subnets": ["10.0.0.0/24", "192.168.1.0/24"],
        }
        model = ServiceConnectionResponseModel(**valid_data)
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "response-connection"
        assert model.ipsec_tunnel == "test-tunnel"
        assert model.region == "us-east-1"
        assert model.onboarding_type == OnboardingType.CLASSIC
        assert model.subnets == ["10.0.0.0/24", "192.168.1.0/24"]

        # Test with nested objects
        complex_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "complex-response",
            "ipsec_tunnel": "test-tunnel",
            "region": "us-east-1",
            "bgp_peer": {
                "local_ip_address": "192.168.1.1",
                "peer_ip_address": "192.168.1.2",
            },
            "protocol": {
                "bgp": {
                    "enable": True,
                    "peer_as": "65000",
                }
            },
            "qos": {
                "enable": True,
                "qos_profile": "high-priority",
            },
        }
        model = ServiceConnectionResponseModel(**complex_data)
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "complex-response"
        assert model.bgp_peer is not None
        assert model.bgp_peer.local_ip_address == "192.168.1.1"
        assert model.protocol is not None
        assert model.protocol.bgp is not None
        assert model.protocol.bgp.enable is True
        assert model.qos is not None
        assert model.qos.enable is True
        assert model.qos.qos_profile == "high-priority"

        # Test missing required ID
        missing_id = valid_data.copy()
        missing_id.pop("id")
        with pytest.raises(ValidationError) as exc_info:
            ServiceConnectionResponseModel(**missing_id)
        assert "Field required" in str(exc_info.value)
        assert "id" in str(exc_info.value)