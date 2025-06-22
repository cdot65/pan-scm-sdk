"""Service classes for interacting with Devices in Palo Alto Networks' Strata Cloud Manager.

This module provides the Device class for performing CRUD operations on Device resources
in the Strata Cloud Manager.
"""

# Standard library imports
from typing import Any, Dict, List, Optional

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.setup.device import DeviceResponseModel


class Device(BaseObject):
    """Manages Device objects in Palo Alto Networks' Strata Cloud Manager.

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
        """Initialize the Device service class.

        Args:
            api_client: The API client instance for making HTTP requests.
            max_limit: Maximum number of items to return in a single request.
                      Defaults to DEFAULT_MAX_LIMIT.

        """
        super().__init__(api_client)
        self.max_limit = min(max_limit, self.ABSOLUTE_MAX_LIMIT)

    @property
    def max_limit(self) -> int:
        """Get the maximum number of items to return in a single request.

        Returns:
            int: The current max_limit value.

        """
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
            return self.ABSOLUTE_MAX_LIMIT

        return limit_int

    def get(
        self,
        device_id: str,
    ) -> DeviceResponseModel:
        """Get a device by its ID.

        Args:
            device_id: The ID of the device to retrieve.

        Returns:
            DeviceResponseModel: The requested device.

        Raises:
            ObjectNotPresentError: If the device doesn't exist.
            APIError: If the API request fails.

        """
        try:
            response = self.api_client.get(f"{self.ENDPOINT}/{device_id}")
            # The API returns a list with a single device object for /devices/:id
            if isinstance(response, list) and response:
                return DeviceResponseModel.model_validate(response[0])
            elif isinstance(response, dict):
                return DeviceResponseModel.model_validate(response)
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
    ) -> DeviceResponseModel | None:
        """Get a device by its exact name.

        Args:
            name: The device name to retrieve.

        Returns:
            DeviceResponseModel | None: The requested device, or None if not found.

        """
        results = self.list()
        if not results:
            return None
        for device in results:
            if device.name == name:
                return device
        return None

    @staticmethod
    def _apply_filters(
        data: List[DeviceResponseModel],
        filters: Dict[str, Any],
    ) -> List[DeviceResponseModel]:
        """Apply client-side filters to a list of devices."""
        filtered = data

        if not filters:
            return filtered

        # Filter by labels (intersection: any label matches)
        if "labels" in filters:
            required_labels = set(filters["labels"])
            filtered = [
                f
                for f in filtered
                if getattr(f, "labels", None) and required_labels.intersection(set(f.labels))
            ]

        # Filter by parent (exact match)
        if "parent" in filters:
            parent_val = filters["parent"]
            filtered = [f for f in filtered if getattr(f, "parent", None) == parent_val]

        # Filter by type (exact match)
        if "type" in filters:
            type_val = filters["type"]
            filtered = [f for f in filtered if getattr(f, "type", None) == type_val]

        # Filter by snippets (intersection: any snippet matches)
        if "snippets" in filters:
            required_snippets = set(filters["snippets"])
            filtered = [
                f
                for f in filtered
                if getattr(f, "snippets", None) and required_snippets.intersection(set(f.snippets))
            ]

        # Filter by model (exact match)
        if "model" in filters:
            model_val = filters["model"]
            filtered = [f for f in filtered if getattr(f, "model", None) == model_val]

        # Filter by serial_number (exact match)
        if "serial_number" in filters:
            serial_val = filters["serial_number"]
            filtered = [f for f in filtered if getattr(f, "serial_number", None) == serial_val]

        # Filter by device_only (boolean match)
        if "device_only" in filters:
            device_only_val = filters["device_only"]
            filtered = [f for f in filtered if getattr(f, "device_only", None) == device_only_val]

        return filtered

    def list(
        self,
        **filters: Any,  # Accept arbitrary filters (type, folder, etc.)
    ) -> List[DeviceResponseModel]:
        """List devices with optional server-side and client-side filtering.

        Args:
            **filters: Additional filters (type, folder, serial_number, etc.).

        Returns:
            List[DeviceResponseModel]: A list of devices matching the filters.

        Raises:
            APIError: If the API request fails.
            InvalidObjectError: If filter parameters are invalid.

        """
        # Prepare API parameters for server-side filtering
        params: Dict[str, Any] = {}
        if "type" in filters:
            params["type"] = filters["type"]
        if "serial_number" in filters:
            params["serial_number"] = filters["serial_number"]
        if "model" in filters:
            params["model"] = filters["model"]

        # Initialize pagination variables
        limit = self.max_limit
        offset = 0
        all_objects = []

        while True:
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

            # Handle single-item response when filters return one object
            if "data" not in response:
                data_items = [response]
            else:
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
                data_items = response["data"]

            # Convert each item to a DeviceResponseModel instance
            object_instances = [DeviceResponseModel.model_validate(item) for item in data_items]
            all_objects.extend(object_instances)

            # If we got fewer than 'limit' objects, we've reached the end
            if len(data_items) < limit:
                break

            # Increment offset for next page
            offset += limit

        # Apply any remaining client-side filters
        filtered_folders = self._apply_filters(
            all_objects,
            {k: v for k, v in filters.items() if k not in ["labels", "type", "parent"]},
        )
        return filtered_folders
