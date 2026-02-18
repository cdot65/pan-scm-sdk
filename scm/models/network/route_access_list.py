"""Route Access List models for Strata Cloud Manager SDK.

Contains Pydantic models for representing route access list objects and related data.
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# --- Nested Models ---


class RouteAccessListSourceAddress(BaseModel):
    """Route access list source address (supports simple address or address+wildcard)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    address: Optional[str] = Field(
        None,
        description="Source IP address",
    )
    wildcard: Optional[str] = Field(
        None,
        description="Source IP wildcard mask",
    )


class RouteAccessListDestinationAddress(BaseModel):
    """Route access list destination address (supports simple address or address+wildcard)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    address: Optional[str] = Field(
        None,
        description="Destination IP address",
    )
    wildcard: Optional[str] = Field(
        None,
        description="Destination IP wildcard mask",
    )


class RouteAccessListIpv4Entry(BaseModel):
    """IPv4 access list entry."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: Optional[int] = Field(
        None,
        description="Sequence number",
        ge=1,
        le=65535,
    )
    action: Optional[str] = Field(
        None,
        description="Action (deny or permit)",
        pattern=r"^(deny|permit)$",
    )
    source_address: Optional[RouteAccessListSourceAddress] = Field(
        None,
        description="Source address configuration",
    )
    destination_address: Optional[RouteAccessListDestinationAddress] = Field(
        None,
        description="Destination address configuration",
    )


class RouteAccessListIpv4(BaseModel):
    """IPv4 access list container."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    ipv4_entry: Optional[List[RouteAccessListIpv4Entry]] = Field(
        None,
        description="IPv4 access list entries",
    )


class RouteAccessListType(BaseModel):
    """Route access list type container."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    ipv4: Optional[RouteAccessListIpv4] = Field(
        None,
        description="IPv4 access list",
    )


# --- Main Models ---


class RouteAccessListBaseModel(BaseModel):
    """Base model for Route Access Lists."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    name: str = Field(
        ...,
        description="Route access list name",
    )
    description: Optional[str] = Field(
        None,
        description="Description",
    )
    type: Optional[RouteAccessListType] = Field(
        None,
        description="Access list type configuration",
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


class RouteAccessListUpdateModel(RouteAccessListBaseModel):
    """Model for updating Route Access Lists."""

    id: UUID = Field(
        ...,
        description="The UUID of the resource",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class RouteAccessListResponseModel(RouteAccessListBaseModel):
    """Model for Route Access List responses."""

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
