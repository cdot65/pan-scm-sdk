# tests/factories.py

# Standard library imports
import uuid
from typing import List

# External libraries
import factory

# Local SDK imports
from scm.models.objects import (
    AddressCreateModel,
    AddressUpdateModel,
    AddressResponseModel,
    AddressGroupCreateModel,
    AddressGroupResponseModel,
    ApplicationCreateModel,
    ServiceCreateModel,
    ServiceResponseModel,
    ServiceUpdateModel,
    TagResponseModel,
    TagCreateModel,
    TagUpdateModel,
    ApplicationResponseModel,
    ApplicationUpdateModel,
    ApplicationGroupCreateModel,
    ApplicationGroupResponseModel,
    ApplicationGroupUpdateModel,
)
from scm.models.objects.address_group import (
    DynamicFilter,
    AddressGroupUpdateModel,
)
from scm.models.objects.service import UDPProtocol, TCPProtocol, Override
from scm.models.security import (
    DNSSecurityProfileCreateModel,
    DNSSecurityProfileResponseModel,
    AntiSpywareProfileResponseModel,
    AntiSpywareProfileCreateModel,
    VulnerabilityProfileCreateModel,
    VulnerabilityProfileResponseModel,
    SecurityRuleCreateModel,
    SecurityRuleMoveModel,
    DecryptionProfileCreateModel,
    DecryptionProfileResponseModel,
)
from scm.models.security.anti_spyware_profiles import (
    AntiSpywarePacketCapture,
    AntiSpywareThreatExceptionBase,
    AntiSpywareCategory,
    AntiSpywareSeverity,
    AntiSpywareProfileUpdateModel,
    AntiSpywareInlinePolicyAction,
    AntiSpywareMicaEngineSpywareEnabledEntry,
    AntiSpywareExemptIpEntry,
)
from scm.models.security.anti_spyware_profiles import (
    AntiSpywareRuleBaseModel as AntiSpywareRuleBaseModel,
)
from scm.models.security.decryption_profiles import (
    SSLVersion,
    DecryptionProfileUpdateModel,
    SSLNoProxy,
    SSLInboundProxy,
    SSLForwardProxy,
    SSLProtocolSettings,
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
    DNSSecurityProfileUpdateModel,
)
from scm.models.security.security_rules import (
    SecurityRuleProfileSetting,
    SecurityRuleRulebase,
    SecurityRuleMoveDestination,
    SecurityRuleResponseModel,
    SecurityRuleAction,
    SecurityRuleUpdateModel,
)
from scm.models.security.vulnerability_protection_profiles import (
    VulnerabilityProfileThreatExceptionModel,
    VulnerabilityProfileRuleModel,
    VulnerabilityProfileHost,
    VulnerabilityProfileCategory,
    VulnerabilityProfileSeverity,
    VulnerabilityProfileUpdateModel,
    VulnerabilityProfilePacketCapture,
    VulnerabilityProfileTimeAttribute,
    VulnerabilityProfileExemptIpEntry,
)
from scm.models.security.wildfire_antivirus_profiles import (
    WildfireAvDirection,
    WildfireAvAnalysis,
    WildfireAvProfileCreateModel,
    WildfireAvProfileResponseModel,
    WildfireAvProfileUpdateModel,
    WildfireAvThreatExceptionEntry,
    WildfireAvMlavExceptionEntry,
    WildfireAvRuleBase,
)


# ----------------------------------------------------------------------------
# Address object factories.
# ----------------------------------------------------------------------------


# SDK tests against SCM API
class AddressCreateApiFactory(factory.Factory):
    """Factory for creating AddressCreateModel instances with different address types."""

    class Meta:
        model = AddressCreateModel

    name = factory.Sequence(lambda n: f"address_{n}")
    description = factory.Faker("sentence")
    folder = "Shared"
    tag = [
        "test-tag",
        "environment-prod",
    ]

    # Address types default to None
    ip_netmask = None
    ip_range = None
    ip_wildcard = None
    fqdn = None

    @classmethod
    def with_ip_netmask(cls, ip_netmask="192.168.1.1/32", **kwargs):
        return cls(ip_netmask=ip_netmask, **kwargs)

    @classmethod
    def with_fqdn(cls, fqdn="example.com", **kwargs):
        return cls(fqdn=fqdn, **kwargs)

    @classmethod
    def with_ip_range(cls, ip_range="192.168.0.1-192.168.0.10", **kwargs):
        return cls(ip_range=ip_range, **kwargs)

    @classmethod
    def with_ip_wildcard(cls, ip_wildcard="10.20.1.0/0.0.248.255", **kwargs):
        return cls(ip_wildcard=ip_wildcard, **kwargs)

    @classmethod
    def with_snippet(cls, **kwargs):
        return cls(folder=None, snippet="TestSnippet", **kwargs)

    @classmethod
    def with_device(cls, **kwargs):
        return cls(folder=None, device="TestDevice", **kwargs)


class AddressUpdateApiFactory(factory.Factory):
    """Factory for creating AddressUpdateModel instances."""

    class Meta:
        model = AddressUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"address_{n}")
    description = factory.Faker("sentence")
    tag = ["updated-tag"]

    # Address types default to None
    ip_netmask = None
    ip_range = None
    ip_wildcard = None
    fqdn = None

    @classmethod
    def with_ip_netmask(cls, ip_netmask="192.168.1.100/32", **kwargs):
        return cls(ip_netmask=ip_netmask, **kwargs)

    @classmethod
    def with_fqdn(cls, fqdn="example.com", **kwargs):
        return cls(fqdn=fqdn, **kwargs)

    @classmethod
    def with_ip_range(cls, ip_range="192.168.0.1-192.168.0.10", **kwargs):
        return cls(ip_range=ip_range, **kwargs)

    @classmethod
    def with_ip_wildcard(cls, ip_wildcard="10.20.1.0/0.0.248.255", **kwargs):
        return cls(ip_wildcard=ip_wildcard, **kwargs)

    @classmethod
    def with_snippet(cls, **kwargs):
        return cls(folder=None, snippet="TestSnippet", **kwargs)

    @classmethod
    def with_device(cls, **kwargs):
        return cls(folder=None, device="TestDevice", **kwargs)


