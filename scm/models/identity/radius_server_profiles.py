"""RADIUS Server Profile models for Strata Cloud Manager SDK.

Contains Pydantic models for representing RADIUS server profile objects and related data.
"""

# scm/models/identity/radius_server_profiles.py

from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


# Component Models
class RadiusProtocol(BaseModel):
    """Represents the RADIUS protocol configuration (oneOf pattern).

    Exactly one protocol type should be provided.

    Attributes:
        CHAP (Optional[Dict]): CHAP protocol.
        PAP (Optional[Dict]): PAP protocol.
        EAP_TTLS_with_PAP (Optional[Dict]): EAP-TTLS with PAP protocol.
        PEAP_MSCHAPv2 (Optional[Dict]): PEAP-MSCHAPv2 protocol.
        PEAP_with_GTC (Optional[Dict]): PEAP with GTC protocol.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    CHAP: Optional[Dict] = Field(
        None,
        description="CHAP protocol",
    )
    PAP: Optional[Dict] = Field(
        None,
        description="PAP protocol",
    )
    EAP_TTLS_with_PAP: Optional[Dict] = Field(
        None,
        description="EAP-TTLS with PAP protocol",
    )
    PEAP_MSCHAPv2: Optional[Dict] = Field(
        None,
        description="PEAP-MSCHAPv2 protocol",
    )
    PEAP_with_GTC: Optional[Dict] = Field(
        None,
        description="PEAP with GTC protocol",
    )


class RadiusServer(BaseModel):
    """Represents a RADIUS server entry.

    Attributes:
        name (Optional[str]): Server name.
        ip_address (Optional[str]): Server IP address.
        port (Optional[int]): Server port number (1-65535).
        secret (Optional[str]): Shared secret.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: Optional[str] = Field(
        None,
        description="Server name",
    )
    ip_address: Optional[str] = Field(
        None,
        description="Server IP address",
    )
    port: Optional[int] = Field(
        None,
        description="Server port number",
        ge=1,
        le=65535,
    )
    secret: Optional[str] = Field(
        None,
        description="Shared secret",
    )


# Base Model
class RadiusServerProfileBaseModel(BaseModel):
    """Base model for RADIUS Server Profile containing common fields across all operations."""

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
    server: Optional[List[RadiusServer]] = Field(
        None,
        description="List of RADIUS servers",
    )
    protocol: Optional[RadiusProtocol] = Field(
        None,
        description="RADIUS protocol configuration",
    )
    retries: Optional[int] = Field(
        None,
        description="Number of retries",
        ge=1,
        le=5,
    )
    timeout: Optional[int] = Field(
        None,
        description="Timeout in seconds",
        ge=1,
        le=120,
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


class RadiusServerProfileCreateModel(RadiusServerProfileBaseModel):
    """Model for creating a new RADIUS Server Profile.

    Inherits from base model and adds create-specific validation.
    """

    @model_validator(mode="after")
    def validate_container_type(self) -> "RadiusServerProfileCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            RadiusServerProfileCreateModel: The validated model instance.

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


class RadiusServerProfileUpdateModel(RadiusServerProfileBaseModel):
    """Model for updating an existing RADIUS Server Profile.

    All fields are optional to allow partial updates.
    """

    id: UUID = Field(
        ...,
        description="Profile ID",
    )


class RadiusServerProfileResponseModel(RadiusServerProfileBaseModel):
    """Model for RADIUS Server Profile API responses.

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
