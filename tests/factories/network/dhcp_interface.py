"""Factory definitions for network DHCP Interface objects."""

import uuid

import factory

from scm.models.network.dhcp_interface import (
    DhcpInterfaceCreateModel,
    DhcpInterfaceResponseModel,
    DhcpInterfaceUpdateModel,
)


# SDK tests against SCM API
class DhcpInterfaceCreateApiFactory(factory.Factory):
    """Factory for creating DhcpInterfaceCreateModel instances."""

    class Meta:
        """Meta class that defines the model for DhcpInterfaceCreateApiFactory."""

        model = DhcpInterfaceCreateModel

    name = factory.Sequence(lambda n: f"dhcp_interface_{n}")
    folder = "Shared"
    server = None
    relay = None

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)


class DhcpInterfaceUpdateApiFactory(factory.Factory):
    """Factory for creating DhcpInterfaceUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for DhcpInterfaceUpdateApiFactory."""

        model = DhcpInterfaceUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"dhcp_interface_{n}")
    server = None
    relay = None


class DhcpInterfaceResponseFactory(factory.Factory):
    """Factory for creating DhcpInterfaceResponseModel instances."""

    class Meta:
        """Meta class that defines the model for DhcpInterfaceResponseFactory."""

        model = DhcpInterfaceResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"dhcp_interface_{n}")
    folder = "Shared"
    server = None
    relay = None

    @classmethod
    def from_request(cls, request_model: DhcpInterfaceCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class DhcpInterfaceCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for DhcpInterfaceCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"dhcp_interface_{n}")
    folder = "Shared"

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestDhcpInterface",
            folder="Shared",
            server={
                "mode": "enabled",
                "ip_pool": ["10.0.0.10-10.0.0.100"],
            },
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="TestDhcpInterface",
            folder="Shared",
            snippet="TestSnippet",
        )

    @classmethod
    def build_with_no_container(cls):
        """Return a data dict without any container."""
        return cls(
            name="TestDhcpInterface",
            folder=None,
            snippet=None,
            device=None,
        )


class DhcpInterfaceUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for DhcpInterfaceUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"dhcp_interface_{n}")

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating a DHCP interface."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedDhcpInterface",
        )
