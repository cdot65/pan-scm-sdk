"""Test factories for Internal DNS Servers deployment objects."""

# Standard library imports
from typing import Any, Dict, List, Union
import uuid

# External libraries
import factory  # type: ignore
from faker import Faker

# Local SDK imports
from scm.models.deployment.internal_dns_servers import (
    InternalDnsServersBaseModel,
    InternalDnsServersCreateModel,
    InternalDnsServersUpdateModel,
)

fake = Faker()


# ----------------------------------------------------------------------------
# Internal DNS Servers factories
# ----------------------------------------------------------------------------


class InternalDnsServersBaseFactory(factory.Factory):
    """Base factory for Internal DNS Servers objects with common fields."""

    class Meta:
        """Factory configuration."""

        model = InternalDnsServersBaseModel
        abstract = True

    name = "test-dns-server"
    domain_name = ["example.com", "test.com"]
    primary = "192.168.1.1"
    secondary = "8.8.8.8"


# ----------------------------------------------------------------------------
# Internal DNS Servers API factories for testing SCM API interactions.
# These return dictionaries for compatibility with existing tests.
# ----------------------------------------------------------------------------


class InternalDnsServersCreateApiFactory:
    """Factory for creating dictionaries suitable for InternalDnsServersCreateModel.

    with the structure used by the Python SDK calls.
    """

    def __call__(self, **kwargs) -> Dict[str, Any]:
        """Create dictionary representation of an Internal DNS Servers create request."""
        data = {
            "name": kwargs.get("name", "test-dns-server"),
            "domain_name": kwargs.get("domain_name", ["example.com", "test.com"]),
            "primary": kwargs.get("primary", "192.168.1.1"),
            "secondary": kwargs.get("secondary", "8.8.8.8"),
        }

        # Update with any other kwargs
        for key, value in kwargs.items():
            if key not in data:
                data[key] = value

        return data

    def with_multiple_domains(self, **kwargs) -> Dict[str, Any]:
        """Create a dictionary with multiple domain names.

        Args:
            **kwargs: Additional attributes to override in the data

        Returns:
            Dict[str, Any]: Data with multiple domain names

        """
        data = self.__call__(**kwargs)
        data["domain_name"] = kwargs.get("domain_name", ["example.com", "test.com", "domain.local"])
        return data

    def with_single_domain(self, **kwargs) -> Dict[str, Any]:
        """Create a dictionary with a single domain name.

        Args:
            **kwargs: Additional attributes to override in the data

        Returns:
            Dict[str, Any]: Data with a single domain name

        """
        data = self.__call__(**kwargs)
        data["domain_name"] = kwargs.get("domain_name", ["example.com"])
        return data

    def without_secondary(self, **kwargs) -> Dict[str, Any]:
        """Create a dictionary without a secondary DNS server.

        Args:
            **kwargs: Additional attributes to override in the data

        Returns:
            Dict[str, Any]: Data without a secondary DNS server

        """
        data = self.__call__(**kwargs)
        data["secondary"] = None
        return data

    def with_invalid_domain_name(self, **kwargs) -> Dict[str, Any]:
        """Create a dictionary with an invalid domain_name format.

        Args:
            **kwargs: Additional attributes to override in the data

        Returns:
            Dict[str, Any]: Data with invalid domain_name

        """
        data = self.__call__(**kwargs)
        data["domain_name"] = kwargs.get("domain_name", 123)  # Invalid type
        return data


class InternalDnsServersUpdateApiFactory:
    """Factory for creating dictionaries suitable for InternalDnsServersUpdateModel.

    with the structure used by the Python SDK calls.
    """

    def __call__(self, **kwargs) -> Dict[str, Any]:
        """Create dictionary representation of an Internal DNS Servers update request."""
        data = {
            "id": kwargs.get("id", str(uuid.uuid4())),
            "name": kwargs.get("name", "updated-dns-server"),
            "domain_name": kwargs.get("domain_name", ["updated.example.com", "updated.test.com"]),
            "primary": kwargs.get("primary", "192.168.2.1"),
            "secondary": kwargs.get("secondary", "8.8.4.4"),
        }

        # Update with any other kwargs
        for key, value in kwargs.items():
            if key not in data:
                data[key] = value

        return data

    def partial_update(self, fields: List[str], **kwargs) -> Dict[str, Any]:
        """Create a dictionary with only specified fields for a partial update.

        Args:
            fields: List of field names to include in the update
            **kwargs: Values for the fields

        Returns:
            Dict[str, Any]: Partial update data

        """
        # Always include id
        if "id" not in fields:
            fields.append("id")

        data = self.__call__(**kwargs)
        return {field: data[field] for field in fields if field in data}

    def without_secondary(self, **kwargs) -> Dict[str, Any]:
        """Create a dictionary update without a secondary DNS server.

        Args:
            **kwargs: Additional attributes to override in the data

        Returns:
            Dict[str, Any]: Update data without a secondary DNS server

        """
        data = self.__call__(**kwargs)
        data["secondary"] = None
        return data

    def with_invalid_domain_name(self, **kwargs) -> Dict[str, Any]:
        """Create a dictionary with an invalid domain_name format.

        Args:
            **kwargs: Additional attributes to override in the data

        Returns:
            Dict[str, Any]: Data with invalid domain_name

        """
        data = self.__call__(**kwargs)
        data["domain_name"] = kwargs.get("domain_name", [])  # Empty list is invalid
        return data


