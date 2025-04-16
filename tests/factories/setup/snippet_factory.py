"""
Factory for generating test Snippet objects.

This module provides factory classes for creating test data 
for Snippet objects in the Strata Cloud Manager SDK.
"""

from typing import Any, Dict
import uuid

import factory
from faker import Faker

fake = Faker()


class FolderReferenceFactory(factory.DictFactory):
    """Factory for generating folder references for snippets."""

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"folder-{n}")


class SnippetBaseFactory(factory.DictFactory):
    """Base factory for Snippet objects with common fields."""

    class Meta:
        abstract = True

    name = factory.Sequence(lambda n: f"test-snippet-{n}")
    description = factory.LazyAttribute(lambda o: f"Description for {o.name}")
    enable_prefix = factory.LazyFunction(lambda: False)
    labels = factory.LazyFunction(lambda: [fake.word() for _ in range(2)])


class SnippetCreateApiFactory(SnippetBaseFactory):
    """Factory for creating SnippetCreateModel instances."""

    @classmethod
    def with_labels(cls, labels=None, **kwargs):
        """
        Create a snippet with specific labels.

        Args:
            labels: The labels to apply to the snippet
            **kwargs: Additional attributes to override in the model

        Returns:
            Dict: A model instance with the specified labels
        """
        if labels is None:
            labels = [fake.word() for _ in range(2)]

        return cls(labels=labels, **kwargs)

    @classmethod
    def minimal(cls, **kwargs):
        """
        Create a minimal snippet with only required fields.

        Args:
            **kwargs: Additional attributes to override in the model

        Returns:
            Dict: A minimal model instance
        """
        return cls(
            description=None,
            labels=None,
            enable_prefix=None,
            **kwargs,
        )

    @classmethod
    def build_for_request(cls, **kwargs):
        """
        Build a dictionary suitable for API request payloads.

        Args:
            **kwargs: Attribute overrides

        Returns:
            Dict[str, Any]: Dictionary with all snippet fields
        """
        return cls(**kwargs)


class SnippetUpdateApiFactory(SnippetBaseFactory):
    """Factory for creating SnippetUpdateModel instances."""

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))

    @classmethod
    def with_updated_labels(cls, labels=None, **kwargs):
        """
        Create a snippet update with updated labels.

        Args:
            labels: List of new label strings
            **kwargs: Additional attributes to override in the model

        Returns:
            Dict: A model instance with updated labels
        """
        if labels is None:
            labels = [fake.word() for _ in range(3)]  # Different from default

        return cls(labels=labels, **kwargs)

    @classmethod
    def with_description_change(cls, description=None, **kwargs):
        """
        Create a snippet update with a new description.

        Args:
            description: New description text
            **kwargs: Additional attributes to override in the model

        Returns:
            Dict: A model instance with updated description
        """
        if description is None:
            description = fake.sentence()

        return cls(description=description, **kwargs)

    @classmethod
    def build_for_request(cls, **kwargs):
        """
        Build a dictionary suitable for API request payloads.

        Args:
            **kwargs: Attribute overrides

        Returns:
            Dict[str, Any]: Dictionary with all snippet fields excluding id
        """
        instance = cls(**kwargs)
        return {k: v for k, v in instance.items() if k != "id"}


