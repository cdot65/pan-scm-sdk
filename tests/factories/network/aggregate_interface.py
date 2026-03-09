"""Factory definitions for network Aggregate Interface objects."""

import uuid

import factory

from scm.models.network.aggregate_interface import (
    AggregateInterfaceCreateModel,
    AggregateInterfaceResponseModel,
    AggregateInterfaceUpdateModel,
)


# SDK tests against SCM API
class AggregateInterfaceCreateApiFactory(factory.Factory):
    """Factory for creating AggregateInterfaceCreateModel instances."""

    class Meta:
        """Meta class that defines the model for AggregateInterfaceCreateApiFactory."""

        model = AggregateInterfaceCreateModel

    name = factory.Sequence(lambda n: f"aggregate_interface_{n}")
    folder = "Shared"
    default_value = None
    comment = None
    layer2 = None
    layer3 = None

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)


class AggregateInterfaceUpdateApiFactory(factory.Factory):
    """Factory for creating AggregateInterfaceUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for AggregateInterfaceUpdateApiFactory."""

        model = AggregateInterfaceUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"aggregate_interface_{n}")
    default_value = None
    comment = None
    layer2 = None
    layer3 = None


class AggregateInterfaceResponseFactory(factory.Factory):
    """Factory for creating AggregateInterfaceResponseModel instances."""

    class Meta:
        """Meta class that defines the model for AggregateInterfaceResponseFactory."""

        model = AggregateInterfaceResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"aggregate_interface_{n}")
    folder = "Shared"
    default_value = None
    comment = None
    layer2 = None
    layer3 = None

    @classmethod
    def from_request(cls, request_model: AggregateInterfaceCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class AggregateInterfaceCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for AggregateInterfaceCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"aggregate_interface_{n}")
    folder = "Shared"

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestAggregateInterface",
            folder="Shared",
            comment="Test aggregate interface",
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="TestAggregateInterface",
            folder="Shared",
            snippet="TestSnippet",
        )

    @classmethod
    def build_with_no_container(cls):
        """Return a data dict without any container."""
        return cls(
            name="TestAggregateInterface",
            folder=None,
            snippet=None,
            device=None,
        )


class AggregateInterfaceUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for AggregateInterfaceUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"aggregate_interface_{n}")

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating an aggregate interface."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedAggregateInterface",
            comment="Updated comment",
        )
