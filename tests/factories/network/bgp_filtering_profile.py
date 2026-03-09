"""Factory definitions for network BGP Filtering Profile objects."""

import uuid

import factory

from scm.models.network.bgp_filtering_profile import (
    BgpFilteringProfileCreateModel,
    BgpFilteringProfileResponseModel,
    BgpFilteringProfileUpdateModel,
)


# SDK tests against SCM API
class BgpFilteringProfileCreateApiFactory(factory.Factory):
    """Factory for creating BgpFilteringProfileCreateModel instances."""

    class Meta:
        """Meta class that defines the model for BgpFilteringProfileCreateApiFactory."""

        model = BgpFilteringProfileCreateModel

    name = factory.Sequence(lambda n: f"bgp_filtering_profile_{n}")
    folder = "Shared"
    ipv4 = None

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)


class BgpFilteringProfileUpdateApiFactory(factory.Factory):
    """Factory for creating BgpFilteringProfileUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for BgpFilteringProfileUpdateApiFactory."""

        model = BgpFilteringProfileUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"bgp_filtering_profile_{n}")
    ipv4 = None


class BgpFilteringProfileResponseFactory(factory.Factory):
    """Factory for creating BgpFilteringProfileResponseModel instances."""

    class Meta:
        """Meta class that defines the model for BgpFilteringProfileResponseFactory."""

        model = BgpFilteringProfileResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"bgp_filtering_profile_{n}")
    folder = "Shared"
    ipv4 = None

    @classmethod
    def from_request(cls, request_model: BgpFilteringProfileCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class BgpFilteringProfileCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for BgpFilteringProfileCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"bgp_filtering_profile_{n}")
    folder = "Shared"

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestBgpFilteringProfile",
            folder="Shared",
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="TestBgpFilteringProfile",
            folder="Shared",
            snippet="TestSnippet",
        )

    @classmethod
    def build_with_no_container(cls):
        """Return a data dict without any container."""
        return cls(
            name="TestBgpFilteringProfile",
            folder=None,
            snippet=None,
            device=None,
        )


class BgpFilteringProfileUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for BgpFilteringProfileUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"bgp_filtering_profile_{n}")

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating a BGP filtering profile."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedBgpFilteringProfile",
        )
