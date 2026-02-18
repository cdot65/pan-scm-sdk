"""BGP Address Family Profile models for Strata Cloud Manager SDK.

Contains Pydantic models for representing BGP address family profile objects and related data.
"""

from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


# --- Nested Models ---


class BgpAddressFamilyAddPath(BaseModel):
    """BGP address family add-path configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    tx_all_paths: Optional[bool] = Field(
        None,
        description="Advertise all paths to peer",
    )
    tx_bestpath_per_AS: Optional[bool] = Field(
        None,
        description="Advertise bestpath per neighboring AS",
    )


class BgpAddressFamilyAllowasIn(BaseModel):
    """BGP address family allowas-in configuration (oneOf: origin or occurrence)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    origin: Optional[Dict[str, Any]] = Field(
        None,
        description="Allow origin AS in path",
    )
    occurrence: Optional[int] = Field(
        None,
        description="Number of times own AS can appear in AS_PATH",
        ge=1,
        le=10,
    )

    @model_validator(mode="after")
    def validate_allowas_in_type(self) -> "BgpAddressFamilyAllowasIn":
        """Enforce origin and occurrence are mutually exclusive."""
        if self.origin is not None and self.occurrence is not None:
            raise ValueError("'origin' and 'occurrence' are mutually exclusive.")
        return self


class BgpAddressFamilyMaximumPrefixRestart(BaseModel):
    """Maximum prefix restart configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    interval: Optional[int] = Field(
        None,
        description="Restart interval",
        ge=1,
        le=65535,
    )


class BgpAddressFamilyMaximumPrefixAction(BaseModel):
    """Maximum prefix action (oneOf: warning_only or restart)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    warning_only: Optional[Dict[str, Any]] = Field(
        None,
        description="Warning only action",
    )
    restart: Optional[BgpAddressFamilyMaximumPrefixRestart] = Field(
        None,
        description="Restart action",
    )

    @model_validator(mode="after")
    def validate_action_type(self) -> "BgpAddressFamilyMaximumPrefixAction":
        """Enforce warning_only and restart are mutually exclusive."""
        if self.warning_only is not None and self.restart is not None:
            raise ValueError("'warning_only' and 'restart' are mutually exclusive.")
        return self


class BgpAddressFamilyMaximumPrefix(BaseModel):
    """BGP address family maximum prefix configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    num_prefixes: Optional[int] = Field(
        None,
        description="Maximum number of prefixes",
        ge=1,
        le=4294967295,
    )
    threshold: Optional[int] = Field(
        None,
        description="Threshold percentage",
        ge=1,
        le=100,
    )
    action: Optional[BgpAddressFamilyMaximumPrefixAction] = Field(
        None,
        description="Action on limit",
    )


class BgpAddressFamilyNextHop(BaseModel):
    """BGP address family next-hop configuration (oneOf: self or self_force)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    self_: Optional[Dict[str, Any]] = Field(
        None,
        alias="self",
        description="Set next-hop to self",
    )
    self_force: Optional[Dict[str, Any]] = Field(
        None,
        description="Force next-hop to self",
    )

    @model_validator(mode="after")
    def validate_next_hop_type(self) -> "BgpAddressFamilyNextHop":
        """Enforce self and self_force are mutually exclusive."""
        if self.self_ is not None and self.self_force is not None:
            raise ValueError("'self' and 'self_force' are mutually exclusive.")
        return self


