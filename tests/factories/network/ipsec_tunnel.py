"""Factory definitions for network IPsec Tunnel objects."""

import uuid

import factory

from scm.models.network.ipsec_tunnel import (
    IPsecTunnelCreateModel,
    IPsecTunnelResponseModel,
    IPsecTunnelUpdateModel,
)


# SDK tests against SCM API
class IPsecTunnelCreateApiFactory(factory.Factory):
    """Factory for creating IPsecTunnelCreateModel instances."""

    class Meta:
        """Meta class that defines the model for IPsecTunnelCreateApiFactory."""

        model = IPsecTunnelCreateModel

    name = factory.Sequence(lambda n: f"ipsec_tunnel_{n}")
    auto_key = {
        "ike_gateway": [{"name": "test-ike-gw"}],
        "ipsec_crypto_profile": "default",
    }
    anti_replay = None
    copy_tos = False
    enable_gre_encapsulation = False
    tunnel_monitor = None
    folder = "Shared"

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)


class IPsecTunnelUpdateApiFactory(factory.Factory):
    """Factory for creating IPsecTunnelUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for IPsecTunnelUpdateApiFactory."""

        model = IPsecTunnelUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"ipsec_tunnel_{n}")
    auto_key = {
        "ike_gateway": [{"name": "test-ike-gw"}],
        "ipsec_crypto_profile": "default",
    }
    anti_replay = None
    copy_tos = False
    enable_gre_encapsulation = False
    tunnel_monitor = None


class IPsecTunnelResponseFactory(factory.Factory):
    """Factory for creating IPsecTunnelResponseModel instances."""

    class Meta:
        """Meta class that defines the model for IPsecTunnelResponseFactory."""

        model = IPsecTunnelResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"ipsec_tunnel_{n}")
    auto_key = {
        "ike_gateway": [{"name": "test-ike-gw"}],
        "ipsec_crypto_profile": "default",
    }
    anti_replay = None
    copy_tos = False
    enable_gre_encapsulation = False
    tunnel_monitor = None
    folder = "Shared"

    @classmethod
    def from_request(cls, request_model: IPsecTunnelCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class IPsecTunnelCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for IPsecTunnelCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"ipsec_tunnel_{n}")
    folder = "Shared"
    auto_key = {
        "ike_gateway": [{"name": "test-ike-gw"}],
        "ipsec_crypto_profile": "default",
    }

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestIPsecTunnel",
            folder="Shared",
            auto_key={
                "ike_gateway": [{"name": "test-ike-gw"}],
                "ipsec_crypto_profile": "default",
            },
            anti_replay=True,
            copy_tos=False,
            enable_gre_encapsulation=False,
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="TestIPsecTunnel",
            folder="Shared",
            snippet="TestSnippet",
            auto_key={
                "ike_gateway": [{"name": "test-ike-gw"}],
                "ipsec_crypto_profile": "default",
            },
        )

    @classmethod
    def build_with_no_container(cls):
        """Return a data dict without any container."""
        return cls(
            name="TestIPsecTunnel",
            folder=None,
            snippet=None,
            device=None,
            auto_key={
                "ike_gateway": [{"name": "test-ike-gw"}],
                "ipsec_crypto_profile": "default",
            },
        )


class IPsecTunnelUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for IPsecTunnelUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"ipsec_tunnel_{n}")
    auto_key = {
        "ike_gateway": [{"name": "test-ike-gw"}],
        "ipsec_crypto_profile": "default",
    }

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating an IPsec tunnel."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedIPsecTunnel",
            auto_key={
                "ike_gateway": [{"name": "updated-ike-gw"}],
                "ipsec_crypto_profile": "updated-profile",
            },
        )
