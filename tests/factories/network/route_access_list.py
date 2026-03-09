"""Factory definitions for network Route Access List objects."""

import uuid

import factory

from scm.models.network.route_access_list import (
    RouteAccessListCreateModel,
    RouteAccessListResponseModel,
    RouteAccessListUpdateModel,
)


# SDK tests against SCM API
class RouteAccessListCreateApiFactory(factory.Factory):
    """Factory for creating RouteAccessListCreateModel instances."""

    class Meta:
        """Meta class that defines the model for RouteAccessListCreateApiFactory."""

        model = RouteAccessListCreateModel

    name = factory.Sequence(lambda n: f"route_access_list_{n}")
    folder = "Shared"
    description = None
    type = None

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)


class RouteAccessListUpdateApiFactory(factory.Factory):
    """Factory for creating RouteAccessListUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for RouteAccessListUpdateApiFactory."""

        model = RouteAccessListUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"route_access_list_{n}")
    description = None
    type = None


class RouteAccessListResponseFactory(factory.Factory):
    """Factory for creating RouteAccessListResponseModel instances."""

    class Meta:
        """Meta class that defines the model for RouteAccessListResponseFactory."""

        model = RouteAccessListResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"route_access_list_{n}")
    folder = "Shared"
    description = None
    type = None

    @classmethod
    def from_request(cls, request_model: RouteAccessListCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class RouteAccessListCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for RouteAccessListCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"route_access_list_{n}")
    folder = "Shared"

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestRouteAccessList",
            folder="Shared",
            description="Test route access list",
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="TestRouteAccessList",
            folder="Shared",
            snippet="TestSnippet",
        )

    @classmethod
    def build_with_no_container(cls):
        """Return a data dict without any container."""
        return cls(
            name="TestRouteAccessList",
            folder=None,
            snippet=None,
            device=None,
        )


class RouteAccessListUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for RouteAccessListUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"route_access_list_{n}")

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating a Route Access List."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedRouteAccessList",
            description="Updated description",
        )
