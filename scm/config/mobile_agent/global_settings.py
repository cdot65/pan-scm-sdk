"""Mobile Agent Global Settings configuration service for Strata Cloud Manager SDK.

Provides service class for managing GlobalProtect global settings via the SCM API.
"""

# scm/config/mobile_agent/global_settings.py

# Standard library imports
import logging
from typing import Any, Dict, Optional

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.mobile_agent import (
    GlobalSettingsResponseModel,
    GlobalSettingsUpdateModel,
)


class GlobalSettings(BaseObject):
    """Manages GlobalProtect Global Settings in Palo Alto Networks' Strata Cloud Manager.

    Global settings are a singleton configuration object with only GET and PUT
    operations. There is no POST (create) or DELETE endpoint, and no query
    parameters - the configuration always exists for the tenant.

    Args:
        api_client: The API client instance

    """

    ENDPOINT = "/config/mobile-agent/v1/global-settings"

    def __init__(
        self,
        api_client,
    ):
        """Initialize the GlobalSettings service with the given API client.

        Args:
            api_client: The API client instance.

        """
        super().__init__(api_client)
        self.logger = logging.getLogger(__name__)

    def get(self) -> GlobalSettingsResponseModel:
        """Get the current GlobalProtect global settings.

        Returns:
            GlobalSettingsResponseModel: The current global settings configuration

        Raises:
            InvalidObjectError: If the response format is invalid

        """
        response = self.api_client.get(self.ENDPOINT)

        if not isinstance(response, dict):
            raise InvalidObjectError(
                message="Invalid response format: expected dictionary",
                error_code="E003",
                http_status_code=500,
                details={"error": "Response is not a dictionary"},
            )

        try:
            return GlobalSettingsResponseModel(**response)
        except Exception as e:
            raise InvalidObjectError(
                message=f"Invalid response format: {str(e)}",
                error_code="E003",
                http_status_code=500,
                details={"error": str(e)},
            )

    def update(
        self,
        data: Dict[str, Any],
    ) -> GlobalSettingsResponseModel:
        """Update the GlobalProtect global settings.

        Args:
            data: Dictionary containing the global settings configuration

        Returns:
            GlobalSettingsResponseModel: The updated global settings configuration.
                When the API returns 200 OK with an empty body, the validated
                request payload is returned instead.

        Raises:
            InvalidObjectError: If the provided data is invalid
            MissingQueryParameterError: If the configuration data is empty

        """
        if not data:
            raise MissingQueryParameterError(
                message="Global settings configuration data cannot be empty",
                error_code="E003",
                http_status_code=400,
                details={"error": "Empty configuration data"},
            )

        try:
            # Validate input data using Pydantic model
            global_settings = GlobalSettingsUpdateModel(**data)
        except Exception as e:
            raise InvalidObjectError(
                message=f"Invalid global settings configuration: {str(e)}",
                error_code="E003",
                http_status_code=400,
                details={"error": str(e)},
            )

        # Convert back to a Python dictionary, removing any unset fields and using aliases
        payload = global_settings.model_dump(
            exclude_unset=True,
            by_alias=True,
        )

        # Send the updated object to the remote API as JSON
        response: Optional[Dict[str, Any]] = self.api_client.put(
            self.ENDPOINT,
            json=payload,
        )

        # The API responds with 200 OK and no body; echo the validated payload then
        if isinstance(response, dict):
            return GlobalSettingsResponseModel(**response)
        return GlobalSettingsResponseModel(**payload)
