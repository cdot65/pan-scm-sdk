"""Schedules configuration service for Strata Cloud Manager SDK.

Provides service class for managing schedule objects via the SCM API.
"""

# scm/config/objects/schedules.py

# Standard library imports
import logging
from typing import Any, Dict, List, Optional

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.objects import (
    ScheduleCreateModel,
    ScheduleResponseModel,
    ScheduleUpdateModel,
)


class Schedule(BaseObject):
    """Manages Schedule objects in Palo Alto Networks' Strata Cloud Manager.

    Schedules can be configured as recurring (weekly or daily) or non-recurring,
    and are used to specify when policies should be active.

    Args:
        api_client: The API client instance
        max_limit (Optional[int]): Maximum number of objects to return in a single API request.
            Defaults to 200. Must be between 1 and 5000.

    """

    ENDPOINT = "/config/objects/v1/schedules"
    DEFAULT_MAX_LIMIT = 200
    ABSOLUTE_MAX_LIMIT = 5000  # Maximum allowed by the API

    def __init__(
        self,
        api_client,
        max_limit: Optional[int] = None,
    ):
        """Initialize the Schedules service with the given API client."""
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
    ) -> ScheduleResponseModel:
        """Create a new schedule object.

        Args:
            data: Dictionary containing schedule data

        Returns:
            ScheduleResponseModel: The created schedule

        """
        # Use the dictionary "data" to pass into Pydantic and return a modeled object
        schedule = ScheduleCreateModel(**data)

        # Convert back to a Python dictionary, removing any unset fields
        payload = schedule.model_dump(exclude_unset=True)

        # Send the updated object to the remote API as JSON, expecting a dictionary object to be returned.
        response: Dict[str, Any] = self.api_client.post(
            self.ENDPOINT,
            json=payload,
        )

        # Return the SCM API response as a new Pydantic object
        return ScheduleResponseModel(**response)

    def get(
        self,
        object_id: str,
    ) -> ScheduleResponseModel:
        """Get a schedule object by ID.

        Args:
            object_id: The ID of the schedule to get

        Returns:
            ScheduleResponseModel: The requested schedule

        """
        # Send the request to the remote API
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.get(endpoint)

        # Return the SCM API response as a new Pydantic object
        return ScheduleResponseModel(**response)

    def update(
        self,
        schedule: ScheduleUpdateModel,
    ) -> ScheduleResponseModel:
        """Update an existing schedule object.

        Args:
            schedule: ScheduleUpdateModel instance containing the update data

        Returns:
            ScheduleResponseModel: The updated schedule

        """
        # Convert to dict for API request, excluding unset fields
        payload = schedule.model_dump(exclude_unset=True)

        # Extract ID and remove from payload since it's in the URL
        object_id = str(schedule.id)
        payload.pop("id", None)

        # Send the updated object to the remote API as JSON
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.put(
            endpoint,
            json=payload,
        )

        # Return the SCM API response as a new Pydantic object
        return ScheduleResponseModel(**response)

    @staticmethod
    def _apply_filters(
        schedules: List[ScheduleResponseModel],
        filters: Dict[str, Any],
    ) -> List[ScheduleResponseModel]:
        """Apply client-side filtering to the list of schedules.

        Args:
            schedules: List of ScheduleResponseModel objects
            filters: Dictionary of filter criteria

        Returns:
            List[ScheduleResponseModel]: Filtered list of schedules

        """
        filtered_schedules = schedules

        # Filter by schedule_type
        if "schedule_type" in filters:
            schedule_type = filters["schedule_type"]
            if schedule_type not in ["recurring", "non_recurring"]:
                raise InvalidObjectError(
                    message="'schedule_type' filter must be 'recurring' or 'non_recurring'",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Object"},
                )

            filtered_schedules = [
                s
                for s in filtered_schedules
                if hasattr(s.schedule_type, schedule_type)
                and getattr(s.schedule_type, schedule_type) is not None
            ]

        # Filter by recurring_type
        if "recurring_type" in filters:
            recurring_type = filters["recurring_type"]
            if recurring_type not in ["weekly", "daily"]:
                raise InvalidObjectError(
                    message="'recurring_type' filter must be 'weekly' or 'daily'",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Object"},
                )

            filtered_schedules = [
                s
                for s in filtered_schedules
                if hasattr(s.schedule_type, "recurring")
                and s.schedule_type.recurring is not None
                and (
                    (recurring_type == "weekly" and s.schedule_type.recurring.weekly is not None)
                    or (recurring_type == "daily" and s.schedule_type.recurring.daily is not None)
                )
            ]

        return filtered_schedules

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
    ) -> List[ScheduleResponseModel]:
        """List schedule objects with optional filtering.

        Args:
            folder: Optional folder name
            snippet: Optional snippet name
            device: Optional device name
            exact_match (bool): If True, only return objects whose container (folder/snippet/device)
                                exactly matches the provided container parameter.
            exclude_folders (List[str], optional): List of folder names to exclude from results.
            exclude_snippets (List[str], optional): List of snippet values to exclude from results.
            exclude_devices (List[str], optional): List of device values to exclude from results.
            **filters: Additional filters including:
                - schedule_type: str - Filter by schedule type ('recurring' or 'non_recurring')
                - recurring_type: str - Filter by recurring type ('weekly' or 'daily')

        Returns:
            List[ScheduleResponseModel]: A list of schedule objects

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

        if not container_parameters:
            raise InvalidObjectError(
                message="At least one of 'folder', 'snippet', or 'device' must be provided.",
                error_code="E003",
                http_status_code=400,
                details={"error": "Missing container parameters"},
            )

        # Pagination logic using instance max_limit
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
            object_instances = [ScheduleResponseModel(**item) for item in data]
            all_objects.extend(object_instances)

            # If we got fewer than 'limit' objects, we've reached the end
            if len(data) < limit:
                break

            offset += limit

        # Apply custom filters first
        filtered_objects = self._apply_filters(
            all_objects,
            filters,
        )

        # If exact_match is True, filter by exact container match
        if exact_match and container_parameters:
            container_key, container_value = next(iter(container_parameters.items()))
            filtered_objects = [
                obj for obj in filtered_objects if getattr(obj, container_key) == container_value
            ]

        # Exclude folders if provided
        if exclude_folders and isinstance(exclude_folders, list):
            filtered_objects = [
                obj for obj in filtered_objects if obj.folder not in exclude_folders
            ]

        # Exclude snippets if provided
        if exclude_snippets and isinstance(exclude_snippets, list):
            filtered_objects = [
                obj for obj in filtered_objects if obj.snippet not in exclude_snippets
            ]

        # Exclude devices if provided
        if exclude_devices and isinstance(exclude_devices, list):
            filtered_objects = [
                obj for obj in filtered_objects if obj.device not in exclude_devices
            ]

        return filtered_objects

    def fetch(
        self,
        name: str,
        folder: Optional[str] = None,
        snippet: Optional[str] = None,
        device: Optional[str] = None,
    ) -> ScheduleResponseModel:
        """Fetch a single schedule by name.

        Args:
            name: The name of the schedule to fetch
            folder: Optional folder name
            snippet: Optional snippet name
            device: Optional device name

        Returns:
            ScheduleResponseModel: The fetched schedule

        Raises:
            MissingQueryParameterError: If name is empty
            InvalidObjectError: If container parameters are invalid or response format is invalid

        """
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
                details={
                    "field": "folder",
                    "error": '"folder" is not allowed to be empty',
                },
            )

        container_parameters = self._build_container_params(folder, snippet, device)

        if not container_parameters:
            raise InvalidObjectError(
                message="At least one of 'folder', 'snippet', or 'device' must be provided.",
                error_code="E003",
                http_status_code=400,
                details={"error": "Missing container parameters"},
            )

        params = container_parameters.copy()
        params["name"] = name

        response = self.api_client.get(self.ENDPOINT, params=params)

        if not isinstance(response, dict):
            raise InvalidObjectError(
                message="Invalid response format: expected dictionary",
                error_code="E003",
                http_status_code=500,
                details={"error": "Response is not a dictionary"},
            )

        # Single object response for matching name parameter
        if "data" in response and isinstance(response["data"], list):
            if not response["data"]:
                raise InvalidObjectError(
                    message=f"No schedule found with name '{name}'",
                    error_code="E005",
                    http_status_code=404,
                    details={"error": "Object not found"},
                )

            # Return the first match
            return ScheduleResponseModel(**response["data"][0])
        elif "id" in response:
            # Direct object response
            return ScheduleResponseModel(**response)
        else:
            raise InvalidObjectError(
                message="Invalid response format",
                error_code="E003",
                http_status_code=500,
                details={"error": "Response format not recognized"},
            )

    def delete(self, object_id: str) -> None:
        """Delete a schedule object.

        Args:
            object_id: The ID of the schedule to delete

        """
        endpoint = f"{self.ENDPOINT}/{object_id}"
        self.api_client.delete(endpoint)
