"""Factory definitions for network Interface Management Profile objects."""

import uuid

import factory

from scm.models.network.interface_management_profile import (
    InterfaceManagementProfileCreateModel,
    InterfaceManagementProfileResponseModel,
    InterfaceManagementProfileUpdateModel,
)


# SDK tests against SCM API
class InterfaceManagementProfileCreateApiFactory(factory.Factory):
    """Factory for creating InterfaceManagementProfileCreateModel instances."""

    class Meta:
        """Meta class that defines the model for InterfaceManagementProfileCreateApiFactory."""

        model = InterfaceManagementProfileCreateModel

    name = factory.Sequence(lambda n: f"if_mgmt_profile_{n}")
    http = None
    https = None
    telnet = None
    ssh = None
    ping = None
    snmp = None
    http_ocsp = None
    response_pages = None
    userid_service = None
    userid_syslog_listener_ssl = None
    userid_syslog_listener_udp = None
    permitted_ip = None
    folder = "Shared"

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)


class InterfaceManagementProfileUpdateApiFactory(factory.Factory):
    """Factory for creating InterfaceManagementProfileUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for InterfaceManagementProfileUpdateApiFactory."""

        model = InterfaceManagementProfileUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"if_mgmt_profile_{n}")
    http = None
    https = None
    telnet = None
    ssh = None
    ping = None
    snmp = None
    http_ocsp = None
    response_pages = None
    userid_service = None
    userid_syslog_listener_ssl = None
    userid_syslog_listener_udp = None
    permitted_ip = None


class InterfaceManagementProfileResponseFactory(factory.Factory):
    """Factory for creating InterfaceManagementProfileResponseModel instances."""

    class Meta:
        """Meta class that defines the model for InterfaceManagementProfileResponseFactory."""

        model = InterfaceManagementProfileResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"if_mgmt_profile_{n}")
    http = None
    https = None
    telnet = None
    ssh = None
    ping = None
    snmp = None
    http_ocsp = None
    response_pages = None
    userid_service = None
    userid_syslog_listener_ssl = None
    userid_syslog_listener_udp = None
    permitted_ip = None
    folder = "Shared"

    @classmethod
    def from_request(cls, request_model: InterfaceManagementProfileCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class InterfaceManagementProfileCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for InterfaceManagementProfileCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"if_mgmt_profile_{n}")
    folder = "Shared"

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestIfMgmtProfile",
            folder="Shared",
            https=True,
            ssh=True,
            ping=True,
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="TestIfMgmtProfile",
            folder="Shared",
            snippet="TestSnippet",
        )

    @classmethod
    def build_with_no_container(cls):
        """Return a data dict without any container."""
        return cls(
            name="TestIfMgmtProfile",
            folder=None,
            snippet=None,
            device=None,
        )


class InterfaceManagementProfileUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for InterfaceManagementProfileUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"if_mgmt_profile_{n}")

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating an interface management profile."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedIfMgmtProfile",
            https=True,
            ssh=True,
        )
