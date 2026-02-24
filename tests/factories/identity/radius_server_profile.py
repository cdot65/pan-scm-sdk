# tests/factories/identity/radius_server_profile.py

"""Factory definitions for RADIUS server profile objects."""

from uuid import uuid4

import factory  # type: ignore
from faker import Faker

from scm.models.identity.radius_server_profiles import (
    RadiusServerProfileCreateModel,
    RadiusServerProfileResponseModel,
    RadiusServerProfileUpdateModel,
)

fake = Faker()


# ----------------------------------------------------------------------------
# API Factories for Create, Update, Response
# ----------------------------------------------------------------------------
class RadiusServerProfileCreateApiFactory(factory.Factory):
    """Factory for creating RadiusServerProfileCreateModel instances."""

    class Meta:
        """Meta class that defines the model for RadiusServerProfileCreateApiFactory."""

        model = RadiusServerProfileCreateModel

    name = factory.Sequence(lambda n: f"radius_server_profile_{n}")
    server = factory.LazyFunction(
        lambda: [{"name": "radius1", "ip_address": "10.0.0.1", "port": 1812, "secret": "secret123"}]
    )
    protocol = factory.LazyFunction(lambda: {"CHAP": {}})
    timeout = 5
    retries = 3
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


class RadiusServerProfileUpdateApiFactory(factory.Factory):
    """Factory for creating RadiusServerProfileUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for RadiusServerProfileUpdateApiFactory."""

        model = RadiusServerProfileUpdateModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    name = factory.Sequence(lambda n: f"radius_server_profile_{n}")
    server = factory.LazyFunction(
        lambda: [{"name": "radius1", "ip_address": "10.0.0.1", "port": 1812, "secret": "secret123"}]
    )
    protocol = factory.LazyFunction(lambda: {"CHAP": {}})
    timeout = 5
    retries = 3
    folder = None
    snippet = None
    device = None


class RadiusServerProfileResponseFactory(factory.Factory):
    """Factory for creating RadiusServerProfileResponseModel instances."""

    class Meta:
        """Meta class that defines the model for RadiusServerProfileResponseFactory."""

        model = RadiusServerProfileResponseModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    name = factory.Sequence(lambda n: f"radius_server_profile_{n}")
    server = factory.LazyFunction(
        lambda: [{"name": "radius1", "ip_address": "10.0.0.1", "port": 1812, "secret": "secret123"}]
    )
    protocol = factory.LazyFunction(lambda: {"CHAP": {}})
    timeout = 5
    retries = 3
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
class RadiusServerProfileCreateModelFactory(factory.Factory):
    """Factory for creating data dicts for RadiusServerProfileCreateModel validation testing."""

    class Meta:
        """Meta class that defines the model for RadiusServerProfileCreateModelFactory."""

        model = dict

    name = factory.Sequence(lambda n: f"radius_server_profile_{n}")
    server = factory.LazyFunction(
        lambda: [{"name": "radius1", "ip_address": "10.0.0.1", "port": 1812, "secret": "secret123"}]
    )
    protocol = factory.LazyFunction(lambda: {"CHAP": {}})
    timeout = 5
    retries = 3
    folder = "Texas"
    snippet = None
    device = None

    @classmethod
    def build_valid(cls, **kwargs):
        """Build valid RADIUS server profile data."""
        return cls(folder="Texas", snippet=None, device=None, **kwargs)

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Build RADIUS server profile with multiple containers."""
        return cls(folder="Texas", snippet="TestSnippet", device=None, **kwargs)

    @classmethod
    def build_with_no_container(cls, **kwargs):
        """Build RADIUS server profile with no container."""
        return cls(folder=None, snippet=None, device=None, **kwargs)


class RadiusServerProfileUpdateModelFactory(factory.Factory):
    """Factory for creating data dicts for RadiusServerProfileUpdateModel validation testing."""

    class Meta:
        """Meta class that defines the model for RadiusServerProfileUpdateModelFactory."""

        model = dict

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"radius_server_profile_{n}")
    server = factory.LazyFunction(
        lambda: [{"name": "radius1", "ip_address": "10.0.0.1", "port": 1812, "secret": "secret123"}]
    )
    protocol = factory.LazyFunction(lambda: {"CHAP": {}})
    timeout = 5
    retries = 3
    folder = None
    snippet = None
    device = None

    @classmethod
    def build_valid(cls, **kwargs):
        """Build valid RADIUS server profile data."""
        return cls(id="123e4567-e89b-12d3-a456-426655440000", **kwargs)
