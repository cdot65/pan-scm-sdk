"""Factory definitions for mobile agent models."""

from factory import Factory, Faker  # type: ignore
import factory.fuzzy  # type: ignore
from faker import Faker as FakerGenerator

from scm.models.mobile_agent.agent_profiles import (
    AgentProfileOperatingSystem,
    AgentProfilesBaseModel,
    AgentProfilesCreateModel,
    AgentProfilesResponseModel,
    AgentProfilesUpdateModel,
)
from scm.models.mobile_agent.agent_versions import AgentVersionModel, AgentVersionsModel
from scm.models.mobile_agent.auth_settings import (
    AuthSettingsBaseModel,
    AuthSettingsCreateModel,
    AuthSettingsMoveModel,
    AuthSettingsResponseModel,
    AuthSettingsUpdateModel,
    MovePosition,
    OperatingSystem,
)
from scm.models.mobile_agent.forwarding_profile_destinations import (
    DestinationFqdnEntry,
    DestinationIpEntry,
    ForwardingProfileDestinationCreateModel,
    ForwardingProfileDestinationResponseModel,
    ForwardingProfileDestinationUpdateModel,
)
from scm.models.mobile_agent.forwarding_profiles import (
    DefinitionMethod,
    ForwardingProfileCreateModel,
    ForwardingProfileResponseModel,
    ForwardingProfileUpdateModel,
    ForwardingRuleBasic,
    ForwardingRuleZtna,
    ZtnaTrafficType,
)
from scm.models.mobile_agent.global_settings import (
    GlobalSettingsResponseModel,
    GlobalSettingsUpdateModel,
    ManualGateway,
    ManualGatewayRegion,
)
from scm.models.mobile_agent.infrastructure_settings import (
    DefaultDomain,
    DnsServerEntry,
    InfrastructureSettingsCreateModel,
    InfrastructureSettingsResponseModel,
    InfrastructureSettingsUpdateModel,
    IpPool,
    PortalHostname,
    PublicDnsServer,
)
from scm.models.mobile_agent.tunnel_profiles import (
    TunnelOperatingSystem,
    TunnelProfileBaseModel,
    TunnelProfileCreateModel,
    TunnelProfileResponseModel,
    TunnelProfileUpdateModel,
)

# Create a single faker instance
fake = FakerGenerator()


class AgentVersionModelFactory(Factory):
    """Factory for AgentVersionModel."""

    class Meta:
        """Meta class for AgentVersionModelFactory."""

        model = AgentVersionModel

    version = factory.LazyFunction(
        lambda: f"{fake.random_int(min=5, max=6)}.{fake.random_int(min=0, max=9)}.{fake.random_int(min=0, max=9)}"
    )
    release_date = factory.LazyFunction(lambda: fake.date(pattern="%Y-%m-%d"))
    is_recommended = factory.fuzzy.FuzzyChoice([True, False, None])


class AgentVersionsModelFactory(Factory):
    """Factory for AgentVersionsModel."""

    class Meta:
        """Meta class for AgentVersionsModelFactory."""

        model = AgentVersionsModel

    agent_versions = factory.LazyFunction(
        lambda: [
            f"{fake.random_int(min=5, max=6)}.{fake.random_int(min=0, max=9)}.{fake.random_int(min=0, max=9)}"
            for _ in range(fake.random_int(min=1, max=5))
        ]
    )


class AuthSettingsBaseModelFactory(Factory):
    """Factory for AuthSettingsBaseModel."""

    class Meta:
        """Meta class for AuthSettingsBaseModelFactory."""

        model = AuthSettingsBaseModel

    name = Faker("pystr", min_chars=5, max_chars=30)
    authentication_profile = Faker("pystr", min_chars=5, max_chars=30)
    os = factory.fuzzy.FuzzyChoice(list(OperatingSystem))
    user_credential_or_client_cert_required = Faker("pybool")
    folder = "Mobile Users"


class AuthSettingsCreateModelFactory(Factory):
    """Factory for AuthSettingsCreateModel."""

    class Meta:
        """Meta class for AuthSettingsCreateModelFactory."""

        model = AuthSettingsCreateModel

    name = Faker("pystr", min_chars=5, max_chars=30)
    authentication_profile = Faker("pystr", min_chars=5, max_chars=30)
    os = factory.fuzzy.FuzzyChoice(list(OperatingSystem))
    user_credential_or_client_cert_required = Faker("pybool")
    folder = "Mobile Users"

    @classmethod
    def build_valid(cls):
        """Build valid data for AuthSettingsCreateModel."""
        model = cls.build()
        return {
            "name": model.name,
            "authentication_profile": model.authentication_profile,
            "os": model.os,
            "user_credential_or_client_cert_required": model.user_credential_or_client_cert_required,
            "folder": model.folder,
        }

    @classmethod
    def build_invalid_name(cls):
        """Build data with invalid name for AuthSettingsCreateModel."""
        data = cls.build_valid()
        data["name"] = "invalid@name"
        return data

    @classmethod
    def build_invalid_folder(cls):
        """Build data with invalid folder for AuthSettingsCreateModel."""
        data = cls.build_valid()
        data["folder"] = "Invalid Folder"
        return data

    @classmethod
    def build_missing_folder(cls):
        """Build data with missing folder for AuthSettingsCreateModel."""
        data = cls.build_valid()
        del data["folder"]
        return data


