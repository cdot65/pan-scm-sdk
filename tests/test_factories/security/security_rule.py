from typing import Dict, Union
import uuid

import factory

from scm.models.security.security_rules import (
    SecurityRuleAction,
    SecurityRuleCreateModel,
    SecurityRuleMoveDestination,
    SecurityRuleMoveModel,
    SecurityRuleProfileSetting,
    SecurityRuleResponseModel,
    SecurityRuleRulebase,
    SecurityRuleUpdateModel,
)


# Component factories
class SecurityRuleProfileSettingFactory(factory.Factory):
    """Factory for creating ProfileSetting instances."""

    class Meta:
        model = SecurityRuleProfileSetting

    group = ["best-practice"]

    @classmethod
    def with_groups(cls, groups: list[str], **kwargs):
        """Create a profile setting with specific groups."""
        return cls(group=groups, **kwargs)

    @classmethod
    def with_empty_group(cls, **kwargs):
        """Create a profile setting with empty group list."""
        return cls(group=[], **kwargs)


# SDK tests against SCM API
class SecurityRuleCreateApiFactory(factory.Factory):
    """Factory for creating SecurityRuleCreateModel instances."""

    class Meta:
        model = SecurityRuleCreateModel

    name = factory.Sequence(lambda n: f"security_rule_{n}")
    description = factory.Faker("sentence")
    folder = "Texas"
    disabled = False
    tag = ["test-tag", "environment-prod"]

    # Default lists
    from_ = ["any"]
    source = ["any"]
    source_user = ["any"]
    source_hip = ["any"]
    to_ = ["any"]
    destination = ["any"]
    destination_hip = ["any"]
    application = ["any"]
    service = ["any"]
    category = ["any"]

    # Boolean flags
    negate_source = False
    negate_destination = False
    log_start = False
    log_end = True

    # Optional fields
    action = SecurityRuleAction.allow
    profile_setting = factory.SubFactory(SecurityRuleProfileSettingFactory)
    log_setting = "default-logging"
    schedule = None
    rulebase = SecurityRuleRulebase.PRE

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def with_custom_zones(cls, from_zones: list[str], to_zones: list[str], **kwargs):
        """Create an instance with custom security zones."""
        return cls(from_=from_zones, to_=to_zones, **kwargs)

    @classmethod
    def with_post_rulebase(cls, **kwargs):
        """Create an instance in the post rulebase."""
        return cls(rulebase=SecurityRuleRulebase.POST, **kwargs)


class SecurityRuleUpdateApiFactory(factory.Factory):
    """Factory for creating SecurityRuleUpdateModel instances."""

    class Meta:
        model = SecurityRuleUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"security_rule_{n}")
    description = factory.Faker("sentence")
    tag = ["updated-tag"]

    # Default lists - change from None to empty lists
    from_ = factory.List([])
    source = factory.List([])
    source_user = factory.List([])
    source_hip = factory.List([])
    to_ = factory.List([])
    destination = factory.List([])
    destination_hip = factory.List([])
    application = factory.List([])
    service = factory.List([])
    category = factory.List([])

    # Boolean flags with defaults
    disabled = False
    negate_source = False
    negate_destination = False
    log_start = False
    log_end = True

    # Optional fields
    action = SecurityRuleAction.allow
    profile_setting = None
    log_setting = None
    schedule = None
    rulebase = None

    @classmethod
    def with_action_update(cls, action: SecurityRuleAction = SecurityRuleAction.deny, **kwargs):
        """Create an instance updating only the action."""
        return cls(action=action, **kwargs)

    @classmethod
    def with_zones_update(cls, from_zones: list[str], to_zones: list[str], **kwargs):
        """Create an instance updating security zones."""
        return cls(from_=from_zones, to_=to_zones, **kwargs)


