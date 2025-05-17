# tests/factories/security/anti_spyware_profile.py

"""Factory definitions for anti-spyware profile objects."""

from uuid import uuid4

import factory  # type: ignore
from faker import Faker

from scm.models.security.anti_spyware_profiles import (
    AntiSpywareProfileBase,
    AntiSpywareProfileCreateModel,
    AntiSpywareProfileResponseModel,
    AntiSpywareProfileUpdateModel,
)

fake = Faker()


# ----------------------------------------------------------------------------
# Base factory for Anti-Spyware Profile models
# ----------------------------------------------------------------------------
class AntiSpywareProfileBaseFactory(factory.Factory):
    """Base factory for Anti-Spyware Profile with common fields."""

    class Meta:
        """Meta class that defines the model for AntiSpywareProfileBaseFactory. This is the base factory for Anti-Spyware Profile models."""

        model = AntiSpywareProfileBase
        abstract = True

    name = factory.Sequence(lambda n: f"anti_spyware_profile_{n}")
    description = factory.LazyFunction(lambda: fake.sentence())
    rules = factory.List([])
    threat_exceptions = factory.List([])
    # Container fields default to None
    folder = None
    snippet = None
    device = None


# ----------------------------------------------------------------------------
# API Factories for Create, Update, Response
# ----------------------------------------------------------------------------
class AntiSpywareProfileCreateApiFactory(AntiSpywareProfileBaseFactory):
    """Factory for creating AntiSpywareProfileCreateModel instances."""

    class Meta:
        """Meta class that defines the model for AntiSpywareProfileCreateApiFactory. This factory inherits from AntiSpywareProfileBaseFactory."""

        model = AntiSpywareProfileCreateModel

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


class AntiSpywareProfileUpdateApiFactory(AntiSpywareProfileBaseFactory):
    """Factory for creating AntiSpywareProfileUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for AntiSpywareProfileUpdateApiFactory. This factory inherits from AntiSpywareProfileBaseFactory."""

        model = AntiSpywareProfileUpdateModel

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

    @classmethod
    def with_cloud_inline_analysis(cls, **kwargs):
        """Factory method to set cloud_inline_analysis=True for supported models."""
        return cls(cloud_inline_analysis=True, **kwargs)


class AntiSpywareProfileResponseFactory(AntiSpywareProfileBaseFactory):
    """Factory for creating AntiSpywareProfileResponseModel instances."""

    class Meta:
        """Meta class that defines the model for AntiSpywareProfileResponseFactory. This factory inherits from AntiSpywareProfileBaseFactory."""

        model = AntiSpywareProfileResponseModel

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
    def from_request(cls, request_model: AntiSpywareProfileCreateModel, **kwargs):
        """Create response factory from request model."""
        data = request_model.model_dump()
        data.pop("id", None)
        return cls(**data, **kwargs)


# ----------------------------------------------------------------------------
# Minimal valid rule and threat exception dict factories
# ----------------------------------------------------------------------------
class AntiSpywareRuleDictFactory:
    """Factory for creating anti-spyware rule dictionaries."""

    @classmethod
    def build_valid(cls, **kwargs):
        """Build valid anti-spyware rule dictionary."""
        return {
            "name": "test-rule",
            "severity": ["critical"],
            "category": "spyware",
            "threat_name": "test-threat",
            "packet_capture": "disable",
            "action": {"alert": {}},
            **kwargs,
        }


class AntiSpywareThreatExceptionDictFactory:
    """Factory for creating anti-spyware threat exception dictionaries."""

    @classmethod
    def build_valid(cls, **kwargs):
        """Build valid anti-spyware threat exception dictionary."""
        return {
            "name": "test-exception",
            "packet_capture": "disable",
            "exempt_ip": [],
            "action": {"alert": {}},
            **kwargs,
        }


# ----------------------------------------------------------------------------
# Model dict factories for Pydantic validation testing
# ----------------------------------------------------------------------------
class AntiSpywareProfileCreateModelFactory(factory.Factory):
    """Factory for creating data dicts for AntiSpywareProfileCreateModel validation testing."""

    class Meta:
        """Meta class that defines the model for AntiSpywareProfileCreateModelFactory."""

        model = dict

    name = factory.Sequence(lambda n: f"anti_spyware_profile_{n}")
    description = factory.LazyFunction(lambda: fake.sentence())
    rules = factory.LazyFunction(lambda: [AntiSpywareRuleDictFactory.build_valid()])
    threat_exceptions = factory.LazyFunction(
        lambda: [AntiSpywareThreatExceptionDictFactory.build_valid()]
    )
    folder = "Texas"
    snippet = None
    device = None

    @classmethod
    def build_valid(cls, **kwargs):
        """Build valid anti-spyware profile."""
        return cls(
            rules=[AntiSpywareRuleDictFactory.build_valid()],
            threat_exceptions=[AntiSpywareThreatExceptionDictFactory.build_valid()],
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


class AntiSpywareProfileUpdateModelFactory(factory.Factory):
    """Factory for creating data dicts for AntiSpywareProfileUpdateModel validation testing."""

    class Meta:
        """Meta class that defines the model for AntiSpywareProfileUpdateModelFactory."""

        model = dict

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"anti_spyware_profile_{n}")
    description = factory.LazyFunction(lambda: fake.sentence())
    rules = factory.LazyFunction(lambda: [AntiSpywareRuleDictFactory.build_valid()])
    threat_exceptions = factory.LazyFunction(
        lambda: [AntiSpywareThreatExceptionDictFactory.build_valid()]
    )
    folder = "Texas"
    snippet = None
    device = None

    @classmethod
    def build_valid(cls, **kwargs):
        """Build valid anti-spyware profile update."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            rules=[AntiSpywareRuleDictFactory.build_valid()],
            threat_exceptions=[AntiSpywareThreatExceptionDictFactory.build_valid()],
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
