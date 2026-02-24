# tests/factories/identity/authentication_profile.py

"""Factory definitions for authentication profile objects."""

from uuid import uuid4

import factory  # type: ignore
from faker import Faker

from scm.models.identity.authentication_profiles import (
    AuthenticationProfileCreateModel,
    AuthenticationProfileResponseModel,
    AuthenticationProfileUpdateModel,
)

fake = Faker()


# ----------------------------------------------------------------------------
# API Factories for Create, Update, Response
# ----------------------------------------------------------------------------
class AuthenticationProfileCreateApiFactory(factory.Factory):
    """Factory for creating AuthenticationProfileCreateModel instances."""

    class Meta:
        """Meta class that defines the model for AuthenticationProfileCreateApiFactory."""

        model = AuthenticationProfileCreateModel

    name = factory.Sequence(lambda n: f"authentication_profile_{n}")
    method = factory.LazyFunction(lambda: {"local_database": {}})
    allow_list = ["all"]
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


class AuthenticationProfileUpdateApiFactory(factory.Factory):
    """Factory for creating AuthenticationProfileUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for AuthenticationProfileUpdateApiFactory."""

        model = AuthenticationProfileUpdateModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    name = factory.Sequence(lambda n: f"authentication_profile_{n}")
    method = factory.LazyFunction(lambda: {"local_database": {}})
    allow_list = ["all"]
    folder = None
    snippet = None
    device = None


class AuthenticationProfileResponseFactory(factory.Factory):
    """Factory for creating AuthenticationProfileResponseModel instances."""

    class Meta:
        """Meta class that defines the model for AuthenticationProfileResponseFactory."""

        model = AuthenticationProfileResponseModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    name = factory.Sequence(lambda n: f"authentication_profile_{n}")
    method = factory.LazyFunction(lambda: {"local_database": {}})
    allow_list = ["all"]
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
class AuthenticationProfileCreateModelFactory(factory.Factory):
    """Factory for creating data dicts for AuthenticationProfileCreateModel validation testing."""

    class Meta:
        """Meta class that defines the model for AuthenticationProfileCreateModelFactory."""

        model = dict

    name = factory.Sequence(lambda n: f"authentication_profile_{n}")
    method = factory.LazyFunction(lambda: {"local_database": {}})
    allow_list = ["all"]
    folder = "Texas"
    snippet = None
    device = None

    @classmethod
    def build_valid(cls, **kwargs):
        """Build valid authentication profile data."""
        return cls(folder="Texas", snippet=None, device=None, **kwargs)

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Build authentication profile with multiple containers."""
        return cls(folder="Texas", snippet="TestSnippet", device=None, **kwargs)

    @classmethod
    def build_with_no_container(cls, **kwargs):
        """Build authentication profile with no container."""
        return cls(folder=None, snippet=None, device=None, **kwargs)


class AuthenticationProfileUpdateModelFactory(factory.Factory):
    """Factory for creating data dicts for AuthenticationProfileUpdateModel validation testing."""

    class Meta:
        """Meta class that defines the model for AuthenticationProfileUpdateModelFactory."""

        model = dict

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"authentication_profile_{n}")
    method = factory.LazyFunction(lambda: {"local_database": {}})
    allow_list = ["all"]
    folder = None
    snippet = None
    device = None

    @classmethod
    def build_valid(cls, **kwargs):
        """Build valid authentication profile data."""
        return cls(id="123e4567-e89b-12d3-a456-426655440000", **kwargs)
