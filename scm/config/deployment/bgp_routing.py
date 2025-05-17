"""BGP Routing configuration service for Strata Cloud Manager SDK.

Provides service class for managing BGP routing settings via the SCM API.
"""

# scm/config/deployment/bgp_routing.py

# Standard library imports
import logging
from typing import Any, Dict

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.deployment import (
    BackboneRoutingEnum,
    BGPRoutingCreateModel,
    BGPRoutingResponseModel,
    BGPRoutingUpdateModel,
    DefaultRoutingModel,
    HotPotatoRoutingModel,
)


class BGPRouting(BaseObject):
    """Manages BGP routing settings for Service Connections in Palo Alto Networks' Strata Cloud Manager.

    This object provides methods to get, create, update, and reset BGP routing configurations.

    Args:
        api_client: The API client instance

    """

    ENDPOINT = "/config/deployment/v1/bgp-routing"

    def __init__(
        self,
        api_client,
    ):
        """Initialize the BgpRouting service with the given API client."""
        super().__init__(api_client)
        self.logger = logging.getLogger(__name__)

    def get(self) -> BGPRoutingResponseModel:
        """Get the current BGP routing settings.

        Returns:
            BGPRoutingResponseModel: The current BGP routing configuration

        Raises:
            InvalidObjectError: If the response format is invalid

        """
        response = self.api_client.get(self.ENDPOINT)

        if not isinstance(response, dict):
            raise InvalidObjectError(
                message="Invalid response format: expected dictionary",
                error_code="E003",
                http_status_code=500,
                details={"error": "Response is not a dictionary"},
            )

        try:
            # Process routing_preference format before validation
            if "routing_preference" in response:
                routing_pref = response["routing_preference"]
                if isinstance(routing_pref, dict):
                    if "default" in routing_pref:
                        response["routing_preference"] = DefaultRoutingModel(
                            default=routing_pref["default"]
                        )
                    elif "hot_potato_routing" in routing_pref:
                        response["routing_preference"] = HotPotatoRoutingModel(
                            hot_potato_routing=routing_pref["hot_potato_routing"]
                        )

            return BGPRoutingResponseModel(**response)
        except Exception as e:
            raise InvalidObjectError(
                message=f"Invalid response format: {str(e)}",
                error_code="E003",
                http_status_code=500,
                details={"error": str(e)},
            )

    def create(
        self,
        data: Dict[str, Any],
    ) -> BGPRoutingResponseModel:
        """Create a new BGP routing configuration.

        Note: Since BGP routing is a singleton object, this method is functionally
        equivalent to update() and will replace any existing configuration.

        Args:
            data: Dictionary containing the BGP routing configuration

        Returns:
            BGPRoutingResponseModel: The created BGP routing configuration

        Raises:
            InvalidObjectError: If the provided data is invalid
            MissingQueryParameterError: If required fields are missing

        """
        if not data:
            raise MissingQueryParameterError(
                message="BGP routing configuration data cannot be empty",
                error_code="E003",
                http_status_code=400,
                details={"error": "Empty configuration data"},
            )

        try:
            # Process routing_preference format before validation
            if "routing_preference" in data:
                routing_pref = data["routing_preference"]
                if isinstance(routing_pref, dict):
                    if "default" in routing_pref:
                        data["routing_preference"] = DefaultRoutingModel(
                            default=routing_pref["default"]
                        )
                    elif "hot_potato_routing" in routing_pref:
                        data["routing_preference"] = HotPotatoRoutingModel(
                            hot_potato_routing=routing_pref["hot_potato_routing"]
                        )
                elif not isinstance(routing_pref, (DefaultRoutingModel, HotPotatoRoutingModel)):
                    raise InvalidObjectError(
                        message="Invalid routing_preference format",
                        error_code="E003",
                        http_status_code=400,
                        details={
                            "error": "routing_preference must be a dictionary with 'default' or 'hot_potato_routing', or a valid model instance"
                        },
                    )

            # Validate input data using Pydantic model
            bgp_routing = BGPRoutingCreateModel(**data)
        except Exception as e:
            raise InvalidObjectError(
                message=f"Invalid BGP routing configuration: {str(e)}",
                error_code="E003",
                http_status_code=400,
                details={"error": str(e)},
            )

        # Convert to dict for API request
        payload = bgp_routing.model_dump(exclude_unset=True, exclude_none=True)

        # Handle serialization of enum values
        if "backbone_routing" in payload and isinstance(
            payload["backbone_routing"], BackboneRoutingEnum
        ):
            payload["backbone_routing"] = payload["backbone_routing"].value

        # Send the created object to the remote API as JSON
        # Let HTTP errors propagate to caller for proper handling
        response = self.api_client.put(
            self.ENDPOINT,
            json=payload,
        )

        if not isinstance(response, dict):
            raise InvalidObjectError(
                message="Invalid response format: expected dictionary",
                error_code="E003",
                http_status_code=500,
                details={"error": "Response is not a dictionary"},
            )

        try:
            # Process routing_preference format before validation
            if "routing_preference" in response:
                routing_pref = response["routing_preference"]
                if isinstance(routing_pref, dict):
                    if "default" in routing_pref:
                        response["routing_preference"] = DefaultRoutingModel(
                            default=routing_pref["default"]
                        )
                    elif "hot_potato_routing" in routing_pref:
                        response["routing_preference"] = HotPotatoRoutingModel(
                            hot_potato_routing=routing_pref["hot_potato_routing"]
                        )

            return BGPRoutingResponseModel(**response)
        except Exception as e:
            raise InvalidObjectError(
                message=f"Invalid response format: {str(e)}",
                error_code="E003",
                http_status_code=500,
                details={"error": str(e)},
            )

    def update(
        self,
        data: Dict[str, Any],
    ) -> BGPRoutingResponseModel:
        """Update the BGP routing settings.

        Args:
            data: Dictionary containing the BGP routing configuration

        Returns:
            BGPRoutingResponseModel: The updated BGP routing configuration

        Raises:
            InvalidObjectError: If the provided data is invalid
            MissingQueryParameterError: If required fields are missing

        """
        if not data:
            raise MissingQueryParameterError(
                message="BGP routing configuration data cannot be empty",
                error_code="E003",
                http_status_code=400,
                details={"error": "Empty configuration data"},
            )

        try:
            # Process routing_preference format before validation
            if "routing_preference" in data:
                routing_pref = data["routing_preference"]
                if isinstance(routing_pref, dict):
                    if "default" in routing_pref:
                        data["routing_preference"] = DefaultRoutingModel(
                            default=routing_pref["default"]
                        )
                    elif "hot_potato_routing" in routing_pref:
                        data["routing_preference"] = HotPotatoRoutingModel(
                            hot_potato_routing=routing_pref["hot_potato_routing"]
                        )
                elif not isinstance(routing_pref, (DefaultRoutingModel, HotPotatoRoutingModel)):
                    raise InvalidObjectError(
                        message="Invalid routing_preference format",
                        error_code="E003",
                        http_status_code=400,
                        details={
                            "error": "routing_preference must be a dictionary with 'default' or 'hot_potato_routing', or a valid model instance"
                        },
                    )

            # Validate input data using Pydantic model
            bgp_routing = BGPRoutingUpdateModel(**data)
        except Exception as e:
            raise InvalidObjectError(
                message=f"Invalid BGP routing configuration: {str(e)}",
                error_code="E003",
                http_status_code=400,
                details={"error": str(e)},
            )

        # Convert to dict for API request
        payload = bgp_routing.model_dump(exclude_unset=True, exclude_none=True)

        # Handle serialization of enum values
        if "backbone_routing" in payload and isinstance(
            payload["backbone_routing"], BackboneRoutingEnum
        ):
            payload["backbone_routing"] = payload["backbone_routing"].value

        # Send the updated object to the remote API as JSON
        # Let HTTP errors propagate to caller for proper handling
        response = self.api_client.put(
            self.ENDPOINT,
            json=payload,
        )

        if not isinstance(response, dict):
            raise InvalidObjectError(
                message="Invalid response format: expected dictionary",
                error_code="E003",
                http_status_code=500,
                details={"error": "Response is not a dictionary"},
            )

        try:
            # Process routing_preference format before validation
            if "routing_preference" in response:
                routing_pref = response["routing_preference"]
                if isinstance(routing_pref, dict):
                    if "default" in routing_pref:
                        response["routing_preference"] = DefaultRoutingModel(
                            default=routing_pref["default"]
                        )
                    elif "hot_potato_routing" in routing_pref:
                        response["routing_preference"] = HotPotatoRoutingModel(
                            hot_potato_routing=routing_pref["hot_potato_routing"]
                        )

            return BGPRoutingResponseModel(**response)
        except Exception as e:
            raise InvalidObjectError(
                message=f"Invalid response format: {str(e)}",
                error_code="E003",
                http_status_code=500,
                details={"error": str(e)},
            )

    def delete(self) -> None:
        """Reset the BGP routing configuration to default values.

        Note: Since BGP routing is a singleton configuration object, it cannot be truly deleted.
        This method resets the configuration to default values instead.

        Raises:
            InvalidObjectError: If there's an error resetting the configuration

        """
        # Default configuration values based on the API specification
        default_config = {
            "routing_preference": {"default": {}},
            "backbone_routing": BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING.value,  # Use enum value
            "accept_route_over_SC": False,
            "outbound_routes_for_services": [],
            "add_host_route_to_ike_peer": False,
            "withdraw_static_route": False,
        }

        try:
            # Send the reset configuration
            self.api_client.put(
                self.ENDPOINT,
                json=default_config,
            )
        except Exception as e:
            raise InvalidObjectError(
                message=f"Error resetting BGP routing configuration: {str(e)}",
                error_code="E003",
                http_status_code=500,
                details={"error": str(e)},
            )
