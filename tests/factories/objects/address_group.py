# tests/factories/objects/address_group.py

from uuid import uuid4

import factory  # type: ignore
from faker import Faker

from scm.models.objects.address_group import (
    AddressGroupBaseModel,
    AddressGroupCreateModel,
    AddressGroupResponseModel,
    AddressGroupUpdateModel,
    DynamicFilter,
)

fake = Faker()


class DynamicFilterFactory(factory.Factory):
    """Factory for creating DynamicFilter instances."""

    class Meta:
        model = DynamicFilter

    filter = "'aws.ec2.key.Name.value.scm-test-scm-test-vpc'"


# Base factory for all address group models
class AddressGroupBaseFactory(factory.Factory):
    """Base factory for AddressGroup with common fields."""

    class Meta:
        model = AddressGroupBaseModel
        abstract = True

    name = factory.Sequence(lambda n: f"address_group_{n}")
    description = fake.sentence()
    tag = ["test-tag", "environment-prod"]

    # Address group type fields default to None
    dynamic = None
    static = None

    # Container fields default to None
    folder = None
    snippet = None
    device = None


class AddressGroupCreateApiFactory(AddressGroupBaseFactory):
    """Factory for creating AddressGroupCreateModel instances with different group types."""

    class Meta:
        model = AddressGroupCreateModel

    # Default to folder container
    folder = "Texas"

    @classmethod
    def with_static(cls, static=None, **kwargs):
        """Create an AddressGroupCreateModel instance with a static address group."""
        if static is None:
            static = ["192.168.1.1"]
        return cls(
            dynamic=None,
            static=static,
            **kwargs,
        )

    @classmethod
    def with_dynamic(cls, filter_str=None, **kwargs):
        """Create an AddressGroupCreateModel instance with a dynamic address group."""
        if filter_str is None:
            filter_str = "'aws.ec2.key.Name.value.scm-test-scm-test-vpc'"
        return cls(
            dynamic=DynamicFilterFactory(filter=filter_str),
            static=None,
            **kwargs,
        )

    @classmethod
    def with_snippet(cls, **kwargs):
        """Create an AddressGroupCreateModel instance with snippet container."""
        return cls(
            folder=None,
            snippet="TestSnippet",
            device=None,
            **kwargs,
        )

    @classmethod
    def with_device(cls, **kwargs):
        """Create an AddressGroupCreateModel instance with device container."""
        return cls(
            folder=None,
            snippet=None,
            device="TestDevice",
            **kwargs,
        )


class AddressGroupUpdateApiFactory(AddressGroupBaseFactory):
    """Factory for creating AddressGroupUpdateModel instances."""

    class Meta:
        model = AddressGroupUpdateModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    tag = ["updated-tag"]

    @classmethod
    def with_static(cls, static=None, **kwargs):
        """Create an AddressGroupUpdateModel instance with a static address group."""
        if static is None:
            static = ["192.168.1.1"]
        return cls(
            dynamic=None,
            static=static,
            **kwargs,
        )

    @classmethod
    def with_dynamic(cls, filter_str=None, **kwargs):
        """Create an AddressGroupUpdateModel instance with a dynamic address group."""
        if filter_str is None:
            filter_str = "'aws.ec2.key.Name.value.scm-test-scm-test-vpc'"
        return cls(
            dynamic=DynamicFilterFactory(filter=filter_str),
            static=None,
            **kwargs,
        )

    @classmethod
    def with_snippet(cls, **kwargs):
        """Create an AddressGroupUpdateModel instance with snippet container."""
        return cls(
            folder=None,
            snippet="TestSnippet",
            device=None,
            **kwargs,
        )

    @classmethod
    def with_device(cls, **kwargs):
        """Create an AddressGroupUpdateModel instance with device container."""
        return cls(
            folder=None,
            snippet=None,
            device="TestDevice",
            **kwargs,
        )


