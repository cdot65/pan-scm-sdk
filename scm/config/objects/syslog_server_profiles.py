"""Syslog Server Profiles configuration service for Strata Cloud Manager SDK.

Provides service class for managing syslog server profile objects via the SCM API.
"""

# scm/config/objects/syslog_server_profiles.py

# Standard library imports
import logging
from typing import Any, Dict, List, Optional

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.objects import (
    SyslogServerProfileCreateModel,
    SyslogServerProfileResponseModel,
    SyslogServerProfileUpdateModel,
)


class SyslogServerProfile(BaseObject):
    """Manages Syslog Server Profile objects in Palo Alto Networks' Strata Cloud Manager.

    Args:
        api_client: The API client instance
        max_limit (Optional[int]): Maximum number of objects to return in a single API request.
            Defaults to 2500. Must be between 1 and 5000.

    """

    ENDPOINT = "/config/objects/v1/syslog-server-profiles"
    DEFAULT_MAX_LIMIT = 2500
    ABSOLUTE_MAX_LIMIT = 5000  # Maximum allowed by the API

    def __init__(
        self,
        api_client,
        max_limit: Optional[int] = None,
    ):
        """Initialize the SyslogServerProfiles service with the given API client."""
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
    ) -> SyslogServerProfileResponseModel:
        """Create a new syslog server profile object.

        Args:
            data: Dictionary containing the syslog server profile data

        Returns:
            SyslogServerProfileResponseModel: The created syslog server profile

        """
        # Use the dictionary "data" to pass into Pydantic and return a modeled object
        syslog_server_profile = SyslogServerProfileCreateModel(**data)

        # Convert back to a Python dictionary, removing any unset fields
        payload = syslog_server_profile.model_dump(exclude_unset=True)
        self.logger.debug(f"Sending syslog server profile payload to API: {payload}")

        # Send the updated object to the remote API as JSON, expecting a dictionary object to be returned.
        try:
            response: Dict[str, Any] = self.api_client.post(
                self.ENDPOINT,
                json=payload,
            )
        except Exception as e:
            self.logger.error(f"Error in API call: {str(e)}", exc_info=True)
            raise

        # Return the SCM API response as a new Pydantic object
        return SyslogServerProfileResponseModel(**response)

    def get(
        self,
        object_id: str,
    ) -> SyslogServerProfileResponseModel:
        """Get a syslog server profile object by ID.

        Args:
            object_id: The ID of the syslog server profile to retrieve

        Returns:
            SyslogServerProfileResponseModel: The retrieved syslog server profile

        """
        # Send the request to the remote API
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.get(endpoint)

        # Return the SCM API response as a new Pydantic object
        return SyslogServerProfileResponseModel(**response)

    def update(
        self,
        syslog_server_profile: SyslogServerProfileUpdateModel,
    ) -> SyslogServerProfileResponseModel:
        """Update an existing syslog server profile object.

        Args:
            syslog_server_profile: SyslogServerProfileUpdateModel instance containing the update data

        Returns:
            SyslogServerProfileResponseModel: The updated syslog server profile

        """
        # Convert to dict for API request, excluding unset fields
        payload = syslog_server_profile.model_dump(exclude_unset=True)

        # Extract ID and remove from payload since it's in the URL
        object_id = str(syslog_server_profile.id)
        payload.pop("id", None)

        # Send the updated object to the remote API as JSON
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.put(
            endpoint,
            json=payload,
        )

        # Return the SCM API response as a new Pydantic object
        return SyslogServerProfileResponseModel(**response)

    @staticmethod
    def _apply_filters(
        syslog_server_profiles: List[SyslogServerProfileResponseModel],
        filters: Dict[str, Any],
    ) -> List[SyslogServerProfileResponseModel]:
        """Apply client-side filtering to the list of syslog server profiles.

        Args:
            syslog_server_profiles: List of SyslogServerProfileResponseModel objects
            filters: Dictionary of filter criteria

        Returns:
            List[SyslogServerProfileResponseModel]: Filtered list of syslog server profiles

        """
        filter_criteria = syslog_server_profiles

        # Filter by transport protocol
        if "transport" in filters:
            if not isinstance(filters["transport"], list):
                raise InvalidObjectError(
                    message="'transport' filter must be a list",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Object"},
                )
            transports = filters["transport"]
            # The servers are stored as a dictionary in the model, so we need to check each server's transport
            filter_criteria = [
                profile
                for profile in filter_criteria
                if any(
                    server_data.get("transport") in transports
                    for server_name, server_data in profile.servers.items()
                )
            ]

        # Filter by format type
        if "format" in filters:
            if not isinstance(filters["format"], list):
                raise InvalidObjectError(
                    message="'format' filter must be a list",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Object"},
                )
            formats = filters["format"]
            filter_criteria = [
                profile
                for profile in filter_criteria
                if any(
                    server_data.get("format") in formats
                    for server_name, server_data in profile.servers.items()
                )
            ]

        return filter_criteria

    @staticmethod
    def _build_container_params(
        folder: Optional[str],
        snippet: Optional[str],
        device: Optional[str],
    ) -> dict:
        """Build container parameters dictionary.

        Args:
            folder: Optional folder name
            snippet: Optional snippet name
            device: Optional device name

        Returns:
            dict: Dictionary of non-None container parameters

        """
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
    ) -> List[SyslogServerProfileResponseModel]:
        """List syslog server profile objects with optional filtering.

        Args:
            folder: Optional folder name
            snippet: Optional snippet name
            device: Optional device name
            exact_match (bool): If True, only return objects whose container
                                exactly matches the provided container parameter.
            exclude_folders (List[str], optional): List of folder names to exclude from results.
            exclude_snippets (List[str], optional): List of snippet values to exclude from results.
            exclude_devices (List[str], optional): List of device values to exclude from results.
            **filters: Additional filters including:
                - transport: List[str] - Filter by server transport protocols (e.g., ['UDP', 'TCP'])
                - format: List[str] - Filter by syslog format (e.g., ['BSD', 'IETF'])

        Returns:
            List[SyslogServerProfileResponseModel]: A list of syslog server profile objects

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
            object_instances = [SyslogServerProfileResponseModel(**item) for item in data]
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
    ) -> SyslogServerProfileResponseModel:
        """Fetch a single syslog server profile by name.

        Args:
            name (str): The name of the syslog server profile to fetch.
            folder (str, optional): The folder in which the resource is defined.
            snippet (str, optional): The snippet in which the resource is defined.
            device (str, optional): The device in which the resource is defined.

        Returns:
            SyslogServerProfileResponseModel: The fetched syslog server profile object as a Pydantic model.

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

        if "id" in response:
            return SyslogServerProfileResponseModel(**response)
        else:
            raise InvalidObjectError(
                message="Invalid response format: missing 'id' field",
                error_code="E003",
                http_status_code=500,
                details={"error": "Response missing 'id' field"},
            )

    def delete(
        self,
        object_id: str,
    ) -> None:
        """Delete a syslog server profile object.

        Args:
            object_id (str): The ID of the object to delete.

        """
        endpoint = f"{self.ENDPOINT}/{object_id}"
        self.api_client.delete(endpoint)
