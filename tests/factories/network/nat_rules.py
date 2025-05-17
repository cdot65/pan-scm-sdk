"""Factory definitions for network NAT rule objects."""

from typing import List
import uuid

import factory

from scm.models.network.nat_rules import (
    InterfaceAddress,
    NatMoveDestination,
    NatRulebase,
    NatRuleCreateModel,
    NatRuleMoveModel,
    NatRuleResponseModel,
    NatRuleUpdateModel,
    NatType,
    SourceTranslation,
)


# Sub factories
class InterfaceAddressFactory(factory.Factory):
    """Factory for creating InterfaceAddress instances."""

    class Meta:
        model = InterfaceAddress

    interface = "ethernet1/1"
    ip = "192.168.1.1"
    floating_ip = None

    @classmethod
    def with_floating_ip(cls, floating_ip: str = "192.168.1.100", **kwargs):
        """Create an instance with a floating IP."""
        return cls(floating_ip=floating_ip, **kwargs)


class SourceTranslationFactory(factory.Factory):
    """Factory for creating SourceTranslation instances."""

    class Meta:
        model = SourceTranslation

    # Need to explicitly set one of the three source translation types
    dynamic_ip_and_port = {
        "type": "dynamic_ip_and_port",
        "translated_address": ["10.0.0.1"],
    }
    dynamic_ip = None
    static_ip = None

    # These fields aren't direct attributes of SourceTranslation
    # but can be used in other contexts
    bi_directional = False
    translated_address = ["10.0.0.1"]  # Used by specific translation types
    fallback = None
    disabled = False
    nat_type = "ipv4"
    source = ["any"]
    destination = ["any"]

    @classmethod
    def with_static_ip(cls, **kwargs):
        """Create an instance with static IP translation."""
        static_ip = {
            "translated_address": "192.168.1.100",
            "bi_directional": "yes" if kwargs.pop("bi_directional", False) else "no",
        }
        return cls(dynamic_ip_and_port=None, dynamic_ip=None, static_ip=static_ip, **kwargs)

    @classmethod
    def with_dynamic_ip(cls, **kwargs):
        """Create an instance with dynamic IP translation."""
        dynamic_ip = {
            "translated_address": ["192.168.1.100", "192.168.1.101"],
            "fallback_type": None,
        }
        return cls(dynamic_ip_and_port=None, dynamic_ip=dynamic_ip, static_ip=None, **kwargs)

    @classmethod
    def with_dynamic_ip_and_port(cls, **kwargs):
        """Create an instance with dynamic IP and port translation."""
        dynamic_ip_and_port = {
            "type": "dynamic_ip_and_port",
            "translated_address": kwargs.pop("translated_address", ["192.168.1.100"]),
        }
        return cls(
            dynamic_ip_and_port=dynamic_ip_and_port,
            dynamic_ip=None,
            static_ip=None,
            **kwargs,
        )

    @classmethod
    def with_bi_directional(cls, **kwargs):
        """Create an instance with bi-directional translation enabled."""
        return cls.with_static_ip(bi_directional=True, **kwargs)


