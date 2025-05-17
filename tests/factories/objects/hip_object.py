"""Test factories for HIP Objects."""

from typing import Any, Dict, Union
from uuid import uuid4

import factory  # type: ignore
from faker import Faker

from scm.models.objects.hip_object import (
    CertificateAttributeModel,
    CertificateModel,
    DiskEncryptionModel,
    EncryptionLocationModel,
    HIPObjectBaseModel,
    HIPObjectCreateModel,
    HIPObjectResponseModel,
    HIPObjectUpdateModel,
    HostInfoModel,
    MobileDeviceModel,
    NetworkInfoModel,
    PatchManagementModel,
    SecurityVendorModel,
    StrContainsModel,
    StrIsModel,
    StrIsNotModel,
)

fake = Faker()


# Helper Factories for nested components
class StrContainsFactory(factory.Factory):
    """Factory for creating string contains comparison."""

    class Meta:
        model = StrContainsModel

    contains = factory.Faker("word")


class StrIsFactory(factory.Factory):
    """Factory for creating string equality comparison."""

    class Meta:
        model = StrIsModel

    is_ = factory.Faker("word")


class StrIsNotFactory(factory.Factory):
    """Factory for creating string inequality comparison."""

    class Meta:
        model = StrIsNotModel

    is_not = factory.Faker("word")


class SecurityVendorFactory(factory.Factory):
    """Factory for creating security vendor specifications."""

    class Meta:
        model = SecurityVendorModel

    name = factory.Faker("company")
    product = factory.LazyFunction(lambda: [fake.word() for _ in range(2)])


class CertificateAttributeFactory(factory.Factory):
    """Factory for creating certificate attributes."""

    class Meta:
        model = CertificateAttributeModel

    name = factory.Faker("word")
    value = factory.Faker("word")


class HostInfoFactory(factory.Factory):
    """Factory for creating host information section."""

    class Meta:
        model = HostInfoModel

    criteria = factory.Dict(
        {
            "domain": factory.SubFactory(StrContainsFactory),
        }
    )


class NetworkInfoFactory(factory.Factory):
    """Factory for creating network information section."""

    class Meta:
        model = NetworkInfoModel

    criteria = factory.Dict({"network": {"is": {"wifi": {}}}})


class PatchManagementFactory(factory.Factory):
    """Factory for creating patch management section."""

    class Meta:
        model = PatchManagementModel

    criteria = factory.Dict({"missing_patches": {"severity": 3, "check": "has-any"}})


class EncryptionLocationFactory(factory.Factory):
    """Factory for creating encryption location."""

    class Meta:
        model = EncryptionLocationModel

    name = factory.Faker("word")
    encryption_state = {"is": "encrypted"}


class DiskEncryptionFactory(factory.Factory):
    """Factory for creating disk encryption section."""

    class Meta:
        model = DiskEncryptionModel

    criteria = factory.Dict(
        {
            "encrypted_locations": factory.LazyFunction(
                lambda: [EncryptionLocationFactory() for _ in range(1)]
            )
        }
    )


class MobileDeviceFactory(factory.Factory):
    """Factory for creating mobile device section."""

    class Meta:
        model = MobileDeviceModel

    criteria = factory.Dict({"jailbroken": False, "disk_encrypted": True})


class CertificateFactory(factory.Factory):
    """Factory for creating certificate section."""

    class Meta:
        model = CertificateModel

    criteria = factory.Dict(
        {
            "certificate_profile": "test-profile",
            "certificate_attributes": factory.LazyFunction(
                lambda: [CertificateAttributeFactory() for _ in range(1)]
            ),
        }
    )


# Base factory for all HIP object models
class HIPObjectBaseFactory(factory.Factory):
    """Base factory for HIP Object with common fields."""

    class Meta:
        model = HIPObjectBaseModel
        abstract = True

    name = factory.Sequence(lambda n: f"hip_object_{n}")
    description = fake.sentence()

    # Container fields default to None
    folder = None
    snippet = None
    device = None

    # Section fields default to None
    host_info = None
    network_info = None
    patch_management = None
    disk_encryption = None
    mobile_device = None
    certificate = None


