"""Mobile Agent Tunnel Profiles configuration service for Strata Cloud Manager SDK.

Provides service class for managing GlobalProtect tunnel settings (tunnel profiles)
via the SCM API.
"""

# scm/config/mobile_agent/tunnel_profiles.py

# Standard library imports
import logging
from typing import Any, Dict, List, Optional

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.mobile_agent import (
    TunnelProfileCreateModel,
    TunnelProfileResponseModel,
    TunnelProfileUpdateModel,
)


class TunnelProfiles(BaseObject):
    """Manages GlobalProtect Tunnel Profiles in Palo Alto Networks' Strata Cloud Manager.

    Tunnel profiles are addressed by name within the 'Mobile Users' folder. The API
    exposes no ID-based endpoints for this resource: create and update operations
    send the folder as a query parameter, and delete operations address the profile
    by name and folder query parameters.

    Args:
        api_client: The API client instance
        max_limit (Optional[int]): Maximum number of objects to return in a single API request.
            Defaults to 2500. Must be between 1 and 5000.

    """

    ENDPOINT = "/config/mobile-agent/v1/tunnel-profiles"
    DEFAULT_MAX_LIMIT = 2500
    ABSOLUTE_MAX_LIMIT = 5000  # Maximum allowed by the API

    def __init__(
        self,
        api_client,
        max_limit: Optional[int] = None,
    ):
        """Initialize the TunnelProfiles service with the given API client.

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
            folder: The folder value to validate

        Raises:
            InvalidObjectError: If the folder is not 'Mobile Users'

        """
        if folder != "Mobile Users":
            raise InvalidObjectError(
                message="Folder must be 'Mobile Users' for GlobalProtect Tunnel Profiles",
                error_code="E003",
                http_status_code=400,
                details={"error": "Invalid folder value"},
            )

    def create(
        self,
        data: Dict[str, Any],
        folder: str = "Mobile Users",
    ) -> TunnelProfileResponseModel:
        """Create a new GlobalProtect Tunnel Profile object.

        Args:
            data: Dictionary containing the tunnel profile configuration
            folder: The folder in which the resource is defined (must be "Mobile Users")

        Returns:
            TunnelProfileResponseModel

        Raises:
            InvalidObjectError: If the provided data or folder is invalid.

        """
        self._validate_folder(folder)

        # Use the dictionary "data" to pass into Pydantic and return a modeled object
        tunnel_profile = TunnelProfileCreateModel(**data)

        # Convert back to a Python dictionary, removing any unset fields and using aliases
        payload = tunnel_profile.model_dump(
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
        return TunnelProfileResponseModel(**response)

    def update(
        self,
        data: Dict[str, Any],
        folder: str = "Mobile Users",
    ) -> TunnelProfileResponseModel:
        """Update an existing GlobalProtect Tunnel Profile object.

        The API addresses tunnel profiles by the name in the request body and the
        folder query parameter; there is no ID-based update endpoint.

        Args:
            data: Dictionary containing the update configuration (must include 'name')
            folder: The folder in which the resource is defined (must be "Mobile Users")

        Returns:
            TunnelProfileResponseModel

        Raises:
            InvalidObjectError: If the provided data or folder is invalid.

        """
        self._validate_folder(folder)

        # Use the dictionary "data" to pass into Pydantic and return a modeled object
        tunnel_profile = TunnelProfileUpdateModel(**data)

        # Convert back to a Python dictionary, removing any unset fields and using aliases
        payload = tunnel_profile.model_dump(
            exclude_unset=True,
            by_alias=True,
        )

        # Send the updated object to the remote API as JSON
        response: Dict[str, Any] = self.api_client.put(
            self.ENDPOINT,
            params={"folder": folder},
            json=payload,
        )

        # Return the API response as a new Pydantic model
        return TunnelProfileResponseModel(**response)

    def list(
        self,
        folder: str = "Mobile Users",
        name: Optional[str] = None,
        **filters,
    ) -> List[TunnelProfileResponseModel]:
        """List GlobalProtect Tunnel Profile objects with optional filtering.

        Args:
            folder: Folder name (defaults to "Mobile Users" as it's the only valid value)
            name: Optional name to filter results by (server-side filter)
            **filters: Additional filters (not currently used but included for future expansion)

        Returns:
            List[TunnelProfileResponseModel]: A list of tunnel profile objects

        Raises:
            InvalidObjectError: If the provided data or response format is invalid.

        """
        self._validate_folder(folder)

        params: Dict[str, Any] = {"folder": folder}
        if name is not None:
            params["name"] = name

        limit = self._max_limit
        offset = 0
        all_objects: List[TunnelProfileResponseModel] = []

        try:
            while True:
                request_params = {**params, "limit": limit, "offset": offset}
                response = self.api_client.get(
                    self.ENDPOINT,
                    params=request_params,
                )

                # Handle direct list response
                if isinstance(response, list):
                    data_items = response
                elif (
                    isinstance(response, dict)
                    and "data" in response
                    and isinstance(response["data"], list)
                ):
                    data_items = response["data"]
                else:
                    raise InvalidObjectError(
                        message="Invalid response format: expected list or dictionary with 'data' field",
                        error_code="E003",
                        http_status_code=500,
                        details={"error": "Response has invalid structure"},
                    )

                all_objects.extend(TunnelProfileResponseModel(**item) for item in data_items)

                if len(data_items) < limit:
                    break
                offset += limit

            return all_objects
        except Exception as e:
            self.logger.error(f"Error listing tunnel profiles: {str(e)}")
            raise

    def fetch(
        self,
        name: str,
        folder: str = "Mobile Users",
    ) -> TunnelProfileResponseModel:
        """Fetch a single GlobalProtect Tunnel Profile by name.

        Args:
            name: The name of the tunnel profile to fetch
            folder: The folder in which the resource is defined (must be "Mobile Users")

        Returns:
            TunnelProfileResponseModel: The fetched tunnel profile object

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
        all_profiles = self.list(folder=folder, name=name)
        matching_profiles = [profile for profile in all_profiles if profile.name == name]

        if not matching_profiles:
            raise InvalidObjectError(
                message=f"Tunnel profile '{name}' not found",
                error_code="E002",
                http_status_code=404,
                details={"error": "No matching tunnel profile found"},
            )

        if len(matching_profiles) > 1:
            self.logger.warning(
                f"Multiple tunnel profiles found for '{name}'. Using the first one."
            )

        return matching_profiles[0]

    def delete(
        self,
        name: str,
        folder: str = "Mobile Users",
    ) -> None:
        """Delete a GlobalProtect Tunnel Profile object.

        The API addresses tunnel profiles by name and folder query parameters;
        there is no ID-based delete endpoint.

        Args:
            name: The name of the tunnel profile to delete
            folder: The folder in which the resource is defined (must be "Mobile Users")

        Raises:
            MissingQueryParameterError: If a required query parameter is missing or empty.
            InvalidObjectError: If the provided folder is invalid.

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

        self.api_client.delete(
            self.ENDPOINT,
            params={"name": name, "folder": folder},
        )
