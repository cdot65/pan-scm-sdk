"""Logical Router configuration service for Strata Cloud Manager SDK.

Provides service class for managing logical router objects via the SCM API.
"""

# scm/config/network/logical_router.py

# Standard library imports
import logging
from typing import Any, Dict, List, Optional

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.network import (
    LogicalRouterCreateModel,
    LogicalRouterResponseModel,
    LogicalRouterUpdateModel,
)


class LogicalRouter(BaseObject):
    """Manages Logical Router objects in Palo Alto Networks' Strata Cloud Manager.

    Args:
        api_client: The API client instance
        max_limit (Optional[int]): Maximum number of objects to return in a single API request.
            Defaults to 2500. Must be between 1 and 5000.

    """

    ENDPOINT = "/config/network/v1/logical-routers"
    DEFAULT_MAX_LIMIT = 2500
    ABSOLUTE_MAX_LIMIT = 5000  # Maximum allowed by the API

    def __init__(
        self,
        api_client,
        max_limit: Optional[int] = None,
    ):
        """Initialize the LogicalRouter service with the given API client."""
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
    ) -> LogicalRouterResponseModel:
        """Create a new logical router object.

        Args:
            data: Dictionary containing the logical router configuration

        Returns:
            LogicalRouterResponseModel

        """
        # Use the dictionary "data" to pass into Pydantic and return a modeled object
        logical_router = LogicalRouterCreateModel(**data)

        # Convert back to a Python dictionary, removing any unset fields and using aliases
        payload = logical_router.model_dump(
            exclude_unset=True,
            by_alias=True,
        )

        # Send the updated object to the remote API as JSON
        response: Dict[str, Any] = self.api_client.post(
            self.ENDPOINT,
            json=payload,
        )

        # Return the API response as a new Pydantic object
        return LogicalRouterResponseModel(**response)

    def get(
        self,
        object_id: str,
    ) -> LogicalRouterResponseModel:
        """Get a logical router object by ID.

        Args:
            object_id: The ID of the logical router to retrieve

        Returns:
            LogicalRouterResponseModel

        """
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.get(endpoint)
        return LogicalRouterResponseModel(**response)

    def update(
        self,
        router: LogicalRouterUpdateModel,
    ) -> LogicalRouterResponseModel:
        """Update an existing logical router object.

        Args:
            router: LogicalRouterUpdateModel instance containing the update data

        Returns:
            LogicalRouterResponseModel

        """
        # Convert to dict for API request, excluding unset fields and using aliases
        payload = router.model_dump(
            exclude_unset=True,
            by_alias=True,
        )

        # Extract ID and remove from payload since it's in the URL
        object_id = str(router.id)
        payload.pop("id", None)

        # Send the updated object to the remote API as JSON
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.put(
            endpoint,
            json=payload,
        )

        # Return the API response as a new Pydantic model
        return LogicalRouterResponseModel(**response)

    @staticmethod
    def _apply_filters(
        routers: List[LogicalRouterResponseModel],
        filters: Dict[str, Any],
    ) -> List[LogicalRouterResponseModel]:
        """Apply client-side filtering to the list of logical routers.

        Args:
            routers: List of LogicalRouterResponseModel objects
            filters: Dictionary of filter criteria

        Returns:
            List[LogicalRouterResponseModel]: Filtered list of logical routers

        """
        filter_criteria = routers

        # Filter by routing_stack
        if "routing_stack" in filters:
            if not isinstance(filters["routing_stack"], list):
                raise InvalidObjectError(
                    message="'routing_stack' filter must be a list",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Object"},
                )
            stacks = filters["routing_stack"]
            filter_criteria = [
                router
                for router in filter_criteria
                if router.routing_stack is not None and router.routing_stack.value in stacks
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
    ) -> List[LogicalRouterResponseModel]:
        """List logical router objects with optional filtering.

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
                - routing_stack: List[str] - Filter by routing stack values

        Returns:
            List[LogicalRouterResponseModel]: A list of logical router objects

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
                    details={
                        "field": "data",
                        "error": '"data" field missing in the response',
                    },
                )

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
            object_instances = [LogicalRouterResponseModel(**item) for item in data]
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
    ) -> LogicalRouterResponseModel:
        """Fetch a single logical router by name.

        Args:
            name: The name of the logical router to fetch
            folder: The folder in which the resource is defined
            snippet: The snippet in which the resource is defined
            device: The device in which the resource is defined

        Returns:
            LogicalRouterResponseModel: The fetched logical router object

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

        # Handle raw list response (API returns array directly without data wrapper)
        if isinstance(response, list):
            if not response:
                raise InvalidObjectError(
                    message=f"Logical router '{name}' not found",
                    error_code="E002",
                    http_status_code=404,
                    details={"error": "No matching logical router found"},
                )
            if len(response) > 1:
                self.logger.warning(
                    f"Multiple logical routers found for '{name}'. Using the first one."
                )
            return LogicalRouterResponseModel(**response[0])

        if not isinstance(response, dict):
            raise InvalidObjectError(
                message="Invalid response format: expected dictionary or list",
                error_code="E003",
                http_status_code=500,
                details={"error": "Response is not a dictionary or list"},
            )

        # Handle the expected format (direct object with 'id' field)
        if "id" in response:
            return LogicalRouterResponseModel(**response)
        # Handle the alternate format (like list() with 'data' array)
        elif "data" in response and isinstance(response["data"], list):
            if not response["data"]:
                raise InvalidObjectError(
                    message=f"Logical router '{name}' not found",
                    error_code="E002",
                    http_status_code=404,
                    details={"error": "No matching logical router found"},
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
                    f"Multiple logical routers found for '{name}'. Using the first one."
                )
            # Return the first item in the data array
            return LogicalRouterResponseModel(**response["data"][0])
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
        """Delete a logical router object.

        Args:
            object_id: The ID of the object to delete

        """
        endpoint = f"{self.ENDPOINT}/{object_id}"
        self.api_client.delete(endpoint)
