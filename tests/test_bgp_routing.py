# tests/test_bgp_routing.py

import unittest
from unittest.mock import MagicMock, patch

import pytest
from tests.scm.mock_scm import MockScm
from scm.config.deployment.bgp_routing import BGPRouting
from scm.models.deployment import (
    BGPRoutingCreateModel,
    BGPRoutingUpdateModel,
    BGPRoutingResponseModel,
    DefaultRoutingModel,
    HotPotatoRoutingModel,
    BackboneRoutingEnum
)


class TestBGPRouting(unittest.TestCase):
    """Test cases for BGPRouting class."""

    def setUp(self):
        """Set up test fixtures."""
        self.api_client = MockScm()
        self.bgp_routing = BGPRouting(self.api_client)

    def test_get_bgp_routing(self):
        """Test fetching BGP routing settings."""
        # Mock API response
        mock_response = {
            "routing_preference": {"default": {}},
            "backbone_routing": "no-asymmetric-routing",
            "accept_route_over_SC": True,
            "outbound_routes_for_services": ["10.0.0.0/8", "192.168.0.0/16"],
            "add_host_route_to_ike_peer": False,
            "withdraw_static_route": True
        }
        self.api_client.get.return_value = mock_response

        # Call the method
        result = self.bgp_routing.get()

        # Verify API call
        self.api_client.get.assert_called_once_with(
            self.bgp_routing.ENDPOINT
        )

        # Verify response
        self.assertIsInstance(result, BGPRoutingResponseModel)
        self.assertEqual(result.backbone_routing, BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING)
        self.assertEqual(result.accept_route_over_SC, True)
        self.assertEqual(result.outbound_routes_for_services, ["10.0.0.0/8", "192.168.0.0/16"])
        self.assertEqual(result.add_host_route_to_ike_peer, False)
        self.assertEqual(result.withdraw_static_route, True)

    def test_create_bgp_routing(self):
        """Test creating BGP routing settings."""
        # Prepare creation data
        create_data = {
            "routing_preference": {"default": {}},
            "backbone_routing": "asymmetric-routing-only",
            "accept_route_over_SC": True,
            "outbound_routes_for_services": ["10.0.0.0/8"],
            "add_host_route_to_ike_peer": True,
            "withdraw_static_route": True
        }

        # Mock API response that simulates the actual API behavior
        mock_response = {
            "routing_preference": {"default": {}},
            "backbone_routing": "asymmetric-routing-only",
            "accept_route_over_SC": True,
            "outbound_routes_for_services": ["10.0.0.0/8"],
            "add_host_route_to_ike_peer": True,
            "withdraw_static_route": True
        }
        self.api_client.put.return_value = mock_response

        # Call the method
        result = self.bgp_routing.create(create_data)

        # Verify API call
        self.api_client.put.assert_called_once()
        call_args = self.api_client.put.call_args
        self.assertEqual(call_args[0][0], self.bgp_routing.ENDPOINT)

        # Verify payload
        payload = call_args[1]["json"]
        self.assertIsInstance(payload, dict)
        self.assertEqual(payload["backbone_routing"], "asymmetric-routing-only")
        self.assertEqual(payload["accept_route_over_SC"], True)

        # Verify response
        self.assertIsInstance(result, BGPRoutingResponseModel)
        self.assertEqual(result.backbone_routing, BackboneRoutingEnum.ASYMMETRIC_ROUTING_ONLY)
        self.assertEqual(result.accept_route_over_SC, True)
        self.assertEqual(result.outbound_routes_for_services, ["10.0.0.0/8"])
        self.assertEqual(result.add_host_route_to_ike_peer, True)
        self.assertEqual(result.withdraw_static_route, True)

    def test_update_bgp_routing(self):
        """Test updating BGP routing settings."""
        # Prepare update data
        update_data = {
            "routing_preference": {"hot_potato_routing": {}},
            "backbone_routing": "asymmetric-routing-with-load-share",
            "accept_route_over_SC": False,
            "outbound_routes_for_services": ["172.16.0.0/12"],
            "add_host_route_to_ike_peer": True,
            "withdraw_static_route": False
        }

        # Mock API response
        mock_response = update_data.copy()
        self.api_client.put.return_value = mock_response

        # Call the method
        result = self.bgp_routing.update(update_data)

        # Verify API call
        self.api_client.put.assert_called_once()
        call_args = self.api_client.put.call_args
        self.assertEqual(call_args[0][0], self.bgp_routing.ENDPOINT)

        # Verify payload
        payload = call_args[1]["json"]
        self.assertIsInstance(payload, dict)
        self.assertEqual(payload["backbone_routing"], "asymmetric-routing-with-load-share")
        self.assertEqual(payload["accept_route_over_SC"], False)

        # Verify response
        self.assertIsInstance(result, BGPRoutingResponseModel)
        self.assertEqual(result.backbone_routing, BackboneRoutingEnum.ASYMMETRIC_ROUTING_WITH_LOAD_SHARE)
        self.assertEqual(result.accept_route_over_SC, False)
        self.assertEqual(result.outbound_routes_for_services, ["172.16.0.0/12"])
        self.assertEqual(result.add_host_route_to_ike_peer, True)
        self.assertEqual(result.withdraw_static_route, False)

    def test_delete_bgp_routing(self):
        """Test resetting BGP routing settings."""
        # Call the delete method
        self.bgp_routing.delete()

        # Verify API call
        self.api_client.put.assert_called_once()
        call_args = self.api_client.put.call_args
        self.assertEqual(call_args[0][0], self.bgp_routing.ENDPOINT)

        # Verify default payload was sent
        payload = call_args[1]["json"]
        self.assertIsInstance(payload, dict)
        self.assertEqual(payload["backbone_routing"], "no-asymmetric-routing")
        self.assertEqual(payload["accept_route_over_SC"], False)
        self.assertEqual(payload["outbound_routes_for_services"], [])
        self.assertEqual(payload["add_host_route_to_ike_peer"], False)
        self.assertEqual(payload["withdraw_static_route"], False)

    def test_routing_preference_serialization(self):
        """Test correct serialization of routing preference models."""
        # Test with DefaultRoutingModel
        default_model = BGPRoutingCreateModel(
            routing_preference=DefaultRoutingModel(),
            backbone_routing=BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING
        )
        default_dict = default_model.model_dump()
        self.assertIn("routing_preference", default_dict)
        self.assertEqual(default_dict["routing_preference"], {"default": {}})

        # Test with HotPotatoRoutingModel
        hot_potato_model = BGPRoutingCreateModel(
            routing_preference=HotPotatoRoutingModel(),
            backbone_routing=BackboneRoutingEnum.ASYMMETRIC_ROUTING_ONLY
        )
        hot_potato_dict = hot_potato_model.model_dump()
        self.assertIn("routing_preference", hot_potato_dict)
        self.assertEqual(hot_potato_dict["routing_preference"], {"hot_potato_routing": {}})

    def test_model_validation(self):
        """Test model validation."""
        # Test creating a valid model
        valid_model = BGPRoutingCreateModel(
            routing_preference=DefaultRoutingModel(),
            backbone_routing=BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
            accept_route_over_SC=True
        )
        self.assertIsInstance(valid_model, BGPRoutingCreateModel)
        
        # Test model serialization
        model_dict = valid_model.model_dump()
        self.assertIn("routing_preference", model_dict)
        self.assertIn("backbone_routing", model_dict)
        self.assertIn("accept_route_over_SC", model_dict)
        
    def test_outbound_routes_conversion(self):
        """Test conversion of outbound_routes_for_services from string to list."""
        # Create a model with a string value for outbound_routes_for_services
        create_data = {
            "routing_preference": {"default": {}},
            "backbone_routing": "no-asymmetric-routing",
            "outbound_routes_for_services": "10.0.0.0/8"  # String instead of list
        }
        
        # Mock API response with all required fields
        mock_response = {
            "routing_preference": {"default": {}},
            "backbone_routing": "no-asymmetric-routing",
            "outbound_routes_for_services": ["10.0.0.0/8"],
            "accept_route_over_SC": False,
            "add_host_route_to_ike_peer": False,
            "withdraw_static_route": False
        }
        self.api_client.put.return_value = mock_response
        
        # Call create method
        result = self.bgp_routing.create(create_data)
        
        # Verify the API call payload had the routes converted to a list
        call_args = self.api_client.put.call_args
        payload = call_args[1]["json"]
        self.assertIsInstance(payload["outbound_routes_for_services"], list)
        self.assertEqual(payload["outbound_routes_for_services"], ["10.0.0.0/8"])
        
        # Verify the returned object has the correct format
        self.assertEqual(result.outbound_routes_for_services, ["10.0.0.0/8"])
        
    def test_empty_outbound_routes(self):
        """Test handling of None and empty values for outbound_routes_for_services."""
        # Test with None
        create_data = {
            "routing_preference": {"default": {}},
            "backbone_routing": "no-asymmetric-routing",
            "outbound_routes_for_services": None,
            "accept_route_over_SC": False,
            "add_host_route_to_ike_peer": False,
            "withdraw_static_route": False
        }
        
        # Complete mock response with all required fields
        mock_response = {
            "routing_preference": {"default": {}},
            "backbone_routing": "no-asymmetric-routing",
            "outbound_routes_for_services": [],
            "accept_route_over_SC": False,
            "add_host_route_to_ike_peer": False,
            "withdraw_static_route": False
        }
        self.api_client.put.return_value = mock_response
        
        result = self.bgp_routing.create(create_data)
        self.assertEqual(result.outbound_routes_for_services, [])
        
        # Test with empty list
        create_data["outbound_routes_for_services"] = []
        # Keep all required fields in the data dictionary
        create_data.update({
            "accept_route_over_SC": False,
            "add_host_route_to_ike_peer": False,
            "withdraw_static_route": False
        })
        self.api_client.put.return_value = mock_response
        
        result = self.bgp_routing.create(create_data)
        self.assertEqual(result.outbound_routes_for_services, [])
        
    def test_api_response_processing(self):
        """Test the processing of API responses with different routing_preference formats."""
        # Test with default routing
        mock_response = {
            "routing_preference": {"default": {}},
            "backbone_routing": "no-asymmetric-routing",
            "accept_route_over_SC": False,
            "outbound_routes_for_services": [],
            "add_host_route_to_ike_peer": False,
            "withdraw_static_route": False
        }
        self.api_client.get.return_value = mock_response
        
        result = self.bgp_routing.get()
        self.assertIsInstance(result.routing_preference, DefaultRoutingModel)
        
        # Test with hot potato routing
        mock_response["routing_preference"] = {"hot_potato_routing": {}}
        self.api_client.get.return_value = mock_response
        
        result = self.bgp_routing.get()
        self.assertIsInstance(result.routing_preference, HotPotatoRoutingModel)


if __name__ == "__main__":
    unittest.main()
