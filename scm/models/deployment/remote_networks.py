# scm/models/deployment/remote_networks.py

from typing import Optional, List
from uuid import UUID
from enum import Enum

from pydantic import (
    BaseModel,
    Field,
    model_validator,
    ConfigDict,
)


class EcmpLoadBalancingEnum(str, Enum):
    enable = "enable"
    disable = "disable"


class PeeringTypeEnum(str, Enum):
    exchange_v4_over_v4 = "exchange-v4-over-v4"
    exchange_v4_v6_over_v4 = "exchange-v4-v6-over-v4"
    exchange_v4_over_v4_v6_over_v6 = "exchange-v4-over-v4-v6-over-v6"
    exchange_v6_over_v6 = "exchange-v6-over-v6"


class BgpPeerModel(BaseModel):
    local_ip_address: Optional[str] = None
    peer_ip_address: Optional[str] = None
    secret: Optional[str] = None


class BgpModel(BaseModel):
    do_not_export_routes: Optional[bool] = None
    enable: Optional[bool] = None
    local_ip_address: Optional[str] = None
    originate_default_route: Optional[bool] = None
    peer_as: Optional[str] = None
    peer_ip_address: Optional[str] = None
    peering_type: Optional[PeeringTypeEnum] = None
    secret: Optional[str] = None
    summarize_mobile_user_routes: Optional[bool] = None


class ProtocolModel(BaseModel):
    bgp: Optional[BgpModel] = None
    bgp_peer: Optional[BgpPeerModel] = None


class EcmpTunnelModel(BaseModel):
    name: str = Field(..., max_length=63)
    ipsec_tunnel: str = Field(..., max_length=1023)
    local_ip_address: Optional[str] = None
    peer_as: Optional[str] = None
    peer_ip_address: Optional[str] = None
    peering_type: Optional[PeeringTypeEnum] = None
    secret: Optional[str] = None
    summarize_mobile_user_routes: Optional[bool] = None
    do_not_export_routes: Optional[bool] = None
    originate_default_route: Optional[bool] = None


class RemoteNetworkBaseModel(BaseModel):
    """
    Base model for Remote Network objects containing fields common to all CRUD operations.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    # Required fields
    name: str = Field(
        ...,
        max_length=63,
        description="Alphanumeric string begin with letter: [0-9a-zA-Z._-]",
        pattern=r"^[A-Za-z][0-9A-Za-z._-]*$",
    )
    region: str = Field(
        ...,
        min_length=1,
    )
    license_type: str = Field(
        default="FWAAS-AGGREGATE",
        min_length=1,
        description="license type (new customers use aggregate licensing)",
    )

    # Optional fields
    description: Optional[str] = Field(
        None,
        max_length=1023,
    )
    subnets: Optional[List[str]] = None
    spn_name: Optional[str] = Field(
        None,
        description="spn-name is needed when license_type is FWAAS-AGGREGATE",
    )

    # ECMP related
    ecmp_load_balancing: Optional[EcmpLoadBalancingEnum] = Field(
        default=EcmpLoadBalancingEnum.disable,
        description="enable or disable ECMP load balancing",
    )
    ecmp_tunnels: Optional[List[EcmpTunnelModel]] = Field(
        None,
        max_length=4,
        description="ecmp_tunnels is required when ecmp_load_balancing is enable",
    )

    # Non-ECMP ipsec tunnel
    ipsec_tunnel: Optional[str] = Field(
        None,
        description="ipsec_tunnel is required when ecmp_load_balancing is disable",
    )
    secondary_ipsec_tunnel: Optional[str] = None
    protocol: Optional[ProtocolModel] = None

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
    def validate_remote_network_logic(self) -> "RemoteNetworkBaseModel":
        if self.ecmp_load_balancing == EcmpLoadBalancingEnum.enable:
            if not self.ecmp_tunnels:
                raise ValueError(
                    "ecmp_tunnels is required when ecmp_load_balancing is enable"
                )
        else:
            # disable
            if not self.ipsec_tunnel:
                raise ValueError(
                    "ipsec_tunnel is required when ecmp_load_balancing is disable"
                )

        if self.license_type == "FWAAS-AGGREGATE" and not self.spn_name:
            raise ValueError(
                "spn_name is required when license_type is FWAAS-AGGREGATE"
            )

        return self


class RemoteNetworkCreateModel(RemoteNetworkBaseModel):
    """
    Model for creating a new Remote Network.
    Ensures exactly one container field is set (folder, snippet, or device).
    """

    @model_validator(mode="after")
    def validate_container_type(self) -> "RemoteNetworkCreateModel":
        container_fields = ["folder", "snippet", "device"]
        provided = [f for f in container_fields if getattr(self, f) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder' must be provided.")
        return self


class RemoteNetworkUpdateModel(RemoteNetworkBaseModel):
    """
    Model for updating an existing Remote Network.
    Includes optional id field.
    """

    id: Optional[UUID] = Field(
        ...,
        description="The UUID of the remote network",
        examples=["abcd-1234"],
    )


class RemoteNetworkResponseModel(RemoteNetworkBaseModel):
    """
    Model for Remote Network API responses.
    Includes id as a required field.
    """

    id: UUID = Field(
        ...,
        description="The UUID of the remote network",
        examples=["abcd-1234"],
    )
