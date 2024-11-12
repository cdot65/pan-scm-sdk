# tests/factories.py
import uuid

import factory

from scm.models.objects import (
    ApplicationCreateModel,
    ServiceCreateModel,
    ApplicationGroupCreateModel,
)
from scm.models.objects import (
    AddressResponseModel,
    AddressCreateModel,
    AddressUpdateModel,
)
from scm.models.objects.address_group import (
    AddressGroupCreateModel,
    DynamicFilter,
    AddressGroupResponseModel,
)
from scm.models.security import (
    DNSSecurityProfileCreateModel,
    DNSSecurityProfileResponseModel,
    AntiSpywareProfileResponseModel,
    AntiSpywareProfileCreateModel,
)
from scm.models.security.anti_spyware_profiles import (
    PacketCapture,
    ActionRequest,
    ThreatExceptionBase,
    Category,
    Severity,
    RuleBaseModel,
)
from scm.models.security.dns_security_profiles import (
    BotnetDomainsModel,
    ListActionRequestModel,
    PacketCaptureEnum,
    ListEntryBaseModel,
    WhitelistEntryModel,
    IPv6AddressEnum,
    IPv4AddressEnum,
    SinkholeSettingsModel,
    LogLevelEnum,
    ActionEnum,
    DNSSecurityCategoryEntryModel,
)
from scm.models.security.security_rules import (
    SecurityRuleCreateModel,
    ProfileSetting,
    Rulebase,
    SecurityRuleMoveModel,
    RuleMoveDestination,
    SecurityRuleResponseModel,
)


class AddressCreateIpNetmaskFactory(factory.Factory):
    """Factory for creating AddressCreateModel instances."""

    class Meta:
        model = AddressCreateModel

    name = factory.Sequence(lambda n: f"address_{n}")
    description = "Test Address"
    ip_netmask = "192.168.1.1/32"
    folder = "Shared"
    tag = ["test-tag", "environment-prod"]

    @classmethod
    def with_snippet(cls, **kwargs):
        return cls(folder=None, snippet="TestSnippet", **kwargs)

    @classmethod
    def with_device(cls, **kwargs):
        return cls(folder=None, device="TestDevice", **kwargs)


class AddressCreateFqdnFactory(factory.Factory):
    """Factory for creating AddressCreateModel instances."""

    class Meta:
        model = AddressCreateModel

    name = factory.Sequence(lambda n: f"address_{n}")
    description = "Test Address"
    fqdn = "pytest.example.com"
    folder = "Shared"
    tag = ["test-tag", "environment-prod"]

    @classmethod
    def with_snippet(cls, **kwargs):
        return cls(folder=None, snippet="TestSnippet", **kwargs)

    @classmethod
    def with_device(cls, **kwargs):
        return cls(folder=None, device="TestDevice", **kwargs)


class AddressCreateIpRangeFactory(factory.Factory):
    """Factory for creating AddressCreateModel instances."""

    class Meta:
        model = AddressCreateModel

    name = factory.Sequence(lambda n: f"address_{n}")
    description = "Test Address"
    ip_range = "192.168.255.100-192.168.255.105"
    folder = "Shared"
    tag = ["test-tag", "environment-prod"]

    @classmethod
    def with_snippet(cls, **kwargs):
        return cls(folder=None, snippet="TestSnippet", **kwargs)

    @classmethod
    def with_device(cls, **kwargs):
        return cls(folder=None, device="TestDevice", **kwargs)


class AddressCreateIpWildcardFactory(factory.Factory):
    """Factory for creating AddressCreateModel instances."""

    class Meta:
        model = AddressCreateModel

    name = factory.Sequence(lambda n: f"address_{n}")
    description = "Test Address"
    ip_wildcard = "10.20.1.0/0.0.248.255"
    folder = "Shared"
    tag = ["test-tag", "environment-prod"]

    @classmethod
    def with_snippet(cls, **kwargs):
        return cls(folder=None, snippet="TestSnippet", **kwargs)

    @classmethod
    def with_device(cls, **kwargs):
        return cls(folder=None, device="TestDevice", **kwargs)


class DynamicFilterFactory(factory.Factory):
    class Meta:
        model = DynamicFilter

    filter = "'test', 'abc123', 'prod', 'web'"


class AddressGroupDynamicFactory(factory.Factory):
    class Meta:
        model = AddressGroupCreateModel

    name = "ValidDynamicAddressGroup"
    description = "This is just a pytest that will fail"
    dynamic = factory.SubFactory(DynamicFilterFactory)
    folder = "MainFolder"
    tag = ["tag1", "tag2"]


class AddressGroupStaticFactory(factory.Factory):
    class Meta:
        model = AddressGroupCreateModel

    name = "ValidStaticAddressGroup"
    description = "Static AddressCreateModel Group Test"
    static = [
        "address-object1",
        "address-object2",
        "address-object3",
        "address-object4",
    ]
    folder = "MainFolder"
    tag = ["tag1", "tag2"]


