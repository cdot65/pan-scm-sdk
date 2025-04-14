"""Test factories for Remote Networks deployment objects."""

# Standard library imports
from typing import Any, Dict, Union
from uuid import uuid4

# External libraries
import factory  # type: ignore
from faker import Faker

# Local SDK imports
from scm.models.deployment.remote_networks import (
    EcmpLoadBalancingEnum,
    EcmpTunnelModel,
    PeeringTypeEnum,
    RemoteNetworkBaseModel,
    RemoteNetworkCreateModel,
    RemoteNetworkResponseModel,
    RemoteNetworkUpdateModel,
)

fake = Faker()


# Base factory for all remote network models
class RemoteNetworkBaseFactory(factory.Factory):
    """Base factory for Remote Network objects with common fields."""

    class Meta:
        model = RemoteNetworkBaseModel
        abstract = True

    # Required fields
    name = factory.Sequence(lambda n: f"remote_network_{n}")
    region = "us-east-1"
    license_type = "FWAAS-AGGREGATE"  # Default from schema

    # Optional fields
    description = fake.sentence()
    subnets = []
    spn_name = "spn-test"  # Required when license_type is FWAAS-AGGREGATE

    # ECMP related
    ecmp_load_balancing = EcmpLoadBalancingEnum.disable
    ecmp_tunnels = None

    # Non-ECMP ipsec tunnel
    ipsec_tunnel = "ipsec-tunnel-default"  # Required when ecmp_load_balancing is disable
    secondary_ipsec_tunnel = None
    protocol = None

    # Container fields
    folder = "Texas"
    snippet = None
    device = None


# ----------------------------------------------------------------------------
# Remote Network API factories for testing SCM API interactions.
# ----------------------------------------------------------------------------


class RemoteNetworkCreateApiFactory(RemoteNetworkBaseFactory):
    """
    Factory for creating RemoteNetworkCreateModel instances with
    the structure used by the Python SDK calls.
    """

    class Meta:
        model = RemoteNetworkCreateModel

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """
        Create a RemoteNetworkCreateModel with snippet container.

        Args:
            snippet: Name of the snippet container
            **kwargs: Additional attributes to override in the model

        Returns:
            RemoteNetworkCreateModel: A model instance with snippet container
        """
        return cls(
            folder=None,
            snippet=snippet,
            device=None,
            **kwargs,
        )

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """
        Create a RemoteNetworkCreateModel with device container.

        Args:
            device: Name of the device container
            **kwargs: Additional attributes to override in the model

        Returns:
            RemoteNetworkCreateModel: A model instance with device container
        """
        return cls(
            folder=None,
            snippet=None,
            device=device,
            **kwargs,
        )

    @classmethod
    def with_ecmp_enabled(cls, ecmp_tunnel_count=2, **kwargs):
        """
        Create a RemoteNetworkCreateModel with ecmp_load_balancing=enable and
        the required ecmp_tunnels list.

        Args:
            ecmp_tunnel_count: Number of ECMP tunnels to create
            **kwargs: Additional attributes to override in the model

        Returns:
            RemoteNetworkCreateModel: A model instance with ECMP enabled
        """
        # Generate sample EcmpTunnelModel entries
        tunnels = []
        for i in range(ecmp_tunnel_count):
            tunnels.append(
                {
                    "name": f"ecmp_tunnel_{i}",
                    "ipsec_tunnel": f"ipsec-tunnel-ecmp-{i}",
                }
            )

        return cls(
            ecmp_load_balancing=EcmpLoadBalancingEnum.enable,
            ecmp_tunnels=tunnels,
            ipsec_tunnel=None,  # must be None if ecmp is enabled
            **kwargs,
        )

    @classmethod
    def without_spn_name(cls, **kwargs):
        """
        Create a RemoteNetworkCreateModel with license_type=FWAAS-AGGREGATE
        but missing spn_name (which will raise validation error).

        Args:
            **kwargs: Additional attributes to override in the model

        Returns:
            RemoteNetworkCreateModel: A model instance missing required spn_name
        """
        return cls(
            spn_name=None,
            **kwargs,
        )

    @classmethod
    def with_protocol_bgp(cls, **kwargs):
        """
        Create a RemoteNetworkCreateModel with protocol containing a BgpModel.

        Args:
            **kwargs: Additional attributes to override in the model

        Returns:
            RemoteNetworkCreateModel: A model instance with BGP protocol
        """
        protocol_data = {
            "bgp": {
                "enable": True,
                "local_ip_address": "192.0.2.1",
                "peer_ip_address": "203.0.113.5",
                "peer_as": "65001",
                "peering_type": "exchange-v4-over-v4",
            }
        }
        return cls(
            protocol=protocol_data,
            **kwargs,
        )


