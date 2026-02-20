"""BGP Redistribution Profile models for Strata Cloud Manager SDK.

Contains Pydantic models for representing BGP redistribution profile objects and related data.
"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


# --- Nested Models ---


class BgpRedistributionProtocol(BaseModel):
    """Redistribution configuration for a single protocol (static, ospf, or connected).

    NOT mutually exclusive -- all three protocols can coexist under unicast.
    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    enable: Optional[bool] = Field(
        None,
        description="Enable redistribution for this protocol",
    )
    metric: Optional[int] = Field(
        None,
        description="Metric value",
        ge=1,
        le=65535,
    )
    route_map: Optional[str] = Field(
        None,
        description="Route map name to apply",
    )


class BgpRedistributionUnicast(BaseModel):
    """Unicast redistribution containing static, ospf, and connected protocols."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    static: Optional[BgpRedistributionProtocol] = Field(
        None,
        description="Static route redistribution",
    )
    ospf: Optional[BgpRedistributionProtocol] = Field(
        None,
        description="OSPF route redistribution",
    )
    connected: Optional[BgpRedistributionProtocol] = Field(
        None,
        description="Connected route redistribution",
    )


class BgpRedistributionIpv4(BaseModel):
    """IPv4 container for redistribution profiles."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    unicast: Optional[BgpRedistributionUnicast] = Field(
        None,
        description="Unicast redistribution configuration",
    )


# --- Main Models ---


class BgpRedistributionProfileBaseModel(BaseModel):
    """Base model for BGP Redistribution Profiles."""

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
    ipv4: Optional[BgpRedistributionIpv4] = Field(
        None,
        description="IPv4 redistribution configuration",
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


class BgpRedistributionProfileCreateModel(BgpRedistributionProfileBaseModel):
    """Model for creating new BGP Redistribution Profiles."""

    @model_validator(mode="after")
    def validate_container_type(self) -> "BgpRedistributionProfileCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            BgpRedistributionProfileCreateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = ["folder", "snippet", "device"]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class BgpRedistributionProfileUpdateModel(BgpRedistributionProfileBaseModel):
    """Model for updating BGP Redistribution Profiles."""

    id: UUID = Field(
        ...,
        description="The UUID of the resource",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class BgpRedistributionProfileResponseModel(BgpRedistributionProfileBaseModel):
    """Model for BGP Redistribution Profile responses."""

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