class AuthSettingsResponseModelFactory(Factory):
    """Factory for AuthSettingsResponseModel."""

    class Meta:
        """Meta class for AuthSettingsResponseModelFactory."""

        model = AuthSettingsResponseModel

    name = Faker("pystr", min_chars=5, max_chars=30)
    authentication_profile = Faker("pystr", min_chars=5, max_chars=30)
    os = factory.fuzzy.FuzzyChoice(list(OperatingSystem))
    user_credential_or_client_cert_required = Faker("pybool")
    folder = "Mobile Users"


class AuthSettingsUpdateModelFactory(Factory):
    """Factory for AuthSettingsUpdateModel."""

    class Meta:
        """Meta class for AuthSettingsUpdateModelFactory."""

        model = AuthSettingsUpdateModel

    name = Faker("pystr", min_chars=5, max_chars=30)
    authentication_profile = Faker("pystr", min_chars=5, max_chars=30)
    os = factory.fuzzy.FuzzyChoice(list(OperatingSystem))
    user_credential_or_client_cert_required = Faker("pybool")
    folder = "Mobile Users"

    @classmethod
    def build_valid(cls):
        """Build valid data for AuthSettingsUpdateModel."""
        model = cls.build()
        return {
            "name": model.name,
            "authentication_profile": model.authentication_profile,
            "os": model.os,
            "user_credential_or_client_cert_required": model.user_credential_or_client_cert_required,
            "folder": model.folder,
        }

    @classmethod
    def build_minimal_update(cls):
        """Build minimal update data for AuthSettingsUpdateModel."""
        return {
            "authentication_profile": fake.pystr(min_chars=5, max_chars=30),
        }

    @classmethod
    def build_invalid_name(cls):
        """Build data with invalid name for AuthSettingsUpdateModel."""
        data = cls.build_valid()
        data["name"] = "invalid@name"
        return data

    @classmethod
    def build_invalid_folder(cls):
        """Build data with invalid folder for AuthSettingsUpdateModel."""
        data = cls.build_valid()
        data["folder"] = "Invalid Folder"
        return data


class AuthSettingsMoveModelFactory(Factory):
    """Factory for AuthSettingsMoveModel."""

    class Meta:
        """Meta class for AuthSettingsMoveModelFactory."""

        model = AuthSettingsMoveModel

    name = Faker("pystr", min_chars=5, max_chars=30)
    where = MovePosition.TOP
    destination = None

    class Params:
        """Parameters to control factory behavior."""

        needs_destination = factory.Trait(
            where=MovePosition.BEFORE, destination=Faker("pystr", min_chars=5, max_chars=30)
        )

    @classmethod
    def build_valid_before(cls):
        """Build valid data for before move."""
        return {
            "name": fake.pystr(min_chars=5, max_chars=30),
            "where": MovePosition.BEFORE,
            "destination": fake.pystr(min_chars=5, max_chars=30),
        }

    @classmethod
    def build_valid_after(cls):
        """Build valid data for after move."""
        return {
            "name": fake.pystr(min_chars=5, max_chars=30),
            "where": MovePosition.AFTER,
            "destination": fake.pystr(min_chars=5, max_chars=30),
        }

    @classmethod
    def build_valid_top(cls):
        """Build valid data for top move."""
        return {
            "name": fake.pystr(min_chars=5, max_chars=30),
            "where": MovePosition.TOP,
        }

    @classmethod
    def build_valid_bottom(cls):
        """Build valid data for bottom move."""
        return {
            "name": fake.pystr(min_chars=5, max_chars=30),
            "where": MovePosition.BOTTOM,
        }

    @classmethod
    def build_invalid_before_missing_destination(cls):
        """Build invalid data for before move with missing destination."""
        return {
            "name": fake.pystr(min_chars=5, max_chars=30),
            "where": MovePosition.BEFORE,
        }

    @classmethod
    def build_invalid_top_with_destination(cls):
        """Build invalid data for top move with destination."""
        return {
            "name": fake.pystr(min_chars=5, max_chars=30),
            "where": MovePosition.TOP,
            "destination": fake.pystr(min_chars=5, max_chars=30),
        }


