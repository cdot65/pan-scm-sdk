# tests/test_factories/objects/service.py

from uuid import uuid4

import factory  # type: ignore
from faker import Faker

from scm.models.objects.service import (
    Override,
    ServiceBaseModel,
    ServiceCreateModel,
    ServiceResponseModel,
    ServiceUpdateModel,
    TCPProtocol,
    UDPProtocol,
)

fake = Faker()


# ----------------------------------------------------------------------------
# Protocol sub-factories
# ----------------------------------------------------------------------------


class OverrideFactory(factory.Factory):
    """Factory for creating Override instances."""

    class Meta:
        model = Override

    timeout = 3600  # Default value from OpenAPI spec
    halfclose_timeout = 120  # Default value from OpenAPI spec
    timewait_timeout = 15  # Default value from OpenAPI spec

    @classmethod
    def with_minimum_timeouts(cls, **kwargs):
        """Create an Override instance with minimum allowed timeout values."""
        return cls(timeout=1, halfclose_timeout=1, timewait_timeout=1, **kwargs)

    @classmethod
    def with_maximum_timeouts(cls, **kwargs):
        """Create an Override instance with maximum allowed timeout values."""
        return cls(timeout=604800, halfclose_timeout=604800, timewait_timeout=600, **kwargs)


class TCPProtocolFactory(factory.Factory):
    """Factory for creating TCPProtocol instances."""

    class Meta:
        model = TCPProtocol

    port = "80,443"
    source_port = None  # Added source_port field from OpenAPI spec
    override = factory.SubFactory(OverrideFactory)

    @classmethod
    def with_source_port(cls, port="80,443", source_port="1024-2048", **kwargs):
        """Create a TCPProtocol instance with source port specified."""
        return cls(port=port, source_port=source_port, **kwargs)

    @classmethod
    def with_timeout_edge_cases(cls, min_timeouts=False, max_timeouts=False, **kwargs):
        """Create a TCPProtocol instance with edge case timeout values."""
        if min_timeouts:
            override = OverrideFactory.with_minimum_timeouts()
        elif max_timeouts:
            override = OverrideFactory.with_maximum_timeouts()
        else:
            override = OverrideFactory()

        return cls(override=override, **kwargs)


class UDPProtocolFactory(factory.Factory):
    """Factory for creating UDPProtocol instances."""

    class Meta:
        model = UDPProtocol

    port = "53"
    source_port = None  # Added source_port field from OpenAPI spec
    override = factory.SubFactory(OverrideFactory)

    @classmethod
    def with_source_port(cls, port="53", source_port="1024-2048", **kwargs):
        """Create a UDPProtocol instance with source port specified."""
        return cls(port=port, source_port=source_port, **kwargs)

    @classmethod
    def with_timeout_edge_cases(cls, min_timeouts=False, max_timeouts=False, **kwargs):
        """Create a UDPProtocol instance with edge case timeout values."""
        if min_timeouts:
            override = OverrideFactory.with_minimum_timeouts()
        elif max_timeouts:
            override = OverrideFactory.with_maximum_timeouts()
        else:
            override = OverrideFactory(timeout=30)  # UDP default is 30s

        return cls(override=override, **kwargs)


# ----------------------------------------------------------------------------
# Base Service factory
# ----------------------------------------------------------------------------


class ServiceBaseFactory(factory.Factory):
    """Base factory for Service with common fields."""

    class Meta:
        model = ServiceBaseModel
        abstract = True

    name = factory.Sequence(lambda n: f"service_{n}")
    description = fake.sentence()
    tag = ["test-tag", "environment-prod"]
    protocol = None

    # Container fields default to None
    folder = None
    snippet = None
    device = None


# ----------------------------------------------------------------------------
# Service factories for API interaction testing
# ----------------------------------------------------------------------------


