"""Test models for Service Connections."""

from uuid import UUID

from pydantic import ValidationError
import pytest

from scm.models.deployment import (
    BgpPeerModel,
    BgpProtocolModel,
    NoExportCommunity,
    ProtocolModel,
    QosModel,
    ServiceConnectionCreateModel,
    ServiceConnectionResponseModel,
    ServiceConnectionUpdateModel,
)
from tests.factories.deployment import (
    BgpPeerModelFactory,
    BgpProtocolModelFactory,
    ProtocolModelFactory,
    ServiceConnectionCreateApiFactory,
    ServiceConnectionCreateModelFactory,
    ServiceConnectionQosModelFactory,
    ServiceConnectionResponseFactory,
    ServiceConnectionResponseModelFactory,
    ServiceConnectionUpdateModelFactory,
)


class TestServiceConnectionModels:
    """Test Service Connection Pydantic models."""

    def test_service_connection_base_model_validation(self):
        """Test validation of ServiceConnectionBaseModel through the Create model."""
        # Test valid model
        valid_data = ServiceConnectionCreateApiFactory.build()
        model = ServiceConnectionCreateModel(**valid_data)
        assert model.name == valid_data["name"]
        assert model.folder == "Service Connections"  # Default value
        assert model.ipsec_tunnel == valid_data["ipsec_tunnel"]
        assert model.region == valid_data["region"]
        assert model.onboarding_type == valid_data["onboarding_type"]
        assert model.backup_SC == valid_data["backup_SC"]
        assert model.subnets == valid_data["subnets"]
        assert model.source_nat == valid_data["source_nat"]

        # Test with whitespace in name
        valid_with_whitespace = ServiceConnectionCreateApiFactory.build(name="My Test Connection")
        model = ServiceConnectionCreateModel(**valid_with_whitespace)
        assert model.name == "My Test Connection"

        # Test with multiple words and special characters
        valid_with_special_chars = ServiceConnectionCreateApiFactory.build(name="AWS-Connection-1")
        model = ServiceConnectionCreateModel(**valid_with_special_chars)
        assert model.name == "AWS-Connection-1"

        # Test invalid name with invalid characters
        invalid_name = ServiceConnectionCreateApiFactory.build(name="Invalid@Connection!")
        with pytest.raises(ValidationError) as exc_info:
            ServiceConnectionCreateModel(**invalid_name)
        assert "String should match pattern" in str(exc_info.value)

        # Test invalid name (too long)
        invalid_name = ServiceConnectionCreateApiFactory.build(name="A" * 64)  # Max length is 63
        with pytest.raises(ValidationError) as exc_info:
            ServiceConnectionCreateModel(**invalid_name)
        assert "should have at most 63 characters" in str(exc_info.value).lower()

    def test_bgp_peer_model(self):
        """Test BgpPeerModel validation."""
        # Test with all fields
        valid_data = BgpPeerModelFactory.build()
        model = BgpPeerModel(**valid_data.__dict__)
        assert model.local_ip_address == valid_data.local_ip_address
        assert model.local_ipv6_address == valid_data.local_ipv6_address
        assert model.peer_ip_address == valid_data.peer_ip_address
        assert model.peer_ipv6_address == valid_data.peer_ipv6_address
        assert model.secret == valid_data.secret

        # Test with minimal fields
        minimal_data = BgpPeerModelFactory.build(
            local_ipv6_address=None,
            peer_ipv6_address=None,
            secret=None,
        )
        model = BgpPeerModel(**minimal_data.__dict__)
        assert model.local_ip_address == minimal_data.local_ip_address
        assert model.peer_ip_address == minimal_data.peer_ip_address
        assert model.local_ipv6_address is None
        assert model.peer_ipv6_address is None
        assert model.secret is None

    def test_bgp_protocol_model(self):
        """Test BgpProtocolModel validation."""
        # Test with all fields
        valid_data = BgpProtocolModelFactory.build()
        model = BgpProtocolModel(**valid_data.__dict__)
        assert model.do_not_export_routes == valid_data.do_not_export_routes
        assert model.enable == valid_data.enable
        assert model.fast_failover == valid_data.fast_failover
        assert model.local_ip_address == valid_data.local_ip_address
        assert model.originate_default_route == valid_data.originate_default_route
        assert model.peer_as == valid_data.peer_as
        assert model.peer_ip_address == valid_data.peer_ip_address
        assert model.secret == valid_data.secret
        assert model.summarize_mobile_user_routes == valid_data.summarize_mobile_user_routes

        # Test with minimal fields
        minimal_data = BgpProtocolModelFactory.build(
            do_not_export_routes=None,
            fast_failover=None,
            local_ip_address=None,
            originate_default_route=None,
            peer_ip_address=None,
            secret=None,
            summarize_mobile_user_routes=None,
        )
        model = BgpProtocolModel(**minimal_data.__dict__)
        assert model.enable == minimal_data.enable
        assert model.peer_as == minimal_data.peer_as
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
        valid_data = ProtocolModelFactory.build()
        model = ProtocolModel(**valid_data.__dict__)
        assert model.bgp is not None
        assert model.bgp.enable == valid_data.bgp.enable
        assert model.bgp.peer_as == valid_data.bgp.peer_as

        # Test without BGP protocol
        minimal_data = ProtocolModelFactory.build(bgp=None)
        model = ProtocolModel(**minimal_data.__dict__)
        assert model.bgp is None

    def test_qos_model(self):
        """Test QosModel validation."""
        # Test with all fields
        valid_data = ServiceConnectionQosModelFactory.build()
        model = QosModel(**valid_data.__dict__)
        assert model.enable == valid_data.enable
        assert model.qos_profile == valid_data.qos_profile

        # Test with minimal fields
        minimal_data = ServiceConnectionQosModelFactory.build(qos_profile=None)
        model = QosModel(**minimal_data.__dict__)
        assert model.enable == minimal_data.enable
        assert model.qos_profile is None

    def test_no_export_community_enum(self):
        """Test NoExportCommunity enum validation."""
        # Test valid values
        assert NoExportCommunity.DISABLED == "Disabled"
        assert NoExportCommunity.ENABLED_IN == "Enabled-In"
        assert NoExportCommunity.ENABLED_OUT == "Enabled-Out"
        assert NoExportCommunity.ENABLED_BOTH == "Enabled-Both"

        # Test valid assignment in model
        valid_data = ServiceConnectionCreateApiFactory.build(no_export_community="Enabled-Both")
        model = ServiceConnectionCreateModel(**valid_data)
        assert model.no_export_community == NoExportCommunity.ENABLED_BOTH

        # Test invalid value
        invalid_data = ServiceConnectionCreateApiFactory.build(no_export_community="Invalid-Value")
        with pytest.raises(ValidationError) as exc_info:
            ServiceConnectionCreateModel(**invalid_data)
        assert "Input should be 'Disabled'" in str(exc_info.value)

    def test_service_connection_create_model(self):
        """Test ServiceConnectionCreateModel validation."""
        # Test complete model
        valid_model = ServiceConnectionCreateModelFactory.build()
        assert valid_model.name is not None
        assert valid_model.ipsec_tunnel is not None
        assert valid_model.region is not None
        assert valid_model.bgp_peer is not None
        assert valid_model.protocol is not None
        assert valid_model.protocol.bgp is not None
        assert valid_model.protocol.bgp.enable is True
        assert valid_model.qos is not None
        # Fix: Don't assume enable will always be true, as it's using FuzzyChoice([True, False])
        assert valid_model.qos.enable in (True, False)

        # Convert to dict for API
        api_dict = valid_model.model_dump()
        assert isinstance(api_dict, dict)
        assert "name" in api_dict
        assert "ipsec_tunnel" in api_dict  # Field uses snake_case, not camelCase

        # Test minimal required fields
        minimal_data = ServiceConnectionCreateApiFactory.build(
            bgp_peer=None,
            protocol=None,
            qos=None,
            backup_SC=None,
            subnets=None,
            no_export_community=None,
            source_nat=None,
        )
        model = ServiceConnectionCreateModel(**minimal_data)
        assert model.name == minimal_data["name"]
        assert model.ipsec_tunnel == minimal_data["ipsec_tunnel"]
        assert model.region == minimal_data["region"]
        assert model.onboarding_type == minimal_data["onboarding_type"]
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
        valid_model = ServiceConnectionUpdateModelFactory.build()
        assert isinstance(valid_model.id, UUID)
        assert valid_model.name is not None
        assert valid_model.ipsec_tunnel is not None
        assert valid_model.region is not None

        # Test with complex objects
        complex_model = ServiceConnectionUpdateModelFactory.build(
            bgp_peer=BgpPeerModelFactory.build(),
            protocol=ProtocolModelFactory.build(),
        )
        assert isinstance(complex_model.id, UUID)
        assert complex_model.name is not None
        assert complex_model.bgp_peer is not None
        assert complex_model.bgp_peer.local_ip_address is not None
        assert complex_model.protocol is not None
        assert complex_model.protocol.bgp is not None
        assert complex_model.protocol.bgp.enable is True

        # Test with invalid UUID
        with pytest.raises(ValidationError):
            ServiceConnectionUpdateModel(
                id="not-a-uuid",
                name="updated-connection",
                ipsec_tunnel="updated-tunnel",
                region="us-west-2",
            )

        # Test missing required ID
        with pytest.raises(ValidationError) as exc_info:
            ServiceConnectionUpdateModel(
                name="updated-connection", ipsec_tunnel="updated-tunnel", region="us-west-2"
            )
        assert "Field required" in str(exc_info.value)
        assert "id" in str(exc_info.value)

    def test_service_connection_response_model(self):
        """Test ServiceConnectionResponseModel validation."""
        # Test valid response model
        valid_data = ServiceConnectionResponseFactory.build()
        model = ServiceConnectionResponseModel(**valid_data)
        assert model.id == UUID(valid_data["id"])
        assert model.name == valid_data["name"]
        assert model.ipsec_tunnel == valid_data["ipsec_tunnel"]
        assert model.region == valid_data["region"]
        assert model.onboarding_type == valid_data["onboarding_type"]
        assert model.subnets == valid_data["subnets"]

        # Test with nested objects
        complex_model = ServiceConnectionResponseModelFactory.build()
        assert isinstance(complex_model.id, UUID)
        assert complex_model.name is not None
        assert complex_model.bgp_peer is not None
        assert complex_model.protocol is not None
        assert complex_model.protocol.bgp is not None
        assert complex_model.protocol.bgp.enable is True
        assert complex_model.qos is not None
        assert complex_model.qos.enable in (True, False)

        # Test missing required ID
        invalid_data = ServiceConnectionResponseFactory.build()
        invalid_data.pop("id")
        with pytest.raises(ValidationError) as exc_info:
            ServiceConnectionResponseModel(**invalid_data)
        assert "Field required" in str(exc_info.value)
        assert "id" in str(exc_info.value)


