"""Region configuration service for Strata Cloud Manager SDK.

Provides service class for managing region objects via the SCM API.
"""

# scm/config/objects/region.py

# Standard library imports
import logging
from typing import Any, Dict, List, Optional

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.objects import RegionCreateModel, RegionResponseModel, RegionUpdateModel


class Region(BaseObject):
    """Manages Region objects in Palo Alto Networks' Strata Cloud Manager.

    Note:
        While the SDK models support 'description' and 'tag' fields for region objects
        to maintain consistency with other object types, these fields are not supported
        by the Strata Cloud Manager API. They will be automatically excluded when
        sending requests to the API.

    Args:
        api_client: The API client instance
        max_limit (Optional[int]): Maximum number of objects to return in a single API request.
            Defaults to 5000. Must be between 1 and 10000.

    """

    ENDPOINT = "/config/objects/v1/regions"
    DEFAULT_MAX_LIMIT = 2500
    ABSOLUTE_MAX_LIMIT = 5000  # Maximum allowed by the API

    def __init__(
        self,
        api_client,
        max_limit: Optional[int] = None,
    ):
        """Initialize the Region service with the given API client."""
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
    ) -> RegionResponseModel:
        """Create a new region object.

        Returns:
            RegionResponseModel

        """
        # Use the dictionary "data" to pass into Pydantic and return a modeled object
        region = RegionCreateModel(**data)

        # Convert back to a Python dictionary, removing any unset fields
        # Also exclude tag and description fields since they're not supported by the API
        payload = region.model_dump(exclude_unset=True, exclude={"tag", "description"})

        # Send the updated object to the remote API as JSON, expecting a dictionary object to be returned.
        response: Dict[str, Any] = self.api_client.post(
            self.ENDPOINT,
            json=payload,
        )

        # Return the SCM API response as a new Pydantic object
        return RegionResponseModel(**response)

    def get(
        self,
        object_id: str,
    ) -> RegionResponseModel:
        """Get a region object by ID.

        Returns:
            RegionResponseModel

        """
        # Send the request to the remote API
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.get(endpoint)

        # Return the SCM API response as a new Pydantic object
        return RegionResponseModel(**response)

    def update(
        self,
        region: RegionUpdateModel,
    ) -> RegionResponseModel:
        """Update an existing region object.

        Args:
            region: RegionUpdateModel instance containing the update data

        Returns:
            RegionResponseModel

        """
        # Convert to dict for API request, excluding unset fields
        # Also exclude tag and description fields since they're not supported by the API
        payload = region.model_dump(exclude_unset=True, exclude={"tag", "description"})

        # Extract ID and remove from payload since it's in the URL
        object_id = str(region.id)
        payload.pop("id", None)

        # Send the updated object to the remote API as JSON
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.put(
            endpoint,
            json=payload,
        )

        # Return the SCM API response as a new Pydantic object
        return RegionResponseModel(**response)

    @staticmethod
    def _apply_filters(
        regions: List[RegionResponseModel],
        filters: Dict[str, Any],
    ) -> List[RegionResponseModel]:
        """Apply client-side filtering to the list of regions.

        Args:
            regions: List of RegionResponseModel objects
            filters: Dictionary of filter criteria

        Returns:
            List[RegionResponseModel]: Filtered list of regions

        """
        filter_criteria = regions

        # Filter by geo_location (latitude/longitude ranges)
        if "geo_location" in filters:
            if not isinstance(filters["geo_location"], dict):
                raise InvalidObjectError(
                    message="'geo_location' filter must be a dictionary",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Object"},
                )

            geo_filter = filters["geo_location"]

            # Filter by latitude range if specified
            if "latitude" in geo_filter:
                lat_range = geo_filter["latitude"]
                if isinstance(lat_range, dict) and "min" in lat_range and "max" in lat_range:
                    filter_criteria = [
                        region
                        for region in filter_criteria
                        if region.geo_location
                        and region.geo_location.latitude >= lat_range["min"]
                        and region.geo_location.latitude <= lat_range["max"]
                    ]

            # Filter by longitude range if specified
            if "longitude" in geo_filter:
                long_range = geo_filter["longitude"]
                if isinstance(long_range, dict) and "min" in long_range and "max" in long_range:
                    filter_criteria = [
                        region
                        for region in filter_criteria
                        if region.geo_location
                        and region.geo_location.longitude >= long_range["min"]
                        and region.geo_location.longitude <= long_range["max"]
                    ]

        # Filter by addresses
        if "addresses" in filters:
            if not isinstance(filters["addresses"], list):
                raise InvalidObjectError(
                    message="'addresses' filter must be a list",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Object"},
                )
            addresses = filters["addresses"]
            filter_criteria = [
                region
                for region in filter_criteria
                if region.address and any(addr in region.address for addr in addresses)
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
    ) -> List[RegionResponseModel]:
        """List region objects with optional filtering.

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
                - geo_location: Dict with latitude/longitude range filters
                - addresses: List[str] - Filter by addresses (e.g., ['10.0.0.0/24'])

        Returns:
            List[RegionResponseModel]: A list of region objects

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
            # Filter out any items without valid ID - likely predefined or system regions
            invalid_data = [item for item in data if not isinstance(item, dict) or "id" not in item]
            if invalid_data:
                self.logger.debug(f"Filtering out {len(invalid_data)} items without valid ID field")
                for idx, item in enumerate(invalid_data[:3]):  # Log up to 3 examples
                    self.logger.debug(f"Invalid item {idx}: {item}")
                if len(invalid_data) > 3:
                    self.logger.debug(f"... and {len(invalid_data) - 3} more")

            # Accept all items (with or without 'id')
            object_instances = [
                RegionResponseModel(**item) for item in data if isinstance(item, dict)
            ]
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
    ) -> RegionResponseModel:
        """Fetch a single region by name.

        Args:
            name (str): The name of the region to fetch.
            folder (str, optional): The folder in which the resource is defined.
            snippet (str, optional): The snippet in which the resource is defined.
            device (str, optional): The device in which the resource is defined.

        Returns:
            RegionResponseModel: The fetched region object as a Pydantic model.

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

        # Allow predefined regions (no 'id') to be returned as well
        return RegionResponseModel(**response)

    def delete(
        self,
        object_id: str,
    ) -> None:
        """Delete a region object.

        Args:
            object_id (str): The ID of the object to delete.

        """
        endpoint = f"{self.ENDPOINT}/{object_id}"
        self.api_client.delete(endpoint)
