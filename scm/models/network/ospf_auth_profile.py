"""OSPF Authentication Profile models for Strata Cloud Manager SDK.

Contains Pydantic models for representing OSPF authentication profile objects and related data.
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


# --- Nested Models ---


class OspfAuthProfileMd5Key(BaseModel):
    """OSPF auth profile MD5 key entry."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: Optional[int] = Field(
        None,
        description="Key ID",
        ge=1,
        le=255,
    )
    key: Optional[str] = Field(
        None,
        description="MD5 hash",
        max_length=16,
    )
    preferred: Optional[bool] = Field(
        None,
        description="Preferred key",
    )


# --- Main Models ---


class OspfAuthProfileBaseModel(BaseModel):
    """Base model for OSPF Authentication Profiles."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    name: str = Field(
        ...,
        description="Profile name",
    )
    password: Optional[str] = Field(
        None,
        description="Simple password authentication",
    )
    md5: Optional[List[OspfAuthProfileMd5Key]] = Field(
        None,
        description="MD5 authentication keys",
    )

    # Container fields
    folder: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The folder in which the resource is defined",
    )
    snippet: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The snippet in which the resource is defined",
    )
    device: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The device in which the resource is defined",
    )

    @model_validator(mode="after")
    def validate_auth_type(self) -> "OspfAuthProfileBaseModel":
        """Enforce password and md5 are mutually exclusive."""
        if self.password is not None and self.md5 is not None:
            raise ValueError("'password' and 'md5' are mutually exclusive.")
        return self


class OspfAuthProfileCreateModel(OspfAuthProfileBaseModel):
    """Model for creating new OSPF Authentication Profiles."""

    @model_validator(mode="after")
    def validate_container_type(self) -> "OspfAuthProfileCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            OspfAuthProfileCreateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = ["folder", "snippet", "device"]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class OspfAuthProfileUpdateModel(OspfAuthProfileBaseModel):
    """Model for updating OSPF Authentication Profiles."""

    id: UUID = Field(
        ...,
        description="The UUID of the resource",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class OspfAuthProfileResponseModel(OspfAuthProfileBaseModel):
    """Model for OSPF Authentication Profile responses."""

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    id: UUID = Field(
        ...,
        description="The UUID of the resource",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
