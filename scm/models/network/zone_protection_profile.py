"""Zone Protection Profile models for Strata Cloud Manager SDK.

Contains Pydantic models for representing zone protection profile objects and related data.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


# --- Flood Protection Models ---


class FloodRed(BaseModel):
    """Random Early Detection (RED) configuration for flood protection."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    alarm_rate: Optional[int] = Field(
        None,
        description="Alarm rate threshold",
        ge=0,
        le=2000000,
    )
    activate_rate: Optional[int] = Field(
        None,
        description="Activate rate threshold",
        ge=0,
        le=2000000,
    )
    maximal_rate: Optional[int] = Field(
        None,
        description="Maximal rate threshold",
        ge=0,
        le=2000000,
    )


class FloodSynCookies(BaseModel):
    """SYN Cookies configuration for TCP SYN flood protection."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    alarm_rate: Optional[int] = Field(
        None,
        description="Alarm rate threshold",
        ge=0,
        le=2000000,
    )
    activate_rate: Optional[int] = Field(
        None,
        description="Activate rate threshold",
        ge=0,
        le=2000000,
    )
    maximal_rate: Optional[int] = Field(
        None,
        description="Maximal rate threshold",
        ge=0,
        le=2000000,
    )


class TcpSynFlood(BaseModel):
    """TCP SYN flood protection configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    enable: Optional[bool] = Field(
        None,
        description="Enable TCP SYN flood protection",
    )
    red: Optional[FloodRed] = Field(
        None,
        description="Random Early Detection configuration",
    )
    syn_cookies: Optional[FloodSynCookies] = Field(
        None,
        description="SYN Cookies configuration",
    )

    @model_validator(mode="after")
    def validate_red_syn_cookies_mutual_exclusivity(self) -> "TcpSynFlood":
        """Validate that red and syn_cookies are mutually exclusive."""
        if self.red is not None and self.syn_cookies is not None:
            raise ValueError("'red' and 'syn_cookies' are mutually exclusive.")
        return self


class UdpFlood(BaseModel):
    """UDP flood protection configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    enable: Optional[bool] = Field(
        None,
        description="Enable UDP flood protection",
    )
    red: Optional[FloodRed] = Field(
        None,
        description="Random Early Detection configuration",
    )


class SctpInitFlood(BaseModel):
    """SCTP INIT flood protection configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    enable: Optional[bool] = Field(
        None,
        description="Enable SCTP INIT flood protection",
    )
    red: Optional[FloodRed] = Field(
        None,
        description="Random Early Detection configuration",
    )


class IcmpFlood(BaseModel):
    """ICMP flood protection configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    enable: Optional[bool] = Field(
        None,
        description="Enable ICMP flood protection",
    )
    red: Optional[FloodRed] = Field(
        None,
        description="Random Early Detection configuration",
    )


class Icmpv6Flood(BaseModel):
    """ICMPv6 flood protection configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    enable: Optional[bool] = Field(
        None,
        description="Enable ICMPv6 flood protection",
    )
    red: Optional[FloodRed] = Field(
        None,
        description="Random Early Detection configuration",
    )


class OtherIpFlood(BaseModel):
    """Other IP flood protection configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    enable: Optional[bool] = Field(
        None,
        description="Enable other IP flood protection",
    )
    red: Optional[FloodRed] = Field(
        None,
        description="Random Early Detection configuration",
    )


class FloodProtection(BaseModel):
    """Flood protection configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    tcp_syn: Optional[TcpSynFlood] = Field(
        None,
        description="TCP SYN flood protection",
    )
    udp: Optional[UdpFlood] = Field(
        None,
        description="UDP flood protection",
    )
    sctp_init: Optional[SctpInitFlood] = Field(
        None,
        description="SCTP INIT flood protection",
    )
    icmp: Optional[IcmpFlood] = Field(
        None,
        description="ICMP flood protection",
    )
    icmpv6: Optional[Icmpv6Flood] = Field(
        None,
        description="ICMPv6 flood protection",
    )
    other_ip: Optional[OtherIpFlood] = Field(
        None,
        description="Other IP flood protection",
    )


# --- Scan Protection Models ---


