"""Kerberos Server Profile models for Strata Cloud Manager SDK.

Contains Pydantic models for representing Kerberos server profile objects and related data.
"""

# scm/models/identity/kerberos_server_profiles.py

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


# Component Models
class KerberosServer(BaseModel):
    """Represents a Kerberos server entry.

    Attributes:
        name (Optional[str]): Server name.
        host (Optional[str]): Server hostname or IP address.
        port (Optional[int]): Server port number (1-65535).

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: Optional[str] = Field(
        None,
        description="Server name",
    )
    host: Optional[str] = Field(
        None,
        description="Server hostname or IP address",
    )
    port: Optional[int] = Field(
        None,
        description="Server port number",
        ge=1,
        le=65535,
    )


# Base Model
class KerberosServerProfileBaseModel(BaseModel):
    """Base model for Kerberos Server Profile containing common fields across all operations."""

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
    server: Optional[List[KerberosServer]] = Field(
        None,
        description="List of Kerberos servers",
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


class KerberosServerProfileCreateModel(KerberosServerProfileBaseModel):
    """Model for creating a new Kerberos Server Profile.

    Inherits from base model and adds create-specific validation.
    """

    @model_validator(mode="after")
    def validate_container_type(self) -> "KerberosServerProfileCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            KerberosServerProfileCreateModel: The validated model instance.

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


class KerberosServerProfileUpdateModel(KerberosServerProfileBaseModel):
    """Model for updating an existing Kerberos Server Profile.

    All fields are optional to allow partial updates.
    """

    id: UUID = Field(
        ...,
        description="Profile ID",
    )


class KerberosServerProfileResponseModel(KerberosServerProfileBaseModel):
    """Model for Kerberos Server Profile API responses.

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
