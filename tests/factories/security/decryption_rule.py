"""Factory definitions for decryption rule objects."""

from typing import Dict, Union
import uuid

import factory

from scm.models.security.decryption_rules import (
    DecryptionRuleAction,
    DecryptionRuleCreateModel,
    DecryptionRuleMoveDestination,
    DecryptionRuleMoveModel,
    DecryptionRuleResponseModel,
    DecryptionRuleRulebase,
    DecryptionRuleUpdateModel,
)


# SDK tests against SCM API
class DecryptionRuleCreateApiFactory(factory.Factory):
    """Factory for creating DecryptionRuleCreateModel instances."""

    class Meta:  # noqa: D106
        model = DecryptionRuleCreateModel

    name = factory.Sequence(lambda n: f"decryption_rule_{n}")
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
    service = ["any"]
    category = ["any"]

    # Boolean flags
    negate_source = False
    negate_destination = False

    # Optional fields
    action = DecryptionRuleAction.no_decrypt
    log_setting = "default-logging"
    rulebase = DecryptionRuleRulebase.PRE

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
        return cls(rulebase=DecryptionRuleRulebase.POST, **kwargs)


class DecryptionRuleUpdateApiFactory(factory.Factory):
    """Factory for creating DecryptionRuleUpdateModel instances."""

    class Meta:  # noqa: D106
        model = DecryptionRuleUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"decryption_rule_{n}")
    description = factory.Faker("sentence")
    tag = ["updated-tag"]

    # Default lists
    from_ = factory.List([])
    source = factory.List([])
    source_user = factory.List([])
    source_hip = factory.List([])
    to_ = factory.List([])
    destination = factory.List([])
    destination_hip = factory.List([])
    service = factory.List([])
    category = factory.List([])

    # Boolean flags with defaults
    disabled = False
    negate_source = False
    negate_destination = False

    # Optional fields
    action = DecryptionRuleAction.no_decrypt
    log_setting = None
    rulebase = None

    @classmethod
    def with_action_update(
        cls, action: DecryptionRuleAction = DecryptionRuleAction.decrypt, **kwargs
    ):
        """Create an instance updating only the action."""
        return cls(action=action, **kwargs)

    @classmethod
    def with_zones_update(cls, from_zones: list[str], to_zones: list[str], **kwargs):
        """Create an instance updating security zones."""
        return cls(from_=from_zones, to_=to_zones, **kwargs)


class DecryptionRuleResponseFactory(factory.Factory):
    """Factory for creating DecryptionRuleResponseModel instances."""

    class Meta:  # noqa: D106
        model = DecryptionRuleResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"decryption_rule_{n}")
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
    service = ["any"]
    category = ["any"]

    # Boolean flags
    disabled = False
    negate_source = False
    negate_destination = False

    # Optional fields
    action = DecryptionRuleAction.no_decrypt
    log_setting = "default-logging"

    # Set device to None by default
    device = None

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: Union[str, Dict] = "TestDevice", **kwargs):
        """Create an instance with device container."""
        if isinstance(device, dict) and device != {}:
            raise ValueError("If device is a dictionary, it must be empty")
        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def with_empty_dict_device(cls, **kwargs):
        """Create an instance with an empty dictionary as device."""
        return cls(folder=None, snippet=None, device={}, **kwargs)

    @classmethod
    def from_request(cls, request_model: DecryptionRuleCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


class DecryptionRuleMoveApiFactory(factory.Factory):
    """Factory for creating DecryptionRuleMoveModel instances."""

    class Meta:  # noqa: D106
        model = DecryptionRuleMoveModel

    destination = DecryptionRuleMoveDestination.TOP
    rulebase = DecryptionRuleRulebase.PRE
    destination_rule = None

    @classmethod
    def before_rule(cls, dest_rule=None, **kwargs):
        """Create a move configuration for placing before another rule."""
        if dest_rule is None:
            dest_rule = str(uuid.uuid4())
        return cls(
            destination=DecryptionRuleMoveDestination.BEFORE,
            destination_rule=dest_rule,
            **kwargs,
        )

    @classmethod
    def after_rule(cls, dest_rule=None, **kwargs):
        """Create a move configuration for placing after another rule."""
        if dest_rule is None:
            dest_rule = str(uuid.uuid4())
        return cls(
            destination=DecryptionRuleMoveDestination.AFTER,
            destination_rule=dest_rule,
            **kwargs,
        )


# Pydantic modeling tests
class DecryptionRuleCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for DecryptionRuleCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"decryption_rule_{n}")
    description = factory.Faker("sentence")
    folder = "Texas"
    tag = ["test-tag"]
    action = "no-decrypt"

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestRule",
            folder="Texas",
            action="no-decrypt",
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
            action="no-decrypt",
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
            action="no-decrypt",
            source=["any", "any"],
            tag=["tag1", "tag1"],
        )


class DecryptionRuleUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for DecryptionRuleUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"decryption_rule_{n}")
    description = factory.Faker("sentence")

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating a decryption rule."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedRule",
            action="decrypt",
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


class DecryptionRuleMoveModelFactory(factory.DictFactory):
    """Factory for creating data dicts for DecryptionRuleMoveModel validation testing."""

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