class AddressResponseFactory(factory.Factory):
    """Factory for creating AddressResponseModel instances."""

    class Meta:
        model = AddressResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"address_{n}")
    description = factory.Faker("sentence")
    tag = ["response-tag"]
    folder = "Shared"

    # Address types default to None
    ip_netmask = None
    ip_range = None
    ip_wildcard = None
    fqdn = None

    @classmethod
    def with_ip_netmask(cls, ip_netmask="192.168.1.1/32", **kwargs):
        return cls(ip_netmask=ip_netmask, **kwargs)

    @classmethod
    def with_fqdn(cls, fqdn="example.com", **kwargs):
        return cls(fqdn=fqdn, **kwargs)

    @classmethod
    def with_ip_range(cls, ip_range="192.168.0.1-192.168.0.10", **kwargs):
        return cls(ip_range=ip_range, **kwargs)

    @classmethod
    def with_ip_wildcard(cls, ip_wildcard="10.20.1.0/0.0.248.255", **kwargs):
        return cls(ip_wildcard=ip_wildcard, **kwargs)

    @classmethod
    def with_snippet(cls, **kwargs):
        return cls(folder=None, snippet="TestSnippet", **kwargs)

    @classmethod
    def with_device(cls, **kwargs):
        return cls(folder=None, device="TestDevice", **kwargs)

    @classmethod
    def from_request(cls, request_model: AddressCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class AddressCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for AddressCreateModel."""

    name = factory.Sequence(lambda n: f"address_{n}")
    description = factory.Faker("sentence")
    tag = [
        "test-tag",
        "environment-prod",
    ]

    # We intentionally omit the address type fields to simulate missing them

    @classmethod
    def build_without_type(cls):
        """Return a data dict without the required address type fields."""
        return cls(
            name="Test123",
            folder="Shared",
            # No address type fields provided
        )

    @classmethod
    def build_with_multiple_types(cls):
        """Return a data dict multiple type fields."""
        return cls(
            name="Test123",
            folder="Shared",
            ip_netmask="1.1.1.1/32",
            fqdn="example.com",
        )

    @classmethod
    def build_with_no_containers(cls):
        """Return a data dict without any containers."""
        return cls(
            name="Test123",
            fqdn="example.com",
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict multiple containers."""
        return cls(
            name="Test123",
            folder="Shared",
            snippet="this will fail",
            fqdn="example.com",
        )

    @classmethod
    def build_valid(cls):
        """Return a data dict with all the expected attributes."""
        return cls(
            name="Test123",
            ip_netmask="10.5.0.11",
            folder="Texas",
            tag=["Python", "Automation"],
            description="This is a test",
        )


class AddressUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for AddressCreateModel."""

    name = factory.Sequence(lambda n: f"address_{n}")
    description = factory.Faker("sentence")
    folder = "Shared"
    tag = [
        "test-tag",
        "environment-prod",
    ]

    # We intentionally omit the address type fields to simulate missing them

    @classmethod
    def build_without_type(cls):
        """Return a data dict without the required address type fields."""
        return cls(
            name="Test123",
            folder="Shared",
            # No address type fields provided
        )

    @classmethod
    def build_with_multiple_types(cls):
        """Return a data dict multiple type fields."""
        return cls(
            name="Test123",
            folder="Shared",
            ip_netmask="1.1.1.1/32",
            fqdn="example.com",
        )

    @classmethod
    def build_with_no_containers(cls):
        """Return a data dict without any containers."""
        return cls(
            name="Test123",
            fqdn="example.com",
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict multiple containers."""
        return cls(
            name="Test123",
            folder="Shared",
            snippet="this will fail",
            fqdn="example.com",
        )

    @classmethod
    def build_valid(cls):
        """Return a data dict with all the expected attributes."""
        return cls(
            id="12345678-1234-5678-1234-567812345678",
            name="Test123",
            ip_netmask="10.5.0.11",
            folder="Texas",
            tag=["Python", "Automation"],
            description="This is a test",
        )


# ----------------------------------------------------------------------------
# Address Group object factories.
# ----------------------------------------------------------------------------


# Sub factories
class DynamicFilterFactory(factory.Factory):
    class Meta:
        model = DynamicFilter

    filter = "'aws.ec2.key.Name.value.scm-test-scm-test-vpc'"


# SDK tests against SCM API
class AddressGroupCreateApiFactory(factory.Factory):
    """Factory for creating AddressGroupCreateModel instances with different group types."""

    class Meta:
        model = AddressGroupCreateModel

    name = factory.Sequence(lambda n: f"address_group_{n}")
    description = factory.Faker("sentence")
    folder = "Shared"
    tag = ["test-tag", "environment-prod"]

    # Address group types default to None
    dynamic = None
    static = None

    @classmethod
    def with_static(cls, static=None, **kwargs):
        """Create an AddressGroupCreateModel instance with a static address group."""
        if static is None:
            static = [
                "address-object1",
                "address-object2",
                "address-object3",
                "address-object4",
            ]
        return cls(static=static, **kwargs)

    @classmethod
    def with_dynamic(cls, filter_str=None, **kwargs):
        """Create an AddressGroupCreateModel instance with a dynamic address group."""
        if filter_str is None:
            dynamic_filter = DynamicFilterFactory()
        else:
            dynamic_filter = DynamicFilter(filter=filter_str)
        return cls(dynamic=dynamic_filter, **kwargs)

    @classmethod
    def with_snippet(cls, **kwargs):
        return cls(folder=None, snippet="TestSnippet", **kwargs)

    @classmethod
    def with_device(cls, **kwargs):
        return cls(folder=None, device="TestDevice", **kwargs)


class AddressGroupUpdateApiFactory(factory.Factory):
    """Factory for creating AddressGroupUpdateModel instances."""

    class Meta:
        model = AddressGroupUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"address_group_{n}")
    description = factory.Faker("sentence")
    tag = ["updated-tag"]

    # Address group types default to None
    dynamic = None
    static = None

    @classmethod
    def with_static(cls, static=None, **kwargs):
        """Create an AddressGroupUpdateModel instance with a static address group."""
        if static is None:
            static = ["address-object1", "address-object2"]
        return cls(static=static, **kwargs)

    @classmethod
    def with_dynamic(cls, filter_str=None, **kwargs):
        """Create an AddressGroupUpdateModel instance with a dynamic address group."""
        if filter_str is None:
            dynamic_filter = DynamicFilterFactory()
        else:
            dynamic_filter = DynamicFilter(filter=filter_str)
        return cls(dynamic=dynamic_filter, **kwargs)

    @classmethod
    def with_snippet(cls, **kwargs):
        return cls(folder=None, snippet="TestSnippet", **kwargs)

    @classmethod
    def with_device(cls, **kwargs):
        return cls(folder=None, device="TestDevice", **kwargs)