class ServiceCreateApiFactory(ServiceBaseFactory):
    """Factory for creating ServiceCreateModel instances with different protocols."""

    class Meta:
        model = ServiceCreateModel

    # Default to folder container
    folder = "Texas"

    @classmethod
    def with_tcp(cls, port="80,443", **kwargs):
        """Create a ServiceCreateModel instance with TCP protocol."""
        return cls(protocol={"tcp": {"port": port}}, **kwargs)

    @classmethod
    def with_tcp_source_port(cls, port="80,443", source_port="1024-2048", **kwargs):
        """Create a ServiceCreateModel instance with TCP protocol including source port."""
        return cls(protocol={"tcp": {"port": port, "source_port": source_port}}, **kwargs)

    @classmethod
    def with_tcp_overrides(
        cls,
        port="80,443",
        timeout=3600,
        halfclose_timeout=120,
        timewait_timeout=15,
        **kwargs,
    ):
        """Create a ServiceCreateModel instance with TCP protocol and override settings."""
        override = {}
        if timeout is not None:
            override["timeout"] = timeout
        if halfclose_timeout is not None:
            override["halfclose_timeout"] = halfclose_timeout
        if timewait_timeout is not None:
            override["timewait_timeout"] = timewait_timeout

        tcp_config = {"port": port}
        if override:
            tcp_config["override"] = override

        return cls(protocol={"tcp": tcp_config}, **kwargs)

    @classmethod
    def with_udp(cls, port="53", **kwargs):
        """Create a ServiceCreateModel instance with UDP protocol."""
        return cls(protocol={"udp": {"port": port}}, **kwargs)

    @classmethod
    def with_udp_source_port(cls, port="53", source_port="1024-2048", **kwargs):
        """Create a ServiceCreateModel instance with UDP protocol including source port."""
        return cls(protocol={"udp": {"port": port, "source_port": source_port}}, **kwargs)

    @classmethod
    def with_udp_override(cls, port="53", timeout=30, **kwargs):
        """Create a ServiceCreateModel instance with UDP protocol and override settings."""
        tcp_config = {"port": port}
        if timeout is not None:
            tcp_config["override"] = {"timeout": timeout}

        return cls(protocol={"udp": tcp_config}, **kwargs)

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def with_invalid_name(cls, **kwargs):
        """Create an instance with an invalid name (failing pattern validation)."""
        return cls(name="invalid@name#", **kwargs)

    @classmethod
    def build_without_protocol(cls, **kwargs):
        """Return an instance without the required protocol field."""
        return cls(protocol=None, **kwargs)

    @classmethod
    def build_with_multiple_protocols(cls, **kwargs):
        """Return an instance with both TCP and UDP protocols (should fail validation)."""
        protocol_data = {
            "tcp": {"port": "80,443"},
            "udp": {"port": "53"},
        }
        return cls(protocol=protocol_data, **kwargs)

    @classmethod
    def build_with_no_containers(cls, **kwargs):
        """Return an instance without any containers (should fail validation)."""
        return cls(folder=None, snippet=None, device=None, **kwargs)

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Return an instance with multiple containers (should fail validation)."""
        return cls(folder="Texas", snippet="TestSnippet", device=None, **kwargs)

    @classmethod
    def build_with_timeout_edge_cases(cls, min_timeouts=False, max_timeouts=False, **kwargs):
        """Create instance with edge case timeout values."""
        if min_timeouts:
            override = {"timeout": 1, "halfclose_timeout": 1, "timewait_timeout": 1}
        elif max_timeouts:
            override = {
                "timeout": 604800,
                "halfclose_timeout": 604800,
                "timewait_timeout": 600,
            }
        else:
            override = {
                "timeout": 3600,
                "halfclose_timeout": 120,
                "timewait_timeout": 15,
            }

        return cls(protocol={"tcp": {"port": "80,443", "override": override}}, **kwargs)


class ServiceUpdateApiFactory(ServiceBaseFactory):
    """Factory for creating ServiceUpdateModel instances."""

    class Meta:
        model = ServiceUpdateModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    name = factory.Sequence(lambda n: f"service_{n}")
    description = fake.sentence()
    tag = ["updated-tag"]
    protocol = None

    @classmethod
    def with_tcp(cls, port="80,443", **kwargs):
        """Create a ServiceUpdateModel instance with TCP protocol."""
        return cls(protocol={"tcp": {"port": port}}, **kwargs)

    @classmethod
    def with_tcp_source_port(cls, port="80,443", source_port="1024-2048", **kwargs):
        """Create a ServiceUpdateModel instance with TCP protocol including source port."""
        return cls(protocol={"tcp": {"port": port, "source_port": source_port}}, **kwargs)

    @classmethod
    def with_tcp_overrides(
        cls,
        port="80,443",
        timeout=3600,
        halfclose_timeout=120,
        timewait_timeout=15,
        **kwargs,
    ):
        """Create a ServiceUpdateModel instance with TCP protocol and override settings."""
        override = {}
        if timeout is not None:
            override["timeout"] = timeout
        if halfclose_timeout is not None:
            override["halfclose_timeout"] = halfclose_timeout
        if timewait_timeout is not None:
            override["timewait_timeout"] = timewait_timeout

        tcp_config = {"port": port}
        if override:
            tcp_config["override"] = override

        return cls(protocol={"tcp": tcp_config}, **kwargs)

    @classmethod
    def with_udp(cls, port="53", **kwargs):
        """Create a ServiceUpdateModel instance with UDP protocol."""
        return cls(protocol={"udp": {"port": port}}, **kwargs)

    @classmethod
    def with_udp_source_port(cls, port="53", source_port="1024-2048", **kwargs):
        """Create a ServiceUpdateModel instance with UDP protocol including source port."""
        return cls(protocol={"udp": {"port": port, "source_port": source_port}}, **kwargs)

    @classmethod
    def with_invalid_name(cls, **kwargs):
        """Create an instance with an invalid name (failing pattern validation)."""
        return cls(name="invalid@name#", **kwargs)

    @classmethod
    def build_without_protocol(cls, **kwargs):
        """Return an instance without the required protocol field."""
        return cls(protocol=None, **kwargs)

    @classmethod
    def build_with_multiple_protocols(cls, **kwargs):
        """Return an instance with both TCP and UDP protocols (should fail validation)."""
        protocol_data = {
            "tcp": {"port": "80,443"},
            "udp": {"port": "53"},
        }
        return cls(protocol=protocol_data, **kwargs)

    @classmethod
    def build_with_no_containers(cls, **kwargs):
        """Return an instance without any containers."""
        return cls(folder=None, snippet=None, device=None, **kwargs)

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Return an instance with multiple containers (should fail validation)."""
        return cls(folder="Texas", snippet="TestSnippet", device=None, **kwargs)


