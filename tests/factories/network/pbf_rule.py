"""Factory definitions for network PBF Rule objects."""

import uuid

import factory

from scm.models.network.pbf_rule import (
    PbfRuleCreateModel,
    PbfRuleResponseModel,
    PbfRuleUpdateModel,
)


# SDK tests against SCM API
class PbfRuleCreateApiFactory(factory.Factory):
    """Factory for creating PbfRuleCreateModel instances."""

    class Meta:
        """Meta class that defines the model for PbfRuleCreateApiFactory."""

        model = PbfRuleCreateModel

    name = factory.Sequence(lambda n: f"pbf_rule_{n}")
    folder = "Shared"
    description = factory.Faker("sentence")
    tag = None
    schedule = None
    disabled = None
    from_ = None
    source = None
    source_user = None
    destination = None
    destination_application = None
    service = None
    application = None
    action = None
    enforce_symmetric_return = None

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def with_forward_action(cls, **kwargs):
        """Create an instance with forward action."""
        return cls(
            action={
                "forward": {
                    "egress_interface": "ethernet1/1",
                    "nexthop": {"ip_address": "10.0.0.1"},
                },
            },
            **kwargs,
        )

    @classmethod
    def with_discard_action(cls, **kwargs):
        """Create an instance with discard action."""
        return cls(
            action={"discard": {}},
            **kwargs,
        )


class PbfRuleUpdateApiFactory(factory.Factory):
    """Factory for creating PbfRuleUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for PbfRuleUpdateApiFactory."""

        model = PbfRuleUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"pbf_rule_{n}")
    description = factory.Faker("sentence")
    tag = None
    schedule = None
    disabled = None
    from_ = None
    source = None
    source_user = None
    destination = None
    destination_application = None
    service = None
    application = None
    action = None
    enforce_symmetric_return = None


class PbfRuleResponseFactory(factory.Factory):
    """Factory for creating PbfRuleResponseModel instances."""

    class Meta:
        """Meta class that defines the model for PbfRuleResponseFactory."""

        model = PbfRuleResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"pbf_rule_{n}")
    folder = "Shared"
    description = factory.Faker("sentence")
    tag = None
    schedule = None
    disabled = None
    from_ = None
    source = None
    source_user = None
    destination = None
    destination_application = None
    service = None
    application = None
    action = None
    enforce_symmetric_return = None

    @classmethod
    def from_request(cls, request_model: PbfRuleCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class PbfRuleCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for PbfRuleCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"pbf_rule_{n}")
    folder = "Shared"

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestPbfRule",
            folder="Shared",
            description="Test PBF rule",
            source=["any"],
            destination=["any"],
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="TestPbfRule",
            folder="Shared",
            snippet="TestSnippet",
        )

    @classmethod
    def build_with_no_container(cls):
        """Return a data dict without any container."""
        return cls(
            name="TestPbfRule",
            folder=None,
            snippet=None,
            device=None,
        )


class PbfRuleUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for PbfRuleUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"pbf_rule_{n}")

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating a PBF rule."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedPbfRule",
            description="Updated PBF rule description",
        )