class AddressGroupResponseFactory(factory.Factory):
    """Factory for creating AddressGroupResponseModel instances."""

    class Meta:
        model = AddressGroupResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"address_group_{n}")
    description = factory.Faker("sentence")
    folder = "Shared"
    tag = ["response-tag"]

    # Address group types default to None
    dynamic = None
    static = None

    @classmethod
    def with_static(cls, static=None, **kwargs):
        """Create an AddressGroupResponseModel instance with a static address group."""
        if static is None:
            static = ["address-object1", "address-object2", "address-object3"]
        return cls(static=static, **kwargs)

    @classmethod
    def with_dynamic(cls, filter_str=None, **kwargs):
        """Create an AddressGroupResponseModel instance with a dynamic address group."""
        if filter_str is None:
            dynamic_filter = DynamicFilterFactory()
        else:
            dynamic_filter = DynamicFilter(filter=filter_str)
        return cls(dynamic=dynamic_filter, **kwargs)

    @classmethod
    def with_snippet(cls, **kwargs):
        return cls(folder=None, snippet="TestSnippet", **kwargs)

    @classmethod
    def with_device(cls, **kwargs):
        return cls(folder=None, device="TestDevice", **kwargs)

    @classmethod
    def from_request(cls, request_model: AddressGroupCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class AddressGroupCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for AddressGroupCreateModel."""

    name = factory.Sequence(lambda n: f"address_group_{n}")
    description = factory.Faker("sentence")
    folder = "Shared"
    tag = ["test-tag", "environment-prod"]

    # Group type fields default to None
    dynamic = None
    static = None

    @classmethod
    def build_without_type(cls):
        """Return a data dict without the required group type fields."""
        return cls(
            name="TestAddressGroup",
            folder="Shared",
            # No group type fields provided
        )

    @classmethod
    def build_with_multiple_types(cls):
        """Return a data dict with multiple type fields."""
        return cls(
            name="TestAddressGroup",
            folder="Shared",
            static=["address1", "address2"],
            dynamic={"filter": "'tag1 and tag2'"},
        )

    @classmethod
    def build_with_no_containers(cls):
        """Return a data dict without any containers."""
        return cls(
            name="TestAddressGroup",
            static=["address1", "address2"],
            # No folder, snippet, or device
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="TestAddressGroup",
            folder="Shared",
            snippet="this will fail",
            static=["address1", "address2"],
        )

    @classmethod
    def build_valid_static(cls):
        """Return a valid data dict for a static address group."""
        return cls(
            name="TestAddressGroup",
            static=["address1", "address2"],
            folder="Shared",
            tag=["Python", "Automation"],
            description="This is a test static address group",
        )

    @classmethod
    def build_valid_dynamic(cls):
        """Return a valid data dict for a dynamic address group."""
        return cls(
            name="TestAddressGroup",
            dynamic={"filter": "'tag1 and tag2'"},
            folder="Shared",
            tag=["Python", "Automation"],
            description="This is a test dynamic address group",
        )


class AddressGroupUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for AddressGroupUpdateModel."""

    id = "12345678-1234-5678-1234-567812345678"
    name = factory.Sequence(lambda n: f"address_group_{n}")
    description = factory.Faker("sentence")
    tag = ["test-tag", "environment-prod"]

    # Group type fields default to None
    dynamic = None
    static = None

    @classmethod
    def build_without_type(cls):
        """Return a data dict without the required group type fields."""
        return cls(
            id="12345678-1234-5678-1234-567812345678",
            name="TestAddressGroup",
            folder="Shared",
            # No group type fields provided
        )

    @classmethod
    def build_with_multiple_types(cls):
        """Return a data dict with multiple type fields."""
        return cls(
            id="12345678-1234-5678-1234-567812345678",
            name="TestAddressGroup",
            folder="Shared",
            static=["address1", "address2"],
            dynamic={"filter": "'tag1 and tag2'"},
        )

    @classmethod
    def build_valid_static(cls):
        """Return a valid data dict for a static address group."""
        return cls(
            id="12345678-1234-5678-1234-567812345678",
            name="TestAddressGroup",
            static=["address1", "address2"],
            folder="Shared",
            tag=["Python", "Automation"],
            description="This is a test static address group",
        )

    @classmethod
    def build_valid_dynamic(cls):
        """Return a valid data dict for a dynamic address group."""
        return cls(
            id="12345678-1234-5678-1234-567812345678",
            name="TestAddressGroup",
            dynamic={"filter": "'tag1 and tag2'"},
            folder="Shared",
            tag=["Python", "Automation"],
            description="This is a test dynamic address group",
        )


# ----------------------------------------------------------------------------
# Application object factories.
# ----------------------------------------------------------------------------


# SDK tests against SCM API
class ApplicationCreateApiFactory(factory.Factory):
    """Factory for creating ApplicationCreateModel instances."""

    class Meta:
        model = ApplicationCreateModel

    name = factory.Sequence(lambda n: f"application_{n}")
    description = factory.Faker("sentence")
    category = "general-internet"
    subcategory = "file-sharing"
    technology = "client-server"
    risk = 1
    ports = ["tcp/80,443", "udp/3478"]
    folder = "Prisma Access"
    snippet = None

    # Boolean attributes with explicit defaults
    evasive = False
    pervasive = False
    excessive_bandwidth_use = False
    used_by_malware = False
    transfers_files = False
    has_known_vulnerabilities = False
    tunnels_other_apps = False
    prone_to_misuse = False
    no_certifications = False

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, **kwargs)

    @classmethod
    def with_high_risk(cls, **kwargs):
        """Create an instance with high risk level."""
        return cls(risk=5, **kwargs)

    @classmethod
    def with_all_boolean_flags(cls, value: bool = True, **kwargs):
        """Create an instance with all boolean flags set to specified value."""
        return cls(
            evasive=value,
            pervasive=value,
            excessive_bandwidth_use=value,
            used_by_malware=value,
            transfers_files=value,
            has_known_vulnerabilities=value,
            tunnels_other_apps=value,
            prone_to_misuse=value,
            no_certifications=value,
            **kwargs,
        )

    @classmethod
    def build_with_invalid_name(cls, **kwargs):
        """Return an instance with invalid name pattern."""
        return cls(name="invalid@name#here", **kwargs)

    @classmethod
    def build_with_invalid_risk(cls, **kwargs):
        """Return an instance with invalid risk value."""
        return cls(risk=-1, **kwargs)


class ApplicationUpdateApiFactory(factory.Factory):
    """Factory for creating ApplicationUpdateModel instances."""

    class Meta:
        model = ApplicationUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    # All fields are optional for partial updates
    name = None
    description = None
    category = None
    subcategory = None
    technology = None
    risk = None
    ports = None

    # Boolean attributes
    evasive = None
    pervasive = None
    excessive_bandwidth_use = None
    used_by_malware = None
    transfers_files = None
    has_known_vulnerabilities = None
    tunnels_other_apps = None
    prone_to_misuse = None
    no_certifications = None

    @classmethod
    def with_risk_update(cls, risk: int = 3, **kwargs):
        """Create an instance updating only the risk level."""
        return cls(risk=risk, **kwargs)

    @classmethod
    def with_boolean_updates(cls, **kwargs):
        """Create an instance updating all boolean flags."""
        return cls(
            evasive=True,
            pervasive=True,
            excessive_bandwidth_use=True,
            used_by_malware=True,
            transfers_files=True,
            has_known_vulnerabilities=True,
            tunnels_other_apps=True,
            prone_to_misuse=True,
            no_certifications=True,
            **kwargs,
        )


class ApplicationResponseFactory(factory.Factory):
    """Factory for creating ApplicationResponseModel instances."""

    class Meta:
        model = ApplicationResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"application_{n}")
    description = factory.Faker("paragraph", nb_sentences=5)
    category = "general-internet"
    subcategory = "file-sharing"
    technology = "client-server"
    risk = 1
    ports = ["tcp/80,443", "udp/3478"]
    folder = "Prisma Access"
    snippet = None

    # Boolean attributes
    evasive = False
    pervasive = False
    excessive_bandwidth_use = False
    used_by_malware = False
    transfers_files = False
    has_known_vulnerabilities = False
    tunnels_other_apps = False
    prone_to_misuse = False
    no_certifications = False

    @classmethod
    def with_long_description(cls, length: int = 4000, **kwargs):
        """Create an instance with a description near the maximum length."""
        return cls(description="A" * length, **kwargs)

    @classmethod
    def with_unknown_app(cls, **kwargs):
        """Create an instance for unknown-tcp application type."""
        return cls(
            name="unknown-tcp",
            subcategory=None,
            technology=None,
            risk=1,
            **kwargs,
        )


