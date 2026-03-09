"""SAML Server Profile models for Strata Cloud Manager SDK.

Contains Pydantic models for representing SAML server profile objects and related data.
"""

# scm/models/identity/saml_server_profiles.py

from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


# Enums
class SamlSsoBindings(str, Enum):
    """Enumeration of SAML SSO binding types."""

    post = "post"
    redirect = "redirect"


class SamlSloBindings(str, Enum):
    """Enumeration of SAML SLO binding types."""

    post = "post"
    redirect = "redirect"


# Base Model
class SamlServerProfileBaseModel(BaseModel):
    """Base model for SAML Server Profile containing common fields across all operations."""

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
    entity_id: str = Field(
        ...,
        description="Entity ID",
        max_length=1024,
    )
    certificate: str = Field(
        ...,
        description="Certificate name",
        max_length=63,
    )
    sso_url: str = Field(
        ...,
        description="Single Sign-On URL",
        max_length=255,
    )
    sso_bindings: SamlSsoBindings = Field(
        ...,
        description="SSO binding type",
    )
    slo_bindings: Optional[SamlSloBindings] = Field(
        None,
        description="SLO binding type",
    )
    max_clock_skew: Optional[int] = Field(
        None,
        description="Maximum clock skew in seconds",
        ge=1,
        le=900,
    )
    validate_idp_certificate: Optional[bool] = Field(
        None,
        description="Validate IDP certificate",
    )
    want_auth_requests_signed: Optional[bool] = Field(
        None,
        description="Want authentication requests signed",
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


class SamlServerProfileCreateModel(SamlServerProfileBaseModel):
    """Model for creating a new SAML Server Profile.

    Inherits from base model and adds create-specific validation.
    """

    @model_validator(mode="after")
    def validate_container_type(self) -> "SamlServerProfileCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            SamlServerProfileCreateModel: The validated model instance.

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


class SamlServerProfileUpdateModel(SamlServerProfileBaseModel):
    """Model for updating an existing SAML Server Profile.

    All fields are optional to allow partial updates.
    """

    id: UUID = Field(
        ...,
        description="Profile ID",
    )


class SamlServerProfileResponseModel(SamlServerProfileBaseModel):
    """Model for SAML Server Profile API responses.

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
