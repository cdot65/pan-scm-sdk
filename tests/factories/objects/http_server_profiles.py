# tests/factories/objects/http_server_profiles.py

"""Factory definitions for HTTP server profile objects."""

from typing import Dict
from uuid import uuid4

import factory  # type: ignore
from faker import Faker

from scm.models.objects.http_server_profiles import (
    HTTPServerProfileBaseModel,
    HTTPServerProfileCreateModel,
    HTTPServerProfileResponseModel,
    HTTPServerProfileUpdateModel,
    PayloadFormatModel,
    ServerModel,
)

fake = Faker()


# ----------------------------------------------------------------------------
# Nested Model Factories
# ----------------------------------------------------------------------------


class ServerModelFactory(factory.Factory):
    """Factory for creating ServerModel instances."""

    class Meta:
        """Meta class that defines the model for ServerModelFactory, inheriting from factory.Factory."""

        model = ServerModel

    name = factory.Sequence(lambda n: f"server_{n}")
    address = factory.Faker("ipv4")
    protocol = "HTTPS"
    port = 443
    tls_version = "1.2"
    certificate_profile = None
    http_method = "GET"
    username = None
    password = None


class PayloadFormatModelFactory(factory.Factory):
    """Factory for creating PayloadFormatModel instances."""

    class Meta:
        """Meta class that defines the model for PayloadFormatModelFactory."""

        model = PayloadFormatModel

    name = "Default"
    url_format = "/api/logs"
    headers = [{"name": "Content-Type", "value": "application/json"}]
    params = [{"name": "format", "value": "json"}]
    payload = '{"event": "$eventid", "ip": "$src", "timestamp": "$time_generated"}'


# ----------------------------------------------------------------------------
# Base Factory for HTTP Server Profiles
# ----------------------------------------------------------------------------


class HTTPServerProfileBaseFactory(factory.Factory):
    """Base factory for HTTP Server Profile with common fields."""

    class Meta:
        """Meta class that defines the model for HTTPServerProfileBaseFactory."""

        model = HTTPServerProfileBaseModel
        abstract = True

    name = factory.Sequence(lambda n: f"http_server_profile_{n}")
    description = fake.sentence()
    tag_registration = False

    # Server configurations
    @factory.lazy_attribute
    def server(self):
        """Generate a list of server configurations."""
        return [ServerModelFactory()]

    # Format settings - default to None
    format = None

    # Container fields default to None
    folder = None
    snippet = None
    device = None


# ----------------------------------------------------------------------------
# API Factories for HTTP Server Profiles
# ----------------------------------------------------------------------------


class HTTPServerProfileCreateApiFactory(HTTPServerProfileBaseFactory):
    """Factory for creating HTTPServerProfileCreateModel instances."""

    class Meta:
        """Meta class that defines the model for HTTPServerProfileCreateModelFactory."""

        model = HTTPServerProfileCreateModel

    # Default to folder container
    folder = "Texas"

    @classmethod
    def with_multiple_servers(cls, count=2, **kwargs):
        """Create a profile with multiple servers."""
        servers = [ServerModelFactory() for _ in range(count)]
        return cls(server=servers, **kwargs)

    @classmethod
    def with_formats(cls, log_types=None, **kwargs):
        """Create a profile with format settings for specific log types."""
        if log_types is None:
            log_types = ["config", "system", "traffic"]

        formats = {log_type: PayloadFormatModelFactory() for log_type in log_types}
        return cls(format=formats, **kwargs)

    @classmethod
    def with_snippet(cls, **kwargs):
        """Create a profile with snippet container."""
        return cls(
            folder=None,
            snippet="TestSnippet",
            device=None,
            **kwargs,
        )

    @classmethod
    def with_device(cls, **kwargs):
        """Create a profile with device container."""
        return cls(
            folder=None,
            snippet=None,
            device="TestDevice",
            **kwargs,
        )


