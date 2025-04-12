"""Tests for the IKE Gateway models."""

from uuid import UUID

import pytest
from pydantic import ValidationError

from scm.models.network import (IKEGatewayCreateModel, IKEGatewayResponseModel,
                                IKEGatewayUpdateModel, LocalIdType, PeerIdType,
                                ProtocolVersion)

# Test data
VALID_IKE_GATEWAY = {
    "name": "test-ike-gateway",
    "folder": "test-folder",
    "authentication": {"pre_shared_key": {"key": "secret-key"}},
    "peer_id": {"type": "ipaddr", "id": "10.0.0.1"},
    "local_id": {"type": "ipaddr", "id": "192.168.1.1"},
    "protocol": {
        "version": "ikev2",
        "ikev2": {"ike_crypto_profile": "default", "dpd": {"enable": True}},
    },
    "protocol_common": {"nat_traversal": {"enable": True}, "passive_mode": False},
    "peer_address": {"ip": "10.0.0.1"},
}


def test_create_model_valid():
    """Test creating a valid IKEGatewayCreateModel."""
    model = IKEGatewayCreateModel(**VALID_IKE_GATEWAY)
    assert model.name == "test-ike-gateway"
    assert model.folder == "test-folder"
    assert model.authentication.pre_shared_key.key == "secret-key"
    assert model.peer_id.type == PeerIdType.IPADDR
    assert model.peer_id.id == "10.0.0.1"
    assert model.local_id.type == LocalIdType.IPADDR
    assert model.local_id.id == "192.168.1.1"
    assert model.protocol.version == ProtocolVersion.IKEV2
    assert model.protocol.ikev2.ike_crypto_profile == "default"
    assert model.protocol.ikev2.dpd.enable is True
    assert model.protocol_common.nat_traversal.enable is True
    assert model.protocol_common.passive_mode is False
    assert model.peer_address.ip == "10.0.0.1"


def test_create_model_missing_container():
    """Test that the model validates exactly one container field."""
    data = VALID_IKE_GATEWAY.copy()
    # Remove folder, without adding snippet or device
    del data["folder"]

    with pytest.raises(ValidationError) as exc_info:
        IKEGatewayCreateModel(**data)

    assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(exc_info.value)


def test_create_model_multiple_containers():
    """Test that the model rejects multiple container fields."""
    data = VALID_IKE_GATEWAY.copy()
    # Add snippet when folder is already present
    data["snippet"] = "test-snippet"

    with pytest.raises(ValidationError) as exc_info:
        IKEGatewayCreateModel(**data)

    assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(exc_info.value)


def test_authentication_validation():
    """Test authentication method validation."""
    data = VALID_IKE_GATEWAY.copy()
    data["authentication"] = {}

    with pytest.raises(ValidationError) as exc_info:
        IKEGatewayCreateModel(**data)

    assert "At least one authentication method must be provided" in str(exc_info.value)

    # Test multiple authentication methods
    data["authentication"] = {
        "pre_shared_key": {"key": "secret-key"},
        "certificate": {"certificate_profile": "default"},
    }

    with pytest.raises(ValidationError) as exc_info:
        IKEGatewayCreateModel(**data)

    assert "Only one authentication method can be configured" in str(exc_info.value)


def test_peer_address_validation():
    """Test peer address validation."""
    data = VALID_IKE_GATEWAY.copy()

    # Test multiple peer address types
    data["peer_address"] = {"ip": "10.0.0.1", "fqdn": "example.com"}

    with pytest.raises(ValidationError) as exc_info:
        IKEGatewayCreateModel(**data)

    assert "Exactly one peer address type must be configured" in str(exc_info.value)

    # Test missing peer address
    data["peer_address"] = {}

    with pytest.raises(ValidationError) as exc_info:
        IKEGatewayCreateModel(**data)

    assert "Exactly one peer address type must be configured" in str(exc_info.value)


def test_protocol_validation():
    """Test protocol validation based on version."""
    data = VALID_IKE_GATEWAY.copy()

    # Test IKEv1 without ikev1 config
    data["protocol"] = {"version": "ikev1"}

    with pytest.raises(ValidationError) as exc_info:
        IKEGatewayCreateModel(**data)

    assert "IKEv1 configuration is required when version is set to ikev1" in str(exc_info.value)

    # Test IKEv2 without ikev2 config
    data["protocol"] = {"version": "ikev2"}

    with pytest.raises(ValidationError) as exc_info:
        IKEGatewayCreateModel(**data)

    assert "IKEv2 configuration is required when version is set to ikev2" in str(exc_info.value)

    # Test ikev2-preferred without any config
    data["protocol"] = {"version": "ikev2-preferred"}

    with pytest.raises(ValidationError) as exc_info:
        IKEGatewayCreateModel(**data)

    assert "Either IKEv1 or IKEv2 configuration must be provided" in str(exc_info.value)


def test_update_model():
    """Test the update model with a valid ID."""
    data = VALID_IKE_GATEWAY.copy()
    data["id"] = "123e4567-e89b-12d3-a456-426655440000"

    model = IKEGatewayUpdateModel(**data)
    assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
    assert model.name == "test-ike-gateway"


def test_response_model():
    """Test the response model with a valid ID."""
    data = VALID_IKE_GATEWAY.copy()
    data["id"] = "123e4567-e89b-12d3-a456-426655440000"

    model = IKEGatewayResponseModel(**data)
    assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
    assert model.name == "test-ike-gateway"


def test_model_serialization():
    """Test model serialization to dict."""
    data = VALID_IKE_GATEWAY.copy()
    data["id"] = "123e4567-e89b-12d3-a456-426655440000"

    model = IKEGatewayResponseModel(**data)
    serialized = model.model_dump(exclude_unset=True)

    assert serialized["id"] == UUID("123e4567-e89b-12d3-a456-426655440000")
    assert serialized["name"] == "test-ike-gateway"
    assert serialized["authentication"]["pre_shared_key"]["key"] == "secret-key"
    assert serialized["peer_id"]["type"] == "ipaddr"
    assert serialized["peer_address"]["ip"] == "10.0.0.1"
