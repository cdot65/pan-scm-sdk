"""Factory definitions for network Layer2 Subinterface objects."""

import uuid

import factory

from scm.models.network.layer2_subinterface import (
    Layer2SubinterfaceCreateModel,
    Layer2SubinterfaceResponseModel,
    Layer2SubinterfaceUpdateModel,
)


# SDK tests against SCM API
class Layer2SubinterfaceCreateApiFactory(factory.Factory):
    """Factory for creating Layer2SubinterfaceCreateModel instances."""

    class Meta:
        """Meta class that defines the model for Layer2SubinterfaceCreateApiFactory."""

        model = Layer2SubinterfaceCreateModel

    name = factory.Sequence(lambda n: f"ethernet1/1.{n + 100}")
    vlan_tag = factory.Sequence(lambda n: str(n + 100))
    folder = "Shared"
    parent_interface = None
    comment = None

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)


class Layer2SubinterfaceUpdateApiFactory(factory.Factory):
    """Factory for creating Layer2SubinterfaceUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for Layer2SubinterfaceUpdateApiFactory."""

        model = Layer2SubinterfaceUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"ethernet1/1.{n + 100}")
    vlan_tag = factory.Sequence(lambda n: str(n + 100))
    parent_interface = None
    comment = None


class Layer2SubinterfaceResponseFactory(factory.Factory):
    """Factory for creating Layer2SubinterfaceResponseModel instances."""

    class Meta:
        """Meta class that defines the model for Layer2SubinterfaceResponseFactory."""

        model = Layer2SubinterfaceResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"ethernet1/1.{n + 100}")
    vlan_tag = factory.Sequence(lambda n: str(n + 100))
    folder = "Shared"
    parent_interface = None
    comment = None

    @classmethod
    def from_request(cls, request_model: Layer2SubinterfaceCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class Layer2SubinterfaceCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for Layer2SubinterfaceCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"ethernet1/1.{n + 100}")
    vlan_tag = "100"
    folder = "Shared"

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="ethernet1/1.100",
            vlan_tag="100",
            folder="Shared",
            parent_interface="ethernet1/1",
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="ethernet1/1.100",
            vlan_tag="100",
            folder="Shared",
            snippet="TestSnippet",
        )

    @classmethod
    def build_with_no_container(cls):
        """Return a data dict without any container."""
        return cls(
            name="ethernet1/1.100",
            vlan_tag="100",
            folder=None,
            snippet=None,
            device=None,
        )


class Layer2SubinterfaceUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for Layer2SubinterfaceUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"ethernet1/1.{n + 100}")
    vlan_tag = "100"

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating a Layer2 Subinterface."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="ethernet1/1.200",
            vlan_tag="200",
        )