class HTTPServerProfileUpdateApiFactory(HTTPServerProfileBaseFactory):
    """Factory for creating HTTPServerProfileUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for HTTPServerProfileUpdateModelFactory."""

        model = HTTPServerProfileUpdateModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    folder = "Texas"  # Default to folder container

    @classmethod
    def with_multiple_servers(cls, count=2, **kwargs):
        """Create a profile with multiple servers."""
        servers = [ServerModelFactory() for _ in range(count)]
        return cls(server=servers, **kwargs)

    @classmethod
    def with_formats(cls, log_types=None, **kwargs):
        """Create a profile with format settings for specific log types."""
        if log_types is None:
            log_types = ["config", "system", "traffic"]

        formats = {log_type: PayloadFormatModelFactory() for log_type in log_types}
        return cls(format=formats, **kwargs)

    @classmethod
    def with_snippet(cls, **kwargs):
        """Create a profile with snippet container."""
        return cls(
            folder=None,
            snippet="TestSnippet",
            device=None,
            **kwargs,
        )

    @classmethod
    def with_device(cls, **kwargs):
        """Create a profile with device container."""
        return cls(
            folder=None,
            snippet=None,
            device="TestDevice",
            **kwargs,
        )


class HTTPServerProfileResponseFactory(HTTPServerProfileBaseFactory):
    """Factory for creating HTTPServerProfileResponseModel instances."""

    class Meta:
        """Meta class that defines the model for HTTPServerProfileResponseModelFactory."""

        model = HTTPServerProfileResponseModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    folder = "Texas"  # Default to folder container

    @classmethod
    def with_multiple_servers(cls, count=2, **kwargs):
        """Create a profile with multiple servers."""
        servers = [ServerModelFactory() for _ in range(count)]
        return cls(server=servers, **kwargs)

    @classmethod
    def with_formats(cls, log_types=None, **kwargs):
        """Create a profile with format settings for specific log types."""
        if log_types is None:
            log_types = ["config", "system", "traffic"]

        formats = {log_type: PayloadFormatModelFactory() for log_type in log_types}
        return cls(format=formats, **kwargs)

    @classmethod
    def with_snippet(cls, **kwargs):
        """Create a profile with snippet container."""
        return cls(
            folder=None,
            snippet="TestSnippet",
            device=None,
            **kwargs,
        )

    @classmethod
    def with_device(cls, **kwargs):
        """Create a profile with device container."""
        return cls(
            folder=None,
            snippet=None,
            device="TestDevice",
            **kwargs,
        )

    @classmethod
    def from_request(cls, request_data: Dict, **kwargs):
        """Create a response model from a request dictionary."""
        # Combine request data with the provided kwargs
        data = {**request_data, **kwargs}
        return cls(**data)


# ----------------------------------------------------------------------------
# Model Factories for Validation Testing
# ----------------------------------------------------------------------------


class HTTPServerProfileCreateModelFactory:
    """Factory for creating data dicts for HTTPServerProfileCreateModel validation testing."""

    model = dict
    name = factory.Sequence(lambda n: f"http_server_profile_{n}")
    description = fake.sentence()
    folder = "Texas"
    tag_registration = False
    server = [
        {
            "name": "primary_server",
            "address": "192.168.1.100",
            "protocol": "HTTPS",
            "port": 443,
        }
    ]
    format = None

    @classmethod
    def build_valid(cls, **kwargs) -> Dict:
        """Return a valid data dict for validation."""
        # Generate a name with the sequence if not provided
        name = kwargs.get("name", f"http_server_profile_{fake.random_int()}")

        data = {
            "name": name,
            "description": kwargs.get("description", cls.description),
            "folder": kwargs.get("folder", cls.folder),
            "server": kwargs.get("server", cls.server),
        }

        if "tag_registration" in kwargs:
            data["tag_registration"] = kwargs["tag_registration"]

        if "format" in kwargs and kwargs["format"] is not None:
            data["format"] = kwargs["format"]

        return data

    @classmethod
    def build_with_no_containers(cls) -> Dict:
        """Return a data dict without any containers."""
        data = cls.build_valid()
        data.pop("folder", None)
        return data

    @classmethod
    def build_with_multiple_containers(cls) -> Dict:
        """Return a data dict with multiple containers."""
        data = cls.build_valid()
        data["snippet"] = "TestSnippet"
        data["device"] = "TestDevice"
        return data

    @classmethod
    def build_with_log_formats(cls, log_types=None) -> Dict:
        """Return a data dict with format settings for specific log types."""
        if log_types is None:
            log_types = ["config", "system", "traffic"]

        formats = {}
        for log_type in log_types:
            formats[log_type] = {
                "name": "Default",
                "url_format": f"/api/logs/{log_type}",
                "headers": [{"name": "Content-Type", "value": "application/json"}],
                "params": [{"name": "format", "value": "json"}],
                "payload": f'{{"event": "$eventid", "type": "{log_type}", "timestamp": "$time_generated"}}',
            }

        data = cls.build_valid()
        data["format"] = formats
        return data


