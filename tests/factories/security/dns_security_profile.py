"""Factory definitions for DNS security profile objects."""

import uuid

import factory

from scm.models.security.dns_security_profiles import (
    ActionEnum,
    BotnetDomainsModel,
    DNSSecurityCategoryEntryModel,
    DNSSecurityProfileCreateModel,
    DNSSecurityProfileResponseModel,
    DNSSecurityProfileUpdateModel,
    IPv4AddressEnum,
    IPv6AddressEnum,
    ListActionRequestModel,
    ListEntryBaseModel,
    LogLevelEnum,
    PacketCaptureEnum,
    SinkholeSettingsModel,
    WhitelistEntryModel,
)


# Component factories
class DNSSecurityCategoryEntryFactory(factory.Factory):
    """Factory for creating DNSSecurityCategoryEntryModel instances."""

    class Meta:
        model = DNSSecurityCategoryEntryModel

    name = "pan-dns-sec-malware"
    action = ActionEnum.default
    log_level = LogLevelEnum.default
    packet_capture = PacketCaptureEnum.disable

    @classmethod
    def with_action(cls, action: ActionEnum = ActionEnum.block, **kwargs):
        """Create an instance with a specific action."""
        return cls(action=action, **kwargs)

    @classmethod
    def with_log_level(cls, level: LogLevelEnum = LogLevelEnum.high, **kwargs):
        """Create an instance with a specific log level."""
        return cls(log_level=level, **kwargs)


class ListActionRequestFactory(factory.Factory):
    """Factory for creating ListActionRequestModel instances."""

    class Meta:
        model = ListActionRequestModel

    root = {"sinkhole": {}}

    @classmethod
    def with_action(cls, action: str = "block", **kwargs):
        """Create an instance with a specific action."""
        return cls(root={action: {}}, **kwargs)


class ListEntryBaseFactory(factory.Factory):
    """Factory for creating ListEntryBaseModel instances."""

    class Meta:
        model = ListEntryBaseModel

    name = factory.Faker("word")
    packet_capture = PacketCaptureEnum.disable
    action = factory.SubFactory(ListActionRequestFactory)

    @classmethod
    def with_packet_capture(
        cls, capture: PacketCaptureEnum = PacketCaptureEnum.single_packet, **kwargs
    ):
        """Create an instance with specific packet capture settings."""
        return cls(packet_capture=capture, **kwargs)


class SinkholeSettingsFactory(factory.Factory):
    """Factory for creating SinkholeSettingsModel instances."""

    class Meta:
        model = SinkholeSettingsModel

    ipv4_address = IPv4AddressEnum.default_ip
    ipv6_address = IPv6AddressEnum.localhost

    @classmethod
    def with_custom_addresses(
        cls,
        ipv4: IPv4AddressEnum = IPv4AddressEnum.localhost,
        ipv6: IPv6AddressEnum = IPv6AddressEnum.localhost,
        **kwargs,
    ):
        """Create an instance with custom IPv4 and IPv6 addresses."""
        return cls(ipv4_address=ipv4, ipv6_address=ipv6, **kwargs)


class WhitelistEntryFactory(factory.Factory):
    """Factory for creating WhitelistEntryModel instances."""

    class Meta:
        model = WhitelistEntryModel

    name = factory.Faker("domain_name")
    description = factory.Faker("sentence")


class BotnetDomainsFactory(factory.Factory):
    """Factory for creating BotnetDomainsModel instances."""

    class Meta:
        model = BotnetDomainsModel

    dns_security_categories = factory.List([factory.SubFactory(DNSSecurityCategoryEntryFactory)])
    lists = factory.List([factory.SubFactory(ListEntryBaseFactory)])
    sinkhole = factory.SubFactory(SinkholeSettingsFactory)
    whitelist = factory.List([factory.SubFactory(WhitelistEntryFactory)])

    @classmethod
    def with_empty_lists(cls, **kwargs):
        """Create an instance with empty lists."""
        return cls(dns_security_categories=[], lists=[], whitelist=[], **kwargs)


# Main factories for API testing
class DNSSecurityProfileCreateApiFactory(factory.Factory):
    """Factory for creating DNSSecurityProfileCreateModel instances."""

    class Meta:
        model = DNSSecurityProfileCreateModel

    name = factory.Sequence(lambda n: f"dns_security_profile_{n}")
    description = factory.Faker("sentence")
    folder = "Texas"
    botnet_domains = factory.SubFactory(BotnetDomainsFactory)
    snippet = None
    device = None

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def with_empty_botnet_domains(cls, **kwargs):
        """Create an instance with empty botnet domains configuration."""
        return cls(botnet_domains=BotnetDomainsFactory.with_empty_lists(), **kwargs)


class DNSSecurityProfileUpdateApiFactory(factory.Factory):
    """Factory for creating DNSSecurityProfileUpdateModel instances."""

    class Meta:
        model = DNSSecurityProfileUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"dns_security_profile_{n}")
    description = factory.Faker("sentence")
    botnet_domains = factory.SubFactory(BotnetDomainsFactory)

    @classmethod
    def with_updated_sinkhole(cls, **kwargs):
        """Create an instance with updated sinkhole settings."""
        return cls(
            botnet_domains=BotnetDomainsFactory(
                sinkhole=SinkholeSettingsFactory.with_custom_addresses()
            ),
            **kwargs,
        )


class DNSSecurityProfileResponseFactory(factory.Factory):
    """Factory for creating DNSSecurityProfileResponseModel instances."""

    class Meta:
        model = DNSSecurityProfileResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"dns_security_profile_{n}")
    description = factory.Faker("sentence")
    folder = "Texas"
    botnet_domains = factory.SubFactory(BotnetDomainsFactory)
    snippet = None
    device = None

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def from_request(cls, request_model: DNSSecurityProfileCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Dict factories for pydantic model validation testing
class DNSSecurityProfileCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for DNSSecurityProfileCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"dns_security_profile_{n}")
    description = factory.Faker("sentence")
    folder = "Texas"

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestProfile",
            folder="Texas",
            botnet_domains={
                "dns_security_categories": [
                    {"name": "malware", "action": "block", "log_level": "high"}
                ]
            },
        )

    @classmethod
    def build_with_invalid_name(cls):
        """Return a data dict with invalid name pattern."""
        return cls(
            name="@invalid-name#",
            folder="Texas",
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="TestProfile",
            folder="Texas",
            snippet="TestSnippet",
        )

    @classmethod
    def build_with_invalid_action(cls):
        """Return a data dict with invalid action in botnet domains."""
        return cls(
            name="TestProfile",
            folder="Texas",
            botnet_domains={
                "dns_security_categories": [{"name": "malware", "action": "invalid-action"}]
            },
        )


class DNSSecurityProfileUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for DNSSecurityProfileUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"dns_security_profile_{n}")
    description = factory.Faker("sentence")

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating a DNS security profile."""
        return cls(
            name="UpdatedProfile",
            description="Updated description",
            botnet_domains={"sinkhole": {"ipv4_address": "127.0.0.1", "ipv6_address": "::1"}},
        )

    @classmethod
    def build_with_invalid_fields(cls):
        """Return a data dict with multiple invalid fields."""
        return cls(
            id="invalid-uuid",
            name="@invalid-name",
            botnet_domains={"dns_security_categories": [{"name": "malware", "action": "invalid"}]},
        )

    @classmethod
    def build_minimal_update(cls):
        """Return a data dict with minimal valid update fields."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            description="Updated description",
        )
