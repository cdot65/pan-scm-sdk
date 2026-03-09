"""Factory definitions for network BGP Address Family Profile objects."""

import uuid

import factory

from scm.models.network.bgp_address_family_profile import (
    BgpAddressFamilyProfileCreateModel,
    BgpAddressFamilyProfileResponseModel,
    BgpAddressFamilyProfileUpdateModel,
)


# SDK tests against SCM API
class BgpAddressFamilyProfileCreateApiFactory(factory.Factory):
    """Factory for creating BgpAddressFamilyProfileCreateModel instances."""

    class Meta:
        """Meta class that defines the model for BgpAddressFamilyProfileCreateApiFactory."""

        model = BgpAddressFamilyProfileCreateModel

    name = factory.Sequence(lambda n: f"bgp_af_profile_{n}")
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


class BgpAddressFamilyProfileUpdateApiFactory(factory.Factory):
    """Factory for creating BgpAddressFamilyProfileUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for BgpAddressFamilyProfileUpdateApiFactory."""

        model = BgpAddressFamilyProfileUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"bgp_af_profile_{n}")
    ipv4 = None


class BgpAddressFamilyProfileResponseFactory(factory.Factory):
    """Factory for creating BgpAddressFamilyProfileResponseModel instances."""

    class Meta:
        """Meta class that defines the model for BgpAddressFamilyProfileResponseFactory."""

        model = BgpAddressFamilyProfileResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"bgp_af_profile_{n}")
    folder = "Shared"
    ipv4 = None

    @classmethod
    def from_request(cls, request_model: BgpAddressFamilyProfileCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class BgpAddressFamilyProfileCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for BgpAddressFamilyProfileCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"bgp_af_profile_{n}")
    folder = "Shared"

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestBgpAfProfile",
            folder="Shared",
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="TestBgpAfProfile",
            folder="Shared",
            snippet="TestSnippet",
        )

    @classmethod
    def build_with_no_container(cls):
        """Return a data dict without any container."""
        return cls(
            name="TestBgpAfProfile",
            folder=None,
            snippet=None,
            device=None,
        )


class BgpAddressFamilyProfileUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for BgpAddressFamilyProfileUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"bgp_af_profile_{n}")

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating a BGP address family profile."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedBgpAfProfile",
        )
