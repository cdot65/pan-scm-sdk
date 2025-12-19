"""Test factories for BGP Routing deployment objects."""

# Standard library imports
from typing import Any, Dict, List, Union

# External libraries
import factory  # type: ignore
from faker import Faker

# Local SDK imports
from scm.models.deployment.bgp_routing import (
    BackboneRoutingEnum,
    BGPRoutingBaseModel,
    BGPRoutingCreateModel,
    BGPRoutingUpdateModel,
    DefaultRoutingModel,
    HotPotatoRoutingModel,
)

fake = Faker()


# ----------------------------------------------------------------------------
# Routing preference factories
# ----------------------------------------------------------------------------


class DefaultRoutingModelFactory(factory.Factory):
    """Factory for creating DefaultRoutingModel instances."""

    class Meta:
        """Factory configuration."""

        model = DefaultRoutingModel

    default = factory.Dict({})


class HotPotatoRoutingModelFactory(factory.Factory):
    """Factory for creating HotPotatoRoutingModel instances."""

    class Meta:
        """Factory configuration."""

        model = HotPotatoRoutingModel

    hot_potato_routing = factory.Dict({})


# ----------------------------------------------------------------------------
# BGP Routing factories
# ----------------------------------------------------------------------------


class BGPRoutingBaseFactory(factory.Factory):
    """Base factory for BGP Routing objects with common fields."""

    class Meta:
        """Factory configuration."""

        model = BGPRoutingBaseModel
        abstract = True

    routing_preference = None
    backbone_routing = None
    accept_route_over_SC = None
    outbound_routes_for_services = None
    add_host_route_to_ike_peer = None
    withdraw_static_route = None


# ----------------------------------------------------------------------------
# BGP Routing API factories for testing SCM API interactions.
# These return dictionaries for compatibility with existing tests.
# ----------------------------------------------------------------------------


class BGPRoutingCreateApiFactory:
    """Factory for creating dictionaries suitable for BGPRoutingCreateModel.

    with the structure used by the Python SDK calls.
    """

    def __call__(self, **kwargs) -> Dict[str, Any]:
        """Create dictionary representation of a BGP routing create request."""
        data = {
            "backbone_routing": kwargs.get("backbone_routing", "no-asymmetric-routing"),
            "routing_preference": kwargs.get("routing_preference", {"default": {}}),
            "accept_route_over_SC": kwargs.get("accept_route_over_SC", False),
            "outbound_routes_for_services": kwargs.get(
                "outbound_routes_for_services", ["10.0.0.0/24"]
            ),
            "add_host_route_to_ike_peer": kwargs.get("add_host_route_to_ike_peer", False),
            "withdraw_static_route": kwargs.get("withdraw_static_route", False),
        }

        # Update with any other kwargs
        for key, value in kwargs.items():
            if key not in data:
                data[key] = value

        return data

    def with_hot_potato_routing(self, **kwargs) -> Dict[str, Any]:
        """Create a dictionary with hot potato routing preference.

        Args:
            **kwargs: Additional attributes to override in the data

        Returns:
            Dict[str, Any]: Data with hot potato routing preference

        """
        data = self(**kwargs)
        data["routing_preference"] = {"hot_potato_routing": {}}
        return data

    def with_asymmetric_routing_only(self, **kwargs) -> Dict[str, Any]:
        """Create a dictionary with asymmetric routing only.

        Args:
            **kwargs: Additional attributes to override in the data

        Returns:
            Dict[str, Any]: Data with asymmetric routing only

        """
        data = self(**kwargs)
        data["backbone_routing"] = "asymmetric-routing-only"
        return data

    def with_asymmetric_routing_with_load_share(self, **kwargs) -> Dict[str, Any]:
        """Create a dictionary with asymmetric routing with load share.

        Args:
            **kwargs: Additional attributes to override in the data

        Returns:
            Dict[str, Any]: Data with asymmetric routing with load share

        """
        data = self(**kwargs)
        data["backbone_routing"] = "asymmetric-routing-with-load-share"
        return data

    def with_custom_outbound_routes(self, routes: List[str], **kwargs) -> Dict[str, Any]:
        """Create a dictionary with custom outbound routes.

        Args:
            routes: List of CIDR routes
            **kwargs: Additional attributes to override in the data

        Returns:
            Dict[str, Any]: Data with custom outbound routes

        """
        data = self(**kwargs)
        data["outbound_routes_for_services"] = routes
        return data