class BgpAddressFamilyRemovePrivateAS(BaseModel):
    """BGP address family remove-private-AS configuration (oneOf: all or replace_AS)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    all: Optional[Dict[str, Any]] = Field(
        None,
        description="Remove all private AS numbers",
    )
    replace_AS: Optional[Dict[str, Any]] = Field(
        None,
        description="Replace private AS numbers",
    )

    @model_validator(mode="after")
    def validate_remove_type(self) -> "BgpAddressFamilyRemovePrivateAS":
        """Enforce all and replace_AS are mutually exclusive."""
        if self.all is not None and self.replace_AS is not None:
            raise ValueError("'all' and 'replace_AS' are mutually exclusive.")
        return self


class BgpAddressFamilySendCommunity(BaseModel):
    """BGP address family send-community configuration (oneOf: all, both, extended, large, standard)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    all: Optional[Dict[str, Any]] = Field(
        None,
        description="Send all communities",
    )
    both: Optional[Dict[str, Any]] = Field(
        None,
        description="Send both standard and extended",
    )
    extended: Optional[Dict[str, Any]] = Field(
        None,
        description="Send extended communities",
    )
    large: Optional[Dict[str, Any]] = Field(
        None,
        description="Send large communities",
    )
    standard: Optional[Dict[str, Any]] = Field(
        None,
        description="Send standard communities",
    )

    @model_validator(mode="after")
    def validate_send_community_type(self) -> "BgpAddressFamilySendCommunity":
        """Enforce at most one send community type is set."""
        fields = [self.all, self.both, self.extended, self.large, self.standard]
        provided = [f for f in fields if f is not None]
        if len(provided) > 1:
            raise ValueError(
                "At most one send community type can be set: all, both, extended, large, or standard."
            )
        return self


class BgpAddressFamilyOrf(BaseModel):
    """BGP address family ORF configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    orf_prefix_list: Optional[str] = Field(
        None,
        description="ORF prefix list mode",
        pattern=r"^(none|both|receive|send)$",
    )


class BgpAddressFamily(BaseModel):
    """Core BGP address family configuration (reused for unicast and multicast)."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    enable: Optional[bool] = Field(
        None,
        description="Enable address family",
    )
    soft_reconfig_with_stored_info: Optional[bool] = Field(
        None,
        description="Soft reconfiguration with stored routes",
    )
    add_path: Optional[BgpAddressFamilyAddPath] = Field(
        None,
        description="Add-path configuration",
    )
    as_override: Optional[bool] = Field(
        None,
        description="Override ASNs in outbound updates if AS-Path equals Remote-AS",
    )
    route_reflector_client: Optional[bool] = Field(
        None,
        description="Route reflector client",
    )
    default_originate: Optional[bool] = Field(
        None,
        description="Originate default route",
    )
    default_originate_map: Optional[str] = Field(
        None,
        description="Default originate route map",
    )
    allowas_in: Optional[BgpAddressFamilyAllowasIn] = Field(
        None,
        description="Allow-AS-in configuration",
    )
    maximum_prefix: Optional[BgpAddressFamilyMaximumPrefix] = Field(
        None,
        description="Maximum prefix configuration",
    )
    next_hop: Optional[BgpAddressFamilyNextHop] = Field(
        None,
        description="Next-hop configuration",
    )
    remove_private_AS: Optional[BgpAddressFamilyRemovePrivateAS] = Field(
        None,
        description="Remove private AS configuration",
    )
    send_community: Optional[BgpAddressFamilySendCommunity] = Field(
        None,
        description="Send community configuration",
    )
    orf: Optional[BgpAddressFamilyOrf] = Field(
        None,
        description="ORF configuration",
    )


class BgpAddressFamilyProfileIpv4UnicastMulticast(BaseModel):
    """IPv4 unicast/multicast container inside the ipv4 wrapper."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    unicast: Optional[BgpAddressFamily] = Field(
        None,
        description="Unicast address family",
    )
    multicast: Optional[BgpAddressFamily] = Field(
        None,
        description="Multicast address family",
    )


# --- Main Models ---


class BgpAddressFamilyProfileBaseModel(BaseModel):
    """Base model for BGP Address Family Profiles."""

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
    ipv4: Optional[BgpAddressFamilyProfileIpv4UnicastMulticast] = Field(
        None,
        description="IPv4 address family configuration",
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


class BgpAddressFamilyProfileUpdateModel(BgpAddressFamilyProfileBaseModel):
    """Model for updating BGP Address Family Profiles."""

    id: UUID = Field(
        ...,
        description="The UUID of the resource",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class BgpAddressFamilyProfileResponseModel(BgpAddressFamilyProfileBaseModel):
    """Model for BGP Address Family Profile responses."""

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
