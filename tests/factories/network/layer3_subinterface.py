"""Factory definitions for network Layer3 Subinterface objects."""

import uuid

import factory

from scm.models.network.layer3_subinterface import (
    Layer3SubinterfaceCreateModel,
    Layer3SubinterfaceResponseModel,
    Layer3SubinterfaceUpdateModel,
)


# SDK tests against SCM API
class Layer3SubinterfaceCreateApiFactory(factory.Factory):
    """Factory for creating Layer3SubinterfaceCreateModel instances."""

    class Meta:
        """Meta class that defines the model for Layer3SubinterfaceCreateApiFactory."""

        model = Layer3SubinterfaceCreateModel

    name = factory.Sequence(lambda n: f"ethernet1/1.{n + 100}")
    folder = "Shared"
    tag = None
    parent_interface = None
    comment = None
    mtu = None
    interface_management_profile = None
    ip = None
    dhcp_client = None
    arp = None
    ddns_config = None

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)


class Layer3SubinterfaceUpdateApiFactory(factory.Factory):
    """Factory for creating Layer3SubinterfaceUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for Layer3SubinterfaceUpdateApiFactory."""

        model = Layer3SubinterfaceUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"ethernet1/1.{n + 100}")
    tag = None
    parent_interface = None
    comment = None
    mtu = None
    interface_management_profile = None
    ip = None
    dhcp_client = None
    arp = None
    ddns_config = None


class Layer3SubinterfaceResponseFactory(factory.Factory):
    """Factory for creating Layer3SubinterfaceResponseModel instances."""

    class Meta:
        """Meta class that defines the model for Layer3SubinterfaceResponseFactory."""

        model = Layer3SubinterfaceResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"ethernet1/1.{n + 100}")
    folder = "Shared"
    tag = None
    parent_interface = None
    comment = None
    mtu = None
    interface_management_profile = None
    ip = None
    dhcp_client = None
    arp = None
    ddns_config = None

    @classmethod
    def from_request(cls, request_model: Layer3SubinterfaceCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class Layer3SubinterfaceCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for Layer3SubinterfaceCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"ethernet1/1.{n + 100}")
    folder = "Shared"

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="ethernet1/1.100",
            folder="Shared",
            tag=100,
            parent_interface="ethernet1/1",
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="ethernet1/1.100",
            folder="Shared",
            snippet="TestSnippet",
        )

    @classmethod
    def build_with_no_container(cls):
        """Return a data dict without any container."""
        return cls(
            name="ethernet1/1.100",
            folder=None,
            snippet=None,
            device=None,
        )


class Layer3SubinterfaceUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for Layer3SubinterfaceUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"ethernet1/1.{n + 100}")

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating a Layer3 Subinterface."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="ethernet1/1.200",
            tag=200,
        )
