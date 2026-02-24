# tests/factories/identity/tacacs_server_profile.py

"""Factory definitions for TACACS+ server profile objects."""

from uuid import uuid4

import factory  # type: ignore
from faker import Faker

from scm.models.identity.tacacs_server_profiles import (
    TacacsServerProfileCreateModel,
    TacacsServerProfileResponseModel,
    TacacsServerProfileUpdateModel,
)

fake = Faker()


# ----------------------------------------------------------------------------
# API Factories for Create, Update, Response
# ----------------------------------------------------------------------------
class TacacsServerProfileCreateApiFactory(factory.Factory):
    """Factory for creating TacacsServerProfileCreateModel instances."""

    class Meta:
        """Meta class that defines the model for TacacsServerProfileCreateApiFactory."""

        model = TacacsServerProfileCreateModel

    name = factory.Sequence(lambda n: f"tacacs_server_profile_{n}")
    server = factory.LazyFunction(
        lambda: [{"name": "tacacs1", "address": "10.0.0.1", "port": 49, "secret": "secret123"}]
    )
    protocol = "CHAP"
    timeout = 5
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


class TacacsServerProfileUpdateApiFactory(factory.Factory):
    """Factory for creating TacacsServerProfileUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for TacacsServerProfileUpdateApiFactory."""

        model = TacacsServerProfileUpdateModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    name = factory.Sequence(lambda n: f"tacacs_server_profile_{n}")
    server = factory.LazyFunction(
        lambda: [{"name": "tacacs1", "address": "10.0.0.1", "port": 49, "secret": "secret123"}]
    )
    protocol = "CHAP"
    timeout = 5
    folder = None
    snippet = None
    device = None


class TacacsServerProfileResponseFactory(factory.Factory):
    """Factory for creating TacacsServerProfileResponseModel instances."""

    class Meta:
        """Meta class that defines the model for TacacsServerProfileResponseFactory."""

        model = TacacsServerProfileResponseModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    name = factory.Sequence(lambda n: f"tacacs_server_profile_{n}")
    server = factory.LazyFunction(
        lambda: [{"name": "tacacs1", "address": "10.0.0.1", "port": 49, "secret": "secret123"}]
    )
    protocol = "CHAP"
    timeout = 5
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
class TacacsServerProfileCreateModelFactory(factory.Factory):
    """Factory for creating data dicts for TacacsServerProfileCreateModel validation testing."""

    class Meta:
        """Meta class that defines the model for TacacsServerProfileCreateModelFactory."""

        model = dict

    name = factory.Sequence(lambda n: f"tacacs_server_profile_{n}")
    server = factory.LazyFunction(
        lambda: [{"name": "tacacs1", "address": "10.0.0.1", "port": 49, "secret": "secret123"}]
    )
    protocol = "CHAP"
    timeout = 5
    folder = "Texas"
    snippet = None
    device = None

    @classmethod
    def build_valid(cls, **kwargs):
        """Build valid TACACS+ server profile data."""
        return cls(folder="Texas", snippet=None, device=None, **kwargs)

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Build TACACS+ server profile with multiple containers."""
        return cls(folder="Texas", snippet="TestSnippet", device=None, **kwargs)

    @classmethod
    def build_with_no_container(cls, **kwargs):
        """Build TACACS+ server profile with no container."""
        return cls(folder=None, snippet=None, device=None, **kwargs)


class TacacsServerProfileUpdateModelFactory(factory.Factory):
    """Factory for creating data dicts for TacacsServerProfileUpdateModel validation testing."""

    class Meta:
        """Meta class that defines the model for TacacsServerProfileUpdateModelFactory."""

        model = dict

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"tacacs_server_profile_{n}")
    server = factory.LazyFunction(
        lambda: [{"name": "tacacs1", "address": "10.0.0.1", "port": 49, "secret": "secret123"}]
    )
    protocol = "CHAP"
    timeout = 5
    folder = None
    snippet = None
    device = None

    @classmethod
    def build_valid(cls, **kwargs):
        """Build valid TACACS+ server profile data."""
        return cls(id="123e4567-e89b-12d3-a456-426655440000", **kwargs)
