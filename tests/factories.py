# tests/factories.py

# Standard library imports
import uuid
from typing import Dict, List, Union

# External libraries
import factory  # type: ignore

from scm.models.deployment import RemoteNetworkCreateModel
from scm.models.deployment.remote_networks import (
    EcmpLoadBalancingEnum,
    EcmpTunnelModel,
    PeeringTypeEnum,
    RemoteNetworkResponseModel,
    RemoteNetworkUpdateModel,
)
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
from scm.models.objects import (
    ServiceCreateModel,
    ServiceGroupCreateModel,
    ServiceGroupResponseModel,
    ServiceGroupUpdateModel,
    ServiceResponseModel,
    ServiceUpdateModel,
    TagCreateModel,
    TagResponseModel,
    TagUpdateModel,
)
from scm.models.objects.service import Override, TCPProtocol, UDPProtocol
from scm.models.security import (
    AntiSpywareProfileCreateModel,
    AntiSpywareProfileResponseModel,
    DecryptionProfileCreateModel,
    DecryptionProfileResponseModel,
    DNSSecurityProfileCreateModel,
    DNSSecurityProfileResponseModel,
    SecurityRuleCreateModel,
    SecurityRuleMoveModel,
    VulnerabilityProfileCreateModel,
    VulnerabilityProfileResponseModel,
)
from scm.models.security.anti_spyware_profiles import (
    AntiSpywareCategory,
    AntiSpywareExemptIpEntry,
    AntiSpywareInlinePolicyAction,
    AntiSpywareMicaEngineSpywareEnabledEntry,
    AntiSpywarePacketCapture,
    AntiSpywareProfileUpdateModel,
)
from scm.models.security.anti_spyware_profiles import (
    AntiSpywareRuleBaseModel as AntiSpywareRuleBaseModel,
)
from scm.models.security.anti_spyware_profiles import (
    AntiSpywareSeverity,
    AntiSpywareThreatExceptionBase,
)
from scm.models.security.decryption_profiles import (
    DecryptionProfileUpdateModel,
    SSLForwardProxy,
    SSLInboundProxy,
    SSLNoProxy,
    SSLProtocolSettings,
    SSLVersion,
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
    folder = "Texas"
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
        return cls(folder="Texas", snippet="TestSnippet", device=None, **kwargs)


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
        return cls(folder="Texas", snippet="TestSnippet", device=None, **kwargs)


class ServiceResponseFactory(factory.Factory):
    """Factory for creating ServiceResponseModel instances."""

    class Meta:
        model = ServiceResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"service_{n}")
    description = factory.Faker("sentence")
    folder = "Texas"
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
    folder = "Texas"
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
            folder="Texas",
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
        return cls(folder="Texas", snippet="TestSnippet", device=None, **kwargs)

    @classmethod
    def build_valid(cls, **kwargs):
        """Return a valid data dict for updating a service."""
        return cls(protocol={"tcp": {"port": "80,443"}}, **kwargs)


# ----------------------------------------------------------------------------
# Service Group object factories.
# ----------------------------------------------------------------------------


