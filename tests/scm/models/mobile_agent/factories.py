"""Factory definitions for mobile agent models."""

from factory import Factory, Faker  # type: ignore
import factory.fuzzy  # type: ignore
from faker import Faker as FakerGenerator

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
