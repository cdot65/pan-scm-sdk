# tests/factories/security/url_access_profile.py

"""Factory definitions for URL access profile objects."""

from uuid import uuid4

import factory  # type: ignore
from faker import Faker

from scm.models.security.url_access_profiles import (
    URLAccessProfileBaseModel,
    URLAccessProfileCreateModel,
    URLAccessProfileResponseModel,
    URLAccessProfileUpdateModel,
)

fake = Faker()


# ----------------------------------------------------------------------------
# Base factory for URL Access Profile models
# ----------------------------------------------------------------------------
class URLAccessProfileBaseFactory(factory.Factory):
    """Base factory for URL Access Profile with common fields."""

    class Meta:
        """Meta class that defines the model for URLAccessProfileBaseFactory."""

        model = URLAccessProfileBaseModel
        abstract = True

    name = factory.Sequence(lambda n: f"url_access_profile_{n}")
    description = factory.LazyFunction(lambda: fake.sentence())
    alert = None
    allow = None
    block = None
    continue_ = None
    # Container fields default to None
    folder = None
    snippet = None
    device = None


# ----------------------------------------------------------------------------
# API Factories for Create, Update, Response
# ----------------------------------------------------------------------------
class URLAccessProfileCreateApiFactory(URLAccessProfileBaseFactory):
    """Factory for creating URLAccessProfileCreateModel instances."""

    class Meta:
        """Meta class that defines the model for URLAccessProfileCreateApiFactory."""

        model = URLAccessProfileCreateModel

    folder = "Texas"

    @classmethod
    def with_folder(cls, folder="Texas", **kwargs):
        """Factory method for creating with folder."""
        return cls(folder=folder, snippet=None, device=None, **kwargs)

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Factory method for creating with snippet."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """Factory method for creating with device."""
        return cls(folder=None, snippet=None, device=device, **kwargs)


class URLAccessProfileUpdateApiFactory(URLAccessProfileBaseFactory):
    """Factory for creating URLAccessProfileUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for URLAccessProfileUpdateApiFactory."""

        model = URLAccessProfileUpdateModel

    id = factory.LazyFunction(lambda: str(uuid4()))

    @classmethod
    def with_folder(cls, folder="Texas", **kwargs):
        """Factory method for creating with folder."""
        return cls(folder=folder, snippet=None, device=None, **kwargs)

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Factory method for creating with snippet."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """Factory method for creating with device."""
        return cls(folder=None, snippet=None, device=device, **kwargs)


class URLAccessProfileResponseFactory(URLAccessProfileBaseFactory):
    """Factory for creating URLAccessProfileResponseModel instances."""

    class Meta:
        """Meta class that defines the model for URLAccessProfileResponseFactory."""

        model = URLAccessProfileResponseModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    folder = "Texas"

    @classmethod
    def with_folder(cls, folder="Texas", **kwargs):
        """Factory method for creating with folder."""
        return cls(folder=folder, snippet=None, device=None, **kwargs)

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Factory method for creating with snippet."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """Factory method for creating with device."""
        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def from_request(cls, request_model: URLAccessProfileCreateModel, **kwargs):
        """Create response factory from request model."""
        data = request_model.model_dump()
        data.pop("id", None)
        return cls(**data, **kwargs)


# ----------------------------------------------------------------------------
# Model dict factories for Pydantic validation testing
# ----------------------------------------------------------------------------
class URLAccessProfileCreateModelFactory(factory.Factory):
    """Factory for creating data dicts for URLAccessProfileCreateModel validation testing."""

    class Meta:
        """Meta class that defines the model for URLAccessProfileCreateModelFactory."""

        model = dict

    name = factory.Sequence(lambda n: f"url_access_profile_{n}")
    description = factory.LazyFunction(lambda: fake.sentence())
    folder = "Texas"
    snippet = None
    device = None

    @classmethod
    def build_valid(cls, **kwargs):
        """Build valid URL access profile."""
        return cls(
            folder="Texas",
            snippet=None,
            device=None,
            **kwargs,
        )

    @classmethod
    def build_with_folder(cls, **kwargs):
        """Build profile with folder container."""
        return cls(folder="Texas", snippet=None, device=None, **kwargs)

    @classmethod
    def build_with_snippet(cls, **kwargs):
        """Build profile with snippet container."""
        return cls(folder=None, snippet="TestSnippet", device=None, **kwargs)

    @classmethod
    def build_with_device(cls, **kwargs):
        """Build profile with device container."""
        return cls(folder=None, snippet=None, device="TestDevice", **kwargs)

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Build profile with multiple containers."""
        return cls(folder="Texas", snippet="TestSnippet", device=None, **kwargs)

    @classmethod
    def build_with_no_container(cls, **kwargs):
        """Build profile with no container."""
        return cls(folder=None, snippet=None, device=None, **kwargs)


class URLAccessProfileUpdateModelFactory(factory.Factory):
    """Factory for creating data dicts for URLAccessProfileUpdateModel validation testing."""

    class Meta:
        """Meta class that defines the model for URLAccessProfileUpdateModelFactory."""

        model = dict

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"url_access_profile_{n}")
    description = factory.LazyFunction(lambda: fake.sentence())
    folder = "Texas"
    snippet = None
    device = None

    @classmethod
    def build_valid(cls, **kwargs):
        """Build valid URL access profile update."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            folder="Texas",
            snippet=None,
            device=None,
            **kwargs,
        )

    @classmethod
    def build_with_folder(cls, **kwargs):
        """Build profile with folder container."""
        return cls(folder="Texas", snippet=None, device=None, **kwargs)

    @classmethod
    def build_with_snippet(cls, **kwargs):
        """Build profile with snippet container."""
        return cls(folder=None, snippet="TestSnippet", device=None, **kwargs)

    @classmethod
    def build_with_device(cls, **kwargs):
        """Build profile with device container."""
        return cls(folder=None, snippet=None, device="TestDevice", **kwargs)

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Build profile with multiple containers."""
        return cls(folder="Texas", snippet="TestSnippet", device=None, **kwargs)

    @classmethod
    def build_with_no_container(cls, **kwargs):
        """Build profile with no container."""
        return cls(folder=None, snippet=None, device=None, **kwargs)