class HIPObjectCreateApiFactory(HIPObjectBaseFactory):
    """Factory for creating HIPObjectCreateModel instances."""

    class Meta:
        model = HIPObjectCreateModel

    # Default to folder container
    folder = "My Folder"
    host_info = factory.SubFactory(HostInfoFactory)

    @classmethod
    def with_host_info(cls, **kwargs):
        """Create a HIPObjectCreateModel instance with host info."""
        return cls(
            host_info=HostInfoFactory(),
            **kwargs,
        )

    @classmethod
    def with_network_info(cls, **kwargs):
        """Create a HIPObjectCreateModel instance with network info."""
        return cls(
            network_info=NetworkInfoFactory(),
            **kwargs,
        )

    @classmethod
    def with_patch_management(cls, **kwargs):
        """Create a HIPObjectCreateModel instance with patch management."""
        return cls(
            patch_management=PatchManagementFactory(),
            **kwargs,
        )

    @classmethod
    def with_disk_encryption(cls, **kwargs):
        """Create a HIPObjectCreateModel instance with disk encryption."""
        return cls(
            disk_encryption=DiskEncryptionFactory(),
            **kwargs,
        )

    @classmethod
    def with_mobile_device(cls, **kwargs):
        """Create a HIPObjectCreateModel instance with mobile device."""
        return cls(
            mobile_device=MobileDeviceFactory(),
            **kwargs,
        )

    @classmethod
    def with_certificate(cls, **kwargs):
        """Create a HIPObjectCreateModel instance with certificate."""
        return cls(
            certificate=CertificateFactory(),
            **kwargs,
        )

    @classmethod
    def with_snippet(cls, **kwargs):
        """Create a HIPObjectCreateModel instance with snippet container."""
        return cls(
            folder=None,
            snippet="TestSnippet",
            device=None,
            **kwargs,
        )

    @classmethod
    def with_device(cls, **kwargs):
        """Create a HIPObjectCreateModel instance with device container."""
        return cls(
            folder=None,
            snippet=None,
            device="TestDevice",
            **kwargs,
        )


class HIPObjectUpdateApiFactory(HIPObjectBaseFactory):
    """Factory for creating HIPObjectUpdateModel instances."""

    class Meta:
        model = HIPObjectUpdateModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    folder = "My Folder"
    host_info = factory.SubFactory(HostInfoFactory)

    @classmethod
    def with_host_info(cls, **kwargs):
        """Create a HIPObjectUpdateModel instance with host info."""
        return cls(
            host_info=HostInfoFactory(),
            **kwargs,
        )

    @classmethod
    def with_network_info(cls, **kwargs):
        """Create a HIPObjectUpdateModel instance with network info."""
        return cls(
            network_info=NetworkInfoFactory(),
            **kwargs,
        )

    @classmethod
    def with_patch_management(cls, **kwargs):
        """Create a HIPObjectUpdateModel instance with patch management."""
        return cls(
            patch_management=PatchManagementFactory(),
            **kwargs,
        )

    @classmethod
    def with_disk_encryption(cls, **kwargs):
        """Create a HIPObjectUpdateModel instance with disk encryption."""
        return cls(
            disk_encryption=DiskEncryptionFactory(),
            **kwargs,
        )

    @classmethod
    def with_mobile_device(cls, **kwargs):
        """Create a HIPObjectUpdateModel instance with mobile device."""
        return cls(
            mobile_device=MobileDeviceFactory(),
            **kwargs,
        )

    @classmethod
    def with_certificate(cls, **kwargs):
        """Create a HIPObjectUpdateModel instance with certificate."""
        return cls(
            certificate=CertificateFactory(),
            **kwargs,
        )

    @classmethod
    def with_snippet(cls, **kwargs):
        """Create a HIPObjectUpdateModel instance with snippet container."""
        return cls(
            folder=None,
            snippet="TestSnippet",
            device=None,
            **kwargs,
        )

    @classmethod
    def with_device(cls, **kwargs):
        """Create a HIPObjectUpdateModel instance with device container."""
        return cls(
            folder=None,
            snippet=None,
            device="TestDevice",
            **kwargs,
        )

    @classmethod
    def without_id(cls, **kwargs):
        """Create a HIPObjectUpdateModel instance without ID."""
        return cls(
            id=None,
            **kwargs,
        )

    @classmethod
    def with_additional_encryption_location(cls, **kwargs):
        """Create a HIPObjectUpdateModel instance with disk encryption and additional locations.

        This factory method creates a HIP object update model with disk encryption section
        that includes multiple encrypted locations.

        Args:
            **kwargs: Additional keyword arguments to pass to the factory

        Returns:
            HIPObjectUpdateModel: A configured HIP object update model

        """
        # Create encryption locations
        encrypted_locations = [
            {"name": "C:", "encryption_state": {"is": "encrypted"}},
            {"name": "D:", "encryption_state": {"is": "encrypted"}},
        ]

        # Create disk encryption section
        disk_encryption = {"criteria": {"encrypted_locations": encrypted_locations}}

        # Return HIP object with disk encryption
        return cls(
            disk_encryption=disk_encryption,
            **kwargs,
        )


