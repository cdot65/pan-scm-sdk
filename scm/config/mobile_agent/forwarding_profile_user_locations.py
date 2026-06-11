"""Forwarding Profile User Locations configuration service for Strata Cloud Manager SDK.

Provides service class for managing GlobalProtect forwarding profile user
locations via the SCM API.
"""

# scm/config/mobile_agent/forwarding_profile_user_locations.py

# Standard library imports
import logging
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import (
    APIError,
    InvalidObjectError,
    MissingQueryParameterError,
    ObjectNotPresentError,
)
from scm.models.mobile_agent import (
    ForwardingProfileUserLocationCreateModel,
    ForwardingProfileUserLocationResponseModel,
    ForwardingProfileUserLocationUpdateModel,
)


class ForwardingProfileUserLocations(BaseObject):
    """Manages GlobalProtect Forwarding Profile User Locations in Strata Cloud Manager.

    Args:
        api_client: The API client instance
        max_limit (Optional[int]): Maximum number of objects to return in a single API request.
            Defaults to 2500. Must be between 1 and 5000.

    """

    ENDPOINT = "/config/mobile-agent/v1/forwarding-profile-user-locations"
    DEFAULT_MAX_LIMIT = 2500
    ABSOLUTE_MAX_LIMIT = 5000  # Maximum allowed by the API

    def __init__(
        self,
        api_client,
        max_limit: Optional[int] = None,
    ):
        """Initialize the ForwardingProfileUserLocations service with the given API client.

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
        """Validate that folder is 'Mobile Users'.

        Args:
            folder: The folder name to validate

        Raises:
            InvalidObjectError: If the folder is not 'Mobile Users'

        """
        if folder != "Mobile Users":
            raise InvalidObjectError(
                message="Folder must be 'Mobile Users' for forwarding profile user locations",
                error_code="E003",
                http_status_code=400,
                details={"error": "Invalid folder value"},
            )

    def create(
        self,
        data: Dict[str, Any],
        folder: str = "Mobile Users",
    ) -> ForwardingProfileUserLocationResponseModel:
        """Create a new GlobalProtect Forwarding Profile User Location.

        Args:
            data: Dictionary containing the user location configuration
            folder: The folder in which the resource is defined (must be "Mobile Users")

        Returns:
            ForwardingProfileUserLocationResponseModel

        Raises:
            InvalidObjectError: If the provided data or folder is invalid.

        """
        self._validate_folder(folder)

        # Use the dictionary "data" to pass into Pydantic and return a modeled object
        user_location = ForwardingProfileUserLocationCreateModel(**data)

        # Convert back to a Python dictionary, removing any unset fields
        payload = user_location.model_dump(exclude_unset=True)

        # Send the updated object to the remote API as JSON
        response: Dict[str, Any] = self.api_client.post(
            self.ENDPOINT,
            params={"folder": folder},
            json=payload,
        )

        # Return the API response as a new Pydantic object
        return ForwardingProfileUserLocationResponseModel(**response)

    def get(
        self,
        object_id: Union[str, UUID],
    ) -> ForwardingProfileUserLocationResponseModel:
        """Get a GlobalProtect Forwarding Profile User Location by ID.

        Args:
            object_id: The ID of the user location to retrieve

        Returns:
            ForwardingProfileUserLocationResponseModel

        Raises:
            ObjectNotPresentError: If the user location doesn't exist.
            APIError: If the API request fails.

        """
        object_id_str = str(object_id)
        try:
            response: Dict[str, Any] = self.api_client.get(f"{self.ENDPOINT}/{object_id_str}")
            return ForwardingProfileUserLocationResponseModel(**response)
        except APIError as e:
            if e.http_status_code == 404:
                raise ObjectNotPresentError(
                    f"Forwarding profile user location with ID {object_id} not found"
                )
            raise

    def update(
        self,
        user_location: ForwardingProfileUserLocationUpdateModel,
    ) -> ForwardingProfileUserLocationResponseModel:
        """Update an existing GlobalProtect Forwarding Profile User Location.

        Args:
            user_location: The ForwardingProfileUserLocationUpdateModel
                containing the updated data

        Returns:
            ForwardingProfileUserLocationResponseModel

        Raises:
            InvalidObjectError: If the update data is invalid.
            ObjectNotPresentError: If the user location doesn't exist.
            APIError: If the API request fails.

        """
        # Convert to dict for API request, excluding unset fields
        payload = user_location.model_dump(exclude_unset=True)

        # Extract ID and remove from payload since it's in the URL
        object_id = str(user_location.id)
        payload.pop("id", None)

        # Send the updated object to the remote API as JSON
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.put(
            endpoint,
            json=payload,
        )

        # Return the API response as a new Pydantic object
        return ForwardingProfileUserLocationResponseModel(**response)

    def delete(
        self,
        object_id: Union[str, UUID],
    ) -> None:
        """Delete a GlobalProtect Forwarding Profile User Location.

        Args:
            object_id: The ID of the user location to delete

        Raises:
            ObjectNotPresentError: If the user location doesn't exist.
            APIError: If the API request fails.

        """
        object_id_str = str(object_id)
        try:
            self.api_client.delete(f"{self.ENDPOINT}/{object_id_str}")
        except APIError as e:
            if e.http_status_code == 404:
                raise ObjectNotPresentError(
                    f"Forwarding profile user location with ID {object_id} not found"
                )
            raise

    def list(
        self,
        folder: str = "Mobile Users",
        name: Optional[str] = None,
    ) -> List[ForwardingProfileUserLocationResponseModel]:
        """List GlobalProtect Forwarding Profile User Locations.

        Args:
            folder: Folder name (defaults to "Mobile Users" as it's the only valid value)
            name: Filter by the name of the configuration resource (server-side)

        Returns:
            List[ForwardingProfileUserLocationResponseModel]: A list of user
                locations

        Raises:
            InvalidObjectError: If the provided data or response format is invalid.

        """
        self._validate_folder(folder)

        params: Dict[str, Any] = {"folder": folder}
        if name is not None:
            params["name"] = name

        limit = self.max_limit
        offset = 0
        all_objects: List[ForwardingProfileUserLocationResponseModel] = []

        while True:
            params.update({"limit": limit, "offset": offset})
            response = self.api_client.get(self.ENDPOINT, params=params)

            if isinstance(response, list):
                data_items = response
            elif isinstance(response, dict) and isinstance(response.get("data"), list):
                data_items = response["data"]
            else:
                raise InvalidObjectError(
                    message=(
                        "Invalid response format: expected list or dictionary with 'data' field"
                    ),
                    error_code="E003",
                    http_status_code=500,
                    details={"error": "Response has invalid structure"},
                )

            all_objects.extend(
                ForwardingProfileUserLocationResponseModel(**item) for item in data_items
            )

            if len(data_items) < limit:
                break
            offset += limit

        return all_objects

    def fetch(
        self,
        name: str,
        folder: str = "Mobile Users",
    ) -> ForwardingProfileUserLocationResponseModel:
        """Fetch a single GlobalProtect Forwarding Profile User Location by name.

        Args:
            name: The name of the user location to fetch
            folder: The folder in which the resource is defined (must be "Mobile Users")

        Returns:
            ForwardingProfileUserLocationResponseModel: The fetched user
                location object

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
        results = self.list(folder=folder, name=name)
        matches = [item for item in results if item.name == name]

        if not matches:
            raise InvalidObjectError(
                message=f"Forwarding profile user location '{name}' not found",
                error_code="E002",
                http_status_code=404,
                details={"error": "No matching forwarding profile user location found"},
            )

        if len(matches) > 1:
            self.logger.warning(
                f"Multiple forwarding profile user locations found for '{name}'. "
                "Using the first one."
            )

        return matches[0]
