"""Factory definitions for mobile agent Auth Settings objects."""

import factory

from scm.models.mobile_agent.auth_settings import (
    AuthSettingsCreateModel,
    AuthSettingsResponseModel,
    AuthSettingsUpdateModel,
)


# SDK tests against SCM API
class AuthSettingsCreateApiFactory(factory.Factory):
    """Factory for creating AuthSettingsCreateModel instances."""

    class Meta:
        """Meta class that defines the model for AuthSettingsCreateApiFactory."""

        model = AuthSettingsCreateModel

    name = factory.Sequence(lambda n: f"auth_settings_{n}")
    authentication_profile = "default-auth-profile"
    os = "Any"
    user_credential_or_client_cert_required = None
    folder = "Mobile Users"


class AuthSettingsUpdateApiFactory(factory.Factory):
    """Factory for creating AuthSettingsUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for AuthSettingsUpdateApiFactory."""

        model = AuthSettingsUpdateModel

    name = factory.Sequence(lambda n: f"auth_settings_{n}")
    authentication_profile = "default-auth-profile"
    os = None
    user_credential_or_client_cert_required = None
    folder = "Mobile Users"


class AuthSettingsResponseFactory(factory.Factory):
    """Factory for creating AuthSettingsResponseModel instances."""

    class Meta:
        """Meta class that defines the model for AuthSettingsResponseFactory."""

        model = AuthSettingsResponseModel

    name = factory.Sequence(lambda n: f"auth_settings_{n}")
    authentication_profile = "default-auth-profile"
    os = "Any"
    user_credential_or_client_cert_required = None
    folder = "Mobile Users"

    @classmethod
    def from_request(cls, request_model: AuthSettingsCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class AuthSettingsCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for AuthSettingsCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"auth_settings_{n}")
    authentication_profile = "default-auth-profile"
    folder = "Mobile Users"

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestAuthSettings",
            authentication_profile="test-auth-profile",
            os="Any",
            folder="Mobile Users",
        )

    @classmethod
    def build_with_no_container(cls):
        """Return a data dict without any container."""
        return cls(
            name="TestAuthSettings",
            authentication_profile="test-auth-profile",
            folder=None,
        )


class AuthSettingsUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for AuthSettingsUpdateModel validation testing."""

    name = factory.Sequence(lambda n: f"auth_settings_{n}")
    authentication_profile = "default-auth-profile"

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating auth settings."""
        return cls(
            name="UpdatedAuthSettings",
            authentication_profile="updated-auth-profile",
            folder="Mobile Users",
        )
