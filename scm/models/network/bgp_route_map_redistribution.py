"""BGP Route Map Redistribution models for Strata Cloud Manager SDK.

Contains Pydantic models for representing BGP route map redistribution objects and related data.
This is the most complex model in v0.9.0, using 2-level oneOf discrimination:
- Level 1: Source protocol (bgp, ospf, connected_static) - mutually exclusive
- Level 2: Target protocol within each source - mutually exclusive

Each source->target combination has its own route_map array with variant-specific match/set fields.
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


# --- Match Models ---


class BgpRouteMapRedistBgpMatchIpv4(BaseModel):
    """IPv4 match criteria for BGP source redistribution."""

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


class BgpRouteMapRedistBgpMatch(BaseModel):
    """Match criteria for BGP source redistribution entries."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    as_path_access_list: Optional[str] = Field(
        None,
        description="AS path access list name",
    )
    regular_community: Optional[str] = Field(
        None,
        description="Regular community to match",
    )
    large_community: Optional[str] = Field(
        None,
        description="Large community to match",
    )
    extended_community: Optional[str] = Field(
        None,
        description="Extended community to match",
    )
    interface: Optional[str] = Field(
        None,
        description="Interface to match",
    )
    tag: Optional[int] = Field(
        None,
        description="Tag value to match",
    )
    local_preference: Optional[int] = Field(
        None,
        description="Local preference to match",
    )
    metric: Optional[int] = Field(
        None,
        description="Metric to match",
    )
    origin: Optional[str] = Field(
        None,
        description="Origin to match",
    )
    peer: Optional[str] = Field(
        None,
        description="Peer type to match",
        pattern=r"^(local|none)$",
    )
    ipv4: Optional[BgpRouteMapRedistBgpMatchIpv4] = Field(
        None,
        description="IPv4 match criteria",
    )


class BgpRouteMapRedistSimpleMatchIpv4(BaseModel):
    """IPv4 match criteria for OSPF/connected-static source redistribution."""

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


class BgpRouteMapRedistSimpleMatch(BaseModel):
    """Match criteria for OSPF/connected-static source redistribution entries."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    interface: Optional[str] = Field(
        None,
        description="Interface to match",
    )
    metric: Optional[int] = Field(
        None,
        description="Metric to match",
    )
    tag: Optional[int] = Field(
        None,
        description="Tag to match",
    )
    ipv4: Optional[BgpRouteMapRedistSimpleMatchIpv4] = Field(
        None,
        description="IPv4 match criteria",
    )


# --- Set Models ---


class BgpRouteMapRedistSetMetric(BaseModel):
    """Metric set action.

    NOTE: 'substract' is the actual API spelling (typo). Preserved exactly.
    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    action: Optional[str] = Field(
        None,
        description="Metric action type",
        pattern=r"^(set|add|substract)$",  # API typo preserved
    )
    value: Optional[int] = Field(
        None,
        description="Metric value",
    )


class BgpRouteMapRedistSetAggregator(BaseModel):
    """Aggregator set configuration."""

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


class BgpRouteMapRedistSetIpv4(BaseModel):
    """IPv4 set configuration."""

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
        description="Next-hop to set",
    )


class BgpRouteMapRedistSetToBgp(BaseModel):
    """Set actions when target is BGP (full BGP set fields)."""

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
        description="Local preference to set",
    )
    tag: Optional[int] = Field(
        None,
        description="Tag to set",
    )
    metric: Optional[BgpRouteMapRedistSetMetric] = Field(
        None,
        description="Metric action",
    )
    weight: Optional[int] = Field(
        None,
        description="Weight to set",
    )
    origin: Optional[str] = Field(
        None,
        description="Origin to set",
        pattern=r"^(none|egp|igp|incomplete)$",
    )
    remove_regular_community: Optional[str] = Field(
        None,
        description="Community to remove",
    )
    remove_large_community: Optional[str] = Field(
        None,
        description="Large community to remove",
    )
    originator_id: Optional[str] = Field(
        None,
        description="Originator ID to set",
    )
    aggregator: Optional[BgpRouteMapRedistSetAggregator] = Field(
        None,
        description="Aggregator config",
    )
    ipv4: Optional[BgpRouteMapRedistSetIpv4] = Field(
        None,
        description="IPv4 set config",
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
        description="Communities to set",
    )
    overwrite_regular_community: Optional[bool] = Field(
        None,
        description="Overwrite communities",
    )
    large_community: Optional[List[str]] = Field(
        None,
        description="Large communities to set",
    )
    overwrite_large_community: Optional[bool] = Field(
        None,
        description="Overwrite large communities",
    )


class BgpRouteMapRedistSetToOspf(BaseModel):
    """Set actions when target is OSPF (metric, metric_type, tag only)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    metric: Optional[BgpRouteMapRedistSetMetric] = Field(
        None,
        description="Metric action",
    )
    metric_type: Optional[str] = Field(
        None,
        description="OSPF metric type",
    )
    tag: Optional[int] = Field(
        None,
        description="Tag to set",
    )


class BgpRouteMapRedistSetToRib(BaseModel):
    """Set actions when target is RIB (source_address only)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    ipv4: Optional[BgpRouteMapRedistSetIpv4] = Field(
        None,
        description="IPv4 set (source_address)",
    )


