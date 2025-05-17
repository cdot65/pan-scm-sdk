# tests/factories/objects/tag.py

"""Factory definitions for tag objects."""

# Standard library imports
from typing import Any, Dict, Union
from uuid import uuid4

# External libraries
import factory
from faker import Faker

# Local SDK imports
from scm.models.objects.tag import (
    TagBaseModel,
    TagCreateModel,
    TagResponseModel,
    TagUpdateModel,
)

fake = Faker()


# Base factory for all tag models
class TagBaseFactory(factory.Factory):
    """Base factory for Tag objects with common fields."""

    class Meta:
        model = TagBaseModel
        abstract = True

    name = factory.Sequence(lambda n: f"tag_{n}")
    comments = fake.sentence()
    color = None
    folder = None
    snippet = None
    device = None


# ----------------------------------------------------------------------------
# Tag API factories for testing SCM API interactions.
# ----------------------------------------------------------------------------


class TagCreateApiFactory(TagBaseFactory):
    """Factory for creating TagCreateModel instances."""

    class Meta:
        model = TagCreateModel

    # Default to folder container
    folder = "Texas"

    @classmethod
    def with_folder(cls, folder="Texas", **kwargs):
        """Create a tag with a specific folder.

        Args:
            folder: The folder name
            **kwargs: Additional attributes to override in the model

        Returns:
            TagCreateModel: A model instance with folder container

        """
        return cls(
            folder=folder,
            snippet=None,
            device=None,
            **kwargs,
        )

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Create a tag with a snippet container.

        Args:
            snippet: The snippet name
            **kwargs: Additional attributes to override in the model

        Returns:
            TagCreateModel: A model instance with snippet container

        """
        return cls(
            folder=None,
            snippet=snippet,
            device=None,
            **kwargs,
        )

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """Create a tag with a device container.

        Args:
            device: The device name
            **kwargs: Additional attributes to override in the model

        Returns:
            TagCreateModel: A model instance with device container

        """
        return cls(
            folder=None,
            snippet=None,
            device=device,
            **kwargs,
        )

    @classmethod
    def with_color(cls, color="Red", **kwargs):
        """Create a tag with a specific color.

        Args:
            color: The color name (must be one of the valid Colors enum values)
            **kwargs: Additional attributes to override in the model

        Returns:
            TagCreateModel: A model instance with the specified color

        """
        return cls(color=color, **kwargs)

    @classmethod
    def build_with_invalid_color(cls, **kwargs):
        """Create a tag with an invalid color (should fail validation).

        Args:
            **kwargs: Additional attributes to override in the model

        Returns:
            TagCreateModel: A model instance with an invalid color

        """
        return cls(color="InvalidColor", **kwargs)

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Create a tag with multiple containers (should fail validation).

        Args:
            **kwargs: Additional attributes to override in the model

        Returns:
            TagCreateModel: A model instance with multiple containers

        """
        return cls(
            folder="Texas",
            snippet="TestSnippet",
            device=None,
            **kwargs,
        )

    @classmethod
    def build_with_no_container(cls, **kwargs):
        """Create a tag without any container (should fail validation).

        Args:
            **kwargs: Additional attributes to override in the model

        Returns:
            TagCreateModel: A model instance without any container

        """
        return cls(
            folder=None,
            snippet=None,
            device=None,
            **kwargs,
        )


class TagUpdateApiFactory(TagBaseFactory):
    """Factory for creating TagUpdateModel instances."""

    class Meta:
        model = TagUpdateModel

    id = factory.LazyFunction(lambda: str(uuid4()))

    @classmethod
    def with_color(cls, color="Blue", **kwargs):
        """Update a tag with a specific color.

        Args:
            color: The color name (must be one of the valid Colors enum values)
            **kwargs: Additional attributes to override in the model

        Returns:
            TagUpdateModel: A model instance with the specified color

        """
        return cls(color=color, **kwargs)

    @classmethod
    def build_with_invalid_color(cls, **kwargs):
        """Create a tag update with an invalid color (should fail validation).

        Args:
            **kwargs: Additional attributes to override in the model

        Returns:
            TagUpdateModel: A model instance with an invalid color

        """
        return cls(color="InvalidColor", **kwargs)