class ApplicationFactory(factory.Factory):
    class Meta:
        model = ApplicationCreateModel

    name = "ValidApplication"
    description = "Application from pan-scm-sdk Test"
    category = "collaboration"
    subcategory = "file-sharing"
    technology = "client-server"
    risk = 1
    ports = ["tcp/80,443", "udp/3478"]
    folder = "Prisma Access"
    evasive = False
    pervasive = False
    excessive_bandwidth_use = False
    used_by_malware = False
    transfers_files = False
    has_known_vulnerabilities = True
    tunnels_other_apps = False
    prone_to_misuse = False
    no_certifications = False


class ApplicationGroupFactory(factory.Factory):
    class Meta:
        model = ApplicationGroupCreateModel

    name = "ValidStaticApplicationGroup"
    members = [
        "office365-consumer-access",
        "office365-enterprise-access",
    ]
    folder = "Prisma Access"


class ServiceFactory(factory.Factory):
    class Meta:
        model = ServiceCreateModel

    name = factory.Faker("word")
    description = "PyTest ServiceCreateModel test"
    tag = ["Automation"]
    folder = "Prisma Access"
    protocol = {"tcp": {"port": "80,443"}}


class BaseSecurityRuleFactory(factory.Factory):
    """Base factory for common security rule fields."""

    name = factory.Sequence(lambda n: f"security_rule_{n}")
    description = factory.Faker("sentence")
    action = "allow"

    # Lists with default values
    source = ["any"]
    destination = ["any"]
    application = ["any"]
    service = ["any"]
    source_user = ["any"]
    source_hip = ["any"]
    destination_hip = ["any"]
    category = ["any"]
    tag = factory.List([factory.Faker("word") for _ in range(2)])

    # Boolean fields
    disabled = False
    log_start = False
    log_end = True

    # Other fields
    log_setting = "Cortex Data Lake"
    profile_setting = factory.SubFactory("tests.factories.ProfileSettingFactory")


class SecurityRuleRequestFactory(BaseSecurityRuleFactory):
    """Factory for creating SecurityRuleCreateModel instances."""

    class Meta:
        model = SecurityRuleCreateModel

    folder = "Shared"  # Default container type

    @classmethod
    def with_snippet(cls, **kwargs) -> SecurityRuleCreateModel:
        """Create a security rule with snippet container."""
        return cls(folder=None, snippet="TestSnippet", **kwargs)

    @classmethod
    def with_device(cls, **kwargs) -> SecurityRuleCreateModel:
        """Create a security rule with device container."""
        return cls(folder=None, device="TestDevice", **kwargs)

    @classmethod
    def create_batch_with_names(
        cls, names: list[str], **kwargs
    ) -> list[SecurityRuleCreateModel]:
        """Create multiple security rules with specified names."""
        return [cls(name=name, **kwargs) for name in names]


class SecurityRuleResponseFactory(BaseSecurityRuleFactory):
    """Factory for creating SecurityRuleResponseModel instances."""

    class Meta:
        model = SecurityRuleResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    folder = factory.SelfAttribute("..folder")  # Inherits from request if provided

    @classmethod
    def from_request(
        cls,
        request_model: SecurityRuleCreateModel,
        **kwargs,
    ) -> SecurityRuleResponseModel:
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data.update(kwargs)
        return cls(**data)


class SecurityRuleMoveFactory(factory.Factory):
    """Factory for creating SecurityRuleMoveModel instances."""

    class Meta:
        model = SecurityRuleMoveModel

    source_rule = factory.LazyFunction(lambda: str(uuid.uuid4()))
    destination = RuleMoveDestination.TOP
    rulebase = Rulebase.PRE
    destination_rule = None

    @classmethod
    def before_rule(cls, **kwargs) -> SecurityRuleMoveModel:
        """Create a move configuration for placing before another rule."""
        return cls(
            destination=RuleMoveDestination.BEFORE,
            destination_rule=str(uuid.uuid4()),
            **kwargs,
        )

    @classmethod
    def after_rule(cls, **kwargs) -> SecurityRuleMoveModel:
        """Create a move configuration for placing after another rule."""
        return cls(
            destination=RuleMoveDestination.AFTER,
            destination_rule=str(uuid.uuid4()),
            **kwargs,
        )

    @classmethod
    def to_post_rulebase(cls, **kwargs) -> SecurityRuleMoveModel:
        """Create a move configuration for the post rulebase."""
        return cls(rulebase=Rulebase.POST, **kwargs)


class ProfileSettingFactory(factory.Factory):
    """Factory for creating ProfileSetting instances."""

    class Meta:
        model = ProfileSetting

    group = ["best-practice"]

    @classmethod
    def with_groups(cls, groups: list[str]) -> ProfileSetting:
        """Create a profile setting with specific groups."""
        return cls(group=groups)


class DNSSecurityCategoryEntryFactory(factory.Factory):
    class Meta:
        model = DNSSecurityCategoryEntryModel

    name = "pan-dns-sec-malware"
    action = ActionEnum.default
    log_level = LogLevelEnum.default
    packet_capture = PacketCaptureEnum.disable


class SinkholeSettingsFactory(factory.Factory):
    class Meta:
        model = SinkholeSettingsModel

    ipv4_address = IPv4AddressEnum.default_ip
    ipv6_address = IPv6AddressEnum.localhost