# --- Route Map Entry Models (7 Variants) ---


# BGP Source Entries


class BgpRouteMapRedistBgpToOspfEntry(BaseModel):
    """Route map entry for bgp->ospf redistribution."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: int = Field(
        ...,
        description="Sequence number",
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
    match: Optional[BgpRouteMapRedistBgpMatch] = Field(
        None,
        description="BGP match criteria",
    )
    set: Optional[BgpRouteMapRedistSetToOspf] = Field(
        None,
        description="OSPF set actions",
    )


class BgpRouteMapRedistBgpToRibEntry(BaseModel):
    """Route map entry for bgp->rib redistribution."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: int = Field(
        ...,
        description="Sequence number",
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
    match: Optional[BgpRouteMapRedistBgpMatch] = Field(
        None,
        description="BGP match criteria",
    )
    set: Optional[BgpRouteMapRedistSetToRib] = Field(
        None,
        description="RIB set actions",
    )


# OSPF Source Entries


class BgpRouteMapRedistOspfToBgpEntry(BaseModel):
    """Route map entry for ospf->bgp redistribution."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: int = Field(
        ...,
        description="Sequence number",
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
    match: Optional[BgpRouteMapRedistSimpleMatch] = Field(
        None,
        description="Simple match criteria",
    )
    set: Optional[BgpRouteMapRedistSetToBgp] = Field(
        None,
        description="BGP set actions",
    )


class BgpRouteMapRedistOspfToRibEntry(BaseModel):
    """Route map entry for ospf->rib redistribution."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: int = Field(
        ...,
        description="Sequence number",
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
    match: Optional[BgpRouteMapRedistSimpleMatch] = Field(
        None,
        description="Simple match criteria",
    )
    set: Optional[BgpRouteMapRedistSetToRib] = Field(
        None,
        description="RIB set actions",
    )


# Connected/Static Source Entries


class BgpRouteMapRedistConnStaticToBgpEntry(BaseModel):
    """Route map entry for connected_static->bgp redistribution."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: int = Field(
        ...,
        description="Sequence number",
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
    match: Optional[BgpRouteMapRedistSimpleMatch] = Field(
        None,
        description="Simple match criteria",
    )
    set: Optional[BgpRouteMapRedistSetToBgp] = Field(
        None,
        description="BGP set actions",
    )


class BgpRouteMapRedistConnStaticToOspfEntry(BaseModel):
    """Route map entry for connected_static->ospf redistribution."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: int = Field(
        ...,
        description="Sequence number",
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
    match: Optional[BgpRouteMapRedistSimpleMatch] = Field(
        None,
        description="Simple match criteria",
    )
    set: Optional[BgpRouteMapRedistSetToOspf] = Field(
        None,
        description="OSPF set actions",
    )


class BgpRouteMapRedistConnStaticToRibEntry(BaseModel):
    """Route map entry for connected_static->rib redistribution."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: int = Field(
        ...,
        description="Sequence number",
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
    match: Optional[BgpRouteMapRedistSimpleMatch] = Field(
        None,
        description="Simple match criteria",
    )
    set: Optional[BgpRouteMapRedistSetToRib] = Field(
        None,
        description="RIB set actions",
    )


# --- Target Container Models (7 Variants) ---


class BgpRouteMapRedistBgpToOspf(BaseModel):
    """Container for bgp->ospf redistribution route maps."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    route_map: Optional[List[BgpRouteMapRedistBgpToOspfEntry]] = Field(
        None,
        description="Route map entries",
    )


class BgpRouteMapRedistBgpToRib(BaseModel):
    """Container for bgp->rib redistribution route maps."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    route_map: Optional[List[BgpRouteMapRedistBgpToRibEntry]] = Field(
        None,
        description="Route map entries",
    )


class BgpRouteMapRedistOspfToBgp(BaseModel):
    """Container for ospf->bgp redistribution route maps."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    route_map: Optional[List[BgpRouteMapRedistOspfToBgpEntry]] = Field(
        None,
        description="Route map entries",
    )


class BgpRouteMapRedistOspfToRib(BaseModel):
    """Container for ospf->rib redistribution route maps."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    route_map: Optional[List[BgpRouteMapRedistOspfToRibEntry]] = Field(
        None,
        description="Route map entries",
    )


class BgpRouteMapRedistConnStaticToBgp(BaseModel):
    """Container for connected_static->bgp redistribution route maps."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    route_map: Optional[List[BgpRouteMapRedistConnStaticToBgpEntry]] = Field(
        None,
        description="Route map entries",
    )


