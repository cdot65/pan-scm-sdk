"""Factory definitions for network Logical Router objects."""

import uuid

import factory

from scm.models.network.logical_router import (
    LogicalRouterCreateModel,
    LogicalRouterResponseModel,
    LogicalRouterUpdateModel,
)


# SDK tests against SCM API
class LogicalRouterCreateApiFactory(factory.Factory):
    """Factory for creating LogicalRouterCreateModel instances."""

    class Meta:
        """Meta class that defines the model for LogicalRouterCreateApiFactory."""

        model = LogicalRouterCreateModel

    name = factory.Sequence(lambda n: f"logical_router_{n}")
    folder = "Shared"
    routing_stack = None
    vrf = None

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)


class LogicalRouterUpdateApiFactory(factory.Factory):
    """Factory for creating LogicalRouterUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for LogicalRouterUpdateApiFactory."""

        model = LogicalRouterUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"logical_router_{n}")
    routing_stack = None
    vrf = None


class LogicalRouterResponseFactory(factory.Factory):
    """Factory for creating LogicalRouterResponseModel instances."""

    class Meta:
        """Meta class that defines the model for LogicalRouterResponseFactory."""

        model = LogicalRouterResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"logical_router_{n}")
    folder = "Shared"
    routing_stack = None
    vrf = None

    @classmethod
    def from_request(cls, request_model: LogicalRouterCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class LogicalRouterCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for LogicalRouterCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"logical_router_{n}")
    folder = "Shared"

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestLogicalRouter",
            folder="Shared",
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="TestLogicalRouter",
            folder="Shared",
            snippet="TestSnippet",
        )

    @classmethod
    def build_with_no_container(cls):
        """Return a data dict without any container."""
        return cls(
            name="TestLogicalRouter",
            folder=None,
            snippet=None,
            device=None,
        )


class LogicalRouterUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for LogicalRouterUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"logical_router_{n}")

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating a Logical Router."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedLogicalRouter",
        )
