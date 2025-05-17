"""Service Connections models for Strata Cloud Manager SDK.

Contains Pydantic models for representing service connection objects and related data.
"""

from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OnboardingType(str, Enum):
    """Types of onboarding for service connections."""

    CLASSIC = "classic"


class NoExportCommunity(str, Enum):
    """No export community options for service connections."""

    DISABLED = "Disabled"
    ENABLED_IN = "Enabled-In"
    ENABLED_OUT = "Enabled-Out"
    ENABLED_BOTH = "Enabled-Both"


class BgpPeerModel(BaseModel):
    """BGP peer configuration for service connections."""

    local_ip_address: Optional[str] = Field(None, description="Local IPv4 address for BGP peering")
    local_ipv6_address: Optional[str] = Field(
        None, description="Local IPv6 address for BGP peering"
    )
    peer_ip_address: Optional[str] = Field(None, description="Peer IPv4 address for BGP peering")
    peer_ipv6_address: Optional[str] = Field(None, description="Peer IPv6 address for BGP peering")
    secret: Optional[str] = Field(None, description="BGP authentication secret")


class BgpProtocolModel(BaseModel):
    """BGP protocol configuration for service connections."""

    do_not_export_routes: Optional[bool] = Field(None, description="Do not export routes option")
    enable: Optional[bool] = Field(None, description="Enable BGP")
    fast_failover: Optional[bool] = Field(None, description="Enable fast failover")
    local_ip_address: Optional[str] = Field(None, description="Local IPv4 address for BGP peering")
    originate_default_route: Optional[bool] = Field(None, description="Originate default route")
    peer_as: Optional[str] = Field(None, description="BGP peer AS number")
    peer_ip_address: Optional[str] = Field(None, description="Peer IPv4 address for BGP peering")
    secret: Optional[str] = Field(None, description="BGP authentication secret")
    summarize_mobile_user_routes: Optional[bool] = Field(
        None, description="Summarize mobile user routes"
    )


class ProtocolModel(BaseModel):
    """Protocol configuration for service connections."""

    bgp: Optional[BgpProtocolModel] = Field(None, description="BGP protocol configuration")


class QosModel(BaseModel):
    """QoS configuration for service connections."""

    enable: Optional[bool] = Field(None, description="Enable QoS")
    qos_profile: Optional[str] = Field(None, description="QoS profile name")


class ServiceConnectionBaseModel(BaseModel):
    """Base model for Service Connections containing fields common to all operations."""

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    name: str = Field(
        ...,
        description="The name of the service connection",
        pattern=r"^[0-9a-zA-Z._\- ]+$",  # Pattern includes whitespace
        max_length=63,
    )
    folder: Optional[str] = Field(
        "Service Connections",
        description="The folder containing the service connection",
    )
    ipsec_tunnel: str = Field(..., description="IPsec tunnel for the service connection")
    onboarding_type: OnboardingType = Field(
        OnboardingType.CLASSIC, description="Onboarding type for the service connection"
    )
    region: str = Field(..., description="Region for the service connection")
    backup_SC: Optional[str] = Field(None, description="Backup service connection")
    bgp_peer: Optional[BgpPeerModel] = Field(None, description="BGP peer configuration")
    nat_pool: Optional[str] = Field(None, description="NAT pool for the service connection")
    no_export_community: Optional[NoExportCommunity] = Field(
        None, description="No export community configuration"
    )
    protocol: Optional[ProtocolModel] = Field(None, description="Protocol configuration")
    qos: Optional[QosModel] = Field(None, description="QoS configuration")
    secondary_ipsec_tunnel: Optional[str] = Field(None, description="Secondary IPsec tunnel")
    source_nat: Optional[bool] = Field(None, description="Enable source NAT")
    subnets: Optional[List[str]] = Field(None, description="Subnets for the service connection")


class ServiceConnectionCreateModel(ServiceConnectionBaseModel):
    """Model for creating new Service Connections."""

    id: Optional[str] = None


class ServiceConnectionUpdateModel(ServiceConnectionBaseModel):
    """Model for updating existing Service Connections."""

    id: UUID = Field(
        ...,
        description="The UUID of the service connection",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class ServiceConnectionResponseModel(ServiceConnectionBaseModel):
    """Model for Service Connection responses."""

    id: UUID = Field(
        ...,
        description="The UUID of the service connection",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
