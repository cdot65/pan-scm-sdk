"""Test factories for Network Locations deployment objects."""

# Standard library imports
from typing import Any, Dict, List

# External libraries
import factory  # type: ignore
from faker import Faker

# Local SDK imports
from scm.models.deployment.network_locations import NetworkLocationModel

fake = Faker()


# ----------------------------------------------------------------------------
# Network Location factories
# ----------------------------------------------------------------------------


class NetworkLocationBaseFactory(factory.Factory):
    """Base factory for Network Location objects."""

    class Meta:
        model = NetworkLocationModel
        abstract = True

    value = "us-west-1"
    display = "US West"
    continent = "North America"
    latitude = 37.38314
    longitude = -121.98306
    region = "us-west-1"
    aggregate_region = "us-southwest"


# ----------------------------------------------------------------------------
# Network Location API factories for testing SCM API interactions.
# These return dictionaries for compatibility with existing tests.
# ----------------------------------------------------------------------------


class NetworkLocationApiFactory:
    """Factory for creating dictionaries suitable for NetworkLocationModel
    with the structure used by the Python SDK calls.
    """

    def __call__(self, **kwargs) -> Dict[str, Any]:
        """Create dictionary representation of a Network Location."""
        data = {
            "value": kwargs.get("value", "us-west-1"),
            "display": kwargs.get("display", "US West"),
            "continent": kwargs.get("continent", "North America"),
            "latitude": kwargs.get("latitude", 37.38314),
            "longitude": kwargs.get("longitude", -121.98306),
            "region": kwargs.get("region", "us-west-1"),
            "aggregate_region": kwargs.get("aggregate_region", "us-southwest"),
        }

        # Update with any other kwargs
        for key, value in kwargs.items():
            if key not in data:
                data[key] = value

        return data

    def with_no_optionals(self, **kwargs) -> Dict[str, Any]:
        """Create a dictionary with only required fields.

        Args:
            **kwargs: Additional attributes to override in the data

        Returns:
            Dict[str, Any]: Data with only required fields

        """
        data = {
            "value": kwargs.get("value", "us-west-1"),
            "display": kwargs.get("display", "US West"),
        }

        # Update with any other kwargs
        for key, value in kwargs.items():
            if key not in data:
                data[key] = value

        return data

    def with_invalid_latitude(self, **kwargs) -> Dict[str, Any]:
        """Create a dictionary with an invalid latitude.

        Args:
            **kwargs: Additional attributes to override in the data

        Returns:
            Dict[str, Any]: Data with invalid latitude

        """
        data = self.__call__(**kwargs)
        data["latitude"] = kwargs.get("latitude", 100)  # Invalid: outside -90 to 90 range
        return data

    def with_invalid_longitude(self, **kwargs) -> Dict[str, Any]:
        """Create a dictionary with an invalid longitude.

        Args:
            **kwargs: Additional attributes to override in the data

        Returns:
            Dict[str, Any]: Data with invalid longitude

        """
        data = self.__call__(**kwargs)
        data["longitude"] = kwargs.get("longitude", 200)  # Invalid: outside -180 to 180 range
        return data

    def multiple_locations(self, count: int = 3) -> List[Dict[str, Any]]:
        """Create a list of multiple network location dictionaries.

        Args:
            count: Number of locations to create

        Returns:
            List[Dict[str, Any]]: List of network location dictionaries

        """
        regions = ["us-west-1", "us-east-1", "eu-west-1", "ap-southeast-1", "sa-east-1"]
        displays = ["US West", "US East", "Europe West", "Asia Pacific", "South America"]
        continents = ["North America", "North America", "Europe", "Asia", "South America"]

        locations = []
        for i in range(min(count, len(regions))):
            locations.append(
                self.__call__(
                    value=regions[i],
                    display=displays[i],
                    continent=continents[i],
                    region=regions[i],
                    latitude=fake.latitude(),
                    longitude=fake.longitude(),
                    aggregate_region=regions[i].split("-")[0],
                )
            )

        # If we need more locations than our predefined list
        for i in range(len(regions), count):
            region_code = f"region-{i + 1}"
            locations.append(
                self.__call__(
                    value=region_code,
                    display=f"Region {i + 1}",
                    continent=fake.random_element(
                        elements=("North America", "Europe", "Asia", "Africa", "Oceania")
                    ),
                    region=region_code,
                    latitude=fake.latitude(),
                    longitude=fake.longitude(),
                    aggregate_region=fake.random_element(
                        elements=("north", "south", "east", "west")
                    ),
                )
            )

        return locations


# Create instances of the factories so they can be called directly
NetworkLocationApiFactory = NetworkLocationApiFactory()


# ----------------------------------------------------------------------------
# Pydantic model factories for direct model validation testing
# ----------------------------------------------------------------------------


