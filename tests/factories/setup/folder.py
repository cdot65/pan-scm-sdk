# tests/factories/setup/folder.py

# Standard library imports
from typing import Any, Dict, Union
from uuid import uuid4

# External libraries
import factory
from faker import Faker

# Local SDK imports
from scm.models.setup.folder import (
    FolderBaseModel,
    FolderCreateModel,
    FolderResponseModel,
    FolderUpdateModel,
)

fake = Faker()


# Base factory for all folder models
class FolderBaseFactory(factory.Factory):
    """Base factory for Folder objects with common fields."""

    class Meta:
        model = FolderBaseModel
        abstract = True

    name = factory.Sequence(lambda n: f"folder_{n}")
    parent = "root"  # Default parent is root
    description = factory.LazyFunction(lambda: fake.sentence())
    labels = factory.LazyFunction(lambda: [fake.word() for _ in range(2)])
    snippets = None


# ----------------------------------------------------------------------------
# Folder API factories for testing SCM API interactions.
# ----------------------------------------------------------------------------


class FolderCreateApiFactory(FolderBaseFactory):
    """Factory for creating FolderCreateModel instances."""

    class Meta:
        model = FolderCreateModel

    @classmethod
    def with_parent(cls, parent="root", **kwargs):
        """
        Create a folder with a specific parent.

        Args:
            parent: The ID of the parent folder
            **kwargs: Additional attributes to override in the model

        Returns:
            FolderCreateModel: A model instance with the specified parent
        """
        return cls(
            parent=parent,
            **kwargs,
        )

    @classmethod
    def with_labels(cls, labels=None, **kwargs):
        """
        Create a folder with specific labels.

        Args:
            labels: List of label strings
            **kwargs: Additional attributes to override in the model

        Returns:
            FolderCreateModel: A model instance with the specified labels
        """
        if labels is None:
            labels = [fake.word(), fake.word()]

        return cls(
            labels=labels,
            **kwargs,
        )

    @classmethod
    def with_snippets(cls, snippets=None, **kwargs):
        """
        Create a folder with specific snippets.

        Args:
            snippets: List of snippet IDs
            **kwargs: Additional attributes to override in the model

        Returns:
            FolderCreateModel: A model instance with the specified snippets
        """
        if snippets is None:
            snippets = [str(uuid4()), str(uuid4())]

        return cls(
            snippets=snippets,
            **kwargs,
        )


class FolderUpdateApiFactory(FolderBaseFactory):
    """Factory for creating FolderUpdateModel instances."""

    class Meta:
        model = FolderUpdateModel

    id = factory.LazyFunction(lambda: str(uuid4()))

    @classmethod
    def with_new_parent(cls, parent="new_parent_id", **kwargs):
        """
        Create a folder update with a new parent (for moving folders).

        Args:
            parent: The ID of the new parent folder
            **kwargs: Additional attributes to override in the model

        Returns:
            FolderUpdateModel: A model instance with the specified parent
        """
        return cls(
            parent=parent,
            **kwargs,
        )

    @classmethod
    def with_updated_labels(cls, labels=None, **kwargs):
        """
        Create a folder update with updated labels.

        Args:
            labels: List of new label strings
            **kwargs: Additional attributes to override in the model

        Returns:
            FolderUpdateModel: A model instance with updated labels
        """
        if labels is None:
            labels = [f"updated_{fake.word()}" for _ in range(2)]

        return cls(
            labels=labels,
            **kwargs,
        )


class FolderResponseFactory(FolderBaseFactory):
    """Factory for creating FolderResponseModel instances."""

    class Meta:
        model = FolderResponseModel

    id = factory.LazyFunction(lambda: str(uuid4()))

    @classmethod
    def with_parent(cls, parent="parent_id", **kwargs):
        """
        Create a response model with a specific parent.

        Args:
            parent: The parent folder ID
            **kwargs: Additional attributes to override in the model

        Returns:
            FolderResponseModel: A model instance with the specified parent
        """
        return cls(
            parent=parent,
            **kwargs,
        )

    @classmethod
    def root_folder(cls, **kwargs):
        """
        Create a response model for a root folder (empty parent).

        Args:
            **kwargs: Additional attributes to override in the model

        Returns:
            FolderResponseModel: A root folder model instance
        """
        return cls(
            parent="",
            **kwargs,
        )

    @classmethod
    def from_request(
        cls, request_model: Union[FolderCreateModel, FolderUpdateModel, Dict[str, Any]], **kwargs
    ):
        """
        Create a response model based on a request model.

        This is useful for simulating the API's response to a create or update request.

        Args:
            request_model: The create/update request model or dictionary to base the response on
            **kwargs: Additional attributes to override in the response

        Returns:
            FolderResponseModel instance
        """
        # Convert to dict if it's a Pydantic model
        if hasattr(request_model, "model_dump"):
            data = request_model.model_dump()
        else:
            data = request_model.copy()

        # Generate a UUID if not provided
        if "id" not in data and "id" not in kwargs:
            data["id"] = str(uuid4())

        # Merge the request data with any override kwargs
        merged_data = {**data, **kwargs}

        return cls(**merged_data)


