"""BGP Filtering Profile models for Strata Cloud Manager SDK.

Contains Pydantic models for representing BGP filtering profile objects and related data.
"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


# --- Nested Models ---


class BgpFilterList(BaseModel):
    """Filter list with inbound/outbound string references."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    inbound: Optional[str] = Field(
        None,
        description="Inbound filter list name",
    )
    outbound: Optional[str] = Field(
        None,
        description="Outbound filter list name",
    )


class BgpNetworkFilters(BaseModel):
    """Network filters with distribute_list and prefix_list options."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    distribute_list: Optional[str] = Field(
        None,
        description="Distribute list name",
    )
    prefix_list: Optional[str] = Field(
        None,
        description="Prefix list name",
    )


class BgpRouteMaps(BaseModel):
    """Route maps with inbound/outbound string references."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    inbound: Optional[str] = Field(
        None,
        description="Inbound route map name",
    )
    outbound: Optional[str] = Field(
        None,
        description="Outbound route map name",
    )


class BgpConditionalAdvertisementCondition(BaseModel):
    """Condition for conditional advertisement (exist/non_exist)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    advertise_map: Optional[str] = Field(
        None,
        description="Advertise map name",
    )


class BgpConditionalAdvertisement(BaseModel):
    """Conditional advertisement with exist/non_exist conditions."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    exist: Optional[BgpConditionalAdvertisementCondition] = Field(
        None,
        description="Exist condition",
    )
    non_exist: Optional[BgpConditionalAdvertisementCondition] = Field(
        None,
        description="Non-exist condition",
    )


class BgpFilter(BaseModel):
    """Shared BGP filter schema used by unicast directly."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    filter_list: Optional[BgpFilterList] = Field(
        None,
        description="Filter list configuration",
    )
    inbound_network_filters: Optional[BgpNetworkFilters] = Field(
        None,
        description="Inbound network filters",
    )
    outbound_network_filters: Optional[BgpNetworkFilters] = Field(
        None,
        description="Outbound network filters",
    )
    route_maps: Optional[BgpRouteMaps] = Field(
        None,
        description="Route maps configuration",
    )
    conditional_advertisement: Optional[BgpConditionalAdvertisement] = Field(
        None,
        description="Conditional advertisement configuration",
    )
    unsuppress_map: Optional[str] = Field(
        None,
        description="Unsuppress map name",
    )


class BgpFilteringProfileMulticast(BaseModel):
    """IPv4 multicast filtering (oneOf: inherit boolean OR full bgp-filter).

    When inherit=True, no other filter fields should be set.
    When filter fields are set, inherit should not be set.
    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    inherit: Optional[bool] = Field(
        None,
        description="Inherit filtering from unicast",
    )
    filter_list: Optional[BgpFilterList] = Field(
        None,
        description="Filter list configuration",
    )
    inbound_network_filters: Optional[BgpNetworkFilters] = Field(
        None,
        description="Inbound network filters",
    )
    outbound_network_filters: Optional[BgpNetworkFilters] = Field(
        None,
        description="Outbound network filters",
    )
    route_maps: Optional[BgpRouteMaps] = Field(
        None,
        description="Route maps configuration",
    )
    conditional_advertisement: Optional[BgpConditionalAdvertisement] = Field(
        None,
        description="Conditional advertisement configuration",
    )
    unsuppress_map: Optional[str] = Field(
        None,
        description="Unsuppress map name",
    )

    @model_validator(mode="after")
    def validate_multicast_type(self) -> "BgpFilteringProfileMulticast":
        """Enforce inherit and filter fields are mutually exclusive."""
        filter_fields = [
            self.filter_list,
            self.inbound_network_filters,
            self.outbound_network_filters,
            self.route_maps,
            self.conditional_advertisement,
            self.unsuppress_map,
        ]
        has_filters = any(f is not None for f in filter_fields)
        if self.inherit is not None and has_filters:
            raise ValueError("'inherit' and filter fields are mutually exclusive in multicast.")
        return self


class BgpFilteringProfileIpv4(BaseModel):
    """IPv4 container with unicast and multicast."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    unicast: Optional[BgpFilter] = Field(
        None,
        description="Unicast filtering",
    )
    multicast: Optional[BgpFilteringProfileMulticast] = Field(
        None,
        description="Multicast filtering",
    )


# --- Main Models ---


class BgpFilteringProfileBaseModel(BaseModel):
    """Base model for BGP Filtering Profiles."""

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
    ipv4: Optional[BgpFilteringProfileIpv4] = Field(
        None,
        description="IPv4 filtering configuration",
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


class BgpFilteringProfileCreateModel(BgpFilteringProfileBaseModel):
    """Model for creating new BGP Filtering Profiles."""

    @model_validator(mode="after")
    def validate_container_type(self) -> "BgpFilteringProfileCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            BgpFilteringProfileCreateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = ["folder", "snippet", "device"]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class BgpFilteringProfileUpdateModel(BgpFilteringProfileBaseModel):
    """Model for updating BGP Filtering Profiles."""

    id: UUID = Field(
        ...,
        description="The UUID of the resource",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class BgpFilteringProfileResponseModel(BgpFilteringProfileBaseModel):
    """Model for BGP Filtering Profile responses."""

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
