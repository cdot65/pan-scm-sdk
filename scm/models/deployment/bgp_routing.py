"""BGP Routing models for Strata Cloud Manager SDK.

Contains Pydantic models and enums for representing BGP routing configuration data.
"""

# scm/models/deployment/bgp_routing.py

from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
    model_validator,
)


class BackboneRoutingEnum(str, Enum):
    """Enum representing the possible backbone routing options."""

    NO_ASYMMETRIC_ROUTING = "no-asymmetric-routing"
    ASYMMETRIC_ROUTING_ONLY = "asymmetric-routing-only"
    ASYMMETRIC_ROUTING_WITH_LOAD_SHARE = "asymmetric-routing-with-load-share"


class DefaultRoutingModel(BaseModel):
    """Model for default routing preference configuration."""

    model_config = ConfigDict(extra="forbid")

    default: Dict[str, Any] = Field(
        default_factory=dict,
        description="Default routing configuration",
    )


class HotPotatoRoutingModel(BaseModel):
    """Model for hot potato routing preference configuration."""

    model_config = ConfigDict(extra="forbid")

    hot_potato_routing: Dict[str, Any] = Field(
        default_factory=dict,
        description="Hot potato routing configuration",
    )


class BGPRoutingBaseModel(BaseModel):
    """Base model for BGP Routing configurations.

    Attributes:
        routing_preference: The routing preference setting (default or hot potato).
        backbone_routing: Backbone routing configuration for asymmetric routing options.
        accept_route_over_SC: Whether to accept routes over service connections.
        outbound_routes_for_services: List of outbound routes for services.
        add_host_route_to_ike_peer: Whether to add host route to IKE peer.
        withdraw_static_route: Whether to withdraw static routes.

    """

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        extra="forbid",
    )

    routing_preference: Optional[Union[DefaultRoutingModel, HotPotatoRoutingModel]] = None
    backbone_routing: Optional[BackboneRoutingEnum] = None
    accept_route_over_SC: Optional[bool] = None
    outbound_routes_for_services: Optional[List[str]] = None
    add_host_route_to_ike_peer: Optional[bool] = None
    withdraw_static_route: Optional[bool] = None

    @field_serializer("routing_preference")
    def serialize_routing_preference(
        self, value: Optional[Union[DefaultRoutingModel, HotPotatoRoutingModel]]
    ) -> Optional[Dict[str, Any]]:
        """Serialize routing_preference to correct format for API requests."""
        if value is None:
            return None
        if isinstance(value, DefaultRoutingModel):
            return {"default": {}}
        if isinstance(value, HotPotatoRoutingModel):
            return {"hot_potato_routing": {}}
        return None


class BGPRoutingUpdateModel(BGPRoutingBaseModel):
    """Model for updating BGP routing settings.

    All fields optional to support partial updates.
    Note: BGP routing is a singleton resource with no create endpoint.
    """

    @field_validator("outbound_routes_for_services", mode="before")
    @classmethod
    def ensure_list_or_none(cls, v):
        """Convert single string to list, preserve None for partial updates."""
        if v is None:
            return None
        if isinstance(v, str):
            return [v]
        if not isinstance(v, list):
            raise ValueError("outbound_routes_for_services must be a list of strings")
        return v

    @model_validator(mode="after")
    def validate_at_least_one_field(self) -> "BGPRoutingUpdateModel":
        """Ensure at least one field is set for update."""
        fields = [
            self.routing_preference,
            self.backbone_routing,
            self.accept_route_over_SC,
            self.outbound_routes_for_services,
            self.add_host_route_to_ike_peer,
            self.withdraw_static_route,
        ]
        if all(f is None for f in fields):
            raise ValueError("At least one field must be specified for update")
        return self


class BGPRoutingResponseModel(BGPRoutingBaseModel):
    """Model for BGP routing API responses.

    All fields optional per OpenAPI spec - API may return partial data
    when BGP routing hasn't been fully configured.
    """

    # Override to set default to empty list
    outbound_routes_for_services: List[str] = Field(
        default_factory=list,
        description="List of outbound routes for services in CIDR notation",
    )

    @field_validator("outbound_routes_for_services", mode="before")
    @classmethod
    def ensure_list(cls, v):
        """Convert single string to list, None to empty list."""
        if v is None:
            return []
        if isinstance(v, str):
            return [v]
        return v


# Backwards compatibility alias for existing code that uses BGPRoutingCreateModel
# BGP routing is a singleton resource with only GET/PUT endpoints (no POST)
BGPRoutingCreateModel = BGPRoutingUpdateModel