# Pydantic modeling tests
class ApplicationCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for ApplicationCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"application_{n}")
    description = factory.Faker("sentence")
    category = "general-internet"
    subcategory = "file-sharing"
    technology = "client-server"
    risk = 1
    ports = ["tcp/80,443", "udp/3478"]
    folder = "Prisma Access"
    snippet = None

    @classmethod
    def build_with_invalid_ports(cls, **kwargs):
        """Return a data dict with invalid port format."""
        return cls(ports=["invalid-port-format"], **kwargs)

    @classmethod
    def build_with_invalid_folder(cls, **kwargs):
        """Return a data dict with invalid folder pattern."""
        return cls(folder="Invalid@Folder#Pattern", **kwargs)


class ApplicationUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for ApplicationUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = None
    description = None
    category = None
    subcategory = None
    technology = None
    risk = None
    ports = None

    @classmethod
    def build_with_invalid_fields(cls, **kwargs):
        """Return a data dict with multiple invalid fields."""
        return cls(
            name="invalid@name",
            risk=-1,
            ports=["invalid-port"],
            folder="Invalid@Folder",
            **kwargs,
        )


# ----------------------------------------------------------------------------
# Application Group object factories.
# ----------------------------------------------------------------------------


# SDK tests against SCM API
class ApplicationGroupCreateApiFactory(factory.Factory):
    """Factory for creating ApplicationGroupCreateModel instances."""

    class Meta:
        model = ApplicationGroupCreateModel

    name = factory.Sequence(lambda n: f"application_group_{n}")
    members = [
        "office365-consumer-access",
        "office365-enterprise-access",
    ]
    folder = "Shared"
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
    def with_members(cls, members: list[str], **kwargs):
        """Create an instance with specific members."""
        return cls(members=members, **kwargs)

    @classmethod
    def with_single_member(cls, member: str = "single-app", **kwargs):
        """Create an instance with a single member."""
        return cls(members=[member], **kwargs)


class ApplicationGroupUpdateApiFactory(factory.Factory):
    """Factory for creating ApplicationGroupUpdateModel instances."""

    class Meta:
        model = ApplicationGroupUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"application_group_{n}")
    members = [
        "office365-consumer-access",
        "office365-enterprise-access",
    ]
    folder = None
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
    def with_members(cls, members: list[str], **kwargs):
        """Create an instance with specific members."""
        return cls(members=members, **kwargs)


class ApplicationGroupResponseFactory(factory.Factory):
    """Factory for creating ApplicationGroupResponseModel instances."""

    class Meta:
        model = ApplicationGroupResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"application_group_{n}")
    members = [
        "office365-consumer-access",
        "office365-enterprise-access",
    ]
    folder = "Shared"
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
    def with_members(cls, members: list[str], **kwargs):
        """Create an instance with specific members."""
        return cls(members=members, **kwargs)

    @classmethod
    def from_request(cls, request_model: ApplicationGroupCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class ApplicationGroupCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for ApplicationGroupCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"application_group_{n}")
    members = [
        "office365-consumer-access",
        "office365-enterprise-access",
    ]
    folder = "Shared"
    snippet = None
    device = None

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestApplicationGroup",
            members=["app1", "app2"],
            folder="Shared",
        )

    @classmethod
    def build_with_invalid_name(cls):
        """Return a data dict with invalid name pattern."""
        return cls(
            name="@invalid-name#",
            members=["app1"],
            folder="Shared",
        )

    @classmethod
    def build_with_empty_members(cls):
        """Return a data dict with empty members list."""
        return cls(
            name="TestGroup",
            members=[],
            folder="Shared",
        )

    @classmethod
    def build_with_invalid_folder(cls):
        """Return a data dict with invalid folder pattern."""
        return cls(
            name="TestGroup",
            members=["app1"],
            folder="Invalid@Folder#",
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="TestGroup",
            members=["app1"],
            folder="Shared",
            snippet="TestSnippet",
        )

    @classmethod
    def build_with_no_container(cls):
        """Return a data dict without any container."""
        return cls(
            name="TestGroup",
            members=["app1"],
        )


class ApplicationGroupUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for ApplicationGroupUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"application_group_{n}")
    members = [
        "office365-consumer-access",
        "office365-enterprise-access",
    ]
    folder = None
    snippet = None
    device = None

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating an application group."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedGroup",
            members=["updated-app1", "updated-app2"],
            folder="UpdatedFolder",
        )

    @classmethod
    def build_with_invalid_fields(cls):
        """Return a data dict with multiple invalid fields."""
        return cls(
            id="invalid-uuid",
            name="@invalid-name",
            members=[],
            folder="Invalid@Folder",
        )

    @classmethod
    def build_minimal_update(cls):
        """Return a data dict with minimal valid update fields."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            members=["new-app"],
        )


# ----------------------------------------------------------------------------
# Service object factories.
# ----------------------------------------------------------------------------


# Sub factories
class OverrideFactory(factory.Factory):
    """Factory for creating Override instances."""

    class Meta:
        model = Override

    timeout = 10
    halfclose_timeout = 10
    timewait_timeout = 10


class TCPProtocolFactory(factory.Factory):
    """Factory for creating TCPProtocol instances."""

    class Meta:
        model = TCPProtocol

    port = "80,443"
    override = factory.SubFactory(OverrideFactory)


class UDPProtocolFactory(factory.Factory):
    """Factory for creating UDPProtocol instances."""

    class Meta:
        model = UDPProtocol

    port = "53"
    override = factory.SubFactory(OverrideFactory)


# SDK tests against SCM API
class ServiceCreateApiFactory(factory.Factory):
    """Factory for creating ServiceCreateModel instances with different protocols."""

    class Meta:
        model = ServiceCreateModel

    name = factory.Sequence(lambda n: f"service_{n}")
    description = factory.Faker("sentence")
    folder = "Shared"
    snippet = None
    device = None
    tag = ["test-tag", "environment-prod"]
    protocol = None  # Will be set in specific methods

    @classmethod
    def with_tcp(cls, port="80,443", **kwargs):
        """Create a ServiceCreateModel instance with TCP protocol."""
        return cls(protocol={"tcp": {"port": port}}, **kwargs)

    @classmethod
    def with_udp(cls, port="53", **kwargs):
        """Create a ServiceCreateModel instance with UDP protocol."""
        return cls(protocol={"udp": {"port": port}}, **kwargs)

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def build_without_protocol(cls, **kwargs):
        """Return an instance without the required protocol field."""
        return cls(protocol=None, **kwargs)

    @classmethod
    def build_with_multiple_protocols(cls, **kwargs):
        """Return an instance with both TCP and UDP protocols."""
        return cls(
            protocol={
                "tcp": {"port": "80"},
                "udp": {"port": "53"},
            },
            **kwargs,
        )

    @classmethod
    def build_with_no_containers(cls, **kwargs):
        """Return an instance without any containers."""
        return cls(folder=None, snippet=None, device=None, **kwargs)

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Return an instance with multiple containers (should fail validation)."""
        return cls(folder="Shared", snippet="TestSnippet", device=None, **kwargs)