class ScanActionBlockIp(BaseModel):
    """Block IP action configuration for scan protection."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    track_by: str = Field(
        ...,
        description="Track by source or source-and-destination",
        pattern=r"^(source|source-and-destination)$",
    )
    duration: int = Field(
        ...,
        description="Block duration in seconds",
        ge=1,
        le=3600,
    )


class ScanAction(BaseModel):
    """Scan action configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    allow: Optional[Dict[str, Any]] = Field(
        None,
        description="Allow action",
    )
    alert: Optional[Dict[str, Any]] = Field(
        None,
        description="Alert action",
    )
    block: Optional[Dict[str, Any]] = Field(
        None,
        description="Block action",
    )
    block_ip: Optional[ScanActionBlockIp] = Field(
        None,
        description="Block IP action",
    )

    @model_validator(mode="after")
    def validate_exactly_one_action(self) -> "ScanAction":
        """Validate that exactly one action is set."""
        actions = [self.allow, self.alert, self.block, self.block_ip]
        set_actions = [a for a in actions if a is not None]
        if len(set_actions) != 1:
            raise ValueError("Exactly one action must be set (allow, alert, block, or block_ip).")
        return self


class ScanEntry(BaseModel):
    """Scan entry configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(
        ...,
        description="Scan entry name",
        pattern=r"^(8001|8002|8003|8006)$",
    )
    action: Optional[ScanAction] = Field(
        None,
        description="Scan action configuration",
    )
    interval: Optional[int] = Field(
        None,
        description="Scan interval",
        ge=2,
        le=65535,
    )
    threshold: Optional[int] = Field(
        None,
        description="Scan threshold",
        ge=2,
        le=65535,
    )


class ScanWhiteListEntry(BaseModel):
    """Scan whitelist entry configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(
        ...,
        description="Whitelist entry name",
    )
    ipv4: Optional[str] = Field(
        None,
        description="IPv4 address",
    )
    ipv6: Optional[str] = Field(
        None,
        description="IPv6 address",
    )


# --- Non-IP Protocol Models ---


class NonIpProtocolEntry(BaseModel):
    """Non-IP protocol entry configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(
        ...,
        description="Protocol entry name",
    )
    ether_type: str = Field(
        ...,
        description="Ethernet type",
    )
    enable: Optional[bool] = Field(
        None,
        description="Enable this protocol entry",
    )


class NonIpProtocol(BaseModel):
    """Non-IP protocol configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    list_type: Optional[str] = Field(
        None,
        description="List type (exclude or include)",
        pattern=r"^(exclude|include)$",
    )
    protocol: Optional[List[NonIpProtocolEntry]] = Field(
        None,
        description="Protocol entries",
    )


# --- L2 Security Group Tag Models ---


class SgtEntry(BaseModel):
    """Security Group Tag entry configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(
        ...,
        description="SGT entry name",
    )
    tag: str = Field(
        ...,
        description="Security group tag value",
    )
    enable: Optional[bool] = Field(
        None,
        description="Enable this SGT entry",
    )


class L2SecGroupTagProtection(BaseModel):
    """Layer 2 Security Group Tag protection configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    tags: Optional[List[SgtEntry]] = Field(
        None,
        description="Security Group Tag entries",
    )


# --- Main Models ---


