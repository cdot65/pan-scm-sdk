# tests/factories/security/app_override_rule.py

"""Factory definitions for app override rule objects."""

import uuid

import factory

from scm.models.security.app_override_rules import (
    AppOverrideRuleCreateModel,
    AppOverrideRuleMoveDestination,
    AppOverrideRuleMoveModel,
    AppOverrideRuleProtocol,
    AppOverrideRuleResponseModel,
    AppOverrideRuleRulebase,
    AppOverrideRuleUpdateModel,
)


# SDK tests against SCM API
class AppOverrideRuleCreateApiFactory(factory.Factory):
    """Factory for creating AppOverrideRuleCreateModel instances."""

    class Meta:  # noqa: D106
        model = AppOverrideRuleCreateModel

    name = factory.Sequence(lambda n: f"app_override_rule_{n}")
    description = factory.Faker("sentence")
    folder = "Texas"
    application = "web-browsing"
    port = "80"
    protocol = AppOverrideRuleProtocol.tcp

    # Default lists
    from_ = ["any"]
    source = ["any"]
    to_ = ["any"]
    destination = ["any"]

    # Boolean flags
    disabled = False
    negate_source = False
    negate_destination = False

    # Optional fields
    tag = ["test-tag"]
    rulebase = AppOverrideRuleRulebase.PRE

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def with_custom_zones(cls, from_zones, to_zones, **kwargs):
        """Create an instance with custom security zones."""
        return cls(from_=from_zones, to_=to_zones, **kwargs)

    @classmethod
    def with_post_rulebase(cls, **kwargs):
        """Create an instance in the post rulebase."""
        return cls(rulebase=AppOverrideRuleRulebase.POST, **kwargs)


class AppOverrideRuleUpdateApiFactory(factory.Factory):
    """Factory for creating AppOverrideRuleUpdateModel instances."""

    class Meta:  # noqa: D106
        model = AppOverrideRuleUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"app_override_rule_{n}")
    description = factory.Faker("sentence")
    application = "web-browsing"
    port = "80"
    protocol = AppOverrideRuleProtocol.tcp
    tag = ["updated-tag"]

    # Default lists
    from_ = ["any"]
    source = ["any"]
    to_ = ["any"]
    destination = ["any"]

    # Boolean flags with defaults
    disabled = False
    negate_source = False
    negate_destination = False

    # Optional fields
    rulebase = None

    @classmethod
    def with_application_update(cls, application="ssl", **kwargs):
        """Create an instance updating only the application."""
        return cls(application=application, **kwargs)

    @classmethod
    def with_zones_update(cls, from_zones, to_zones, **kwargs):
        """Create an instance updating security zones."""
        return cls(from_=from_zones, to_=to_zones, **kwargs)


class AppOverrideRuleResponseFactory(factory.Factory):
    """Factory for creating AppOverrideRuleResponseModel instances."""

    class Meta:  # noqa: D106
        model = AppOverrideRuleResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"app_override_rule_{n}")
    description = factory.Faker("sentence")
    folder = "Texas"
    application = "web-browsing"
    port = "80"
    protocol = AppOverrideRuleProtocol.tcp
    tag = ["response-tag"]

    # Default lists
    from_ = ["any"]
    source = ["any"]
    to_ = ["any"]
    destination = ["any"]

    # Boolean flags
    disabled = False
    negate_source = False
    negate_destination = False

    # Set device to None by default
    device = None

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """Create an instance with device container."""
        if isinstance(device, dict) and device != {}:
            raise ValueError("If device is a dictionary, it must be empty")
        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def with_empty_dict_device(cls, **kwargs):
        """Create an instance with an empty dictionary as device."""
        return cls(folder=None, snippet=None, device={}, **kwargs)

    @classmethod
    def from_request(cls, request_model: AppOverrideRuleCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


class AppOverrideRuleMoveApiFactory(factory.Factory):
    """Factory for creating AppOverrideRuleMoveModel instances."""

    class Meta:  # noqa: D106
        model = AppOverrideRuleMoveModel

    destination = AppOverrideRuleMoveDestination.TOP
    rulebase = AppOverrideRuleRulebase.PRE
    destination_rule = None

    @classmethod
    def before_rule(cls, dest_rule=None, **kwargs):
        """Create a move configuration for placing before another rule."""
        if dest_rule is None:
            dest_rule = str(uuid.uuid4())
        return cls(
            destination=AppOverrideRuleMoveDestination.BEFORE,
            destination_rule=dest_rule,
            **kwargs,
        )

    @classmethod
    def after_rule(cls, dest_rule=None, **kwargs):
        """Create a move configuration for placing after another rule."""
        if dest_rule is None:
            dest_rule = str(uuid.uuid4())
        return cls(
            destination=AppOverrideRuleMoveDestination.AFTER,
            destination_rule=dest_rule,
            **kwargs,
        )


# Pydantic modeling tests
class AppOverrideRuleCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for AppOverrideRuleCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"app_override_rule_{n}")
    description = factory.Faker("sentence")
    folder = "Texas"
    application = "web-browsing"
    port = "80"
    protocol = "tcp"
    tag = ["test-tag"]

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestRule",
            folder="Texas",
            application="web-browsing",
            port="80",
            protocol="tcp",
            from_=["trust"],
            to_=["untrust"],
            source=["192.168.1.0/24"],
            destination=["any"],
        )

    @classmethod
    def build_with_invalid_name(cls):
        """Return a data dict with invalid name pattern."""
        return cls(
            name="@invalid-name#",
            folder="Texas",
            application="web-browsing",
            port="80",
            protocol="tcp",
        )

    @classmethod
    def build_with_duplicate_items(cls):
        """Return a data dict with duplicate list items."""
        return cls(
            name="TestRule",
            folder="Texas",
            application="web-browsing",
            port="80",
            protocol="tcp",
            source=["any", "any"],
            tag=["tag1", "tag1"],
        )


class AppOverrideRuleUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for AppOverrideRuleUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"app_override_rule_{n}")
    description = factory.Faker("sentence")
    application = "web-browsing"
    port = "80"
    protocol = "tcp"

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating an app override rule."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedRule",
            application="ssl",
            port="443",
            protocol="tcp",
            source=["updated-source"],
            destination=["updated-dest"],
        )

    @classmethod
    def build_with_invalid_fields(cls):
        """Return a data dict with multiple invalid fields."""
        return cls(
            id="invalid-uuid",
            name="@invalid-name",
            application="web-browsing",
            port="80",
            protocol="tcp",
            source=["source", "source"],  # Duplicate items
        )

    @classmethod
    def build_minimal_update(cls):
        """Return a data dict with minimal valid update fields."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="MinimalUpdate",
            application="web-browsing",
            port="80",
            protocol="tcp",
            description="Updated description",
        )


class AppOverrideRuleMoveModelFactory(factory.DictFactory):
    """Factory for creating data dicts for AppOverrideRuleMoveModel validation testing."""

    destination = "top"
    rulebase = "pre"

    @classmethod
    def build_valid_before(cls):
        """Return a valid data dict for before move operation."""
        return cls(
            destination="before",
            destination_rule="987fcdeb-54ba-3210-9876-fedcba098765",
            rulebase="pre",
        )

    @classmethod
    def build_with_invalid_destination(cls):
        """Return a data dict with invalid destination."""
        return cls(
            destination="invalid",
            rulebase="pre",
        )

    @classmethod
    def build_missing_destination_rule(cls):
        """Return a data dict missing required destination_rule."""
        return cls(
            destination="before",
            rulebase="pre",
        )