class ServiceUpdateApiFactory(factory.Factory):
    """Factory for creating ServiceUpdateModel instances."""

    class Meta:
        model = ServiceUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"service_{n}")
    description = factory.Faker("sentence")
    tag = ["updated-tag"]
    protocol = None  # Will be set in specific methods

    @classmethod
    def with_tcp(cls, port="80,443", **kwargs):
        """Create a ServiceUpdateModel instance with TCP protocol."""
        return cls(protocol={"tcp": {"port": port}}, **kwargs)

    @classmethod
    def with_udp(cls, port="53", **kwargs):
        """Create a ServiceUpdateModel instance with UDP protocol."""
        return cls(protocol={"udp": {"port": port}}, **kwargs)

    @classmethod
    def build_without_protocol(cls, **kwargs):
        """Return an instance without the required protocol field."""
        return cls(protocol=None, **kwargs)

    @classmethod
    def build_with_multiple_protocols(cls, **kwargs):
        """Return an instance with both TCP and UDP protocols."""
        return cls(
            protocol={
                "tcp": {"port": "80"},
                "udp": {"port": "53"},
            },
            **kwargs,
        )

    @classmethod
    def build_with_no_containers(cls, **kwargs):
        """Return an instance without any containers."""
        return cls(folder=None, snippet=None, device=None, **kwargs)

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Return an instance with multiple containers."""
        return cls(folder="Shared", snippet="TestSnippet", device=None, **kwargs)


class ServiceResponseFactory(factory.Factory):
    """Factory for creating ServiceResponseModel instances."""

    class Meta:
        model = ServiceResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"service_{n}")
    description = factory.Faker("sentence")
    folder = "Shared"
    snippet = None
    device = None
    tag = ["response-tag"]
    protocol = None  # Will be set in specific methods

    @classmethod
    def with_tcp(cls, port="80,443", **kwargs):
        """Create a ServiceResponseModel instance with TCP protocol."""
        return cls(protocol={"tcp": {"port": port}}, **kwargs)

    @classmethod
    def with_tcp_override(
        cls,
        port="80,443",
        timeout=None,
        halfclose_timeout=None,
        timewait_timeout=None,
        **kwargs,
    ):
        """Create a ServiceResponseModel instance with TCP protocol and override settings."""
        protocol = {"tcp": {"port": port}}

        if any(x is not None for x in [timeout, halfclose_timeout, timewait_timeout]):
            protocol["tcp"]["override"] = {}
            if timeout is not None:
                protocol["tcp"]["override"]["timeout"] = timeout
            if halfclose_timeout is not None:
                protocol["tcp"]["override"]["halfclose_timeout"] = halfclose_timeout
            if timewait_timeout is not None:
                protocol["tcp"]["override"]["timewait_timeout"] = timewait_timeout

        return cls(protocol=protocol, **kwargs)

    @classmethod
    def with_udp(cls, port="53", **kwargs):
        """Create a ServiceResponseModel instance with UDP protocol."""
        return cls(protocol={"udp": {"port": port}}, **kwargs)

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def from_request(cls, request_model: ServiceCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class ServiceCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for ServiceCreateModel."""

    name = factory.Sequence(lambda n: f"service_{n}")
    description = factory.Faker("sentence")
    folder = "Shared"
    snippet = None
    device = None
    tag = ["test-tag", "environment-prod"]
    protocol = None  # Will be set in specific methods

    @classmethod
    def build_without_protocol(cls, **kwargs):
        """Return a data dict without the required protocol field."""
        return cls(protocol=None, **kwargs)

    @classmethod
    def build_with_multiple_protocols(cls, **kwargs):
        """Return a data dict with both TCP and UDP protocols."""
        return cls(
            protocol={
                "tcp": {"port": "80"},
                "udp": {"port": "53"},
            },
            **kwargs,
        )

    @classmethod
    def build_with_no_containers(cls, **kwargs):
        """Return a data dict without any containers."""
        return cls(folder=None, snippet=None, device=None, **kwargs)

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Return a data dict with multiple containers."""
        return cls(
            folder="Shared",
            snippet="TestSnippet",
            protocol={"tcp": {"port": "80,443"}},
            device=None,
            **kwargs,
        )

    @classmethod
    def build_valid_tcp(cls, **kwargs):
        """Return a valid data dict for a TCP service."""
        return cls(protocol={"tcp": {"port": "80,443"}}, **kwargs)

    @classmethod
    def build_valid_udp(cls, **kwargs):
        """Return a valid data dict for a UDP service."""
        return cls(protocol={"udp": {"port": "53"}}, **kwargs)


class ServiceUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for ServiceUpdateModel."""

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"service_{n}")
    description = factory.Faker("sentence")
    tag = ["updated-tag"]
    protocol = None  # Will be set in specific methods

    @classmethod
    def build_without_protocol(cls, **kwargs):
        """Return a data dict without the required protocol field."""
        return cls(protocol=None, **kwargs)

    @classmethod
    def build_with_multiple_protocols(cls, **kwargs):
        """Return a data dict with both TCP and UDP protocols."""
        return cls(
            protocol={
                "tcp": {"port": "80"},
                "udp": {"port": "53"},
            },
            **kwargs,
        )

    @classmethod
    def build_with_no_containers(cls, **kwargs):
        """Return a data dict without any containers."""
        return cls(folder=None, snippet=None, device=None, **kwargs)

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Return a data dict with multiple containers."""
        return cls(folder="Shared", snippet="TestSnippet", device=None, **kwargs)

    @classmethod
    def build_valid(cls, **kwargs):
        """Return a valid data dict for updating a service."""
        return cls(protocol={"tcp": {"port": "80,443"}}, **kwargs)


# ----------------------------------------------------------------------------
# Tag object factories.
# ----------------------------------------------------------------------------


# SDK tests against SCM API
class TagCreateApiFactory(factory.Factory):
    """Factory for creating TagCreateModel instances."""

    class Meta:
        model = TagCreateModel

    name = factory.Sequence(lambda n: f"tag_{n}")
    comments = factory.Faker("sentence")
    color = None  # Default to None; can be set using with_color()
    folder = "Shared"
    snippet = None
    device = None

    @classmethod
    def with_folder(cls, folder="Shared", **kwargs):
        """Create a tag with a specific folder."""
        return cls(folder=folder, snippet=None, device=None, **kwargs)

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Create a tag with a snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """Create a tag with a device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def with_color(cls, color="Red", **kwargs):
        """Create a tag with a specific color."""
        return cls(color=color, **kwargs)


class TagUpdateApiFactory(factory.Factory):
    """Factory for creating TagUpdateModel instances."""

    class Meta:
        model = TagUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"tag_{n}")
    comments = factory.Faker("sentence")
    color = None  # Default to None; can be set using with_color()

    @classmethod
    def with_color(cls, color="Blue", **kwargs):
        """Update a tag with a specific color."""
        return cls(color=color, **kwargs)