class SecurityRuleResponseFactory(factory.Factory):
    """Factory for creating SecurityRuleResponseModel instances."""

    class Meta:
        model = SecurityRuleResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"security_rule_{n}")
    description = factory.Faker("sentence")
    folder = "Texas"
    tag = ["response-tag"]

    # Default lists
    from_ = ["any"]
    source = ["any"]
    source_user = ["any"]
    source_hip = ["any"]
    to_ = ["any"]
    destination = ["any"]
    destination_hip = ["any"]
    application = ["any"]
    service = ["any"]
    category = ["any"]

    # Boolean flags
    disabled = False
    negate_source = False
    negate_destination = False
    log_start = False
    log_end = True

    # Optional fields
    action = SecurityRuleAction.allow
    profile_setting = factory.SubFactory(SecurityRuleProfileSettingFactory)
    log_setting = "default-logging"
    schedule = None

    # Set device to None by default (will be overridden by with_device)
    device = None

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: Union[str, Dict] = "TestDevice", **kwargs):
        """
        Create an instance with device container.

        Args:
            device: Either a string device name or an empty dictionary
            **kwargs: Additional fields to override

        Returns:
            An instance of SecurityRuleResponseModel
        """
        # Validate the device parameter
        if isinstance(device, dict) and device != {}:
            raise ValueError("If device is a dictionary, it must be empty")

        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def with_empty_dict_device(cls, **kwargs):
        """
        Create an instance with an empty dictionary as device.

        Returns:
            An instance of SecurityRuleResponseModel with device={}
        """
        return cls(folder=None, snippet=None, device={}, **kwargs)

    @classmethod
    def from_request(cls, request_model: SecurityRuleCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


class SecurityRuleMoveApiFactory(factory.Factory):
    """Factory for creating SecurityRuleMoveModel instances."""

    class Meta:
        model = SecurityRuleMoveModel

    destination = SecurityRuleMoveDestination.TOP
    rulebase = SecurityRuleRulebase.PRE
    destination_rule = None

    @classmethod
    def before_rule(cls, dest_rule=None, **kwargs):
        """Create a move configuration for placing before another rule."""
        if dest_rule is None:
            dest_rule = str(uuid.uuid4())
        return cls(
            destination=SecurityRuleMoveDestination.BEFORE,
            destination_rule=dest_rule,
            **kwargs,
        )

    @classmethod
    def after_rule(cls, dest_rule=None, **kwargs):
        """Create a move configuration for placing after another rule."""
        if dest_rule is None:
            dest_rule = str(uuid.uuid4())
        return cls(
            destination=SecurityRuleMoveDestination.AFTER,
            destination_rule=dest_rule,
            **kwargs,
        )


# Pydantic modeling tests
class SecurityRuleCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for SecurityRuleCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"security_rule_{n}")
    description = factory.Faker("sentence")
    folder = "Texas"
    tag = ["test-tag"]
    action = "allow"

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestRule",
            folder="Texas",
            action="allow",
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
            action="allow",
        )

    @classmethod
    def build_with_invalid_action(cls):
        """Return a data dict with invalid action."""
        return cls(
            name="TestRule",
            folder="Texas",
            action="invalid-action",
        )

    @classmethod
    def build_with_duplicate_items(cls):
        """Return a data dict with duplicate list items."""
        return cls(
            name="TestRule",
            folder="Texas",
            source=["any", "any"],
            tag=["tag1", "tag1"],
        )


class SecurityRuleUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for SecurityRuleUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"security_rule_{n}")
    description = factory.Faker("sentence")

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating a security rule."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedRule",
            action="deny",
            source=["updated-source"],
            destination=["updated-dest"],
        )

    @classmethod
    def build_with_invalid_fields(cls):
        """Return a data dict with multiple invalid fields."""
        return cls(
            id="invalid-uuid",
            name="@invalid-name",
            action="invalid-action",
            source=["source", "source"],  # Duplicate items
        )

    @classmethod
    def build_minimal_update(cls):
        """Return a data dict with minimal valid update fields."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            description="Updated description",
        )


class SecurityRuleMoveModelFactory(factory.DictFactory):
    """Factory for creating data dicts for SecurityRuleMoveModel validation testing."""

    source_rule = factory.LazyFunction(lambda: str(uuid.uuid4()))
    destination = "top"
    rulebase = "pre"

    @classmethod
    def build_valid_before(cls):
        """Return a valid data dict for before move operation."""
        return cls(
            source_rule="123e4567-e89b-12d3-a456-426655440000",
            destination="before",
            destination_rule="987fcdeb-54ba-3210-9876-fedcba098765",
            rulebase="pre",
        )

    @classmethod
    def build_with_invalid_destination(cls):
        """Return a data dict with invalid destination."""
        return cls(
            source_rule="123e4567-e89b-12d3-a456-426655440000",
            destination="invalid",
            rulebase="pre",
        )

    @classmethod
    def build_missing_destination_rule(cls):
        """Return a data dict missing required destination_rule."""
        return cls(
            source_rule="123e4567-e89b-12d3-a456-426655440000",
            destination="before",
            rulebase="pre",
        )
