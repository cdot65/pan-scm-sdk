"""
Service classes for interacting with Devices in Palo Alto Networks' Strata Cloud Manager.

This module provides the Device class for performing CRUD operations on Device resources
in the Strata Cloud Manager.
"""

# Standard library imports
from typing import Any, Dict, Optional

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.setup.device import (
    DeviceListResponseModel,
    DeviceModel,
)


class Device(BaseObject):
    """
    Manages Device objects in Palo Alto Networks' Strata Cloud Manager.

    This class provides methods for creating, retrieving, updating, and deleting Device resources.

    Attributes:
        ENDPOINT: The API endpoint for Device resources.
        DEFAULT_MAX_LIMIT: The default maximum number of items to return in a single request.
        ABSOLUTE_MAX_LIMIT: The maximum allowed number of items to return in a single request.
    """

    ENDPOINT = "/config/setup/v1/devices"
    DEFAULT_MAX_LIMIT = 200
    ABSOLUTE_MAX_LIMIT = 1000  # Adjust as per actual API if needed

    def __init__(
        self,
        api_client,
        max_limit: int = DEFAULT_MAX_LIMIT,
    ):
        """
        Initialize the Device service class.

        Args:
            api_client: The API client instance for making HTTP requests.
            max_limit: Maximum number of items to return in a single request.
                      Defaults to DEFAULT_MAX_LIMIT.
        """
        super().__init__(api_client)
        self.max_limit = min(max_limit, self.ABSOLUTE_MAX_LIMIT)

    @property
    def max_limit(self) -> int:
        return self._max_limit

    @max_limit.setter
    def max_limit(self, value: int) -> None:
        """Set a new maximum limit for API requests."""
        self._max_limit = self._validate_max_limit(value)

    def _validate_max_limit(self, limit: Optional[int]) -> int:
        """
        Validates the max_limit parameter.

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
            return self.ABSOLUTE_MAX_LIMIT

        return limit_int

    def get(
        self,
        device_id: str,
    ) -> DeviceModel:
        """
        Get a device by its ID.

        Args:
            device_id: The ID of the device to retrieve.

        Returns:
            DeviceModel: The requested device.

        Raises:
            ObjectNotPresentError: If the device doesn't exist.
            APIError: If the API request fails.
        """
        try:
            response = self.api_client.get(f"{self.ENDPOINT}/{device_id}")
            # The API returns a list with a single device object for /devices/:id
            if isinstance(response, list) and response:
                return DeviceModel.model_validate(response[0])
            elif isinstance(response, dict):
                return DeviceModel.model_validate(response)
            else:
                raise InvalidObjectError(
                    message="Unexpected response format for device get",
                    error_code="E003",
                    http_status_code=500,
                    details={"error": "Response is not a dict or list"},
                )
        except APIError as e:
            if getattr(e, "http_status_code", None) == 404:
                raise ObjectNotPresentError(f"Device with ID {device_id} not found")
            raise

    def fetch(
        self,
        name: str,
    ) -> DeviceModel | None:
        """
        Get a device by its exact name.

        Args:
            name: The device name to retrieve.

        Returns:
            DeviceModel | None: The requested device, or None if not found.
        """
        results = self.list()
        if not results.data:
            return None
        for device in results.data:
            if device.name == name:
                return device
        return None

    def list(
        self,
        **filters: Any,
    ) -> DeviceListResponseModel:
        """
        List devices with optional server-side and client-side filtering.

        Args:
            **filters: Additional filters (labels, type, etc.).

        Returns:
            DeviceListResponseModel: Paginated response model with devices.

        Raises:
            APIError: If the API request fails.
            InvalidObjectError: If filter parameters are invalid.
        """
        params: Dict[str, Any] = {}
        # Map known filters to params if supported by API
        for key in ["type", "folder", "serial_number", "is_connected", "model"]:
            if key in filters:
                params[key] = filters[key]
        limit = self.max_limit
        offset = 0
        response = self.api_client.get(
            self.ENDPOINT,
            params={"limit": limit, "offset": offset, **params},
        )
        return DeviceListResponseModel.model_validate(response)
