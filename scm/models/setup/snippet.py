"""Models for interacting with Snippets in Palo Alto Networks' Strata Cloud Manager.

This module defines the Pydantic models used for creating, updating, and
representing Snippet resources in the Strata Cloud Manager.
"""

from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class FolderReference(BaseModel):
    """Reference to a folder that a snippet is applied to."""

    id: UUID = Field(..., description="The UUID of the folder")
    name: str = Field(..., description="The name of the folder")

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        """Validate that the name is not empty."""
        if not value or value.strip() == "":
            raise ValueError("Folder name cannot be empty")
        return value


class SnippetBaseModel(BaseModel):
    """Base model for Snippet resources containing common fields.

    Attributes:
        name: The name of the snippet.
        description: Optional description of the snippet.
        labels: Optional list of labels to apply to the snippet.
        enable_prefix: Whether to enable prefix for the snippet.

    """

    name: str = Field(
        ...,
        description="The name of the snippet",
    )
    description: Optional[str] = Field(
        default=None,
        description="An optional description of the snippet",
    )
    labels: Optional[List[str]] = Field(
        default=None,
        description="Optional list of labels to apply to the snippet",
    )
    enable_prefix: Optional[bool] = Field(
        default=None,
        description="Whether to enable prefix for this snippet",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        """Validate that the name is not empty."""
        if not value or value.strip() == "":
            raise ValueError("Snippet name cannot be empty")
        return value


class SnippetCreateModel(SnippetBaseModel):
    """Model for creating new Snippet resources.

    Inherits all fields from SnippetBaseModel without additional fields.
    """

    pass


class SnippetUpdateModel(SnippetBaseModel):
    """Model for updating existing Snippet resources.

    Attributes:
        id: The unique identifier of the snippet to update.

    """

    id: UUID = Field(
        ...,
        description="The unique identifier of the snippet",
    )


class SnippetResponseModel(SnippetBaseModel):
    """Model for Snippet responses from the API.

    Attributes:
        id: The unique identifier of the snippet.
        type: The type of snippet (predefined, custom, or readonly).
        display_name: The display name of the snippet.
        last_update: Timestamp of the last update.
        created_in: Timestamp of when the snippet was created.
        folders: Folders the snippet is applied to.
        shared_in: Sharing scope of the snippet.

    """

    id: UUID = Field(
        ...,
        description="The unique identifier of the snippet",
    )
    type: Optional[Literal["predefined", "custom", "readonly"]] = Field(
        default=None,
        description="The type of snippet (predefined, custom, or readonly)",
    )
    display_name: Optional[str] = Field(
        default=None,
        description="The display name of the snippet",
    )
    last_update: Optional[str] = Field(
        default=None,
        description="Timestamp of the last update",
    )
    created_in: Optional[str] = Field(
        default=None,
        description="Timestamp of when the snippet was created",
    )
    folders: Optional[List[FolderReference]] = Field(
        default=None,
        description="Folders the snippet is applied to",
    )
    shared_in: Optional[str] = Field(
        default=None,
        description="Sharing scope of the snippet (e.g., 'local')",
    )