def _build_infrastructure_settings_data():
    """Build a valid infrastructure settings data dictionary."""
    return {
        "name": fake.pystr(min_chars=5, max_chars=30),
        "dns_servers": [
            {
                "name": fake.pystr(min_chars=5, max_chars=30),
                "dns_suffix": [fake.domain_name()],
                "primary_public_dns": {"dns_server": fake.ipv4()},
                "secondary_public_dns": {"dns_server": fake.ipv4()},
            }
        ],
        "ip_pools": [
            {
                "name": fake.pystr(min_chars=5, max_chars=30),
                "ip_pool": ["10.10.0.0/16"],
            }
        ],
        "portal_hostname": {
            "default_domain": {"hostname": fake.domain_word()},
        },
    }


class InfrastructureSettingsCreateModelFactory(Factory):
    """Factory for InfrastructureSettingsCreateModel."""

    class Meta:
        """Meta class for InfrastructureSettingsCreateModelFactory."""

        model = InfrastructureSettingsCreateModel

    name = Faker("pystr", min_chars=5, max_chars=30)
    dns_servers = factory.LazyFunction(
        lambda: [DnsServerEntry(primary_public_dns=PublicDnsServer(dns_server=fake.ipv4()))]
    )
    ip_pools = factory.LazyFunction(lambda: [IpPool(name="pool-1", ip_pool=["10.10.0.0/16"])])
    portal_hostname = factory.LazyFunction(
        lambda: PortalHostname(default_domain=DefaultDomain(hostname=fake.domain_word()))
    )

    @classmethod
    def build_valid(cls):
        """Build valid data for InfrastructureSettingsCreateModel."""
        return _build_infrastructure_settings_data()

    @classmethod
    def build_missing_required(cls):
        """Build data with missing required fields for InfrastructureSettingsCreateModel."""
        data = _build_infrastructure_settings_data()
        del data["dns_servers"]
        return data


class InfrastructureSettingsUpdateModelFactory(Factory):
    """Factory for InfrastructureSettingsUpdateModel."""

    class Meta:
        """Meta class for InfrastructureSettingsUpdateModelFactory."""

        model = InfrastructureSettingsUpdateModel

    name = Faker("pystr", min_chars=5, max_chars=30)
    dns_servers = factory.LazyFunction(
        lambda: [DnsServerEntry(primary_public_dns=PublicDnsServer(dns_server=fake.ipv4()))]
    )
    ip_pools = factory.LazyFunction(lambda: [IpPool(name="pool-1", ip_pool=["10.10.0.0/16"])])
    portal_hostname = factory.LazyFunction(
        lambda: PortalHostname(default_domain=DefaultDomain(hostname=fake.domain_word()))
    )

    @classmethod
    def build_valid(cls):
        """Build valid data for InfrastructureSettingsUpdateModel."""
        return _build_infrastructure_settings_data()


class InfrastructureSettingsResponseModelFactory(Factory):
    """Factory for InfrastructureSettingsResponseModel."""

    class Meta:
        """Meta class for InfrastructureSettingsResponseModelFactory."""

        model = InfrastructureSettingsResponseModel

    id = factory.LazyFunction(lambda: fake.uuid4())
    name = Faker("pystr", min_chars=5, max_chars=30)
    dns_servers = factory.LazyFunction(
        lambda: [DnsServerEntry(primary_public_dns=PublicDnsServer(dns_server=fake.ipv4()))]
    )
    ip_pools = factory.LazyFunction(lambda: [IpPool(name="pool-1", ip_pool=["10.10.0.0/16"])])
    portal_hostname = factory.LazyFunction(
        lambda: PortalHostname(default_domain=DefaultDomain(hostname=fake.domain_word()))
    )

    @classmethod
    def build_valid(cls):
        """Build valid data for InfrastructureSettingsResponseModel."""
        data = _build_infrastructure_settings_data()
        data["id"] = fake.uuid4()
        return data


class GlobalSettingsUpdateModelFactory(Factory):
    """Factory for GlobalSettingsUpdateModel."""

    class Meta:
        """Meta class for GlobalSettingsUpdateModelFactory."""

        model = GlobalSettingsUpdateModel

    agent_version = factory.LazyFunction(
        lambda: f"{fake.random_int(min=5, max=6)}.{fake.random_int(min=0, max=9)}.{fake.random_int(min=0, max=9)}"
    )
    manual_gateway = factory.LazyFunction(
        lambda: ManualGateway(
            region=[
                ManualGatewayRegion(
                    name=fake.pystr(min_chars=5, max_chars=20),
                    locations=[fake.pystr(min_chars=5, max_chars=20)],
                )
            ]
        )
    )

    @classmethod
    def build_valid(cls):
        """Build valid data for GlobalSettingsUpdateModel."""
        return {
            "agent_version": "6.2.1",
            "manual_gateway": {
                "region": [
                    {
                        "name": "americas",
                        "locations": ["us-east-1"],
                    }
                ]
            },
        }


