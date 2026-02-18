"""DHCP Interface configuration service for Strata Cloud Manager SDK.

Provides service class for managing DHCP server and relay configurations
on firewall interfaces via the SCM API.
"""

# scm/config/network/dhcp_interface.py

# Standard library imports
import logging
from typing import Any, Dict, List, Optional

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.network import (
    DhcpInterfaceCreateModel,
    DhcpInterfaceResponseModel,
    DhcpInterfaceUpdateModel,
)


class DhcpInterface(BaseObject):
    """Manages DHCP Interface objects in Palo Alto Networks' Strata Cloud Manager.

    Args:
        api_client: The API client instance
        max_limit (Optional[int]): Maximum number of objects to return in a single API request.
            Defaults to 2500. Must be between 1 and 5000.

    Note:
        **Known SCM API limitation (as of 2026-02):** The DHCP Interface API endpoints
        ``GET /dhcp-interfaces/{id}``, ``PUT /dhcp-interfaces/{id}``, and
        ``DELETE /dhcp-interfaces/{id}`` return 404 despite being documented on pan.dev.
        Only ``GET /dhcp-interfaces`` (list) and ``POST /dhcp-interfaces`` (create) are
        functional. The ``get()``, ``update()``, ``fetch()``, and ``delete()`` methods on
        this class will raise ``NotImplementedError`` until the API is fixed. Use ``list()``
        with client-side filtering as a workaround.

    """

    ENDPOINT = "/config/network/v1/dhcp-interfaces"
    DEFAULT_MAX_LIMIT = 2500
    ABSOLUTE_MAX_LIMIT = 5000  # Maximum allowed by the API

    def __init__(
        self,
        api_client,
        max_limit: Optional[int] = None,
    ):
        """Initialize the DhcpInterface service with the given API client."""
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
    ) -> DhcpInterfaceResponseModel:
        """Create a new DHCP interface configuration.

        Args:
            data: Dictionary containing the DHCP interface configuration

        Returns:
            DhcpInterfaceResponseModel

        """
        # Use the dictionary "data" to pass into Pydantic and return a modeled object
        dhcp_interface = DhcpInterfaceCreateModel(**data)

        # Convert back to a Python dictionary, removing any unset fields and using aliases
        payload = dhcp_interface.model_dump(
            exclude_unset=True,
            by_alias=True,
        )

        # Send the updated object to the remote API as JSON
        response: Dict[str, Any] = self.api_client.post(
            self.ENDPOINT,
            json=payload,
        )

        # Return the API response as a new Pydantic object
        return DhcpInterfaceResponseModel(**response)

    def get(
        self,
        object_id: str,
    ) -> DhcpInterfaceResponseModel:
        """Get a DHCP interface configuration by ID.

        Args:
            object_id: The ID of the DHCP interface to retrieve

        Returns:
            DhcpInterfaceResponseModel

        Raises:
            NotImplementedError: The SCM API ``GET /dhcp-interfaces/{id}`` endpoint
                returns 404. Use ``list()`` with client-side filtering instead.

        """
        raise NotImplementedError(
            "The SCM API does not currently support GET /dhcp-interfaces/{id}. "
            "This endpoint returns 404 despite being documented on pan.dev. "
            "Use list() with client-side filtering as a workaround."
        )

    def update(
        self,
        dhcp_interface: DhcpInterfaceUpdateModel,
    ) -> DhcpInterfaceResponseModel:
        """Update an existing DHCP interface configuration.

        Args:
            dhcp_interface: DhcpInterfaceUpdateModel instance containing the update data

        Returns:
            DhcpInterfaceResponseModel

        Raises:
            NotImplementedError: The SCM API ``PUT /dhcp-interfaces/{id}`` endpoint
                returns 404. Re-create the DHCP interface as a workaround.

        """
        raise NotImplementedError(
            "The SCM API does not currently support PUT /dhcp-interfaces/{id}. "
            "This endpoint returns 404 despite being documented on pan.dev. "
            "Delete and re-create the DHCP interface as a workaround."
        )

    @staticmethod
    def _apply_filters(
        dhcp_interfaces: List[DhcpInterfaceResponseModel],
        filters: Dict[str, Any],
    ) -> List[DhcpInterfaceResponseModel]:
        """Apply client-side filtering to the list of DHCP interfaces.

        Args:
            dhcp_interfaces: List of DhcpInterfaceResponseModel objects
            filters: Dictionary of filter criteria

        Returns:
            List[DhcpInterfaceResponseModel]: Filtered list of DHCP interfaces

        """
        filter_criteria = dhcp_interfaces

        # Filter by mode (server mode)
        if "mode" in filters:
            if not isinstance(filters["mode"], list):
                raise InvalidObjectError(
                    message="'mode' filter must be a list",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Object"},
                )
            modes = filters["mode"]
            filter_criteria = [
                iface
                for iface in filter_criteria
                if iface.server and iface.server.mode and iface.server.mode.value in modes
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
    ) -> List[DhcpInterfaceResponseModel]:
        """List DHCP interface objects with optional filtering.

        Args:
            folder: Optional folder name
            snippet: Optional snippet name
            device: Optional device name
            exact_match: If True, only return objects whose container
                        exactly matches the provided container parameter
            exclude_folders: List of folder names to exclude from results
            exclude_snippets: List of snippet values to exclude from results
            exclude_devices: List of device values to exclude from results
            **filters: Additional filters including:
                - mode: List[str] - Filter by DHCP server mode (e.g., ["auto", "enabled"])

        Returns:
            List[DhcpInterfaceResponseModel]: A list of DHCP interface objects

        """
        if folder == "":
            raise MissingQueryParameterError(
                message="Field 'folder' cannot be empty",
                error_code="E003",
                http_status_code=400,
                details={
                    "field": "folder",
                    "error": '"folder" is not allowed to be empty',
                },
            )

        container_parameters = self._build_container_params(
            folder,
            snippet,
            device,
        )

        if len(container_parameters) != 1:
            raise InvalidObjectError(
                message="Exactly one of 'folder', 'snippet', or 'device' must be provided.",
                error_code="E003",
                http_status_code=400,
                details={"error": "Invalid container parameters"},
            )

        # Pagination logic
        limit = self._max_limit
        offset = 0
        all_objects = []

        while True:
            params = container_parameters.copy()
            params["limit"] = limit
            params["offset"] = offset

            response = self.api_client.get(
                self.ENDPOINT,
                params=params,
            )

            # The DHCP API returns a raw array instead of {"data": [...]}
            if isinstance(response, list):
                data = response
            elif isinstance(response, dict) and "data" in response:
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
                data = response["data"]
            else:
                raise InvalidObjectError(
                    message="Invalid response format: expected list or dictionary with 'data' field",
                    error_code="E003",
                    http_status_code=500,
                    details={"error": "Response is not a list or dictionary with 'data' field"},
                )
            object_instances = [DhcpInterfaceResponseModel(**item) for item in data]
            all_objects.extend(object_instances)

            # If we got fewer than 'limit' objects, we've reached the end
            if len(data) < limit:
                break

            offset += limit

        # Apply existing filters first
        filtered_objects = self._apply_filters(
            all_objects,
            filters,
        )

        # Determine which container key and value we are filtering on
        container_key, container_value = next(iter(container_parameters.items()))

        # If exact_match is True, filter out filtered_objects that don't match exactly
        if exact_match:
            filtered_objects = [
                each for each in filtered_objects if getattr(each, container_key) == container_value
            ]

        # Exclude folders if provided
        if exclude_folders and isinstance(exclude_folders, list):
            filtered_objects = [
                each for each in filtered_objects if each.folder not in exclude_folders
            ]

        # Exclude snippets if provided
        if exclude_snippets and isinstance(exclude_snippets, list):
            filtered_objects = [
                each for each in filtered_objects if each.snippet not in exclude_snippets
            ]

        # Exclude devices if provided
        if exclude_devices and isinstance(exclude_devices, list):
            filtered_objects = [
                each for each in filtered_objects if each.device not in exclude_devices
            ]

        return filtered_objects

    def fetch(
        self,
        name: str,
        folder: Optional[str] = None,
        snippet: Optional[str] = None,
        device: Optional[str] = None,
    ) -> DhcpInterfaceResponseModel:
        """Fetch a single DHCP interface by name.

        Args:
            name: The name of the DHCP interface to fetch
            folder: The folder in which the resource is defined
            snippet: The snippet in which the resource is defined
            device: The device in which the resource is defined

        Returns:
            DhcpInterfaceResponseModel: The fetched DHCP interface object

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

        if folder == "":
            raise MissingQueryParameterError(
                message="Field 'folder' cannot be empty",
                error_code="E003",
                http_status_code=400,
                details={
                    "field": "folder",
                    "error": '"folder" is not allowed to be empty',
                },
            )

        params = {}

        container_parameters = self._build_container_params(
            folder,
            snippet,
            device,
        )

        if len(container_parameters) != 1:
            raise InvalidObjectError(
                message="Exactly one of 'folder', 'snippet', or 'device' must be provided.",
                error_code="E003",
                http_status_code=400,
                details={
                    "error": "Exactly one of 'folder', 'snippet', or 'device' must be provided."
                },
            )

        params.update(container_parameters)
        params["name"] = name

        response = self.api_client.get(
            self.ENDPOINT,
            params=params,
        )

        # The DHCP API returns a raw array instead of {"data": [...]}
        if isinstance(response, list):
            if not response:
                raise InvalidObjectError(
                    message=f"DHCP interface '{name}' not found",
                    error_code="E002",
                    http_status_code=404,
                    details={"error": "No matching DHCP interface found"},
                )
            if len(response) > 1:
                self.logger.warning(
                    f"Multiple DHCP interfaces found for '{name}'. Using the first one."
                )
            return DhcpInterfaceResponseModel(**response[0])

        if not isinstance(response, dict):
            raise InvalidObjectError(
                message="Invalid response format: expected dictionary or list",
                error_code="E003",
                http_status_code=500,
                details={"error": "Response is not a dictionary or list"},
            )

        # Handle the expected format (direct object with 'id' field)
        if "id" in response:
            return DhcpInterfaceResponseModel(**response)
        # Handle the alternate format (like list() with 'data' array)
        elif "data" in response and isinstance(response["data"], list):
            if not response["data"]:
                raise InvalidObjectError(
                    message=f"DHCP interface '{name}' not found",
                    error_code="E002",
                    http_status_code=404,
                    details={"error": "No matching DHCP interface found"},
                )
            if "id" not in response["data"][0]:
                raise InvalidObjectError(
                    message="Invalid response format: missing 'id' field in data array",
                    error_code="E003",
                    http_status_code=500,
                    details={"error": "Response data item missing 'id' field"},
                )
            if len(response["data"]) > 1:
                self.logger.warning(
                    f"Multiple DHCP interfaces found for '{name}'. Using the first one."
                )
            # Return the first item in the data array
            return DhcpInterfaceResponseModel(**response["data"][0])
        else:
            raise InvalidObjectError(
                message="Invalid response format: expected either 'id' or 'data' field",
                error_code="E003",
                http_status_code=500,
                details={"error": "Response has invalid structure"},
            )

    def delete(
        self,
        object_id: str,
    ) -> None:
        """Delete a DHCP interface configuration.

        Args:
            object_id: The ID of the object to delete

        Raises:
            NotImplementedError: The SCM API ``DELETE /dhcp-interfaces/{id}`` endpoint
                returns 404. Remove the DHCP configuration via the SCM UI or by
                deleting the parent interface.

        """
        raise NotImplementedError(
            "The SCM API does not currently support DELETE /dhcp-interfaces/{id}. "
            "This endpoint returns 404 despite being documented on pan.dev. "
            "Remove the DHCP configuration via the SCM UI or by deleting the parent interface."
        )