class TagResponseFactory(factory.Factory):
    """Factory for creating TagResponseModel instances."""

    class Meta:
        model = TagResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"tag_{n}")
    comments = factory.Faker("sentence")
    color = None
    folder = "Shared"
    snippet = None
    device = None

    @classmethod
    def with_folder(cls, folder="Shared", **kwargs):
        """Create a response model with a specific folder."""
        return cls(folder=folder, snippet=None, device=None, **kwargs)

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Create a response model with a snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """Create a response model with a device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def with_color(cls, color="Red", **kwargs):
        """Create a response model with a specific color."""
        return cls(color=color, **kwargs)

    @classmethod
    def from_request(cls, request_model: TagCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class TagCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for TagCreateModel."""

    name = factory.Sequence(lambda n: f"tag_{n}")
    comments = factory.Faker("sentence")
    color = "Red"  # Default color; can be overridden
    folder = "Shared"
    snippet = None
    device = None

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestTag",
            comments="This is a test tag",
            color="Blue",
            folder="Texas",
        )

    @classmethod
    def build_with_invalid_color(cls):
        """Return a data dict with an invalid color."""
        return cls(
            name="InvalidColorTag",
            comments="This tag has an invalid color",
            color="InvalidColor",
            folder="Shared",
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers (should fail validation)."""
        return cls(
            name="TestTag",
            folder="Shared",
            snippet="MySnippet",
            color="Blue",
        )

    @classmethod
    def build_with_no_container(cls):
        """Return a data dict without any containers (should fail validation)."""
        return cls(
            name="TestTag",
            color="Blue",
            # No folder, snippet, or device provided
        )


class TagUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for TagUpdateModel."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"tag_{n}")
    comments = factory.Faker("sentence")
    color = "Green"

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating a tag."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedTag",
            comments="This is an updated test tag",
            color="Yellow",
        )

    @classmethod
    def build_with_invalid_color(cls):
        """Return a data dict with an invalid color."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="InvalidColorTag",
            color="InvalidColor",
        )


# ----------------------------------------------------------------------------
# Anti-Spyware Profile object factories.
# ----------------------------------------------------------------------------


# Sub factories
class AntiSpywareExemptIpEntryFactory(factory.Factory):
    """Factory for creating ExemptIpEntry instances."""

    class Meta:
        model = AntiSpywareExemptIpEntry

    name = "192.168.1.1"

    @classmethod
    def with_custom_ip(cls, ip: str = "10.0.0.1", **kwargs):
        """Create an instance with a custom IP address."""
        return cls(name=ip, **kwargs)


class AntiSpywareMicaEngineSpywareEnabledEntryFactory(factory.Factory):
    """Factory for creating MicaEngineSpywareEnabledEntry instances."""

    class Meta:
        model = AntiSpywareMicaEngineSpywareEnabledEntry

    name = factory.Sequence(lambda n: f"mica_engine_{n}")
    inline_policy_action = AntiSpywareInlinePolicyAction.alert

    @classmethod
    def with_action(
        cls,
        action: AntiSpywareInlinePolicyAction = AntiSpywareInlinePolicyAction.drop,
        **kwargs,
    ):
        """Create an instance with a specific inline policy action."""
        return cls(inline_policy_action=action, **kwargs)


class AntiSpywareRuleBaseFactory(factory.Factory):
    """Factory for creating RuleBaseModel instances."""

    class Meta:
        model = AntiSpywareRuleBaseModel

    name = factory.Sequence(lambda n: f"rule_{n}")
    severity = [AntiSpywareSeverity.critical, AntiSpywareSeverity.high]
    category = AntiSpywareCategory.spyware
    threat_name = "any"
    packet_capture = AntiSpywarePacketCapture.disable

    @classmethod
    def with_severity(cls, severities: list[AntiSpywareSeverity], **kwargs):
        """Create an instance with specific severity levels."""
        return cls(severity=severities, **kwargs)

    @classmethod
    def with_category(
        cls, category: AntiSpywareCategory = AntiSpywareCategory.botnet, **kwargs
    ):
        """Create an instance with a specific category."""
        return cls(category=category, **kwargs)


class AntiSpywareThreatExceptionBaseFactory(factory.Factory):
    """Factory for creating ThreatExceptionBase instances."""

    class Meta:
        model = AntiSpywareThreatExceptionBase

    name = factory.Sequence(lambda n: f"exception_{n}")
    packet_capture = AntiSpywarePacketCapture.single_packet
    exempt_ip = factory.LazyAttribute(
        lambda _: [AntiSpywareExemptIpEntry(name="192.168.1.1")]
    )
    notes = "Test exception"

    @classmethod
    def with_multiple_exempt_ips(cls, ips: list[str], **kwargs):
        """Create an instance with multiple exempt IPs."""
        return cls(
            exempt_ip=[AntiSpywareExemptIpEntry(name=ip) for ip in ips], **kwargs
        )


# SDK tests against SCM API
class AntiSpywareProfileCreateApiFactory(factory.Factory):
    """Factory for creating AntiSpywareProfileCreateModel instances."""

    class Meta:
        model = AntiSpywareProfileCreateModel

    name = factory.Sequence(lambda n: f"profile_{n}")
    description = factory.Faker("sentence")
    folder = "Shared"
    cloud_inline_analysis = False
    rules = factory.LazyAttribute(lambda _: [AntiSpywareRuleBaseFactory()])
    threat_exception = factory.LazyAttribute(
        lambda _: [AntiSpywareThreatExceptionBaseFactory()]
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
    def with_mica_engine(cls, entries: list[dict] = None, **kwargs):
        """Create a profile with MICA engine entries."""
        if entries is None:
            entries = [AntiSpywareMicaEngineSpywareEnabledEntryFactory()]
        return cls(mica_engine_spyware_enabled=entries, **kwargs)

    @classmethod
    def with_inline_exceptions(
        cls, urls: list[str] = None, ips: list[str] = None, **kwargs
    ):
        """Create a profile with inline exceptions."""
        return cls(
            inline_exception_edl_url=urls, inline_exception_ip_address=ips, **kwargs
        )


class AntiSpywareProfileUpdateApiFactory(factory.Factory):
    """Factory for creating AntiSpywareProfileUpdateModel instances."""

    class Meta:
        model = AntiSpywareProfileUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"profile_{n}")
    description = factory.Faker("sentence")
    rules = factory.List([factory.SubFactory(AntiSpywareRuleBaseFactory)])
    threat_exception = factory.List(
        [factory.SubFactory(AntiSpywareThreatExceptionBaseFactory)]
    )

    @classmethod
    def with_cloud_inline_analysis(cls, enabled: bool = True, **kwargs):
        """Create an instance with cloud inline analysis enabled/disabled."""
        return cls(cloud_inline_analysis=enabled, **kwargs)

    @classmethod
    def with_empty_rules(cls, **kwargs):
        """Create an instance with no rules."""
        return cls(rules=[], **kwargs)


