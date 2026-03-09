"""Factory definitions for network OSPF Authentication Profile objects."""

import uuid

import factory

from scm.models.network.ospf_auth_profile import (
    OspfAuthProfileCreateModel,
    OspfAuthProfileResponseModel,
    OspfAuthProfileUpdateModel,
)


# SDK tests against SCM API
class OspfAuthProfileCreateApiFactory(factory.Factory):
    """Factory for creating OspfAuthProfileCreateModel instances."""

    class Meta:
        """Meta class that defines the model for OspfAuthProfileCreateApiFactory."""

        model = OspfAuthProfileCreateModel

    name = factory.Sequence(lambda n: f"ospf_auth_profile_{n}")
    folder = "Shared"
    password = None
    md5 = None

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)


class OspfAuthProfileUpdateApiFactory(factory.Factory):
    """Factory for creating OspfAuthProfileUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for OspfAuthProfileUpdateApiFactory."""

        model = OspfAuthProfileUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"ospf_auth_profile_{n}")
    password = None
    md5 = None


class OspfAuthProfileResponseFactory(factory.Factory):
    """Factory for creating OspfAuthProfileResponseModel instances."""

    class Meta:
        """Meta class that defines the model for OspfAuthProfileResponseFactory."""

        model = OspfAuthProfileResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"ospf_auth_profile_{n}")
    folder = "Shared"
    password = None
    md5 = None

    @classmethod
    def from_request(cls, request_model: OspfAuthProfileCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class OspfAuthProfileCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for OspfAuthProfileCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"ospf_auth_profile_{n}")
    folder = "Shared"

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestOspfAuthProfile",
            folder="Shared",
            password="testpassword",
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="TestOspfAuthProfile",
            folder="Shared",
            snippet="TestSnippet",
        )

    @classmethod
    def build_with_no_container(cls):
        """Return a data dict without any container."""
        return cls(
            name="TestOspfAuthProfile",
            folder=None,
            snippet=None,
            device=None,
        )


class OspfAuthProfileUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for OspfAuthProfileUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"ospf_auth_profile_{n}")

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating an OSPF Auth Profile."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedOspfAuthProfile",
            password="updatedpassword",
        )