# SDK tests against SCM API
class NatRuleCreateApiFactory(factory.Factory):
    """Factory for creating NatRuleCreateModel instances."""

    class Meta:
        model = NatRuleCreateModel

    name = factory.Sequence(lambda n: f"nat_rule_{n}")
    description = factory.Faker("sentence")
    tag = ["Automation", "Decrypted"]  # Example tags (tags are no longer restricted)
    disabled = False
    nat_type = NatType.ipv4
    from_ = ["any"]
    to_ = ["any"]
    source = ["any"]
    destination = ["any"]
    service = None
    source_translation = None
    folder = "Shared"

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def with_source_translation(cls, **kwargs):
        """Create an instance with source translation."""
        return cls(
            source_translation=SourceTranslationFactory.with_dynamic_ip_and_port(),
            **kwargs,
        )

    @classmethod
    def with_custom_zones(cls, from_zones: List[str], to_zones: List[str], **kwargs):
        """Create an instance with custom zones."""
        return cls(from_=from_zones, to_=to_zones, **kwargs)

    @classmethod
    def build_with_no_containers(cls, **kwargs):
        """Return an instance without any containers."""
        return cls(folder=None, snippet=None, device=None, **kwargs)

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Return an instance with multiple containers (should fail validation)."""
        return cls(folder="Texas", snippet="TestSnippet", device=None, **kwargs)


class NatRuleUpdateApiFactory(factory.Factory):
    """Factory for creating NatRuleUpdateModel instances."""

    class Meta:
        model = NatRuleUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"nat_rule_{n}")
    description = factory.Faker("sentence")
    tag = ["Automation"]  # Example tag (tags are no longer restricted)
    disabled = False
    nat_type = NatType.ipv4
    from_ = ["any"]
    to_ = ["any"]
    source = ["any"]
    destination = ["any"]
    service = None
    source_translation = None

    @classmethod
    def with_source_translation(cls, **kwargs):
        """Create an instance with source translation."""
        return cls(
            source_translation=SourceTranslationFactory.with_dynamic_ip_and_port(),
            **kwargs,
        )

    @classmethod
    def with_zones_update(cls, from_zones: List[str], to_zones: List[str], **kwargs):
        """Create an instance updating security zones."""
        return cls(from_=from_zones, to_=to_zones, **kwargs)


class NatRuleResponseFactory(factory.Factory):
    """Factory for creating NatRuleResponseModel instances."""

    class Meta:
        model = NatRuleResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"nat_rule_{n}")
    description = factory.Faker("sentence")
    tag = ["Automation", "Decrypted"]  # Example tags (tags are no longer restricted)
    disabled = False
    nat_type = NatType.ipv4
    from_ = ["any"]
    to_ = ["any"]
    source = ["any"]
    destination = ["any"]
    service = None
    source_translation = None

    @classmethod
    def with_source_translation(cls, **kwargs):
        """Create an instance with source translation."""
        return cls(
            source_translation=SourceTranslationFactory.with_dynamic_ip_and_port(),
            **kwargs,
        )

    @classmethod
    def from_request(cls, request_model: NatRuleCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


class NatRuleMoveApiFactory(factory.Factory):
    """Factory for creating NatRuleMoveModel instances."""

    class Meta:
        model = NatRuleMoveModel

    destination = NatMoveDestination.TOP
    rulebase = NatRulebase.PRE
    destination_rule = None

    @classmethod
    def before_rule(cls, dest_rule=None, **kwargs):
        """Create a move configuration for placing before another rule."""
        if dest_rule is None:
            dest_rule = str(uuid.uuid4())
        return cls(
            destination=NatMoveDestination.BEFORE,
            destination_rule=dest_rule,
            **kwargs,
        )

    @classmethod
    def after_rule(cls, dest_rule=None, **kwargs):
        """Create a move configuration for placing after another rule."""
        if dest_rule is None:
            dest_rule = str(uuid.uuid4())
        return cls(
            destination=NatMoveDestination.AFTER,
            destination_rule=dest_rule,
            **kwargs,
        )


# Pydantic modeling tests
class NatRuleCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for NatRuleCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"nat_rule_{n}")
    description = factory.Faker("sentence")
    folder = "Shared"
    tag = ["Automation"]  # Example tag (tags are no longer restricted)
    nat_type = NatType.ipv4

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestNatRule",
            folder="Shared",
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
            folder="Shared",
        )

    @classmethod
    def build_with_duplicate_items(cls):
        """Return a data dict with duplicate list items."""
        return cls(
            name="TestNatRule",
            folder="Shared",
            source=["any", "any"],
            tag=["tag1", "tag1"],
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="TestNatRule",
            folder="Shared",
            snippet="TestSnippet",
        )

    @classmethod
    def build_with_no_container(cls):
        """Return a data dict without any container."""
        return cls(
            name="TestNatRule",
            folder=None,
            snippet=None,
            device=None,
        )


class NatRuleUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for NatRuleUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"nat_rule_{n}")
    description = factory.Faker("sentence")

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating a NAT rule."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedNatRule",
            source=["updated-source"],
            destination=["updated-dest"],
        )

    @classmethod
    def build_with_invalid_fields(cls):
        """Return a data dict with multiple invalid fields."""
        return cls(
            id="invalid-uuid",
            name="@invalid-name",
            source=["source", "source"],  # Duplicate items
        )

    @classmethod
    def build_minimal_update(cls):
        """Return a data dict with minimal valid update fields."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            description="Updated description",
        )


class NatRuleMoveModelFactory(factory.DictFactory):
    """Factory for creating data dicts for NatRuleMoveModel validation testing."""

    source_rule = factory.LazyFunction(lambda: str(uuid.uuid4()))
    destination = NatMoveDestination.TOP
    rulebase = NatRulebase.PRE

    @classmethod
    def build_valid_before(cls):
        """Return a valid data dict for before move operation."""
        return cls(
            source_rule="123e4567-e89b-12d3-a456-426655440000",
            destination=NatMoveDestination.BEFORE,
            destination_rule="987fcdeb-54ba-3210-9876-fedcba098765",
            rulebase=NatRulebase.PRE,
        )

    @classmethod
    def build_with_invalid_destination(cls):
        """Return a data dict with invalid destination."""
        return cls(
            source_rule="123e4567-e89b-12d3-a456-426655440000",
            destination="invalid",
            rulebase=NatRulebase.PRE,
        )

    @classmethod
    def build_missing_destination_rule(cls):
        """Return a data dict missing required destination_rule."""
        return cls(
            source_rule="123e4567-e89b-12d3-a456-426655440000",
            destination=NatMoveDestination.BEFORE,
            rulebase=NatRulebase.PRE,
        )
