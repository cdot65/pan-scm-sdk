"""Factory definitions for network BGP Route Map objects."""

import uuid

import factory

from scm.models.network.bgp_route_map import (
    BgpRouteMapCreateModel,
    BgpRouteMapResponseModel,
    BgpRouteMapUpdateModel,
)


# SDK tests against SCM API
class BgpRouteMapCreateApiFactory(factory.Factory):
    """Factory for creating BgpRouteMapCreateModel instances."""

    class Meta:
        """Meta class that defines the model for BgpRouteMapCreateApiFactory."""

        model = BgpRouteMapCreateModel

    name = factory.Sequence(lambda n: f"bgp_route_map_{n}")
    folder = "Shared"
    route_map = None

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)


class BgpRouteMapUpdateApiFactory(factory.Factory):
    """Factory for creating BgpRouteMapUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for BgpRouteMapUpdateApiFactory."""

        model = BgpRouteMapUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"bgp_route_map_{n}")
    route_map = None


class BgpRouteMapResponseFactory(factory.Factory):
    """Factory for creating BgpRouteMapResponseModel instances."""

    class Meta:
        """Meta class that defines the model for BgpRouteMapResponseFactory."""

        model = BgpRouteMapResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"bgp_route_map_{n}")
    folder = "Shared"
    route_map = None

    @classmethod
    def from_request(cls, request_model: BgpRouteMapCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class BgpRouteMapCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for BgpRouteMapCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"bgp_route_map_{n}")
    folder = "Shared"

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestBgpRouteMap",
            folder="Shared",
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="TestBgpRouteMap",
            folder="Shared",
            snippet="TestSnippet",
        )

    @classmethod
    def build_with_no_container(cls):
        """Return a data dict without any container."""
        return cls(
            name="TestBgpRouteMap",
            folder=None,
            snippet=None,
            device=None,
        )


class BgpRouteMapUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for BgpRouteMapUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"bgp_route_map_{n}")

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating a BGP route map."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedBgpRouteMap",
        )
