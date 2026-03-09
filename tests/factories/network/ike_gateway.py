"""Factory definitions for network IKE Gateway objects."""

import uuid

import factory

from scm.models.network.ike_gateway import (
    IKEGatewayCreateModel,
    IKEGatewayResponseModel,
    IKEGatewayUpdateModel,
)


# SDK tests against SCM API
class IKEGatewayCreateApiFactory(factory.Factory):
    """Factory for creating IKEGatewayCreateModel instances."""

    class Meta:
        """Meta class that defines the model for IKEGatewayCreateApiFactory."""

        model = IKEGatewayCreateModel

    name = factory.Sequence(lambda n: f"ike_gateway_{n}")
    authentication = {"pre_shared_key": {"key": "test-secret-key"}}
    peer_id = None
    local_id = None
    protocol = {"version": "ikev2-preferred", "ikev2": {"ike_crypto_profile": "default"}}
    protocol_common = None
    peer_address = {"ip": "10.0.0.1"}
    folder = "Shared"

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)


class IKEGatewayUpdateApiFactory(factory.Factory):
    """Factory for creating IKEGatewayUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for IKEGatewayUpdateApiFactory."""

        model = IKEGatewayUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"ike_gateway_{n}")
    authentication = {"pre_shared_key": {"key": "test-secret-key"}}
    peer_id = None
    local_id = None
    protocol = {"version": "ikev2-preferred", "ikev2": {"ike_crypto_profile": "default"}}
    protocol_common = None
    peer_address = {"ip": "10.0.0.1"}


class IKEGatewayResponseFactory(factory.Factory):
    """Factory for creating IKEGatewayResponseModel instances."""

    class Meta:
        """Meta class that defines the model for IKEGatewayResponseFactory."""

        model = IKEGatewayResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"ike_gateway_{n}")
    authentication = {"pre_shared_key": {"key": "test-secret-key"}}
    peer_id = None
    local_id = None
    protocol = {"version": "ikev2-preferred", "ikev2": {"ike_crypto_profile": "default"}}
    protocol_common = None
    peer_address = {"ip": "10.0.0.1"}
    folder = "Shared"

    @classmethod
    def from_request(cls, request_model: IKEGatewayCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class IKEGatewayCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for IKEGatewayCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"ike_gateway_{n}")
    folder = "Shared"
    authentication = {"pre_shared_key": {"key": "test-secret-key"}}
    protocol = {"version": "ikev2-preferred", "ikev2": {"ike_crypto_profile": "default"}}
    peer_address = {"ip": "10.0.0.1"}

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestIKEGateway",
            folder="Shared",
            authentication={"pre_shared_key": {"key": "my-secret-key"}},
            protocol={"version": "ikev2-preferred", "ikev2": {"ike_crypto_profile": "default"}},
            peer_address={"ip": "10.0.0.1"},
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="TestIKEGateway",
            folder="Shared",
            snippet="TestSnippet",
            authentication={"pre_shared_key": {"key": "test-secret-key"}},
            protocol={"version": "ikev2-preferred", "ikev2": {"ike_crypto_profile": "default"}},
            peer_address={"ip": "10.0.0.1"},
        )

    @classmethod
    def build_with_no_container(cls):
        """Return a data dict without any container."""
        return cls(
            name="TestIKEGateway",
            folder=None,
            snippet=None,
            device=None,
            authentication={"pre_shared_key": {"key": "test-secret-key"}},
            protocol={"version": "ikev2-preferred", "ikev2": {"ike_crypto_profile": "default"}},
            peer_address={"ip": "10.0.0.1"},
        )


class IKEGatewayUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for IKEGatewayUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"ike_gateway_{n}")
    authentication = {"pre_shared_key": {"key": "test-secret-key"}}
    protocol = {"version": "ikev2-preferred", "ikev2": {"ike_crypto_profile": "default"}}
    peer_address = {"ip": "10.0.0.1"}

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating an IKE gateway."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedIKEGateway",
            authentication={"pre_shared_key": {"key": "updated-secret-key"}},
            protocol={"version": "ikev2-preferred", "ikev2": {"ike_crypto_profile": "default"}},
            peer_address={"ip": "10.0.0.2"},
        )
