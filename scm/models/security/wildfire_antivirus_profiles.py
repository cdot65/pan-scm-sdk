# scm/models/security/wildfire_antivirus_profiles.py

from typing import List, Optional
from pydantic import (
    BaseModel,
    Field,
    model_validator,
    field_validator,
    ConfigDict,
)
from enum import Enum
import uuid


class Analysis(str, Enum):
    """Enumeration of analysis types."""

    public_cloud = "public-cloud"
    private_cloud = "private-cloud"


class Direction(str, Enum):
    """Enumeration of directions."""

    download = "download"
    upload = "upload"
    both = "both"


class RuleBase(BaseModel):
    """
    Base class for Rule.
    """

    name: str = Field(
        ...,
        description="Rule name",
    )
    analysis: Optional[Analysis] = Field(
        None,
        description="Analysis type",
    )
    application: List[str] = Field(
        default_factory=lambda: ["any"],
        description="List of applications",
    )
    direction: Direction = Field(
        ...,
        description="Direction",
    )
    file_type: List[str] = Field(
        default_factory=lambda: ["any"],
        description="List of file types",
    )


class RuleRequest(RuleBase):
    pass  # No additional fields needed for request-specific model


class RuleResponse(RuleBase):
    pass  # No additional fields needed for response-specific model


class MlavExceptionEntry(BaseModel):
    """
    Represents an entry in the 'mlav_exception' list.
    """

    name: str = Field(
        ...,
        description="Exception name",
    )
    description: Optional[str] = Field(
        None,
        description="Description",
    )
    filename: str = Field(
        ...,
        description="Filename",
    )


class ThreatExceptionEntry(BaseModel):
    """
    Represents an entry in the 'threat_exception' list.
    """

    name: str = Field(
        ...,
        description="Threat exception name",
    )
    notes: Optional[str] = Field(
        None,
        description="Notes",
    )


class WildfireAntivirusProfileBaseModel(BaseModel):
    """
    Base model for Wildfire Antivirus Profile, containing common fields.
    """

    name: str = Field(
        ...,
        description="Profile name",
        pattern=r"^[a-zA-Z0-9._-]+$",
    )
    description: Optional[str] = Field(
        None,
        description="Description",
    )
    packet_capture: Optional[bool] = Field(
        False,
        description="Packet capture enabled",
    )
    mlav_exception: Optional[List[MlavExceptionEntry]] = Field(
        None,
        description="MLAV exceptions",
    )
    rules: List[RuleBase] = Field(
        ...,
        description="List of rules",
    )
    threat_exception: Optional[List[ThreatExceptionEntry]] = Field(
        None,
        description="List of threat exceptions",
    )


class WildfireAntivirusProfileRequestModel(WildfireAntivirusProfileBaseModel):
    """
    Represents a Wildfire Antivirus Profile for API requests.
    """

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

    model_config = ConfigDict(validate_assignment=True, arbitrary_types_allowed=True)

    @model_validator(mode="after")
    def validate_container(self) -> "WildfireAntivirusProfileRequestModel":
        container_fields = [
            "folder",
            "snippet",
            "device",
        ]
        provided_containers = [
            field for field in container_fields if getattr(self, field) is not None
        ]

        if len(provided_containers) != 1:
            raise ValueError(
                "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            )

        return self


class WildfireAntivirusProfileResponseModel(WildfireAntivirusProfileBaseModel):
    """
    Represents a Wildfire Antivirus Profile for API responses.
    """

    id: str = Field(
        ...,
        description="Profile ID",
    )
    folder: Optional[str] = Field(
        None,
        description="Folder",
    )
    snippet: Optional[str] = Field(
        None,
        description="Snippet",
    )
    device: Optional[str] = Field(
        None,
        description="Device",
    )

    @field_validator("id", mode="before")
    @classmethod
    def validate_id(cls, v):
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError("Invalid UUID format for 'id'")
        return v


class WildfireAntivirusProfilesResponse(BaseModel):
    """
    Represents the API response containing a list of Wildfire Antivirus Profiles.
    """

    data: List[WildfireAntivirusProfileResponseModel]
    offset: int
    total: int
    limit: int