class HIPObjectResponseFactory(HIPObjectBaseFactory):
    """Factory for creating HIPObjectResponseModel instances."""

    class Meta:
        model = HIPObjectResponseModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    folder = "My Folder"
    host_info = factory.SubFactory(HostInfoFactory)

    @classmethod
    def build(cls, **kwargs):
        """Create a basic HIPObjectResponseModel instance.

        Args:
            **kwargs: Additional keyword arguments to override default values

        Returns:
            HIPObjectResponseModel: A configured HIP object response model

        """
        return cls(**kwargs)

    @classmethod
    def with_host_info(cls, **kwargs):
        """Create a HIPObjectResponseModel instance with host info."""
        return cls(
            host_info=HostInfoFactory(),
            **kwargs,
        )

    @classmethod
    def with_network_info(cls, **kwargs):
        """Create a HIPObjectResponseModel instance with network info."""
        return cls(
            network_info=NetworkInfoFactory(),
            **kwargs,
        )

    @classmethod
    def with_patch_management(cls, **kwargs):
        """Create a HIPObjectResponseModel instance with patch management."""
        return cls(
            patch_management=PatchManagementFactory(),
            **kwargs,
        )

    @classmethod
    def with_disk_encryption(cls, **kwargs):
        """Create a HIPObjectResponseModel instance with disk encryption."""
        return cls(
            disk_encryption=DiskEncryptionFactory(),
            **kwargs,
        )

    @classmethod
    def with_mobile_device(cls, **kwargs):
        """Create a HIPObjectResponseModel instance with mobile device."""
        return cls(
            mobile_device=MobileDeviceFactory(),
            **kwargs,
        )

    @classmethod
    def with_certificate(cls, **kwargs):
        """Create a HIPObjectResponseModel instance with certificate."""
        return cls(
            certificate=CertificateFactory(),
            **kwargs,
        )

    @classmethod
    def with_snippet(cls, **kwargs):
        """Create a HIPObjectResponseModel instance with snippet container."""
        return cls(
            folder=None,
            snippet="TestSnippet",
            device=None,
            **kwargs,
        )

    @classmethod
    def with_device(cls, **kwargs):
        """Create a HIPObjectResponseModel instance with device container."""
        return cls(
            folder=None,
            snippet=None,
            device="TestDevice",
            **kwargs,
        )

    @classmethod
    def from_request(
        cls, request_model: Union[HIPObjectCreateModel, Dict[str, Any]], **kwargs
    ) -> HIPObjectResponseModel:
        """Create a response model based on a request model.

        This is useful for simulating the API's response to a create request.

        Args:
            request_model: The create request model or dictionary to base the response on
            **kwargs: Additional attributes to override in the response

        Returns:
            HIPObjectResponseModel instance

        """
        if isinstance(request_model, dict):
            data = request_model.copy()
        else:
            data = request_model.model_dump()

        # Add or override the id field if not in kwargs
        if "id" not in kwargs:
            data["id"] = str(uuid4())

        # Override with any additional kwargs
        data.update(kwargs)

        return cls(**data)


# ----------------------------------------------------------------------------
# HIP Object model factories for Pydantic validation testing.
# ----------------------------------------------------------------------------


