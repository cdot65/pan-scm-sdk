"""Factory definitions for network BGP Route Map Redistribution objects."""

import uuid

import factory

from scm.models.network.bgp_route_map_redistribution import (
    BgpRouteMapRedistributionCreateModel,
    BgpRouteMapRedistributionResponseModel,
    BgpRouteMapRedistributionUpdateModel,
)


# SDK tests against SCM API
class BgpRouteMapRedistributionCreateApiFactory(factory.Factory):
    """Factory for creating BgpRouteMapRedistributionCreateModel instances."""

    class Meta:
        """Meta class that defines the model for BgpRouteMapRedistributionCreateApiFactory."""

        model = BgpRouteMapRedistributionCreateModel

    name = factory.Sequence(lambda n: f"bgp_route_map_redist_{n}")
    folder = "Shared"
    bgp = None
    ospf = None
    connected_static = None

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)


class BgpRouteMapRedistributionUpdateApiFactory(factory.Factory):
    """Factory for creating BgpRouteMapRedistributionUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for BgpRouteMapRedistributionUpdateApiFactory."""

        model = BgpRouteMapRedistributionUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"bgp_route_map_redist_{n}")
    bgp = None
    ospf = None
    connected_static = None


class BgpRouteMapRedistributionResponseFactory(factory.Factory):
    """Factory for creating BgpRouteMapRedistributionResponseModel instances."""

    class Meta:
        """Meta class that defines the model for BgpRouteMapRedistributionResponseFactory."""

        model = BgpRouteMapRedistributionResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"bgp_route_map_redist_{n}")
    folder = "Shared"
    bgp = None
    ospf = None
    connected_static = None

    @classmethod
    def from_request(cls, request_model: BgpRouteMapRedistributionCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class BgpRouteMapRedistributionCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for BgpRouteMapRedistributionCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"bgp_route_map_redist_{n}")
    folder = "Shared"

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestBgpRouteMapRedist",
            folder="Shared",
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="TestBgpRouteMapRedist",
            folder="Shared",
            snippet="TestSnippet",
        )

    @classmethod
    def build_with_no_container(cls):
        """Return a data dict without any container."""
        return cls(
            name="TestBgpRouteMapRedist",
            folder=None,
            snippet=None,
            device=None,
        )


class BgpRouteMapRedistributionUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for BgpRouteMapRedistributionUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"bgp_route_map_redist_{n}")

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating a BGP route map redistribution."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedBgpRouteMapRedist",
        )
