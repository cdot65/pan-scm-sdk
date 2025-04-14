# tests/factories/objects/service_group.py

# Standard library imports
from typing import Any, Dict, Union
from uuid import uuid4

# External libraries
import factory
from faker import Faker

# Local SDK imports
from scm.models.objects.service_group import (
    ServiceGroupBaseModel,
    ServiceGroupCreateModel,
    ServiceGroupResponseModel,
    ServiceGroupUpdateModel,
)

fake = Faker()


# Base factory for all service group models
class ServiceGroupBaseFactory(factory.Factory):
    """Base factory for Service Group with common fields."""

    class Meta:
        model = ServiceGroupBaseModel
        abstract = True

    name = factory.Sequence(lambda n: f"service_group_{n}")
    members = None
    tag = ["test-tag", "environment-prod"]
    folder = None
    snippet = None
    device = None


# ----------------------------------------------------------------------------
# Service Group API factories for testing SCM API interactions.
# ----------------------------------------------------------------------------


class ServiceGroupCreateApiFactory(ServiceGroupBaseFactory):
    """Factory for creating ServiceGroupCreateModel instances with members."""

    class Meta:
        model = ServiceGroupCreateModel

    # Default to folder container
    folder = "Texas"

    @classmethod
    def with_members(cls, members=None, **kwargs):
        """
        Create a ServiceGroupCreateModel instance with members.

        Args:
            members: List of member names (defaults to ["custom-service1", "custom-service2"])
            **kwargs: Additional attributes to override in the model

        Returns:
            ServiceGroupCreateModel: A model instance with members set
        """
        if members is None:
            members = ["custom-service1", "custom-service2"]
        return cls(members=members, **kwargs)

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """
        Create an instance with snippet container.

        Args:
            snippet: The snippet value to use
            **kwargs: Additional attributes to override in the model

        Returns:
            ServiceGroupCreateModel: A model instance with snippet container
        """
        return cls(
            snippet=snippet,
            folder=None,
            device=None,
            **kwargs,
        )

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """
        Create an instance with device container.

        Args:
            device: The device value to use
            **kwargs: Additional attributes to override in the model

        Returns:
            ServiceGroupCreateModel: A model instance with device container
        """
        return cls(
            device=device,
            folder=None,
            snippet=None,
            **kwargs,
        )

    @classmethod
    def build_without_members(cls, **kwargs):
        """
        Return an instance without the required members field.

        Args:
            **kwargs: Additional attributes to override in the model

        Returns:
            ServiceGroupCreateModel: A model instance without members
        """
        return cls(members=None, **kwargs)

    @classmethod
    def build_with_duplicate_members(cls, **kwargs):
        """
        Return an instance with duplicate members (should fail validation).

        Args:
            **kwargs: Additional attributes to override in the model

        Returns:
            ServiceGroupCreateModel: A model instance with duplicate members
        """
        return cls(members=["service1", "service1"], **kwargs)

    @classmethod
    def build_with_no_containers(cls, **kwargs):
        """
        Return an instance without any containers.

        Args:
            **kwargs: Additional attributes to override in the model

        Returns:
            ServiceGroupCreateModel: A model instance without containers
        """
        return cls(folder=None, snippet=None, device=None, **kwargs)

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """
        Return an instance with multiple containers (should fail validation).

        Args:
            **kwargs: Additional attributes to override in the model

        Returns:
            ServiceGroupCreateModel: A model instance with multiple containers
        """
        return cls(folder="Test Folder", snippet="Test Snippet", device=None, **kwargs)