class RemoteNetworkUpdateApiFactory(RemoteNetworkBaseFactory):
    """
    Factory for creating RemoteNetworkUpdateModel instances with
    the structure used by the Python SDK calls.
    """

    class Meta:
        model = RemoteNetworkUpdateModel

    # From the schema, id is required for update
    id = factory.LazyFunction(lambda: str(uuid4()))

    @classmethod
    def with_ecmp_enabled(cls, ecmp_tunnel_count=2, **kwargs):
        """
        Enable ecmp_load_balancing and provide ecmp_tunnels.

        Args:
            ecmp_tunnel_count: Number of ECMP tunnels to create
            **kwargs: Additional attributes to override in the model

        Returns:
            RemoteNetworkUpdateModel: A model instance with ECMP enabled
        """
        tunnels = []
        for i in range(ecmp_tunnel_count):
            tunnels.append(
                {
                    "name": f"ecmp_tunnel_{i}",
                    "ipsec_tunnel": f"ipsec-tunnel-ecmp-{i}",
                }
            )
        return cls(
            ecmp_load_balancing=EcmpLoadBalancingEnum.enable,
            ecmp_tunnels=tunnels,
            ipsec_tunnel=None,
            **kwargs,
        )

    @classmethod
    def without_spn_name(cls, **kwargs):
        """
        Create a RemoteNetworkUpdateModel with license_type=FWAAS-AGGREGATE
        but missing spn_name (will raise validation error).

        Args:
            **kwargs: Additional attributes to override in the model

        Returns:
            RemoteNetworkUpdateModel: A model instance missing required spn_name
        """
        return cls(
            spn_name=None,
            **kwargs,
        )

    @classmethod
    def with_protocol_bgp(cls, **kwargs):
        """
        Create a RemoteNetworkUpdateModel with protocol containing a BgpModel.

        Args:
            **kwargs: Additional attributes to override in the model

        Returns:
            RemoteNetworkUpdateModel: A model instance with BGP protocol
        """
        protocol_data = {
            "bgp": {
                "enable": True,
                "local_ip_address": "192.0.2.99",
                "peer_ip_address": "198.51.100.5",
                "peer_as": "65055",
                "peering_type": "exchange-v4-over-v4-v6-over-v6",
            }
        }
        return cls(
            protocol=protocol_data,
            **kwargs,
        )


