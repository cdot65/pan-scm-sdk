"""Factory definitions for network Ethernet Interface objects."""

import uuid

import factory

from scm.models.network.ethernet_interface import (
    EthernetInterfaceCreateModel,
    EthernetInterfaceResponseModel,
    EthernetInterfaceUpdateModel,
)


# SDK tests against SCM API
class EthernetInterfaceCreateApiFactory(factory.Factory):
    """Factory for creating EthernetInterfaceCreateModel instances."""

    class Meta:
        """Meta class that defines the model for EthernetInterfaceCreateApiFactory."""

        model = EthernetInterfaceCreateModel

    name = factory.Sequence(lambda n: f"$ethernet_if_{n}")
    default_value = None
    comment = None
    link_speed = "auto"
    link_duplex = "auto"
    link_state = "auto"
    poe = None
    layer2 = None
    layer3 = None
    tap = None
    folder = "Shared"
    slot = None

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)


class EthernetInterfaceUpdateApiFactory(factory.Factory):
    """Factory for creating EthernetInterfaceUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for EthernetInterfaceUpdateApiFactory."""

        model = EthernetInterfaceUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"$ethernet_if_{n}")
    default_value = None
    comment = None
    link_speed = "auto"
    link_duplex = "auto"
    link_state = "auto"
    poe = None
    layer2 = None
    layer3 = None
    tap = None
    slot = None


class EthernetInterfaceResponseFactory(factory.Factory):
    """Factory for creating EthernetInterfaceResponseModel instances."""

    class Meta:
        """Meta class that defines the model for EthernetInterfaceResponseFactory."""

        model = EthernetInterfaceResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"$ethernet_if_{n}")
    default_value = None
    comment = None
    link_speed = "auto"
    link_duplex = "auto"
    link_state = "auto"
    poe = None
    layer2 = None
    layer3 = None
    tap = None
    folder = "Shared"
    slot = None

    @classmethod
    def from_request(cls, request_model: EthernetInterfaceCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class EthernetInterfaceCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for EthernetInterfaceCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"$ethernet_if_{n}")
    folder = "Shared"

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="$ethernet_if_test",
            folder="Shared",
            default_value="ethernet1/1",
            comment="Test ethernet interface",
            link_speed="auto",
            link_duplex="auto",
            link_state="auto",
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="$ethernet_if_test",
            folder="Shared",
            snippet="TestSnippet",
        )

    @classmethod
    def build_with_no_container(cls):
        """Return a data dict without any container."""
        return cls(
            name="$ethernet_if_test",
            folder=None,
            snippet=None,
            device=None,
        )


class EthernetInterfaceUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for EthernetInterfaceUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"$ethernet_if_{n}")

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating an ethernet interface."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="$updated_ethernet_if",
            comment="Updated ethernet interface",
        )
