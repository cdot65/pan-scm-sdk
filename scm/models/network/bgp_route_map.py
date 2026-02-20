"""BGP Route Map models for Strata Cloud Manager SDK.

Contains Pydantic models for representing BGP route map objects and related data.
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


# --- Nested Models ---


class BgpRouteMapMatchIpv4(BaseModel):
    """IPv4 match criteria for BGP route map entries."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    address: Optional[str] = Field(
        None,
        description="IPv4 address prefix list to match",
    )
    next_hop: Optional[str] = Field(
        None,
        description="IPv4 next-hop prefix list to match",
    )
    route_source: Optional[str] = Field(
        None,
        description="IPv4 route source to match",
    )


class BgpRouteMapMatch(BaseModel):
    """Match criteria for a BGP route map entry."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    as_path_access_list: Optional[str] = Field(
        None,
        description="AS path access list name",
    )
    interface: Optional[str] = Field(
        None,
        description="Interface name to match",
    )
    regular_community: Optional[str] = Field(
        None,
        description="Regular community to match",
    )
    origin: Optional[str] = Field(
        None,
        description="Origin to match",
    )
    large_community: Optional[str] = Field(
        None,
        description="Large community to match",
    )
    tag: Optional[int] = Field(
        None,
        description="Tag value to match",
    )
    extended_community: Optional[str] = Field(
        None,
        description="Extended community to match",
    )
    local_preference: Optional[int] = Field(
        None,
        description="Local preference to match",
    )
    metric: Optional[int] = Field(
        None,
        description="Metric value to match",
    )
    peer: Optional[str] = Field(
        None,
        description="Peer type to match",
        pattern=r"^(local|none)$",
    )
    ipv4: Optional[BgpRouteMapMatchIpv4] = Field(
        None,
        description="IPv4 match criteria",
    )


class BgpRouteMapSetMetric(BaseModel):
    """Metric set action for BGP route map entries.

    NOTE: 'substract' is the actual API spelling (typo in the API). Preserved exactly.
    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    action: Optional[str] = Field(
        None,
        description="Metric action type",
        pattern=r"^(set|add|substract)$",  # API typo: 'substract' not 'subtract'
    )
    value: Optional[int] = Field(
        None,
        description="Metric value",
    )


class BgpRouteMapSetAggregator(BaseModel):
    """Aggregator set configuration for BGP route map entries."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    as_: Optional[int] = Field(
        None,
        alias="as",
        description="Aggregator AS number",
    )
    router_id: Optional[str] = Field(
        None,
        description="Aggregator router ID",
    )


class BgpRouteMapSetIpv4(BaseModel):
    """IPv4 set configuration for BGP route map entries."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    source_address: Optional[str] = Field(
        None,
        description="Source address to set",
    )
    next_hop: Optional[str] = Field(
        None,
        description="Next-hop address to set",
    )


class BgpRouteMapSet(BaseModel):
    """Set actions for a BGP route map entry."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    atomic_aggregate: Optional[bool] = Field(
        None,
        description="Set atomic aggregate",
    )
    local_preference: Optional[int] = Field(
        None,
        description="Local preference value to set",
    )
    tag: Optional[int] = Field(
        None,
        description="Tag value to set",
    )
    metric: Optional[BgpRouteMapSetMetric] = Field(
        None,
        description="Metric action",
    )
    weight: Optional[int] = Field(
        None,
        description="Weight value to set",
    )
    origin: Optional[str] = Field(
        None,
        description="Origin to set",
        pattern=r"^(none|egp|igp|incomplete)$",
    )
    remove_regular_community: Optional[str] = Field(
        None,
        description="Regular community to remove",
    )
    remove_large_community: Optional[str] = Field(
        None,
        description="Large community to remove",
    )
    originator_id: Optional[str] = Field(
        None,
        description="Originator ID to set",
    )
    aggregator: Optional[BgpRouteMapSetAggregator] = Field(
        None,
        description="Aggregator configuration",
    )
    ipv4: Optional[BgpRouteMapSetIpv4] = Field(
        None,
        description="IPv4 set configuration",
    )
    aspath_exclude: Optional[str] = Field(
        None,
        description="AS path to exclude",
    )
    aspath_prepend: Optional[str] = Field(
        None,
        description="AS path to prepend",
    )
    regular_community: Optional[List[str]] = Field(
        None,
        description="Regular communities to set",
    )
    overwrite_regular_community: Optional[bool] = Field(
        None,
        description="Overwrite existing regular communities",
    )
    large_community: Optional[List[str]] = Field(
        None,
        description="Large communities to set",
    )
    overwrite_large_community: Optional[bool] = Field(
        None,
        description="Overwrite existing large communities",
    )


class BgpRouteMapEntry(BaseModel):
    """A single entry in a BGP route map (sequence number + match/set)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: int = Field(
        ...,
        description="Sequence number for the route map entry",
        ge=1,
        le=65535,
    )
    description: Optional[str] = Field(
        None,
        description="Entry description",
    )
    action: Optional[str] = Field(
        None,
        description="Entry action",
        pattern=r"^(permit|deny)$",
    )
    match: Optional[BgpRouteMapMatch] = Field(
        None,
        description="Match criteria",
    )
    set: Optional[BgpRouteMapSet] = Field(
        None,
        description="Set actions",
    )


# --- Main Models ---


class BgpRouteMapBaseModel(BaseModel):
    """Base model for BGP Route Maps."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    name: str = Field(
        ...,
        description="Route map name",
    )
    route_map: Optional[List[BgpRouteMapEntry]] = Field(
        None,
        description="List of route map entries",
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


class BgpRouteMapCreateModel(BgpRouteMapBaseModel):
    """Model for creating new BGP Route Maps."""

    @model_validator(mode="after")
    def validate_container_type(self) -> "BgpRouteMapCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            BgpRouteMapCreateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = ["folder", "snippet", "device"]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class BgpRouteMapUpdateModel(BgpRouteMapBaseModel):
    """Model for updating BGP Route Maps."""

    id: UUID = Field(
        ...,
        description="The UUID of the resource",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class BgpRouteMapResponseModel(BgpRouteMapBaseModel):
    """Model for BGP Route Map responses."""

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