class RemoteNetworkResponseFactory(RemoteNetworkBaseFactory):
    """
    Factory for creating RemoteNetworkResponseModel instances
    to mimic the actual data returned by the SCM API.
    """

    class Meta:
        model = RemoteNetworkResponseModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    name = factory.Sequence(lambda n: f"remote_network_{n}")
    region = "us-east-1"
    license_type = "FWAAS-AGGREGATE"
    spn_name = "spn-response"
    ecmp_load_balancing = EcmpLoadBalancingEnum.disable
    ipsec_tunnel = "ipsec-tunnel-response"

    @classmethod
    def with_protocol_bgp(cls, **kwargs):
        """
        Create an instance with BGP protocol enabled.

        Args:
            **kwargs: Additional attributes to override in the model

        Returns:
            RemoteNetworkResponseModel: A model instance with BGP protocol
        """
        protocol_data = {
            "bgp": {
                "enable": True,
                "peer_ip_address": "10.11.0.254",
                "peer_as": "65515",
                "local_ip_address": "192.168.11.11",
                "peering_type": PeeringTypeEnum.exchange_v4_over_v4,
            }
        }
        # Pass the protocol as a dict instead of a pre-constructed model
        return cls(protocol=protocol_data, **kwargs)

    @classmethod
    def with_ecmp_enabled(cls, ecmp_tunnel_count=2, **kwargs):
        """
        Return a response with ecmp enabled and ecmp_tunnels data.

        Args:
            ecmp_tunnel_count: Number of ECMP tunnels to create
            **kwargs: Additional attributes to override in the model

        Returns:
            RemoteNetworkResponseModel: A model instance with ECMP enabled
        """
        tunnels = []
        for i in range(ecmp_tunnel_count):
            tunnels.append(
                EcmpTunnelModel(
                    name=f"ecmp_tunnel_{i}",
                    ipsec_tunnel=f"ipsec-tunnel-ecmp-{i}",
                )
            )
        return cls(
            ecmp_load_balancing=EcmpLoadBalancingEnum.enable,
            ipsec_tunnel=None,
            ecmp_tunnels=tunnels,
            **kwargs,
        )

    @classmethod
    def from_request(
        cls,
        request_model: Union[RemoteNetworkCreateModel, RemoteNetworkUpdateModel, Dict[str, Any]],
        **kwargs,
    ):
        """
        Create a response model based on a create request model,
        adding a newly generated id and any overridden kwargs.

        Args:
            request_model: The create/update request model or dictionary to base the response on
            **kwargs: Additional attributes to override in the response

        Returns:
            RemoteNetworkResponseModel: A model instance based on the request
        """
        if isinstance(request_model, (RemoteNetworkCreateModel, RemoteNetworkUpdateModel)):
            data = request_model.model_dump()
        else:
            data = request_model.copy()

        if "id" not in data or not data["id"]:
            data["id"] = str(uuid4())

        data.update(kwargs)
        return RemoteNetworkResponseModel(**data)


# ----------------------------------------------------------------------------
# Remote Network model factories for Pydantic validation testing.
# ----------------------------------------------------------------------------


class RemoteNetworkCreateModelFactory(factory.DictFactory):
    """
    Factory for creating dictionary data suitable for instantiating RemoteNetworkCreateModel.
    Useful for direct Pydantic validation tests.
    """

    name = factory.Sequence(lambda n: f"remote_network_{n}")
    region = "us-west-2"
    license_type = "FWAAS-AGGREGATE"
    spn_name = "spn-test"

    # ecmp_load_balancing defaults to disable => ipsec_tunnel is required
    ecmp_load_balancing = "disable"
    ipsec_tunnel = "ipsec-tunnel-default"
    ecmp_tunnels = None

    folder = "Remote Networks"
    snippet = None
    device = None

    @classmethod
    def build_valid(cls, **kwargs) -> Dict[str, Any]:
        """
        Return a valid data dict with all the expected attributes.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Valid data for RemoteNetworkCreateModel
        """
        data = {
            "name": "test-remote-network",
            "region": "us-east-1",
            "license_type": "FWAAS-AGGREGATE",
            "spn_name": "test-spn",
            "ecmp_load_balancing": "disable",
            "ipsec_tunnel": "test-ipsec-tunnel",
            "folder": "Remote Networks",
        }
        data.update(kwargs)
        return data

    @classmethod
    def build_ecmp_enabled(cls, ecmp_count=2, **kwargs) -> Dict[str, Any]:
        """
        Return a data dict with ECMP load balancing enabled.

        Args:
            ecmp_count: Number of ECMP tunnels to create
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Data for RemoteNetworkCreateModel with ECMP enabled
        """
        ecmp_tunnels = []
        for i in range(ecmp_count):
            ecmp_tunnels.append(
                {
                    "name": f"tunnel-{i}",
                    "ipsec_tunnel": f"ipsec-tunnel-{i}",
                }
            )

        data = {
            "name": "ecmp-remote-network",
            "region": "us-east-1",
            "license_type": "FWAAS-AGGREGATE",
            "spn_name": "test-spn",
            "ecmp_load_balancing": "enable",
            "ecmp_tunnels": ecmp_tunnels,
            "folder": "Remote Networks",
        }
        data.update(kwargs)
        return data

    @classmethod
    def build_without_required_ipsec_tunnel(cls, **kwargs) -> Dict[str, Any]:
        """
        Return a data dict with ecmp_load_balancing=disable but missing ipsec_tunnel.
        Will cause validation error.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Invalid data for RemoteNetworkCreateModel
        """
        data = {
            "name": "invalid-remote-network",
            "region": "us-east-1",
            "license_type": "FWAAS-AGGREGATE",
            "spn_name": "test-spn",
            "ecmp_load_balancing": "disable",
            # Missing ipsec_tunnel
            "folder": "Remote Networks",
        }
        data.update(kwargs)
        return data

    @classmethod
    def build_without_container(cls, **kwargs) -> Dict[str, Any]:
        """
        Return a data dict without any container (folder, snippet, device).
        Will cause validation error.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Invalid data for RemoteNetworkCreateModel
        """
        data = {
            "name": "no-container-remote-network",
            "region": "us-east-1",
            "license_type": "FWAAS-AGGREGATE",
            "spn_name": "test-spn",
            "ecmp_load_balancing": "disable",
            "ipsec_tunnel": "test-ipsec-tunnel",
            # No folder, snippet, or device
        }
        data.update(kwargs)
        return data

    @classmethod
    def build_no_container(cls, **kwargs) -> Dict[str, Any]:
        """Alias for build_without_container for test compatibility."""
        return cls.build_without_container(**kwargs)

    @classmethod
    def without_spn_name(cls, **kwargs) -> Dict[str, Any]:
        """
        Return a data dict missing the required spn_name field.
        Will cause validation error.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Invalid data for RemoteNetworkCreateModel
        """
        data = cls.build_valid()
        data["spn_name"] = None
        data.update(kwargs)
        return data

    @classmethod
    def build_with_multiple_containers(cls, **kwargs) -> Dict[str, Any]:
        """
        Return a data dict with multiple containers (folder and snippet).
        Will cause validation error.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Invalid data for RemoteNetworkCreateModel
        """
        data = {
            "name": "multi-container-remote-network",
            "region": "us-east-1",
            "license_type": "FWAAS-AGGREGATE",
            "spn_name": "test-spn",
            "ecmp_load_balancing": "disable",
            "ipsec_tunnel": "test-ipsec-tunnel",
            "folder": "Remote Networks",
            "snippet": "Test Snippet",
        }
        data.update(kwargs)
        return data


