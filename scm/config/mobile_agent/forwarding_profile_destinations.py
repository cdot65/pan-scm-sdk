"""Mobile Agent Forwarding Profile Destinations configuration service for Strata Cloud Manager SDK.

Provides service class for managing GlobalProtect forwarding profile destinations via the SCM API.
"""

# scm/config/mobile_agent/forwarding_profile_destinations.py

# Standard library imports
import logging
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.mobile_agent import (
    ForwardingProfileDestinationCreateModel,
    ForwardingProfileDestinationResponseModel,
    ForwardingProfileDestinationUpdateModel,
)


class ForwardingProfileDestinations(BaseObject):
    """Manages GlobalProtect Forwarding Profile Destinations in Palo Alto Networks' Strata Cloud Manager.

    Args:
        api_client: The API client instance
        max_limit (Optional[int]): Maximum number of objects to return in a single API request.
            Defaults to 2500. Must be between 1 and 5000.

    """

    ENDPOINT = "/config/mobile-agent/v1/forwarding-profile-destinations"
    DEFAULT_MAX_LIMIT = 2500
    ABSOLUTE_MAX_LIMIT = 5000  # Maximum allowed by the API

    def __init__(
        self,
        api_client,
        max_limit: Optional[int] = None,
    ):
        """Initialize the ForwardingProfileDestinations service with the given API client.

        Args:
            api_client: The API client instance.
            max_limit: Maximum number of items per API request. Defaults to API maximum.

        """
        super().__init__(api_client)
        self.logger = logging.getLogger(__name__)

        # Validate and set max_limit
        self._max_limit = self._validate_max_limit(max_limit)

    @property
    def max_limit(self) -> int:
        """Get the current maximum limit for API requests.

        Returns:
            int

        """
        return self._max_limit

    @max_limit.setter
    def max_limit(self, value: int) -> None:
        """Set a new maximum limit for API requests.

        Args:
            value: The maximum number of items to return in a single API request.

        """
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

    @staticmethod
    def _validate_folder(folder: str) -> None:
        """Validate that the folder is 'Mobile Users'.

        Args:
            folder: The folder name to validate

        Raises:
            InvalidObjectError: If the folder is not 'Mobile Users'

        """
        if folder != "Mobile Users":
            raise InvalidObjectError(
                message=(
                    "Folder must be 'Mobile Users' for GlobalProtect Forwarding Profile "
                    "Destinations"
                ),
                error_code="E003",
                http_status_code=400,
                details={"error": "Invalid folder value"},
            )

    def create(
        self,
        data: Dict[str, Any],
        folder: str = "Mobile Users",
    ) -> ForwardingProfileDestinationResponseModel:
        """Create a new GlobalProtect Forwarding Profile Destination object.

        The folder is sent as a query parameter, per the SCM mobile-agent API. It may be
        supplied either as the `folder` argument or as a `folder` key in `data`.

        Args:
            data: Dictionary containing the destination configuration
            folder: Folder name (defaults to "Mobile Users" as it's the only valid value)

        Returns:
            ForwardingProfileDestinationResponseModel

        """
        # The folder is a query parameter, not part of the request body
        data = dict(data)
        folder = data.pop("folder", folder)
        self._validate_folder(folder)

        # Use the dictionary "data" to pass into Pydantic and return a modeled object
        destination = ForwardingProfileDestinationCreateModel(**data)

        # Convert back to a Python dictionary, removing any unset fields and using aliases
        payload = destination.model_dump(
            exclude_unset=True,
            by_alias=True,
        )

        # Send the updated object to the remote API as JSON
        response: Dict[str, Any] = self.api_client.post(
            self.ENDPOINT,
            params={"folder": folder},
            json=payload,
        )

        # Return the API response as a new Pydantic object
        return ForwardingProfileDestinationResponseModel(**response)

    def get(
        self,
        object_id: Union[str, UUID],
    ) -> ForwardingProfileDestinationResponseModel:
        """Get a GlobalProtect Forwarding Profile Destination object by ID.

        Args:
            object_id: The ID of the destination to retrieve

        Returns:
            ForwardingProfileDestinationResponseModel

        """
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.get(endpoint)
        return ForwardingProfileDestinationResponseModel(**response)

    def update(
        self,
        object_id: Union[str, UUID],
        data: Dict[str, Any],
    ) -> ForwardingProfileDestinationResponseModel:
        """Update an existing GlobalProtect Forwarding Profile Destination object.

        Args:
            object_id: The ID of the object to update
            data: Dictionary containing the update configuration

        Returns:
            ForwardingProfileDestinationResponseModel

        """
        # Use the dictionary "data" to pass into Pydantic and return a modeled object
        destination = ForwardingProfileDestinationUpdateModel(**data)

        # Convert back to a Python dictionary, removing any unset fields and using aliases
        payload = destination.model_dump(
            exclude_unset=True,
            by_alias=True,
        )

        # The object ID is provided in the URL path, not the request body
        payload.pop("id", None)

        # Send the updated object to the remote API as JSON
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.put(
            endpoint,
            json=payload,
        )

        # Return the API response as a new Pydantic model
        return ForwardingProfileDestinationResponseModel(**response)

    def list(
        self,
        folder: str = "Mobile Users",
        name: Optional[str] = None,
        **filters,
    ) -> List[ForwardingProfileDestinationResponseModel]:
        """List GlobalProtect Forwarding Profile Destination objects with optional filtering.

        Args:
            folder: Folder name (defaults to "Mobile Users" as it's the only valid value)
            name: Filter by destination name (server-side)
            **filters: Additional filters (not currently used but included for future expansion)

        Returns:
            List[ForwardingProfileDestinationResponseModel]: A list of destination objects

        Raises:
            InvalidObjectError: If the provided data or response format is invalid.

        """
        self._validate_folder(folder)

        params: Dict[str, Any] = {"folder": folder}
        if name is not None:
            params["name"] = name

        limit = self.max_limit
        offset = 0
        all_objects: List[ForwardingProfileDestinationResponseModel] = []

        while True:
            params.update({"limit": limit, "offset": offset})
            response = self.api_client.get(
                self.ENDPOINT,
                params=params,
            )

            if (
                isinstance(response, dict)
                and "data" in response
                and isinstance(response["data"], list)
            ):
                data_items = response["data"]
            elif isinstance(response, list):
                data_items = response
            else:
                raise InvalidObjectError(
                    message="Invalid response format: expected list or dictionary with 'data' field",
                    error_code="E003",
                    http_status_code=500,
                    details={"error": "Response has invalid structure"},
                )

            all_objects.extend(
                ForwardingProfileDestinationResponseModel(**item) for item in data_items
            )

            if len(data_items) < limit:
                break
            offset += limit

        return all_objects

    def fetch(
        self,
        name: str,
        folder: str = "Mobile Users",
    ) -> ForwardingProfileDestinationResponseModel:
        """Fetch a single GlobalProtect Forwarding Profile Destination by name.

        Args:
            name: The name of the destination to fetch
            folder: The folder in which the resource is defined (must be "Mobile Users")

        Returns:
            ForwardingProfileDestinationResponseModel: The fetched destination object

        Raises:
            MissingQueryParameterError: If a required query parameter is missing or empty.
            InvalidObjectError: If the provided data or response format is invalid.

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

        self._validate_folder(folder)

        # Filter server-side by name, then match exactly
        all_destinations = self.list(folder=folder, name=name)
        matching_destinations = [
            destination for destination in all_destinations if destination.name == name
        ]

        if not matching_destinations:
            raise InvalidObjectError(
                message=f"Forwarding profile destination '{name}' not found",
                error_code="E002",
                http_status_code=404,
                details={"error": "No matching forwarding profile destination found"},
            )

        if len(matching_destinations) > 1:
            self.logger.warning(
                f"Multiple forwarding profile destinations found for '{name}'. Using the first one."
            )

        return matching_destinations[0]

    def delete(
        self,
        object_id: Union[str, UUID],
    ) -> None:
        """Delete a GlobalProtect Forwarding Profile Destination object.

        Args:
            object_id: The ID of the object to delete

        """
        endpoint = f"{self.ENDPOINT}/{object_id}"
        self.api_client.delete(endpoint)
