"""Models for Loopback Interface in Palo Alto Networks' Strata Cloud Manager.

This module defines the Pydantic models used for creating, updating, and
representing Loopback Interface resources in the Strata Cloud Manager.
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from scm.models.network._interface_common import Ipv6Config, StaticIpEntry


class LoopbackInterfaceBaseModel(BaseModel):
    """Base model for Loopback Interface resources containing common fields."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(
        ...,
        pattern=r"^\$[a-zA-Z\d\-_. ]+$",
        description="Loopback interface name (variable format)",
    )
    default_value: Optional[str] = Field(
        default=None,
        pattern=r"^loopback\.([1-9][0-9]{0,3})$",
        description="Default interface assignment (e.g., loopback.123)",
    )
    comment: Optional[str] = Field(
        default=None,
        description="Interface description/comment",
    )
    mtu: Optional[int] = Field(
        default=None,
        ge=576,
        le=9216,
        description="Maximum transmission unit (MTU)",
    )
    interface_management_profile: Optional[str] = Field(
        default=None,
        description="Interface management profile name",
    )
    ip: Optional[List[StaticIpEntry]] = Field(
        default=None,
        description="List of IPv4 addresses",
    )
    ipv6: Optional[Ipv6Config] = Field(
        default=None,
        description="IPv6 configuration",
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


class LoopbackInterfaceCreateModel(LoopbackInterfaceBaseModel):
    """Model for creating new Loopback Interface resources."""

    @model_validator(mode="after")
    def validate_container_type(self) -> "LoopbackInterfaceCreateModel":
        """Ensure exactly one container field is set.

        Returns:
            LoopbackInterfaceCreateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = ["folder", "snippet", "device"]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class LoopbackInterfaceUpdateModel(LoopbackInterfaceBaseModel):
    """Model for updating existing Loopback Interface resources."""

    id: UUID = Field(
        ...,
        description="The UUID of the loopback interface",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class LoopbackInterfaceResponseModel(LoopbackInterfaceBaseModel):
    """Model for Loopback Interface responses from the API."""

    id: UUID = Field(
        ...,
        description="The UUID of the loopback interface",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
