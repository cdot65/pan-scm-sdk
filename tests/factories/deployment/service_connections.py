"""Factory classes for generating Service Connections test data."""

import random
from typing import Any, Dict
import uuid

from factory import Factory, LazyAttribute, LazyFunction, SubFactory
from factory.fuzzy import FuzzyChoice

from scm.models.deployment import (
    BgpPeerModel,
    BgpProtocolModel,
    NoExportCommunity,
    OnboardingType,
    ProtocolModel,
    QosModel,
    ServiceConnectionCreateModel,
    ServiceConnectionResponseModel,
    ServiceConnectionUpdateModel,
)


class ServiceConnectionBaseFactory(Factory):
    """Base factory for Service Connection test data."""

    class Meta:
        """Factory configuration."""

        abstract = True

    name = LazyFunction(lambda: f"sc-test-{uuid.uuid4().hex[:8]}")
    folder = "Service Connections"
    ipsec_tunnel = LazyFunction(lambda: f"tunnel-{uuid.uuid4().hex[:8]}")
    region = FuzzyChoice(["us-east-1", "us-west-1", "eu-west-1", "ap-southeast-1"])
    onboarding_type = FuzzyChoice([e.value for e in OnboardingType])
    backup_SC = LazyFunction(lambda: f"backup-sc-{uuid.uuid4().hex[:8]}")
    subnets = LazyAttribute(
        lambda _: [
            f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.0/24"
            for _ in range(random.randint(1, 3))
        ]
    )
    no_export_community = FuzzyChoice([e.value for e in NoExportCommunity])
    source_nat = FuzzyChoice([True, False])

    @classmethod
    def generate_bgp_peer(cls) -> Dict[str, Any]:
        """Generate a BGP peer configuration."""
        return {
            "local_ip_address": f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}",
            "local_ipv6_address": f"2001:db8::{random.randint(1, 9999)}",
            "peer_ip_address": f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}",
            "peer_ipv6_address": f"2001:db8::{random.randint(1, 9999)}",
            "secret": f"secret-{uuid.uuid4().hex[:8]}",
        }

    @classmethod
    def generate_bgp_protocol(cls) -> Dict[str, Any]:
        """Generate a BGP protocol configuration."""
        return {
            "do_not_export_routes": random.choice([True, False]),
            "enable": True,
            "fast_failover": random.choice([True, False]),
            "local_ip_address": f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}",
            "originate_default_route": random.choice([True, False]),
            "peer_as": str(random.randint(64512, 65534)),
            "peer_ip_address": f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}",
            "secret": f"secret-{uuid.uuid4().hex[:8]}",
            "summarize_mobile_user_routes": random.choice([True, False]),
        }

    @classmethod
    def generate_protocol(cls) -> Dict[str, Any]:
        """Generate a protocol configuration."""
        return {
            "bgp": cls.generate_bgp_protocol(),
        }

    @classmethod
    def generate_qos(cls) -> Dict[str, Any]:
        """Generate a QoS configuration."""
        return {
            "enable": random.choice([True, False]),
            "qos_profile": f"profile-{uuid.uuid4().hex[:8]}",
        }


class ServiceConnectionCreateApiFactory(ServiceConnectionBaseFactory):
    """Factory for generating Service Connection create API data."""

    class Meta:
        """Factory configuration."""

        model = dict

    bgp_peer = LazyFunction(ServiceConnectionBaseFactory.generate_bgp_peer)
    protocol = LazyFunction(ServiceConnectionBaseFactory.generate_protocol)
    qos = LazyFunction(ServiceConnectionBaseFactory.generate_qos)


class ServiceConnectionUpdateApiFactory(ServiceConnectionBaseFactory):
    """Factory for generating Service Connection update API data."""

    class Meta:
        """Factory configuration."""

        model = dict

    id = LazyFunction(lambda: str(uuid.uuid4()))
    bgp_peer = LazyFunction(ServiceConnectionBaseFactory.generate_bgp_peer)
    protocol = LazyFunction(ServiceConnectionBaseFactory.generate_protocol)
    qos = LazyFunction(ServiceConnectionBaseFactory.generate_qos)


class ServiceConnectionResponseFactory(ServiceConnectionBaseFactory):
    """Factory for generating Service Connection response API data."""

    class Meta:
        """Factory configuration."""

        model = dict

    id = LazyFunction(lambda: str(uuid.uuid4()))
    bgp_peer = LazyFunction(ServiceConnectionBaseFactory.generate_bgp_peer)
    protocol = LazyFunction(ServiceConnectionBaseFactory.generate_protocol)
    qos = LazyFunction(ServiceConnectionBaseFactory.generate_qos)


class BgpPeerModelFactory(Factory):
    """Factory for generating BgpPeerModel instances."""

    class Meta:
        """Factory configuration."""

        model = BgpPeerModel

    local_ip_address = LazyFunction(
        lambda: f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}"
    )
    local_ipv6_address = LazyFunction(lambda: f"2001:db8::{random.randint(1, 9999)}")
    peer_ip_address = LazyFunction(
        lambda: f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}"
    )
    peer_ipv6_address = LazyFunction(lambda: f"2001:db8::{random.randint(1, 9999)}")
    secret = LazyFunction(lambda: f"secret-{uuid.uuid4().hex[:8]}")


