# tests/factories/security/anti_spyware_profile.py

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
        model = AntiSpywareProfileCreateModel

    folder = "Texas"

    @classmethod
    def with_folder(cls, folder="Texas", **kwargs):
        return cls(folder=folder, snippet=None, device=None, **kwargs)

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        return cls(folder=None, snippet=None, device=device, **kwargs)


class AntiSpywareProfileUpdateApiFactory(AntiSpywareProfileBaseFactory):
    """Factory for creating AntiSpywareProfileUpdateModel instances."""

    class Meta:
        model = AntiSpywareProfileUpdateModel

    id = factory.LazyFunction(lambda: str(uuid4()))

    @classmethod
    def with_folder(cls, folder="Texas", **kwargs):
        return cls(folder=folder, snippet=None, device=None, **kwargs)

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def with_cloud_inline_analysis(cls, **kwargs):
        """Factory method to set cloud_inline_analysis=True for supported models."""
        return cls(cloud_inline_analysis=True, **kwargs)


class AntiSpywareProfileResponseFactory(AntiSpywareProfileBaseFactory):
    """Factory for creating AntiSpywareProfileResponseModel instances."""

    class Meta:
        model = AntiSpywareProfileResponseModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    folder = "Texas"

    @classmethod
    def with_folder(cls, folder="Texas", **kwargs):
        return cls(folder=folder, snippet=None, device=None, **kwargs)

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def from_request(cls, request_model: AntiSpywareProfileCreateModel, **kwargs):
        data = request_model.model_dump()
        data.pop("id", None)
        return cls(**data, **kwargs)


# ----------------------------------------------------------------------------
# Minimal valid rule and threat exception dict factories
# ----------------------------------------------------------------------------
class AntiSpywareRuleDictFactory:
    @classmethod
    def build_valid(cls, **kwargs):
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
    @classmethod
    def build_valid(cls, **kwargs):
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
        return cls(folder="Texas", snippet=None, device=None, **kwargs)

    @classmethod
    def build_with_snippet(cls, **kwargs):
        return cls(folder=None, snippet="TestSnippet", device=None, **kwargs)

    @classmethod
    def build_with_device(cls, **kwargs):
        return cls(folder=None, snippet=None, device="TestDevice", **kwargs)

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        return cls(folder="Texas", snippet="TestSnippet", device=None, **kwargs)

    @classmethod
    def build_with_no_container(cls, **kwargs):
        return cls(folder=None, snippet=None, device=None, **kwargs)


class AntiSpywareProfileUpdateModelFactory(factory.Factory):
    """Factory for creating data dicts for AntiSpywareProfileUpdateModel validation testing."""

    class Meta:
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
        return cls(folder="Texas", snippet=None, device=None, **kwargs)

    @classmethod
    def build_with_snippet(cls, **kwargs):
        return cls(folder=None, snippet="TestSnippet", device=None, **kwargs)

    @classmethod
    def build_with_device(cls, **kwargs):
        return cls(folder=None, snippet=None, device="TestDevice", **kwargs)

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        return cls(folder="Texas", snippet="TestSnippet", device=None, **kwargs)

    @classmethod
    def build_with_no_container(cls, **kwargs):
        return cls(folder=None, snippet=None, device=None, **kwargs)