class SnippetResponseFactory(SnippetBaseFactory):
    """Factory for creating SnippetResponseModel instances."""

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    type = "custom"
    display_name = None
    last_update = factory.LazyFunction(lambda: fake.word())
    created_in = factory.LazyFunction(lambda: fake.word())
    folders = factory.LazyFunction(lambda: [])
    shared_in = "local"

    @classmethod
    def with_type(cls, type_value="custom", **kwargs):
        """
        Create a response model with a specific type.

        Args:
            type_value: The snippet type (predefined, custom, readonly)
            **kwargs: Additional attributes to override in the model

        Returns:
            Dict: A model instance with the specified type
        """
        return cls(type=type_value, **kwargs)

    @classmethod
    def with_folders(cls, folder_count=2, **kwargs):
        """
        Create a response model with associated folders.

        Args:
            folder_count: Number of folders to associate
            **kwargs: Additional attributes to override in the model

        Returns:
            Dict: A model instance with folder associations
        """
        folders = [FolderReferenceFactory() for _ in range(folder_count)]
        return cls(folders=folders, **kwargs)

    @classmethod
    def predefined(cls, **kwargs):
        """
        Create a predefined snippet response.

        Args:
            **kwargs: Additional attributes to override in the model

        Returns:
            Dict: A predefined snippet model instance
        """
        return cls(type="predefined", **kwargs)

    @classmethod
    def readonly(cls, **kwargs):
        """
        Create a readonly snippet response.

        Args:
            **kwargs: Additional attributes to override in the model

        Returns:
            Dict: A readonly snippet model instance
        """
        return cls(type="readonly", **kwargs)

    @classmethod
    def from_request(
        cls, request_model: Dict[str, Any], **kwargs
    ):
        """
        Create a response model based on a request model.

        This is useful for simulating the API's response to a create or update request.

        Args:
            request_model: The create/update request model or dictionary to base the response on
            **kwargs: Additional attributes to override in the response

        Returns:
            Dict instance
        """
        # Start with the base fields from the request model
        response_data = {
            key: value
            for key, value in request_model.items()
            if key not in ["id"]  # Don't copy ID if present in update model
        }

        # Add response-specific fields
        response_data.update(
            {
                "id": kwargs.pop("id", str(uuid.uuid4())),
                "type": kwargs.pop("type", "custom"),
                "display_name": kwargs.pop("display_name", None),
                "last_update": kwargs.pop("last_update", fake.word()),
                "created_in": kwargs.pop("created_in", fake.word()),
                "folders": kwargs.pop("folders", []),
                "shared_in": kwargs.pop("shared_in", "local"),
            }
        )

        # Add any remaining override fields
        response_data.update(kwargs)

        return cls(**response_data)

    @classmethod
    def build_list_response(cls, count=3, **kwargs):
        """
        Build a dictionary mimicking the list API response with multiple snippets.

        Args:
            count: Number of snippets to include
            **kwargs: Attributes to apply to all snippets

        Returns:
            Dict with data, limit, offset and total fields
        """
        snippets = [cls(**kwargs) for _ in range(count)]
        return {
            "data": snippets,
            "limit": 50,
            "offset": 0,
            "total": count,
        }


# ----------------------------------------------------------------------------
# Snippet model factories for Pydantic validation testing.
# ----------------------------------------------------------------------------


