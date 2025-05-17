"""WildFire Antivirus Profiles security models for Strata Cloud Manager SDK.

Contains Pydantic models for representing WildFire antivirus profile objects and related data.
"""

# scm/models/security/wildfire_antivirus_profiles.py

from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


# Enums
class WildfireAvAnalysis(str, Enum):
    """Enumeration of analysis types."""

    public_cloud = "public-cloud"
    private_cloud = "private-cloud"


class WildfireAvDirection(str, Enum):
    """Enumeration of directions."""

    download = "download"
    upload = "upload"
    both = "both"


# Component Models
class WildfireAvRuleBase(BaseModel):
    """Base class for Rule configuration."""

    name: str = Field(..., description="Rule name")
    analysis: Optional[WildfireAvAnalysis] = Field(None, description="Analysis type")
    application: List[str] = Field(
        default_factory=lambda: ["any"],
        description="List of applications",
    )
    direction: WildfireAvDirection = Field(..., description="Direction")
    file_type: List[str] = Field(
        default_factory=lambda: ["any"],
        description="List of file types",
    )


class WildfireAvMlavExceptionEntry(BaseModel):
    """Represents an entry in the 'mlav_exception' list."""

    name: str = Field(..., description="Exception name")
    description: Optional[str] = Field(None, description="Description")
    filename: str = Field(..., description="Filename")


class WildfireAvThreatExceptionEntry(BaseModel):
    """Represents an entry in the 'threat_exception' list."""

    name: str = Field(..., description="Threat exception name")
    notes: Optional[str] = Field(None, description="Notes")


"""
Module for Wildfire Antivirus Profile models and related logic.
"""


# Base Model
class WildfireAvProfileBase(BaseModel):
    """Base model for Wildfire Antivirus Profile containing common fields."""

    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    name: str = Field(
        ...,
        description="Profile name",
        pattern=r"^[a-zA-Z0-9._-]+$",
    )
    description: Optional[str] = Field(None, description="Description")
    packet_capture: Optional[bool] = Field(
        False,
        description="Packet capture enabled",
    )
    mlav_exception: Optional[List[WildfireAvMlavExceptionEntry]] = Field(
        None,
        description="MLAV exceptions",
    )
    rules: List[WildfireAvRuleBase] = Field(..., description="List of rules")
    threat_exception: Optional[List[WildfireAvThreatExceptionEntry]] = Field(
        None,
        description="List of threat exceptions",
    )
    folder: Optional[str] = Field(
        None,
        description="Folder",
        max_length=64,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
    )
    snippet: Optional[str] = Field(
        None,
        description="Snippet",
        max_length=64,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
    )
    device: Optional[str] = Field(
        None,
        description="Device",
        max_length=64,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
    )


# Create Model
class WildfireAvProfileCreateModel(WildfireAvProfileBase):
    """Model for creating a new Wildfire Antivirus Profile.

    Inherits from base model and adds container validation.
    """

    @model_validator(mode="after")
    def validate_container_type(self) -> "WildfireAvProfileCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            WildfireAvProfileCreateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = ["folder", "snippet", "device"]
        provided_containers = [
            field for field in container_fields if getattr(self, field) is not None
        ]
        if len(provided_containers) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


# Update Model
class WildfireAvProfileUpdateModel(WildfireAvProfileBase):
    """Model for updating an existing Wildfire Antivirus Profile.

    All fields are optional to allow partial updates.
    """

    id: Optional[UUID] = Field(
        ...,
        description="Profile ID",
    )


# Response Model
class WildfireAvProfileResponseModel(WildfireAvProfileBase):
    """Model for Wildfire Antivirus Profile API responses.

    Includes all base fields plus the id field.
    """

    id: UUID = Field(
        ...,
        description="Profile ID",
    )