class GlobalSettingsResponseModelFactory(Factory):
    """Factory for GlobalSettingsResponseModel."""

    class Meta:
        """Meta class for GlobalSettingsResponseModelFactory."""

        model = GlobalSettingsResponseModel

    agent_version = factory.LazyFunction(
        lambda: f"{fake.random_int(min=5, max=6)}.{fake.random_int(min=0, max=9)}.{fake.random_int(min=0, max=9)}"
    )
    manual_gateway = None


class TunnelProfileBaseModelFactory(Factory):
    """Factory for TunnelProfileBaseModel."""

    class Meta:
        """Meta class for TunnelProfileBaseModelFactory."""

        model = TunnelProfileBaseModel

    name = Faker("pystr", min_chars=5, max_chars=30)
    no_direct_access_to_local_network = Faker("pybool")
    os = factory.LazyFunction(lambda: [TunnelOperatingSystem.WINDOWS, TunnelOperatingSystem.MAC])
    retrieve_framed_ip_address = Faker("pybool")
    source_user = factory.LazyFunction(lambda: [fake.user_name() for _ in range(2)])


class TunnelProfileCreateModelFactory(Factory):
    """Factory for TunnelProfileCreateModel."""

    class Meta:
        """Meta class for TunnelProfileCreateModelFactory."""

        model = TunnelProfileCreateModel

    name = Faker("pystr", min_chars=5, max_chars=30)
    no_direct_access_to_local_network = Faker("pybool")
    os = factory.LazyFunction(lambda: [TunnelOperatingSystem.WINDOWS])
    retrieve_framed_ip_address = Faker("pybool")

    @classmethod
    def build_valid(cls):
        """Build valid data for TunnelProfileCreateModel."""
        return {
            "name": fake.pystr(min_chars=5, max_chars=30),
            "no_direct_access_to_local_network": fake.pybool(),
            "os": [TunnelOperatingSystem.WINDOWS],
            "retrieve_framed_ip_address": fake.pybool(),
        }

    @classmethod
    def build_valid_full(cls):
        """Build valid data with all nested structures for TunnelProfileCreateModel."""
        return {
            "name": fake.pystr(min_chars=5, max_chars=30),
            "authentication_override": {
                "accept_cookie": {
                    "cookie_lifetime": {"lifetime_in_hours": 24},
                    "cookie_encrypt_decrypt_cert": "test-cert",
                    "generate_cookie": True,
                }
            },
            "no_direct_access_to_local_network": True,
            "os": [TunnelOperatingSystem.WINDOWS, TunnelOperatingSystem.IOS],
            "retrieve_framed_ip_address": False,
            "source_address": {
                "ip_address": ["10.0.0.0/24"],
                "region": ["US"],
            },
            "source_user": ["user1", "user2"],
            "split_tunneling": {
                "access_route": ["10.1.0.0/16"],
                "exclude_access_route": ["10.2.0.0/16"],
                "exclude_applications": ["app1"],
                "exclude_domains": {"list": [{"name": "example.com", "ports": [443]}]},
                "include_applications": ["app2"],
                "include_domains": {"list": [{"name": "internal.example.com", "ports": [80, 443]}]},
            },
        }

    @classmethod
    def build_invalid_name(cls):
        """Build data with invalid (too long) name for TunnelProfileCreateModel."""
        data = cls.build_valid()
        data["name"] = "x" * 32  # exceeds 31 char max
        return data

    @classmethod
    def build_invalid_os(cls):
        """Build data with invalid os value for TunnelProfileCreateModel."""
        data = cls.build_valid()
        data["os"] = ["InvalidOS"]
        return data


class TunnelProfileUpdateModelFactory(Factory):
    """Factory for TunnelProfileUpdateModel."""

    class Meta:
        """Meta class for TunnelProfileUpdateModelFactory."""

        model = TunnelProfileUpdateModel

    name = Faker("pystr", min_chars=5, max_chars=30)
    no_direct_access_to_local_network = Faker("pybool")
    os = factory.LazyFunction(lambda: [TunnelOperatingSystem.LINUX])
    retrieve_framed_ip_address = Faker("pybool")

    @classmethod
    def build_valid(cls):
        """Build valid data for TunnelProfileUpdateModel."""
        return {
            "name": fake.pystr(min_chars=5, max_chars=30),
            "no_direct_access_to_local_network": fake.pybool(),
            "os": [TunnelOperatingSystem.LINUX],
            "retrieve_framed_ip_address": fake.pybool(),
        }