class InternalDnsServersResponseFactory:
    """Factory for creating dictionaries suitable for InternalDnsServersResponseModel.

    to mimic the actual data returned by the SCM API.
    """

    def __call__(self, **kwargs) -> Dict[str, Any]:
        """Create dictionary representation of an Internal DNS Servers response."""
        data = {
            "id": kwargs.get("id", str(uuid.uuid4())),
            "name": kwargs.get("name", "test-dns-server"),
            "domain_name": kwargs.get("domain_name", ["example.com", "test.com"]),
            "primary": kwargs.get("primary", "192.168.1.1"),
            "secondary": kwargs.get("secondary", "8.8.8.8"),
        }

        # Update with any other kwargs
        for key, value in kwargs.items():
            if key not in data:
                data[key] = value

        return data

    def without_secondary(self, **kwargs) -> Dict[str, Any]:
        """Create a response dictionary without a secondary DNS server.

        Args:
            **kwargs: Additional attributes to override in the data

        Returns:
            Dict[str, Any]: Response data without a secondary DNS server

        """
        data = self.__call__(**kwargs)
        data["secondary"] = None
        return data

    def with_single_domain(self, **kwargs) -> Dict[str, Any]:
        """Create a response dictionary with a single domain name.

        Args:
            **kwargs: Additional attributes to override in the data

        Returns:
            Dict[str, Any]: Response data with a single domain name

        """
        data = self.__call__(**kwargs)
        data["domain_name"] = kwargs.get("domain_name", ["example.com"])
        return data

    def from_request(
        self,
        request_data: Union[
            Dict[str, Any], InternalDnsServersCreateModel, InternalDnsServersUpdateModel
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
        # Convert models to dict if necessary
        if hasattr(request_data, "model_dump"):
            request_dict = request_data.model_dump(exclude_unset=True)
        else:
            request_dict = dict(request_data)

        # Start with a response based on the request
        response = dict(request_dict)

        # Add an ID if not already present (for create requests)
        if "id" not in response:
            response["id"] = str(uuid.uuid4())

        # Override with any provided kwargs
        for key, value in kwargs.items():
            response[key] = value

        return response


# Create instances of the factories so they can be called directly
InternalDnsServersCreateApiFactory = InternalDnsServersCreateApiFactory()
InternalDnsServersUpdateApiFactory = InternalDnsServersUpdateApiFactory()
InternalDnsServersResponseFactory = InternalDnsServersResponseFactory()


# ----------------------------------------------------------------------------
# Pydantic model factories for direct model validation testing
# ----------------------------------------------------------------------------


class InternalDnsServersCreateModelFactory:
    """Factory for creating dictionary data suitable for instantiating InternalDnsServersCreateModel.

    Useful for direct Pydantic validation tests.
    """

    model = dict
    name = "test-dns-server"
    domain_name = ["example.com", "test.com"]
    primary = "192.168.1.1"
    secondary = "8.8.8.8"

    @classmethod
    def build_valid(cls, **kwargs) -> Dict[str, Any]:
        """Return a valid data dict with all expected attributes.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Valid data for InternalDnsServersCreateModel

        """
        data = {
            "name": cls.name,
            "domain_name": cls.domain_name,
            "primary": cls.primary,
            "secondary": cls.secondary,
        }
        data.update(kwargs)
        return data

    @classmethod
    def build_with_single_domain(cls, **kwargs) -> Dict[str, Any]:
        """Return a data dict with a single domain name.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Data for InternalDnsServersCreateModel with a single domain

        """
        data = cls.build_valid(**kwargs)
        data["domain_name"] = ["example.com"]
        data.update(kwargs)
        return data

    @classmethod
    def build_without_secondary(cls, **kwargs) -> Dict[str, Any]:
        """Return a data dict without a secondary DNS server.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Data for InternalDnsServersCreateModel without a secondary server

        """
        data = cls.build_valid(**kwargs)
        data["secondary"] = None
        data.update(kwargs)
        return data

    @classmethod
    def build_with_invalid_name(cls, **kwargs) -> Dict[str, Any]:
        """Return a data dict with an invalid name.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Data for InternalDnsServersCreateModel with an invalid name

        """
        data = cls.build_valid(**kwargs)
        data["name"] = "invalid@name"  # Contains invalid character
        data.update(kwargs)
        return data

    @classmethod
    def build_with_empty_domain_name(cls, **kwargs) -> Dict[str, Any]:
        """Return a data dict with an empty domain_name list, which is invalid.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Data for InternalDnsServersCreateModel with empty domain_name

        """
        data = cls.build_valid(**kwargs)
        data["domain_name"] = []  # Invalid: must not be empty
        data.update(kwargs)
        return data


class InternalDnsServersUpdateModelFactory:
    """Factory for creating dictionary data suitable for instantiating InternalDnsServersUpdateModel.

    Useful for direct Pydantic validation tests.
    """

    model = dict
    id = str(uuid.uuid4())
    name = "updated-dns-server"
    domain_name = ["updated.example.com", "updated.test.com"]
    primary = "192.168.2.1"
    secondary = "8.8.4.4"

    @classmethod
    def build_valid(cls, **kwargs) -> Dict[str, Any]:
        """Return a valid data dict with all expected attributes.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Valid data for InternalDnsServersUpdateModel

        """
        data = {
            "id": kwargs.get("id", cls.id),
            "name": cls.name,
            "domain_name": cls.domain_name,
            "primary": cls.primary,
            "secondary": cls.secondary,
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
            Dict[str, Any]: Partial data for InternalDnsServersUpdateModel

        """
        data = {"id": kwargs.get("id", cls.id)}

        for field in fields:
            if field == "id":
                continue  # Already added
            elif field == "name":
                data["name"] = kwargs.get("name", cls.name)
            elif field == "domain_name":
                data["domain_name"] = kwargs.get("domain_name", cls.domain_name)
            elif field == "primary":
                data["primary"] = kwargs.get("primary", cls.primary)
            elif field == "secondary":
                data["secondary"] = kwargs.get("secondary", cls.secondary)

        # Add any additional fields from kwargs that might not be in the specified fields
        for key, value in kwargs.items():
            if key not in data:
                data[key] = value

        return data

    @classmethod
    def build_without_secondary(cls, **kwargs) -> Dict[str, Any]:
        """Return a data dict without a secondary DNS server.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Data for InternalDnsServersUpdateModel without a secondary server

        """
        data = cls.build_valid(**kwargs)
        data["secondary"] = None
        data.update(kwargs)
        return data

    @classmethod
    def build_empty(cls) -> Dict[str, Any]:
        """Return an empty data dict with only the required id field for testing invalid updates.

        Returns:
            Dict[str, Any]: Empty data for InternalDnsServersUpdateModel

        """
        return {
            "id": cls.id,
        }

    @classmethod
    def build_with_empty_domain_name(cls, **kwargs) -> Dict[str, Any]:
        """Return a data dict with an empty domain_name list, which is invalid.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Data for InternalDnsServersUpdateModel with empty domain_name

        """
        data = cls.build_valid(**kwargs)
        data["domain_name"] = []  # Invalid: must not be empty
        data.update(kwargs)
        return data


class InternalDnsServersResponseModelFactory:
    """Factory for creating dictionary data suitable for instantiating InternalDnsServersResponseModel.

    Useful for direct Pydantic validation tests.
    """

    model = dict
    id = str(uuid.uuid4())
    name = "test-dns-server"
    domain_name = ["example.com", "test.com"]
    primary = "192.168.1.1"
    secondary = "8.8.8.8"

    @classmethod
    def build_valid(cls, **kwargs) -> Dict[str, Any]:
        """Return a valid data dict for a response model.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Valid data for InternalDnsServersResponseModel

        """
        data = {
            "id": kwargs.get("id", cls.id),
            "name": cls.name,
            "domain_name": cls.domain_name,
            "primary": cls.primary,
            "secondary": cls.secondary,
        }
        data.update(kwargs)
        return data

    @classmethod
    def build_without_secondary(cls, **kwargs) -> Dict[str, Any]:
        """Return a data dict without a secondary DNS server.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Data for InternalDnsServersResponseModel without a secondary server

        """
        data = cls.build_valid(**kwargs)
        data["secondary"] = None
        data.update(kwargs)
        return data

    @classmethod
    def build_with_single_domain(cls, **kwargs) -> Dict[str, Any]:
        """Return a data dict with a single domain name.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Data for InternalDnsServersResponseModel with single domain

        """
        data = cls.build_valid(**kwargs)
        data["domain_name"] = ["example.com"]
        data.update(kwargs)
        return data

    @classmethod
    def build_with_invalid_id(cls, **kwargs) -> Dict[str, Any]:
        """Return a data dict with an invalid ID format.

        Args:
            **kwargs: Additional attributes to override in the data dict

        Returns:
            Dict[str, Any]: Data for InternalDnsServersResponseModel with invalid ID

        """
        data = cls.build_valid(**kwargs)
        data["id"] = "not-a-valid-uuid"
        data.update(kwargs)
        return data
