# tests/factories/identity/kerberos_server_profile.py

"""Factory definitions for Kerberos server profile objects."""

from uuid import uuid4

import factory  # type: ignore
from faker import Faker

from scm.models.identity.kerberos_server_profiles import (
    KerberosServerProfileCreateModel,
    KerberosServerProfileResponseModel,
    KerberosServerProfileUpdateModel,
)

fake = Faker()


# ----------------------------------------------------------------------------
# API Factories for Create, Update, Response
# ----------------------------------------------------------------------------
class KerberosServerProfileCreateApiFactory(factory.Factory):
    """Factory for creating KerberosServerProfileCreateModel instances."""

    class Meta:
        """Meta class that defines the model for KerberosServerProfileCreateApiFactory."""

        model = KerberosServerProfileCreateModel

    name = factory.Sequence(lambda n: f"kerberos_server_profile_{n}")
    server = factory.LazyFunction(lambda: [{"name": "kdc1", "host": "10.0.0.1", "port": 88}])
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


class KerberosServerProfileUpdateApiFactory(factory.Factory):
    """Factory for creating KerberosServerProfileUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for KerberosServerProfileUpdateApiFactory."""

        model = KerberosServerProfileUpdateModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    name = factory.Sequence(lambda n: f"kerberos_server_profile_{n}")
    server = factory.LazyFunction(lambda: [{"name": "kdc1", "host": "10.0.0.1", "port": 88}])
    folder = None
    snippet = None
    device = None


class KerberosServerProfileResponseFactory(factory.Factory):
    """Factory for creating KerberosServerProfileResponseModel instances."""

    class Meta:
        """Meta class that defines the model for KerberosServerProfileResponseFactory."""

        model = KerberosServerProfileResponseModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    name = factory.Sequence(lambda n: f"kerberos_server_profile_{n}")
    server = factory.LazyFunction(lambda: [{"name": "kdc1", "host": "10.0.0.1", "port": 88}])
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
class KerberosServerProfileCreateModelFactory(factory.Factory):
    """Factory for creating data dicts for KerberosServerProfileCreateModel validation testing."""

    class Meta:
        """Meta class that defines the model for KerberosServerProfileCreateModelFactory."""

        model = dict

    name = factory.Sequence(lambda n: f"kerberos_server_profile_{n}")
    server = factory.LazyFunction(lambda: [{"name": "kdc1", "host": "10.0.0.1", "port": 88}])
    folder = "Texas"
    snippet = None
    device = None

    @classmethod
    def build_valid(cls, **kwargs):
        """Build valid Kerberos server profile data."""
        return cls(folder="Texas", snippet=None, device=None, **kwargs)

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Build Kerberos server profile with multiple containers."""
        return cls(folder="Texas", snippet="TestSnippet", device=None, **kwargs)

    @classmethod
    def build_with_no_container(cls, **kwargs):
        """Build Kerberos server profile with no container."""
        return cls(folder=None, snippet=None, device=None, **kwargs)


class KerberosServerProfileUpdateModelFactory(factory.Factory):
    """Factory for creating data dicts for KerberosServerProfileUpdateModel validation testing."""

    class Meta:
        """Meta class that defines the model for KerberosServerProfileUpdateModelFactory."""

        model = dict

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"kerberos_server_profile_{n}")
    server = factory.LazyFunction(lambda: [{"name": "kdc1", "host": "10.0.0.1", "port": 88}])
    folder = None
    snippet = None
    device = None

    @classmethod
    def build_valid(cls, **kwargs):
        """Build valid Kerberos server profile data."""
        return cls(id="123e4567-e89b-12d3-a456-426655440000", **kwargs)
