"""Test factories for HIP Profiles.

This module provides factory classes for creating test instances of HIP Profile models
used in the Palo Alto Networks Strata Cloud Manager SDK.
"""

from typing import Any, Dict, Optional, Union
from uuid import uuid4

import factory  # type: ignore
from faker import Faker

from scm.models.objects.hip_profile import (
    HIPProfileBaseModel,
    HIPProfileCreateModel,
    HIPProfileResponseModel,
    HIPProfileUpdateModel,
)

fake = Faker()


# Base factory for all HIP profile models
class HIPProfileBaseFactory(factory.Factory):
    """Base factory for HIP Profile with common fields."""

    class Meta:
        """Meta class that defines the model for HIPProfileBaseFactory."""

        model = HIPProfileBaseModel
        abstract = True

    name = factory.Sequence(lambda n: f"hip_profile_{n}")
    match = "'hip-object.managed' or 'hip-object.host-info.domain'"
    description = fake.sentence()

    # Container fields default to None
    folder: Optional[str] = None
    snippet: Optional[str] = None
    device: Optional[str] = None


class HIPProfileCreateApiFactory(HIPProfileBaseFactory):
    """Factory for creating HIPProfileCreateModel instances."""

    class Meta:
        """Meta class that defines the model for HIPProfileCreateModelFactory."""

        model = HIPProfileCreateModel

    # Default to folder container
    folder = "My Folder"

    @classmethod
    def with_simple_match(cls, **kwargs: Any) -> HIPProfileCreateModel:
        """Create a HIPProfileCreateModel instance with a simple match criteria."""
        return cls(
            match="'hip-object.managed'",
            **kwargs,
        )

    @classmethod
    def with_complex_match(cls, **kwargs: Any) -> HIPProfileCreateModel:
        """Create a HIPProfileCreateModel instance with a complex match criteria."""
        return cls(
            match="('hip-object.host-info.domain' and 'hip-object.network-info.network') or 'hip-object.certificate'",
            **kwargs,
        )

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs: Any) -> HIPProfileCreateModel:
        """Create a HIPProfileCreateModel instance with snippet container."""
        return cls(
            folder=None,
            snippet=snippet,
            device=None,
            **kwargs,
        )

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs: Any) -> HIPProfileCreateModel:
        """Create a HIPProfileCreateModel instance with device container."""
        return cls(
            folder=None,
            snippet=None,
            device=device,
            **kwargs,
        )

    @classmethod
    def with_folder(cls, folder: str = "TestFolder", **kwargs: Any) -> HIPProfileCreateModel:
        """Create a HIPProfileCreateModel instance with folder container."""
        return cls(
            folder=folder,
            snippet=None,
            device=None,
            **kwargs,
        )


class HIPProfileUpdateApiFactory(HIPProfileBaseFactory):
    """Factory for creating HIPProfileUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for HIPProfileUpdateModelFactory."""

        model = HIPProfileUpdateModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    folder = "My Folder"

    @classmethod
    def with_simple_match(cls, **kwargs: Any) -> HIPProfileUpdateModel:
        """Create a HIPProfileUpdateModel instance with a simple match criteria."""
        return cls(
            match="'hip-object.managed'",
            **kwargs,
        )

    @classmethod
    def with_complex_match(cls, **kwargs: Any) -> HIPProfileUpdateModel:
        """Create a HIPProfileUpdateModel instance with a complex match criteria."""
        return cls(
            match="('hip-object.host-info.domain' and 'hip-object.network-info.network') or 'hip-object.certificate'",
            **kwargs,
        )

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs: Any) -> HIPProfileUpdateModel:
        """Create a HIPProfileUpdateModel instance with snippet container."""
        return cls(
            folder=None,
            snippet=snippet,
            device=None,
            **kwargs,
        )

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs: Any) -> HIPProfileUpdateModel:
        """Create a HIPProfileUpdateModel instance with device container."""
        return cls(
            folder=None,
            snippet=None,
            device=device,
            **kwargs,
        )

    @classmethod
    def with_folder(cls, folder: str = "UpdatedFolder", **kwargs: Any) -> HIPProfileUpdateModel:
        """Create a HIPProfileUpdateModel instance with folder container."""
        return cls(
            folder=folder,
            snippet=None,
            device=None,
            **kwargs,
        )

    @classmethod
    def without_id(cls, **kwargs: Any) -> HIPProfileUpdateModel:
        """Create a HIPProfileUpdateModel instance without ID."""
        return cls(
            id=None,
            **kwargs,
        )


