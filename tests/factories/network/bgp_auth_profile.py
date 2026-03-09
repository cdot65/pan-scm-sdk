"""Factory definitions for network BGP Authentication Profile objects."""

import uuid

import factory

from scm.models.network.bgp_auth_profile import (
    BgpAuthProfileCreateModel,
    BgpAuthProfileResponseModel,
    BgpAuthProfileUpdateModel,
)


# SDK tests against SCM API
class BgpAuthProfileCreateApiFactory(factory.Factory):
    """Factory for creating BgpAuthProfileCreateModel instances."""

    class Meta:
        """Meta class that defines the model for BgpAuthProfileCreateApiFactory."""

        model = BgpAuthProfileCreateModel

    name = factory.Sequence(lambda n: f"bgp_auth_profile_{n}")
    folder = "Shared"
    secret = None

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)


class BgpAuthProfileUpdateApiFactory(factory.Factory):
    """Factory for creating BgpAuthProfileUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for BgpAuthProfileUpdateApiFactory."""

        model = BgpAuthProfileUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"bgp_auth_profile_{n}")
    secret = None


class BgpAuthProfileResponseFactory(factory.Factory):
    """Factory for creating BgpAuthProfileResponseModel instances."""

    class Meta:
        """Meta class that defines the model for BgpAuthProfileResponseFactory."""

        model = BgpAuthProfileResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"bgp_auth_profile_{n}")
    folder = "Shared"
    secret = None

    @classmethod
    def from_request(cls, request_model: BgpAuthProfileCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class BgpAuthProfileCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for BgpAuthProfileCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"bgp_auth_profile_{n}")
    folder = "Shared"

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestBgpAuthProfile",
            folder="Shared",
            secret="my-secret-key",
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="TestBgpAuthProfile",
            folder="Shared",
            snippet="TestSnippet",
        )

    @classmethod
    def build_with_no_container(cls):
        """Return a data dict without any container."""
        return cls(
            name="TestBgpAuthProfile",
            folder=None,
            snippet=None,
            device=None,
        )


class BgpAuthProfileUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for BgpAuthProfileUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"bgp_auth_profile_{n}")

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating a BGP auth profile."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedBgpAuthProfile",
            secret="updated-secret",
        )
