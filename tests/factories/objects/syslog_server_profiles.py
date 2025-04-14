# tests/factories/objects/syslog_server_profiles.py

from uuid import uuid4

import factory  # type: ignore
from faker import Faker

from scm.models.objects.syslog_server_profiles import (
    EscapingModel,
    FormatModel,
    SyslogServerModel,
    SyslogServerProfileBaseModel,
    SyslogServerProfileCreateModel,
    SyslogServerProfileResponseModel,
    SyslogServerProfileUpdateModel,
)

fake = Faker()


class EscapingModelFactory(factory.Factory):
    """Factory for creating EscapingModel instances."""

    class Meta:
        model = EscapingModel

    escape_character = "\\"
    escaped_characters = "%$[]"


class FormatModelFactory(factory.Factory):
    """Factory for creating FormatModel instances."""

    class Meta:
        model = FormatModel

    escaping = factory.SubFactory(EscapingModelFactory)
    traffic = "$format_string_traffic"
    threat = "$format_string_threat"
    wildfire = "$format_string_wildfire"
    url = "$format_string_url"
    system = "$format_string_system"

    @classmethod
    def minimal(cls):
        """Create a minimal format model with just traffic and threat formats."""
        return cls(
            traffic="$format_string_traffic",
            threat="$format_string_threat",
            escaping=EscapingModelFactory(),
            wildfire=None,
            url=None,
            data=None,
            gtp=None,
            sctp=None,
            tunnel=None,
            auth=None,
            userid=None,
            iptag=None,
            decryption=None,
            config=None,
            system=None,
            globalprotect=None,
            hip_match=None,
            correlation=None,
        )


class SyslogServerModelFactory(factory.Factory):
    """Factory for creating SyslogServerModel instances."""

    class Meta:
        model = SyslogServerModel

    name = factory.Sequence(lambda n: f"server-{n}")
    server = factory.Faker("ipv4")
    transport = "UDP"
    port = 514
    format = "BSD"
    facility = "LOG_USER"

    @classmethod
    def with_tcp(cls, **kwargs):
        """Create a server instance using TCP transport."""
        return cls(transport="TCP", **kwargs)

    @classmethod
    def with_ietf(cls, **kwargs):
        """Create a server instance using IETF format."""
        return cls(format="IETF", **kwargs)

    @classmethod
    def with_custom_facility(cls, facility="LOG_LOCAL0", **kwargs):
        """Create a server instance with custom facility."""
        return cls(facility=facility, **kwargs)


# Base factory for all syslog server profile models
class SyslogServerProfileBaseFactory(factory.Factory):
    """Base factory for Syslog Server Profile with common fields."""

    class Meta:
        model = SyslogServerProfileBaseModel
        abstract = True

    name = factory.Sequence(lambda n: f"syslog-profile-{n}")
    server = factory.List([factory.SubFactory(SyslogServerModelFactory)])
    format = factory.SubFactory(FormatModelFactory)

    # Container fields default to None
    folder = None
    snippet = None
    device = None


class SyslogServerProfileCreateModelFactory(SyslogServerProfileBaseFactory):
    """Factory for creating SyslogServerProfileCreateModel instances."""

    class Meta:
        model = SyslogServerProfileCreateModel

    # Default to folder container
    folder = "Shared"

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        # Ensure server field is included if not provided
        if "server" not in kwargs:
            kwargs["server"] = [SyslogServerModelFactory()]
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """Create an instance with device container."""
        # Ensure server field is included if not provided
        if "server" not in kwargs:
            kwargs["server"] = [SyslogServerModelFactory()]
        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def build_with_multiple_containers(cls):
        """Create data with multiple containers for validation testing."""
        return {
            "name": fake.word(),
            "server": [
                {
                    "name": "test-server",
                    "server": "192.168.1.100",
                    "transport": "UDP",
                    "port": 514,
                    "format": "BSD",
                    "facility": "LOG_USER",
                }
            ],
            "folder": "Shared",
            "snippet": "TestSnippet",
            "device": None,
        }

    @classmethod
    def with_multiple_servers(cls, count=3, **kwargs):
        """Create an instance with multiple server configurations."""
        servers = [SyslogServerModelFactory() for _ in range(count)]
        return cls(server=servers, **kwargs)

    @classmethod
    def with_minimal_format(cls, **kwargs):
        """Create an instance with minimal format configuration."""
        return cls(format=FormatModelFactory.minimal(), **kwargs)


class SyslogServerProfileUpdateModelFactory(SyslogServerProfileBaseFactory):
    """Factory for creating SyslogServerProfileUpdateModel instances."""

    class Meta:
        model = SyslogServerProfileUpdateModel

    id = factory.LazyFunction(lambda: str(uuid4()))

    @classmethod
    def with_updated_servers(cls, **kwargs):
        """Create an instance with updated server list."""
        updated_servers = [
            SyslogServerModelFactory(name="updated-server-1"),
            SyslogServerModelFactory(name="updated-server-2", transport="TCP"),
        ]
        return cls(server=updated_servers, **kwargs)

    @classmethod
    def with_updated_format(cls, **kwargs):
        """Create an instance with updated format settings."""
        updated_format = FormatModelFactory(
            traffic="$updated_traffic_format",
            threat="$updated_threat_format",
        )
        return cls(format=updated_format, **kwargs)


class SyslogServerProfileResponseModelFactory(SyslogServerProfileBaseFactory):
    """Factory for creating SyslogServerProfileResponseModel instances."""

    class Meta:
        model = SyslogServerProfileResponseModel

    id = factory.LazyFunction(lambda: uuid4())  # Note: This is a UUID object, not string
    folder = "Shared"

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Create a response instance with snippet container."""
        if "server" not in kwargs:
            kwargs["server"] = [SyslogServerModelFactory()]
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """Create a response instance with device container."""
        if "server" not in kwargs:
            kwargs["server"] = [SyslogServerModelFactory()]
        return cls(folder=None, snippet=None, device=device, **kwargs)