class TunnelProfileResponseModelFactory(Factory):
    """Factory for TunnelProfileResponseModel."""

    class Meta:
        """Meta class for TunnelProfileResponseModelFactory."""

        model = TunnelProfileResponseModel

    name = Faker("pystr", min_chars=5, max_chars=30)
    no_direct_access_to_local_network = Faker("pybool")
    os = factory.LazyFunction(lambda: [TunnelOperatingSystem.WINDOWS])
    retrieve_framed_ip_address = Faker("pybool")
    folder = "Mobile Users"


class AgentProfilesBaseModelFactory(Factory):
    """Factory for AgentProfilesBaseModel."""

    class Meta:
        """Meta class for AgentProfilesBaseModelFactory."""

        model = AgentProfilesBaseModel

    name = Faker("pystr", min_chars=5, max_chars=30)
    folder = "Mobile Users"
    os = factory.LazyFunction(lambda: [fake.random_element(list(AgentProfileOperatingSystem))])
    source_user = factory.LazyFunction(lambda: [fake.user_name()])


class AgentProfilesCreateModelFactory(Factory):
    """Factory for AgentProfilesCreateModel."""

    class Meta:
        """Meta class for AgentProfilesCreateModelFactory."""

        model = AgentProfilesCreateModel

    name = Faker("pystr", min_chars=5, max_chars=30)
    folder = "Mobile Users"
    os = factory.LazyFunction(lambda: [fake.random_element(list(AgentProfileOperatingSystem))])
    source_user = factory.LazyFunction(lambda: [fake.user_name()])

    @classmethod
    def build_valid(cls):
        """Build valid data for AgentProfilesCreateModel."""
        model = cls.build()
        return {
            "name": model.name,
            "folder": model.folder,
            "os": model.os,
            "source_user": model.source_user,
        }

    @classmethod
    def build_valid_nested(cls):
        """Build valid data with nested structures for AgentProfilesCreateModel."""
        data = cls.build_valid()
        data.update(
            {
                "agent_ui": {
                    "agent_user_override_timeout": 30,
                    "max_agent_user_overrides": 5,
                    "passcode": "secret-passcode",
                    "welcome_page": {"page": "factory-default"},
                },
                "authentication_override": {
                    "accept_cookie": {"cookie_lifetime": {"lifetime_in_hours": 24}},
                    "generate_cookie": True,
                },
                "gateways": {
                    "external": {
                        "list": [
                            {
                                "name": "gw-external",
                                "choice": {"fqdn": "gw.example.com"},
                                "manual": True,
                                "priority_rule": [{"name": "rule-1", "priority": "1"}],
                            }
                        ]
                    },
                    "internal": {
                        "list": [
                            {
                                "name": "gw-internal",
                                "choice": {"ip": {"ipv4": "10.0.0.1"}},
                                "source_ip": ["10.0.0.0/8"],
                            }
                        ]
                    },
                },
                "gp_app_config": {
                    "config": [
                        {"name": "connect-method", "value": ["user-logon"]},
                        {"name": "tunnel-mtu", "value": [1400]},
                    ]
                },
                "hip_collection": {
                    "collect_hip_data": True,
                    "max_wait_time": 20,
                    "custom_checks": {
                        "windows": {"process_list": ["winproc.exe"]},
                        "mac_os": {"plist": [{"name": "com.example.plist", "key": ["k1"]}]},
                        "linux": {"process_list": ["linuxproc"]},
                    },
                },
                "internal_host_detection": {
                    "hostname": "internal.example.com",
                    "ip_address": "10.1.1.1",
                },
                "save_user_credentials": "1",
                "third_party_vpn_clients": ["PAN Virtual Ethernet Adapter"],
            }
        )
        return data

    @classmethod
    def build_invalid_folder(cls):
        """Build data with invalid folder for AgentProfilesCreateModel."""
        data = cls.build_valid()
        data["folder"] = "Invalid Folder"
        return data

    @classmethod
    def build_missing_folder(cls):
        """Build data with missing folder for AgentProfilesCreateModel."""
        data = cls.build_valid()
        del data["folder"]
        return data


class AgentProfilesUpdateModelFactory(Factory):
    """Factory for AgentProfilesUpdateModel."""

    class Meta:
        """Meta class for AgentProfilesUpdateModelFactory."""

        model = AgentProfilesUpdateModel

    name = Faker("pystr", min_chars=5, max_chars=30)
    folder = "Mobile Users"
    os = factory.LazyFunction(lambda: [fake.random_element(list(AgentProfileOperatingSystem))])

    @classmethod
    def build_valid(cls):
        """Build valid data for AgentProfilesUpdateModel."""
        model = cls.build()
        return {
            "name": model.name,
            "folder": model.folder,
            "os": model.os,
        }

    @classmethod
    def build_missing_folder(cls):
        """Build data with missing folder for AgentProfilesUpdateModel."""
        data = cls.build_valid()
        del data["folder"]
        return data