class HIPObjectCreateModelFactory:
    """Factory for creating data dicts for HIPObjectCreateModel validation testing."""

    model = dict
    name = factory.Sequence(lambda n: f"hip_object_{n}")
    description = fake.sentence()
    folder = "My Folder"

    @classmethod
    def build_with_no_containers(cls, **kwargs):
        """Return a data dict without any containers."""
        data = {
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "host_info": {
                "criteria": {
                    "domain": {"contains": "example.com"},
                }
            },
        }
        return data

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Return a data dict with multiple containers."""
        data = {
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "folder": "My Folder",
            "snippet": "My Snippet",
            "host_info": {
                "criteria": {
                    "domain": {"contains": "example.com"},
                }
            },
        }
        return data

    @classmethod
    def build_valid_host_info(cls, **kwargs):
        """Return a valid data dict with host info."""
        data = {
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "folder": kwargs.get("folder", cls.folder),
            "host_info": {
                "criteria": {
                    "domain": {"contains": "example.com"},
                }
            },
        }
        return data

    @classmethod
    def build_valid_network_info(cls, **kwargs):
        """Return a valid data dict with network info."""
        data = {
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "folder": kwargs.get("folder", cls.folder),
            "network_info": {"criteria": {"network": {"is": {"wifi": {}}}}},
        }
        return data

    @classmethod
    def build_valid_patch_management(cls, **kwargs):
        """Return a valid data dict with patch management."""
        data = {
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "folder": kwargs.get("folder", cls.folder),
            "patch_management": {
                "criteria": {"missing_patches": {"severity": 3, "check": "has-any"}}
            },
        }
        return data

    @classmethod
    def build_valid_disk_encryption(cls, **kwargs):
        """Return a valid data dict with disk encryption."""
        data = {
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "folder": kwargs.get("folder", cls.folder),
            "disk_encryption": {
                "criteria": {
                    "encrypted_locations": [{"name": "C:", "encryption_state": {"is": "encrypted"}}]
                }
            },
        }
        return data

    @classmethod
    def build_valid_mobile_device(cls, **kwargs):
        """Return a valid data dict with mobile device."""
        data = {
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "folder": kwargs.get("folder", cls.folder),
            "mobile_device": {"criteria": {"jailbroken": False, "disk_encrypted": True}},
        }
        return data

    @classmethod
    def build_valid_certificate(cls, **kwargs):
        """Return a valid data dict with certificate."""
        data = {
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "folder": kwargs.get("folder", cls.folder),
            "certificate": {
                "criteria": {
                    "certificate_profile": "test-profile",
                    "certificate_attributes": [{"name": "attribute1", "value": "value1"}],
                }
            },
        }
        return data


class HIPObjectUpdateModelFactory:
    """Factory for creating data dicts for HIPObjectUpdateModel validation testing."""

    model = dict
    id = "12345678-1234-5678-1234-567812345678"
    name = factory.Sequence(lambda n: f"hip_object_{n}")
    description = fake.sentence()
    folder = "My Folder"

    @classmethod
    def build_without_id(cls, **kwargs):
        """Return a data dict without ID."""
        data = {
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "folder": kwargs.get("folder", cls.folder),
            "host_info": {
                "criteria": {
                    "domain": {"contains": "example.com"},
                }
            },
        }
        return data

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Return a data dict with multiple containers."""
        data = {
            "id": kwargs.get("id", cls.id),
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "folder": "My Folder",
            "snippet": "My Snippet",
            "host_info": {
                "criteria": {
                    "domain": {"contains": "example.com"},
                }
            },
        }
        return data

    @classmethod
    def build_valid(cls, **kwargs):
        """Return a valid data dict for update."""
        data = {
            "id": kwargs.get("id", cls.id),
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "folder": kwargs.get("folder", cls.folder),
            "host_info": {
                "criteria": {
                    "domain": {"contains": "example.com"},
                }
            },
        }
        return data


class HIPObjectResponseModelFactory:
    """Factory for creating data dicts for HIPObjectResponseModel validation testing."""

    model = dict
    id = "12345678-1234-5678-1234-567812345678"
    name = factory.Sequence(lambda n: f"hip_object_{n}")
    description = fake.sentence()
    folder = "My Folder"

    @classmethod
    def build_valid(cls, **kwargs):
        """Return a valid data dict for response."""
        data = {
            "id": kwargs.get("id", cls.id),
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "folder": kwargs.get("folder", cls.folder),
            "host_info": {
                "criteria": {
                    "domain": {"contains": "example.com"},
                }
            },
        }
        return data

    @classmethod
    def build_from_request(cls, request_data: dict, **kwargs):
        """Return a data dictionary based on request data.

        Args:
            request_data: Request data dictionary to base the response on
            **kwargs: Additional attributes to override

        Returns:
            Dictionary with response data

        """
        data = request_data.copy()

        # Add ID if not present
        if "id" not in data or "id" not in kwargs:
            data["id"] = cls.id

        # Override with any additional kwargs
        data.update(kwargs)

        return data