class TagResponseFactory(TagBaseFactory):
    """Factory for creating TagResponseModel instances."""

    class Meta:
        model = TagResponseModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    folder = "Texas"  # Default to folder container

    @classmethod
    def with_folder(cls, folder="Texas", **kwargs):
        """Create a response model with a specific folder.

        Args:
            folder: The folder name
            **kwargs: Additional attributes to override in the model

        Returns:
            TagResponseModel: A model instance with folder container

        """
        return cls(
            folder=folder,
            snippet=None,
            device=None,
            **kwargs,
        )

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Create a response model with a snippet container.

        Args:
            snippet: The snippet name
            **kwargs: Additional attributes to override in the model

        Returns:
            TagResponseModel: A model instance with snippet container

        """
        return cls(
            folder=None,
            snippet=snippet,
            device=None,
            **kwargs,
        )

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """Create a response model with a device container.

        Args:
            device: The device name
            **kwargs: Additional attributes to override in the model

        Returns:
            TagResponseModel: A model instance with device container

        """
        return cls(
            folder=None,
            snippet=None,
            device=device,
            **kwargs,
        )

    @classmethod
    def with_color(cls, color="Red", **kwargs):
        """Create a response model with a specific color.

        Args:
            color: The color name (must be one of the valid Colors enum values)
            **kwargs: Additional attributes to override in the model

        Returns:
            TagResponseModel: A model instance with the specified color

        """
        return cls(color=color, **kwargs)

    @classmethod
    def from_request(
        cls, request_model: Union[TagCreateModel, TagUpdateModel, Dict[str, Any]], **kwargs
    ) -> TagResponseModel:
        """Create a response model based on a request model.

        This is useful for simulating the API's response to a create or update request.

        Args:
            request_model: The create/update request model or dictionary to base the response on
            **kwargs: Additional attributes to override in the response

        Returns:
            TagResponseModel instance

        """
        if isinstance(request_model, (TagCreateModel, TagUpdateModel)):
            data = request_model.model_dump()
        else:
            data = request_model.copy()

        # If the model already has an ID, preserve it
        if "id" not in data or not data["id"]:
            data["id"] = str(uuid4())

        data.update(kwargs)
        return TagResponseModel(**data)


# ----------------------------------------------------------------------------
# Tag model factories for Pydantic validation testing.
# ----------------------------------------------------------------------------


class TagCreateModelFactory(factory.DictFactory):
    """Factory for creating dictionary data for TagCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"tag_{n}")
    comments = fake.sentence()
    color = "Red"  # Default color; can be overridden
    folder = "Texas"
    snippet = None
    device = None

    @classmethod
    def build_valid(cls, **kwargs) -> Dict[str, Any]:
        """Return a valid data dict with all expected attributes.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Valid data for TagCreateModel

        """
        data = {
            "name": "TestTag",
            "comments": "This is a test tag",
            "color": "Blue",
            "folder": "Texas",
        }
        data.update(kwargs)
        return data

    @classmethod
    def build_with_invalid_color(cls, **kwargs) -> Dict[str, Any]:
        """Return a data dict with an invalid color.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Data for TagCreateModel with invalid color

        """
        data = {
            "name": "InvalidColorTag",
            "comments": "This tag has an invalid color",
            "color": "InvalidColor",
            "folder": "Texas",
        }
        data.update(kwargs)
        return data

    @classmethod
    def build_with_multiple_containers(cls, **kwargs) -> Dict[str, Any]:
        """Return a data dict with multiple containers (should fail validation).

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Data for TagCreateModel with multiple containers

        """
        data = {
            "name": "TestTag",
            "folder": "Texas",
            "snippet": "MySnippet",
            "color": "Blue",
        }
        data.update(kwargs)
        return data

    @classmethod
    def build_with_no_container(cls, **kwargs) -> Dict[str, Any]:
        """Return a data dict without any containers (should fail validation).

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Data for TagCreateModel without containers

        """
        data = {
            "name": "TestTag",
            "color": "Blue",
            "folder": None,
            "snippet": None,
            "device": None,
        }
        data.update(kwargs)
        return data


class TagUpdateModelFactory(factory.DictFactory):
    """Factory for creating dictionary data for TagUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"tag_{n}")
    comments = fake.sentence()
    color = "Green"

    @classmethod
    def build_valid(cls, **kwargs) -> Dict[str, Any]:
        """Return a valid data dict for updating a tag.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Valid data for TagUpdateModel

        """
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "UpdatedTag",
            "comments": "This tag has been updated",
            "color": "Green",
        }
        data.update(kwargs)
        return data

    @classmethod
    def build_with_invalid_color(cls, **kwargs) -> Dict[str, Any]:
        """Return a data dict with an invalid color.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Data for TagUpdateModel with invalid color

        """
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "InvalidColorTag",
            "comments": "This tag has an invalid color",
            "color": "InvalidColor",
        }
        data.update(kwargs)
        return data
