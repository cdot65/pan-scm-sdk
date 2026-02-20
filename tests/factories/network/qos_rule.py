"""Factory definitions for network QoS Rule objects."""

import uuid

import factory

from scm.models.network.qos_rule import (
    QosMoveDestination,
    QosRulebase,
    QosRuleCreateModel,
    QosRuleMoveModel,
    QosRuleResponseModel,
    QosRuleUpdateModel,
)


# SDK tests against SCM API
class QosRuleCreateApiFactory(factory.Factory):
    """Factory for creating QosRuleCreateModel instances."""

    class Meta:
        """Meta class that defines the model for QosRuleCreateApiFactory."""

        model = QosRuleCreateModel

    name = factory.Sequence(lambda n: f"qos_rule_{n}")
    folder = "Shared"
    description = factory.Faker("sentence")
    action = None
    schedule = None
    dscp_tos = None

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def with_action(cls, **kwargs):
        """Create an instance with action configuration."""
        return cls(
            action={"class": "class1"},
            **kwargs,
        )


class QosRuleUpdateApiFactory(factory.Factory):
    """Factory for creating QosRuleUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for QosRuleUpdateApiFactory."""

        model = QosRuleUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"qos_rule_{n}")
    description = factory.Faker("sentence")
    action = None
    schedule = None
    dscp_tos = None


class QosRuleResponseFactory(factory.Factory):
    """Factory for creating QosRuleResponseModel instances."""

    class Meta:
        """Meta class that defines the model for QosRuleResponseFactory."""

        model = QosRuleResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"qos_rule_{n}")
    folder = "Shared"
    description = factory.Faker("sentence")
    action = None
    schedule = None
    dscp_tos = None


class QosRuleMoveApiFactory(factory.Factory):
    """Factory for creating QosRuleMoveModel instances."""

    class Meta:
        """Meta class that defines the model for QosRuleMoveApiFactory."""

        model = QosRuleMoveModel

    destination = QosMoveDestination.TOP
    rulebase = QosRulebase.PRE
    destination_rule = None

    @classmethod
    def before_rule(cls, dest_rule=None, **kwargs):
        """Create a move configuration for placing before another rule."""
        if dest_rule is None:
            dest_rule = str(uuid.uuid4())
        return cls(
            destination=QosMoveDestination.BEFORE,
            destination_rule=dest_rule,
            **kwargs,
        )

    @classmethod
    def after_rule(cls, dest_rule=None, **kwargs):
        """Create a move configuration for placing after another rule."""
        if dest_rule is None:
            dest_rule = str(uuid.uuid4())
        return cls(
            destination=QosMoveDestination.AFTER,
            destination_rule=dest_rule,
            **kwargs,
        )


# Pydantic modeling tests
class QosRuleCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for QosRuleCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"qos_rule_{n}")
    folder = "Shared"

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestQosRule",
            folder="Shared",
            description="Test QoS rule",
            action={"class": "class1"},
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="TestQosRule",
            folder="Shared",
            snippet="TestSnippet",
        )

    @classmethod
    def build_with_no_container(cls):
        """Return a data dict without any container."""
        return cls(
            name="TestQosRule",
            folder=None,
            snippet=None,
            device=None,
        )


class QosRuleUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for QosRuleUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"qos_rule_{n}")

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating a QoS rule."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedQosRule",
            description="Updated QoS rule description",
        )


class QosRuleMoveModelFactory(factory.DictFactory):
    """Factory for creating data dicts for QosRuleMoveModel validation testing."""

    destination = QosMoveDestination.TOP
    rulebase = QosRulebase.PRE

    @classmethod
    def build_valid_before(cls):
        """Return a valid data dict for before move operation."""
        return cls(
            destination=QosMoveDestination.BEFORE,
            destination_rule="987fcdeb-54ba-3210-9876-fedcba098765",
            rulebase=QosRulebase.PRE,
        )

    @classmethod
    def build_with_invalid_destination(cls):
        """Return a data dict with invalid destination."""
        return cls(
            destination="invalid",
            rulebase=QosRulebase.PRE,
        )

    @classmethod
    def build_missing_destination_rule(cls):
        """Return a data dict missing required destination_rule."""
        return cls(
            destination=QosMoveDestination.BEFORE,
            rulebase=QosRulebase.PRE,
        )
