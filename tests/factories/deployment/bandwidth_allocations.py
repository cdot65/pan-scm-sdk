"""Test factories for Bandwidth Allocations deployment objects."""

# Standard library imports
from typing import Any, Dict, Union

# External libraries
import factory  # type: ignore
from faker import Faker

# Local SDK imports
from scm.models.deployment.bandwidth_allocations import (
    BandwidthAllocationBaseModel,
    BandwidthAllocationCreateModel,
    BandwidthAllocationUpdateModel,
    QosModel,
)

fake = Faker()


# ----------------------------------------------------------------------------
# QoS factories
# ----------------------------------------------------------------------------


class QosModelFactory(factory.Factory):
    """Factory for creating QosModel instances."""

    class Meta:
        model = QosModel

    enabled = True
    customized = False
    profile = "default-profile"
    guaranteed_ratio = 0.5

    @classmethod
    def build_valid(cls, **kwargs) -> Dict[str, Any]:
        """Return a valid data dict with all expected attributes.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Valid data for QosModel

        """
        data = {
            "enabled": True,
            "customized": True,
            "profile": "test-profile",
            "guaranteed_ratio": 0.5,
        }
        data.update(kwargs)
        return data

    @classmethod
    def disabled(cls, **kwargs):
        """Create a QosModel with QoS disabled.

        Args:
            **kwargs: Additional attributes to override in the model

        Returns:
            QosModel: A model instance with QoS disabled

        """
        return cls(enabled=False, **kwargs)

    @classmethod
    def customized_profile(cls, profile="custom-profile", ratio=0.75, **kwargs):
        """Create a QosModel with customized profile settings.

        Args:
            profile: The QoS profile name
            ratio: The guaranteed ratio value
            **kwargs: Additional attributes to override in the model

        Returns:
            QosModel: A model instance with customized QoS profile

        """
        return cls(
            enabled=True,
            customized=True,
            profile=profile,
            guaranteed_ratio=ratio,
            **kwargs,
        )


# Base factory for all bandwidth allocation models
class BandwidthAllocationBaseFactory(factory.Factory):
    """Base factory for Bandwidth Allocation objects with common fields."""

    class Meta:
        model = BandwidthAllocationBaseModel
        abstract = True

    name = factory.Sequence(lambda n: f"bandwidth_region_{n}")
    allocated_bandwidth = 100.0
    spn_name_list = ["spn1", "spn2"]
    qos = None


# ----------------------------------------------------------------------------
# Bandwidth Allocation API factories for testing SCM API interactions.
# These return dictionaries for compatibility with existing tests.
# ----------------------------------------------------------------------------


class BandwidthAllocationCreateApiFactory:
    """Factory for creating dictionaries suitable for BandwidthAllocationCreateModel
    with the structure used by the Python SDK calls.
    """

    def __call__(self, **kwargs) -> Dict[str, Any]:
        """Create dictionary representation of a bandwidth allocation create request."""
        data = {
            "name": kwargs.get("name", "test-region"),
            "allocated_bandwidth": kwargs.get("allocated_bandwidth", 100.0),
            "spn_name_list": kwargs.get("spn_name_list", ["spn1", "spn2"]),
        }

        if "qos" in kwargs:
            data["qos"] = kwargs["qos"]

        # Update with any other kwargs
        for key, value in kwargs.items():
            if key not in data and key != "qos":
                data[key] = value

        return data

    def with_qos(
        self, enabled=True, customized=False, profile="default", ratio=0.5, **kwargs
    ) -> Dict[str, Any]:
        """Create a dictionary with QoS settings.

        Args:
            enabled: Whether QoS is enabled
            customized: Whether to use customized QoS settings
            profile: The QoS profile name
            ratio: The guaranteed ratio value
            **kwargs: Additional attributes to override in the data

        Returns:
            Dict[str, Any]: Data with QoS settings

        """
        qos_data = {
            "enabled": enabled,
            "customized": customized,
            "profile": profile,
            "guaranteed_ratio": ratio,
        }
        return {
            "name": kwargs.get("name", "test-region"),
            "allocated_bandwidth": kwargs.get("allocated_bandwidth", 100.0),
            "spn_name_list": kwargs.get("spn_name_list", ["spn1", "spn2"]),
            "qos": qos_data,
            **{
                k: v
                for k, v in kwargs.items()
                if k not in ["name", "allocated_bandwidth", "spn_name_list"]
            },
        }

    def with_spn_list(self, spn_list=None, **kwargs) -> Dict[str, Any]:
        """Create a dictionary with specific SPN list.

        Args:
            spn_list: List of SPN names
            **kwargs: Additional attributes to override in the data

        Returns:
            Dict[str, Any]: Data with specific SPN list

        """
        if spn_list is None:
            spn_list = ["custom-spn1", "custom-spn2"]
        return {
            "name": kwargs.get("name", "test-region"),
            "allocated_bandwidth": kwargs.get("allocated_bandwidth", 100.0),
            "spn_name_list": spn_list,
            **{k: v for k, v in kwargs.items() if k not in ["name", "allocated_bandwidth"]},
        }