class BGPRoutingUpdateApiFactory:
    """Factory for creating dictionaries suitable for BGPRoutingUpdateModel.

    with the structure used by the Python SDK calls.
    """

    def __call__(self, **kwargs) -> Dict[str, Any]:
        """Create dictionary representation of a BGP routing update request."""
        data = {
            "backbone_routing": kwargs.get("backbone_routing", "asymmetric-routing-only"),
            "routing_preference": kwargs.get("routing_preference", {"hot_potato_routing": {}}),
            "accept_route_over_SC": kwargs.get("accept_route_over_SC", True),
            "outbound_routes_for_services": kwargs.get(
                "outbound_routes_for_services", ["192.168.1.0/24", "10.0.0.0/24"]
            ),
            "add_host_route_to_ike_peer": kwargs.get("add_host_route_to_ike_peer", True),
            "withdraw_static_route": kwargs.get("withdraw_static_route", True),
        }

        # Update with any other kwargs
        for key, value in kwargs.items():
            if key not in data:
                data[key] = value

        return data

    def with_default_routing(self, **kwargs) -> Dict[str, Any]:
        """Create a dictionary with default routing preference.

        Args:
            **kwargs: Additional attributes to override in the data

        Returns:
            Dict[str, Any]: Data with default routing preference

        """
        data = self(**kwargs)
        data["routing_preference"] = {"default": {}}
        return data

    def with_no_asymmetric_routing(self, **kwargs) -> Dict[str, Any]:
        """Create a dictionary with no asymmetric routing.

        Args:
            **kwargs: Additional attributes to override in the data

        Returns:
            Dict[str, Any]: Data with no asymmetric routing

        """
        data = self(**kwargs)
        data["backbone_routing"] = "no-asymmetric-routing"
        return data

    def partial_update(self, fields: List[str], **kwargs) -> Dict[str, Any]:
        """Create a dictionary with only specified fields for a partial update.

        Args:
            fields: List of field names to include in the update
            **kwargs: Values for the fields

        Returns:
            Dict[str, Any]: Partial update data

        """
        data = {}
        full_data = self(**kwargs)

        for field in fields:
            if field in full_data:
                data[field] = full_data[field]

        return data


class BGPRoutingResponseFactory:
    """Factory for creating dictionaries suitable for BGPRoutingResponseModel.

    to mimic the actual data returned by the SCM API.
    """

    def __call__(self, **kwargs) -> Dict[str, Any]:
        """Create dictionary representation of a BGP routing response."""
        data = {
            "backbone_routing": kwargs.get("backbone_routing", "no-asymmetric-routing"),
            "routing_preference": kwargs.get("routing_preference", {"default": {}}),
            "accept_route_over_SC": kwargs.get("accept_route_over_SC", False),
            "outbound_routes_for_services": kwargs.get(
                "outbound_routes_for_services", ["10.0.0.0/24"]
            ),
            "add_host_route_to_ike_peer": kwargs.get("add_host_route_to_ike_peer", False),
            "withdraw_static_route": kwargs.get("withdraw_static_route", False),
        }

        # Update with any other kwargs
        for key, value in kwargs.items():
            if key not in data:
                data[key] = value

        return data

    def with_hot_potato_routing(self, **kwargs) -> Dict[str, Any]:
        """Create a response dictionary with hot potato routing preference.

        Args:
            **kwargs: Additional attributes to override in the data

        Returns:
            Dict[str, Any]: Response data with hot potato routing preference

        """
        data = self(**kwargs)
        data["routing_preference"] = {"hot_potato_routing": {}}
        return data

    def from_request(
        self,
        request_data: Union[Dict[str, Any], BGPRoutingCreateModel, BGPRoutingUpdateModel],
        **kwargs,
    ) -> Dict[str, Any]:
        """Create a response dictionary based on a request.

        This is useful for simulating the API's response to a create or update request.

        Args:
            request_data: The create/update request dict or model to base the response on
            **kwargs: Additional attributes to override in the response

        Returns:
            Dict[str, Any]: Response data based on the request

        """
        # Convert model to dict if needed
        if hasattr(request_data, "model_dump"):
            request_dict = request_data.model_dump()
        else:
            request_dict = dict(request_data)

        # Create response based on request
        response_data = self(**request_dict)

        # Override with any additional kwargs
        for key, value in kwargs.items():
            response_data[key] = value

        return response_data

    def build_empty(self) -> Dict[str, Any]:
        """Create an empty response (for testing partial API responses).

        Returns:
            Dict[str, Any]: Empty response data

        """
        return {}

    def build_partial(self, **kwargs) -> Dict[str, Any]:
        """Create a partial response with only specified fields.

        Args:
            **kwargs: Fields to include in the response

        Returns:
            Dict[str, Any]: Partial response data

        """
        return kwargs


