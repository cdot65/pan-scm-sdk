# examples/bgp_routing_example.py
"""Example script for BGP routing management."""

import os
import sys
import logging
from typing import Dict, Any

# Add parent directory to path to import scm
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scm.api import SCMClient
from scm.auth import SCMAuth
from scm.config.deployment.bgp_routing import BGPRouting
from scm.models.deployment import (
    BGPRoutingCreateModel,
    DefaultRoutingPreferenceModel,
    BackboneRoutingEnum,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Demonstrate BGP routing configuration with the Strata Cloud Manager SDK."""
    # Authentication
    client_id = os.environ.get("SCM_CLIENT_ID")
    client_secret = os.environ.get("SCM_CLIENT_SECRET")
    tsg_id = os.environ.get("SCM_TSG_ID")

    if not client_id or not client_secret or not tsg_id:
        logger.error(
            "Missing required environment variables. Please set SCM_CLIENT_ID, SCM_CLIENT_SECRET, and SCM_TSG_ID."
        )
        sys.exit(1)

    # Initialize authentication
    auth = SCMAuth(
        client_id=client_id,
        client_secret=client_secret,
        scope=f"tsg_id:{tsg_id}",
    )

    # Initialize API client
    client = SCMClient(auth=auth)

    # Initialize BGP routing service
    bgp_routing = BGPRouting(client)

    # Get current BGP routing settings
    try:
        current_settings = bgp_routing.get()
        logger.info("Current BGP routing settings:")
        logger.info(f"Backbone routing: {current_settings.backbone_routing}")
        logger.info(
            f"Accept route over Service Connection: {current_settings.accept_route_over_SC}"
        )

        if current_settings.outbound_routes_for_services:
            logger.info(
                f"Outbound routes for services: {', '.join(current_settings.outbound_routes_for_services)}"
            )

        if current_settings.routing_preference:
            preference_type = (
                "Default"
                if hasattr(current_settings.routing_preference, "default")
                else "Hot Potato"
            )
            logger.info(f"Routing preference: {preference_type}")

        logger.info(f"Add host route to IKE peer: {current_settings.add_host_route_to_ike_peer}")
        logger.info(f"Withdraw static route: {current_settings.withdraw_static_route}")

    except Exception as e:
        logger.error(f"Error getting BGP routing settings: {e}")
        sys.exit(1)

    # Example 1: Update using direct dictionary approach
    try:
        # Example update payload
        update_data: Dict[str, Any] = {
            "routing_preference": {"hot_potato_routing": {}},  # Switch to hot potato routing
            "backbone_routing": BackboneRoutingEnum.ASYMMETRIC_ROUTING_WITH_LOAD_SHARE,
            "accept_route_over_SC": True,
            "outbound_routes_for_services": ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"],
            "add_host_route_to_ike_peer": True,
            "withdraw_static_route": False,
        }

        # Ask for confirmation before updating
        confirm = input(
            "\nDo you want to update BGP routing settings with dictionary approach? (y/n): "
        )
        if confirm.lower() == "y":
            updated_settings = bgp_routing.update(update_data)
            logger.info("\nBGP routing settings updated successfully:")
            logger.info(f"New backbone routing: {updated_settings.backbone_routing}")
            logger.info("New routing preference: Hot Potato")

    except Exception as e:
        logger.error(f"Error updating BGP routing settings: {e}")
        sys.exit(1)

    # Example 2: Update using Pydantic model approach
    try:
        # Create model directly
        bgp_routing_model = BGPRoutingCreateModel(
            routing_preference=DefaultRoutingPreferenceModel(),
            backbone_routing=BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
            accept_route_over_SC=False,
            outbound_routes_for_services=["192.168.0.0/16"],
            add_host_route_to_ike_peer=False,
            withdraw_static_route=True,
        )

        # Ask for confirmation before updating
        confirm = input(
            "\nDo you want to update BGP routing settings with Pydantic model approach? (y/n): "
        )
        if confirm.lower() == "y":
            # Convert model to dict for update
            model_dict = bgp_routing_model.model_dump()
            updated_settings = bgp_routing.update(model_dict)
            logger.info("\nBGP routing settings updated successfully:")
            logger.info(f"New backbone routing: {updated_settings.backbone_routing}")
            logger.info("New routing preference: Default")

    except Exception as e:
        logger.error(f"Error updating BGP routing settings with model: {e}")
        sys.exit(1)

    # Example 3: Reset to defaults
    try:
        # Ask for confirmation before resetting
        confirm = input("\nDo you want to reset BGP routing settings to defaults? (y/n): ")
        if confirm.lower() == "y":
            bgp_routing.delete()
            logger.info("\nBGP routing settings reset to defaults.")

            # Verify reset
            reset_settings = bgp_routing.get()
            logger.info("Verified settings after reset:")
            logger.info(f"Backbone routing: {reset_settings.backbone_routing}")

    except Exception as e:
        logger.error(f"Error resetting BGP routing settings: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