class BandwidthAllocationUpdateApiFactory:
    """Factory for creating dictionaries suitable for BandwidthAllocationUpdateModel
    with the structure used by the Python SDK calls.
    """

    def __call__(self, **kwargs) -> Dict[str, Any]:
        """Create dictionary representation of a bandwidth allocation update request."""
        data = {
            "name": kwargs.get("name", "test-region"),
            "allocated_bandwidth": kwargs.get("allocated_bandwidth", 200.0),
            "spn_name_list": kwargs.get("spn_name_list", ["spn3", "spn4"]),
        }

        if "qos" in kwargs:
            data["qos"] = kwargs["qos"]

        # Update with any other kwargs
        for key, value in kwargs.items():
            if key not in data and key != "qos":
                data[key] = value

        return data

    def with_qos(
        self, enabled=True, customized=True, profile="updated-profile", ratio=0.8, **kwargs
    ) -> Dict[str, Any]:
        """Create a dictionary with QoS settings.

        Args:
            enabled: Whether QoS is enabled
            customized: Whether to use customized QoS settings
            profile: The QoS profile name
            ratio: The guaranteed ratio value
            **kwargs: Additional attributes to override in the data

        Returns:
            Dict[str, Any]: Data with QoS settings

        """
        qos_data = {
            "enabled": enabled,
            "customized": customized,
            "profile": profile,
            "guaranteed_ratio": ratio,
        }
        return {
            "name": kwargs.get("name", "test-region"),
            "allocated_bandwidth": kwargs.get("allocated_bandwidth", 200.0),
            "spn_name_list": kwargs.get("spn_name_list", ["spn3", "spn4"]),
            "qos": qos_data,
            **{
                k: v
                for k, v in kwargs.items()
                if k not in ["name", "allocated_bandwidth", "spn_name_list"]
            },
        }

    def with_spn_list(self, spn_list=None, **kwargs) -> Dict[str, Any]:
        """Create a dictionary with specific SPN list.

        Args:
            spn_list: List of SPN names
            **kwargs: Additional attributes to override in the data

        Returns:
            Dict[str, Any]: Data with specific SPN list

        """
        if spn_list is None:
            spn_list = ["updated-spn1", "updated-spn2"]
        return {
            "name": kwargs.get("name", "test-region"),
            "allocated_bandwidth": kwargs.get("allocated_bandwidth", 200.0),
            "spn_name_list": spn_list,
            **{k: v for k, v in kwargs.items() if k not in ["name", "allocated_bandwidth"]},
        }

    def partial_update(self, **fields_to_update) -> Dict[str, Any]:
        """Create a partial update dictionary with just the specified fields.

        Args:
            **fields_to_update: Fields to include in the partial update

        Returns:
            Dict[str, Any]: A dictionary with only specified fields

        """
        return fields_to_update


