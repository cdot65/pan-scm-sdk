"""Internal DNS Servers configuration service for Strata Cloud Manager SDK.

Provides service class for managing internal DNS server objects via the SCM API.
"""

# scm/config/deployment/internal_dns_servers.py

# Standard library imports
import logging
from typing import Any, Dict, List, Optional

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.deployment import (
    InternalDnsServersCreateModel,
    InternalDnsServersResponseModel,
    InternalDnsServersUpdateModel,
)


class InternalDnsServers(BaseObject):
    """Manages Internal DNS Server objects in Palo Alto Networks' Strata Cloud Manager.

    Args:
        api_client: The API client instance
        max_limit (Optional[int]): Maximum number of objects to return in a single API request.
            Defaults to 2500. Must be between 1 and 5000.

    """

    ENDPOINT = "/config/deployment/v1/internal-dns-servers"
    DEFAULT_MAX_LIMIT = 2500
    ABSOLUTE_MAX_LIMIT = 5000  # Maximum allowed by the API

    def __init__(
        self,
        api_client,
        max_limit: Optional[int] = None,
    ):
        """Initialize the InternalDnsServers service with the given API client."""
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
            # Update message to match expected test format
            raise InvalidObjectError(
                "max_limit must be an integer",
                error_code="E003",
                http_status_code=400,
                details={"error": "Invalid max_limit type"},
            )

        if limit_int < 1:
            # Update message to match expected test format
            raise InvalidObjectError(
                "max_limit must be greater than 0",
                error_code="E003",
                http_status_code=400,
                details={"error": "Invalid max_limit value"},
            )

        if limit_int > self.ABSOLUTE_MAX_LIMIT:
            # Update message to match expected test format
            raise InvalidObjectError(
                f"max_limit cannot exceed {self.ABSOLUTE_MAX_LIMIT}",
                error_code="E003",
                http_status_code=400,
                details={"error": "max_limit exceeds maximum allowed value"},
            )

        return limit_int

    def create(
        self,
        data: Dict[str, Any],
    ) -> InternalDnsServersResponseModel:
        """Create a new internal DNS server object.

        Args:
            data: Dictionary containing the internal DNS server configuration

        Returns:
            InternalDnsServersResponseModel

        """
        # Use the dictionary "data" to pass into Pydantic and return a modeled object
        internal_dns_server = InternalDnsServersCreateModel(**data)

        # Convert back to a Python dictionary, removing any unset fields
        payload = internal_dns_server.model_dump(
            exclude_unset=True,
            by_alias=True,
        )

        # Send the updated object to the remote API as JSON
        response: Dict[str, Any] = self.api_client.post(
            self.ENDPOINT,
            json=payload,
        )

        # Return the API response as a new Pydantic object
        return InternalDnsServersResponseModel(**response)

    def get(
        self,
        object_id: str,
    ) -> InternalDnsServersResponseModel:
        """Get an internal DNS server object by ID.

        Args:
            object_id: The ID of the internal DNS server to retrieve

        Returns:
            InternalDnsServersResponseModel

        """
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.get(endpoint)
        return InternalDnsServersResponseModel(**response)

    def update(
        self,
        dns_server: InternalDnsServersUpdateModel,
    ) -> InternalDnsServersResponseModel:
        """Update an existing internal DNS server object.

        Args:
            dns_server: InternalDnsServersUpdateModel instance containing the update data

        Returns:
            InternalDnsServersResponseModel

        """
        # Convert to dict for API request, excluding unset fields and using aliases
        payload = dns_server.model_dump(
            exclude_unset=True,
            by_alias=True,
        )

        # Extract ID and remove from payload since it's in the URL
        object_id = str(dns_server.id)
        payload.pop("id", None)

        # Send the updated object to the remote API as JSON
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.put(
            endpoint,
            json=payload,
        )

        # Return the API response as a new Pydantic model
        return InternalDnsServersResponseModel(**response)

    def list(
        self,
        name: Optional[str] = None,
        **filters,
    ) -> List[InternalDnsServersResponseModel]:
        """List internal DNS server objects with optional filtering.

        Args:
            name: Optional DNS server name to filter by
            **filters: Additional filters

        Returns:
            List[InternalDnsServersResponseModel]: A list of internal DNS server objects

        """
        # Pagination logic
        limit = self._max_limit
        offset = 0
        all_objects = []

        params = {}

        # Add name if provided
        if name:
            params["name"] = name

        # Combine pagination parameters with any custom filters
        params.update(filters)

        while True:
            # Build request params for this page
            request_params = params.copy()
            request_params["limit"] = limit
            request_params["offset"] = offset

            response = self.api_client.get(
                self.ENDPOINT,
                params=request_params,
            )

            if not isinstance(response, dict):
                # Update message to match expected test format
                raise InvalidObjectError(
                    "Invalid response format: expected dictionary",
                    error_code="E003",
                    http_status_code=500,
                    details={"error": "Response is not a dictionary"},
                )

            if "data" not in response:
                # Update message to match expected test format
                raise InvalidObjectError(
                    "Invalid response format: missing 'data' field",
                    error_code="E003",
                    http_status_code=500,
                    details={
                        "field": "data",
                        "error": '"data" field missing in the response',
                    },
                )

            if not isinstance(response["data"], list):
                # Update message to match expected test format
                raise InvalidObjectError(
                    "Invalid response format: 'data' field must be a list",
                    error_code="E003",
                    http_status_code=500,
                    details={
                        "field": "data",
                        "error": '"data" field must be a list',
                    },
                )

            data = response["data"]
            object_instances = [InternalDnsServersResponseModel(**item) for item in data]
            all_objects.extend(object_instances)

            # If we got fewer than 'limit' objects, we've reached the end
            if len(data) < limit:
                break

            # Prepare for the next page
            offset += len(data)

        return all_objects

    def fetch(
        self,
        name: str,
    ) -> InternalDnsServersResponseModel:
        """Fetch a single internal DNS server by name.

        Args:
            name: The name of the internal DNS server to fetch

        Returns:
            InternalDnsServersResponseModel: The fetched internal DNS server object

        """
        if not name:
            # Update message to match expected test format
            raise MissingQueryParameterError(
                "Field 'name' cannot be empty",
                error_code="E003",
                http_status_code=400,
                details={
                    "field": "name",
                    "error": '"name" is not allowed to be empty',
                },
            )

        params = {"name": name}

        response = self.api_client.get(
            self.ENDPOINT,
            params=params,
        )

        if not isinstance(response, dict):
            # Update message to match expected test format
            raise InvalidObjectError(
                "Invalid response format: expected dictionary",
                error_code="E003",
                http_status_code=500,
                details={"error": "Response is not a dictionary"},
            )

        # Handle the expected format (direct object with 'id' field)
        if "id" in response:
            return InternalDnsServersResponseModel(**response)
        # Handle the alternate format (like list() with 'data' array)
        elif "data" in response and isinstance(response["data"], list):
            if not response["data"]:
                # Update message to match expected test format
                raise InvalidObjectError(
                    f"Internal DNS server '{name}' not found",
                    error_code="E002",
                    http_status_code=404,
                    details={"error": "No matching internal DNS server found"},
                )
            if len(response["data"]) > 0 and "id" not in response["data"][0]:
                # Update message to match expected test format
                raise InvalidObjectError(
                    "Invalid response format: missing 'id' field in data array",
                    error_code="E003",
                    http_status_code=500,
                    details={"error": "Response data item missing 'id' field"},
                )
            if len(response["data"]) > 1:
                self.logger.warning(
                    f"Multiple internal DNS servers found for '{name}'. Using the first one."
                )
            # Return the first item in the data array
            return InternalDnsServersResponseModel(**response["data"][0])
        else:
            # Update message to match expected test format
            raise InvalidObjectError(
                "Invalid response format: expected either 'id' or 'data' field",
                error_code="E003",
                http_status_code=500,
                details={"error": "Response has invalid structure"},
            )

    def delete(
        self,
        object_id: str,
    ) -> None:
        """Delete an internal DNS server object.

        Args:
            object_id: The ID of the object to delete

        """
        endpoint = f"{self.ENDPOINT}/{object_id}"
        self.api_client.delete(endpoint)
