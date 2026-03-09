"""Factory definitions for network Route Prefix List objects."""

import uuid

import factory

from scm.models.network.route_prefix_list import (
    RoutePrefixListCreateModel,
    RoutePrefixListResponseModel,
    RoutePrefixListUpdateModel,
)


# SDK tests against SCM API
class RoutePrefixListCreateApiFactory(factory.Factory):
    """Factory for creating RoutePrefixListCreateModel instances."""

    class Meta:
        """Meta class that defines the model for RoutePrefixListCreateApiFactory."""

        model = RoutePrefixListCreateModel

    name = factory.Sequence(lambda n: f"route_prefix_list_{n}")
    folder = "Shared"
    description = None
    ipv4 = None

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)


class RoutePrefixListUpdateApiFactory(factory.Factory):
    """Factory for creating RoutePrefixListUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for RoutePrefixListUpdateApiFactory."""

        model = RoutePrefixListUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"route_prefix_list_{n}")
    description = None
    ipv4 = None


class RoutePrefixListResponseFactory(factory.Factory):
    """Factory for creating RoutePrefixListResponseModel instances."""

    class Meta:
        """Meta class that defines the model for RoutePrefixListResponseFactory."""

        model = RoutePrefixListResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"route_prefix_list_{n}")
    folder = "Shared"
    description = None
    ipv4 = None

    @classmethod
    def from_request(cls, request_model: RoutePrefixListCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class RoutePrefixListCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for RoutePrefixListCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"route_prefix_list_{n}")
    folder = "Shared"

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestRoutePrefixList",
            folder="Shared",
            description="Test route prefix list",
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="TestRoutePrefixList",
            folder="Shared",
            snippet="TestSnippet",
        )

    @classmethod
    def build_with_no_container(cls):
        """Return a data dict without any container."""
        return cls(
            name="TestRoutePrefixList",
            folder=None,
            snippet=None,
            device=None,
        )


class RoutePrefixListUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for RoutePrefixListUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"route_prefix_list_{n}")

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating a Route Prefix List."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedRoutePrefixList",
            description="Updated description",
        )