class HTTPServerProfileUpdateModelFactory:
    """Factory for creating data dicts for HTTPServerProfileUpdateModel validation testing."""

    model = dict
    id = "12345678-1234-5678-1234-567812345678"
    name = factory.Sequence(lambda n: f"http_server_profile_{n}")
    description = fake.sentence()
    folder = "Texas"
    tag_registration = False
    server = [
        {
            "name": "primary_server",
            "address": "192.168.1.100",
            "protocol": "HTTPS",
            "port": 443,
        }
    ]
    format = None

    @classmethod
    def build_valid(cls, **kwargs) -> Dict:
        """Return a valid data dict for validation."""
        # Generate a name with the sequence if not provided
        name = kwargs.get("name", f"http_server_profile_{fake.random_int()}")

        data = {
            "id": kwargs.get("id", cls.id),
            "name": name,
            "description": kwargs.get("description", cls.description),
            "server": kwargs.get("server", cls.server),
        }

        # Add folder if provided
        if "folder" in kwargs:
            data["folder"] = kwargs["folder"]
        else:
            data["folder"] = cls.folder

        if "tag_registration" in kwargs:
            data["tag_registration"] = kwargs["tag_registration"]

        if "format" in kwargs and kwargs["format"] is not None:
            data["format"] = kwargs["format"]

        return data

    @classmethod
    def build_without_id(cls) -> Dict:
        """Return a data dict without the required id field."""
        data = cls.build_valid()
        data.pop("id", None)
        return data

    @classmethod
    def build_with_invalid_id(cls) -> Dict:
        """Return a data dict with an invalid id format."""
        data = cls.build_valid()
        data["id"] = "not-a-valid-uuid"
        return data

    @classmethod
    def build_with_log_formats(cls, log_types=None) -> Dict:
        """Return a data dict with format settings for specific log types."""
        if log_types is None:
            log_types = ["config", "system", "traffic"]

        formats = {}
        for log_type in log_types:
            formats[log_type] = {
                "name": "Default",
                "url_format": f"/api/logs/{log_type}",
                "headers": [{"name": "Content-Type", "value": "application/json"}],
                "params": [{"name": "format", "value": "json"}],
                "payload": f'{{"event": "$eventid", "type": "{log_type}", "timestamp": "$time_generated"}}',
            }

        data = cls.build_valid()
        data["format"] = formats
        return data


class HTTPServerProfileResponseModelFactory:
    """Factory for creating data dicts for HTTPServerProfileResponseModel validation testing."""

    model = dict
    id = "12345678-1234-5678-1234-567812345678"
    name = factory.Sequence(lambda n: f"http_server_profile_{n}")
    description = fake.sentence()
    folder = "Texas"
    tag_registration = False
    server = [
        {
            "name": "primary_server",
            "address": "192.168.1.100",
            "protocol": "HTTPS",
            "port": 443,
        }
    ]
    format = None

    @classmethod
    def build_valid(cls, **kwargs) -> Dict:
        """Return a valid data dict for validation."""
        # Generate a name with the sequence if not provided
        name = kwargs.get("name", f"http_server_profile_{fake.random_int()}")

        data = {
            "id": kwargs.get("id", cls.id),
            "name": name,
            "description": kwargs.get("description", cls.description),
            "folder": kwargs.get("folder", cls.folder),
            "server": kwargs.get("server", cls.server),
        }

        if "tag_registration" in kwargs:
            data["tag_registration"] = kwargs["tag_registration"]

        if "format" in kwargs and kwargs["format"] is not None:
            data["format"] = kwargs["format"]

        return data

    @classmethod
    def build_without_id(cls) -> Dict:
        """Return a data dict without the required id field."""
        data = cls.build_valid()
        data.pop("id", None)
        return data

    @classmethod
    def build_with_invalid_id(cls) -> Dict:
        """Return a data dict with an invalid id format."""
        data = cls.build_valid()
        data["id"] = "not-a-valid-uuid"
        return data