# SDK tests against SCM API
class ServiceGroupCreateApiFactory(factory.Factory):
    """Factory for creating ServiceGroupCreateModel instances with members."""

    class Meta:
        model = ServiceGroupCreateModel

    name = factory.Sequence(lambda n: f"service_{n}")
    members = None  # Will be set in specific methods
    tag = ["test-tag", "environment-prod"]
    folder = "Texas"
    snippet = None
    device = None

    @classmethod
    def with_members(cls, **kwargs):
        """Create a ServiceGroupCreateModel instance with two members."""
        return cls(
            folder="Texas",
            members=["test1", "test2"],
            **kwargs,
        )

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(
            folder=None,
            snippet=snippet,
            device=None,
            members=["test1", "test2"],
            **kwargs,
        )

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(
            folder=None,
            snippet=None,
            device=device,
            members=["test1", "test2"],
            **kwargs,
        )

    @classmethod
    def build_without_members(cls, **kwargs):
        """Return an instance without the required protocol field."""
        return cls(
            members=None,
            **kwargs,
        )

    @classmethod
    def build_with_duplicate_protocols(cls, **kwargs):
        """Return an instance with both TCP and UDP protocols."""
        return cls(
            members=["test1", "test1"],
            **kwargs,
        )

    @classmethod
    def build_with_no_containers(cls, **kwargs):
        """Return an instance without any containers."""
        return cls(
            folder=None,
            snippet=None,
            device=None,
            members=["test1", "test1"],
            **kwargs,
        )

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Return an instance with multiple containers (should fail validation)."""
        return cls(
            folder="Texas",
            snippet="TestSnippet",
            device=None,
            members=["test1", "test1"],
            **kwargs,
        )


class ServiceGroupUpdateApiFactory(factory.Factory):
    """Factory for creating ServiceUpdateModel instances."""

    class Meta:
        model = ServiceGroupUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"service_{n}")
    members = None  # Will be set in specific methods
    tag = ["test-tag", "environment-prod"]
    folder = "Texas"
    snippet = None
    device = None

    @classmethod
    def with_members(cls, **kwargs):
        """Create a ServiceGroupCreateModel instance with two members."""
        return cls(
            folder="Texas",
            members=["test1", "test2"],
            **kwargs,
        )

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(
            folder=None,
            snippet=snippet,
            device=None,
            members=["test1", "test2"],
            **kwargs,
        )

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(
            folder=None,
            snippet=None,
            device=device,
            members=["test1", "test2"],
            **kwargs,
        )

    @classmethod
    def build_without_members(cls, **kwargs):
        """Return an instance without the required protocol field."""
        return cls(
            members=None,
            **kwargs,
        )

    @classmethod
    def build_with_duplicate_protocols(cls, **kwargs):
        """Return an instance with both TCP and UDP protocols."""
        return cls(
            members=["test1", "test1"],
            **kwargs,
        )

    @classmethod
    def build_with_no_containers(cls, **kwargs):
        """Return an instance without any containers."""
        return cls(
            folder=None,
            snippet=None,
            device=None,
            members=["test1", "test1"],
            **kwargs,
        )

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Return an instance with multiple containers (should fail validation)."""
        return cls(
            folder="Texas",
            snippet="TestSnippet",
            device=None,
            members=["test1", "test1"],
            **kwargs,
        )