class ZoneProtectionProfileBaseModel(BaseModel):
    """Base model for Zone Protection Profiles containing fields common to all operations."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    name: str = Field(
        ...,
        description="The name of the zone protection profile",
        max_length=31,
    )
    description: Optional[str] = Field(
        None,
        description="Description of the zone protection profile",
        max_length=255,
    )

    # Flood protection
    flood: Optional[FloodProtection] = Field(
        None,
        description="Flood protection configuration",
    )

    # Scan protection
    scan: Optional[List[ScanEntry]] = Field(
        None,
        description="Scan protection entries",
    )
    scan_white_list: Optional[List[ScanWhiteListEntry]] = Field(
        None,
        description="Scan whitelist entries",
    )

    # Discard boolean fields
    spoofed_ip_discard: Optional[bool] = Field(
        None,
        description="Discard spoofed IP packets",
    )
    strict_ip_check: Optional[bool] = Field(
        None,
        description="Enable strict IP address checking",
    )
    fragmented_traffic_discard: Optional[bool] = Field(
        None,
        description="Discard fragmented traffic",
    )
    strict_source_routing_discard: Optional[bool] = Field(
        None,
        description="Discard strict source routing packets",
    )
    loose_source_routing_discard: Optional[bool] = Field(
        None,
        description="Discard loose source routing packets",
    )
    timestamp_discard: Optional[bool] = Field(
        None,
        description="Discard timestamp option packets",
    )
    record_route_discard: Optional[bool] = Field(
        None,
        description="Discard record route option packets",
    )
    security_discard: Optional[bool] = Field(
        None,
        description="Discard security option packets",
    )
    stream_id_discard: Optional[bool] = Field(
        None,
        description="Discard stream ID option packets",
    )
    unknown_option_discard: Optional[bool] = Field(
        None,
        description="Discard unknown option packets",
    )
    malformed_option_discard: Optional[bool] = Field(
        None,
        description="Discard malformed option packets",
    )
    mismatched_overlapping_tcp_segment_discard: Optional[bool] = Field(
        None,
        description="Discard mismatched overlapping TCP segments",
    )
    tcp_handshake_discard: Optional[bool] = Field(
        None,
        description="Discard incomplete TCP handshake packets",
    )
    tcp_syn_with_data_discard: Optional[bool] = Field(
        None,
        description="Discard TCP SYN packets with data",
    )
    tcp_synack_with_data_discard: Optional[bool] = Field(
        None,
        description="Discard TCP SYN-ACK packets with data",
    )

    # String enum fields
    reject_non_syn_tcp: Optional[str] = Field(
        None,
        description="Reject non-SYN TCP (global/yes/no)",
        pattern=r"^(global|yes|no)$",
    )
    asymmetric_path: Optional[str] = Field(
        None,
        description="Asymmetric path handling (global/drop/bypass)",
        pattern=r"^(global|drop|bypass)$",
    )
    mptcp_option_strip: Optional[str] = Field(
        None,
        description="MPTCP option strip (no/yes/global)",
        pattern=r"^(no|yes|global)$",
    )

    # More boolean fields
    tcp_timestamp_strip: Optional[bool] = Field(
        None,
        description="Strip TCP timestamp option",
    )
    tcp_fast_open_and_data_strip: Optional[bool] = Field(
        None,
        description="Strip TCP Fast Open and data",
    )
    icmp_ping_zero_id_discard: Optional[bool] = Field(
        None,
        description="Discard ICMP ping with zero ID",
    )
    icmp_frag_discard: Optional[bool] = Field(
        None,
        description="Discard fragmented ICMP packets",
    )
    icmp_large_packet_discard: Optional[bool] = Field(
        None,
        description="Discard large ICMP packets",
    )
    discard_icmp_embedded_error: Optional[bool] = Field(
        None,
        description="Discard ICMP embedded error messages",
    )
    suppress_icmp_timeexceeded: Optional[bool] = Field(
        None,
        description="Suppress ICMP time exceeded messages",
    )
    suppress_icmp_needfrag: Optional[bool] = Field(
        None,
        description="Suppress ICMP need fragmentation messages",
    )

    # IPv6 protection (simplified to Dict for deeply nested structure)
    ipv6: Optional[Dict[str, Any]] = Field(
        None,
        description="IPv6 protection configuration",
    )

    # Non-IP protocol
    non_ip_protocol: Optional[NonIpProtocol] = Field(
        None,
        description="Non-IP protocol configuration",
    )

    # L2 Security Group Tag protection
    l2_sec_group_tag_protection: Optional[L2SecGroupTagProtection] = Field(
        None,
        description="Layer 2 Security Group Tag protection",
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


class ZoneProtectionProfileCreateModel(ZoneProtectionProfileBaseModel):
    """Model for creating new Zone Protection Profiles."""

    @model_validator(mode="after")
    def validate_container_type(self) -> "ZoneProtectionProfileCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            ZoneProtectionProfileCreateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = ["folder", "snippet", "device"]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class ZoneProtectionProfileUpdateModel(ZoneProtectionProfileBaseModel):
    """Model for updating existing Zone Protection Profiles."""

    id: UUID = Field(
        ...,
        description="The UUID of the zone protection profile",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class ZoneProtectionProfileResponseModel(ZoneProtectionProfileBaseModel):
    """Model for Zone Protection Profile responses."""

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    id: UUID = Field(
        ...,
        description="The UUID of the zone protection profile",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
