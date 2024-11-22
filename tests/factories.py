# tests/factories.py

# Standard library imports
import uuid

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
    VulnerabilityProtectionProfileCreateModel,
    VulnerabilityProtectionProfileResponseModel,
    SecurityRuleCreateModel,
    SecurityRuleMoveModel,
)
from scm.models.security.anti_spyware_profiles import (
    PacketCapture,
    ActionRequest,
    ThreatExceptionBase,
    Category,
    Severity,
    AntiSpywareProfileUpdateModel,
    InlinePolicyAction,
    MicaEngineSpywareEnabledEntry,
    ExemptIpEntry,
)
from scm.models.security.anti_spyware_profiles import (
    RuleBaseModel as AntiSpywareRuleBaseModel,
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
    ProfileSetting,
    Rulebase,
    RuleMoveDestination,
    SecurityRuleResponseModel,
)
from scm.models.security.vulnerability_protection_profiles import (
    ThreatExceptionModel,
    VulnerabilityRuleModel,
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
    snippet = None  # Default to None; can be set using with_snippet()

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
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, **kwargs)

    @classmethod
    def build_without_required_fields(cls, **kwargs):
        """Return an instance without required fields (should fail validation)."""
        return cls(
            name=None,
            category=None,
            subcategory=None,
            technology=None,
            risk=None,
            **kwargs,
        )

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Return an instance with multiple containers (should fail validation)."""
        return cls(folder="Shared", snippet="TestSnippet", **kwargs)

    @classmethod
    def build_with_no_container(cls, **kwargs):
        """Return an instance without any container (should fail validation)."""
        return cls(folder=None, snippet=None, **kwargs)

    @classmethod
    def build_with_long_description(cls, **kwargs):
        """Return an instance with description exceeding max_length."""
        long_description = "A" * 2000  # Exceeds 1023 characters
        return cls(description=long_description, **kwargs)

    @classmethod
    def build_valid(cls, **kwargs):
        """Return a valid instance."""
        return cls(**kwargs)


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
    def build_partial_update(cls, **kwargs):
        """Return an instance with partial update data."""
        return cls(
            id=str(uuid.uuid4()),
            name="updated-application",
            description="Updated description",
            **kwargs,
        )

    @classmethod
    def build_full_update(cls, **kwargs):
        """Return an instance with all fields for a full update."""
        return cls(
            id=str(uuid.uuid4()),
            name=factory.Sequence(lambda n: f"application_{n}"),
            description=factory.Faker("sentence"),
            category="general-internet",
            subcategory="file-sharing",
            technology="client-server",
            risk=1,
            ports=["tcp/80,443", "udp/3478"],
            evasive=False,
            pervasive=False,
            excessive_bandwidth_use=False,
            used_by_malware=False,
            transfers_files=False,
            has_known_vulnerabilities=False,
            tunnels_other_apps=False,
            prone_to_misuse=False,
            no_certifications=False,
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
    snippet = None  # Default to None; can be set using with_snippet()

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
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, **kwargs)

    @classmethod
    def without_subcategory_and_technology(cls, **kwargs):
        """Create an instance without subcategory and technology."""
        return cls(subcategory=None, technology=None, **kwargs)

    @classmethod
    def from_request(cls, request_model: ApplicationCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class ApplicationCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for ApplicationCreateModel."""

    name = factory.Sequence(lambda n: f"application_{n}")
    description = factory.Faker("sentence")
    category = "general-internet"
    subcategory = "file-sharing"
    technology = "client-server"
    risk = 1
    ports = ["tcp/80,443", "udp/3478"]
    folder = "Prisma Access"
    snippet = None  # Default to None; can be set using snippet field

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
    def build_valid(cls, **kwargs):
        """Return a valid data dict for creating an application."""
        return cls(**kwargs)

    @classmethod
    def build_with_missing_required_fields(cls, **kwargs):
        """Return a data dict missing required fields (should fail validation)."""
        return cls(
            name=None,
            category=None,
            subcategory=None,
            technology=None,
            risk=None,
            **kwargs,
        )

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Return a data dict with multiple containers (should fail validation)."""
        return cls(folder="Shared", snippet="TestSnippet", **kwargs)

    @classmethod
    def build_with_no_container(cls, **kwargs):
        """Return a data dict without any container (should fail validation)."""
        return cls(folder=None, snippet=None, **kwargs)

    @classmethod
    def build_with_long_description(cls, **kwargs):
        """Return a data dict with description exceeding max_length."""
        long_description = "A" * 2000  # Exceeds 1023 characters
        return cls(description=long_description, **kwargs)


class ApplicationUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for ApplicationUpdateModel."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    # All fields are optional for updates
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
    def build_valid(cls, **kwargs):
        """Return a valid data dict for updating an application."""
        return cls(**kwargs)

    @classmethod
    def build_partial_update(cls, **kwargs):
        """Return a data dict for partial update."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="updated-application",
            description="Updated description",
            **kwargs,
        )

    @classmethod
    def build_full_update(cls, **kwargs):
        """Return a data dict with all fields for a full update."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name=factory.Sequence(lambda n: f"application_{n}"),
            description=factory.Faker("sentence"),
            category="general-internet",
            subcategory="file-sharing",
            technology="client-server",
            risk=1,
            ports=["tcp/80,443", "udp/3478"],
            evasive=False,
            pervasive=False,
            excessive_bandwidth_use=False,
            used_by_malware=False,
            transfers_files=False,
            has_known_vulnerabilities=False,
            tunnels_other_apps=False,
            prone_to_misuse=False,
            no_certifications=False,
            **kwargs,
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
class ExemptIpEntryFactory(factory.Factory):
    """Factory for creating ExemptIpEntry instances."""

    class Meta:
        model = ExemptIpEntry

    name = "192.168.1.1"


class MicaEngineSpywareEnabledEntryFactory(factory.Factory):
    """Factory for creating MicaEngineSpywareEnabledEntry instances."""

    class Meta:
        model = MicaEngineSpywareEnabledEntry

    name = factory.Sequence(lambda n: f"mica_engine_{n}")
    inline_policy_action = InlinePolicyAction.alert


class AntiSpywareRuleBaseFactory(factory.Factory):
    """Factory for creating AntiSpywareRuleBaseModel instances."""

    class Meta:
        model = AntiSpywareRuleBaseModel

    name = factory.Sequence(lambda n: f"rule_{n}")
    severity = [Severity.critical, Severity.high]
    category = Category.spyware
    threat_name = "any"
    packet_capture = PacketCapture.disable


class ThreatExceptionBaseFactory(factory.Factory):
    """Factory for creating ThreatExceptionBase instances."""

    class Meta:
        model = ThreatExceptionBase

    name = factory.Sequence(lambda n: f"exception_{n}")
    packet_capture = PacketCapture.single_packet
    exempt_ip = [factory.SubFactory(ExemptIpEntryFactory)]
    notes = "Test exception"


# SDK tests against SCM API
class AntiSpywareProfileCreateApiFactory(factory.Factory):
    """Factory for creating AntiSpywareProfileCreateModel instances."""

    class Meta:
        model = AntiSpywareProfileCreateModel

    name = factory.Sequence(lambda n: f"profile_{n}")
    description = factory.Faker("sentence")
    folder = "Shared"
    cloud_inline_analysis = False
    rules = factory.List([factory.SubFactory(AntiSpywareRuleBaseFactory)])
    threat_exception = factory.List([factory.SubFactory(ThreatExceptionBaseFactory)])

    @classmethod
    def with_snippet(cls, **kwargs):
        """Create a profile with snippet container."""
        return cls(folder=None, snippet="TestSnippet", **kwargs)

    @classmethod
    def with_device(cls, **kwargs):
        """Create a profile with device container."""
        return cls(folder=None, device="TestDevice", **kwargs)

    @classmethod
    def with_mica_engine(cls, **kwargs):
        """Create a profile with MICA engine entries."""
        return cls(
            mica_engine_spyware_enabled=[
                factory.SubFactory(MicaEngineSpywareEnabledEntryFactory)
            ],
            **kwargs,
        )


class AntiSpywareProfileUpdateApiFactory(factory.Factory):
    """Factory for creating AntiSpywareProfileUpdateModel instances."""

    class Meta:
        model = AntiSpywareProfileUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"profile_{n}")
    description = factory.Faker("sentence")
    rules = factory.List([factory.SubFactory(AntiSpywareRuleBaseFactory)])
    threat_exception = factory.List([factory.SubFactory(ThreatExceptionBaseFactory)])


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
    threat_exception = factory.List([factory.SubFactory(ThreatExceptionBaseFactory)])

    @classmethod
    def with_snippet(cls, **kwargs):
        """Create a profile with snippet container."""
        return cls(folder=None, snippet="TestSnippet", **kwargs)

    @classmethod
    def with_device(cls, **kwargs):
        """Create a profile with device container."""
        return cls(folder=None, device="TestDevice", **kwargs)

    @classmethod
    def from_request(cls, request_model: AntiSpywareProfileCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class AntiSpywareProfileCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for AntiSpywareProfileCreateModel."""

    name = factory.Sequence(lambda n: f"profile_{n}")
    description = factory.Faker("sentence")
    folder = "Shared"
    cloud_inline_analysis = False
    rules = []

    @classmethod
    def build_without_container(cls):
        """Return a data dict without any containers."""
        return cls(
            name="TestProfile",
            rules=[
                {
                    "name": "TestRule",
                    "severity": [Severity.critical],
                    "category": Category.spyware,
                }
            ],
            # No folder, snippet, or device
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="TestProfile",
            folder="Shared",
            snippet="this will fail",
            rules=[
                {
                    "name": "TestRule",
                    "severity": [Severity.critical],
                    "category": Category.spyware,
                }
            ],
        )

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for creating a profile."""
        return cls(
            name="TestProfile",
            folder="Shared",
            description="Test anti-spyware profile",
            cloud_inline_analysis=True,
            rules=[
                {
                    "name": "TestRule",
                    "severity": [Severity.critical, Severity.high],
                    "category": Category.spyware,
                    "threat_name": "test_threat",
                    "packet_capture": PacketCapture.disable,
                }
            ],
            threat_exception=[
                {
                    "name": "TestException",
                    "packet_capture": PacketCapture.single_packet,
                    "exempt_ip": [{"name": "192.168.1.1"}],
                    "notes": "Test exception",
                }
            ],
        )


class AntiSpywareProfileUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for AntiSpywareProfileUpdateModel."""

    id = "12345678-1234-5678-1234-567812345678"
    name = factory.Sequence(lambda n: f"profile_{n}")
    description = factory.Faker("sentence")
    rules = []

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating a profile."""
        return cls(
            id="12345678-1234-5678-1234-567812345678",
            name="UpdatedProfile",
            description="Updated anti-spyware profile",
            rules=[
                {
                    "name": "UpdatedRule",
                    "severity": [Severity.high],
                    "category": Category.botnet,
                    "packet_capture": PacketCapture.extended_capture,
                }
            ],
            threat_exception=[],
        )


# ----------------------------------------------------------------------------
# Other object factories.
# ----------------------------------------------------------------------------


class SecurityRuleBaseFactory(factory.Factory):
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


class SecurityRuleRequestBaseFactory(SecurityRuleBaseFactory):
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


class SecurityRuleResponseBaseFactory(SecurityRuleBaseFactory):
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


class AntiSpywareRuleCreateFactory(factory.Factory):
    """Factory for creating RuleRequest instances."""

    class Meta:
        model = AntiSpywareRuleBaseModel

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


class VulnerabilityRuleRequestFactory(factory.Factory):
    """Factory for creating VulnerabilityRuleModel instances."""

    class Meta:
        model = VulnerabilityRuleModel

    name = factory.Sequence(lambda n: f"rule_{n}")
    severity = ["critical"]
    category = "dos"
    host = "client"
    threat_name = "any"
    packet_capture = "single-packet"
    action = factory.LazyAttribute(lambda _: {"alert": {}})
    cve = ["any"]
    vendor_id = ["any"]

    @classmethod
    def with_block_ip_action(cls, **kwargs):
        """Create a rule with block_ip action."""
        return cls(
            action={"block_ip": {"track_by": "source", "duration": 3600}}, **kwargs
        )


class ThreatExceptionRequestFactory(factory.Factory):
    """Factory for creating ThreatExceptionModel instances."""

    class Meta:
        model = ThreatExceptionModel

    name = factory.Sequence(lambda n: f"exception_{n}")
    action = factory.LazyAttribute(lambda _: ActionRequest("allow"))
    packet_capture = "single-packet"
    exempt_ip = [{"name": "192.168.1.1"}]
    notes = "Test exception"


class VulnerabilityProtectionProfileRequestFactory(factory.Factory):
    """Factory for creating VulnerabilityProtectionProfileCreateModel instances."""

    class Meta:
        model = VulnerabilityProtectionProfileCreateModel

    name = factory.Sequence(lambda n: f"profile_{n}")
    folder = "Prisma Access"
    description = "Test vulnerability protection profile"
    rules = factory.List([factory.SubFactory(VulnerabilityRuleRequestFactory)])
    threat_exception = factory.List([factory.SubFactory(ThreatExceptionRequestFactory)])

    @classmethod
    def with_snippet(cls, **kwargs):
        """Create a profile with snippet container."""
        return cls(folder=None, snippet="TestSnippet", **kwargs)

    @classmethod
    def with_device(cls, **kwargs):
        """Create a profile with device container."""
        return cls(folder=None, device="TestDevice", **kwargs)


class VulnerabilityProtectionProfileResponseFactory(
    VulnerabilityProtectionProfileRequestFactory
):
    """Factory for creating VulnerabilityProtectionProfileResponseModel instances."""

    class Meta:
        model = VulnerabilityProtectionProfileResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))

    @classmethod
    def from_request(
        cls, request_model: VulnerabilityProtectionProfileCreateModel, **kwargs
    ):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data.update(kwargs)
        return cls(**data)


class ApplicationGroupFactory(factory.Factory):
    class Meta:
        model = ApplicationGroupCreateModel

    name = "ValidStaticApplicationGroup"
    members = [
        "office365-consumer-access",
        "office365-enterprise-access",
    ]
    folder = "Prisma Access"