# Create instances of the factories so they can be called directly
BGPRoutingCreateApiFactory = BGPRoutingCreateApiFactory()
BGPRoutingUpdateApiFactory = BGPRoutingUpdateApiFactory()
BGPRoutingResponseFactory = BGPRoutingResponseFactory()


# ----------------------------------------------------------------------------
# Factories specifically for model validation (Pydantic) tests
# ----------------------------------------------------------------------------


class BGPRoutingCreateModelFactory(factory.Factory):
    """Factory for creating dictionary data suitable for instantiating BGPRoutingCreateModel.

    Note: BGPRoutingCreateModel is now an alias for BGPRoutingUpdateModel since
    the API only supports GET/PUT operations (no POST).
    """

    class Meta:
        """Factory configuration."""

        model = dict

    backbone_routing = BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING
    routing_preference = {"default": {}}
    accept_route_over_SC = False
    outbound_routes_for_services = ["10.0.0.0/24"]
    add_host_route_to_ike_peer = False
    withdraw_static_route = False

    @classmethod
    def build_valid(cls, **kwargs) -> Dict[str, Any]:
        """Return a valid data dict with all expected attributes.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Valid data for BGPRoutingCreateModel

        """
        data = {
            "backbone_routing": BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
            "routing_preference": {"default": {}},
            "accept_route_over_SC": False,
            "outbound_routes_for_services": ["10.0.0.0/24"],
            "add_host_route_to_ike_peer": False,
            "withdraw_static_route": False,
        }
        data.update(kwargs)
        return data

    @classmethod
    def build_with_hot_potato_routing(cls, **kwargs) -> Dict[str, Any]:
        """Return a data dict with hot potato routing.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Data for BGPRoutingCreateModel with hot potato routing

        """
        data = cls.build_valid(**kwargs)
        data["routing_preference"] = {"hot_potato_routing": {}}
        return data

    @classmethod
    def build_with_default_model_objects(cls, **kwargs) -> Dict[str, Any]:
        """Return a data dict using DefaultRoutingModel object instead of dict.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Data for BGPRoutingCreateModel with DefaultRoutingModel object

        """
        data = cls.build_valid(**kwargs)
        data["routing_preference"] = DefaultRoutingModel()
        return data

    @classmethod
    def build_with_invalid_backbone_routing(cls, **kwargs) -> Dict[str, Any]:
        """Return a data dict with invalid backbone routing value.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Invalid data for BGPRoutingCreateModel

        """
        data = cls.build_valid(**kwargs)
        data["backbone_routing"] = "invalid-routing-value"
        return data


