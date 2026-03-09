"""Factory definitions for security Authentication Rule objects."""

import uuid

import factory

from scm.models.security.authentication_rules import (
    AuthenticationRuleCreateModel,
    AuthenticationRuleResponseModel,
    AuthenticationRuleUpdateModel,
)


# SDK tests against SCM API
class AuthenticationRuleCreateApiFactory(factory.Factory):
    """Factory for creating AuthenticationRuleCreateModel instances."""

    class Meta:
        """Meta class that defines the model for AuthenticationRuleCreateApiFactory."""

        model = AuthenticationRuleCreateModel

    name = factory.Sequence(lambda n: f"auth_rule_{n}")
    folder = "Shared"
    disabled = False
    description = None
    tag = factory.LazyFunction(list)
    from_ = factory.LazyFunction(lambda: ["any"])
    source = factory.LazyFunction(lambda: ["any"])
    negate_source = False
    source_user = factory.LazyFunction(lambda: ["any"])
    source_hip = factory.LazyFunction(lambda: ["any"])
    to_ = factory.LazyFunction(lambda: ["any"])
    destination = factory.LazyFunction(lambda: ["any"])
    negate_destination = False
    destination_hip = factory.LazyFunction(lambda: ["any"])
    service = factory.LazyFunction(lambda: ["any"])
    category = factory.LazyFunction(lambda: ["any"])
    authentication_enforcement = None
    hip_profiles = None
    group_tag = None
    timeout = None
    log_setting = None
    log_authentication_timeout = False
    rulebase = None

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)


class AuthenticationRuleUpdateApiFactory(factory.Factory):
    """Factory for creating AuthenticationRuleUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for AuthenticationRuleUpdateApiFactory."""

        model = AuthenticationRuleUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"auth_rule_{n}")
    disabled = False
    description = None
    tag = factory.LazyFunction(list)
    from_ = factory.LazyFunction(lambda: ["any"])
    source = factory.LazyFunction(lambda: ["any"])
    negate_source = False
    source_user = factory.LazyFunction(lambda: ["any"])
    source_hip = factory.LazyFunction(lambda: ["any"])
    to_ = factory.LazyFunction(lambda: ["any"])
    destination = factory.LazyFunction(lambda: ["any"])
    negate_destination = False
    destination_hip = factory.LazyFunction(lambda: ["any"])
    service = factory.LazyFunction(lambda: ["any"])
    category = factory.LazyFunction(lambda: ["any"])
    authentication_enforcement = None
    hip_profiles = None
    group_tag = None
    timeout = None
    log_setting = None
    log_authentication_timeout = False
    rulebase = None


class AuthenticationRuleResponseFactory(factory.Factory):
    """Factory for creating AuthenticationRuleResponseModel instances."""

    class Meta:
        """Meta class that defines the model for AuthenticationRuleResponseFactory."""

        model = AuthenticationRuleResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"auth_rule_{n}")
    folder = "Shared"
    disabled = False
    description = None
    tag = factory.LazyFunction(list)
    from_ = factory.LazyFunction(lambda: ["any"])
    source = factory.LazyFunction(lambda: ["any"])
    negate_source = False
    source_user = factory.LazyFunction(lambda: ["any"])
    source_hip = factory.LazyFunction(lambda: ["any"])
    to_ = factory.LazyFunction(lambda: ["any"])
    destination = factory.LazyFunction(lambda: ["any"])
    negate_destination = False
    destination_hip = factory.LazyFunction(lambda: ["any"])
    service = factory.LazyFunction(lambda: ["any"])
    category = factory.LazyFunction(lambda: ["any"])
    authentication_enforcement = None
    hip_profiles = None
    group_tag = None
    timeout = None
    log_setting = None
    log_authentication_timeout = False
    rulebase = None

    @classmethod
    def from_request(cls, request_model: AuthenticationRuleCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class AuthenticationRuleCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for AuthenticationRuleCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"auth_rule_{n}")
    folder = "Shared"

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestAuthRule",
            folder="Shared",
            source=["any"],
            destination=["any"],
            service=["any"],
            category=["any"],
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="TestAuthRule",
            folder="Shared",
            snippet="TestSnippet",
        )

    @classmethod
    def build_with_no_container(cls):
        """Return a data dict without any container."""
        return cls(
            name="TestAuthRule",
            folder=None,
            snippet=None,
            device=None,
        )


class AuthenticationRuleUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for AuthenticationRuleUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"auth_rule_{n}")

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating an authentication rule."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedAuthRule",
            description="Updated authentication rule",
        )
