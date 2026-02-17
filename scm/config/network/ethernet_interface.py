"""Ethernet Interface configuration service for Strata Cloud Manager SDK.

Provides service class for managing ethernet interface objects via the SCM API.
"""

# Standard library imports
import logging
from typing import Any, Dict, List, Optional

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.network.ethernet_interface import (
    EthernetInterfaceCreateModel,
    EthernetInterfaceResponseModel,
    EthernetInterfaceUpdateModel,
)


class EthernetInterface(BaseObject):
    """Manages Ethernet Interface objects in Palo Alto Networks' Strata Cloud Manager.

    Args:
        api_client: The API client instance
        max_limit (Optional[int]): Maximum number of objects to return in a single API request.
            Defaults to 2500. Must be between 1 and 5000.

    """

    ENDPOINT = "/config/network/v1/ethernet-interfaces"
    DEFAULT_MAX_LIMIT = 2500
    ABSOLUTE_MAX_LIMIT = 5000

    def __init__(
        self,
        api_client,
        max_limit: Optional[int] = None,
    ):
        """Initialize the EthernetInterface service with the given API client."""
        super().__init__(api_client)
        self.logger = logging.getLogger(__name__)
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
        """Validate the max_limit parameter."""
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

    def create(self, data: Dict[str, Any]) -> EthernetInterfaceResponseModel:
        """Create a new ethernet interface object."""
        ethernet = EthernetInterfaceCreateModel(**data)
        payload = ethernet.model_dump(exclude_unset=True, by_alias=True)
        response: Dict[str, Any] = self.api_client.post(self.ENDPOINT, json=payload)
        return EthernetInterfaceResponseModel(**response)

    def get(self, object_id: str) -> EthernetInterfaceResponseModel:
        """Get an ethernet interface object by ID."""
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.get(endpoint)
        return EthernetInterfaceResponseModel(**response)

    def update(self, ethernet: EthernetInterfaceUpdateModel) -> EthernetInterfaceResponseModel:
        """Update an existing ethernet interface object."""
        payload = ethernet.model_dump(exclude_unset=True, by_alias=True)
        object_id = str(ethernet.id)
        payload.pop("id", None)
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.put(endpoint, json=payload)
        return EthernetInterfaceResponseModel(**response)

    def delete(self, object_id: str) -> None:
        """Delete an ethernet interface object."""
        endpoint = f"{self.ENDPOINT}/{object_id}"
        self.api_client.delete(endpoint)

    @staticmethod
    def _apply_filters(
        interfaces: List[EthernetInterfaceResponseModel],
        filters: Dict[str, Any],
    ) -> List[EthernetInterfaceResponseModel]:
        """Apply client-side filtering to the list of ethernet interfaces."""
        filter_criteria = interfaces

        # Filter by interface mode (layer2/layer3/tap)
        if "mode" in filters:
            if not isinstance(filters["mode"], str):
                raise InvalidObjectError(
                    message="'mode' filter must be a string",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Object"},
                )
            mode = filters["mode"]
            if mode == "layer2":
                filter_criteria = [iface for iface in filter_criteria if iface.layer2 is not None]
            elif mode == "layer3":
                filter_criteria = [iface for iface in filter_criteria if iface.layer3 is not None]
            elif mode == "tap":
                filter_criteria = [iface for iface in filter_criteria if iface.tap is not None]

        # Filter by link speed
        if "link_speed" in filters:
            if not isinstance(filters["link_speed"], str):
                raise InvalidObjectError(
                    message="'link_speed' filter must be a string",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Object"},
                )
            filter_criteria = [
                iface for iface in filter_criteria if iface.link_speed == filters["link_speed"]
            ]

        # Filter by link state
        if "link_state" in filters:
            if not isinstance(filters["link_state"], str):
                raise InvalidObjectError(
                    message="'link_state' filter must be a string",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Object"},
                )
            filter_criteria = [
                iface for iface in filter_criteria if iface.link_state == filters["link_state"]
            ]

        return filter_criteria

    @staticmethod
    def _build_container_params(
        folder: Optional[str],
        snippet: Optional[str],
        device: Optional[str],
    ) -> dict:
        """Build container parameters dictionary."""
        return {
            k: v
            for k, v in {"folder": folder, "snippet": snippet, "device": device}.items()
            if v is not None
        }

    def list(
        self,
        folder: Optional[str] = None,
        snippet: Optional[str] = None,
        device: Optional[str] = None,
        exact_match: bool = False,
        exclude_folders: Optional[List[str]] = None,
        exclude_snippets: Optional[List[str]] = None,
        exclude_devices: Optional[List[str]] = None,
        **filters,
    ) -> List[EthernetInterfaceResponseModel]:
        """List ethernet interface objects with optional filtering."""
        if folder == "":
            raise MissingQueryParameterError(
                message="Field 'folder' cannot be empty",
                error_code="E003",
                http_status_code=400,
                details={"field": "folder", "error": '"folder" is not allowed to be empty'},
            )

        container_parameters = self._build_container_params(folder, snippet, device)

        if len(container_parameters) != 1:
            raise InvalidObjectError(
                message="Exactly one of 'folder', 'snippet', or 'device' must be provided.",
                error_code="E003",
                http_status_code=400,
                details={"error": "Invalid container parameters"},
            )

        limit = self._max_limit
        offset = 0
        all_objects = []

        while True:
            params = container_parameters.copy()
            params["limit"] = limit
            params["offset"] = offset

            response = self.api_client.get(self.ENDPOINT, params=params)

            if not isinstance(response, dict):
                raise InvalidObjectError(
                    message="Invalid response format: expected dictionary",
                    error_code="E003",
                    http_status_code=500,
                    details={"error": "Response is not a dictionary"},
                )

            if "data" not in response:
                raise InvalidObjectError(
                    message="Invalid response format: missing 'data' field",
                    error_code="E003",
                    http_status_code=500,
                    details={"field": "data", "error": '"data" field missing in the response'},
                )

            if not isinstance(response["data"], list):
                raise InvalidObjectError(
                    message="Invalid response format: 'data' field must be a list",
                    error_code="E003",
                    http_status_code=500,
                    details={"field": "data", "error": '"data" field must be a list'},
                )

            data = response["data"]
            object_instances = [EthernetInterfaceResponseModel(**item) for item in data]
            all_objects.extend(object_instances)

            if len(data) < limit:
                break
            offset += limit

        filtered_objects = self._apply_filters(all_objects, filters)
        container_key, container_value = next(iter(container_parameters.items()))

        if exact_match:
            filtered_objects = [
                each for each in filtered_objects if getattr(each, container_key) == container_value
            ]

        if exclude_folders and isinstance(exclude_folders, list):
            filtered_objects = [each for each in filtered_objects if each.folder not in exclude_folders]

        if exclude_snippets and isinstance(exclude_snippets, list):
            filtered_objects = [each for each in filtered_objects if each.snippet not in exclude_snippets]

        if exclude_devices and isinstance(exclude_devices, list):
            filtered_objects = [each for each in filtered_objects if each.device not in exclude_devices]

        return filtered_objects

    def fetch(
        self,
        name: str,
        folder: Optional[str] = None,
        snippet: Optional[str] = None,
        device: Optional[str] = None,
    ) -> EthernetInterfaceResponseModel:
        """Fetch a single ethernet interface by name."""
        if not name:
            raise MissingQueryParameterError(
                message="Field 'name' cannot be empty",
                error_code="E003",
                http_status_code=400,
                details={"field": "name", "error": '"name" is not allowed to be empty'},
            )

        if folder == "":
            raise MissingQueryParameterError(
                message="Field 'folder' cannot be empty",
                error_code="E003",
                http_status_code=400,
                details={"field": "folder", "error": '"folder" is not allowed to be empty'},
            )

        container_parameters = self._build_container_params(folder, snippet, device)

        if len(container_parameters) != 1:
            raise InvalidObjectError(
                message="Exactly one of 'folder', 'snippet', or 'device' must be provided.",
                error_code="E003",
                http_status_code=400,
                details={"error": "Exactly one of 'folder', 'snippet', or 'device' must be provided."},
            )

        params = {}
        params.update(container_parameters)
        params["name"] = name

        response = self.api_client.get(self.ENDPOINT, params=params)

        if not isinstance(response, dict):
            raise InvalidObjectError(
                message="Invalid response format: expected dictionary",
                error_code="E003",
                http_status_code=500,
                details={"error": "Response is not a dictionary"},
            )

        if "id" in response:
            return EthernetInterfaceResponseModel(**response)
        elif "data" in response and isinstance(response["data"], list):
            if not response["data"]:
                raise InvalidObjectError(
                    message=f"Ethernet interface '{name}' not found",
                    error_code="E002",
                    http_status_code=404,
                    details={"error": "No matching ethernet interface found"},
                )
            if "id" not in response["data"][0]:
                raise InvalidObjectError(
                    message="Invalid response format: missing 'id' field in data array",
                    error_code="E003",
                    http_status_code=500,
                    details={"error": "Response data item missing 'id' field"},
                )
            if len(response["data"]) > 1:
                self.logger.warning(f"Multiple ethernet interfaces found for '{name}'. Using the first one.")
            return EthernetInterfaceResponseModel(**response["data"][0])
        else:
            raise InvalidObjectError(
                message="Invalid response format: expected either 'id' or 'data' field",
                error_code="E003",
                http_status_code=500,
                details={"error": "Response has invalid structure"},
            )
