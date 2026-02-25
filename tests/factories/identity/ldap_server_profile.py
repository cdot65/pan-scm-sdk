# tests/factories/identity/ldap_server_profile.py

"""Factory definitions for LDAP server profile objects."""

from uuid import uuid4

import factory  # type: ignore
from faker import Faker

from scm.models.identity.ldap_server_profiles import (
    LdapServerProfileCreateModel,
    LdapServerProfileResponseModel,
    LdapServerProfileUpdateModel,
)

fake = Faker()


# ----------------------------------------------------------------------------
# API Factories for Create, Update, Response
# ----------------------------------------------------------------------------
class LdapServerProfileCreateApiFactory(factory.Factory):
    """Factory for creating LdapServerProfileCreateModel instances."""

    class Meta:
        """Meta class that defines the model for LdapServerProfileCreateApiFactory."""

        model = LdapServerProfileCreateModel

    name = factory.Sequence(lambda n: f"ldap_server_profile_{n}")
    server = factory.LazyFunction(lambda: [{"name": "ldap1", "address": "10.0.0.1", "port": 389}])
    base = "dc=example,dc=com"
    ldap_type = "active-directory"
    ssl = False
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


class LdapServerProfileUpdateApiFactory(factory.Factory):
    """Factory for creating LdapServerProfileUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for LdapServerProfileUpdateApiFactory."""

        model = LdapServerProfileUpdateModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    name = factory.Sequence(lambda n: f"ldap_server_profile_{n}")
    server = factory.LazyFunction(lambda: [{"name": "ldap1", "address": "10.0.0.1", "port": 389}])
    base = "dc=example,dc=com"
    ldap_type = "active-directory"
    ssl = False
    folder = None
    snippet = None
    device = None


class LdapServerProfileResponseFactory(factory.Factory):
    """Factory for creating LdapServerProfileResponseModel instances."""

    class Meta:
        """Meta class that defines the model for LdapServerProfileResponseFactory."""

        model = LdapServerProfileResponseModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    name = factory.Sequence(lambda n: f"ldap_server_profile_{n}")
    server = factory.LazyFunction(lambda: [{"name": "ldap1", "address": "10.0.0.1", "port": 389}])
    base = "dc=example,dc=com"
    ldap_type = "active-directory"
    ssl = False
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
class LdapServerProfileCreateModelFactory(factory.Factory):
    """Factory for creating data dicts for LdapServerProfileCreateModel validation testing."""

    class Meta:
        """Meta class that defines the model for LdapServerProfileCreateModelFactory."""

        model = dict

    name = factory.Sequence(lambda n: f"ldap_server_profile_{n}")
    server = factory.LazyFunction(lambda: [{"name": "ldap1", "address": "10.0.0.1", "port": 389}])
    base = "dc=example,dc=com"
    ldap_type = "active-directory"
    ssl = False
    folder = "Texas"
    snippet = None
    device = None

    @classmethod
    def build_valid(cls, **kwargs):
        """Build valid LDAP server profile data."""
        return cls(folder="Texas", snippet=None, device=None, **kwargs)

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Build LDAP server profile with multiple containers."""
        return cls(folder="Texas", snippet="TestSnippet", device=None, **kwargs)

    @classmethod
    def build_with_no_container(cls, **kwargs):
        """Build LDAP server profile with no container."""
        return cls(folder=None, snippet=None, device=None, **kwargs)


class LdapServerProfileUpdateModelFactory(factory.Factory):
    """Factory for creating data dicts for LdapServerProfileUpdateModel validation testing."""

    class Meta:
        """Meta class that defines the model for LdapServerProfileUpdateModelFactory."""

        model = dict

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"ldap_server_profile_{n}")
    server = factory.LazyFunction(lambda: [{"name": "ldap1", "address": "10.0.0.1", "port": 389}])
    base = "dc=example,dc=com"
    ldap_type = "active-directory"
    ssl = False
    folder = None
    snippet = None
    device = None

    @classmethod
    def build_valid(cls, **kwargs):
        """Build valid LDAP server profile data."""
        return cls(id="123e4567-e89b-12d3-a456-426655440000", **kwargs)