class AgentProfilesResponseModelFactory(Factory):
    """Factory for AgentProfilesResponseModel."""

    class Meta:
        """Meta class for AgentProfilesResponseModelFactory."""

        model = AgentProfilesResponseModel

    name = Faker("pystr", min_chars=5, max_chars=30)
    folder = "Mobile Users"
    os = factory.LazyFunction(lambda: [fake.random_element(list(AgentProfileOperatingSystem))])


class ForwardingRuleBasicFactory(Factory):
    """Factory for ForwardingRuleBasic."""

    class Meta:
        """Meta class for ForwardingRuleBasicFactory."""

        model = ForwardingRuleBasic

    name = Faker("pystr", min_chars=5, max_chars=30)
    enabled = Faker("pybool")
    user_locations = "Any"
    destinations = "Any"
    connectivity = "direct"


class ForwardingRuleZtnaFactory(Factory):
    """Factory for ForwardingRuleZtna."""

    class Meta:
        """Meta class for ForwardingRuleZtnaFactory."""

        model = ForwardingRuleZtna

    name = Faker("pystr", min_chars=5, max_chars=30)
    traffic_type = factory.fuzzy.FuzzyChoice(list(ZtnaTrafficType))
    enabled = Faker("pybool")
    user_locations = "Any"
    source_applications = "Any"
    destinations = "Any"
    connectivity = "direct"


class ForwardingProfileCreateModelFactory(Factory):
    """Factory for ForwardingProfileCreateModel."""

    class Meta:
        """Meta class for ForwardingProfileCreateModelFactory."""

        model = ForwardingProfileCreateModel

    name = Faker("pystr", min_chars=5, max_chars=30)
    description = Faker("sentence")
    definition_method = DefinitionMethod.RULES

    @classmethod
    def build_valid(cls):
        """Build valid data for ForwardingProfileCreateModel."""
        return {
            "name": fake.pystr(min_chars=5, max_chars=30),
            "description": fake.sentence(),
            "definition_method": "rules",
            "type": {
                "ztna_agent": {
                    "forwarding_rules": [
                        {
                            "name": fake.pystr(min_chars=5, max_chars=30),
                            "traffic_type": "dns",
                        }
                    ],
                }
            },
        }

    @classmethod
    def build_invalid_name(cls):
        """Build data with invalid name for ForwardingProfileCreateModel."""
        data = cls.build_valid()
        data["name"] = "invalid@name"
        return data


class ForwardingProfileUpdateModelFactory(Factory):
    """Factory for ForwardingProfileUpdateModel."""

    class Meta:
        """Meta class for ForwardingProfileUpdateModelFactory."""

        model = ForwardingProfileUpdateModel

    id = factory.LazyFunction(lambda: fake.uuid4())
    name = Faker("pystr", min_chars=5, max_chars=30)
    description = Faker("sentence")
    definition_method = DefinitionMethod.RULES

    @classmethod
    def build_valid(cls):
        """Build valid data for ForwardingProfileUpdateModel."""
        return {
            "id": fake.uuid4(),
            "name": fake.pystr(min_chars=5, max_chars=30),
            "description": fake.sentence(),
        }


class ForwardingProfileResponseModelFactory(Factory):
    """Factory for ForwardingProfileResponseModel."""

    class Meta:
        """Meta class for ForwardingProfileResponseModelFactory."""

        model = ForwardingProfileResponseModel

    id = factory.LazyFunction(lambda: fake.uuid4())
    name = Faker("pystr", min_chars=5, max_chars=30)
    description = Faker("sentence")
    definition_method = DefinitionMethod.RULES


class DestinationFqdnEntryFactory(Factory):
    """Factory for DestinationFqdnEntry."""

    class Meta:
        """Meta class for DestinationFqdnEntryFactory."""

        model = DestinationFqdnEntry

    name = factory.LazyFunction(lambda: f"{fake.pystr(min_chars=3, max_chars=10)}.example.com")
    port = factory.LazyFunction(lambda: fake.random_int(min=1, max=65535))


class DestinationIpEntryFactory(Factory):
    """Factory for DestinationIpEntry."""

    class Meta:
        """Meta class for DestinationIpEntryFactory."""

        model = DestinationIpEntry

    name = factory.LazyFunction(lambda: fake.ipv4())
    port = factory.LazyFunction(lambda: fake.random_int(min=1, max=65535))