class BgpProtocolModelFactory(Factory):
    """Factory for generating BgpProtocolModel instances."""

    class Meta:
        """Factory configuration."""

        model = BgpProtocolModel

    do_not_export_routes = FuzzyChoice([True, False])
    enable = True
    fast_failover = FuzzyChoice([True, False])
    local_ip_address = LazyFunction(
        lambda: f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}"
    )
    originate_default_route = FuzzyChoice([True, False])
    peer_as = LazyFunction(lambda: str(random.randint(64512, 65534)))
    peer_ip_address = LazyFunction(
        lambda: f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}"
    )
    secret = LazyFunction(lambda: f"secret-{uuid.uuid4().hex[:8]}")
    summarize_mobile_user_routes = FuzzyChoice([True, False])


class ProtocolModelFactory(Factory):
    """Factory for generating ProtocolModel instances."""

    class Meta:
        """Factory configuration."""

        model = ProtocolModel

    bgp = SubFactory(BgpProtocolModelFactory)


class QosModelFactory(Factory):
    """Factory for generating QosModel instances."""

    class Meta:
        """Factory configuration."""

        model = QosModel

    enable = FuzzyChoice([True, False])
    qos_profile = LazyFunction(lambda: f"profile-{uuid.uuid4().hex[:8]}")


class ServiceConnectionCreateModelFactory(Factory):
    """Factory for generating ServiceConnectionCreateModel instances."""

    class Meta:
        """Factory configuration."""

        model = ServiceConnectionCreateModel

    name = LazyFunction(lambda: f"sc-test-{uuid.uuid4().hex[:8]}")
    folder = "Service Connections"
    ipsec_tunnel = LazyFunction(lambda: f"tunnel-{uuid.uuid4().hex[:8]}")
    region = FuzzyChoice(["us-east-1", "us-west-1", "eu-west-1", "ap-southeast-1"])
    onboarding_type = FuzzyChoice([e.value for e in OnboardingType])
    backup_SC = LazyFunction(lambda: f"backup-sc-{uuid.uuid4().hex[:8]}")
    subnets = LazyAttribute(
        lambda _: [
            f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.0/24"
            for _ in range(random.randint(1, 3))
        ]
    )
    no_export_community = FuzzyChoice([e.value for e in NoExportCommunity])
    source_nat = FuzzyChoice([True, False])
    bgp_peer = SubFactory(BgpPeerModelFactory)
    protocol = SubFactory(ProtocolModelFactory)
    qos = SubFactory(QosModelFactory)


class ServiceConnectionUpdateModelFactory(Factory):
    """Factory for generating ServiceConnectionUpdateModel instances."""

    class Meta:
        """Factory configuration."""

        model = ServiceConnectionUpdateModel

    id = LazyFunction(lambda: uuid.uuid4())
    name = LazyFunction(lambda: f"sc-test-{uuid.uuid4().hex[:8]}")
    folder = "Service Connections"
    ipsec_tunnel = LazyFunction(lambda: f"tunnel-{uuid.uuid4().hex[:8]}")
    region = FuzzyChoice(["us-east-1", "us-west-1", "eu-west-1", "ap-southeast-1"])
    onboarding_type = FuzzyChoice([e.value for e in OnboardingType])
    backup_SC = LazyFunction(lambda: f"backup-sc-{uuid.uuid4().hex[:8]}")
    subnets = LazyAttribute(
        lambda _: [
            f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.0/24"
            for _ in range(random.randint(1, 3))
        ]
    )
    no_export_community = FuzzyChoice([e.value for e in NoExportCommunity])
    source_nat = FuzzyChoice([True, False])
    bgp_peer = SubFactory(BgpPeerModelFactory)
    protocol = SubFactory(ProtocolModelFactory)
    qos = SubFactory(QosModelFactory)


class ServiceConnectionResponseModelFactory(Factory):
    """Factory for generating ServiceConnectionResponseModel instances."""

    class Meta:
        """Factory configuration."""

        model = ServiceConnectionResponseModel

    id = LazyFunction(lambda: uuid.uuid4())
    name = LazyFunction(lambda: f"sc-test-{uuid.uuid4().hex[:8]}")
    folder = "Service Connections"
    ipsec_tunnel = LazyFunction(lambda: f"tunnel-{uuid.uuid4().hex[:8]}")
    region = FuzzyChoice(["us-east-1", "us-west-1", "eu-west-1", "ap-southeast-1"])
    onboarding_type = FuzzyChoice([e.value for e in OnboardingType])
    backup_SC = LazyFunction(lambda: f"backup-sc-{uuid.uuid4().hex[:8]}")
    subnets = LazyAttribute(
        lambda _: [
            f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.0/24"
            for _ in range(random.randint(1, 3))
        ]
    )
    no_export_community = FuzzyChoice([e.value for e in NoExportCommunity])
    source_nat = FuzzyChoice([True, False])
    bgp_peer = SubFactory(BgpPeerModelFactory)
    protocol = SubFactory(ProtocolModelFactory)
    qos = SubFactory(QosModelFactory)