class HIPProfileResponseFactory(HIPProfileBaseFactory):
    """Factory for creating HIPProfileResponseModel instances."""

    class Meta:
        """Meta class that defines the model for HIPProfileResponseModelFactory."""

        model = HIPProfileResponseModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    folder = "My Folder"

    @classmethod
    def build(cls, **kwargs: Any) -> HIPProfileResponseModel:
        """Create a basic HIPProfileResponseModel instance.

        Args:
            **kwargs: Additional keyword arguments to override default values

        Returns:
            HIPProfileResponseModel: A configured HIP profile response model

        """
        return cls(**kwargs)

    @classmethod
    def with_simple_match(cls, **kwargs: Any) -> HIPProfileResponseModel:
        """Create a HIPProfileResponseModel instance with a simple match criteria."""
        return cls(
            match="'hip-object.managed'",
            **kwargs,
        )

    @classmethod
    def with_complex_match(cls, **kwargs: Any) -> HIPProfileResponseModel:
        """Create a HIPProfileResponseModel instance with a complex match criteria."""
        return cls(
            match="('hip-object.host-info.domain' and 'hip-object.network-info.network') or 'hip-object.certificate'",
            **kwargs,
        )

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs: Any) -> HIPProfileResponseModel:
        """Create a HIPProfileResponseModel instance with snippet container."""
        return cls(
            folder=None,
            snippet=snippet,
            device=None,
            **kwargs,
        )

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs: Any) -> HIPProfileResponseModel:
        """Create a HIPProfileResponseModel instance with device container."""
        return cls(
            folder=None,
            snippet=None,
            device=device,
            **kwargs,
        )

    @classmethod
    def with_folder(cls, folder: str = "ResponseFolder", **kwargs: Any) -> HIPProfileResponseModel:
        """Create a HIPProfileResponseModel instance with folder container."""
        return cls(
            folder=folder,
            snippet=None,
            device=None,
            **kwargs,
        )

    @classmethod
    def from_request(
        cls, request_model: Union[HIPProfileCreateModel, Dict[str, Any]], **kwargs: Any
    ) -> HIPProfileResponseModel:
        """Create a response model based on a request model.

        This is useful for simulating the API's response to a create request.

        Args:
            request_model: The create request model or dictionary to base the response on
            **kwargs: Additional attributes to override in the response

        Returns:
            HIPProfileResponseModel instance

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
# HIP Profile model factories for Pydantic validation testing.
# ----------------------------------------------------------------------------


class HIPProfileCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for HIPProfileCreateModel validation testing."""

    name = "test_hip_profile"
    match = "'hip-object.managed' or 'hip-object.host-info.domain'"
    description = "Test HIP profile description"
    folder = "My Folder"

    @classmethod
    def build_with_no_containers(cls, **kwargs: Any) -> Dict[str, Any]:
        """Return a data dict without any containers."""
        data = {
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "match": kwargs.get("match", cls.match),
        }
        return data

    @classmethod
    def build_with_multiple_containers(cls, **kwargs: Any) -> Dict[str, Any]:
        """Return a data dict with multiple containers."""
        data = {
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "match": kwargs.get("match", cls.match),
            "folder": "My Folder",
            "snippet": "My Snippet",
        }
        return data

    @classmethod
    def build_with_simple_match(cls, **kwargs: Any) -> Dict[str, Any]:
        """Return a data dict with a simple match criteria."""
        data = {
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "match": "'hip-object.managed'",
            "folder": kwargs.get("folder", cls.folder),
        }
        return data

    @classmethod
    def build_with_complex_match(cls, **kwargs: Any) -> Dict[str, Any]:
        """Return a data dict with a complex match criteria."""
        data = {
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "match": "('hip-object.host-info.domain' and 'hip-object.network-info.network') or 'hip-object.certificate'",
            "folder": kwargs.get("folder", cls.folder),
        }
        return data

    @classmethod
    def build_with_invalid_match(cls, **kwargs: Any) -> Dict[str, Any]:
        """Return a data dict with invalid match criteria syntax."""
        data = {
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "match": "'hip-object.managed' and ('hip-object.host-info.domain'",
            "folder": kwargs.get("folder", cls.folder),
        }
        return data

    @classmethod
    def build_valid(cls, **kwargs: Any) -> Dict[str, Any]:
        """Return a valid data dict for validation."""
        data = {
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "match": kwargs.get("match", cls.match),
            "folder": kwargs.get("folder", cls.folder),
        }
        return data


class HIPProfileUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for HIPProfileUpdateModel validation testing."""

    id = str(uuid4())
    name = "update_hip_profile"
    match = "'hip-object.managed' or 'hip-object.host-info.domain'"
    description = "Updated HIP profile description"
    folder = "My Folder"

    @classmethod
    def build_without_id(cls, **kwargs: Any) -> Dict[str, Any]:
        """Return a data dict without ID."""
        data = {
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "match": kwargs.get("match", cls.match),
            "folder": kwargs.get("folder", cls.folder),
        }
        return data

    @classmethod
    def build_with_multiple_containers(cls, **kwargs: Any) -> Dict[str, Any]:
        """Return a data dict with multiple containers."""
        data = {
            "id": kwargs.get("id", cls.id),
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "match": kwargs.get("match", cls.match),
            "folder": "My Folder",
            "snippet": "My Snippet",
        }
        return data

    @classmethod
    def build_with_invalid_match(cls, **kwargs: Any) -> Dict[str, Any]:
        """Return a data dict with invalid match criteria syntax."""
        data = {
            "id": kwargs.get("id", cls.id),
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "match": "'hip-object.managed' and ('hip-object.host-info.domain'",
            "folder": kwargs.get("folder", cls.folder),
        }
        return data

    @classmethod
    def build_valid(cls, **kwargs: Any) -> Dict[str, Any]:
        """Return a valid data dict for update."""
        data = {
            "id": kwargs.get("id", cls.id),
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "match": kwargs.get("match", cls.match),
            "folder": kwargs.get("folder", cls.folder),
        }
        return data


class HIPProfileResponseModelFactory(factory.DictFactory):
    """Factory for creating data dicts for HIPProfileResponseModel validation testing."""

    id = str(uuid4())
    name = "response_hip_profile"
    match = "'hip-object.managed' or 'hip-object.host-info.domain'"
    description = "Response HIP profile description"
    folder = "My Folder"

    @classmethod
    def build_valid(cls, **kwargs: Any) -> Dict[str, Any]:
        """Return a valid data dict for response."""
        data = {
            "id": kwargs.get("id", cls.id),
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "match": kwargs.get("match", cls.match),
            "folder": kwargs.get("folder", cls.folder),
        }
        return data

    @classmethod
    def build_without_id(cls, **kwargs: Any) -> Dict[str, Any]:
        """Return a data dict without ID for validation testing."""
        data = {
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "match": kwargs.get("match", cls.match),
            "folder": kwargs.get("folder", cls.folder),
        }
        return data

    @classmethod
    def build_from_request(cls, request_data: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
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
