# tests/factories/__init__.py

"""Factory definitions for test objects."""

# Import deployment related factories
from tests.factories.deployment.bandwidth_allocations import (
    BandwidthAllocationBaseFactory,
    BandwidthAllocationCreateApiFactory,
    BandwidthAllocationCreateModelFactory,
    BandwidthAllocationResponseFactory,
    BandwidthAllocationUpdateApiFactory,
    QosModelFactory,
)
from tests.factories.deployment.bgp_routing import (
    BGPRoutingBaseFactory,
    BGPRoutingCreateApiFactory,
    BGPRoutingCreateModelFactory,
    BGPRoutingResponseFactory,
    BGPRoutingResponseModelFactory,
    BGPRoutingUpdateApiFactory,
    BGPRoutingUpdateModelFactory,
    DefaultRoutingModelFactory,
    HotPotatoRoutingModelFactory,
)
from tests.factories.deployment.remote_networks import (
    RemoteNetworkBaseFactory,
    RemoteNetworkCreateApiFactory,
    RemoteNetworkCreateModelFactory,
    RemoteNetworkResponseFactory,
    RemoteNetworkUpdateApiFactory,
    RemoteNetworkUpdateModelFactory,
)
from tests.factories.deployment.service_connections import (
    BgpPeerModelFactory,
    BgpProtocolModelFactory,
    ProtocolModelFactory,
)
from tests.factories.deployment.service_connections import (
    QosModelFactory as ServiceConnectionQosModelFactory,
)
from tests.factories.deployment.service_connections import (
    ServiceConnectionBaseFactory,
    ServiceConnectionCreateApiFactory,
    ServiceConnectionCreateModelFactory,
    ServiceConnectionResponseFactory,
    ServiceConnectionResponseModelFactory,
    ServiceConnectionUpdateApiFactory,
    ServiceConnectionUpdateModelFactory,
)

