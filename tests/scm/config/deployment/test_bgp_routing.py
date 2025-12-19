"""Test module for BGP Routing configuration service.

This module contains unit tests for the BGP Routing configuration service and its related models.
"""
# tests/scm/config/deployment/test_bgp_routing.py

# Standard library imports
from unittest.mock import MagicMock

# External libraries
import pytest
from requests.exceptions import HTTPError

# Local SDK imports
from scm.config.deployment import BGPRouting
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.deployment import (
    BackboneRoutingEnum,
    BGPRoutingResponseModel,
    DefaultRoutingModel,
    HotPotatoRoutingModel,
)
from tests.factories.deployment.bgp_routing import (
    BGPRoutingCreateApiFactory,
    BGPRoutingResponseFactory,
    BGPRoutingUpdateApiFactory,
)
from tests.utils import raise_mock_http_error


@pytest.mark.usefixtures("load_env")
class TestBGPRoutingBase:
    """Base class for BGPRouting tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = BGPRouting(self.mock_scm)


class TestBGPRoutingGet(TestBGPRoutingBase):
    """Tests for getting BGP routing settings."""

    def test_get_valid(self):
        """Test getting BGP routing settings successfully."""
        mock_response = BGPRoutingResponseFactory()
        self.mock_scm.get.return_value = mock_response

        bgp_routing = self.client.get()

        self.mock_scm.get.assert_called_once_with("/config/deployment/v1/bgp-routing")
        assert isinstance(bgp_routing, BGPRoutingResponseModel)
        assert bgp_routing.backbone_routing == BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING
        assert isinstance(bgp_routing.routing_preference, DefaultRoutingModel)
        assert bgp_routing.accept_route_over_SC is False
        assert bgp_routing.outbound_routes_for_services == ["10.0.0.0/24"]
        assert bgp_routing.add_host_route_to_ike_peer is False
        assert bgp_routing.withdraw_static_route is False

    def test_get_with_hot_potato_routing(self):
        """Test getting BGP routing settings with hot potato routing."""
        mock_response = BGPRoutingResponseFactory(routing_preference={"hot_potato_routing": {}})
        self.mock_scm.get.return_value = mock_response

        bgp_routing = self.client.get()

        assert isinstance(bgp_routing.routing_preference, HotPotatoRoutingModel)
        assert bgp_routing.routing_preference.hot_potato_routing == {}

    def test_get_response_not_dict(self):
        """Test handling when response is not a dictionary."""
        self.mock_scm.get.return_value = "not a dictionary"

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.get()

        assert "Response is not a dictionary" in str(exc_info.value)

    def test_get_empty_response(self):
        """Test handling when response is empty (all fields optional)."""
        self.mock_scm.get.return_value = {}

        bgp_routing = self.client.get()

        assert isinstance(bgp_routing, BGPRoutingResponseModel)
        assert bgp_routing.routing_preference is None
        assert bgp_routing.backbone_routing is None
        assert bgp_routing.outbound_routes_for_services == []

    def test_get_partial_response(self):
        """Test handling when response has only some fields."""
        mock_response = {"backbone_routing": "no-asymmetric-routing"}
        self.mock_scm.get.return_value = mock_response

        bgp_routing = self.client.get()

        assert isinstance(bgp_routing, BGPRoutingResponseModel)
        assert bgp_routing.backbone_routing == BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING
        assert bgp_routing.routing_preference is None

    def test_get_error(self):
        """Test error handling during get operation."""
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=404,
            error_code="E005",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.get()

        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Object not found"
        assert error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"

    def test_get_invalid_routing_preference(self):
        """Test handling an unknown routing_preference format."""
        mock_response = BGPRoutingResponseFactory()
        mock_response["routing_preference"] = {"unknown_type": {}}
        self.mock_scm.get.return_value = mock_response

        # With optional fields, unknown routing_preference format returns None
        result = self.client.get()
        assert isinstance(result, BGPRoutingResponseModel)
        # The unknown routing_preference is not converted to a model
        assert result.routing_preference is None

    def test_get_none_routing_preference(self):
        """Test handling a None routing_preference value."""
        mock_response = BGPRoutingResponseFactory()
        mock_response.pop("routing_preference")
        self.mock_scm.get.return_value = mock_response

        # All fields are optional, so this should succeed
        result = self.client.get()
        assert isinstance(result, BGPRoutingResponseModel)
        assert result.routing_preference is None


class TestBGPRoutingCreate(TestBGPRoutingBase):
    """Tests for creating BGP routing settings."""

    def test_create_valid(self):
        """Test creating BGP routing settings successfully."""
        test_data = BGPRoutingCreateApiFactory()
        mock_response = BGPRoutingResponseFactory()

        self.mock_scm.put.return_value = mock_response
        bgp_routing = self.client.create(test_data)

        # Verify the API was called
        assert self.mock_scm.put.call_count == 1
        args, kwargs = self.mock_scm.put.call_args
        assert args[0] == "/config/deployment/v1/bgp-routing"

        # Verify the payload contains the expected data
        payload = kwargs["json"]
        assert "backbone_routing" in payload
        assert payload["backbone_routing"] == "no-asymmetric-routing"
        assert "routing_preference" in payload
        assert "default" in payload["routing_preference"]

        # Verify the response model is correct
        assert isinstance(bgp_routing, BGPRoutingResponseModel)
        assert bgp_routing.backbone_routing == BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING
        assert isinstance(bgp_routing.routing_preference, DefaultRoutingModel)

    def test_create_with_hot_potato_routing(self):
        """Test creating BGP routing with hot potato routing."""
        test_data = BGPRoutingCreateApiFactory(routing_preference={"hot_potato_routing": {}})
        mock_response = BGPRoutingResponseFactory(routing_preference={"hot_potato_routing": {}})

        self.mock_scm.put.return_value = mock_response
        bgp_routing = self.client.create(test_data)

        assert isinstance(bgp_routing.routing_preference, HotPotatoRoutingModel)

    def test_create_empty_data(self):
        """Test creating with empty data raises error."""
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.create({})

        assert "Empty configuration data" in str(exc_info.value)

    def test_create_invalid_data(self):
        """Test creating with invalid data raises error."""
        invalid_data = {"backbone_routing": "invalid-value"}

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.create(invalid_data)

        # The error message contains validation details
        assert "validation error" in str(exc_info.value).lower() or "Invalid" in str(exc_info.value)

    def test_create_response_not_dict(self):
        """Test handling when response is not a dictionary."""
        test_data = BGPRoutingCreateApiFactory()
        self.mock_scm.put.return_value = "not a dictionary"

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.create(test_data)

        assert "Response is not a dictionary" in str(exc_info.value)

    def test_create_error(self):
        """Test error handling during create operation."""
        test_data = BGPRoutingCreateApiFactory()

        self.mock_scm.put.side_effect = raise_mock_http_error(
            status_code=400,
            error_code="E003",
            message="Create failed",
            error_type="Malformed Command",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.create(test_data)

        assert exc_info.value.response.status_code == 400

    def test_create_invalid_routing_preference(self):
        """Test creating with an invalid routing_preference format."""
        test_data = BGPRoutingCreateApiFactory()
        test_data["routing_preference"] = {"unknown_type": {}}

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.create(test_data)

        assert "routing_preference" in str(exc_info.value)

    def test_create_with_enum_instance(self):
        """Test creating with an actual enum instance instead of string."""
        test_data = BGPRoutingCreateApiFactory()
        test_data["backbone_routing"] = BackboneRoutingEnum.ASYMMETRIC_ROUTING_ONLY
        mock_response = BGPRoutingResponseFactory(backbone_routing="asymmetric-routing-only")

        self.mock_scm.put.return_value = mock_response
        self.client.create(test_data)

        # Verify the API was called with the correct enum value
        args, kwargs = self.mock_scm.put.call_args
        payload = kwargs["json"]
        assert payload["backbone_routing"] == "asymmetric-routing-only"

    def test_create_with_routing_preference_model_instances(self):
        """Test creating with routing_preference as model instances."""
        # Test with DefaultRoutingModel
        test_data = BGPRoutingCreateApiFactory()
        test_data["routing_preference"] = DefaultRoutingModel()
        self.mock_scm.put.return_value = BGPRoutingResponseFactory()

        result = self.client.create(test_data)
        assert isinstance(result, BGPRoutingResponseModel)

        # Verify payload format
        args, kwargs = self.mock_scm.put.call_args
        payload = kwargs["json"]
        assert "routing_preference" in payload
        assert "default" in payload["routing_preference"]

        # Test with HotPotatoRoutingModel
        test_data = BGPRoutingCreateApiFactory()
        test_data["routing_preference"] = HotPotatoRoutingModel()
        mock_response = BGPRoutingResponseFactory(routing_preference={"hot_potato_routing": {}})

        self.mock_scm.put.return_value = mock_response

        result = self.client.create(test_data)
        assert isinstance(result, BGPRoutingResponseModel)
        assert isinstance(result.routing_preference, HotPotatoRoutingModel)

        # Verify payload format
        args, kwargs = self.mock_scm.put.call_args
        payload = kwargs["json"]
        assert "routing_preference" in payload
        assert "hot_potato_routing" in payload["routing_preference"]

    def test_create_invalid_routing_preference_model(self):
        """Test handling of invalid routing_preference model instances."""

        class InvalidModel:
            def __init__(self):
                pass

        test_data = BGPRoutingCreateApiFactory()
        test_data["routing_preference"] = InvalidModel()

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.create(test_data)

        error = exc_info.value
        assert error.http_status_code == 400
        assert error.error_code == "E003"


class TestBGPRoutingUpdate(TestBGPRoutingBase):
    """Tests for updating BGP routing settings."""

    def test_update_valid(self):
        """Test updating BGP routing settings successfully."""
        test_data = BGPRoutingUpdateApiFactory()
        mock_response = BGPRoutingResponseFactory(
            backbone_routing="asymmetric-routing-only",
            routing_preference={"hot_potato_routing": {}},
            accept_route_over_SC=True,
            outbound_routes_for_services=["192.168.1.0/24", "10.0.0.0/24"],
            add_host_route_to_ike_peer=True,
            withdraw_static_route=True,
        )

        self.mock_scm.put.return_value = mock_response
        bgp_routing = self.client.update(test_data)

        # Verify the API was called
        assert self.mock_scm.put.call_count == 1
        args, kwargs = self.mock_scm.put.call_args
        assert args[0] == "/config/deployment/v1/bgp-routing"

        # Verify the payload contains the expected data
        payload = kwargs["json"]
        assert "backbone_routing" in payload
        assert payload["backbone_routing"] == "asymmetric-routing-only"
        assert "routing_preference" in payload
        assert "hot_potato_routing" in payload["routing_preference"]

        # Verify the response model is correct
        assert isinstance(bgp_routing, BGPRoutingResponseModel)
        assert bgp_routing.backbone_routing == BackboneRoutingEnum.ASYMMETRIC_ROUTING_ONLY
        assert isinstance(bgp_routing.routing_preference, HotPotatoRoutingModel)
        assert bgp_routing.accept_route_over_SC is True
        assert bgp_routing.outbound_routes_for_services == ["192.168.1.0/24", "10.0.0.0/24"]
        assert bgp_routing.add_host_route_to_ike_peer is True
        assert bgp_routing.withdraw_static_route is True

    def test_update_partial(self):
        """Test updating only some fields."""
        test_data = {"backbone_routing": "asymmetric-routing-only", "accept_route_over_SC": True}
        mock_response = BGPRoutingResponseFactory(
            backbone_routing="asymmetric-routing-only", accept_route_over_SC=True
        )

        self.mock_scm.put.return_value = mock_response
        bgp_routing = self.client.update(test_data)

        assert bgp_routing.backbone_routing == BackboneRoutingEnum.ASYMMETRIC_ROUTING_ONLY
        assert bgp_routing.accept_route_over_SC is True

    def test_update_empty_data(self):
        """Test updating with empty data raises error."""
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.update({})

        assert "Empty configuration data" in str(exc_info.value)

    def test_update_invalid_data(self):
        """Test updating with invalid data raises error."""
        invalid_data = {"backbone_routing": "invalid-value"}

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.update(invalid_data)

        # The error message contains validation details
        assert "validation error" in str(exc_info.value).lower() or "Invalid" in str(exc_info.value)

    def test_update_response_not_dict(self):
        """Test handling when response is not a dictionary."""
        test_data = BGPRoutingUpdateApiFactory()
        self.mock_scm.put.return_value = "not a dictionary"

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.update(test_data)

        assert "Response is not a dictionary" in str(exc_info.value)

    def test_update_error(self):
        """Test error handling during update operation."""
        test_data = BGPRoutingUpdateApiFactory()

        self.mock_scm.put.side_effect = raise_mock_http_error(
            status_code=400,
            error_code="E003",
            message="Update failed",
            error_type="Malformed Command",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.update(test_data)

        assert exc_info.value.response.status_code == 400

    def test_update_invalid_routing_preference(self):
        """Test updating with an invalid routing_preference format."""
        test_data = BGPRoutingUpdateApiFactory()
        test_data["routing_preference"] = {"unknown_type": {}}

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.update(test_data)

        assert "routing_preference" in str(exc_info.value)

    def test_update_invalid_routing_preference_object(self):
        """Test updating with an invalid routing_preference object."""

        class InvalidModel:
            def __init__(self):
                pass

        test_data = BGPRoutingUpdateApiFactory()
        test_data["routing_preference"] = InvalidModel()

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.update(test_data)

        error = exc_info.value
        assert error.http_status_code == 400
        assert error.error_code == "E003"

    def test_update_with_string_outbound_routes(self):
        """Test updating with a string value for outbound_routes_for_services."""
        test_data = {
            "backbone_routing": "asymmetric-routing-only",
            "outbound_routes_for_services": "10.0.0.0/24",
        }
        mock_response = BGPRoutingResponseFactory(
            backbone_routing="asymmetric-routing-only",
            outbound_routes_for_services=["10.0.0.0/24"],
        )

        self.mock_scm.put.return_value = mock_response
        bgp_routing = self.client.update(test_data)

        # Verify the string was converted to a list in the request
        args, kwargs = self.mock_scm.put.call_args
        payload = kwargs["json"]
        assert isinstance(payload["outbound_routes_for_services"], list)
        assert payload["outbound_routes_for_services"] == ["10.0.0.0/24"]

        # Verify response model
        assert bgp_routing.outbound_routes_for_services == ["10.0.0.0/24"]

    def test_update_with_enum_backbone_routing(self):
        """Test updating with an enum instance for backbone_routing."""
        test_data = {"backbone_routing": BackboneRoutingEnum.ASYMMETRIC_ROUTING_WITH_LOAD_SHARE}
        mock_response = BGPRoutingResponseFactory(
            backbone_routing="asymmetric-routing-with-load-share"
        )

        self.mock_scm.put.return_value = mock_response
        bgp_routing = self.client.update(test_data)

        # Verify the enum was converted to a string in the request
        args, kwargs = self.mock_scm.put.call_args
        payload = kwargs["json"]
        assert payload["backbone_routing"] == "asymmetric-routing-with-load-share"

        # Verify response model contains the enum
        assert (
            bgp_routing.backbone_routing == BackboneRoutingEnum.ASYMMETRIC_ROUTING_WITH_LOAD_SHARE
        )

    def test_update_with_default_routing_dict(self):
        """Test updating with default routing preference as a dict."""
        test_data = {
            "backbone_routing": BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
            "routing_preference": {"default": {"custom_setting": "test_value"}},
        }

        mock_response = BGPRoutingResponseFactory(
            backbone_routing="no-asymmetric-routing", routing_preference={"default": {}}
        )

        self.mock_scm.put.return_value = mock_response

        result = self.client.update(test_data)

        assert isinstance(result, BGPRoutingResponseModel)
        assert isinstance(result.routing_preference, DefaultRoutingModel)

        # Verify the API call payload contains transformed routing_preference
        args, kwargs = self.mock_scm.put.call_args
        payload = kwargs["json"]
        assert "routing_preference" in payload
        assert "default" in payload["routing_preference"]


class TestBGPRoutingDelete(TestBGPRoutingBase):
    """Tests for resetting BGP routing settings (delete method)."""

    def test_delete_valid(self):
        """Test resetting BGP routing settings successfully."""
        self.mock_scm.put.return_value = None
        self.client.delete()

        self.mock_scm.put.assert_called_once()
        # Check if the default config was sent correctly
        call_args = self.mock_scm.put.call_args[1]
        assert call_args["json"]["backbone_routing"] == "no-asymmetric-routing"
        assert call_args["json"]["routing_preference"] == {"default": {}}
        assert call_args["json"]["accept_route_over_SC"] is False
        assert call_args["json"]["outbound_routes_for_services"] == []
        assert call_args["json"]["add_host_route_to_ike_peer"] is False
        assert call_args["json"]["withdraw_static_route"] is False

    def test_delete_error(self):
        """Test error handling during delete operation."""
        self.mock_scm.put.side_effect = raise_mock_http_error(
            status_code=500,
            error_code="E500",
            message="Internal Error",
            error_type="Server Error",
        )

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.delete()

        error = exc_info.value
        assert error.http_status_code == 500
        assert error.error_code == "E003"
        assert "Error resetting BGP routing configuration" in error.message

    def test_delete_with_success_response(self):
        """Test delete operation with a success response."""
        mock_response = {"status": "success", "message": "Configuration reset"}
        self.mock_scm.put.return_value = mock_response

        self.client.delete()

        # Verify the API was called with the default configuration
        call_args = self.mock_scm.put.call_args[1]
        assert call_args["json"]["backbone_routing"] == "no-asymmetric-routing"
        assert call_args["json"]["routing_preference"] == {"default": {}}

    def test_delete_endpoint_url(self):
        """Test that delete uses the correct endpoint URL."""
        self.mock_scm.put.return_value = None
        self.client.delete()

        args, _ = self.mock_scm.put.call_args
        assert args[0] == "/config/deployment/v1/bgp-routing"