class ForwardingProfileDestinationCreateModelFactory(Factory):
    """Factory for ForwardingProfileDestinationCreateModel."""

    class Meta:
        """Meta class for ForwardingProfileDestinationCreateModelFactory."""

        model = ForwardingProfileDestinationCreateModel

    name = Faker("pystr", min_chars=5, max_chars=30)
    description = Faker("sentence")

    @classmethod
    def build_valid(cls):
        """Build valid data for ForwardingProfileDestinationCreateModel."""
        return {
            "name": fake.pystr(min_chars=5, max_chars=30),
            "description": fake.sentence(),
            "fqdn": [{"name": "*.example.com", "port": 443}],
            "ip_addresses": [{"name": "10.0.0.0/8"}],
        }

    @classmethod
    def build_invalid_name(cls):
        """Build data with invalid name for ForwardingProfileDestinationCreateModel."""
        data = cls.build_valid()
        data["name"] = "invalid@name"
        return data


class ForwardingProfileDestinationUpdateModelFactory(Factory):
    """Factory for ForwardingProfileDestinationUpdateModel."""

    class Meta:
        """Meta class for ForwardingProfileDestinationUpdateModelFactory."""

        model = ForwardingProfileDestinationUpdateModel

    id = factory.LazyFunction(lambda: fake.uuid4())
    name = Faker("pystr", min_chars=5, max_chars=30)
    description = Faker("sentence")

    @classmethod
    def build_valid(cls):
        """Build valid data for ForwardingProfileDestinationUpdateModel."""
        return {
            "id": fake.uuid4(),
            "name": fake.pystr(min_chars=5, max_chars=30),
            "description": fake.sentence(),
        }


class ForwardingProfileDestinationResponseModelFactory(Factory):
    """Factory for ForwardingProfileDestinationResponseModel."""

    class Meta:
        """Meta class for ForwardingProfileDestinationResponseModelFactory."""

        model = ForwardingProfileDestinationResponseModel

    id = factory.LazyFunction(lambda: fake.uuid4())
    name = Faker("pystr", min_chars=5, max_chars=30)
    description = Faker("sentence")


# -------------------- Forwarding Profile sub-resource factories --------------------

from scm.models.mobile_agent.forwarding_profile_regional_and_custom_proxies import (  # noqa: E402
    ForwardingProfileRegionalAndCustomProxyCreateModel,
    ForwardingProfileRegionalAndCustomProxyResponseModel,
    ForwardingProfileRegionalAndCustomProxyUpdateModel,
    RegionalProxyConnectivityName,
    RegionalProxyConnectivityPreference,
    RegionalProxyServer,
    RegionalProxyType,
)
from scm.models.mobile_agent.forwarding_profile_source_applications import (  # noqa: E402
    ForwardingProfileSourceApplicationCreateModel,
    ForwardingProfileSourceApplicationResponseModel,
    ForwardingProfileSourceApplicationUpdateModel,
)
from scm.models.mobile_agent.forwarding_profile_user_locations import (  # noqa: E402
    ForwardingProfileUserLocationCreateModel,
    ForwardingProfileUserLocationResponseModel,
    ForwardingProfileUserLocationUpdateModel,
    UserLocationChoice,
    UserLocationIpEntry,
)


class ForwardingProfileSourceApplicationCreateModelFactory(Factory):
    """Factory for ForwardingProfileSourceApplicationCreateModel."""

    class Meta:
        """Meta class for ForwardingProfileSourceApplicationCreateModelFactory."""

        model = ForwardingProfileSourceApplicationCreateModel

    name = Faker("pystr", min_chars=5, max_chars=30)
    description = Faker("sentence")
    applications = factory.LazyFunction(
        lambda: [fake.pystr(min_chars=5, max_chars=20) for _ in range(fake.random_int(min=1, max=4))]
    )

    @classmethod
    def build_valid(cls):
        """Build valid data for ForwardingProfileSourceApplicationCreateModel."""
        model = cls.build()
        return {
            "name": model.name,
            "description": model.description,
            "applications": model.applications,
        }

    @classmethod
    def build_invalid_name(cls):
        """Build data with invalid name for ForwardingProfileSourceApplicationCreateModel."""
        data = cls.build_valid()
        data["name"] = "invalid name!"
        return data


class ForwardingProfileSourceApplicationUpdateModelFactory(Factory):
    """Factory for ForwardingProfileSourceApplicationUpdateModel."""

    class Meta:
        """Meta class for ForwardingProfileSourceApplicationUpdateModelFactory."""

        model = ForwardingProfileSourceApplicationUpdateModel

    id = Faker("uuid4")
    name = Faker("pystr", min_chars=5, max_chars=30)
    applications = factory.LazyFunction(lambda: [fake.pystr(min_chars=5, max_chars=20)])


