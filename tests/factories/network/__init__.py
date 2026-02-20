"""Network factories for testing."""

from tests.factories.network.nat_rules import (
    InterfaceAddressFactory,
    NatRuleCreateApiFactory,
    NatRuleCreateModelFactory,
    NatRuleMoveApiFactory,
    NatRuleMoveModelFactory,
    NatRuleResponseFactory,
    NatRuleUpdateApiFactory,
    NatRuleUpdateModelFactory,
    SourceTranslationFactory,
)
from tests.factories.network.qos_profile import (
    QosProfileCreateApiFactory,
    QosProfileCreateModelFactory,
    QosProfileResponseFactory,
    QosProfileUpdateApiFactory,
    QosProfileUpdateModelFactory,
)
from tests.factories.network.qos_rule import (
    QosRuleCreateApiFactory,
    QosRuleCreateModelFactory,
    QosRuleMoveApiFactory,
    QosRuleMoveModelFactory,
    QosRuleResponseFactory,
    QosRuleUpdateApiFactory,
    QosRuleUpdateModelFactory,
)
from tests.factories.network.dns_proxy import (
    DnsProxyCreateApiFactory,
    DnsProxyCreateModelFactory,
    DnsProxyResponseFactory,
    DnsProxyUpdateApiFactory,
    DnsProxyUpdateModelFactory,
)
from tests.factories.network.pbf_rule import (
    PbfRuleCreateApiFactory,
    PbfRuleCreateModelFactory,
    PbfRuleResponseFactory,
    PbfRuleUpdateApiFactory,
    PbfRuleUpdateModelFactory,
)

# Explicitly export these factories
__all__ = [
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