class BGPRoutingUpdateModelFactory(factory.Factory):
    """Factory for creating dictionary data suitable for instantiating BGPRoutingUpdateModel.

    Useful for direct Pydantic validation tests.
    """

    class Meta:
        """Factory configuration."""

        model = dict

    backbone_routing = BackboneRoutingEnum.ASYMMETRIC_ROUTING_ONLY
    routing_preference = {"hot_potato_routing": {}}
    accept_route_over_SC = True
    outbound_routes_for_services = ["192.168.1.0/24", "10.0.0.0/24"]
    add_host_route_to_ike_peer = True
    withdraw_static_route = True

    @classmethod
    def build_valid(cls, **kwargs) -> Dict[str, Any]:
        """Return a valid data dict with all expected attributes.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Valid data for BGPRoutingUpdateModel

        """
        data = {
            "backbone_routing": BackboneRoutingEnum.ASYMMETRIC_ROUTING_ONLY,
            "routing_preference": {"hot_potato_routing": {}},
            "accept_route_over_SC": True,
            "outbound_routes_for_services": ["192.168.1.0/24", "10.0.0.0/24"],
            "add_host_route_to_ike_peer": True,
            "withdraw_static_route": True,
        }
        data.update(kwargs)
        return data

    @classmethod
    def build_partial(cls, fields: List[str], **kwargs) -> Dict[str, Any]:
        """Return a partial update data dict with only specified fields.

        Args:
            fields: List of field names to include in the update
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Partial data for BGPRoutingUpdateModel

        """
        data = {}
        full_data = cls.build_valid(**kwargs)

        for field in fields:
            if field in full_data:
                data[field] = full_data[field]

        return data

    @classmethod
    def build_with_default_routing(cls, **kwargs) -> Dict[str, Any]:
        """Return a data dict with default routing preference.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Data for BGPRoutingUpdateModel with default routing

        """
        data = cls.build_valid(**kwargs)
        data["routing_preference"] = {"default": {}}
        return data

    @classmethod
    def build_empty(cls) -> Dict[str, Any]:
        """Return an empty data dict for testing empty updates.

        Returns:
            Dict[str, Any]: Empty data for BGPRoutingUpdateModel

        """
        return {}


class BGPRoutingResponseModelFactory(factory.Factory):
    """Factory for creating dictionary data suitable for instantiating BGPRoutingResponseModel.

    Useful for direct Pydantic validation tests.
    """

    class Meta:
        """Factory configuration."""

        model = dict

    backbone_routing = BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING
    routing_preference = {"default": {}}
    accept_route_over_SC = False
    outbound_routes_for_services = ["10.0.0.0/24"]
    add_host_route_to_ike_peer = False
    withdraw_static_route = False

    @classmethod
    def build_valid(cls, **kwargs) -> Dict[str, Any]:
        """Return a valid data dict for a response model.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Valid data for BGPRoutingResponseModel

        """
        data = {
            "backbone_routing": BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
            "routing_preference": {"default": {}},
            "accept_route_over_SC": False,
            "outbound_routes_for_services": ["10.0.0.0/24"],
            "add_host_route_to_ike_peer": False,
            "withdraw_static_route": False,
        }
        data.update(kwargs)
        return data

    @classmethod
    def build_with_hot_potato_routing(cls, **kwargs) -> Dict[str, Any]:
        """Return a data dict with hot potato routing preference.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Valid data for BGPRoutingResponseModel with hot potato routing

        """
        data = cls.build_valid(**kwargs)
        data["routing_preference"] = {"hot_potato_routing": {}}
        return data

    @classmethod
    def build_with_model_objects(cls, **kwargs) -> Dict[str, Any]:
        """Return a data dict with proper model objects instead of dicts.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Valid data for BGPRoutingResponseModel with model objects

        """
        data = cls.build_valid(**kwargs)

        # Convert dict routing_preference to actual model object
        if "routing_preference" in data:
            routing_pref = data["routing_preference"]
            if "default" in routing_pref:
                data["routing_preference"] = DefaultRoutingModel(**routing_pref)
            elif "hot_potato_routing" in routing_pref:
                data["routing_preference"] = HotPotatoRoutingModel(**routing_pref)

        return data

    @classmethod
    def build_empty(cls) -> Dict[str, Any]:
        """Return an empty data dict for testing empty responses.

        Returns:
            Dict[str, Any]: Empty data for BGPRoutingResponseModel

        """
        return {}

    @classmethod
    def build_partial(cls, **kwargs) -> Dict[str, Any]:
        """Return a partial data dict with only specified fields.

        Args:
            **kwargs: Fields to include in the response

        Returns:
            Dict[str, Any]: Partial data for BGPRoutingResponseModel

        """
        return kwargs
