"""Service Connections configuration service for Strata Cloud Manager SDK.

Provides service class for managing service connection objects via the SCM API.
"""

# scm/config/deployment/service_connections.py

# Standard library imports
import logging
import re
from typing import Any, Dict, List, Optional

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.deployment import (
    ServiceConnectionCreateModel,
    ServiceConnectionResponseModel,
    ServiceConnectionUpdateModel,
)


class ServiceConnection(BaseObject):
    """Manages Service Connection objects in Palo Alto Networks' Strata Cloud Manager.

    Args:
        api_client: The API client instance
        max_limit (Optional[int]): Maximum number of objects to return in a single API request.
            Defaults to 200. Must be between 1 and 1000.

    """

    ENDPOINT = "/config/deployment/v1/service-connections"
    DEFAULT_MAX_LIMIT = 200
    ABSOLUTE_MAX_LIMIT = 1000  # Maximum allowed by the API

    def __init__(
        self,
        api_client,
        max_limit: Optional[int] = None,
    ):
        """Initialize the ServiceConnections service with the given API client."""
        super().__init__(api_client)
        self.logger = logging.getLogger(__name__)

        # Validate and set max_limit
        self._max_limit = self._validate_max_limit(max_limit)

    @property
    def max_limit(self) -> int:
        """Get the current maximum limit for API requests."""
        return self._max_limit

    @max_limit.setter
    def max_limit(self, value: int) -> None:
        """Set a new maximum limit for API requests."""
        self._max_limit = self._validate_max_limit(value)

    def _validate_max_limit(self, limit: Optional[int]) -> int:
        """Validate the max_limit parameter.

        Args:
            limit: The limit to validate

        Returns:
            int: The validated limit

        Raises:
            InvalidObjectError: If the limit is invalid

        """
        if limit is None:
            return self.DEFAULT_MAX_LIMIT

        try:
            limit_int = int(limit)
        except (TypeError, ValueError):
            raise InvalidObjectError(
                message="max_limit must be an integer",
                error_code="E003",
                http_status_code=400,
                details={"error": "Invalid max_limit type"},
            )

        if limit_int < 1:
            raise InvalidObjectError(
                message="max_limit must be greater than 0",
                error_code="E003",
                http_status_code=400,
                details={"error": "Invalid max_limit value"},
            )

        if limit_int > self.ABSOLUTE_MAX_LIMIT:
            raise InvalidObjectError(
                message=f"max_limit cannot exceed {self.ABSOLUTE_MAX_LIMIT}",
                error_code="E003",
                http_status_code=400,
                details={"error": "max_limit exceeds maximum allowed value"},
            )

        return limit_int

    def create(
        self,
        data: Dict[str, Any],
    ) -> ServiceConnectionResponseModel:
        """Create a new service connection.

        Args:
            data: Dictionary containing the service connection configuration

        Returns:
            ServiceConnectionResponseModel

        """
        # Use the dictionary "data" to pass into Pydantic and return a modeled object
        service_connection = ServiceConnectionCreateModel(**data)

        # Convert back to a Python dictionary, removing any unset fields and using aliases
        payload = service_connection.model_dump(
            exclude_unset=True,
            by_alias=True,
        )

        # Send the updated object to the remote API as JSON
        response: Dict[str, Any] = self.api_client.post(
            self.ENDPOINT,
            json=payload,
        )

        # Return the API response as a new Pydantic object
        return ServiceConnectionResponseModel(**response)

    def get(
        self,
        object_id: str,
    ) -> ServiceConnectionResponseModel:
        """Get a service connection by ID.

        Args:
            object_id: The ID of the service connection to retrieve

        Returns:
            ServiceConnectionResponseModel

        """
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.get(endpoint)
        return ServiceConnectionResponseModel(**response)

    def update(
        self,
        service_connection: ServiceConnectionUpdateModel,
    ) -> ServiceConnectionResponseModel:
        """Update an existing service connection.

        Args:
            service_connection: ServiceConnectionUpdateModel instance containing the update data

        Returns:
            ServiceConnectionResponseModel

        """
        # Convert to dict for API request, excluding unset fields and using aliases
        payload = service_connection.model_dump(
            exclude_unset=True,
            by_alias=True,
        )

        # Extract ID and remove from payload since it's in the URL
        object_id = str(service_connection.id)
        payload.pop("id", None)

        # Send the updated object to the remote API as JSON
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.put(
            endpoint,
            json=payload,
        )

        # Return the API response as a new Pydantic model
        return ServiceConnectionResponseModel(**response)

    def list(
        self,
        name: Optional[str] = None,
        **filters,
    ) -> List[ServiceConnectionResponseModel]:
        """List service connection objects with optional filtering.

        Args:
            name: Optional name filter
            **filters: Additional query parameters to pass to the API

        Returns:
            List[ServiceConnectionResponseModel]: A list of service connection objects

        """
        # Pagination logic
        limit = self._max_limit
        offset = 0
        all_objects = []

        # Folder is required for service-connections API (from OpenAPI spec)
        base_params = dict(filters)
        base_params["folder"] = "Service Connections"  # Always set folder parameter

        # Add name filter if provided
        if name:
            if not isinstance(name, str) or not name.strip():
                raise InvalidObjectError(
                    message="Name filter must be a non-empty string",
                    error_code="E002",
                    http_status_code=400,
                )
            if len(name) > 255:
                raise InvalidObjectError(
                    message="Name filter exceeds maximum length of 255 characters",
                    error_code="E003",
                    http_status_code=400,
                )
            # Validate name format (alphanumeric, underscores, and hyphens allowed)
            if not re.match(r"^[a-zA-Z0-9_-]{1,255}$", name.strip()):
                raise InvalidObjectError(
                    message="Invalid name format. Name must contain only alphanumeric characters, underscores, and hyphens",
                    error_code="E003",
                    http_status_code=400,
                )
            base_params["name"] = name.strip()

        while True:
            params = base_params.copy()
            params["limit"] = limit
            params["offset"] = offset

            response = self.api_client.get(
                self.ENDPOINT,
                params=params,
            )

            if not isinstance(response, dict):
                raise InvalidObjectError(
                    message="Invalid response format: expected dictionary",
                    error_code="E003",
                    http_status_code=500,
                    details={"error": "Response is not a dictionary"},
                )

            if "data" not in response:
                raise InvalidObjectError(
                    message="Invalid response format: missing 'data' field",
                    error_code="E003",
                    http_status_code=500,
                    details={
                        "field": "data",
                        "error": '"data" field missing in the response',
                    },
                )

            if not isinstance(response["data"], list):
                raise InvalidObjectError(
                    message="Invalid response format: 'data' field must be a list",
                    error_code="E003",
                    http_status_code=500,
                    details={
                        "field": "data",
                        "error": '"data" field must be a list',
                    },
                )

            data = response["data"]
            object_instances = [ServiceConnectionResponseModel(**item) for item in data]
            all_objects.extend(object_instances)

            # If we got fewer than 'limit' objects, we've reached the end
            if len(data) < limit:
                break

            offset += limit

        return all_objects

    def fetch(
        self,
        name: str,
    ) -> ServiceConnectionResponseModel:
        """Fetch a single service connection by name.

        Args:
            name: The name of the service connection to fetch

        Returns:
            ServiceConnectionResponseModel: The fetched service connection object

        """
        if not name:
            raise MissingQueryParameterError(
                message="Field 'name' cannot be empty",
                error_code="E003",
                http_status_code=400,
                details={
                    "field": "name",
                    "error": '"name" is not allowed to be empty',
                },
            )

        params = {
            "name": name,
            "folder": "Service Connections",  # Required for service-connections API
        }

        response = self.api_client.get(
            self.ENDPOINT,
            params=params,
        )

        if not isinstance(response, dict):
            raise InvalidObjectError(
                message="Invalid response format: expected dictionary",
                error_code="E003",
                http_status_code=500,
                details={"error": "Response is not a dictionary"},
            )

        # If we receive a data list, we need to extract the first matching item
        if "data" in response and isinstance(response["data"], list):
            if len(response["data"]) == 0:
                raise InvalidObjectError(
                    message=f"No service connection found with name: {name}",
                    error_code="E004",
                    http_status_code=404,
                    details={"error": "Service connection not found"},
                )

            for item in response["data"]:
                if item.get("name") == name:
                    return ServiceConnectionResponseModel(**item)

            # If we get here, no exact match was found
            raise InvalidObjectError(
                message=f"No exact match found for service connection with name: {name}",
                error_code="E004",
                http_status_code=404,
                details={"error": "Service connection not found"},
            )

        # Direct response with ID field (single resource response)
        if "id" in response:
            return ServiceConnectionResponseModel(**response)

        raise InvalidObjectError(
            message="Invalid response format",
            error_code="E003",
            http_status_code=500,
            details={"error": "Response format not recognized"},
        )

    def delete(
        self,
        object_id: str,
    ) -> None:
        """Delete a service connection object.

        Args:
            object_id: The ID of the object to delete

        """
        endpoint = f"{self.ENDPOINT}/{object_id}"
        self.api_client.delete(endpoint)