class SnippetCreateModelFactory(factory.DictFactory):
    """Factory for creating dictionary data for SnippetCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"snippet_{n}")
    description = factory.LazyFunction(lambda: fake.sentence())
    labels = factory.LazyFunction(lambda: [fake.word() for _ in range(2)])
    enable_prefix = False

    @classmethod
    def build_valid(cls, **kwargs):
        """
        Return a valid data dict with all expected attributes.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Valid data for SnippetCreateModel
        """
        data = {
            "name": f"snippet_{fake.word()}",
            "description": fake.sentence(),
            "labels": [fake.word() for _ in range(2)],
            "enable_prefix": False,
        }
        return {**data, **kwargs}

    @classmethod
    def build_without_name(cls, **kwargs):
        """
        Return data without a name field (should fail validation).

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Data for SnippetCreateModel without a name
        """
        data = cls.build_valid(**kwargs)
        data.pop("name", None)
        return data
        
    @classmethod
    def build_minimal(cls, **kwargs):
        """
        Return a minimal valid data dict with only required fields.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Minimal valid data for SnippetCreateModel
        """
        return {"name": f"minimal_snippet_{fake.word()}", **kwargs}


class SnippetUpdateModelFactory(factory.DictFactory):
    """Factory for creating dictionary data for SnippetUpdateModel validation testing."""

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"updated_snippet_{n}")
    description = factory.LazyFunction(lambda: fake.sentence())
    labels = factory.LazyFunction(lambda: [fake.word() for _ in range(2)])
    enable_prefix = True

    @classmethod
    def build_valid(cls, **kwargs):
        """
        Return a valid data dict for updating a snippet.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Valid data for SnippetUpdateModel
        """
        data = {
            "id": kwargs.pop("id", str(uuid.uuid4())),
            "name": kwargs.pop("name", f"updated_snippet_{fake.word()}"),
            "description": kwargs.pop("description", fake.sentence()),
            "labels": kwargs.pop("labels", [fake.word() for _ in range(2)]),
            "enable_prefix": kwargs.pop("enable_prefix", True),
        }
        data.update(kwargs)
        return data

    @classmethod
    def build_without_id(cls, **kwargs):
        """
        Return data without an ID field (should fail validation).

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Data for SnippetUpdateModel without an ID
        """
        data = cls.build_valid(**kwargs)
        data.pop("id", None)
        return data
        
    @classmethod
    def build_with_empty_name(cls, **kwargs):
        """
        Return data with an empty name (should fail validation).

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Data for SnippetUpdateModel with empty name
        """
        return cls.build_valid(name="", **kwargs)


class SnippetResponseModelFactory(factory.DictFactory):
    """Factory for creating dictionary data for SnippetResponseModel validation testing."""

    @classmethod
    def build_valid(cls, **kwargs):
        """
        Return a valid data dict for a snippet response.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Valid data for SnippetResponseModel
        """
        data = {
            "id": kwargs.pop("id", str(uuid.uuid4())),
            "name": kwargs.pop("name", f"snippet_{fake.word()}"),
            "description": kwargs.pop("description", "Description for snippet"),
            "labels": kwargs.pop("labels", [fake.word() for _ in range(2)]),
            "enable_prefix": kwargs.pop("enable_prefix", False),
            "type": kwargs.pop("type", "custom"),
            "display_name": kwargs.pop("display_name", None),
            "last_update": kwargs.pop("last_update", fake.word()),
            "created_in": kwargs.pop("created_in", fake.word()),
            "folders": kwargs.pop("folders", []),
            "shared_in": kwargs.pop("shared_in", "local"),
        }
        data.update(kwargs)
        return data

    @classmethod
    def build_predefined(cls, **kwargs):
        """
        Return a valid data dict for a predefined snippet.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Valid data for a predefined SnippetResponseModel
        """
        return cls.build_valid(type="predefined", **kwargs)
        
    @classmethod
    def build_custom(cls, **kwargs):
        """
        Return a valid data dict for a custom snippet.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Valid data for a custom SnippetResponseModel
        """
        return cls.build_valid(type="custom", **kwargs)

    @classmethod
    def build_with_folders(cls, folder_count=2, **kwargs):
        """
        Return a valid data dict for a snippet with folders.

        Args:
            folder_count: Number of folders to associate
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Valid data for SnippetResponseModel with folders
        """
        folders = []
        for _ in range(folder_count):
            folders.append(
                {
                    "id": str(uuid.uuid4()),
                    "name": f"folder_{fake.word()}",
                }
            )
        return cls.build_valid(folders=folders, **kwargs)
        
    @classmethod
    def build_with_empty_name(cls, **kwargs):
        """
        Return an invalid data dict with empty name (should fail validation).

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Invalid data for SnippetResponseModel with empty name
        """
        return cls.build_valid(name="", **kwargs)
        
    @classmethod
    def build_without_id(cls, **kwargs):
        """
        Return an invalid data dict without ID (should fail validation).

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Invalid data for SnippetResponseModel without ID
        """
        data = cls.build_valid(**kwargs)
        data.pop("id", None)
        return data
