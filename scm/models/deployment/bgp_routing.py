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

    default: Dict[str, Any] = Field(
        default_factory=dict,
        description="Default routing configuration",
    )


class HotPotatoRoutingModel(BaseModel):
    """Model for hot potato routing preference configuration."""

    hot_potato_routing: Dict[str, Any] = Field(
        default_factory=dict,
        description="Hot potato routing configuration",
    )


class BGPRoutingBaseModel(BaseModel):
    """Base model for BGP Routing configurations containing fields common to all operations.

    Attributes:
        routing_preference (Union[DefaultRoutingModel, HotPotatoRoutingModel]):
            The routing preference setting (default or hot potato).
        backbone_routing (BackboneRoutingEnum):
            Backbone routing configuration for asymmetric routing options.
        accept_route_over_SC (bool):
            Whether to accept routes over service connections.
        outbound_routes_for_services (List[str]):
            List of outbound routes for services.
        add_host_route_to_ike_peer (bool):
            Whether to add host route to IKE peer.
        withdraw_static_route (bool):
            Whether to withdraw static routes.

    """

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    # Define fields in the base model
    routing_preference: Optional[Union[DefaultRoutingModel, HotPotatoRoutingModel]] = None
    backbone_routing: Optional[BackboneRoutingEnum] = None
    accept_route_over_SC: Optional[bool] = None
    outbound_routes_for_services: Optional[List[str]] = None
    add_host_route_to_ike_peer: Optional[bool] = None
    withdraw_static_route: Optional[bool] = None

    @field_validator("outbound_routes_for_services", mode="before")
    @classmethod
    def validate_outbound_routes(cls, v):
        """Ensure outbound_routes_for_services is a list."""
        # Check the calling class to determine behavior
        is_update_model = cls.__name__ == "BGPRoutingUpdateModel"

        if v is None:
            # For update model, keep None to allow partial updates
            if is_update_model:
                return None
            # For other models, convert to empty list
            return []

        if isinstance(v, str):
            return [v]
        if not isinstance(v, list):
            raise ValueError("outbound_routes_for_services must be a list of strings")
        return v

    @field_serializer("routing_preference")
    def serialize_routing_preference(
        self, value: Optional[Union[DefaultRoutingModel, HotPotatoRoutingModel]]
    ) -> Optional[Dict[str, Any]]:
        """Serialize routing_preference to correct format for API requests."""
        if value is None:
            return None

        if isinstance(value, DefaultRoutingModel):
            return {"default": {}}
        elif isinstance(value, HotPotatoRoutingModel):
            return {"hot_potato_routing": {}}

        return None


class BGPRoutingCreateModel(BGPRoutingBaseModel):
    """Model for creating BGP routing settings.

    Inherits from BGPRoutingBaseModel and enforces required fields for creation.
    """

    # Required fields
    backbone_routing: BackboneRoutingEnum = Field(
        ...,
        description="Backbone routing configuration for asymmetric routing options",
    )

    # Fields with default values
    routing_preference: Optional[Union[DefaultRoutingModel, HotPotatoRoutingModel]] = Field(
        None,
        description="The routing preference configuration",
    )

    accept_route_over_SC: bool = Field(
        False,
        description="Accept route over Service Connection",
    )

    outbound_routes_for_services: List[str] = Field(
        default_factory=list,
        description="List of outbound routes for services in CIDR notation",
    )

    add_host_route_to_ike_peer: bool = Field(
        False,
        description="Whether to add host route to IKE peer",
    )

    withdraw_static_route: bool = Field(
        False,
        description="Whether to withdraw static route",
    )

    @model_validator(mode="after")
    def validate_routing_preference_type(self) -> "BGPRoutingCreateModel":
        """Validate that routing_preference is the correct type if provided."""
        if self.routing_preference is not None:
            if not isinstance(
                self.routing_preference, (DefaultRoutingModel, HotPotatoRoutingModel)
            ):
                raise ValueError(
                    "routing_preference must be either DefaultRoutingModel or HotPotatoRoutingModel"
                )
        return self


class BGPRoutingUpdateModel(BGPRoutingBaseModel):
    """Model for updating BGP routing settings.

    All fields are optional to support partial updates.
    """

    routing_preference: Optional[Union[DefaultRoutingModel, HotPotatoRoutingModel]] = Field(
        None,
        description="The routing preference configuration",
    )

    backbone_routing: Optional[BackboneRoutingEnum] = Field(
        None,
        description="Backbone routing configuration for asymmetric routing options",
    )

    accept_route_over_SC: Optional[bool] = Field(
        None,
        description="Accept route over Service Connection",
    )

    outbound_routes_for_services: Optional[List[str]] = Field(
        None,
        description="List of outbound routes for services in CIDR notation",
    )

    add_host_route_to_ike_peer: Optional[bool] = Field(
        None,
        description="Whether to add host route to IKE peer",
    )

    withdraw_static_route: Optional[bool] = Field(
        None,
        description="Whether to withdraw static route",
    )

    # We don't need a separate validator here since outbound_routes_for_services
    # is already validated in the parent class. The behavior for None will be
    # handled in the model_validator below

    @model_validator(mode="after")
    def validate_update_model(self) -> "BGPRoutingUpdateModel":
        """Validate the update model.

        1. Ensures routing_preference is the correct type if provided
        2. Ensures at least one field is set for update
        """
        if self.routing_preference is not None:
            if not isinstance(
                self.routing_preference, (DefaultRoutingModel, HotPotatoRoutingModel)
            ):
                raise ValueError(
                    "routing_preference must be either DefaultRoutingModel or HotPotatoRoutingModel"
                )

        # Ensure at least one field is set for update
        field_count = sum(
            1
            for f in [
                self.routing_preference,
                self.backbone_routing,
                self.accept_route_over_SC,
                self.outbound_routes_for_services,
                self.add_host_route_to_ike_peer,
                self.withdraw_static_route,
            ]
            if f is not None
        )

        if field_count == 0:
            raise ValueError("At least one field must be specified for update")

        return self


class BGPRoutingResponseModel(BGPRoutingBaseModel):
    """Model for BGP routing API responses.

    Inherits from BGPRoutingBaseModel but makes all fields required for response validation.
    """

    routing_preference: Union[DefaultRoutingModel, HotPotatoRoutingModel] = Field(
        ...,
        description="The routing preference configuration",
    )

    backbone_routing: BackboneRoutingEnum = Field(
        ...,
        description="Backbone routing configuration for asymmetric routing options",
    )

    accept_route_over_SC: bool = Field(
        ...,
        description="Accept route over Service Connection",
    )

    outbound_routes_for_services: List[str] = Field(
        ...,
        description="List of outbound routes for services in CIDR notation",
    )

    add_host_route_to_ike_peer: bool = Field(
        ...,
        description="Whether to add host route to IKE peer",
    )

    withdraw_static_route: bool = Field(
        ...,
        description="Whether to withdraw static route",
    )

    # We're inheriting the serializer from the parent class, so no need to define it again here
