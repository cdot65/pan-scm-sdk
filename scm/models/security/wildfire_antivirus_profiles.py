# scm/models/security/wildfire_antivirus_profiles.py

from typing import List, Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
    model_validator,
    ConfigDict,
)
from enum import Enum


# Enums
class Analysis(str, Enum):
    """Enumeration of analysis types."""

    public_cloud = "public-cloud"
    private_cloud = "private-cloud"


class Direction(str, Enum):
    """Enumeration of directions."""

    download = "download"
    upload = "upload"
    both = "both"


# Component Models
class RuleBase(BaseModel):
    """Base class for Rule configuration."""

    name: str = Field(..., description="Rule name")
    analysis: Optional[Analysis] = Field(None, description="Analysis type")
    application: List[str] = Field(
        default_factory=lambda: ["any"],
        description="List of applications",
    )
    direction: Direction = Field(..., description="Direction")
    file_type: List[str] = Field(
        default_factory=lambda: ["any"],
        description="List of file types",
    )


class MlavExceptionEntry(BaseModel):
    """Represents an entry in the 'mlav_exception' list."""

    name: str = Field(..., description="Exception name")
    description: Optional[str] = Field(None, description="Description")
    filename: str = Field(..., description="Filename")


class ThreatExceptionEntry(BaseModel):
    """Represents an entry in the 'threat_exception' list."""

    name: str = Field(..., description="Threat exception name")
    notes: Optional[str] = Field(None, description="Notes")


# Base Model
class WildfireAntivirusProfileBase(BaseModel):
    """
    Base model for Wildfire Antivirus Profile containing common fields.
    """

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
    mlav_exception: Optional[List[MlavExceptionEntry]] = Field(
        None,
        description="MLAV exceptions",
    )
    rules: List[RuleBase] = Field(..., description="List of rules")
    threat_exception: Optional[List[ThreatExceptionEntry]] = Field(
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
class WildfireAntivirusProfileCreateModel(WildfireAntivirusProfileBase):
    """
    Model for creating a new Wildfire Antivirus Profile.
    Inherits from base model and adds container validation.
    """

    @model_validator(mode="after")
    def validate_container(self) -> "WildfireAntivirusProfileCreateModel":
        container_fields = ["folder", "snippet", "device"]
        provided_containers = [
            field for field in container_fields if getattr(self, field) is not None
        ]
        if len(provided_containers) != 1:
            raise ValueError(
                "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            )
        return self


# Update Model
class WildfireAntivirusProfileUpdateModel(WildfireAntivirusProfileBase):
    """
    Model for updating an existing Wildfire Antivirus Profile.
    All fields are optional to allow partial updates.
    """


# Response Model
class WildfireAntivirusProfileResponseModel(WildfireAntivirusProfileBase):
    """
    Model for Wildfire Antivirus Profile API responses.
    Includes all base fields plus the id field.
    """

    id: UUID = Field(
        ...,
        description="Profile ID",
    )
