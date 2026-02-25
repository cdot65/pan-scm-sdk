# tests/factories/identity/saml_server_profile.py

"""Factory definitions for SAML server profile objects."""

from uuid import uuid4

import factory  # type: ignore
from faker import Faker

from scm.models.identity.saml_server_profiles import (
    SamlServerProfileCreateModel,
    SamlServerProfileResponseModel,
    SamlServerProfileUpdateModel,
)

fake = Faker()


# ----------------------------------------------------------------------------
# API Factories for Create, Update, Response
# ----------------------------------------------------------------------------
class SamlServerProfileCreateApiFactory(factory.Factory):
    """Factory for creating SamlServerProfileCreateModel instances."""

    class Meta:
        """Meta class that defines the model for SamlServerProfileCreateApiFactory."""

        model = SamlServerProfileCreateModel

    name = factory.Sequence(lambda n: f"saml_server_profile_{n}")
    entity_id = "https://idp.example.com/saml"
    certificate = "test-cert"
    sso_url = "https://idp.example.com/sso"
    sso_bindings = "post"
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


class SamlServerProfileUpdateApiFactory(factory.Factory):
    """Factory for creating SamlServerProfileUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for SamlServerProfileUpdateApiFactory."""

        model = SamlServerProfileUpdateModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    name = factory.Sequence(lambda n: f"saml_server_profile_{n}")
    entity_id = "https://idp.example.com/saml"
    certificate = "test-cert"
    sso_url = "https://idp.example.com/sso"
    sso_bindings = "post"
    folder = None
    snippet = None
    device = None


class SamlServerProfileResponseFactory(factory.Factory):
    """Factory for creating SamlServerProfileResponseModel instances."""

    class Meta:
        """Meta class that defines the model for SamlServerProfileResponseFactory."""

        model = SamlServerProfileResponseModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    name = factory.Sequence(lambda n: f"saml_server_profile_{n}")
    entity_id = "https://idp.example.com/saml"
    certificate = "test-cert"
    sso_url = "https://idp.example.com/sso"
    sso_bindings = "post"
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
class SamlServerProfileCreateModelFactory(factory.Factory):
    """Factory for creating data dicts for SamlServerProfileCreateModel validation testing."""

    class Meta:
        """Meta class that defines the model for SamlServerProfileCreateModelFactory."""

        model = dict

    name = factory.Sequence(lambda n: f"saml_server_profile_{n}")
    entity_id = "https://idp.example.com/saml"
    certificate = "test-cert"
    sso_url = "https://idp.example.com/sso"
    sso_bindings = "post"
    folder = "Texas"
    snippet = None
    device = None

    @classmethod
    def build_valid(cls, **kwargs):
        """Build valid SAML server profile data."""
        return cls(folder="Texas", snippet=None, device=None, **kwargs)

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Build SAML server profile with multiple containers."""
        return cls(folder="Texas", snippet="TestSnippet", device=None, **kwargs)

    @classmethod
    def build_with_no_container(cls, **kwargs):
        """Build SAML server profile with no container."""
        return cls(folder=None, snippet=None, device=None, **kwargs)


class SamlServerProfileUpdateModelFactory(factory.Factory):
    """Factory for creating data dicts for SamlServerProfileUpdateModel validation testing."""

    class Meta:
        """Meta class that defines the model for SamlServerProfileUpdateModelFactory."""

        model = dict

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"saml_server_profile_{n}")
    entity_id = "https://idp.example.com/saml"
    certificate = "test-cert"
    sso_url = "https://idp.example.com/sso"
    sso_bindings = "post"
    folder = None
    snippet = None
    device = None

    @classmethod
    def build_valid(cls, **kwargs):
        """Build valid SAML server profile data."""
        return cls(id="123e4567-e89b-12d3-a456-426655440000", **kwargs)