# Import network related factories
from tests.factories.network import (
    InterfaceAddressFactory,
    NatRuleCreateApiFactory,
    NatRuleCreateModelFactory,
    NatRuleMoveApiFactory,
    NatRuleMoveModelFactory,
    NatRuleResponseFactory,
    NatRuleUpdateApiFactory,
    NatRuleUpdateModelFactory,
    SourceTranslationFactory,
    # QoS Profile factories
    QosProfileCreateApiFactory,
    QosProfileCreateModelFactory,
    QosProfileResponseFactory,
    QosProfileUpdateApiFactory,
    QosProfileUpdateModelFactory,
    # QoS Rule factories
    QosRuleCreateApiFactory,
    QosRuleCreateModelFactory,
    QosRuleMoveApiFactory,
    QosRuleMoveModelFactory,
    QosRuleResponseFactory,
    QosRuleUpdateApiFactory,
    QosRuleUpdateModelFactory,
    # DNS Proxy factories
    DnsProxyCreateApiFactory,
    DnsProxyCreateModelFactory,
    DnsProxyResponseFactory,
    DnsProxyUpdateApiFactory,
    DnsProxyUpdateModelFactory,
    # PBF Rule factories
    PbfRuleCreateApiFactory,
    PbfRuleCreateModelFactory,
    PbfRuleResponseFactory,
    PbfRuleUpdateApiFactory,
    PbfRuleUpdateModelFactory,
)
from tests.factories.objects.address import (
    AddressCreateApiFactory,
    AddressCreateModelFactory,
    AddressResponseFactory,
    AddressUpdateApiFactory,
    AddressUpdateModelFactory,
)
from tests.factories.objects.address_group import (
    AddressGroupBaseFactory,
    AddressGroupCreateApiFactory,
    AddressGroupCreateModelFactory,
    AddressGroupResponseFactory,
    AddressGroupUpdateApiFactory,
    AddressGroupUpdateModelFactory,
)
from tests.factories.objects.application_filters import (
    ApplicationFiltersBaseFactory,
    ApplicationFiltersCreateApiFactory,
    ApplicationFiltersCreateModelFactory,
    ApplicationFiltersResponseFactory,
    ApplicationFiltersResponseModelFactory,
    ApplicationFiltersUpdateApiFactory,
    ApplicationFiltersUpdateModelFactory,
)
from tests.factories.objects.application_group import (
    ApplicationGroupBaseFactory,
    ApplicationGroupCreateApiFactory,
    ApplicationGroupCreateModelFactory,
    ApplicationGroupResponseFactory,
    ApplicationGroupUpdateApiFactory,
    ApplicationGroupUpdateModelFactory,
)
from tests.factories.objects.dynamic_user_group import (
    DynamicUserGroupBaseFactory,
    DynamicUserGroupCreateApiFactory,
    DynamicUserGroupCreateModelFactory,
    DynamicUserGroupResponseFactory,
    DynamicUserGroupUpdateApiFactory,
    DynamicUserGroupUpdateModelFactory,
)
from tests.factories.objects.external_dynamic_lists import (
    ExternalDynamicListsBaseFactory,
    ExternalDynamicListsCreateApiFactory,
    ExternalDynamicListsCreateModelFactory,
    ExternalDynamicListsResponseFactory,
    ExternalDynamicListsResponseModelFactory,
    ExternalDynamicListsUpdateApiFactory,
    ExternalDynamicListsUpdateModelFactory,
)
from tests.factories.objects.hip_object import (
    HIPObjectBaseFactory,
    HIPObjectCreateApiFactory,
    HIPObjectCreateModelFactory,
    HIPObjectResponseFactory,
    HIPObjectResponseModelFactory,
    HIPObjectUpdateApiFactory,
    HIPObjectUpdateModelFactory,
)
from tests.factories.objects.hip_profile import (
    HIPProfileBaseFactory,
    HIPProfileCreateApiFactory,
    HIPProfileCreateModelFactory,
    HIPProfileResponseFactory,
    HIPProfileResponseModelFactory,
    HIPProfileUpdateApiFactory,
    HIPProfileUpdateModelFactory,
)
from tests.factories.objects.http_server_profiles import (
    HTTPServerProfileBaseFactory,
    HTTPServerProfileCreateApiFactory,
    HTTPServerProfileCreateModelFactory,
    HTTPServerProfileResponseFactory,
    HTTPServerProfileResponseModelFactory,
    HTTPServerProfileUpdateApiFactory,
    HTTPServerProfileUpdateModelFactory,
    PayloadFormatModelFactory,
    ServerModelFactory,
)
from tests.factories.objects.log_forwarding_profile import (
    LogForwardingProfileBaseFactory,
    LogForwardingProfileCreateApiFactory,
    LogForwardingProfileCreateModelFactory,
    LogForwardingProfileResponseFactory,
    LogForwardingProfileResponseModelFactory,
    LogForwardingProfileUpdateApiFactory,
    LogForwardingProfileUpdateModelFactory,
    MatchListItemFactory,
)
from tests.factories.objects.quarantined_devices import (
    QuarantinedDevicesBaseFactory,
    QuarantinedDevicesCreateApiFactory,
    QuarantinedDevicesCreateFactory,
    QuarantinedDevicesListParamsFactory,
    QuarantinedDevicesResponseFactory,
)
from tests.factories.objects.region import (
    RegionBaseFactory,
    RegionCreateApiFactory,
    RegionCreateModelFactory,
    RegionResponseFactory,
    RegionResponseModelFactory,
    RegionUpdateApiFactory,
    RegionUpdateModelFactory,
)
from tests.factories.objects.schedules import (
    ScheduleBaseFactory,
    ScheduleCreateApiFactory,
    ScheduleCreateModelFactory,
    ScheduleResponseFactory,
    ScheduleUpdateApiFactory,
    ScheduleUpdateModelFactory,
)
from tests.factories.objects.syslog_server_profiles import (
    EscapingModelFactory,
    FormatModelFactory,
    SyslogServerModelFactory,
    SyslogServerProfileCreateModelFactory,
    SyslogServerProfileResponseModelFactory,
    SyslogServerProfileUpdateModelFactory,
)
from tests.factories.objects.tag import (
    TagBaseFactory,
    TagCreateApiFactory,
    TagCreateModelFactory,
    TagResponseFactory,
    TagUpdateApiFactory,
    TagUpdateModelFactory,
)
from tests.factories.security import (
    AntiSpywareProfileBaseFactory,
    AntiSpywareProfileCreateApiFactory,
    AntiSpywareProfileCreateModelFactory,
    AntiSpywareProfileResponseFactory,
    AntiSpywareProfileUpdateApiFactory,
    AntiSpywareProfileUpdateModelFactory,
)
from tests.factories.security.url_categories import (
    URLCategoriesCreateModelFactory,
    URLCategoriesResponseModelFactory,
    URLCategoriesUpdateModelFactory,
)

