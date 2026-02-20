"""QoS Profile models for Strata Cloud Manager SDK.

Contains Pydantic models for representing QoS profile objects and related data.
"""

from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


# --- Main Models ---


class QosProfileBaseModel(BaseModel):
    """Base model for QoS Profiles."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    name: str = Field(
        ...,
        description="Alphanumeric string [0-9a-zA-Z._-]",
        max_length=31,
    )
    aggregate_bandwidth: Optional[Dict[str, Any]] = Field(
        None,
        description="Aggregate bandwidth settings with egress_max and egress_guaranteed",
    )
    class_bandwidth_type: Optional[Dict[str, Any]] = Field(
        None,
        description="Class bandwidth type configuration (mbps or percentage)",
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


class QosProfileCreateModel(QosProfileBaseModel):
    """Model for creating new QoS Profiles."""

    @model_validator(mode="after")
    def validate_container_type(self) -> "QosProfileCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            QosProfileCreateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = ["folder", "snippet", "device"]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class QosProfileUpdateModel(QosProfileBaseModel):
    """Model for updating QoS Profiles."""

    id: UUID = Field(
        ...,
        description="The UUID of the resource",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class QosProfileResponseModel(QosProfileBaseModel):
    """Model for QoS Profile responses."""

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
