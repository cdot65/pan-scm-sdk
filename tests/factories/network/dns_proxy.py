"""Factory definitions for network DNS Proxy objects."""

import uuid

import factory

from scm.models.network.dns_proxy import (
    DnsProxyCreateModel,
    DnsProxyResponseModel,
    DnsProxyUpdateModel,
)


# SDK tests against SCM API
class DnsProxyCreateApiFactory(factory.Factory):
    """Factory for creating DnsProxyCreateModel instances."""

    class Meta:
        """Meta class that defines the model for DnsProxyCreateApiFactory."""

        model = DnsProxyCreateModel

    name = factory.Sequence(lambda n: f"dns_proxy_{n}")
    folder = "Shared"
    enabled = True
    default = None
    interface = None
    domain_servers = None
    static_entries = None
    tcp_queries = None
    udp_queries = None
    cache = None

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def with_default_server(cls, **kwargs):
        """Create an instance with a default DNS server."""
        return cls(
            default={
                "primary": "8.8.8.8",
                "secondary": "8.8.4.4",
            },
            **kwargs,
        )


class DnsProxyUpdateApiFactory(factory.Factory):
    """Factory for creating DnsProxyUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for DnsProxyUpdateApiFactory."""

        model = DnsProxyUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"dns_proxy_{n}")
    enabled = True
    default = None
    interface = None
    domain_servers = None
    static_entries = None
    tcp_queries = None
    udp_queries = None
    cache = None


class DnsProxyResponseFactory(factory.Factory):
    """Factory for creating DnsProxyResponseModel instances."""

    class Meta:
        """Meta class that defines the model for DnsProxyResponseFactory."""

        model = DnsProxyResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"dns_proxy_{n}")
    folder = "Shared"
    enabled = True
    default = None
    interface = None
    domain_servers = None
    static_entries = None
    tcp_queries = None
    udp_queries = None
    cache = None

    @classmethod
    def from_request(cls, request_model: DnsProxyCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class DnsProxyCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for DnsProxyCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"dns_proxy_{n}")
    folder = "Shared"

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestDnsProxy",
            folder="Shared",
            enabled=True,
            default={
                "primary": "8.8.8.8",
                "secondary": "8.8.4.4",
            },
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="TestDnsProxy",
            folder="Shared",
            snippet="TestSnippet",
        )

    @classmethod
    def build_with_no_container(cls):
        """Return a data dict without any container."""
        return cls(
            name="TestDnsProxy",
            folder=None,
            snippet=None,
            device=None,
        )


class DnsProxyUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for DnsProxyUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"dns_proxy_{n}")

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating a DNS proxy."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedDnsProxy",
            enabled=True,
        )