class ServiceGroupResponseFactory(factory.Factory):
    """Factory for creating ServiceResponseModel instances."""

    class Meta:
        model = ServiceGroupResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"service_{n}")
    members = None  # Will be set in specific methods
    tag = ["test-tag", "environment-prod"]
    folder = "Texas"
    snippet = None
    device = None

    @classmethod
    def with_members(cls, **kwargs):
        """Create a ServiceGroupCreateModel instance with two members."""
        return cls(
            folder="Texas",
            members=["test1", "test2"],
            **kwargs,
        )

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(
            folder=None,
            snippet=snippet,
            device=None,
            members=["test1", "test2"],
            **kwargs,
        )

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(
            folder=None,
            snippet=None,
            device=device,
            members=["test1", "test2"],
            **kwargs,
        )

    @classmethod
    def build_without_members(cls, **kwargs):
        """Return an instance without the required protocol field."""
        return cls(
            members=None,
            **kwargs,
        )

    @classmethod
    def build_with_duplicate_protocols(cls, **kwargs):
        """Return an instance with both TCP and UDP protocols."""
        return cls(
            members=["test1", "test1"],
            **kwargs,
        )

    @classmethod
    def build_with_no_containers(cls, **kwargs):
        """Return an instance without any containers."""
        return cls(
            folder=None,
            snippet=None,
            device=None,
            members=["test1", "test1"],
            **kwargs,
        )

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Return an instance with multiple containers (should fail validation)."""
        return cls(
            folder="Texas",
            snippet="TestSnippet",
            device=None,
            members=["test1", "test1"],
            **kwargs,
        )

    @classmethod
    def from_request(cls, request_model: ServiceGroupCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class ServiceGroupCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for ServiceGroupCreateModel."""

    name = factory.Sequence(lambda n: f"service_{n}")
    members = None  # Will be set in specific methods
    tag = ["test-tag", "environment-prod"]
    folder = "Texas"
    snippet = None
    device = None

    @classmethod
    def build_without_members(cls, **kwargs):
        """Return a data dict without the required members field."""
        return cls(
            members=None,
            **kwargs,
        )

    @classmethod
    def build_with_no_containers(cls, **kwargs):
        """Return a data dict without any containers."""
        return cls(
            folder=None,
            snippet=None,
            device=None,
            members=["test1", "test1"],
            **kwargs,
        )

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Return a data dict with multiple containers."""
        return cls(
            folder="Texas",
            snippet="TestSnippet",
            device=None,
            members=["test1", "test1"],
            **kwargs,
        )

    @classmethod
    def build_valid_members(cls, **kwargs):
        """Return a valid data dict for a service group."""
        return cls(
            members=["test1", "test1"],
            **kwargs,
        )


class ServiceGroupUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for ServiceUpdateModel."""

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"service_{n}")
    members = None  # Will be set in specific methods
    tag = ["test-tag", "environment-prod"]
    folder = "Texas"
    snippet = None
    device = None

    @classmethod
    def build_without_members(cls, **kwargs):
        """Return a data dict without the required members field."""
        return cls(
            members=None,
            **kwargs,
        )

    @classmethod
    def build_with_no_containers(cls, **kwargs):
        """Return a data dict without any containers."""
        return cls(
            folder=None,
            snippet=None,
            device=None,
            members=["test1", "test1"],
            **kwargs,
        )

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Return a data dict with multiple containers."""
        return cls(
            folder="Texas",
            snippet="TestSnippet",
            device=None,
            members=["test1", "test1"],
            **kwargs,
        )

    @classmethod
    def build_valid_members(cls, **kwargs):
        """Return a valid data dict for a service group."""
        return cls(
            members=["test1", "test1"],
            **kwargs,
        )


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
    folder = "Texas"
    snippet = None
    device = None

    @classmethod
    def with_folder(cls, folder="Texas", **kwargs):
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
    folder = "Texas"
    snippet = None
    device = None

    @classmethod
    def with_folder(cls, folder="Texas", **kwargs):
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
    folder = "Texas"
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
            folder="Texas",
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers (should fail validation)."""
        return cls(
            name="TestTag",
            folder="Texas",
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
    def with_category(cls, category: AntiSpywareCategory = AntiSpywareCategory.botnet, **kwargs):
        """Create an instance with a specific category."""
        return cls(category=category, **kwargs)


class AntiSpywareThreatExceptionBaseFactory(factory.Factory):
    """Factory for creating ThreatExceptionBase instances."""

    class Meta:
        model = AntiSpywareThreatExceptionBase

    name = factory.Sequence(lambda n: f"exception_{n}")
    packet_capture = AntiSpywarePacketCapture.single_packet
    exempt_ip = factory.LazyAttribute(lambda _: [AntiSpywareExemptIpEntry(name="192.168.1.1")])
    notes = "Test exception"

    @classmethod
    def with_multiple_exempt_ips(cls, ips: list[str], **kwargs):
        """Create an instance with multiple exempt IPs."""
        return cls(exempt_ip=[AntiSpywareExemptIpEntry(name=ip) for ip in ips], **kwargs)


# SDK tests against SCM API
class AntiSpywareProfileCreateApiFactory(factory.Factory):
    """Factory for creating AntiSpywareProfileCreateModel instances."""

    class Meta:
        model = AntiSpywareProfileCreateModel

    name = factory.Sequence(lambda n: f"profile_{n}")
    description = factory.Faker("sentence")
    folder = "Texas"
    cloud_inline_analysis = False
    rules = factory.LazyAttribute(lambda _: [AntiSpywareRuleBaseFactory()])
    threat_exception = factory.LazyAttribute(lambda _: [AntiSpywareThreatExceptionBaseFactory()])

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
    def with_inline_exceptions(cls, urls: list[str] = None, ips: list[str] = None, **kwargs):
        """Create a profile with inline exceptions."""
        return cls(inline_exception_edl_url=urls, inline_exception_ip_address=ips, **kwargs)


class AntiSpywareProfileUpdateApiFactory(factory.Factory):
    """Factory for creating AntiSpywareProfileUpdateModel instances."""

    class Meta:
        model = AntiSpywareProfileUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"profile_{n}")
    description = factory.Faker("sentence")
    rules = factory.List([factory.SubFactory(AntiSpywareRuleBaseFactory)])
    threat_exception = factory.List([factory.SubFactory(AntiSpywareThreatExceptionBaseFactory)])

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
    folder = "Texas"
    cloud_inline_analysis = False
    rules = factory.List([factory.SubFactory(AntiSpywareRuleBaseFactory)])
    threat_exception = factory.List([factory.SubFactory(AntiSpywareThreatExceptionBaseFactory)])

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
    folder = "Texas"
    cloud_inline_analysis = False
    rules = []

    @classmethod
    def build_valid(cls):
        """Return a data dict with invalid name pattern."""
        return cls(
            name="valid-profile-name",
            folder="Texas",
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
            folder="Texas",
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
            folder="Texas",
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
            folder="Texas",
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
            folder="Texas",
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
            folder="Texas",
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
    folder = "Texas"
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
    folder = "Texas"
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
    folder = "Texas"

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestProfile",
            folder="Texas",
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
            folder="Texas",
        )

    @classmethod
    def build_with_invalid_ssl_versions(cls):
        """Return a data dict with invalid SSL version configuration."""
        return cls(
            name="TestProfile",
            folder="Texas",
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
            folder="Texas",
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


# ----------------------------------------------------------------------------
# Remote Network object factories for SDK usage (model-based)
# ----------------------------------------------------------------------------


class RemoteNetworkCreateApiFactory(factory.Factory):
    """
    Factory for creating RemoteNetworkCreateModel instances with
    the structure used by the Python SDK calls.
    """

    class Meta:
        model = RemoteNetworkCreateModel

    # Required Fields
    name = factory.Sequence(lambda n: f"remote_network_{n}")
    region = "us-east-1"
    license_type = "FWAAS-AGGREGATE"  # Default from schema
    spn_name = "spn-test"

    # Because ecmp_load_balancing=disable by default in the model,
    # we must provide `ipsec_tunnel`.
    ecmp_load_balancing = EcmpLoadBalancingEnum.disable
    ipsec_tunnel = "ipsec-tunnel-default"
    ecmp_tunnels = None

    # Optional fields
    description = factory.Faker("sentence")
    subnets: List[str] = []
    secondary_ipsec_tunnel = None
    protocol = None

    # Container fields
    folder = "Texas"
    snippet = None
    device = None

    @classmethod
    def with_snippet(
        cls,
        snippet="TestSnippet",
        **kwargs,
    ):
        """Create a RemoteNetworkCreateModel with snippet container."""
        return cls(
            folder=None,
            snippet=snippet,
            device=None,
            **kwargs,
        )

    @classmethod
    def with_device(
        cls,
        device="TestDevice",
        **kwargs,
    ):
        """Create a RemoteNetworkCreateModel with device container."""
        return cls(
            folder=None,
            snippet=None,
            device=device,
            **kwargs,
        )

    @classmethod
    def with_ecmp_enabled(
        cls,
        ecmp_tunnel_count=2,
        **kwargs,
    ):
        """
        Create a RemoteNetworkCreateModel with ecmp_load_balancing=enable and
        the required ecmp_tunnels list.
        """
        # Generate sample EcmpTunnelModel entries
        tunnels = []
        for i in range(ecmp_tunnel_count):
            tunnels.append(
                {
                    "name": f"ecmp_tunnel_{i}",
                    "ipsec_tunnel": f"ipsec-tunnel-ecmp-{i}",
                }
            )

        return cls(
            ecmp_load_balancing=EcmpLoadBalancingEnum.enable,
            ecmp_tunnels=tunnels,
            ipsec_tunnel=None,  # must be None if ecmp is enabled
            **kwargs,
        )

    @classmethod
    def without_spn_name(
        cls,
        **kwargs,
    ):
        """
        Create a RemoteNetworkCreateModel with license_type=FWAAS-AGGREGATE
        but missing spn_name (which will raise validation error).
        """
        return cls(
            spn_name=None,
            **kwargs,
        )

    @classmethod
    def with_protocol_bgp(
        cls,
        **kwargs,
    ):
        """
        Create a RemoteNetworkCreateModel with protocol containing a BgpModel.
        """
        protocol_data = {
            "bgp": {
                "enable": True,
                "local_ip_address": "192.0.2.1",
                "peer_ip_address": "203.0.113.5",
                "peer_as": "65001",
                "peering_type": "exchange-v4-over-v4",
            }
        }
        return cls(
            protocol=protocol_data,
            **kwargs,
        )


class RemoteNetworkUpdateApiFactory(factory.Factory):
    """
    Factory for creating RemoteNetworkUpdateModel instances with
    the structure used by the Python SDK calls.
    """

    class Meta:
        model = RemoteNetworkUpdateModel

    # From the schema, id is required for update
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"remote_network_{n}")
    region = "us-east-1"
    license_type = "FWAAS-AGGREGATE"
    spn_name = "spn-test"

    # ecmp_load_balancing=disable => ipsec_tunnel required
    ecmp_load_balancing = EcmpLoadBalancingEnum.disable
    ipsec_tunnel = "update-tunnel"
    ecmp_tunnels = None

    description = factory.Faker("sentence")
    subnets: List[str] = []
    secondary_ipsec_tunnel = None
    protocol = None

    folder = None
    snippet = None
    device = None

    @classmethod
    def with_ecmp_enabled(
        cls,
        ecmp_tunnel_count=2,
        **kwargs,
    ):
        """Enable ecmp_load_balancing and provide ecmp_tunnels."""
        tunnels = []
        for i in range(ecmp_tunnel_count):
            tunnels.append(
                {
                    "name": f"ecmp_tunnel_{i}",
                    "ipsec_tunnel": f"ipsec-tunnel-ecmp-{i}",
                }
            )
        return cls(
            ecmp_load_balancing=EcmpLoadBalancingEnum.enable,
            ecmp_tunnels=tunnels,
            ipsec_tunnel=None,
            **kwargs,
        )

    @classmethod
    def without_spn_name(
        cls,
        **kwargs,
    ):
        """
        Create a RemoteNetworkUpdateModel with license_type=FWAAS-AGGREGATE
        but missing spn_name (will raise validation error).
        """
        return cls(
            spn_name=None,
            **kwargs,
        )

    @classmethod
    def with_protocol_bgp(
        cls,
        **kwargs,
    ):
        """
        Create a RemoteNetworkUpdateModel with protocol containing a BgpModel.
        """
        protocol_data = {
            "bgp": {
                "enable": True,
                "local_ip_address": "192.0.2.99",
                "peer_ip_address": "198.51.100.5",
                "peer_as": "65055",
                "peering_type": "exchange-v4-over-v4-v6-over-v6",
            }
        }
        return cls(
            protocol=protocol_data,
            **kwargs,
        )