class AntiSpywareProfileResponseFactory(factory.Factory):
    """Factory for creating AntiSpywareProfileResponseModel instances."""

    class Meta:
        model = AntiSpywareProfileResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"profile_{n}")
    description = factory.Faker("sentence")
    folder = "Shared"
    cloud_inline_analysis = False
    rules = factory.List([factory.SubFactory(AntiSpywareRuleBaseFactory)])
    threat_exception = factory.List(
        [factory.SubFactory(AntiSpywareThreatExceptionBaseFactory)]
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
    def from_request(cls, request_model: AntiSpywareProfileCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class AntiSpywareProfileCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for AntiSpywareProfileCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"profile_{n}")
    description = factory.Faker("sentence")
    folder = "Shared"
    cloud_inline_analysis = False
    rules = []

    @classmethod
    def build_valid(cls):
        """Return a data dict with invalid name pattern."""
        return cls(
            name="valid-profile-name",
            folder="Shared",
            rules=[
                {
                    "name": "TestRule",
                    "severity": [AntiSpywareSeverity.critical],
                    "category": AntiSpywareCategory.spyware,
                }
            ],
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with invalid name pattern."""
        return cls(
            name="valid-profile-name",
            folder="Shared",
            snippet="test123",
            rules=[
                {
                    "name": "TestRule",
                    "severity": [AntiSpywareSeverity.critical],
                    "category": AntiSpywareCategory.spyware,
                }
            ],
        )

    @classmethod
    def build_with_invalid_name(cls):
        """Return a data dict with invalid name pattern."""
        return cls(
            name="@invalid-profile-name",
            folder="Shared",
            rules=[
                {
                    "name": "TestRule",
                    "severity": [AntiSpywareSeverity.critical],
                    "category": AntiSpywareCategory.spyware,
                }
            ],
        )

    @classmethod
    def build_with_invalid_rules(cls):
        """Return a data dict with invalid rules structure."""
        return cls(
            name="TestProfile",
            folder="Shared",
            rules=[
                {
                    "name": "TestRule",
                    "severity": ["invalid"],
                    "category": "invalid",
                }
            ],
        )

    @classmethod
    def build_with_invalid_exceptions(cls):
        """Return a data dict with invalid threat exceptions."""
        return cls(
            name="TestProfile",
            folder="Shared",
            rules=[],
            threat_exception=[
                {
                    "name": "TestException",
                    "packet_capture": "invalid",
                }
            ],
        )


class AntiSpywareProfileUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for AntiSpywareProfileUpdateModel validation testing."""

    id = "12345678-1234-5678-1234-567812345678"
    name = factory.Sequence(lambda n: f"profile_{n}")
    description = factory.Faker("sentence")
    rules = []

    @classmethod
    def build_valid(cls):
        """Return a data dict with invalid name pattern."""
        return cls(
            name="valid-profile-name",
            folder="Shared",
            rules=[
                {
                    "name": "TestRule",
                    "severity": [AntiSpywareSeverity.critical],
                    "category": AntiSpywareCategory.spyware,
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
            threat_exception=[{"invalid": "exception"}],
        )

    @classmethod
    def build_minimal_update(cls):
        """Return a data dict with minimal valid update fields."""
        return cls(
            id="12345678-1234-5678-1234-567812345678",
            description="Updated description",
        )


# ----------------------------------------------------------------------------
# Decryption Profile object factories.
# ----------------------------------------------------------------------------


# Sub factories
class SSLProtocolSettingsFactory(factory.Factory):
    """Factory for creating SSLProtocolSettings instances."""

    class Meta:
        model = SSLProtocolSettings

    auth_algo_md5 = True
    auth_algo_sha1 = True
    auth_algo_sha256 = True
    auth_algo_sha384 = True
    enc_algo_3des = True
    enc_algo_aes_128_cbc = True
    enc_algo_aes_128_gcm = True
    enc_algo_aes_256_cbc = True
    enc_algo_aes_256_gcm = True
    enc_algo_chacha20_poly1305 = True
    enc_algo_rc4 = True
    keyxchg_algo_dhe = True
    keyxchg_algo_ecdhe = True
    keyxchg_algo_rsa = True
    max_version = SSLVersion.tls1_2
    min_version = SSLVersion.tls1_0

    @classmethod
    def with_versions(cls, min_ver: SSLVersion, max_ver: SSLVersion, **kwargs):
        """Create an instance with specific SSL/TLS versions."""
        return cls(min_version=min_ver, max_version=max_ver, **kwargs)


class SSLForwardProxyFactory(factory.Factory):
    """Factory for creating SSLForwardProxy instances."""

    class Meta:
        model = SSLForwardProxy

    auto_include_altname = False
    block_client_cert = False
    block_expired_certificate = False
    block_timeout_cert = False
    block_tls13_downgrade_no_resource = False
    block_unknown_cert = False
    block_unsupported_cipher = False
    block_unsupported_version = False
    block_untrusted_issuer = False
    restrict_cert_exts = False
    strip_alpn = False

    @classmethod
    def with_all_blocks_enabled(cls, **kwargs):
        """Create an instance with all blocking options enabled."""
        return cls(
            block_client_cert=True,
            block_expired_certificate=True,
            block_timeout_cert=True,
            block_tls13_downgrade_no_resource=True,
            block_unknown_cert=True,
            block_unsupported_cipher=True,
            block_unsupported_version=True,
            block_untrusted_issuer=True,
            **kwargs,
        )


class SSLInboundProxyFactory(factory.Factory):
    """Factory for creating SSLInboundProxy instances."""

    class Meta:
        model = SSLInboundProxy

    block_if_hsm_unavailable = False
    block_if_no_resource = False
    block_unsupported_cipher = False
    block_unsupported_version = False

    @classmethod
    def with_all_blocks_enabled(cls, **kwargs):
        """Create an instance with all blocking options enabled."""
        return cls(
            block_if_hsm_unavailable=True,
            block_if_no_resource=True,
            block_unsupported_cipher=True,
            block_unsupported_version=True,
            **kwargs,
        )


class SSLNoProxyFactory(factory.Factory):
    """Factory for creating SSLNoProxy instances."""

    class Meta:
        model = SSLNoProxy

    block_expired_certificate = False
    block_untrusted_issuer = False

    @classmethod
    def with_all_blocks_enabled(cls, **kwargs):
        """Create an instance with all blocking options enabled."""
        return cls(
            block_expired_certificate=True,
            block_untrusted_issuer=True,
            **kwargs,
        )


# SDK tests against SCM API
class DecryptionProfileCreateApiFactory(factory.Factory):
    """Factory for creating DecryptionProfileCreateModel instances."""

    class Meta:
        model = DecryptionProfileCreateModel

    name = factory.Sequence(lambda n: f"decryption_profile_{n}")
    folder = "Shared"
    ssl_protocol_settings = factory.SubFactory(SSLProtocolSettingsFactory)
    ssl_forward_proxy = factory.SubFactory(SSLForwardProxyFactory)
    ssl_inbound_proxy = factory.SubFactory(SSLInboundProxyFactory)
    ssl_no_proxy = factory.SubFactory(SSLNoProxyFactory)

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def with_custom_ssl_settings(
        cls,
        min_ver: SSLVersion = SSLVersion.tls1_0,
        max_ver: SSLVersion = SSLVersion.tls1_2,
        **kwargs,
    ):
        """Create an instance with custom SSL protocol settings."""
        return cls(
            ssl_protocol_settings=SSLProtocolSettingsFactory.with_versions(
                min_ver=min_ver, max_ver=max_ver
            ),
            **kwargs,
        )


class DecryptionProfileUpdateApiFactory(factory.Factory):
    """Factory for creating DecryptionProfileUpdateModel instances."""

    class Meta:
        model = DecryptionProfileUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"decryption_profile_{n}")
    ssl_protocol_settings = factory.SubFactory(SSLProtocolSettingsFactory)
    ssl_forward_proxy = factory.SubFactory(SSLForwardProxyFactory)
    ssl_inbound_proxy = factory.SubFactory(SSLInboundProxyFactory)
    ssl_no_proxy = factory.SubFactory(SSLNoProxyFactory)

    @classmethod
    def with_updated_ssl_settings(cls, **kwargs):
        """Create an instance with updated SSL protocol settings."""
        return cls(
            ssl_protocol_settings=SSLProtocolSettingsFactory(
                min_version=SSLVersion.tls1_1,
                max_version=SSLVersion.tls1_3,
            ),
            **kwargs,
        )


class DecryptionProfileResponseFactory(factory.Factory):
    """Factory for creating DecryptionProfileResponseModel instances."""

    class Meta:
        model = DecryptionProfileResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"decryption_profile_{n}")
    folder = "Shared"
    ssl_protocol_settings = factory.SubFactory(SSLProtocolSettingsFactory)
    ssl_forward_proxy = factory.SubFactory(SSLForwardProxyFactory)
    ssl_inbound_proxy = factory.SubFactory(SSLInboundProxyFactory)
    ssl_no_proxy = factory.SubFactory(SSLNoProxyFactory)

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def from_request(cls, request_model: DecryptionProfileCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class DecryptionProfileCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for DecryptionProfileCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"decryption_profile_{n}")
    folder = "Shared"

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestProfile",
            folder="Shared",
            ssl_protocol_settings={
                "min_version": "tls1-0",
                "max_version": "tls1-2",
            },
        )

    @classmethod
    def build_with_invalid_name(cls):
        """Return a data dict with invalid name pattern."""
        return cls(
            name="@invalid-name#",
            folder="Shared",
        )

    @classmethod
    def build_with_invalid_ssl_versions(cls):
        """Return a data dict with invalid SSL version configuration."""
        return cls(
            name="TestProfile",
            folder="Shared",
            ssl_protocol_settings={
                "min_version": "tls1-2",
                "max_version": "tls1-0",  # Invalid: max < min
            },
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="TestProfile",
            folder="Shared",
            snippet="TestSnippet",
        )

    @classmethod
    def build_with_no_container(cls):
        """Return a data dict without any container."""
        return cls(
            name="TestProfile",
            folder=None,
        )


class DecryptionProfileUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for DecryptionProfileUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"decryption_profile_{n}")

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating a decryption profile."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedProfile",
            ssl_protocol_settings={
                "min_version": "tls1-1",
                "max_version": "tls1-3",
            },
        )

    @classmethod
    def build_with_invalid_fields(cls):
        """Return a data dict with multiple invalid fields."""
        return cls(
            id="invalid-uuid",
            name="@invalid-name",
            ssl_protocol_settings={
                "min_version": "invalid-version",
                "max_version": "also-invalid",
            },
        )

    @classmethod
    def build_minimal_update(cls):
        """Return a data dict with minimal valid update fields."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            ssl_forward_proxy={"block_client_cert": True},
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
    folder = "Shared"
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
    def with_action_update(
        cls, action: SecurityRuleAction = SecurityRuleAction.deny, **kwargs
    ):
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
    folder = "Shared"
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

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)

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
    folder = "Shared"
    tag = ["test-tag"]
    action = "allow"

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestRule",
            folder="Shared",
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
            folder="Shared",
            action="allow",
        )

    @classmethod
    def build_with_invalid_action(cls):
        """Return a data dict with invalid action."""
        return cls(
            name="TestRule",
            folder="Shared",
            action="invalid-action",
        )

    @classmethod
    def build_with_duplicate_items(cls):
        """Return a data dict with duplicate list items."""
        return cls(
            name="TestRule",
            folder="Shared",
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

    dns_security_categories = factory.List(
        [factory.SubFactory(DNSSecurityCategoryEntryFactory)]
    )
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
    folder = "Shared"
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
    folder = "Shared"
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
    folder = "Shared"

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestProfile",
            folder="Shared",
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
            folder="Shared",
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="TestProfile",
            folder="Shared",
            snippet="TestSnippet",
        )

    @classmethod
    def build_with_invalid_action(cls):
        """Return a data dict with invalid action in botnet domains."""
        return cls(
            name="TestProfile",
            folder="Shared",
            botnet_domains={
                "dns_security_categories": [
                    {"name": "malware", "action": "invalid-action"}
                ]
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
            botnet_domains={
                "sinkhole": {"ipv4_address": "127.0.0.1", "ipv6_address": "::1"}
            },
        )

    @classmethod
    def build_with_invalid_fields(cls):
        """Return a data dict with multiple invalid fields."""
        return cls(
            id="invalid-uuid",
            name="@invalid-name",
            botnet_domains={
                "dns_security_categories": [{"name": "malware", "action": "invalid"}]
            },
        )

    @classmethod
    def build_minimal_update(cls):
        """Return a data dict with minimal valid update fields."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000", description="Updated description"
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

    @classmethod
    def with_severity(cls, severities: List[VulnerabilityProfileSeverity], **kwargs):
        """Create an instance with specific severity levels."""
        return cls(severity=severities, **kwargs)

    @classmethod
    def with_category(
        cls,
        category: VulnerabilityProfileCategory = VulnerabilityProfileCategory.brute_force,
        **kwargs,
    ):
        """Create an instance with a specific category."""
        return cls(category=category, **kwargs)


