"""URL Access Profiles security models for Strata Cloud Manager SDK.

Contains Pydantic models for representing URL access profile objects and related data.
"""

# scm/models/security/url_access_profiles.py

from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


# Component Models
class CredentialEnforcementMode(BaseModel):
    """Represents the mode configuration for credential enforcement.

    Attributes:
        disabled (Optional[Dict]): Disabled mode.
        domain_credentials (Optional[Dict]): Domain credentials mode.
        ip_user (Optional[Dict]): IP user mode.
        group_mapping (Optional[str]): Group mapping mode.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    disabled: Optional[Dict] = Field(
        None,
        description="Disabled mode",
    )
    domain_credentials: Optional[Dict] = Field(
        None,
        description="Domain credentials mode",
    )
    ip_user: Optional[Dict] = Field(
        None,
        description="IP user mode",
    )
    group_mapping: Optional[str] = Field(
        None,
        description="Group mapping mode",
    )


class CredentialEnforcement(BaseModel):
    """Represents the credential enforcement settings for a URL access profile.

    Attributes:
        alert (Optional[List[str]]): URL categories for alert action.
        allow (Optional[List[str]]): URL categories for allow action.
        block (Optional[List[str]]): URL categories for block action.
        continue_ (Optional[List[str]]): URL categories for continue action.
        log_severity (Optional[str]): Log severity level.
        mode (Optional[CredentialEnforcementMode]): Credential enforcement mode.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    alert: Optional[List[str]] = Field(
        None,
        description="URL categories for alert action",
    )
    allow: Optional[List[str]] = Field(
        None,
        description="URL categories for allow action",
    )
    block: Optional[List[str]] = Field(
        None,
        description="URL categories for block action",
    )
    continue_: Optional[List[str]] = Field(
        None,
        alias="continue",
        description="URL categories for continue action",
    )
    log_severity: Optional[str] = Field(
        "medium",
        description="Log severity level",
    )
    mode: Optional[CredentialEnforcementMode] = Field(
        None,
        description="Credential enforcement mode",
    )


# Base Model
class URLAccessProfileBaseModel(BaseModel):
    """Base model for URL Access Profile containing common fields across all operations."""

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
        max_length=255,
    )
    alert: Optional[List[str]] = Field(
        None,
        description="URL categories for alert action",
    )
    allow: Optional[List[str]] = Field(
        None,
        description="URL categories for allow action",
    )
    block: Optional[List[str]] = Field(
        None,
        description="URL categories for block action",
    )
    continue_: Optional[List[str]] = Field(
        None,
        alias="continue",
        description="URL categories for continue action",
    )
    redirect: Optional[List[str]] = Field(
        None,
        description="URL categories for redirect action",
    )
    cloud_inline_cat: Optional[bool] = Field(
        None,
        description="Enable cloud inline categorization",
    )
    local_inline_cat: Optional[bool] = Field(
        None,
        description="Enable local inline categorization",
    )
    credential_enforcement: Optional[CredentialEnforcement] = Field(
        None,
        description="Credential enforcement settings",
    )
    mlav_category_exception: Optional[List[str]] = Field(
        None,
        description="MLAV category exceptions",
    )
    log_container_page_only: Optional[bool] = Field(
        None,
        description="Log container page only",
    )
    log_http_hdr_referer: Optional[bool] = Field(
        None,
        description="Log HTTP header referer",
    )
    log_http_hdr_user_agent: Optional[bool] = Field(
        None,
        description="Log HTTP header user agent",
    )
    log_http_hdr_xff: Optional[bool] = Field(
        None,
        description="Log HTTP header X-Forwarded-For",
    )
    safe_search_enforcement: Optional[bool] = Field(
        None,
        description="Enable safe search enforcement",
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


class URLAccessProfileCreateModel(URLAccessProfileBaseModel):
    """Model for creating a new URL Access Profile.

    Inherits from base model and adds create-specific validation.
    """

    @model_validator(mode="after")
    def validate_container_type(self) -> "URLAccessProfileCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            URLAccessProfileCreateModel: The validated model instance.

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


class URLAccessProfileUpdateModel(URLAccessProfileBaseModel):
    """Model for updating an existing URL Access Profile.

    All fields are optional to allow partial updates.
    """

    id: UUID = Field(
        ...,
        description="Profile ID",
    )


class URLAccessProfileResponseModel(URLAccessProfileBaseModel):
    """Model for URL Access Profile API responses.

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