class BandwidthAllocationResponseFactory:
    """Factory for creating dictionaries suitable for BandwidthAllocationResponseModel
    to mimic the actual data returned by the SCM API.
    """

    def __call__(self, **kwargs) -> Dict[str, Any]:
        """Create dictionary representation of a bandwidth allocation response."""
        data = {
            "name": kwargs.get("name", "test-region"),
            "allocated_bandwidth": kwargs.get("allocated_bandwidth", 100.0),
            "spn_name_list": kwargs.get("spn_name_list", ["spn1", "spn2"]),
        }

        if "qos" in kwargs:
            data["qos"] = kwargs["qos"]

        # Update with any other kwargs
        for key, value in kwargs.items():
            if key not in data and key != "qos":
                data[key] = value

        return data

    def with_qos(
        self, enabled=True, customized=False, profile="response-profile", ratio=0.6, **kwargs
    ) -> Dict[str, Any]:
        """Create a dictionary with QoS settings.

        Args:
            enabled: Whether QoS is enabled
            customized: Whether to use customized QoS settings
            profile: The QoS profile name
            ratio: The guaranteed ratio value
            **kwargs: Additional attributes to override in the data

        Returns:
            Dict[str, Any]: Data with QoS settings

        """
        qos_data = {
            "enabled": enabled,
            "customized": customized,
            "profile": profile,
            "guaranteed_ratio": ratio,
        }
        return {
            "name": kwargs.get("name", "test-region"),
            "allocated_bandwidth": kwargs.get("allocated_bandwidth", 100.0),
            "spn_name_list": kwargs.get("spn_name_list", ["spn1", "spn2"]),
            "qos": qos_data,
            **{
                k: v
                for k, v in kwargs.items()
                if k not in ["name", "allocated_bandwidth", "spn_name_list"]
            },
        }

    def from_request(
        self,
        request_data: Union[
            Dict[str, Any], BandwidthAllocationCreateModel, BandwidthAllocationUpdateModel
        ],
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
        if isinstance(
            request_data, (BandwidthAllocationCreateModel, BandwidthAllocationUpdateModel)
        ):
            data = request_data.model_dump()
        else:
            data = request_data.copy()

        data.update(kwargs)
        return data

    def list_response(self, items=None, limit=200, offset=0, total=None) -> Dict[str, Any]:
        """Create a list response dictionary with multiple bandwidth allocation entries.

        Args:
            items: List of bandwidth allocation objects or dictionaries to include
            limit: Maximum number of items per page
            offset: Offset into the list of results
            total: Total number of items available

        Returns:
            Dict[str, Any]: A list response with multiple entries

        """
        if items is None:
            items = [
                BandwidthAllocationResponseFactory(
                    name=f"region_{i}",
                    allocated_bandwidth=100.0 + i * 10,
                    spn_name_list=[f"spn{i}a", f"spn{i}b"],
                )
                for i in range(2)  # Default to 2 items to match test expectations
            ]

        if total is None:
            total = len(items)

        return {
            "data": items,
            "limit": limit,
            "offset": offset,
            "total": total,
        }


# Create instances of the factories so they can be called directly
BandwidthAllocationCreateApiFactory = BandwidthAllocationCreateApiFactory()
BandwidthAllocationUpdateApiFactory = BandwidthAllocationUpdateApiFactory()
BandwidthAllocationResponseFactory = BandwidthAllocationResponseFactory()


# ----------------------------------------------------------------------------
# Bandwidth Allocation model factories for Pydantic validation testing.
# ----------------------------------------------------------------------------


class BandwidthAllocationCreateModelFactory(factory.DictFactory):
    """Factory for creating dictionary data suitable for instantiating BandwidthAllocationCreateModel.
    Useful for direct Pydantic validation tests.
    """

    name = factory.Sequence(lambda n: f"bandwidth_region_{n}")
    allocated_bandwidth = 100.0
    spn_name_list = ["spn1", "spn2"]

    @classmethod
    def build_valid(cls, **kwargs) -> Dict[str, Any]:
        """Return a valid data dict with all expected attributes.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Valid data for BandwidthAllocationCreateModel

        """
        data = {
            "name": "test-region",
            "allocated_bandwidth": 100.0,
            "spn_name_list": ["spn1", "spn2"],
        }
        data.update(kwargs)
        return data

    @classmethod
    def build_with_qos(cls, **kwargs) -> Dict[str, Any]:
        """Return a data dict with QoS settings.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Data for BandwidthAllocationCreateModel with QoS

        """
        data = cls.build_valid()
        data["qos"] = {
            "enabled": True,
            "customized": True,
            "profile": "test-profile",
            "guaranteed_ratio": 0.75,
        }
        data.update(kwargs)
        return data

    @classmethod
    def build_with_invalid_name(cls, **kwargs) -> Dict[str, Any]:
        """Return a data dict with invalid name pattern.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Invalid data for BandwidthAllocationCreateModel

        """
        data = cls.build_valid()
        data["name"] = "invalid@name#"
        data.update(kwargs)
        return data

    @classmethod
    def build_with_invalid_bandwidth(cls, **kwargs) -> Dict[str, Any]:
        """Return a data dict with invalid negative bandwidth.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Invalid data for BandwidthAllocationCreateModel

        """
        data = cls.build_valid()
        data["allocated_bandwidth"] = -10.0
        data.update(kwargs)
        return data


class BandwidthAllocationUpdateModelFactory(factory.DictFactory):
    """Factory for creating dictionary data suitable for instantiating BandwidthAllocationUpdateModel.
    Useful for direct Pydantic validation tests.
    """

    name = factory.Sequence(lambda n: f"updated_region_{n}")
    allocated_bandwidth = 200.0
    spn_name_list = ["updated-spn1", "updated-spn2"]

    @classmethod
    def build_valid(cls, **kwargs) -> Dict[str, Any]:
        """Return a valid data dict with all expected attributes.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Valid data for BandwidthAllocationUpdateModel

        """
        data = {
            "name": "test-region",
            "allocated_bandwidth": 200.0,
            "spn_name_list": ["updated-spn1", "updated-spn2"],
        }
        data.update(kwargs)
        return data

    @classmethod
    def build_partial(cls, **kwargs) -> Dict[str, Any]:
        """Return a partial update data dict with just name and bandwidth.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Partial data for BandwidthAllocationUpdateModel

        """
        data = {
            "name": "test-region",
            "allocated_bandwidth": 300.0,
        }
        data.update(kwargs)
        return data

    @classmethod
    def build_with_qos(cls, **kwargs) -> Dict[str, Any]:
        """Return a data dict with QoS settings.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Data for BandwidthAllocationUpdateModel with QoS

        """
        data = cls.build_valid()
        data["qos"] = {
            "enabled": True,
            "customized": True,
            "profile": "updated-profile",
            "guaranteed_ratio": 0.9,
        }
        data.update(kwargs)
        return data


class BandwidthAllocationResponseModelFactory(factory.DictFactory):
    """Factory for creating dictionary data suitable for instantiating BandwidthAllocationResponseModel.
    Useful for direct Pydantic validation tests.
    """

    name = factory.Sequence(lambda n: f"response_region_{n}")
    allocated_bandwidth = 100.0
    spn_name_list = ["response-spn1", "response-spn2"]

    @classmethod
    def build_valid(cls, **kwargs) -> Dict[str, Any]:
        """Return a valid data dict for a response model.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Valid data for BandwidthAllocationResponseModel

        """
        data = {
            "name": "test-region",
            "allocated_bandwidth": 100.0,
            "spn_name_list": ["response-spn1", "response-spn2"],
        }
        data.update(kwargs)
        return data

    @classmethod
    def build_minimal(cls, **kwargs) -> Dict[str, Any]:
        """Return a minimal data dict with only required fields.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Minimal data for BandwidthAllocationResponseModel

        """
        data = {
            "name": "minimal-region",
            "allocated_bandwidth": 50.0,
        }
        data.update(kwargs)
        return data

    @classmethod
    def build_list_response(cls, count=3, **kwargs) -> Dict[str, Any]:
        """Return a data dict for a list response model.

        Args:
            count: Number of items to include in the list
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Valid data for BandwidthAllocationListResponseModel

        """
        items = []
        for i in range(count):
            item = {
                "name": f"region_{i}",
                "allocated_bandwidth": 100.0 + i * 10,
                "spn_name_list": [f"spn{i}a", f"spn{i}b"],
            }
            items.append(item)

        data = {
            "data": items,
            "limit": 200,
            "offset": 0,
            "total": count,
        }
        data.update(kwargs)
        return data