class VulnerabilityProfileThreatExceptionModelFactory(factory.Factory):
    """Factory for creating VulnerabilityProfileThreatExceptionModel instances."""

    class Meta:
        model = VulnerabilityProfileThreatExceptionModel

    name = factory.Sequence(lambda n: f"exception_{n}")
    packet_capture = VulnerabilityProfilePacketCapture.single_packet
    exempt_ip = [factory.SubFactory(VulnerabilityProfileExemptIpEntryFactory)]

    @classmethod
    def with_multiple_exempt_ips(cls, ips: List[str], **kwargs):
        """Create an instance with multiple exempt IPs."""
        return cls(
            exempt_ip=[VulnerabilityProfileExemptIpEntryFactory(name=ip) for ip in ips],
            **kwargs,
        )


# SDK tests against SCM API
class VulnerabilityProfileCreateApiFactory(factory.Factory):
    """Factory for creating VulnerabilityProfileCreateModel instances."""

    class Meta:
        model = VulnerabilityProfileCreateModel

    name = factory.Sequence(lambda n: f"vulnerability_profile_{n}")
    description = factory.Faker("sentence")
    folder = "Shared"
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
    folder = "Shared"
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
    folder = "Shared"
    rules = []

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="valid-profile-name",
            folder="Shared",
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
            folder="Shared",
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
            folder="Shared",
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
            folder="Shared",
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
            folder="Shared",
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
    folder = "Shared"
    packet_capture = False
    rules = factory.List([factory.SubFactory(WildfireAvRuleBaseFactory)])
    mlav_exception = factory.List(
        [factory.SubFactory(WildfireAvMlavExceptionEntryFactory)]
    )
    threat_exception = factory.List(
        [factory.SubFactory(WildfireAvThreatExceptionEntryFactory)]
    )

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
    mlav_exception = factory.List(
        [factory.SubFactory(WildfireAvMlavExceptionEntryFactory)]
    )
    threat_exception = factory.List(
        [factory.SubFactory(WildfireAvThreatExceptionEntryFactory)]
    )

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
    folder = "Shared"
    packet_capture = False
    rules = factory.List([factory.SubFactory(WildfireAvRuleBaseFactory)])
    mlav_exception = factory.List(
        [factory.SubFactory(WildfireAvMlavExceptionEntryFactory)]
    )
    threat_exception = factory.List(
        [factory.SubFactory(WildfireAvThreatExceptionEntryFactory)]
    )

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
    folder = "Shared"
    rules = []

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestWildfireProfile",
            folder="Shared",
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
            folder="Shared",
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
            folder="Shared",
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
            folder="Shared",
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
