"""File Blocking Profiles security models for Strata Cloud Manager SDK.

Contains Pydantic models for representing file blocking profile objects and related data.
"""

# scm/models/security/file_blocking_profiles.py

from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


# Enums
class FileBlockingAction(str, Enum):
    """Enumeration of file blocking actions."""

    alert = "alert"
    block = "block"
    continue_ = "continue"


class FileBlockingDirection(str, Enum):
    """Enumeration of file blocking directions."""

    download = "download"
    upload = "upload"
    both = "both"


# Component Models
class FileBlockingRule(BaseModel):
    """Represents a rule within a file blocking profile.

    Attributes:
        name (str): Rule name.
        action (FileBlockingAction): Action to take when rule matches.
        application (List[str]): Applications to match.
        direction (FileBlockingDirection): Direction of file transfer.
        file_type (List[str]): File types to match.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(
        ...,
        description="Rule name",
    )
    action: FileBlockingAction = Field(
        FileBlockingAction.alert,
        description="Action to take when rule matches",
    )
    application: List[str] = Field(
        default_factory=lambda: ["any"],
        description="Applications to match",
    )
    direction: FileBlockingDirection = Field(
        FileBlockingDirection.both,
        description="Direction of file transfer",
    )
    file_type: List[str] = Field(
        default_factory=lambda: ["any"],
        description="File types to match",
    )


# Base Model
class FileBlockingProfileBaseModel(BaseModel):
    """Base model for File Blocking Profile containing common fields across all operations."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    name: str = Field(
        ...,
        description="Profile name",
    )
    description: Optional[str] = Field(
        None,
        description="Description",
    )
    rules: Optional[List[FileBlockingRule]] = Field(
        None,
        description="List of file blocking rules",
    )

    folder: Optional[str] = Field(
        None,
        description="Folder in which the resource is defined",
        max_length=64,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
    )
    snippet: Optional[str] = Field(
        None,
        description="Snippet in which the resource is defined",
        max_length=64,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
    )
    device: Optional[str] = Field(
        None,
        description="Device in which the resource is defined",
        max_length=64,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
    )


class FileBlockingProfileCreateModel(FileBlockingProfileBaseModel):
    """Model for creating a new File Blocking Profile.

    Inherits from base model and adds create-specific validation.
    """

    @model_validator(mode="after")
    def validate_container_type(self) -> "FileBlockingProfileCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            FileBlockingProfileCreateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = [
            "folder",
            "snippet",
            "device",
        ]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class FileBlockingProfileUpdateModel(FileBlockingProfileBaseModel):
    """Model for updating an existing File Blocking Profile.

    All fields are optional to allow partial updates.
    """

    id: UUID = Field(
        ...,
        description="Profile ID",
    )


class FileBlockingProfileResponseModel(FileBlockingProfileBaseModel):
    """Model for File Blocking Profile API responses.

    Includes all base fields plus the id field.
    """

    model_config = ConfigDict(
        extra="ignore",
        validate_assignment=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    id: UUID = Field(
        ...,
        description="Profile ID",
    )
