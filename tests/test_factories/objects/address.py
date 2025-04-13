# tests/test_factories/objects/address.py

from uuid import uuid4

import factory  # type: ignore
from faker import Faker

from scm.models.objects.address import (
    AddressBaseModel,
    AddressCreateModel,
    AddressResponseModel,
    AddressUpdateModel,
)

fake = Faker()


# Base factory for all address models
class AddressBaseFactory(factory.Factory):
    """Base factory for Address with common fields."""

    class Meta:
        model = AddressBaseModel
        abstract = True

    name = factory.Sequence(lambda n: f"address_{n}")
    description = fake.sentence()
    tag = ["test-tag", "environment-prod"]

    # Address type fields default to None
    ip_netmask = None
    ip_range = None
    ip_wildcard = None
    fqdn = None

    # Container fields default to None
    folder = None
    snippet = None
    device = None


class AddressCreateApiFactory(AddressBaseFactory):
    """Factory for creating AddressCreateModel instances with different address types."""

    class Meta:
        model = AddressCreateModel

    # Default to folder container
    folder = "Texas"

    @classmethod
    def with_ip_netmask(cls, ip_netmask="192.168.1.1/32", **kwargs):
        """Create an AddressCreateModel instance with ip_netmask."""
        return cls(
            ip_netmask=ip_netmask,
            ip_range=None,
            ip_wildcard=None,
            fqdn=None,
            **kwargs,
        )

    @classmethod
    def with_fqdn(cls, fqdn="example.com", **kwargs):
        """Create an AddressCreateModel instance with fqdn."""
        return cls(
            ip_netmask=None,
            ip_range=None,
            ip_wildcard=None,
            fqdn=fqdn,
            **kwargs,
        )

    @classmethod
    def with_ip_range(cls, ip_range="192.168.0.1-192.168.0.10", **kwargs):
        """Create an AddressCreateModel instance with ip_range."""
        return cls(
            ip_netmask=None,
            ip_range=ip_range,
            ip_wildcard=None,
            fqdn=None,
            **kwargs,
        )

    @classmethod
    def with_ip_wildcard(cls, ip_wildcard="10.20.1.0/0.0.248.255", **kwargs):
        """Create an AddressCreateModel instance with ip_wildcard."""
        return cls(
            ip_netmask=None,
            ip_range=None,
            ip_wildcard=ip_wildcard,
            fqdn=None,
            **kwargs,
        )

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Create an AddressCreateModel instance with snippet container."""
        return cls(
            folder=None,
            snippet=snippet,
            device=None,
            **kwargs,
        )

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """Create an AddressCreateModel instance with device container."""
        return cls(
            folder=None,
            snippet=None,
            device=device,
            **kwargs,
        )


class AddressUpdateApiFactory(AddressBaseFactory):
    """Factory for creating AddressUpdateModel instances."""

    class Meta:
        model = AddressUpdateModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    tag = ["updated-tag"]

    @classmethod
    def with_ip_netmask(cls, ip_netmask="192.168.1.100/32", **kwargs):
        """Create an AddressUpdateModel instance with ip_netmask."""
        return cls(
            ip_netmask=ip_netmask,
            ip_range=None,
            ip_wildcard=None,
            fqdn=None,
            **kwargs,
        )

    @classmethod
    def with_fqdn(cls, fqdn="example.com", **kwargs):
        """Create an AddressUpdateModel instance with fqdn."""
        return cls(
            ip_netmask=None,
            ip_range=None,
            ip_wildcard=None,
            fqdn=fqdn,
            **kwargs,
        )

    @classmethod
    def with_ip_range(cls, ip_range="192.168.0.1-192.168.0.10", **kwargs):
        """Create an AddressUpdateModel instance with ip_range."""
        return cls(
            ip_netmask=None,
            ip_range=ip_range,
            ip_wildcard=None,
            fqdn=None,
            **kwargs,
        )

    @classmethod
    def with_ip_wildcard(cls, ip_wildcard="10.20.1.0/0.0.248.255", **kwargs):
        """Create an AddressUpdateModel instance with ip_wildcard."""
        return cls(
            ip_netmask=None,
            ip_range=None,
            ip_wildcard=ip_wildcard,
            fqdn=None,
            **kwargs,
        )

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Create an AddressUpdateModel instance with snippet container."""
        return cls(
            folder=None,
            snippet=snippet,
            device=None,
            **kwargs,
        )

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """Create an AddressUpdateModel instance with device container."""
        return cls(
            folder=None,
            snippet=None,
            device=device,
            **kwargs,
        )


