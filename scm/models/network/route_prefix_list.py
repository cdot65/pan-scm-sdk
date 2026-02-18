"""Route Prefix List models for Strata Cloud Manager SDK.

Contains Pydantic models for representing route prefix list objects and related data.
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


# --- Nested Models ---


class RoutePrefixListPrefixEntry(BaseModel):
    """Route prefix list entry with network and optional ge/le."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    network: Optional[str] = Field(
        None,
        description="Network address",
    )
    greater_than_or_equal: Optional[int] = Field(
        None,
        description="Greater than or equal to prefix length",
        ge=0,
        le=32,
    )
    less_than_or_equal: Optional[int] = Field(
        None,
        description="Less than or equal to prefix length",
        ge=0,
        le=32,
    )


class RoutePrefixListPrefix(BaseModel):
    """Route prefix list prefix configuration (oneOf: network 'any' or entry)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    network: Optional[str] = Field(
        None,
        description="Network (use 'any' for any network)",
        pattern=r"^any$",
    )
    entry: Optional[RoutePrefixListPrefixEntry] = Field(
        None,
        description="Prefix entry with network and optional ge/le",
    )

    @model_validator(mode="after")
    def validate_prefix_type(self) -> "RoutePrefixListPrefix":
        """Enforce network and entry are mutually exclusive."""
        if self.network is not None and self.entry is not None:
            raise ValueError("'network' and 'entry' are mutually exclusive.")
        return self


class RoutePrefixListIpv4Entry(BaseModel):
    """IPv4 prefix list entry."""

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
    prefix: Optional[RoutePrefixListPrefix] = Field(
        None,
        description="Prefix configuration",
    )


class RoutePrefixListIpv4(BaseModel):
    """IPv4 prefix list container."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    ipv4_entry: Optional[List[RoutePrefixListIpv4Entry]] = Field(
        None,
        description="IPv4 prefix list entries",
    )


# --- Main Models ---


class RoutePrefixListBaseModel(BaseModel):
    """Base model for Route Prefix Lists."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    name: str = Field(
        ...,
        description="Filter prefix list name",
    )
    description: Optional[str] = Field(
        None,
        description="Description",
    )
    ipv4: Optional[RoutePrefixListIpv4] = Field(
        None,
        description="IPv4 prefix list configuration",
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


class RoutePrefixListUpdateModel(RoutePrefixListBaseModel):
    """Model for updating Route Prefix Lists."""

    id: UUID = Field(
        ...,
        description="The UUID of the resource",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class RoutePrefixListResponseModel(RoutePrefixListBaseModel):
    """Model for Route Prefix List responses."""

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