class ServiceGroupUpdateApiFactory(ServiceGroupBaseFactory):
    """Factory for creating ServiceGroupUpdateModel instances."""

    class Meta:
        model = ServiceGroupUpdateModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    folder = "Texas"  # Default to folder container

    @classmethod
    def with_members(cls, members=None, **kwargs):
        """
        Create a ServiceGroupUpdateModel instance with members.

        Args:
            members: List of member names (defaults to ["custom-service1", "custom-service2"])
            **kwargs: Additional attributes to override in the model

        Returns:
            ServiceGroupUpdateModel: A model instance with members set
        """
        if members is None:
            members = ["custom-service1", "custom-service2"]
        return cls(members=members, **kwargs)

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """
        Create an instance with snippet container.

        Args:
            snippet: The snippet value to use
            **kwargs: Additional attributes to override in the model

        Returns:
            ServiceGroupUpdateModel: A model instance with snippet container
        """
        return cls(
            snippet=snippet,
            folder=None,
            device=None,
            **kwargs,
        )

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """
        Create an instance with device container.

        Args:
            device: The device value to use
            **kwargs: Additional attributes to override in the model

        Returns:
            ServiceGroupUpdateModel: A model instance with device container
        """
        return cls(
            device=device,
            folder=None,
            snippet=None,
            **kwargs,
        )

    @classmethod
    def build_without_members(cls, **kwargs):
        """
        Return an instance without the required members field.

        Args:
            **kwargs: Additional attributes to override in the model

        Returns:
            ServiceGroupUpdateModel: A model instance without members
        """
        return cls(members=None, **kwargs)

    @classmethod
    def build_with_duplicate_members(cls, **kwargs):
        """
        Return an instance with duplicate members (should fail validation).

        Args:
            **kwargs: Additional attributes to override in the model

        Returns:
            ServiceGroupUpdateModel: A model instance with duplicate members
        """
        return cls(members=["service1", "service1"], **kwargs)

    @classmethod
    def build_with_no_containers(cls, **kwargs):
        """
        Return an instance without any containers.

        Args:
            **kwargs: Additional attributes to override in the model

        Returns:
            ServiceGroupUpdateModel: A model instance without containers
        """
        return cls(folder=None, snippet=None, device=None, **kwargs)

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """
        Return an instance with multiple containers (should fail validation).

        Args:
            **kwargs: Additional attributes to override in the model

        Returns:
            ServiceGroupUpdateModel: A model instance with multiple containers
        """
        return cls(folder="Test Folder", snippet="Test Snippet", device=None, **kwargs)


class ServiceGroupResponseFactory(ServiceGroupBaseFactory):
    """Factory for creating ServiceGroupResponseModel instances."""

    class Meta:
        model = ServiceGroupResponseModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    folder = "Texas"  # Default to folder container

    @classmethod
    def with_members(cls, members=None, **kwargs):
        """
        Create a ServiceGroupResponseModel instance with members.

        Args:
            members: List of member names (defaults to ["custom-service1", "custom-service2"])
            **kwargs: Additional attributes to override in the model

        Returns:
            ServiceGroupResponseModel: A model instance with members set
        """
        if members is None:
            members = ["custom-service1", "custom-service2"]
        return cls(members=members, **kwargs)

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """
        Create an instance with snippet container.

        Args:
            snippet: The snippet value to use
            **kwargs: Additional attributes to override in the model

        Returns:
            ServiceGroupResponseModel: A model instance with snippet container
        """
        return cls(
            snippet=snippet,
            folder=None,
            device=None,
            **kwargs,
        )

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """
        Create an instance with device container.

        Args:
            device: The device value to use
            **kwargs: Additional attributes to override in the model

        Returns:
            ServiceGroupResponseModel: A model instance with device container
        """
        return cls(
            device=device,
            folder=None,
            snippet=None,
            **kwargs,
        )

    @classmethod
    def build_without_members(cls, **kwargs):
        """
        Return an instance without the required members field.

        Args:
            **kwargs: Additional attributes to override in the model

        Returns:
            ServiceGroupResponseModel: A model instance without members
        """
        return cls(members=None, **kwargs)

    @classmethod
    def build_with_duplicate_members(cls, **kwargs):
        """
        Return an instance with duplicate members.

        Args:
            **kwargs: Additional attributes to override in the model

        Returns:
            ServiceGroupResponseModel: A model instance with duplicate members
        """
        return cls(members=["service1", "service1"], **kwargs)

    @classmethod
    def build_with_no_containers(cls, **kwargs):
        """
        Return an instance without any containers.

        Args:
            **kwargs: Additional attributes to override in the model

        Returns:
            ServiceGroupResponseModel: A model instance without containers
        """
        return cls(folder=None, snippet=None, device=None, **kwargs)

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """
        Return an instance with multiple containers.

        Args:
            **kwargs: Additional attributes to override in the model

        Returns:
            ServiceGroupResponseModel: A model instance with multiple containers
        """
        return cls(folder="Test Folder", snippet="Test Snippet", device=None, **kwargs)

    @classmethod
    def from_request(
        cls,
        request_model: Union[ServiceGroupCreateModel, ServiceGroupUpdateModel, Dict[str, Any]],
        **kwargs,
    ) -> ServiceGroupResponseModel:
        """
        Create a response model based on a request model.

        This is useful for simulating the API's response to a create request.

        Args:
            request_model: The create/update request model or dictionary to base the response on
            **kwargs: Additional attributes to override in the response

        Returns:
            ServiceGroupResponseModel instance
        """
        if isinstance(request_model, (ServiceGroupCreateModel, ServiceGroupUpdateModel)):
            data = request_model.model_dump()
        else:
            data = request_model.copy()

        # If the model already has an ID, preserve it
        if "id" not in data or not data["id"]:
            data["id"] = str(uuid4())

        data.update(kwargs)
        return ServiceGroupResponseModel(**data)