class BgpRouteMapRedistConnStaticToOspf(BaseModel):
    """Container for connected_static->ospf redistribution route maps."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    route_map: Optional[List[BgpRouteMapRedistConnStaticToOspfEntry]] = Field(
        None,
        description="Route map entries",
    )


class BgpRouteMapRedistConnStaticToRib(BaseModel):
    """Container for connected_static->rib redistribution route maps."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    route_map: Optional[List[BgpRouteMapRedistConnStaticToRibEntry]] = Field(
        None,
        description="Route map entries",
    )


# --- Source Protocol Models (Level 1 Discrimination) ---


class BgpRouteMapRedistBgpSource(BaseModel):
    """BGP source protocol with targets: ospf or rib (mutually exclusive)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    ospf: Optional[BgpRouteMapRedistBgpToOspf] = Field(
        None,
        description="Redistribute BGP routes to OSPF",
    )
    rib: Optional[BgpRouteMapRedistBgpToRib] = Field(
        None,
        description="Redistribute BGP routes to RIB",
    )

    @model_validator(mode="after")
    def validate_target_type(self) -> "BgpRouteMapRedistBgpSource":
        """Enforce exactly one target protocol is set."""
        targets = [self.ospf, self.rib]
        provided = [t for t in targets if t is not None]
        if len(provided) > 1:
            raise ValueError("Only one of 'ospf' or 'rib' can be set for BGP source.")
        return self


class BgpRouteMapRedistOspfSource(BaseModel):
    """OSPF source protocol with targets: bgp or rib (mutually exclusive)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    bgp: Optional[BgpRouteMapRedistOspfToBgp] = Field(
        None,
        description="Redistribute OSPF routes to BGP",
    )
    rib: Optional[BgpRouteMapRedistOspfToRib] = Field(
        None,
        description="Redistribute OSPF routes to RIB",
    )

    @model_validator(mode="after")
    def validate_target_type(self) -> "BgpRouteMapRedistOspfSource":
        """Enforce exactly one target protocol is set."""
        targets = [self.bgp, self.rib]
        provided = [t for t in targets if t is not None]
        if len(provided) > 1:
            raise ValueError("Only one of 'bgp' or 'rib' can be set for OSPF source.")
        return self


class BgpRouteMapRedistConnectedStaticSource(BaseModel):
    """Connected/Static source protocol with targets: bgp, ospf, or rib (mutually exclusive)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    bgp: Optional[BgpRouteMapRedistConnStaticToBgp] = Field(
        None,
        description="Redistribute connected/static routes to BGP",
    )
    ospf: Optional[BgpRouteMapRedistConnStaticToOspf] = Field(
        None,
        description="Redistribute connected/static routes to OSPF",
    )
    rib: Optional[BgpRouteMapRedistConnStaticToRib] = Field(
        None,
        description="Redistribute connected/static routes to RIB",
    )

    @model_validator(mode="after")
    def validate_target_type(self) -> "BgpRouteMapRedistConnectedStaticSource":
        """Enforce exactly one target protocol is set."""
        targets = [self.bgp, self.ospf, self.rib]
        provided = [t for t in targets if t is not None]
        if len(provided) > 1:
            raise ValueError(
                "Only one of 'bgp', 'ospf', or 'rib' can be set for connected_static source."
            )
        return self


# --- Main Models ---


class BgpRouteMapRedistributionBaseModel(BaseModel):
    """Base model for BGP Route Map Redistributions.

    Uses 2-level oneOf discrimination:
    - Level 1: source protocol (bgp, ospf, connected_static) - mutually exclusive
    - Level 2: target protocol within each source - mutually exclusive
    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    name: str = Field(
        ...,
        description="Redistribution name",
    )
    bgp: Optional[BgpRouteMapRedistBgpSource] = Field(
        None,
        description="BGP as source protocol",
    )
    ospf: Optional[BgpRouteMapRedistOspfSource] = Field(
        None,
        description="OSPF as source protocol",
    )
    connected_static: Optional[BgpRouteMapRedistConnectedStaticSource] = Field(
        None,
        description="Connected/Static as source protocol",
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
    def validate_source_type(self) -> "BgpRouteMapRedistributionBaseModel":
        """Enforce at most one source protocol is set (Level 1 oneOf)."""
        sources = [self.bgp, self.ospf, self.connected_static]
        provided = [s for s in sources if s is not None]
        if len(provided) > 1:
            raise ValueError(
                "At most one source protocol can be set: 'bgp', 'ospf', or 'connected_static'."
            )
        return self


class BgpRouteMapRedistributionCreateModel(BgpRouteMapRedistributionBaseModel):
    """Model for creating new BGP Route Map Redistributions."""

    @model_validator(mode="after")
    def validate_container_type(self) -> "BgpRouteMapRedistributionCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            BgpRouteMapRedistributionCreateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = ["folder", "snippet", "device"]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class BgpRouteMapRedistributionUpdateModel(BgpRouteMapRedistributionBaseModel):
    """Model for updating BGP Route Map Redistributions."""

    id: UUID = Field(
        ...,
        description="The UUID of the resource",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class BgpRouteMapRedistributionResponseModel(BgpRouteMapRedistributionBaseModel):
    """Model for BGP Route Map Redistribution responses."""

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
