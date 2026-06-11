"""Mobile Agent Infrastructure Settings configuration service for Strata Cloud Manager SDK.

Provides service class for managing GlobalProtect infrastructure settings via the SCM API.
"""

# scm/config/mobile_agent/infrastructure_settings.py

# Standard library imports
import logging
from typing import Any, Dict, List, Optional

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.mobile_agent import (
    InfrastructureSettingsCreateModel,
    InfrastructureSettingsResponseModel,
    InfrastructureSettingsUpdateModel,
)


class InfrastructureSettings(BaseObject):
    """Manages GlobalProtect Infrastructure Settings in Palo Alto Networks' Strata Cloud Manager.

    Infrastructure settings are addressed by name within the 'Mobile Users' folder.
    The API has no /{id} paths for this resource: create, update, and delete all
    address the object via the 'name' and 'folder' query parameters.

    Args:
        api_client: The API client instance
        max_limit (Optional[int]): Maximum number of objects to return in a single API request.
            Defaults to 2500. Must be between 1 and 5000.

    """

    ENDPOINT = "/config/mobile-agent/v1/infrastructure-settings"
    DEFAULT_MAX_LIMIT = 2500
    ABSOLUTE_MAX_LIMIT = 5000  # Maximum allowed by the API

    def __init__(
        self,
        api_client,
        max_limit: Optional[int] = None,
    ):
        """Initialize the InfrastructureSettings service with the given API client.

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
            folder: The folder value to validate

        Raises:
            InvalidObjectError: If the folder is not 'Mobile Users'

        """
        if folder != "Mobile Users":
            raise InvalidObjectError(
                message="Folder must be 'Mobile Users' for GlobalProtect Infrastructure Settings",
                error_code="E003",
                http_status_code=400,
                details={"error": "Invalid folder value"},
            )

    @staticmethod
    def _validate_name(name: str) -> None:
        """Validate that name is not empty.

        Args:
            name: The name value to validate

        Raises:
            MissingQueryParameterError: If the name is empty

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

    def create(
        self,
        data: Dict[str, Any],
        folder: str = "Mobile Users",
    ) -> Optional[InfrastructureSettingsResponseModel]:
        """Create a new GlobalProtect Infrastructure Settings object.

        Args:
            data: Dictionary containing the infrastructure settings configuration
            folder: Folder name (defaults to "Mobile Users" as it's the only valid value)

        Returns:
            Optional[InfrastructureSettingsResponseModel]: The created object, or None
                when the API returns 201 Created with an empty body.

        Raises:
            InvalidObjectError: If the provided data or folder is invalid.

        """
        self._validate_folder(folder)

        # Use the dictionary "data" to pass into Pydantic and return a modeled object
        infrastructure_settings = InfrastructureSettingsCreateModel(**data)

        # Convert back to a Python dictionary, removing any unset fields and using aliases
        payload = infrastructure_settings.model_dump(
            exclude_unset=True,
            by_alias=True,
        )

        # Send the new object to the remote API as JSON; the folder is a query parameter
        response: Optional[Dict[str, Any]] = self.api_client.post(
            self.ENDPOINT,
            params={"folder": folder},
            json=payload,
        )

        # The API responds with 201 Created and no body; return the body if one is present
        if isinstance(response, dict):
            return InfrastructureSettingsResponseModel(**response)
        return None

    def update(
        self,
        data: Dict[str, Any],
        folder: str = "Mobile Users",
    ) -> Optional[InfrastructureSettingsResponseModel]:
        """Update an existing GlobalProtect Infrastructure Settings object.

        The object is addressed by the 'name' field in the payload together with
        the folder query parameter; there is no ID-based update path.

        Args:
            data: Dictionary containing the update configuration
            folder: Folder name (defaults to "Mobile Users" as it's the only valid value)

        Returns:
            Optional[InfrastructureSettingsResponseModel]: The updated object, or None
                when the API returns 200 OK with an empty body.

        Raises:
            InvalidObjectError: If the provided data or folder is invalid.

        """
        self._validate_folder(folder)

        # Use the dictionary "data" to pass into Pydantic and return a modeled object
        infrastructure_settings = InfrastructureSettingsUpdateModel(**data)

        # Convert back to a Python dictionary, removing any unset fields and using aliases
        payload = infrastructure_settings.model_dump(
            exclude_unset=True,
            by_alias=True,
        )

        # Send the updated object to the remote API as JSON; the folder is a query parameter
        response: Optional[Dict[str, Any]] = self.api_client.put(
            self.ENDPOINT,
            params={"folder": folder},
            json=payload,
        )

        # The API responds with 200 OK and no body; return the body if one is present
        if isinstance(response, dict):
            return InfrastructureSettingsResponseModel(**response)
        return None

    def list(
        self,
        name: str,
        folder: str = "Mobile Users",
        **filters,
    ) -> List[InfrastructureSettingsResponseModel]:
        """List GlobalProtect Infrastructure Settings objects.

        The API requires both 'name' and 'folder' query parameters for this endpoint.

        Args:
            name: The name of the infrastructure settings (required by the API)
            folder: Folder name (defaults to "Mobile Users" as it's the only valid value)
            **filters: Additional filters (not currently used but included for future expansion)

        Returns:
            List[InfrastructureSettingsResponseModel]: A list of infrastructure settings objects

        Raises:
            MissingQueryParameterError: If a required query parameter is missing or empty.
            InvalidObjectError: If the provided data or response format is invalid.

        """
        self._validate_name(name)
        self._validate_folder(folder)

        params = {
            "name": name,
            "folder": folder,
        }

        try:
            # Request the infrastructure settings
            response = self.api_client.get(
                self.ENDPOINT,
                params=params,
            )

            # Handle direct list response (the API may nest lists; flatten one level)
            if isinstance(response, list):
                items: List[Dict[str, Any]] = []
                for item in response:
                    if isinstance(item, list):
                        items.extend(item)
                    else:
                        items.append(item)
                return [InfrastructureSettingsResponseModel(**item) for item in items]

            # Handle dict response with data array
            if (
                isinstance(response, dict)
                and "data" in response
                and isinstance(response["data"], list)
            ):
                return [
                    InfrastructureSettingsResponseModel(**item) for item in response["data"]
                ]

            # Handle unexpected response format
            raise InvalidObjectError(
                message="Invalid response format: expected list or dictionary with 'data' field",
                error_code="E003",
                http_status_code=500,
                details={"error": "Response has invalid structure"},
            )
        except Exception as e:
            self.logger.error(f"Error listing infrastructure settings: {str(e)}")
            raise

    def fetch(
        self,
        name: str,
        folder: str = "Mobile Users",
    ) -> InfrastructureSettingsResponseModel:
        """Fetch a single GlobalProtect Infrastructure Settings by name.

        Args:
            name: The name of the infrastructure settings to fetch
            folder: The folder in which the resource is defined (must be "Mobile Users")

        Returns:
            InfrastructureSettingsResponseModel: The fetched infrastructure settings object

        Raises:
            MissingQueryParameterError: If a required query parameter is missing or empty.
            InvalidObjectError: If the provided data or response format is invalid.

        """
        all_settings = self.list(name=name, folder=folder)
        matching_settings = [setting for setting in all_settings if setting.name == name]

        if not matching_settings:
            raise InvalidObjectError(
                message=f"Infrastructure settings '{name}' not found",
                error_code="E002",
                http_status_code=404,
                details={"error": "No matching infrastructure settings found"},
            )

        if len(matching_settings) > 1:
            self.logger.warning(
                f"Multiple infrastructure settings found for '{name}'. Using the first one."
            )

        return matching_settings[0]

    def delete(
        self,
        name: str,
        folder: str = "Mobile Users",
    ) -> None:
        """Delete a GlobalProtect Infrastructure Settings object.

        The object is addressed by the 'name' and 'folder' query parameters;
        there is no ID-based delete path.

        Args:
            name: The name of the infrastructure settings to delete
            folder: Folder name (defaults to "Mobile Users" as it's the only valid value)

        Raises:
            MissingQueryParameterError: If a required query parameter is missing or empty.
            InvalidObjectError: If the provided folder is invalid.

        """
        self._validate_name(name)
        self._validate_folder(folder)

        self.api_client.delete(
            self.ENDPOINT,
            params={
                "name": name,
                "folder": folder,
            },
        )
