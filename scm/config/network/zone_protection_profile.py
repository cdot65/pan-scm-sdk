"""Zone Protection Profile configuration service for Strata Cloud Manager SDK.

Provides service class for managing zone protection profile objects via the SCM API.
"""

# scm/config/network/zone_protection_profile.py

# Standard library imports
import logging
from typing import Any, Dict, List, Optional

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.network import (
    ZoneProtectionProfileCreateModel,
    ZoneProtectionProfileResponseModel,
    ZoneProtectionProfileUpdateModel,
)


class ZoneProtectionProfile(BaseObject):
    """Manages Zone Protection Profile objects in Palo Alto Networks' Strata Cloud Manager.

    Args:
        api_client: The API client instance
        max_limit (Optional[int]): Maximum number of objects to return in a single API request.
            Defaults to 2500. Must be between 1 and 5000.

    """

    ENDPOINT = "/config/network/v1/zone-protection-profiles"
    DEFAULT_MAX_LIMIT = 2500
    ABSOLUTE_MAX_LIMIT = 5000  # Maximum allowed by the API

    def __init__(
        self,
        api_client,
        max_limit: Optional[int] = None,
    ):
        """Initialize the ZoneProtectionProfile service with the given API client."""
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
    ) -> ZoneProtectionProfileResponseModel:
        """Create a new zone protection profile object.

        Args:
            data: Dictionary containing the zone protection profile configuration

        Returns:
            ZoneProtectionProfileResponseModel

        """
        # Use the dictionary "data" to pass into Pydantic and return a modeled object
        profile = ZoneProtectionProfileCreateModel(**data)

        # Convert back to a Python dictionary, removing any unset fields and using aliases
        payload = profile.model_dump(
            exclude_unset=True,
            by_alias=True,
        )

        # Send the updated object to the remote API as JSON
        response: Dict[str, Any] = self.api_client.post(
            self.ENDPOINT,
            json=payload,
        )

        # Return the API response as a new Pydantic object
        return ZoneProtectionProfileResponseModel(**response)

    def get(
        self,
        object_id: str,
    ) -> ZoneProtectionProfileResponseModel:
        """Get a zone protection profile object by ID.

        Args:
            object_id: The ID of the zone protection profile to retrieve

        Returns:
            ZoneProtectionProfileResponseModel

        """
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.get(endpoint)
        return ZoneProtectionProfileResponseModel(**response)

    def update(
        self,
        profile: ZoneProtectionProfileUpdateModel,
    ) -> ZoneProtectionProfileResponseModel:
        """Update an existing zone protection profile object.

        Args:
            profile: ZoneProtectionProfileUpdateModel instance containing the update data

        Returns:
            ZoneProtectionProfileResponseModel

        """
        # Convert to dict for API request, excluding unset fields and using aliases
        payload = profile.model_dump(
            exclude_unset=True,
            by_alias=True,
        )

        # Extract ID and remove from payload since it's in the URL
        object_id = str(profile.id)
        payload.pop("id", None)

        # Send the updated object to the remote API as JSON
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.put(
            endpoint,
            json=payload,
        )

        # Return the API response as a new Pydantic model
        return ZoneProtectionProfileResponseModel(**response)

    @staticmethod
    def _apply_filters(
        profiles: List[ZoneProtectionProfileResponseModel],
        filters: Dict[str, Any],
    ) -> List[ZoneProtectionProfileResponseModel]:
        """Apply client-side filtering to the list of zone protection profiles.

        Args:
            profiles: List of ZoneProtectionProfileResponseModel objects
            filters: Dictionary of filter criteria

        Returns:
            List[ZoneProtectionProfileResponseModel]: Filtered list of zone protection profiles

        """
        filter_criteria = profiles

        # Filter by description
        if "description" in filters:
            if not isinstance(filters["description"], str):
                raise InvalidObjectError(
                    message="'description' filter must be a string",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Object"},
                )
            description_filter = filters["description"]
            filter_criteria = [
                profile
                for profile in filter_criteria
                if profile.description and description_filter in profile.description
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
    ) -> List[ZoneProtectionProfileResponseModel]:
        """List zone protection profile objects with optional filtering.

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
                - description: str - Filter by description string match

        Returns:
            List[ZoneProtectionProfileResponseModel]: A list of zone protection profile objects

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
            object_instances = [ZoneProtectionProfileResponseModel(**item) for item in data]
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
    ) -> ZoneProtectionProfileResponseModel:
        """Fetch a single zone protection profile by name.

        Args:
            name: The name of the zone protection profile to fetch
            folder: The folder in which the resource is defined
            snippet: The snippet in which the resource is defined
            device: The device in which the resource is defined

        Returns:
            ZoneProtectionProfileResponseModel: The fetched zone protection profile object

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

        if not isinstance(response, dict):
            raise InvalidObjectError(
                message="Invalid response format: expected dictionary",
                error_code="E003",
                http_status_code=500,
                details={"error": "Response is not a dictionary"},
            )

        # Handle the expected format (direct object with 'id' field)
        if "id" in response:
            return ZoneProtectionProfileResponseModel(**response)
        # Handle the alternate format (like list() with 'data' array)
        elif "data" in response and isinstance(response["data"], list):
            if not response["data"]:
                raise InvalidObjectError(
                    message=f"Zone protection profile '{name}' not found",
                    error_code="E002",
                    http_status_code=404,
                    details={"error": "No matching zone protection profile found"},
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
                    f"Multiple zone protection profiles found for '{name}'. Using the first one."
                )
            # Return the first item in the data array
            return ZoneProtectionProfileResponseModel(**response["data"][0])
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
        """Delete a zone protection profile object.

        Args:
            object_id: The ID of the object to delete

        """
        endpoint = f"{self.ENDPOINT}/{object_id}"
        self.api_client.delete(endpoint)