class RemoteNetworkResponseFactory(factory.Factory):
    """
    Factory for creating RemoteNetworkResponseModel instances
    to mimic the actual data returned by the SCM API.
    """

    class Meta:
        model = RemoteNetworkResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"remote_network_{n}")
    region = "us-east-1"
    license_type = "FWAAS-AGGREGATE"
    spn_name = "spn-response"
    ecmp_load_balancing = EcmpLoadBalancingEnum.disable
    ipsec_tunnel = "ipsec-tunnel-response"
    ecmp_tunnels = None

    description = factory.Faker("sentence")
    subnets: List[str] = []
    secondary_ipsec_tunnel = None
    protocol = None

    folder = "Texas"
    snippet = None
    device = None

    @classmethod
    def with_protocol_bgp(cls, **kwargs):
        """Create an instance with BGP protocol enabled."""
        protocol_data = {
            "bgp": {
                "enable": True,
                "peer_ip_address": "10.11.0.254",
                "peer_as": "65515",
                "local_ip_address": "192.168.11.11",
                "peering_type": PeeringTypeEnum.exchange_v4_over_v4,
            }
        }
        # Pass the protocol as a dict instead of a pre-constructed model
        return cls(protocol=protocol_data, **kwargs)

    @classmethod
    def with_ecmp_enabled(
        cls,
        ecmp_tunnel_count=2,
        **kwargs,
    ):
        """Return a response with ecmp enabled and ecmp_tunnels data."""
        tunnels = []
        for i in range(ecmp_tunnel_count):
            tunnels.append(
                EcmpTunnelModel(
                    name=f"ecmp_tunnel_{i}",
                    ipsec_tunnel=f"ipsec-tunnel-ecmp-{i}",
                )
            )
        return cls(
            ecmp_load_balancing=EcmpLoadBalancingEnum.enable,
            ipsec_tunnel=None,
            ecmp_tunnels=tunnels,
            **kwargs,
        )

    @classmethod
    def from_request(
        cls,
        request_model: RemoteNetworkCreateModel,
        **kwargs,
    ):
        """
        Create a response model based on a create request model,
        adding a newly generated id and any overridden kwargs.
        """
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# ----------------------------------------------------------------------------
# Dict-based factories for direct Pydantic testing
# ----------------------------------------------------------------------------


