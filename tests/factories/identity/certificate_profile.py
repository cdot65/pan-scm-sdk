# tests/factories/identity/certificate_profile.py

"""Factory definitions for certificate profile objects."""

from uuid import uuid4

import factory  # type: ignore
from faker import Faker

from scm.models.identity.certificate_profiles import (
    CertificateProfileCreateModel,
    CertificateProfileResponseModel,
    CertificateProfileUpdateModel,
)

fake = Faker()


# ----------------------------------------------------------------------------
# API Factories for Create, Update, Response
# ----------------------------------------------------------------------------
class CertificateProfileCreateApiFactory(factory.Factory):
    """Factory for creating CertificateProfileCreateModel instances."""

    class Meta:
        """Meta class that defines the model for CertificateProfileCreateApiFactory."""

        model = CertificateProfileCreateModel

    name = factory.Sequence(lambda n: f"certificate_profile_{n}")
    ca_certificates = factory.LazyFunction(lambda: [{"name": "root-ca"}])
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


class CertificateProfileUpdateApiFactory(factory.Factory):
    """Factory for creating CertificateProfileUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for CertificateProfileUpdateApiFactory."""

        model = CertificateProfileUpdateModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    name = factory.Sequence(lambda n: f"certificate_profile_{n}")
    ca_certificates = factory.LazyFunction(lambda: [{"name": "root-ca"}])
    folder = None
    snippet = None
    device = None


class CertificateProfileResponseFactory(factory.Factory):
    """Factory for creating CertificateProfileResponseModel instances."""

    class Meta:
        """Meta class that defines the model for CertificateProfileResponseFactory."""

        model = CertificateProfileResponseModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    name = factory.Sequence(lambda n: f"certificate_profile_{n}")
    ca_certificates = factory.LazyFunction(lambda: [{"name": "root-ca"}])
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
class CertificateProfileCreateModelFactory(factory.Factory):
    """Factory for creating data dicts for CertificateProfileCreateModel validation testing."""

    class Meta:
        """Meta class that defines the model for CertificateProfileCreateModelFactory."""

        model = dict

    name = factory.Sequence(lambda n: f"certificate_profile_{n}")
    ca_certificates = factory.LazyFunction(lambda: [{"name": "root-ca"}])
    folder = "Texas"
    snippet = None
    device = None

    @classmethod
    def build_valid(cls, **kwargs):
        """Build valid certificate profile data."""
        return cls(folder="Texas", snippet=None, device=None, **kwargs)

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Build certificate profile with multiple containers."""
        return cls(folder="Texas", snippet="TestSnippet", device=None, **kwargs)

    @classmethod
    def build_with_no_container(cls, **kwargs):
        """Build certificate profile with no container."""
        return cls(folder=None, snippet=None, device=None, **kwargs)


class CertificateProfileUpdateModelFactory(factory.Factory):
    """Factory for creating data dicts for CertificateProfileUpdateModel validation testing."""

    class Meta:
        """Meta class that defines the model for CertificateProfileUpdateModelFactory."""

        model = dict

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"certificate_profile_{n}")
    ca_certificates = factory.LazyFunction(lambda: [{"name": "root-ca"}])
    folder = None
    snippet = None
    device = None

    @classmethod
    def build_valid(cls, **kwargs):
        """Build valid certificate profile data."""
        if "id" not in kwargs:
            kwargs["id"] = "123e4567-e89b-12d3-a456-426655440000"
        return cls(**kwargs)