class NetworkLocationModelFactory:
    """Factory for creating dictionary data suitable for instantiating NetworkLocationModel.
    Useful for direct Pydantic validation tests.
    """

    model = dict
    value = "us-west-1"
    display = "US West"
    continent = "North America"
    latitude = 37.38314
    longitude = -121.98306
    region = "us-west-1"
    aggregate_region = "us-southwest"

    @classmethod
    def build_valid(cls, **kwargs) -> Dict[str, Any]:
        """Return a valid data dict with all expected attributes.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Valid data for NetworkLocationModel

        """
        data = {
            "value": cls.value,
            "display": cls.display,
            "continent": cls.continent,
            "latitude": cls.latitude,
            "longitude": cls.longitude,
            "region": cls.region,
            "aggregate_region": cls.aggregate_region,
        }
        data.update(kwargs)
        return data

    @classmethod
    def build_minimal(cls, **kwargs) -> Dict[str, Any]:
        """Return data dict with only required fields.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Minimal valid data for NetworkLocationModel

        """
        data = {
            "value": kwargs.get("value", cls.value),
            "display": kwargs.get("display", cls.display),
        }
        # Add any additional fields from kwargs
        for key, value in kwargs.items():
            if key not in data:
                data[key] = value
        return data

    @classmethod
    def build_with_invalid_latitude(cls, **kwargs) -> Dict[str, Any]:
        """Return data dict with invalid latitude.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Data with invalid latitude

        """
        data = cls.build_valid(**kwargs)
        data["latitude"] = kwargs.get("latitude", 100)  # Invalid: outside -90 to 90 range
        return data

    @classmethod
    def build_with_invalid_longitude(cls, **kwargs) -> Dict[str, Any]:
        """Return data dict with invalid longitude.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Data with invalid longitude

        """
        data = cls.build_valid(**kwargs)
        data["longitude"] = kwargs.get("longitude", 200)  # Invalid: outside -180 to 180 range
        return data

    @classmethod
    def build_missing_required(cls, field_to_omit: str) -> Dict[str, Any]:
        """Return data dict missing a required field.

        Args:
            field_to_omit: The required field to omit

        Returns:
            Dict[str, Any]: Data missing a required field

        """
        data = cls.build_valid()
        if field_to_omit in data:
            del data[field_to_omit]
        return data

    @classmethod
    def build_with_none_values(cls, **kwargs) -> Dict[str, Any]:
        """Return data dict with explicit None values for optional fields.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Data with None values for optional fields

        """
        data = {
            "value": kwargs.get("value", cls.value),
            "display": kwargs.get("display", cls.display),
            "continent": None,
            "latitude": None,
            "longitude": None,
            "region": None,
            "aggregate_region": None,
        }
        data.update(kwargs)
        return data

    @classmethod
    def build_with_empty_strings(cls, **kwargs) -> Dict[str, Any]:
        """Return data dict with empty string values for optional string fields.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Data with empty strings for optional string fields

        """
        data = {
            "value": kwargs.get("value", cls.value),
            "display": kwargs.get("display", cls.display),
            "continent": "",
            "region": "",
            "aggregate_region": "",
        }
        data.update(kwargs)
        return data

    @classmethod
    def build_with_invalid_latitude_type(cls, **kwargs) -> Dict[str, Any]:
        """Return data dict with an invalid type for latitude.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Data with invalid latitude type

        """
        data = cls.build_minimal(**kwargs)
        data["latitude"] = kwargs.get("latitude", "invalid")  # Invalid: should be numeric
        return data

    @classmethod
    def build_with_invalid_longitude_type(cls, **kwargs) -> Dict[str, Any]:
        """Return data dict with an invalid type for longitude.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Data with invalid longitude type

        """
        data = cls.build_minimal(**kwargs)
        data["longitude"] = kwargs.get("longitude", "invalid")  # Invalid: should be numeric
        return data

    @classmethod
    def build_with_invalid_value_type(cls, **kwargs) -> Dict[str, Any]:
        """Return data dict with an invalid type for value.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Data with invalid value type

        """
        data = cls.build_minimal(**kwargs)
        data["value"] = kwargs.get("value", 123)  # Invalid: should be string
        return data

    @classmethod
    def build_with_invalid_display_type(cls, **kwargs) -> Dict[str, Any]:
        """Return data dict with an invalid type for display.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Data with invalid display type

        """
        data = cls.build_minimal(**kwargs)
        data["display"] = kwargs.get("display", 123)  # Invalid: should be string
        return data

    @classmethod
    def build_multiple(cls, count: int = 3) -> List[Dict[str, Any]]:
        """Create multiple network location dictionaries.

        Args:
            count: Number of locations to generate

        Returns:
            List[Dict[str, Any]]: List of network location dictionaries

        """
        regions = ["us-west-1", "us-east-1", "eu-west-1", "ap-southeast-1", "sa-east-1"]
        displays = ["US West", "US East", "Europe West", "Asia Pacific", "South America"]
        continents = ["North America", "North America", "Europe", "Asia", "South America"]

        locations = []
        for i in range(min(count, len(regions))):
            locations.append(
                cls.build_valid(
                    value=regions[i],
                    display=displays[i],
                    continent=continents[i],
                    region=regions[i],
                    latitude=fake.latitude(),
                    longitude=fake.longitude(),
                    aggregate_region=regions[i].split("-")[0],
                )
            )

        # If we need more locations than our predefined list
        for i in range(len(regions), count):
            region_code = f"region-{i + 1}"
            locations.append(
                cls.build_valid(
                    value=region_code,
                    display=f"Region {i + 1}",
                    continent=fake.random_element(
                        elements=("North America", "Europe", "Asia", "Africa", "Oceania")
                    ),
                    region=region_code,
                    latitude=fake.latitude(),
                    longitude=fake.longitude(),
                    aggregate_region=fake.random_element(
                        elements=("north", "south", "east", "west")
                    ),
                )
            )

        return locations
