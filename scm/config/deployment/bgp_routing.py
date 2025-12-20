"""BGP Routing configuration service for Strata Cloud Manager SDK.

Provides service class for managing BGP routing settings via the SCM API.
"""

# scm/config/deployment/bgp_routing.py

# Standard library imports
import logging
from typing import Any, Dict, Optional

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.deployment import (
    BackboneRoutingEnum,
    BGPRoutingResponseModel,
    BGPRoutingUpdateModel,
    DefaultRoutingModel,
    HotPotatoRoutingModel,
)


class BGPRouting(BaseObject):
    """Manages BGP routing settings for Service Connections in Strata Cloud Manager.

    BGP routing is a singleton configuration object with only GET and PUT operations.
    There is no POST (create) or DELETE endpoint - the configuration always exists.

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

    def _process_routing_preference(
        self, data: Dict[str, Any]
    ) -> Optional[DefaultRoutingModel | HotPotatoRoutingModel]:
        """Convert routing_preference dict to model instance.

        Args:
            data: Dictionary that may contain routing_preference

        Returns:
            Model instance or None if not present/invalid

        """
        if "routing_preference" not in data:
            return None

        routing_pref = data["routing_preference"]
        if isinstance(routing_pref, (DefaultRoutingModel, HotPotatoRoutingModel)):
            return routing_pref
        if isinstance(routing_pref, dict):
            if "default" in routing_pref:
                return DefaultRoutingModel(default=routing_pref["default"])
            if "hot_potato_routing" in routing_pref:
                return HotPotatoRoutingModel(
                    hot_potato_routing=routing_pref["hot_potato_routing"]
                )
        return None

    def _validate_routing_preference_input(self, data: Dict[str, Any]) -> None:
        """Validate routing_preference in input data.

        Args:
            data: Input data dictionary

        Raises:
            InvalidObjectError: If routing_preference format is invalid

        """
        if "routing_preference" not in data:
            return

        routing_pref = data["routing_preference"]
        if isinstance(routing_pref, (DefaultRoutingModel, HotPotatoRoutingModel)):
            return
        if isinstance(routing_pref, dict):
            if "default" in routing_pref or "hot_potato_routing" in routing_pref:
                return
        raise InvalidObjectError(
            message="Invalid routing_preference format",
            error_code="E003",
            http_status_code=400,
            details={
                "error": "routing_preference must be a dictionary with 'default' or "
                "'hot_potato_routing', or a valid model instance"
            },
        )

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
            routing_model = self._process_routing_preference(response)
            if routing_model is not None:
                response["routing_preference"] = routing_model
            elif "routing_preference" in response:
                # Unknown routing_preference format - remove to avoid validation error
                del response["routing_preference"]

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
        """Create/set BGP routing configuration.

        Note: BGP routing is a singleton object. This method is an alias for update()
        and will replace any existing configuration using PUT.

        Args:
            data: Dictionary containing the BGP routing configuration

        Returns:
            BGPRoutingResponseModel: The BGP routing configuration

        Raises:
            InvalidObjectError: If the provided data is invalid
            MissingQueryParameterError: If required fields are missing

        """
        return self.update(data)

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
            # Validate and convert routing_preference
            self._validate_routing_preference_input(data)
            routing_model = self._process_routing_preference(data)
            if routing_model is not None:
                data["routing_preference"] = routing_model

            # Validate input data using Pydantic model
            bgp_routing = BGPRoutingUpdateModel(**data)
        except InvalidObjectError:
            raise
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
            routing_model = self._process_routing_preference(response)
            if routing_model is not None:
                response["routing_preference"] = routing_model
            elif "routing_preference" in response:
                # Unknown routing_preference format - remove to avoid validation error
                del response["routing_preference"]

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

        Note: BGP routing is a singleton configuration object and cannot be deleted.
        This method resets the configuration to default values instead.

        Raises:
            InvalidObjectError: If there's an error resetting the configuration

        """
        default_config = {
            "routing_preference": {"default": {}},
            "backbone_routing": BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING.value,
            "accept_route_over_SC": False,
            "outbound_routes_for_services": [],
            "add_host_route_to_ike_peer": False,
            "withdraw_static_route": False,
        }

        try:
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
