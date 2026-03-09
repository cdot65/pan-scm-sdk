# tests/factories/objects/auto_tag_actions.py

"""Factory definitions for auto tag action objects."""

# Standard library imports
from typing import Any, Dict, Union
from uuid import uuid4

# External libraries
import factory
from faker import Faker

# Local SDK imports
from scm.models.objects.auto_tag_actions import (
    AutoTagActionBaseModel,
    AutoTagActionCreateModel,
    AutoTagActionResponseModel,
    AutoTagActionUpdateModel,
)

fake = Faker()


class AutoTagActionBaseFactory(factory.Factory):
    """Base factory for AutoTagAction objects with common fields."""

    class Meta:
        """Meta class that defines the model for AutoTagActionBaseFactory."""

        model = AutoTagActionBaseModel
        abstract = True

    name = factory.Sequence(lambda n: f"auto_tag_action_{n}")
    description = fake.sentence()
    folder = None
    snippet = None
    device = None


class AutoTagActionCreateApiFactory(AutoTagActionBaseFactory):
    """Factory for creating AutoTagActionCreateModel instances."""

    class Meta:
        """Meta class that defines the model for AutoTagActionCreateApiFactory."""

        model = AutoTagActionCreateModel

    folder = "Texas"

    @classmethod
    def with_folder(cls, folder="Texas", **kwargs):
        """Create an auto tag action with a specific folder."""
        return cls(folder=folder, snippet=None, device=None, **kwargs)

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Create an auto tag action with a snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """Create an auto tag action with a device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Create an auto tag action with multiple containers (should fail)."""
        return cls(folder="Texas", snippet="TestSnippet", device=None, **kwargs)

    @classmethod
    def build_with_no_container(cls, **kwargs):
        """Create an auto tag action without any container (should fail)."""
        return cls(folder=None, snippet=None, device=None, **kwargs)


class AutoTagActionUpdateApiFactory(AutoTagActionBaseFactory):
    """Factory for creating AutoTagActionUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for AutoTagActionUpdateApiFactory."""

        model = AutoTagActionUpdateModel

    id = factory.LazyFunction(lambda: str(uuid4()))


class AutoTagActionResponseFactory(AutoTagActionBaseFactory):
    """Factory for creating AutoTagActionResponseModel instances."""

    class Meta:
        """Meta class that defines the model for AutoTagActionResponseFactory."""

        model = AutoTagActionResponseModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    folder = "Texas"

    @classmethod
    def with_folder(cls, folder="Texas", **kwargs):
        """Create a response model with a specific folder."""
        return cls(folder=folder, snippet=None, device=None, **kwargs)

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Create a response model with a snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """Create a response model with a device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def from_request(
        cls,
        request_model: Union[AutoTagActionCreateModel, AutoTagActionUpdateModel, Dict[str, Any]],
        **kwargs,
    ) -> AutoTagActionResponseModel:
        """Create a response model based on a request model."""
        if isinstance(request_model, (AutoTagActionCreateModel, AutoTagActionUpdateModel)):
            data = request_model.model_dump()
        else:
            data = request_model.copy()

        if "id" not in data or not data["id"]:
            data["id"] = str(uuid4())

        data.update(kwargs)
        return AutoTagActionResponseModel(**data)


class AutoTagActionCreateModelFactory(factory.DictFactory):
    """Factory for creating dictionary data for AutoTagActionCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"auto_tag_action_{n}")
    description = fake.sentence()
    folder = "Texas"
    snippet = None
    device = None

    @classmethod
    def build_valid(cls, **kwargs) -> Dict[str, Any]:
        """Return a valid data dict with all expected attributes."""
        data = {
            "name": "TestAutoTagAction",
            "description": "Test auto tag action",
            "folder": "Texas",
        }
        data.update(kwargs)
        return data

    @classmethod
    def build_with_multiple_containers(cls, **kwargs) -> Dict[str, Any]:
        """Return a data dict with multiple containers (should fail validation)."""
        data = {
            "name": "TestAutoTagAction",
            "folder": "Texas",
            "snippet": "MySnippet",
        }
        data.update(kwargs)
        return data

    @classmethod
    def build_with_no_container(cls, **kwargs) -> Dict[str, Any]:
        """Return a data dict without any containers (should fail validation)."""
        data = {
            "name": "TestAutoTagAction",
            "folder": None,
            "snippet": None,
            "device": None,
        }
        data.update(kwargs)
        return data


class AutoTagActionUpdateModelFactory(factory.DictFactory):
    """Factory for creating dictionary data for AutoTagActionUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"auto_tag_action_{n}")
    description = fake.sentence()

    @classmethod
    def build_valid(cls, **kwargs) -> Dict[str, Any]:
        """Return a valid data dict for updating an auto tag action."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "UpdatedAutoTagAction",
            "description": "Updated auto tag action",
        }
        data.update(kwargs)
        return data