__all__ = [
    # AntiSpyware Profile factories
    "AntiSpywareProfileBaseFactory",
    "AntiSpywareProfileCreateApiFactory",
    "AntiSpywareProfileCreateModelFactory",
    "AntiSpywareProfileResponseFactory",
    "AntiSpywareProfileUpdateApiFactory",
    "AntiSpywareProfileUpdateModelFactory",
    # Bandwidth allocation factories
    "BandwidthAllocationBaseFactory",
    "BandwidthAllocationCreateApiFactory",
    "BandwidthAllocationCreateModelFactory",
    "BandwidthAllocationResponseFactory",
    "BandwidthAllocationUpdateApiFactory",
    "QosModelFactory",
    # BGP Routing factories
    "BGPRoutingBaseFactory",
    "BGPRoutingCreateApiFactory",
    "BGPRoutingCreateModelFactory",
    "BGPRoutingResponseFactory",
    "BGPRoutingResponseModelFactory",
    "BGPRoutingUpdateApiFactory",
    "BGPRoutingUpdateModelFactory",
    "DefaultRoutingModelFactory",
    "HotPotatoRoutingModelFactory",
    # Quarantined devices factories
    "QuarantinedDevicesBaseFactory",
    "QuarantinedDevicesCreateApiFactory",
    "QuarantinedDevicesCreateFactory",
    "QuarantinedDevicesListParamsFactory",
    "QuarantinedDevicesResponseFactory",
    # Syslog Server Profiles
    "EscapingModelFactory",
    "FormatModelFactory",
    "SyslogServerModelFactory",
    "SyslogServerProfileCreateModelFactory",
    "SyslogServerProfileUpdateModelFactory",
    "SyslogServerProfileResponseModelFactory",
    # HTTP Server Profiles
    "HTTPServerProfileBaseFactory",
    "HTTPServerProfileCreateApiFactory",
    "HTTPServerProfileUpdateApiFactory",
    "HTTPServerProfileResponseFactory",
    "HTTPServerProfileCreateModelFactory",
    "HTTPServerProfileUpdateModelFactory",
    "HTTPServerProfileResponseModelFactory",
    "PayloadFormatModelFactory",
    "ServerModelFactory",
    # Log Forwarding Profiles
    "LogForwardingProfileBaseFactory",
    "LogForwardingProfileCreateApiFactory",
    "LogForwardingProfileUpdateApiFactory",
    "LogForwardingProfileResponseFactory",
    "LogForwardingProfileCreateModelFactory",
    "LogForwardingProfileUpdateModelFactory",
    "LogForwardingProfileResponseModelFactory",
    "MatchListItemFactory",
    # Address
    "AddressCreateApiFactory",
    "AddressUpdateApiFactory",
    "AddressResponseFactory",
    "AddressCreateModelFactory",
    "AddressUpdateModelFactory",
    # Address Group
    "AddressGroupBaseFactory",
    "AddressGroupCreateApiFactory",
    "AddressGroupUpdateApiFactory",
    "AddressGroupResponseFactory",
    "AddressGroupCreateModelFactory",
    "AddressGroupUpdateModelFactory",
    # Application Filters
    "ApplicationFiltersBaseFactory",
    "ApplicationFiltersCreateApiFactory",
    "ApplicationFiltersUpdateApiFactory",
    "ApplicationFiltersResponseFactory",
    "ApplicationFiltersCreateModelFactory",
    "ApplicationFiltersUpdateModelFactory",
    "ApplicationFiltersResponseModelFactory",
    # Application Group
    "ApplicationGroupBaseFactory",
    "ApplicationGroupCreateApiFactory",
    "ApplicationGroupUpdateApiFactory",
    "ApplicationGroupResponseFactory",
    "ApplicationGroupCreateModelFactory",
    "ApplicationGroupUpdateModelFactory",
    # Dynamic User Group
    "DynamicUserGroupBaseFactory",
    "DynamicUserGroupCreateApiFactory",
    "DynamicUserGroupUpdateApiFactory",
    "DynamicUserGroupResponseFactory",
    "DynamicUserGroupCreateModelFactory",
    "DynamicUserGroupUpdateModelFactory",
    # External Dynamic Lists
    "ExternalDynamicListsBaseFactory",
    "ExternalDynamicListsCreateApiFactory",
    "ExternalDynamicListsUpdateApiFactory",
    "ExternalDynamicListsResponseFactory",
    "ExternalDynamicListsCreateModelFactory",
    "ExternalDynamicListsUpdateModelFactory",
    "ExternalDynamicListsResponseModelFactory",
    # HIP Objects
    "HIPObjectBaseFactory",
    "HIPObjectCreateApiFactory",
    "HIPObjectUpdateApiFactory",
    "HIPObjectResponseFactory",
    "HIPObjectCreateModelFactory",
    "HIPObjectUpdateModelFactory",
    "HIPObjectResponseModelFactory",
    # HIP Profiles
    "HIPProfileBaseFactory",
    "HIPProfileCreateApiFactory",
    "HIPProfileUpdateApiFactory",
    "HIPProfileResponseFactory",
    "HIPProfileCreateModelFactory",
    "HIPProfileUpdateModelFactory",
    "HIPProfileResponseModelFactory",
    # Region
    "RegionBaseFactory",
    "RegionCreateApiFactory",
    "RegionUpdateApiFactory",
    "RegionResponseFactory",
    "RegionCreateModelFactory",
    "RegionUpdateModelFactory",
    "RegionResponseModelFactory",
    # Schedules
    "ScheduleBaseFactory",
    "ScheduleCreateApiFactory",
    "ScheduleUpdateApiFactory",
    "ScheduleResponseFactory",
    "ScheduleCreateModelFactory",
    "ScheduleUpdateModelFactory",
    # Security - URL Categories
    "URLCategoriesCreateModelFactory",
    "URLCategoriesUpdateModelFactory",
    "URLCategoriesResponseModelFactory",
    # Service Connection factories
    "BgpPeerModelFactory",
    "BgpProtocolModelFactory",
    "ProtocolModelFactory",
    "ServiceConnectionQosModelFactory",
    "ServiceConnectionBaseFactory",
    "ServiceConnectionCreateApiFactory",
    "ServiceConnectionCreateModelFactory",
    "ServiceConnectionResponseFactory",
    "ServiceConnectionResponseModelFactory",
    "ServiceConnectionUpdateApiFactory",
    "ServiceConnectionUpdateModelFactory",
    # Tag factories
    "TagBaseFactory",
    "TagCreateApiFactory",
    "TagCreateModelFactory",
    "TagResponseFactory",
    "TagUpdateApiFactory",
    "TagUpdateModelFactory",
    # Deployment - Remote Networks factories
    "RemoteNetworkBaseFactory",
    "RemoteNetworkCreateApiFactory",
    "RemoteNetworkCreateModelFactory",
    "RemoteNetworkResponseFactory",
    "RemoteNetworkUpdateApiFactory",
    "RemoteNetworkUpdateModelFactory",
    # Network factories
    "InterfaceAddressFactory",
    "NatRuleCreateApiFactory",
    "NatRuleCreateModelFactory",
    "NatRuleMoveApiFactory",
    "NatRuleMoveModelFactory",
    "NatRuleResponseFactory",
    "NatRuleUpdateApiFactory",
    "NatRuleUpdateModelFactory",
    "SourceTranslationFactory",
    # QoS Profile factories
    "QosProfileCreateApiFactory",
    "QosProfileCreateModelFactory",
    "QosProfileResponseFactory",
    "QosProfileUpdateApiFactory",
    "QosProfileUpdateModelFactory",
    # QoS Rule factories
    "QosRuleCreateApiFactory",
    "QosRuleCreateModelFactory",
    "QosRuleMoveApiFactory",
    "QosRuleMoveModelFactory",
    "QosRuleResponseFactory",
    "QosRuleUpdateApiFactory",
    "QosRuleUpdateModelFactory",
    # DNS Proxy factories
    "DnsProxyCreateApiFactory",
    "DnsProxyCreateModelFactory",
    "DnsProxyResponseFactory",
    "DnsProxyUpdateApiFactory",
    "DnsProxyUpdateModelFactory",
    # PBF Rule factories
    "PbfRuleCreateApiFactory",
    "PbfRuleCreateModelFactory",
    "PbfRuleResponseFactory",
    "PbfRuleUpdateApiFactory",
    "PbfRuleUpdateModelFactory",
]
