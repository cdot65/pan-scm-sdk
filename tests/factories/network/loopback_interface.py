"""Factory definitions for network Loopback Interface objects."""

import uuid

import factory

from scm.models.network.loopback_interface import (
    LoopbackInterfaceCreateModel,
    LoopbackInterfaceResponseModel,
    LoopbackInterfaceUpdateModel,
)


# SDK tests against SCM API
class LoopbackInterfaceCreateApiFactory(factory.Factory):
    """Factory for creating LoopbackInterfaceCreateModel instances."""

    class Meta:
        """Meta class that defines the model for LoopbackInterfaceCreateApiFactory."""

        model = LoopbackInterfaceCreateModel

    name = factory.Sequence(lambda n: f"$loopback_{n}")
    folder = "Shared"
    default_value = None
    comment = None
    mtu = None
    interface_management_profile = None
    ip = None
    ipv6 = None

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)


class LoopbackInterfaceUpdateApiFactory(factory.Factory):
    """Factory for creating LoopbackInterfaceUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for LoopbackInterfaceUpdateApiFactory."""

        model = LoopbackInterfaceUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"$loopback_{n}")
    default_value = None
    comment = None
    mtu = None
    interface_management_profile = None
    ip = None
    ipv6 = None


class LoopbackInterfaceResponseFactory(factory.Factory):
    """Factory for creating LoopbackInterfaceResponseModel instances."""

    class Meta:
        """Meta class that defines the model for LoopbackInterfaceResponseFactory."""

        model = LoopbackInterfaceResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"$loopback_{n}")
    folder = "Shared"
    default_value = None
    comment = None
    mtu = None
    interface_management_profile = None
    ip = None
    ipv6 = None

    @classmethod
    def from_request(cls, request_model: LoopbackInterfaceCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class LoopbackInterfaceCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for LoopbackInterfaceCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"$loopback_{n}")
    folder = "Shared"

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="$loopback_test",
            folder="Shared",
            default_value="loopback.1",
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="$loopback_test",
            folder="Shared",
            snippet="TestSnippet",
        )

    @classmethod
    def build_with_no_container(cls):
        """Return a data dict without any container."""
        return cls(
            name="$loopback_test",
            folder=None,
            snippet=None,
            device=None,
        )


class LoopbackInterfaceUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for LoopbackInterfaceUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"$loopback_{n}")

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating a Loopback Interface."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="$loopback_updated",
        )
