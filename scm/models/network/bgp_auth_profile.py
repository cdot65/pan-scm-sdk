"""BGP Authentication Profile models for Strata Cloud Manager SDK.

Contains Pydantic models for representing BGP authentication profile objects and related data.
"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


# --- Main Models ---


class BgpAuthProfileBaseModel(BaseModel):
    """Base model for BGP Authentication Profiles."""

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
    secret: Optional[str] = Field(
        None,
        description="BGP authentication key",
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


class BgpAuthProfileCreateModel(BgpAuthProfileBaseModel):
    """Model for creating new BGP Authentication Profiles."""

    @model_validator(mode="after")
    def validate_container_type(self) -> "BgpAuthProfileCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            BgpAuthProfileCreateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = ["folder", "snippet", "device"]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class BgpAuthProfileUpdateModel(BgpAuthProfileBaseModel):
    """Model for updating BGP Authentication Profiles."""

    id: UUID = Field(
        ...,
        description="The UUID of the resource",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class BgpAuthProfileResponseModel(BgpAuthProfileBaseModel):
    """Model for BGP Authentication Profile responses."""

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