class RemoteNetworkUpdateModelFactory(factory.DictFactory):
    """
    Factory for creating dictionary data suitable for instantiating RemoteNetworkUpdateModel.
    Useful for direct Pydantic validation tests.
    """

    id = str(uuid4())
    name = factory.Sequence(lambda n: f"updated_remote_network_{n}")
    region = "us-west-2"
    license_type = "FWAAS-AGGREGATE"
    spn_name = "spn-updated"

    # ecmp_load_balancing defaults to disable => ipsec_tunnel is required
    ecmp_load_balancing = "disable"
    ipsec_tunnel = "updated-ipsec-tunnel"
    ecmp_tunnels = None

    @classmethod
    def build_valid(cls, **kwargs) -> Dict[str, Any]:
        """
        Return a valid data dict with all the expected attributes.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Valid data for RemoteNetworkUpdateModel
        """
        data = {
            "id": str(uuid4()),
            "name": "updated-remote-network",
            "region": "us-east-1",
            "license_type": "FWAAS-AGGREGATE",
            "spn_name": "updated-spn",
            "ecmp_load_balancing": "disable",
            "ipsec_tunnel": "updated-ipsec-tunnel",
        }
        data.update(kwargs)
        return data

    @classmethod
    def build_without_id(cls, **kwargs) -> Dict[str, Any]:
        """
        Return a data dict without the required id field.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Invalid data for RemoteNetworkUpdateModel
        """
        data = {
            # Missing id
            "name": "no-id-remote-network",
            "region": "us-east-1",
            "license_type": "FWAAS-AGGREGATE",
            "spn_name": "test-spn",
            "ecmp_load_balancing": "disable",
            "ipsec_tunnel": "test-ipsec-tunnel",
        }
        data.update(kwargs)
        return data

    @classmethod
    def without_spn_name(cls, **kwargs) -> Dict[str, Any]:
        """
        Return a data dict missing the required spn_name field.
        Will cause validation error.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Invalid data for RemoteNetworkUpdateModel
        """
        data = cls.build_valid()
        data["spn_name"] = None
        data.update(kwargs)
        return data