class WhitelistEntryFactory(factory.Factory):
    class Meta:
        model = WhitelistEntryModel

    name = factory.Faker("domain_name")
    description = factory.Faker("sentence")


class ListEntryRequestFactory(factory.Factory):
    class Meta:
        model = ListEntryBaseModel

    name = factory.Faker("word")
    packet_capture = PacketCaptureEnum.disable
    action = factory.LazyFunction(lambda: ListActionRequestModel("sinkhole"))  # noqa


class BotnetDomainsRequestFactory(factory.Factory):
    class Meta:
        model = BotnetDomainsModel

    dns_security_categories = factory.List(
        [factory.SubFactory(DNSSecurityCategoryEntryFactory)]
    )
    sinkhole = factory.SubFactory(SinkholeSettingsFactory)
    lists = factory.List([factory.SubFactory(ListEntryRequestFactory)])
    whitelist = factory.List([factory.SubFactory(WhitelistEntryFactory)])


class DNSSecurityProfileRequestFactory(factory.Factory):
    class Meta:
        model = DNSSecurityProfileCreateModel

    name = factory.Sequence(lambda n: f"profile_{n}")
    folder = "All"
    description = factory.Faker("sentence")
    botnet_domains = factory.SubFactory(BotnetDomainsRequestFactory)
    snippet = None
    device = None

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override the create method to exclude None values."""
        # Remove None values before creating the model
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        return super()._create(model_class, *args, **kwargs)


class DNSSecurityProfileResponseFactory(DNSSecurityProfileRequestFactory):
    class Meta:
        model = DNSSecurityProfileResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))

    @classmethod
    def from_request(cls, request_model: DNSSecurityProfileCreateModel, **kwargs):
        data = request_model.model_dump()
        data.update(kwargs)
        return cls(**data)


class AddressGroupDynamicFilterFactory(factory.Factory):
    class Meta:
        model = DynamicFilter

    filter = "'test-tag' and 'environment-prod'"


class AddressGroupRequestFactory(factory.Factory):
    class Meta:
        model = AddressGroupCreateModel

    name = factory.Sequence(lambda n: f"address_group_{n}")
    description = "Test Address Group"
    folder = "Shared"
    tag = ["test-tag", "environment-prod"]

    @classmethod
    def with_snippet(cls, **kwargs):
        return cls(folder=None, snippet="TestSnippet", **kwargs)

    @classmethod
    def with_device(cls, **kwargs):
        return cls(folder=None, device="TestDevice", **kwargs)


class AddressGroupResponseFactory(AddressGroupRequestFactory):
    class Meta:
        model = AddressGroupResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))

    @classmethod
    def from_request(cls, request_model: AddressGroupCreateModel, **kwargs):
        data = request_model.model_dump()
        data.update(kwargs)
        return cls(**data)


class AntiSpywareRuleCreateFactory(factory.Factory):
    """Factory for creating RuleRequest instances."""

    class Meta:
        model = RuleBaseModel

    name = factory.Sequence(lambda n: f"rule_{n}")
    severity = [Severity.critical, Severity.high]
    category = Category.spyware
    threat_name = "any"
    packet_capture = PacketCapture.disable
    action = factory.LazyAttribute(lambda _: ActionRequest("alert"))

    @classmethod
    def with_block_ip_action(cls, **kwargs):
        """Create a rule with block_ip action."""
        return cls(
            action={"block_ip": {"track_by": "source", "duration": 3600}}, **kwargs
        )


class ThreatExceptionCreateFactory(factory.Factory):
    """Factory for creating ThreatExceptionRequest instances."""

    class Meta:
        model = ThreatExceptionBase

    name = factory.Sequence(lambda n: f"exception_{n}")
    action = factory.LazyAttribute(lambda _: ActionRequest("allow"))
    packet_capture = PacketCapture.single_packet
    exempt_ip = [{"name": "192.168.1.1"}]
    notes = "Test exception"


class AntiSpywareProfileRequestFactory(factory.Factory):
    """Factory for creating AntiSpywareProfileCreateModel instances."""

    class Meta:
        model = AntiSpywareProfileCreateModel

    name = factory.Sequence(lambda n: f"profile_{n}")
    folder = "Prisma Access"
    description = "Test anti-spyware profile"
    rules = factory.List([factory.SubFactory(AntiSpywareRuleCreateFactory)])
    threat_exception = factory.List([factory.SubFactory(ThreatExceptionCreateFactory)])

    @classmethod
    def with_snippet(cls, **kwargs):
        """Create a profile with snippet container."""
        return cls(folder=None, snippet="TestSnippet", **kwargs)

    @classmethod
    def with_device(cls, **kwargs):
        """Create a profile with device container."""
        return cls(folder=None, device="TestDevice", **kwargs)


class AntiSpywareProfileResponseFactory(AntiSpywareProfileRequestFactory):
    """Factory for creating AntiSpywareProfileResponseModel instances."""

    class Meta:
        model = AntiSpywareProfileResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))

    @classmethod
    def from_request(cls, request_model: AntiSpywareProfileCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data.update(kwargs)
        return cls(**data)