# ----------------------------------------------------------------------------
# Service Group model factories for Pydantic validation testing.
# ----------------------------------------------------------------------------


class ServiceGroupCreateModelFactory(factory.DictFactory):
    """Factory for creating dictionary data for ServiceGroupCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"service_group_{n}")
    members = None
    tag = ["test-tag", "environment-prod"]
    folder = "Texas"
    snippet = None
    device = None

    @classmethod
    def build_without_members(cls, **kwargs) -> Dict[str, Any]:
        """
        Return a data dict without the required members field.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Data for ServiceGroupCreateModel validation
        """
        data = {"members": None}
        data.update(kwargs)
        return cls(**data)

    @classmethod
    def build_with_no_containers(cls, **kwargs) -> Dict[str, Any]:
        """
        Return a data dict without any containers.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Data for ServiceGroupCreateModel validation
        """
        data = {"folder": None, "snippet": None, "device": None}
        data.update(kwargs)
        return cls(**data)

    @classmethod
    def build_with_multiple_containers(cls, **kwargs) -> Dict[str, Any]:
        """
        Return a data dict with multiple containers.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Data for ServiceGroupCreateModel validation
        """
        data = {"folder": "Test Folder", "snippet": "Test Snippet", "device": None}
        data.update(kwargs)
        return cls(**data)

    @classmethod
    def build_valid_members(cls, **kwargs) -> Dict[str, Any]:
        """
        Return a valid data dict for a service group.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Valid data for ServiceGroupCreateModel
        """
        data = {"members": ["custom-service1", "custom-service2"]}
        data.update(kwargs)
        return cls(**data)


class ServiceGroupUpdateModelFactory(factory.DictFactory):
    """Factory for creating dictionary data for ServiceGroupUpdateModel validation testing."""

    id = factory.LazyFunction(lambda: str(uuid4()))
    name = factory.Sequence(lambda n: f"service_group_{n}")
    members = None
    tag = ["test-tag", "environment-prod"]
    folder = "Texas"
    snippet = None
    device = None

    @classmethod
    def build_without_members(cls, **kwargs) -> Dict[str, Any]:
        """
        Return a data dict without the required members field.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Data for ServiceGroupUpdateModel validation
        """
        data = {"members": None}
        data.update(kwargs)
        return cls(**data)

    @classmethod
    def build_with_no_containers(cls, **kwargs) -> Dict[str, Any]:
        """
        Return a data dict without any containers.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Data for ServiceGroupUpdateModel validation
        """
        data = {"folder": None, "snippet": None, "device": None}
        data.update(kwargs)
        return cls(**data)

    @classmethod
    def build_with_multiple_containers(cls, **kwargs) -> Dict[str, Any]:
        """
        Return a data dict with multiple containers.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Data for ServiceGroupUpdateModel validation
        """
        data = {"folder": "Test Folder", "snippet": "Test Snippet", "device": None}
        data.update(kwargs)
        return cls(**data)

    @classmethod
    def build_valid_members(cls, **kwargs) -> Dict[str, Any]:
        """
        Return a valid data dict for a service group.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Valid data for ServiceGroupUpdateModel
        """
        data = {"members": ["custom-service1", "custom-service2"]}
        data.update(kwargs)
        return cls(**data)
