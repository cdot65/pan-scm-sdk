"""Factory definitions for network Security Zone objects."""

import uuid

import factory

from scm.models.network.security_zone import (
    SecurityZoneCreateModel,
    SecurityZoneResponseModel,
    SecurityZoneUpdateModel,
)


# SDK tests against SCM API
class SecurityZoneCreateApiFactory(factory.Factory):
    """Factory for creating SecurityZoneCreateModel instances."""

    class Meta:
        """Meta class that defines the model for SecurityZoneCreateApiFactory."""

        model = SecurityZoneCreateModel

    name = factory.Sequence(lambda n: f"security_zone_{n}")
    folder = "Shared"
    enable_user_identification = None
    enable_device_identification = None
    dos_profile = None
    dos_log_setting = None
    network = None
    user_acl = None
    device_acl = None

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)


class SecurityZoneUpdateApiFactory(factory.Factory):
    """Factory for creating SecurityZoneUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for SecurityZoneUpdateApiFactory."""

        model = SecurityZoneUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"security_zone_{n}")
    enable_user_identification = None
    enable_device_identification = None
    dos_profile = None
    dos_log_setting = None
    network = None
    user_acl = None
    device_acl = None


class SecurityZoneResponseFactory(factory.Factory):
    """Factory for creating SecurityZoneResponseModel instances."""

    class Meta:
        """Meta class that defines the model for SecurityZoneResponseFactory."""

        model = SecurityZoneResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"security_zone_{n}")
    folder = "Shared"
    enable_user_identification = None
    enable_device_identification = None
    dos_profile = None
    dos_log_setting = None
    network = None
    user_acl = None
    device_acl = None

    @classmethod
    def from_request(cls, request_model: SecurityZoneCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class SecurityZoneCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for SecurityZoneCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"security_zone_{n}")
    folder = "Shared"

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestSecurityZone",
            folder="Shared",
            enable_user_identification=True,
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="TestSecurityZone",
            folder="Shared",
            snippet="TestSnippet",
        )

    @classmethod
    def build_with_no_container(cls):
        """Return a data dict without any container."""
        return cls(
            name="TestSecurityZone",
            folder=None,
            snippet=None,
            device=None,
        )


class SecurityZoneUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for SecurityZoneUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"security_zone_{n}")

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating a security zone."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedSecurityZone",
            enable_user_identification=True,
        )