class AddressResponseFactory(AddressBaseFactory):
    """Factory for creating AddressResponseModel instances."""

    class Meta:
        model = AddressResponseModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    tag = ["response-tag"]
    folder = "Texas"

    @classmethod
    def with_ip_netmask(cls, ip_netmask="192.168.1.1/32", **kwargs):
        """Create an AddressResponseModel instance with ip_netmask."""
        return cls(
            ip_netmask=ip_netmask,
            ip_range=None,
            ip_wildcard=None,
            fqdn=None,
            **kwargs,
        )

    @classmethod
    def with_fqdn(cls, fqdn="example.com", **kwargs):
        """Create an AddressResponseModel instance with fqdn."""
        return cls(
            ip_netmask=None,
            ip_range=None,
            ip_wildcard=None,
            fqdn=fqdn,
            **kwargs,
        )

    @classmethod
    def with_ip_range(cls, ip_range="192.168.0.1-192.168.0.10", **kwargs):
        """Create an AddressResponseModel instance with ip_range."""
        return cls(
            ip_netmask=None,
            ip_range=ip_range,
            ip_wildcard=None,
            fqdn=None,
            **kwargs,
        )

    @classmethod
    def with_ip_wildcard(cls, ip_wildcard="10.20.1.0/0.0.248.255", **kwargs):
        """Create an AddressResponseModel instance with ip_wildcard."""
        return cls(
            ip_netmask=None,
            ip_range=None,
            ip_wildcard=ip_wildcard,
            fqdn=None,
            **kwargs,
        )

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Create an AddressResponseModel instance with snippet container."""
        return cls(
            folder=None,
            snippet=snippet,
            device=None,
            **kwargs,
        )

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """Create an AddressResponseModel instance with device container."""
        return cls(
            folder=None,
            snippet=None,
            device=device,
            **kwargs,
        )

    @classmethod
    def from_request(cls, request_model: AddressCreateModel, **kwargs):
        """Create a response model based on a request model."""
        # Start with the base fields from the request
        data = {
            "name": request_model.name,
            "description": request_model.description,
            "tag": request_model.tag,
        }

        # Add the container from the request
        if request_model.folder:
            data["folder"] = request_model.folder
        if request_model.snippet:
            data["snippet"] = request_model.snippet
        if request_model.device:
            data["device"] = request_model.device

        # Add the address type from the request
        if request_model.ip_netmask:
            data["ip_netmask"] = request_model.ip_netmask
        if request_model.ip_range:
            data["ip_range"] = request_model.ip_range
        if request_model.ip_wildcard:
            data["ip_wildcard"] = request_model.ip_wildcard
        if request_model.fqdn:
            data["fqdn"] = request_model.fqdn

        # Override with any additional kwargs
        data.update(kwargs)

        return cls(**data)


# ----------------------------------------------------------------------------
# Address model factories for Pydantic validation testing.
# ----------------------------------------------------------------------------


class AddressCreateModelFactory(factory.Factory):
    """Factory for creating data dicts for AddressCreateModel validation testing."""

    class Meta:
        model = dict

    name = factory.Sequence(lambda n: f"address_{n}")
    description = fake.sentence()
    tag = ["test-tag", "environment-prod"]

    @classmethod
    def build_without_type(cls):
        """Return a data dict without the required address type fields."""
        return cls.build(
            name="address_no_type",
            folder="Texas",
        )

    @classmethod
    def build_with_multiple_types(cls):
        """Return a data dict with multiple type fields."""
        return cls.build(
            name="address_multiple_types",
            folder="Texas",
            ip_netmask="192.168.1.1/32",
            fqdn="example.com",
        )

    @classmethod
    def build_with_no_containers(cls):
        """Return a data dict without any containers."""
        return cls.build(
            name="address_no_container",
            ip_netmask="192.168.1.1/32",
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return {
            "name": "address_multiple_containers",
            "ip_netmask": "192.168.1.1/32",
            "folder": "Texas",
            "snippet": "TestSnippet",
        }

    @classmethod
    def build_valid(cls):
        """Return a data dict with all the expected attributes."""
        return cls.build(
            name="valid_address",
            description="Valid address with all fields",
            ip_netmask="192.168.1.1/32",
            folder="Texas",
            tag=["test-tag", "another-tag"],
        )


class AddressUpdateModelFactory(factory.Factory):
    """Factory for creating data dicts for AddressUpdateModel validation testing."""

    class Meta:
        model = dict

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"address_{n}")
    description = fake.sentence()
    folder = "Texas"
    tag = ["test-tag", "environment-prod"]

    @classmethod
    def build_without_type(cls):
        """Return a data dict without the required address type fields."""
        return cls.build(
            name="address_no_type",
            folder="Texas",
        )

    @classmethod
    def build_with_multiple_types(cls):
        """Return a data dict with multiple type fields."""
        return cls.build(
            name="address_multiple_types",
            folder="Texas",
            ip_netmask="192.168.1.1/32",
            fqdn="example.com",
        )

    @classmethod
    def build_with_no_containers(cls):
        """Return a data dict without any containers."""
        return cls.build(
            name="address_no_container",
            ip_netmask="192.168.1.1/32",
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "address_multiple_containers",
            "ip_netmask": "192.168.1.1/32",
            "folder": "Texas",
            "snippet": "TestSnippet",
        }

    @classmethod
    def build_valid(cls):
        """Return a data dict with all the expected attributes."""
        return cls.build(
            name="valid_address",
            description="Valid address with all fields",
            ip_netmask="192.168.1.1/32",
            folder="Texas",
            tag=["test-tag", "another-tag"],
        )
