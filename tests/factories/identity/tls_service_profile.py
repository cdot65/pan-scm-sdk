# tests/factories/identity/tls_service_profile.py

"""Factory definitions for TLS service profile objects."""

from uuid import uuid4

import factory  # type: ignore
from faker import Faker

from scm.models.identity.tls_service_profiles import (
    TlsServiceProfileCreateModel,
    TlsServiceProfileResponseModel,
    TlsServiceProfileUpdateModel,
)

fake = Faker()


# ----------------------------------------------------------------------------
# API Factories for Create, Update, Response
# ----------------------------------------------------------------------------
class TlsServiceProfileCreateApiFactory(factory.Factory):
    """Factory for creating TlsServiceProfileCreateModel instances."""

    class Meta:
        """Meta class that defines the model for TlsServiceProfileCreateApiFactory."""

        model = TlsServiceProfileCreateModel

    name = factory.Sequence(lambda n: f"tls_service_profile_{n}")
    certificate = factory.Sequence(lambda n: f"cert_{n}")
    folder = "Texas"
    snippet = None
    device = None

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Factory method for creating with snippet."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """Factory method for creating with device."""
        return cls(folder=None, snippet=None, device=device, **kwargs)


class TlsServiceProfileUpdateApiFactory(factory.Factory):
    """Factory for creating TlsServiceProfileUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for TlsServiceProfileUpdateApiFactory."""

        model = TlsServiceProfileUpdateModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    name = factory.Sequence(lambda n: f"tls_service_profile_{n}")
    certificate = factory.Sequence(lambda n: f"cert_{n}")
    folder = None
    snippet = None
    device = None


class TlsServiceProfileResponseFactory(factory.Factory):
    """Factory for creating TlsServiceProfileResponseModel instances."""

    class Meta:
        """Meta class that defines the model for TlsServiceProfileResponseFactory."""

        model = TlsServiceProfileResponseModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    name = factory.Sequence(lambda n: f"tls_service_profile_{n}")
    certificate = factory.Sequence(lambda n: f"cert_{n}")
    folder = "Texas"
    snippet = None
    device = None

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Factory method for creating with snippet."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """Factory method for creating with device."""
        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def from_request(cls, request_model, **kwargs):
        """Create response factory from request model."""
        data = request_model.model_dump()
        data.pop("id", None)
        return cls(**data, **kwargs)


# ----------------------------------------------------------------------------
# Model dict factories for Pydantic validation testing
# ----------------------------------------------------------------------------
class TlsServiceProfileCreateModelFactory(factory.Factory):
    """Factory for creating data dicts for TlsServiceProfileCreateModel validation testing."""

    class Meta:
        """Meta class that defines the model for TlsServiceProfileCreateModelFactory."""

        model = dict

    name = factory.Sequence(lambda n: f"tls_service_profile_{n}")
    certificate = factory.Sequence(lambda n: f"cert_{n}")
    folder = "Texas"
    snippet = None
    device = None

    @classmethod
    def build_valid(cls, **kwargs):
        """Build valid TLS service profile data."""
        return cls(folder="Texas", snippet=None, device=None, **kwargs)

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Build TLS service profile with multiple containers."""
        return cls(folder="Texas", snippet="TestSnippet", device=None, **kwargs)

    @classmethod
    def build_with_no_container(cls, **kwargs):
        """Build TLS service profile with no container."""
        return cls(folder=None, snippet=None, device=None, **kwargs)


class TlsServiceProfileUpdateModelFactory(factory.Factory):
    """Factory for creating data dicts for TlsServiceProfileUpdateModel validation testing."""

    class Meta:
        """Meta class that defines the model for TlsServiceProfileUpdateModelFactory."""

        model = dict

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"tls_service_profile_{n}")
    certificate = factory.Sequence(lambda n: f"cert_{n}")
    folder = None
    snippet = None
    device = None

    @classmethod
    def build_valid(cls, **kwargs):
        """Build valid TLS service profile data."""
        if "id" not in kwargs:
            kwargs["id"] = "123e4567-e89b-12d3-a456-426655440000"
        return cls(**kwargs)
