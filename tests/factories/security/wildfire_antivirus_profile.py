import uuid

import factory

from scm.models.security.wildfire_antivirus_profiles import (
    WildfireAvAnalysis,
    WildfireAvDirection,
    WildfireAvMlavExceptionEntry,
    WildfireAvProfileCreateModel,
    WildfireAvProfileResponseModel,
    WildfireAvProfileUpdateModel,
    WildfireAvRuleBase,
    WildfireAvThreatExceptionEntry,
)


# Sub factories
class WildfireAvRuleBaseFactory(factory.Factory):
    """Factory for creating WildfireAvRuleBase instances."""

    class Meta:
        model = WildfireAvRuleBase

    name = factory.Sequence(lambda n: f"rule_{n}")
    analysis = WildfireAvAnalysis.public_cloud
    application = ["any"]
    direction = WildfireAvDirection.both
    file_type = ["any"]

    @classmethod
    def with_specific_analysis(cls, analysis: WildfireAvAnalysis, **kwargs):
        """Create an instance with a specific analysis type."""
        return cls(analysis=analysis, **kwargs)

    @classmethod
    def with_specific_direction(cls, direction: WildfireAvDirection, **kwargs):
        """Create an instance with a specific direction."""
        return cls(direction=direction, **kwargs)


class WildfireAvMlavExceptionEntryFactory(factory.Factory):
    """Factory for creating WildfireAvMlavExceptionEntry instances."""

    class Meta:
        model = WildfireAvMlavExceptionEntry

    name = factory.Sequence(lambda n: f"mlav_exception_{n}")
    description = factory.Faker("sentence")
    filename = factory.Sequence(lambda n: f"file_{n}.txt")


class WildfireAvThreatExceptionEntryFactory(factory.Factory):
    """Factory for creating WildfireAvThreatExceptionEntry instances."""

    class Meta:
        model = WildfireAvThreatExceptionEntry

    name = factory.Sequence(lambda n: f"threat_exception_{n}")
    notes = factory.Faker("sentence")


# SDK tests against SCM API
class WildfireAvProfileCreateApiFactory(factory.Factory):
    """Factory for creating WildfireAvProfileCreateModel instances."""

    class Meta:
        model = WildfireAvProfileCreateModel

    name = factory.Sequence(lambda n: f"wildfire_profile_{n}")
    description = factory.Faker("sentence")
    folder = "Texas"
    packet_capture = False
    rules = factory.List([factory.SubFactory(WildfireAvRuleBaseFactory)])
    mlav_exception = factory.List([factory.SubFactory(WildfireAvMlavExceptionEntryFactory)])
    threat_exception = factory.List([factory.SubFactory(WildfireAvThreatExceptionEntryFactory)])

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, device=device, **kwargs)

    @classmethod
    def with_packet_capture(cls, enabled: bool = True, **kwargs):
        """Create an instance with packet capture enabled/disabled."""
        return cls(packet_capture=enabled, **kwargs)


class WildfireAvProfileUpdateApiFactory(factory.Factory):
    """Factory for creating WildfireAvProfileUpdateModel instances."""

    class Meta:
        model = WildfireAvProfileUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"wildfire_profile_{n}")
    description = factory.Faker("sentence")
    rules = factory.List([factory.SubFactory(WildfireAvRuleBaseFactory)])
    mlav_exception = factory.List([factory.SubFactory(WildfireAvMlavExceptionEntryFactory)])
    threat_exception = factory.List([factory.SubFactory(WildfireAvThreatExceptionEntryFactory)])

    @classmethod
    def with_packet_capture(cls, enabled: bool = True, **kwargs):
        """Create an instance with packet capture enabled/disabled."""
        return cls(packet_capture=enabled, **kwargs)


class WildfireAvProfileResponseFactory(factory.Factory):
    """Factory for creating WildfireAvProfileResponseModel instances."""

    class Meta:
        model = WildfireAvProfileResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"wildfire_profile_{n}")
    description = factory.Faker("sentence")
    folder = "Texas"
    packet_capture = False
    rules = factory.List([factory.SubFactory(WildfireAvRuleBaseFactory)])
    mlav_exception = factory.List([factory.SubFactory(WildfireAvMlavExceptionEntryFactory)])
    threat_exception = factory.List([factory.SubFactory(WildfireAvThreatExceptionEntryFactory)])

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, device=device, **kwargs)

    @classmethod
    def from_request(cls, request_model: WildfireAvProfileCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class WildfireAvProfileCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for WildfireAvProfileCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"wildfire_profile_{n}")
    folder = "Texas"
    rules = []

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestWildfireProfile",
            folder="Texas",
            rules=[
                {
                    "name": "TestRule",
                    "direction": WildfireAvDirection.both,
                    "analysis": WildfireAvAnalysis.public_cloud,
                }
            ],
        )

    @classmethod
    def build_with_invalid_name(cls):
        """Return a data dict with invalid name pattern."""
        return cls(
            name="@invalid-name#",
            folder="Texas",
            rules=[
                {
                    "name": "TestRule",
                    "direction": WildfireAvDirection.both,
                }
            ],
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="TestWildfireProfile",
            folder="Texas",
            snippet="TestSnippet",
            rules=[
                {
                    "name": "TestRule",
                    "direction": WildfireAvDirection.both,
                }
            ],
        )

    @classmethod
    def build_with_no_container(cls):
        """Return a data dict without any container."""
        return cls(
            name="TestWildfireProfile",
            rules=[
                {
                    "name": "TestRule",
                    "direction": WildfireAvDirection.both,
                }
            ],
        )

    @classmethod
    def build_with_invalid_rule(cls):
        """Return a data dict with an invalid rule."""
        return cls(
            name="TestWildfireProfile",
            folder="Texas",
            rules=[
                {
                    "name": "TestRule",
                    "direction": "invalid-direction",
                }
            ],
        )


class WildfireAvProfileUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for WildfireAvProfileUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"wildfire_profile_{n}")
    rules = []

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating a Wildfire Antivirus Profile."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedWildfireProfile",
            rules=[
                {
                    "name": "UpdatedRule",
                    "direction": WildfireAvDirection.download,
                }
            ],
        )

    @classmethod
    def build_with_invalid_fields(cls):
        """Return a data dict with multiple invalid fields."""
        return cls(
            id="invalid-uuid",
            name="@invalid-name",
            rules=[{"invalid": "rule"}],
        )

    @classmethod
    def build_minimal_update(cls):
        """Return a data dict with minimal valid update fields."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            description="Updated description",
        )
