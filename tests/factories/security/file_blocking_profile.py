# tests/factories/security/file_blocking_profile.py

"""Factory definitions for file blocking profile objects."""

from uuid import uuid4

import factory  # type: ignore
from faker import Faker

from scm.models.security.file_blocking_profiles import (
    FileBlockingProfileBaseModel,
    FileBlockingProfileCreateModel,
    FileBlockingProfileResponseModel,
    FileBlockingProfileUpdateModel,
)

fake = Faker()


# ----------------------------------------------------------------------------
# Base factory for File Blocking Profile models
# ----------------------------------------------------------------------------
class FileBlockingProfileBaseFactory(factory.Factory):
    """Base factory for File Blocking Profile with common fields."""

    class Meta:
        """Meta class that defines the model for FileBlockingProfileBaseFactory."""

        model = FileBlockingProfileBaseModel
        abstract = True

    name = factory.Sequence(lambda n: f"file_blocking_profile_{n}")
    description = factory.LazyFunction(lambda: fake.sentence())
    rules = None
    # Container fields default to None
    folder = None
    snippet = None
    device = None


# ----------------------------------------------------------------------------
# API Factories for Create, Update, Response
# ----------------------------------------------------------------------------
class FileBlockingProfileCreateApiFactory(FileBlockingProfileBaseFactory):
    """Factory for creating FileBlockingProfileCreateModel instances."""

    class Meta:
        """Meta class that defines the model for FileBlockingProfileCreateApiFactory."""

        model = FileBlockingProfileCreateModel

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


class FileBlockingProfileUpdateApiFactory(FileBlockingProfileBaseFactory):
    """Factory for creating FileBlockingProfileUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for FileBlockingProfileUpdateApiFactory."""

        model = FileBlockingProfileUpdateModel

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


class FileBlockingProfileResponseFactory(FileBlockingProfileBaseFactory):
    """Factory for creating FileBlockingProfileResponseModel instances."""

    class Meta:
        """Meta class that defines the model for FileBlockingProfileResponseFactory."""

        model = FileBlockingProfileResponseModel

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
    def from_request(cls, request_model: FileBlockingProfileCreateModel, **kwargs):
        """Create response factory from request model."""
        data = request_model.model_dump()
        data.pop("id", None)
        return cls(**data, **kwargs)


# ----------------------------------------------------------------------------
# Minimal valid rule dict factory
# ----------------------------------------------------------------------------
class FileBlockingRuleDictFactory:
    """Factory for creating file blocking rule dictionaries."""

    @classmethod
    def build_valid(cls, **kwargs):
        """Build valid file blocking rule dictionary."""
        return {
            "name": "test-rule",
            "action": "alert",
            "application": ["any"],
            "direction": "both",
            "file_type": ["any"],
            **kwargs,
        }


# ----------------------------------------------------------------------------
# Model dict factories for Pydantic validation testing
# ----------------------------------------------------------------------------
class FileBlockingProfileCreateModelFactory(factory.Factory):
    """Factory for creating data dicts for FileBlockingProfileCreateModel validation testing."""

    class Meta:
        """Meta class that defines the model for FileBlockingProfileCreateModelFactory."""

        model = dict

    name = factory.Sequence(lambda n: f"file_blocking_profile_{n}")
    description = factory.LazyFunction(lambda: fake.sentence())
    rules = factory.LazyFunction(lambda: [FileBlockingRuleDictFactory.build_valid()])
    folder = "Texas"
    snippet = None
    device = None

    @classmethod
    def build_valid(cls, **kwargs):
        """Build valid file blocking profile."""
        return cls(
            rules=[FileBlockingRuleDictFactory.build_valid()],
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


class FileBlockingProfileUpdateModelFactory(factory.Factory):
    """Factory for creating data dicts for FileBlockingProfileUpdateModel validation testing."""

    class Meta:
        """Meta class that defines the model for FileBlockingProfileUpdateModelFactory."""

        model = dict

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"file_blocking_profile_{n}")
    description = factory.LazyFunction(lambda: fake.sentence())
    rules = factory.LazyFunction(lambda: [FileBlockingRuleDictFactory.build_valid()])
    folder = "Texas"
    snippet = None
    device = None

    @classmethod
    def build_valid(cls, **kwargs):
        """Build valid file blocking profile update."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            rules=[FileBlockingRuleDictFactory.build_valid()],
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