class ServiceResponseFactory(ServiceBaseFactory):
    """Factory for creating ServiceResponseModel instances."""

    class Meta:
        model = ServiceResponseModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    name = factory.Sequence(lambda n: f"service_{n}")
    description = fake.sentence()
    folder = "Texas"
    snippet = None
    device = None
    tag = ["response-tag"]
    protocol = None

    @classmethod
    def with_tcp(cls, port="80,443", **kwargs):
        """Create a ServiceResponseModel instance with TCP protocol."""
        return cls(protocol={"tcp": {"port": port}}, **kwargs)

    @classmethod
    def with_tcp_source_port(cls, port="80,443", source_port="1024-2048", **kwargs):
        """Create a ServiceResponseModel instance with TCP protocol including source port."""
        return cls(protocol={"tcp": {"port": port, "source_port": source_port}}, **kwargs)

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
        override = {}
        if timeout is not None:
            override["timeout"] = timeout
        if halfclose_timeout is not None:
            override["halfclose_timeout"] = halfclose_timeout
        if timewait_timeout is not None:
            override["timewait_timeout"] = timewait_timeout

        tcp_config = {"port": port}
        if override:
            tcp_config["override"] = override

        return cls(protocol={"tcp": tcp_config}, **kwargs)

    @classmethod
    def with_udp(cls, port="53", **kwargs):
        """Create a ServiceResponseModel instance with UDP protocol."""
        return cls(protocol={"udp": {"port": port}}, **kwargs)

    @classmethod
    def with_udp_source_port(cls, port="53", source_port="1024-2048", **kwargs):
        """Create a ServiceResponseModel instance with UDP protocol including source port."""
        return cls(protocol={"udp": {"port": port, "source_port": source_port}}, **kwargs)

    @classmethod
    def with_udp_override(
        cls,
        port="53",
        timeout=None,
        **kwargs,
    ):
        """Create a ServiceResponseModel instance with UDP protocol and override settings."""
        tcp_config = {"port": port}
        if timeout is not None:
            tcp_config["override"] = {"timeout": timeout}

        return cls(protocol={"udp": tcp_config}, **kwargs)

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def from_request(cls, request_model: ServiceCreateModel, **kwargs):
        """Create a response model based on a request model."""
        # Convert request model to dict, excluding unset values
        request_dict = request_model.model_dump(exclude_unset=True)

        # Combine with any provided kwargs
        combined_kwargs = {**request_dict, **kwargs}

        # Create and return the response model
        return cls(**combined_kwargs)


# ----------------------------------------------------------------------------
# Service factories for Pydantic model validation testing
# ----------------------------------------------------------------------------