class RemoteNetworkCreateModelDictFactory(factory.DictFactory):
    """
    Factory for creating dictionary data suitable for instantiating RemoteNetworkCreateModel.
    Useful for direct Pydantic validation tests.
    """

    name = factory.Sequence(lambda n: f"remote_network_{n}")
    region = "us-west-2"
    license_type = "FWAAS-AGGREGATE"
    spn_name = "spn-test"

    # ecmp_load_balancing defaults to disable => ipsec_tunnel is required
    ecmp_load_balancing = "disable"
    ipsec_tunnel = "ipsec-tunnel-default"
    ecmp_tunnels = None

    folder = "Remote Networks"
    snippet = None
    device = None

    @classmethod
    def build_valid(
        cls,
        **kwargs,
    ):
        """Return a valid data dict with minimal required fields."""
        return cls(**kwargs)

    @classmethod
    def build_ecmp_enabled(
        cls,
        ecmp_count=2,
        **kwargs,
    ):
        """Return a data dict with ecmp enabled and ecmp_tunnels."""
        tunnels = []
        for i in range(ecmp_count):
            tunnels.append(
                {
                    "name": f"ecmp_tunnel_{i}",
                    "ipsec_tunnel": f"ipsec-tunnel-ecmp-{i}",
                }
            )
        return cls(
            ecmp_load_balancing="enable",
            ecmp_tunnels=tunnels,
            ipsec_tunnel=None,
            **kwargs,
        )

    @classmethod
    def without_spn_name(
        cls,
        **kwargs,
    ):
        """Return a data dict with FWAAS-AGGREGATE license but missing spn_name."""
        return cls(
            spn_name=None,
            **kwargs,
        )

    @classmethod
    def build_multiple_containers(
        cls,
        **kwargs,
    ):
        """Return a data dict with multiple containers (folder + snippet)."""
        return cls(
            folder="Texas",
            snippet="TestSnippet",
            **kwargs,
        )

    @classmethod
    def build_no_container(
        cls,
        **kwargs,
    ):
        """Return a data dict without any containers."""
        return cls(
            folder=None,
            snippet=None,
            device=None,
            **kwargs,
        )


