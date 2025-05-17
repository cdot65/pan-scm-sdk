"""Mobile Agent Auth Settings configuration service for Strata Cloud Manager SDK.

Provides service class for managing mobile agent authentication settings via the SCM API.
"""

# scm/config/mobile_agent/auth_settings.py

# Standard library imports
import logging
from typing import Any, Dict, List, Optional

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.mobile_agent import (
    AuthSettingsCreateModel,
    AuthSettingsMoveModel,
    AuthSettingsResponseModel,
    AuthSettingsUpdateModel,
)


class AuthSettings(BaseObject):
    """Manages GlobalProtect Authentication Settings in Palo Alto Networks' Strata Cloud Manager.

    Args:
        api_client: The API client instance
        max_limit (Optional[int]): Maximum number of objects to return in a single API request.
            Defaults to 2500. Must be between 1 and 5000.

    """

    ENDPOINT = "/config/mobile-agent/v1/authentication-settings"
    DEFAULT_MAX_LIMIT = 2500
    ABSOLUTE_MAX_LIMIT = 5000  # Maximum allowed by the API

    def __init__(
        self,
        api_client,
        max_limit: Optional[int] = None,
    ):
        """Initialize the AuthSettings service with the given API client."""
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
    ) -> AuthSettingsResponseModel:
        """Create a new GlobalProtect Authentication Settings object.

        Args:
            data: Dictionary containing the authentication settings configuration

        Returns:
            AuthSettingsResponseModel

        """
        # Use the dictionary "data" to pass into Pydantic and return a modeled object
        auth_settings = AuthSettingsCreateModel(**data)

        # Convert back to a Python dictionary, removing any unset fields and using aliases
        payload = auth_settings.model_dump(
            exclude_unset=True,
            by_alias=True,
        )

        # Send the updated object to the remote API as JSON
        response: Dict[str, Any] = self.api_client.post(
            self.ENDPOINT,
            json=payload,
        )

        # Return the API response as a new Pydantic object
        return AuthSettingsResponseModel(**response)

    def get(
        self,
        object_id: str,
    ) -> AuthSettingsResponseModel:
        """Get a GlobalProtect Authentication Settings object by ID.

        Args:
            object_id: The ID of the authentication settings to retrieve

        Returns:
            AuthSettingsResponseModel

        """
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.get(endpoint)
        return AuthSettingsResponseModel(**response)

    def update(
        self,
        object_id: str,
        data: Dict[str, Any],
    ) -> AuthSettingsResponseModel:
        """Update an existing GlobalProtect Authentication Settings object.

        Args:
            object_id: The ID of the object to update
            data: Dictionary containing the update configuration

        Returns:
            AuthSettingsResponseModel

        """
        # Use the dictionary "data" to pass into Pydantic and return a modeled object
        auth_settings = AuthSettingsUpdateModel(**data)

        # Convert back to a Python dictionary, removing any unset fields and using aliases
        payload = auth_settings.model_dump(
            exclude_unset=True,
            by_alias=True,
        )

        # Send the updated object to the remote API as JSON
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.put(
            endpoint,
            json=payload,
        )

        # Return the API response as a new Pydantic model
        return AuthSettingsResponseModel(**response)

    def move(
        self,
        move_data: Dict[str, Any],
    ) -> None:
        """Move a GlobalProtect Authentication Settings object to a different position.

        Args:
            move_data: Dictionary containing the move configuration

        Returns:
            None

        """
        # Validate and create move model
        move_model = AuthSettingsMoveModel(**move_data)

        # Convert to dict for API request
        payload = move_model.model_dump(by_alias=True)

        # Send the move request to the remote API as JSON
        endpoint = f"{self.ENDPOINT}/move"
        self.api_client.post(
            endpoint,
            json=payload,
        )

    def list(
        self,
        folder: str = "Mobile Users",
        **filters,
    ) -> List[AuthSettingsResponseModel]:
        """List GlobalProtect Authentication Settings objects with optional filtering.

        Args:
            folder: Folder name (defaults to "Mobile Users" as it's the only valid value)
            **filters: Additional filters (not currently used but included for future expansion)

        Returns:
            List[AuthSettingsResponseModel]: A list of authentication settings objects

        """
        if folder != "Mobile Users":
            raise InvalidObjectError(
                message="Folder must be 'Mobile Users' for GlobalProtect Authentication Settings",
                error_code="E003",
                http_status_code=400,
                details={"error": "Invalid folder value"},
            )

        container_parameters = {"folder": folder}

        try:
            # Request all authentication settings
            response = self.api_client.get(
                self.ENDPOINT,
                params=container_parameters,
            )

            # Handle direct list response
            if isinstance(response, list):
                return [AuthSettingsResponseModel(**item) for item in response]

            # Handle dict response with data array
            if (
                isinstance(response, dict)
                and "data" in response
                and isinstance(response["data"], list)
            ):
                return [AuthSettingsResponseModel(**item) for item in response["data"]]

            # Handle unexpected response format
            raise InvalidObjectError(
                message="Invalid response format: expected list or dictionary with 'data' field",
                error_code="E003",
                http_status_code=500,
                details={"error": "Response has invalid structure"},
            )
        except Exception as e:
            self.logger.error(f"Error listing authentication settings: {str(e)}")
            raise

    def fetch(
        self,
        name: str,
        folder: str = "Mobile Users",
    ) -> AuthSettingsResponseModel:
        """Fetch a single GlobalProtect Authentication Settings by name.

        Args:
            name: The name of the authentication settings to fetch
            folder: The folder in which the resource is defined (must be "Mobile Users")

        Returns:
            AuthSettingsResponseModel: The fetched authentication settings object

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

        if folder != "Mobile Users":
            raise InvalidObjectError(
                message="Folder must be 'Mobile Users' for GlobalProtect Authentication Settings",
                error_code="E003",
                http_status_code=400,
                details={"error": "Invalid folder value"},
            )

        # Get all authentication settings and filter by name
        all_settings = self.list(folder=folder)
        matching_settings = [setting for setting in all_settings if setting.name == name]

        if not matching_settings:
            raise InvalidObjectError(
                message=f"Authentication settings '{name}' not found",
                error_code="E002",
                http_status_code=404,
                details={"error": "No matching authentication settings found"},
            )

        if len(matching_settings) > 1:
            self.logger.warning(
                f"Multiple authentication settings found for '{name}'. Using the first one."
            )

        return matching_settings[0]

    def delete(
        self,
        object_id: str,
    ) -> None:
        """Delete a GlobalProtect Authentication Settings object.

        Args:
            object_id: The ID of the object to delete

        """
        endpoint = f"{self.ENDPOINT}/{object_id}"
        self.api_client.delete(endpoint)
