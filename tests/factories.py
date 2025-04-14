# tests/factories.py

# Standard library imports
from typing import Dict, List, Union
import uuid

# External libraries
import factory  # type: ignore

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

# Local SDK imports
from scm.models.security import (
    DNSSecurityProfileCreateModel,
    DNSSecurityProfileResponseModel,
    SecurityRuleCreateModel,
    SecurityRuleMoveModel,
    VulnerabilityProfileCreateModel,
    VulnerabilityProfileResponseModel,
)
from scm.models.security.dns_security_profiles import (
    ActionEnum,
    BotnetDomainsModel,
    DNSSecurityCategoryEntryModel,
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
from scm.models.security.security_rules import (
    SecurityRuleAction,
    SecurityRuleMoveDestination,
    SecurityRuleProfileSetting,
    SecurityRuleResponseModel,
    SecurityRuleRulebase,
    SecurityRuleUpdateModel,
)
from scm.models.security.vulnerability_protection_profiles import (
    VulnerabilityProfileCategory,
    VulnerabilityProfileExemptIpEntry,
    VulnerabilityProfileHost,
    VulnerabilityProfilePacketCapture,
    VulnerabilityProfileRuleModel,
    VulnerabilityProfileSeverity,
    VulnerabilityProfileThreatExceptionModel,
    VulnerabilityProfileTimeAttribute,
    VulnerabilityProfileTimeAttributeTrackBy,
    VulnerabilityProfileUpdateModel,
)
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

# ----------------------------------------------------------------------------
# Security Rule object factories.
# ----------------------------------------------------------------------------


# Sub factories
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


# ----------------------------------------------------------------------------
# DNS Security Profile object factories.
# ----------------------------------------------------------------------------


# Sub factories
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


# SDK tests against SCM API
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


# Pydantic modeling tests
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


# ----------------------------------------------------------------------------
# Vulnerability Profile object factories.
# ----------------------------------------------------------------------------


# Sub factories
class VulnerabilityProfileExemptIpEntryFactory(factory.Factory):
    """Factory for creating VulnerabilityProfileExemptIpEntry instances."""

    class Meta:
        model = VulnerabilityProfileExemptIpEntry

    name = "192.168.1.1"

    @classmethod
    def with_custom_ip(cls, ip: str = "10.0.0.1", **kwargs):
        """Create an instance with a custom IP address."""
        return cls(name=ip, **kwargs)


class VulnerabilityProfileTimeAttributeFactory(factory.Factory):
    """Factory for creating VulnerabilityProfileTimeAttribute instances."""

    class Meta:
        model = VulnerabilityProfileTimeAttribute

    interval = 60
    threshold = 10
    track_by = "source"


class VulnerabilityProfileRuleModelFactory(factory.Factory):
    """Factory for creating VulnerabilityProfileRuleModel instances."""

    class Meta:
        model = VulnerabilityProfileRuleModel

    name = factory.Sequence(lambda n: f"rule_{n}")
    severity = [VulnerabilityProfileSeverity.critical]
    category = VulnerabilityProfileCategory.any
    host = VulnerabilityProfileHost.any
    packet_capture = VulnerabilityProfilePacketCapture.disable
    threat_name = "any"  # Add the default threat_name here
    action = None
    cve = ["any"]
    vendor_id = ["any"]

    @classmethod
    def with_threat_name(cls, threat_name: str = "custom_threat", **kwargs):
        """Create an instance with a specific threat name."""
        return cls(threat_name=threat_name, **kwargs)


class VulnerabilityProfileThreatExceptionModelFactory(factory.Factory):
    """Factory for creating VulnerabilityProfileThreatExceptionModel instances."""

    class Meta:
        model = VulnerabilityProfileThreatExceptionModel

    name = factory.Sequence(lambda n: f"exception_{n}")
    packet_capture = VulnerabilityProfilePacketCapture.single_packet
    exempt_ip = None
    time_attribute = None
    notes = "Test threat exception"

    # Remove threat_name related methods as they belong to RuleModel
    @classmethod
    def with_exempt_ips(cls, ips: List[str], **kwargs):
        """Create an instance with exempt IPs."""
        return cls(
            exempt_ip=[VulnerabilityProfileExemptIpEntry(name=ip) for ip in ips],
            **kwargs,
        )

    @classmethod
    def with_time_attribute(
        cls,
        interval=60,
        threshold=10,
        track_by=VulnerabilityProfileTimeAttributeTrackBy.source,
        **kwargs,
    ):
        """Create an instance with time attribute settings."""
        return cls(
            time_attribute=VulnerabilityProfileTimeAttribute(
                interval=interval, threshold=threshold, track_by=track_by
            ),
            **kwargs,
        )


# SDK tests against SCM API
class VulnerabilityProfileCreateApiFactory(factory.Factory):
    """Factory for creating VulnerabilityProfileCreateModel instances."""

    class Meta:
        model = VulnerabilityProfileCreateModel

    name = factory.Sequence(lambda n: f"vulnerability_profile_{n}")
    description = factory.Faker("sentence")
    folder = "Texas"
    rules = factory.List([factory.SubFactory(VulnerabilityProfileRuleModelFactory)])
    threat_exception = None

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create a profile with snippet container."""
        return cls(folder=None, snippet=snippet, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create a profile with device container."""
        return cls(folder=None, device=device, **kwargs)

    @classmethod
    def with_multiple_rules(cls, rules_count: int = 3, **kwargs):
        """Create a profile with multiple rules."""
        rules = [VulnerabilityProfileRuleModelFactory() for _ in range(rules_count)]
        return cls(rules=rules, **kwargs)


class VulnerabilityProfileUpdateApiFactory(factory.Factory):
    """Factory for creating VulnerabilityProfileUpdateModel instances."""

    class Meta:
        model = VulnerabilityProfileUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"vulnerability_profile_{n}")
    description = factory.Faker("sentence")
    rules = factory.List([factory.SubFactory(VulnerabilityProfileRuleModelFactory)])
    threat_exception = factory.List(
        [factory.SubFactory(VulnerabilityProfileThreatExceptionModelFactory)]
    )

    @classmethod
    def with_empty_rules(cls, **kwargs):
        """Create an instance with no rules."""
        return cls(rules=[], **kwargs)


