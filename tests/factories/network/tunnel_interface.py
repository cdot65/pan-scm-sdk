"""Factory definitions for network Tunnel Interface objects."""

import uuid

import factory

from scm.models.network.tunnel_interface import (
    TunnelInterfaceCreateModel,
    TunnelInterfaceResponseModel,
    TunnelInterfaceUpdateModel,
)


# SDK tests against SCM API
class TunnelInterfaceCreateApiFactory(factory.Factory):
    """Factory for creating TunnelInterfaceCreateModel instances."""

    class Meta:
        """Meta class that defines the model for TunnelInterfaceCreateApiFactory."""

        model = TunnelInterfaceCreateModel

    name = factory.Sequence(lambda n: f"tunnel_interface_{n}")
    folder = "Shared"
    default_value = None
    comment = None
    mtu = None
    interface_management_profile = None
    ip = None

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)


class TunnelInterfaceUpdateApiFactory(factory.Factory):
    """Factory for creating TunnelInterfaceUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for TunnelInterfaceUpdateApiFactory."""

        model = TunnelInterfaceUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"tunnel_interface_{n}")
    default_value = None
    comment = None
    mtu = None
    interface_management_profile = None
    ip = None


class TunnelInterfaceResponseFactory(factory.Factory):
    """Factory for creating TunnelInterfaceResponseModel instances."""

    class Meta:
        """Meta class that defines the model for TunnelInterfaceResponseFactory."""

        model = TunnelInterfaceResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"tunnel_interface_{n}")
    folder = "Shared"
    default_value = None
    comment = None
    mtu = None
    interface_management_profile = None
    ip = None

    @classmethod
    def from_request(cls, request_model: TunnelInterfaceCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class TunnelInterfaceCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for TunnelInterfaceCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"tunnel_interface_{n}")
    folder = "Shared"

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestTunnelInterface",
            folder="Shared",
            comment="Test tunnel interface",
            mtu=1500,
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="TestTunnelInterface",
            folder="Shared",
            snippet="TestSnippet",
        )

    @classmethod
    def build_with_no_container(cls):
        """Return a data dict without any container."""
        return cls(
            name="TestTunnelInterface",
            folder=None,
            snippet=None,
            device=None,
        )


class TunnelInterfaceUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for TunnelInterfaceUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"tunnel_interface_{n}")

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating a tunnel interface."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedTunnelInterface",
            comment="Updated tunnel interface",
        )