class ForwardingProfileSourceApplicationResponseModelFactory(Factory):
    """Factory for ForwardingProfileSourceApplicationResponseModel."""

    class Meta:
        """Meta class for ForwardingProfileSourceApplicationResponseModelFactory."""

        model = ForwardingProfileSourceApplicationResponseModel

    id = Faker("uuid4")
    name = Faker("pystr", min_chars=5, max_chars=30)
    description = Faker("sentence")
    applications = factory.LazyFunction(lambda: [fake.pystr(min_chars=5, max_chars=20)])


class ForwardingProfileUserLocationCreateModelFactory(Factory):
    """Factory for ForwardingProfileUserLocationCreateModel."""

    class Meta:
        """Meta class for ForwardingProfileUserLocationCreateModelFactory."""

        model = ForwardingProfileUserLocationCreateModel

    name = Faker("pystr", min_chars=5, max_chars=30)
    description = Faker("sentence")
    choice = factory.LazyFunction(
        lambda: UserLocationChoice(ip_addresses=[UserLocationIpEntry(name="10.0.0.0/8")])
    )

    @classmethod
    def build_valid(cls):
        """Build valid data for ForwardingProfileUserLocationCreateModel."""
        model = cls.build()
        return {
            "name": model.name,
            "description": model.description,
            "choice": model.choice.model_dump(exclude_unset=True),
        }


class ForwardingProfileUserLocationUpdateModelFactory(Factory):
    """Factory for ForwardingProfileUserLocationUpdateModel."""

    class Meta:
        """Meta class for ForwardingProfileUserLocationUpdateModelFactory."""

        model = ForwardingProfileUserLocationUpdateModel

    id = Faker("uuid4")
    name = Faker("pystr", min_chars=5, max_chars=30)
    choice = factory.LazyFunction(
        lambda: UserLocationChoice(ip_addresses=[UserLocationIpEntry(name="10.0.0.0/8")])
    )


class ForwardingProfileUserLocationResponseModelFactory(Factory):
    """Factory for ForwardingProfileUserLocationResponseModel."""

    class Meta:
        """Meta class for ForwardingProfileUserLocationResponseModelFactory."""

        model = ForwardingProfileUserLocationResponseModel

    id = Faker("uuid4")
    name = Faker("pystr", min_chars=5, max_chars=30)
    description = Faker("sentence")
    choice = factory.LazyFunction(
        lambda: UserLocationChoice(ip_addresses=[UserLocationIpEntry(name="10.0.0.0/8")])
    )


class ForwardingProfileRegionalAndCustomProxyCreateModelFactory(Factory):
    """Factory for ForwardingProfileRegionalAndCustomProxyCreateModel."""

    class Meta:
        """Meta class for ForwardingProfileRegionalAndCustomProxyCreateModelFactory."""

        model = ForwardingProfileRegionalAndCustomProxyCreateModel

    name = Faker("pystr", min_chars=5, max_chars=30)
    type = factory.fuzzy.FuzzyChoice(list(RegionalProxyType))
    description = Faker("sentence")
    proxy_1 = factory.LazyFunction(
        lambda: RegionalProxyServer(fqdn="proxy1.example.com", port=8080)
    )
    connectivity_preference = factory.LazyFunction(
        lambda: [
            RegionalProxyConnectivityPreference(
                name=RegionalProxyConnectivityName.TUNNEL, enabled=True
            )
        ]
    )

    @classmethod
    def build_valid(cls):
        """Build valid data for ForwardingProfileRegionalAndCustomProxyCreateModel."""
        model = cls.build()
        return {
            "name": model.name,
            "type": model.type,
            "description": model.description,
            "proxy_1": model.proxy_1.model_dump(exclude_unset=True),
            "connectivity_preference": [
                pref.model_dump(exclude_unset=True) for pref in model.connectivity_preference
            ],
        }


class ForwardingProfileRegionalAndCustomProxyUpdateModelFactory(Factory):
    """Factory for ForwardingProfileRegionalAndCustomProxyUpdateModel."""

    class Meta:
        """Meta class for ForwardingProfileRegionalAndCustomProxyUpdateModelFactory."""

        model = ForwardingProfileRegionalAndCustomProxyUpdateModel

    id = Faker("uuid4")
    name = Faker("pystr", min_chars=5, max_chars=30)


class ForwardingProfileRegionalAndCustomProxyResponseModelFactory(Factory):
    """Factory for ForwardingProfileRegionalAndCustomProxyResponseModel."""

    class Meta:
        """Meta class for ForwardingProfileRegionalAndCustomProxyResponseModelFactory."""

        model = ForwardingProfileRegionalAndCustomProxyResponseModel

    id = Faker("uuid4")
    name = Faker("pystr", min_chars=5, max_chars=30)
    type = factory.fuzzy.FuzzyChoice(list(RegionalProxyType))
