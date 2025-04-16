"""
Models for interacting with Folders in Palo Alto Networks' Strata Cloud Manager.

This module defines the Pydantic models used for creating, updating, and
representing Folder resources in the Strata Cloud Manager.
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class FolderBaseModel(BaseModel):
    """
    Base model for Folder resources containing common fields.

    Attributes:
        name: The name of the folder.
        parent: The ID of the parent folder.
        description: Optional description of the folder.
        labels: Optional list of labels to apply to the folder.
        snippets: Optional list of snippet IDs associated with the folder.
    """

    name: str = Field(
        description="The name of the folder",
    )
    parent: str = Field(
        description="The ID of the parent folder",
    )
    description: Optional[str] = Field(
        default=None,
        description="An optional description of the folder",
    )
    labels: Optional[List[str]] = Field(
        default=None,
        description="Optional list of labels to apply to the folder",
    )
    snippets: Optional[List[str]] = Field(
        default=None,
        description="Optional list of snippet IDs associated with the folder",
    )


class FolderCreateModel(FolderBaseModel):
    """
    Model for creating new Folder resources.

    Inherits all fields from FolderBaseModel without additional fields.
    """

    pass


class FolderUpdateModel(FolderBaseModel):
    """
    Model for updating existing Folder resources.

    Attributes:
        id: The unique identifier of the folder to update.
    """

    id: UUID = Field(
        description="The unique identifier of the folder",
    )


class FolderResponseModel(FolderBaseModel):
    """
    Model for Folder responses from the API.

    Attributes:
        id: The unique identifier of the folder.
    """

    id: UUID = Field(
        description="The unique identifier of the folder",
    )

    @field_validator("parent")
    @classmethod
    def validate_parent(cls, v: str) -> str:
        """
        Validate parent field. Empty string is allowed for root folders.

        Args:
            v: The parent value to validate.

        Returns:
            The validated parent value.
        """
        # Allow empty string for root folders
        return v
