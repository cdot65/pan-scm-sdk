"""LDAP Server Profile models for Strata Cloud Manager SDK.

Contains Pydantic models for representing LDAP server profile objects and related data.
"""

# scm/models/identity/ldap_server_profiles.py

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
class LdapType(str, Enum):
    """Enumeration of LDAP server types."""

    active_directory = "active-directory"
    e_directory = "e-directory"
    sun = "sun"
    other = "other"


# Component Models
class LdapServer(BaseModel):
    """Represents an LDAP server entry.

    Attributes:
        name (Optional[str]): Server name.
        address (Optional[str]): Server address.
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


# Base Model
class LdapServerProfileBaseModel(BaseModel):
    """Base model for LDAP Server Profile containing common fields across all operations."""

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
    server: Optional[List[LdapServer]] = Field(
        None,
        description="List of LDAP servers",
    )
    base: Optional[str] = Field(
        None,
        description="Base distinguished name",
        max_length=255,
    )
    bind_dn: Optional[str] = Field(
        None,
        description="Bind distinguished name",
        max_length=255,
    )
    bind_password: Optional[str] = Field(
        None,
        description="Bind password",
        max_length=121,
    )
    bind_timelimit: Optional[str] = Field(
        None,
        description="Bind time limit",
    )
    ldap_type: Optional[LdapType] = Field(
        None,
        description="LDAP server type",
    )
    retry_interval: Optional[int] = Field(
        None,
        description="Retry interval in seconds",
    )
    ssl: Optional[bool] = Field(
        None,
        description="Enable SSL",
    )
    timelimit: Optional[int] = Field(
        None,
        description="Time limit in seconds",
    )
    verify_server_certificate: Optional[bool] = Field(
        None,
        description="Verify server certificate",
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


class LdapServerProfileCreateModel(LdapServerProfileBaseModel):
    """Model for creating a new LDAP Server Profile.

    Inherits from base model and adds create-specific validation.
    """

    @model_validator(mode="after")
    def validate_container_type(self) -> "LdapServerProfileCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            LdapServerProfileCreateModel: The validated model instance.

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


class LdapServerProfileUpdateModel(LdapServerProfileBaseModel):
    """Model for updating an existing LDAP Server Profile.

    All fields are optional to allow partial updates.
    """

    id: UUID = Field(
        ...,
        description="Profile ID",
    )


class LdapServerProfileResponseModel(LdapServerProfileBaseModel):
    """Model for LDAP Server Profile API responses.

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
