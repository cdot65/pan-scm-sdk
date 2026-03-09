"""Auto Tag Actions models for Strata Cloud Manager SDK.

Contains Pydantic models for representing auto tag action objects and related data.
"""

# scm/models/objects/auto_tag_actions.py

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TaggingModel(BaseModel):
    """Model for tagging action settings."""

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )

    action: Optional[str] = Field(
        None,
        description="Tagging action: 'add-tag' or 'remove-tag'",
    )
    target: Optional[str] = Field(
        None,
        description="Target: 'source-address' or 'destination-address'",
    )
    tags: Optional[List[str]] = Field(
        None,
        description="List of tags to apply or remove",
    )
    timeout: Optional[int] = Field(
        None,
        description="Duration in seconds for tag application",
    )


class ActionTypeModel(BaseModel):
    """Model for action type containing tagging settings."""

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )

    tagging: Optional[TaggingModel] = Field(
        None,
        description="Tagging configuration for this action",
    )


class ActionModel(BaseModel):
    """Model for an individual action within an auto tag action."""

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )

    name: str = Field(
        ...,
        description="The name of the action",
    )
    type: Optional[ActionTypeModel] = Field(
        None,
        description="The type configuration for this action",
    )


class AutoTagActionBaseModel(BaseModel):
    """Base model for Auto Tag Action objects."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    name: str = Field(
        ...,
        max_length=63,
        description="The name of the auto tag action",
        pattern=r"^[a-zA-Z0-9_ \.\-]+$",
    )
    description: Optional[str] = Field(
        None,
        max_length=1023,
        description="The description of the auto tag action",
    )
    actions: Optional[List[ActionModel]] = Field(
        None,
        description="List of actions to perform",
    )
    filter: Optional[str] = Field(
        None,
        description="Log filter string that triggers the action",
    )
    log_type: Optional[str] = Field(
        None,
        description="The type of log that triggers this action",
    )
    quarantine: Optional[bool] = Field(
        None,
        description="Whether to quarantine the device",
    )
    send_to_panorama: Optional[bool] = Field(
        None,
        description="Whether to send the tag action to Panorama",
    )

    # Container Types
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


class AutoTagActionCreateModel(AutoTagActionBaseModel):
    """Model for creating a new Auto Tag Action."""

    @model_validator(mode="after")
    def validate_container_type(self) -> "AutoTagActionCreateModel":
        """Ensure exactly one container field is set."""
        container_fields = ["folder", "snippet", "device"]
        provided = [f for f in container_fields if getattr(self, f) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class AutoTagActionUpdateModel(AutoTagActionBaseModel):
    """Model for updating an existing Auto Tag Action."""

    id: Optional[UUID] = Field(
        None,
        description="The UUID of the auto tag action",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class AutoTagActionResponseModel(AutoTagActionBaseModel):
    """Model for Auto Tag Action responses."""

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    id: Optional[UUID] = Field(
        None,
        description="The UUID of the auto tag action",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
