"""TACACS+ Server Profile models for Strata Cloud Manager SDK.

Contains Pydantic models for representing TACACS+ server profile objects and related data.
"""

# scm/models/identity/tacacs_server_profiles.py

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
class TacacsProtocol(str, Enum):
    """Enumeration of TACACS+ protocol types."""

    CHAP = "CHAP"
    PAP = "PAP"


# Component Models
class TacacsServer(BaseModel):
    """Represents a TACACS+ server entry.

    Attributes:
        name (Optional[str]): Server name.
        address (Optional[str]): Server address.
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
    address: Optional[str] = Field(
        None,
        description="Server address",
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
class TacacsServerProfileBaseModel(BaseModel):
    """Base model for TACACS+ Server Profile containing common fields across all operations."""

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
    server: Optional[List[TacacsServer]] = Field(
        None,
        description="List of TACACS+ servers",
    )
    protocol: Optional[TacacsProtocol] = Field(
        None,
        description="TACACS+ protocol type",
    )
    timeout: Optional[int] = Field(
        None,
        description="Timeout in seconds",
        ge=1,
        le=30,
    )
    use_single_connection: Optional[bool] = Field(
        None,
        description="Use single connection",
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


class TacacsServerProfileCreateModel(TacacsServerProfileBaseModel):
    """Model for creating a new TACACS+ Server Profile.

    Inherits from base model and adds create-specific validation.
    """

    @model_validator(mode="after")
    def validate_container_type(self) -> "TacacsServerProfileCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            TacacsServerProfileCreateModel: The validated model instance.

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


class TacacsServerProfileUpdateModel(TacacsServerProfileBaseModel):
    """Model for updating an existing TACACS+ Server Profile.

    All fields are optional to allow partial updates.
    """

    id: UUID = Field(
        ...,
        description="Profile ID",
    )


class TacacsServerProfileResponseModel(TacacsServerProfileBaseModel):
    """Model for TACACS+ Server Profile API responses.

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