class RemoteNetworkUpdateModelDictFactory(factory.DictFactory):
    """
    Factory for creating dictionary data suitable for instantiating RemoteNetworkUpdateModel.
    Useful for direct Pydantic validation tests.
    """

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"remote_network_{n}")
    region = "us-west-2"
    license_type = "FWAAS-AGGREGATE"
    spn_name = "spn-update"
    ecmp_load_balancing = "disable"
    ipsec_tunnel = "ipsec-tunnel-update"
    ecmp_tunnels = None

    folder = None
    snippet = None
    device = None

    @classmethod
    def build_valid(cls, **kwargs):
        """Return a valid data dict with minimal required fields."""
        return cls(**kwargs)

    @classmethod
    def build_ecmp_enabled(
        cls,
        ecmp_count=2,
        **kwargs,
    ):
        """Return a data dict with ecmp enabled and ecmp_tunnels."""
        tunnels = []
        for i in range(ecmp_count):
            tunnels.append(
                {
                    "name": f"ecmp_tunnel_{i}",
                    "ipsec_tunnel": f"ipsec-tunnel-ecmp-{i}",
                }
            )
        return cls(
            ecmp_load_balancing="enable",
            ecmp_tunnels=tunnels,
            ipsec_tunnel=None,
            **kwargs,
        )

    @classmethod
    def without_spn_name(
        cls,
        **kwargs,
    ):
        """Return a data dict with FWAAS-AGGREGATE license but missing spn_name."""
        return cls(
            spn_name=None,
            **kwargs,
        )

    @classmethod
    def build_multiple_containers(
        cls,
        **kwargs,
    ):
        """Return a data dict with multiple containers (folder + snippet)."""
        return cls(
            folder="Texas",
            snippet="TestSnippet",
            **kwargs,
        )

    @classmethod
    def build_no_container(
        cls,
        **kwargs,
    ):
        """Return a data dict without any containers."""
        return cls(
            folder=None,
            snippet=None,
            device=None,
            **kwargs,
        )