class VulnerabilityProfileResponseFactory(factory.Factory):
    """Factory for creating VulnerabilityProfileResponseModel instances."""

    class Meta:
        model = VulnerabilityProfileResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"vulnerability_profile_{n}")
    description = factory.Faker("sentence")
    folder = "Texas"
    rules = factory.List([factory.SubFactory(VulnerabilityProfileRuleModelFactory)])
    threat_exception = factory.List(
        [factory.SubFactory(VulnerabilityProfileThreatExceptionModelFactory)]
    )

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create a profile with snippet container."""
        return cls(folder=None, snippet=snippet, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create a profile with device container."""
        return cls(folder=None, device=device, **kwargs)

    @classmethod
    def from_request(cls, request_model: VulnerabilityProfileCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class VulnerabilityProfileCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for VulnerabilityProfileCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"vulnerability_profile_{n}")
    description = factory.Faker("sentence")
    folder = "Texas"
    rules = []

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="valid-profile-name",
            folder="Texas",
            rules=[
                {
                    "name": "TestRule",
                    "severity": [VulnerabilityProfileSeverity.critical],
                    "category": VulnerabilityProfileCategory.any,
                    "host": VulnerabilityProfileHost.any,
                }
            ],
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="valid-profile-name",
            folder="Texas",
            snippet="test123",
            rules=[
                {
                    "name": "TestRule",
                    "severity": [VulnerabilityProfileSeverity.critical],
                    "category": VulnerabilityProfileCategory.any,
                    "host": VulnerabilityProfileHost.any,
                }
            ],
        )

    @classmethod
    def build_with_invalid_name(cls):
        """Return a data dict with invalid name pattern."""
        return cls(
            name="@invalid-profile-name",
            folder="Texas",
            rules=[
                {
                    "name": "TestRule",
                    "severity": [VulnerabilityProfileSeverity.critical],
                    "category": VulnerabilityProfileCategory.any,
                    "host": VulnerabilityProfileHost.any,
                }
            ],
        )

    @classmethod
    def build_with_invalid_rules(cls):
        """Return a data dict with invalid rules structure."""
        return cls(
            name="TestProfile",
            folder="Texas",
            rules=[
                {
                    "name": "TestRule",
                    "severity": ["invalid"],
                    "category": "invalid",
                    "host": "invalid",
                }
            ],
        )


class VulnerabilityProfileUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for VulnerabilityProfileUpdateModel validation testing."""

    id = "12345678-1234-5678-1234-567812345678"
    name = factory.Sequence(lambda n: f"vulnerability_profile_{n}")
    description = factory.Faker("sentence")
    rules = []

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating a profile."""
        return cls(
            name="valid-profile-name",
            folder="Texas",
            rules=[
                {
                    "name": "TestRule",
                    "severity": [VulnerabilityProfileSeverity.critical],
                    "category": VulnerabilityProfileCategory.any,
                    "host": VulnerabilityProfileHost.any,
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
            id="12345678-1234-5678-1234-567812345678",
            description="Updated description",
        )


# ----------------------------------------------------------------------------
# Wildfire Antivirus Profile object factories.
# ----------------------------------------------------------------------------


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


# ----------------------------------------------------------------------------
# NAT factories for SDK usage (model-based)
# ----------------------------------------------------------------------------


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
