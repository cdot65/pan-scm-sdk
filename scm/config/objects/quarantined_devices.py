"""Quarantined Devices configuration service for Strata Cloud Manager SDK.

Provides service class for managing quarantined device objects via the SCM API.
"""

# scm/config/objects/quarantined_devices.py

# Standard library imports
import logging
from typing import Any, Dict, List, Optional

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.objects import (
    QuarantinedDevicesCreateModel,
    QuarantinedDevicesListParamsModel,
    QuarantinedDevicesResponseModel,
)


class QuarantinedDevices(BaseObject):
    """Manages Quarantined Devices in Palo Alto Networks' Strata Cloud Manager.

    Args:
        api_client: The API client instance

    """

    ENDPOINT = "/config/objects/v1/quarantined-devices"

    def __init__(
        self,
        api_client,
    ):
        """Initialize the QuarantinedDevices service with the given API client."""
        super().__init__(api_client)
        self.logger = logging.getLogger(__name__)

    def create(
        self,
        data: Dict[str, Any],
    ) -> QuarantinedDevicesResponseModel:
        """Create a new quarantined device.

        Args:
            data: Dictionary containing the quarantined device data

        Returns:
            QuarantinedDevicesResponseModel: The created quarantined device

        Raises:
            InvalidObjectError: If the request payload is invalid

        """
        try:
            # Validate the data using Pydantic model
            quarantined_device = QuarantinedDevicesCreateModel(**data)

            # Convert to dictionary for API request, excluding unset fields
            payload = quarantined_device.model_dump(exclude_unset=True)

            # Send the request to the API
            response: Dict[str, Any] = self.api_client.post(
                self.ENDPOINT,
                json=payload,
            )

            # Return the API response as a Pydantic model
            return QuarantinedDevicesResponseModel(**response)
        except Exception as e:
            self.logger.error(f"Error creating quarantined device: {e}", exc_info=True)
            raise

    def list(
        self,
        host_id: Optional[str] = None,
        serial_number: Optional[str] = None,
    ) -> List[QuarantinedDevicesResponseModel]:
        """List quarantined devices with optional filtering.

        Args:
            host_id: Filter by device host ID
            serial_number: Filter by device serial number

        Returns:
            List[QuarantinedDevicesResponseModel]: A list of quarantined devices matching the filters

        Raises:
            InvalidObjectError: If the response format is invalid

        """
        # Create filter params using Pydantic model for validation
        params_model = QuarantinedDevicesListParamsModel(
            host_id=host_id,
            serial_number=serial_number,
        )
        params = params_model.model_dump(exclude_none=True)

        # Make the API request
        response = self.api_client.get(
            self.ENDPOINT,
            params=params,
        )

        # Check if the response is a list
        if not isinstance(response, list):
            raise InvalidObjectError(
                message="Invalid response format: expected list",
                error_code="E003",
                http_status_code=500,
                details={"error": "Response is not a list"},
            )

        # Convert the response items to Pydantic models
        return [QuarantinedDevicesResponseModel(**item) for item in response]

    def delete(
        self,
        host_id: str,
    ) -> None:
        """Delete a quarantined device by host ID.

        Args:
            host_id: The host ID of the quarantined device to delete

        Raises:
            MissingQueryParameterError: If host_id is empty or None

        """
        if not host_id:
            raise MissingQueryParameterError(
                message="Field 'host_id' cannot be empty",
                error_code="E003",
                http_status_code=400,
                details={
                    "field": "host_id",
                    "error": "'host_id' is not allowed to be empty",
                },
            )

        # Make the delete request with the host_id as a query parameter
        self.api_client.delete(
            self.ENDPOINT,
            params={"host_id": host_id},
        )