class TestExtraFieldsForbidden:
    """Test that extra fields are rejected by all models."""

    def test_bgp_peer_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected in BgpPeerModel."""
        with pytest.raises(ValidationError) as exc_info:
            BgpPeerModel(
                local_ip_address="192.168.1.1",
                unknown_field="should fail",
            )
        assert "extra" in str(exc_info.value).lower()

    def test_bgp_protocol_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected in BgpProtocolModel."""
        with pytest.raises(ValidationError) as exc_info:
            BgpProtocolModel(
                enable=True,
                unknown_field="should fail",
            )
        assert "extra" in str(exc_info.value).lower()

    def test_protocol_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected in ProtocolModel."""
        with pytest.raises(ValidationError) as exc_info:
            ProtocolModel(
                bgp={"enable": True},
                unknown_field="should fail",
            )
        assert "extra" in str(exc_info.value).lower()

    def test_qos_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected in QosModel."""
        with pytest.raises(ValidationError) as exc_info:
            QosModel(
                enable=True,
                unknown_field="should fail",
            )
        assert "extra" in str(exc_info.value).lower()

    def test_service_connection_create_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected in ServiceConnectionCreateModel."""
        data = ServiceConnectionCreateApiFactory.build()
        data["unknown_field"] = "should fail"
        with pytest.raises(ValidationError) as exc_info:
            ServiceConnectionCreateModel(**data)
        assert "extra" in str(exc_info.value).lower()

    def test_service_connection_update_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected in ServiceConnectionUpdateModel."""
        valid_model = ServiceConnectionUpdateModelFactory.build()
        data = valid_model.model_dump()
        data["unknown_field"] = "should fail"
        with pytest.raises(ValidationError) as exc_info:
            ServiceConnectionUpdateModel(**data)
        assert "extra" in str(exc_info.value).lower()

    def test_service_connection_response_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected in ServiceConnectionResponseModel."""
        data = ServiceConnectionResponseFactory.build()
        data["unknown_field"] = "should fail"
        with pytest.raises(ValidationError) as exc_info:
            ServiceConnectionResponseModel(**data)
        assert "extra" in str(exc_info.value).lower()