class ServiceCreateModelFactory(factory.Factory):
    """Factory for creating data dicts for ServiceCreateModel."""

    class Meta:
        model = dict

    name = factory.Sequence(lambda n: f"service_{n}")
    description = fake.sentence()
    folder = "Texas"
    snippet = None
    device = None
    tag = ["test-tag", "environment-prod"]
    protocol = None

    @classmethod
    def build_without_protocol(cls, **kwargs):
        """Return a data dict without the required protocol field."""
        data = cls(**kwargs)
        data.pop("protocol", None)
        return data

    @classmethod
    def build_with_multiple_protocols(cls, **kwargs):
        """Return a data dict with both TCP and UDP protocols."""
        data = cls(
            protocol={
                "tcp": {"port": "80,443"},
                "udp": {"port": "53"},
            },
            **kwargs,
        )
        return data

    @classmethod
    def build_with_no_containers(cls, **kwargs):
        """Return a data dict without any containers."""
        data = cls(folder=None, snippet=None, device=None, **kwargs)
        return data

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Return a data dict with multiple containers."""
        data = cls(
            folder="Texas",
            snippet="TestSnippet",
            device=None,
            protocol={"tcp": {"port": "80,443"}},
            **kwargs,
        )
        return data

    @classmethod
    def build_valid_tcp(cls, **kwargs):
        """Return a valid data dict for a TCP service."""
        data = cls(
            protocol={"tcp": {"port": "80,443"}},
            **kwargs,
        )
        return data

    @classmethod
    def build_valid_tcp_with_source_port(cls, **kwargs):
        """Return a valid data dict for a TCP service with source port."""
        data = cls(
            protocol={"tcp": {"port": "80,443", "source_port": "1024-2048"}},
            **kwargs,
        )
        return data

    @classmethod
    def build_valid_udp(cls, **kwargs):
        """Return a valid data dict for a UDP service."""
        data = cls(
            protocol={"udp": {"port": "53"}},
            **kwargs,
        )
        return data

    @classmethod
    def build_valid_udp_with_source_port(cls, **kwargs):
        """Return a valid data dict for a UDP service with source port."""
        data = cls(
            protocol={"udp": {"port": "53", "source_port": "1024-2048"}},
            **kwargs,
        )
        return data

    @classmethod
    def build_with_invalid_name(cls, **kwargs):
        """Return a data dict with an invalid name (failing pattern validation)."""
        data = cls(
            name="invalid@name#",
            protocol={"tcp": {"port": "80,443"}},
            **kwargs,
        )
        return data

    @classmethod
    def build_with_timeout_edge_cases(cls, min_timeouts=False, max_timeouts=False, **kwargs):
        """Create data dict with edge case timeout values."""
        if min_timeouts:
            override = {"timeout": 1, "halfclose_timeout": 1, "timewait_timeout": 1}
        elif max_timeouts:
            override = {
                "timeout": 604800,
                "halfclose_timeout": 604800,
                "timewait_timeout": 600,
            }
        else:
            override = {
                "timeout": 3600,
                "halfclose_timeout": 120,
                "timewait_timeout": 15,
            }

        data = cls(
            protocol={"tcp": {"port": "80,443", "override": override}},
            **kwargs,
        )
        return data


class ServiceUpdateModelFactory(factory.Factory):
    """Factory for creating data dicts for ServiceUpdateModel."""

    class Meta:
        model = dict

    id = factory.LazyFunction(lambda: str(uuid4()))
    name = factory.Sequence(lambda n: f"service_{n}")
    description = fake.sentence()
    tag = ["updated-tag"]
    protocol = None

    @classmethod
    def build_without_protocol(cls, **kwargs):
        """Return a data dict without the required protocol field."""
        data = cls(**kwargs)
        data.pop("protocol", None)
        return data

    @classmethod
    def build_with_multiple_protocols(cls, **kwargs):
        """Return a data dict with both TCP and UDP protocols."""
        data = cls(
            protocol={
                "tcp": {"port": "80,443"},
                "udp": {"port": "53"},
            },
            **kwargs,
        )
        return data

    @classmethod
    def build_with_no_containers(cls, **kwargs):
        """Return a data dict without any containers."""
        data = cls(folder=None, snippet=None, device=None, **kwargs)
        return data

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Return a data dict with multiple containers."""
        data = cls(folder="Texas", snippet="TestSnippet", **kwargs)
        return data

    @classmethod
    def build_valid(cls, **kwargs):
        """Return a valid data dict for updating a service."""
        data = cls(
            protocol={"tcp": {"port": "80,443"}},
            **kwargs,
        )
        return data

    @classmethod
    def build_valid_with_source_port(cls, **kwargs):
        """Return a valid data dict for updating a service with source port."""
        data = cls(
            protocol={"tcp": {"port": "80,443", "source_port": "1024-2048"}},
            **kwargs,
        )
        return data

    @classmethod
    def build_with_invalid_name(cls, **kwargs):
        """Return a data dict with an invalid name (failing pattern validation)."""
        data = cls(
            name="invalid@name#",
            protocol={"tcp": {"port": "80,443"}},
            **kwargs,
        )
        return data