# ----------------------------------------------------------------------------
# Folder model factories for Pydantic validation testing.
# ----------------------------------------------------------------------------


class FolderCreateModelFactory(factory.DictFactory):
    """Factory for creating dictionary data for FolderCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"folder_{n}")
    parent = "parent_id"
    description = factory.LazyFunction(lambda: fake.sentence())
    labels = factory.LazyFunction(lambda: [fake.word() for _ in range(2)])
    snippets = factory.LazyFunction(lambda: [str(uuid4()), str(uuid4())])

    @classmethod
    def build_valid(cls, **kwargs):
        """
        Return a valid data dict with all expected attributes.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Valid data for FolderCreateModel
        """
        data = {
            "name": f"folder_{fake.word()}",
            "parent": "parent_id",
            "description": fake.sentence(),
            "labels": [fake.word() for _ in range(2)],
            "snippets": [str(uuid4()) for _ in range(2)],
        }
        return {**data, **kwargs}

    @classmethod
    def build_without_parent(cls, **kwargs):
        """
        Return data without a parent field (should fail validation).

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Data for FolderCreateModel without a parent
        """
        data = cls.build_valid(**kwargs)
        data.pop("parent", None)
        return data


class FolderUpdateModelFactory(factory.DictFactory):
    """Factory for creating dictionary data for FolderUpdateModel validation testing."""

    id = factory.LazyFunction(lambda: str(uuid4()))
    name = factory.Sequence(lambda n: f"updated_folder_{n}")
    parent = "parent_id"
    description = factory.LazyFunction(lambda: fake.sentence())
    labels = factory.LazyFunction(lambda: [fake.word() for _ in range(2)])
    snippets = factory.LazyFunction(lambda: [str(uuid4()), str(uuid4())])

    @classmethod
    def build_valid(cls, **kwargs):
        """
        Return a valid data dict for updating a folder.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Valid data for FolderUpdateModel
        """
        data = {
            "id": str(uuid4()),
            "name": f"updated_folder_{fake.word()}",
            "parent": "parent_id",
            "description": fake.sentence(),
            "labels": [fake.word() for _ in range(2)],
            "snippets": [str(uuid4()) for _ in range(2)],
        }
        return {**data, **kwargs}

    @classmethod
    def build_without_id(cls, **kwargs):
        """
        Return data without an ID field (should fail validation).

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Data for FolderUpdateModel without an ID
        """
        data = cls.build_valid(**kwargs)
        data.pop("id", None)
        return data


class FolderResponseModelFactory(factory.DictFactory):
    """Factory for creating dictionary data for FolderResponseModel validation testing."""

    id = factory.LazyFunction(lambda: str(uuid4()))
    name = factory.Sequence(lambda n: f"folder_{n}")
    parent = "parent_id"
    description = factory.LazyFunction(lambda: fake.sentence())
    labels = factory.LazyFunction(lambda: [fake.word() for _ in range(2)])
    snippets = factory.LazyFunction(lambda: [str(uuid4()), str(uuid4())])

    @classmethod
    def build_valid(cls, **kwargs):
        """
        Return a valid data dict for a folder response.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Valid data for FolderResponseModel
        """
        data = {
            "id": str(uuid4()),
            "name": f"folder_{fake.word()}",
            "parent": "parent_id",
            "description": fake.sentence(),
            "labels": [fake.word() for _ in range(2)],
            "snippets": [str(uuid4()) for _ in range(2)],
        }
        return {**data, **kwargs}

    @classmethod
    def build_root_folder(cls, **kwargs):
        """
        Return a valid data dict for a root folder (empty parent).

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Valid data for a root FolderResponseModel
        """
        data = cls.build_valid(**kwargs)
        data["parent"] = ""
        return data
