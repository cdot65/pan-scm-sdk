"""Factory definitions for network BGP Redistribution Profile objects."""

import uuid

import factory

from scm.models.network.bgp_redistribution_profile import (
    BgpRedistributionProfileCreateModel,
    BgpRedistributionProfileResponseModel,
    BgpRedistributionProfileUpdateModel,
)


# SDK tests against SCM API
class BgpRedistributionProfileCreateApiFactory(factory.Factory):
    """Factory for creating BgpRedistributionProfileCreateModel instances."""

    class Meta:
        """Meta class that defines the model for BgpRedistributionProfileCreateApiFactory."""

        model = BgpRedistributionProfileCreateModel

    name = factory.Sequence(lambda n: f"bgp_redist_profile_{n}")
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


class BgpRedistributionProfileUpdateApiFactory(factory.Factory):
    """Factory for creating BgpRedistributionProfileUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for BgpRedistributionProfileUpdateApiFactory."""

        model = BgpRedistributionProfileUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"bgp_redist_profile_{n}")
    ipv4 = None


class BgpRedistributionProfileResponseFactory(factory.Factory):
    """Factory for creating BgpRedistributionProfileResponseModel instances."""

    class Meta:
        """Meta class that defines the model for BgpRedistributionProfileResponseFactory."""

        model = BgpRedistributionProfileResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"bgp_redist_profile_{n}")
    folder = "Shared"
    ipv4 = None

    @classmethod
    def from_request(cls, request_model: BgpRedistributionProfileCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class BgpRedistributionProfileCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for BgpRedistributionProfileCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"bgp_redist_profile_{n}")
    folder = "Shared"

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestBgpRedistProfile",
            folder="Shared",
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="TestBgpRedistProfile",
            folder="Shared",
            snippet="TestSnippet",
        )

    @classmethod
    def build_with_no_container(cls):
        """Return a data dict without any container."""
        return cls(
            name="TestBgpRedistProfile",
            folder=None,
            snippet=None,
            device=None,
        )


class BgpRedistributionProfileUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for BgpRedistributionProfileUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"bgp_redist_profile_{n}")

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating a BGP redistribution profile."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedBgpRedistProfile",
        )
