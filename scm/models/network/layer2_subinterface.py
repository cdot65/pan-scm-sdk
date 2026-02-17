"""Models for Layer2 Subinterface in Palo Alto Networks' Strata Cloud Manager.

This module defines the Pydantic models used for creating, updating, and
representing Layer2 Subinterface resources in the Strata Cloud Manager.
"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Layer2SubinterfaceBaseModel(BaseModel):
    """Base model for Layer2 Subinterface resources containing common fields."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(
        ...,
        description="Layer2 subinterface name (e.g., ethernet1/1.100)",
    )
    vlan_tag: str = Field(
        ...,
        pattern=r"^([1-9]\d{0,2}|[1-3]\d{3}|40[0-8]\d|409[0-6])$",
        description="VLAN tag (1-4096)",
    )
    parent_interface: Optional[str] = Field(
        default=None,
        description="Parent interface name",
    )
    comment: Optional[str] = Field(
        default=None,
        description="Interface description/comment",
    )

    # Container fields
    folder: Optional[str] = Field(
        default=None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The folder in which the resource is defined",
    )
    snippet: Optional[str] = Field(
        default=None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The snippet in which the resource is defined",
    )
    device: Optional[str] = Field(
        default=None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The device in which the resource is defined",
    )


class Layer2SubinterfaceCreateModel(Layer2SubinterfaceBaseModel):
    """Model for creating new Layer2 Subinterface resources."""

    @model_validator(mode="after")
    def validate_container_type(self) -> "Layer2SubinterfaceCreateModel":
        """Ensure exactly one container field is set.

        Returns:
            Layer2SubinterfaceCreateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = ["folder", "snippet", "device"]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class Layer2SubinterfaceUpdateModel(Layer2SubinterfaceBaseModel):
    """Model for updating existing Layer2 Subinterface resources."""

    id: UUID = Field(
        ...,
        description="The UUID of the layer2 subinterface",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class Layer2SubinterfaceResponseModel(Layer2SubinterfaceBaseModel):
    """Model for Layer2 Subinterface responses from the API."""

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
    )

    id: UUID = Field(
        ...,
        description="The UUID of the layer2 subinterface",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