class AddressGroupResponseFactory(AddressGroupBaseFactory):
    """Factory for creating AddressGroupResponseModel instances."""

    class Meta:
        model = AddressGroupResponseModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    folder = "Texas"
    tag = ["response-tag"]

    @classmethod
    def with_static(cls, static=None, **kwargs):
        """Create an AddressGroupResponseModel instance with a static address group."""
        if static is None:
            static = ["192.168.1.1"]
        return cls(
            dynamic=None,
            static=static,
            **kwargs,
        )

    @classmethod
    def with_dynamic(cls, filter_str=None, **kwargs):
        """Create an AddressGroupResponseModel instance with a dynamic address group."""
        if filter_str is None:
            filter_str = "'aws.ec2.key.Name.value.scm-test-scm-test-vpc'"
        return cls(
            dynamic=DynamicFilterFactory(filter=filter_str),
            static=None,
            **kwargs,
        )

    @classmethod
    def with_snippet(cls, **kwargs):
        """Create an AddressGroupResponseModel instance with snippet container."""
        return cls(
            folder=None,
            snippet="TestSnippet",
            device=None,
            **kwargs,
        )

    @classmethod
    def with_device(cls, **kwargs):
        """Create an AddressGroupResponseModel instance with device container."""
        return cls(
            folder=None,
            snippet=None,
            device="TestDevice",
            **kwargs,
        )

    @classmethod
    def from_request(cls, request_model: AddressGroupCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()

        # Remove any fields that shouldn't be in the response
        for field in ["id"]:
            if field in data:
                del data[field]

        # Merge with any provided kwargs
        data.update(kwargs)

        return cls(**data)


# ----------------------------------------------------------------------------
# Address Group model factories for Pydantic validation testing.
# ----------------------------------------------------------------------------


class AddressGroupCreateModelFactory(factory.Factory):
    """Factory for creating data dicts for AddressGroupCreateModel validation testing."""

    class Meta:
        model = dict

    name = factory.Sequence(lambda n: f"address_group_{n}")
    description = fake.sentence()
    folder = "Texas"
    tag = ["test-tag", "environment-prod"]
    dynamic = None
    static = None

    @classmethod
    def build_without_type(cls):
        """Return a data dict without the required group type fields."""
        return {
            "name": "ag_without_type",
            "description": "Address group with neither static nor dynamic type",
            "folder": "Texas",
            "tag": ["test-tag"],
        }

    @classmethod
    def build_with_multiple_types(cls):
        """Return a data dict with multiple type fields."""
        return {
            "name": "ag_multiple_types",
            "description": "Address group with both static and dynamic types",
            "folder": "Texas",
            "tag": ["test-tag"],
            "static": ["192.168.1.1"],
            "dynamic": {"filter": "'aws.ec2.key.Name.value.scm-test-scm-test-vpc'"},
        }

    @classmethod
    def build_with_no_containers(cls):
        """Return a data dict without any containers."""
        return {
            "name": "ag_no_container",
            "description": "Address group without any container",
            "tag": ["test-tag"],
            "static": ["192.168.1.1"],
        }

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return {
            "name": "ag_multiple_containers",
            "description": "Address group with multiple containers",
            "folder": "Texas",
            "snippet": "TestSnippet",
            "tag": ["test-tag"],
            "static": ["192.168.1.1"],
        }

    @classmethod
    def build_valid_static(cls):
        """Return a valid data dict for a static address group."""
        return {
            "name": "valid_static_ag",
            "description": "Valid static address group",
            "folder": "Texas",
            "tag": ["test-tag"],
            "static": ["192.168.1.1", "web-servers"],
        }

    @classmethod
    def build_valid_dynamic(cls):
        """Return a valid data dict for a dynamic address group."""
        return {
            "name": "valid_dynamic_ag",
            "description": "Valid dynamic address group",
            "folder": "Texas",
            "tag": ["test-tag"],
            "dynamic": {"filter": "'aws.ec2.key.Name.value.scm-test-scm-test-vpc'"},
        }


class AddressGroupUpdateModelFactory(factory.Factory):
    """Factory for creating data dicts for AddressGroupUpdateModel validation testing."""

    class Meta:
        model = dict

    id = "12345678-1234-5678-1234-567812345678"
    name = factory.Sequence(lambda n: f"address_group_{n}")
    description = fake.sentence()
    tag = ["test-tag", "environment-prod"]
    dynamic = None
    static = None

    @classmethod
    def build_without_type(cls):
        """Return a data dict without the required group type fields."""
        return {
            "id": "12345678-1234-5678-1234-567812345678",
            "name": "ag_without_type",
            "description": "Address group with neither static nor dynamic type",
            "tag": ["test-tag"],
        }

    @classmethod
    def build_with_multiple_types(cls):
        """Return a data dict with multiple type fields."""
        return {
            "id": "12345678-1234-5678-1234-567812345678",
            "name": "ag_multiple_types",
            "description": "Address group with both static and dynamic types",
            "tag": ["test-tag"],
            "static": ["192.168.1.1"],
            "dynamic": {"filter": "'aws.ec2.key.Name.value.scm-test-scm-test-vpc'"},
        }

    @classmethod
    def build_valid_static(cls):
        """Return a valid data dict for a static address group."""
        return {
            "id": "12345678-1234-5678-1234-567812345678",
            "name": "valid_static_ag",
            "description": "Valid static address group",
            "tag": ["test-tag"],
            "static": ["192.168.1.1", "web-servers"],
        }

    @classmethod
    def build_valid_dynamic(cls):
        """Return a valid data dict for a dynamic address group."""
        return {
            "id": "12345678-1234-5678-1234-567812345678",
            "name": "valid_dynamic_ag",
            "description": "Valid dynamic address group",
            "tag": ["test-tag"],
            "dynamic": {"filter": "'aws.ec2.key.Name.value.scm-test-scm-test-vpc'"},
        }
