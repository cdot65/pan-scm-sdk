"""Network Locations configuration service for Strata Cloud Manager SDK.

Provides service class for managing network location objects via the SCM API.
"""

# scm/config/deployment/network_locations.py

# Standard library imports
import logging
from typing import Any, Dict, List, Optional

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.deployment import NetworkLocationModel


class NetworkLocations(BaseObject):
    """Manages Network Location objects in Palo Alto Networks' Strata Cloud Manager.

    Args:
        api_client: The API client instance
        max_limit (Optional[int]): Maximum number of objects to return in a single API request.
            Defaults to 200. Must be between 1 and 1000.

    """

    ENDPOINT = "/config/deployment/v1/locations"
    DEFAULT_MAX_LIMIT = 200
    ABSOLUTE_MAX_LIMIT = 1000

    def __init__(
        self,
        api_client,
        max_limit: Optional[int] = None,
    ):
        """Initialize the NetworkLocations service with the given API client."""
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

    @staticmethod
    def _apply_filters(
        locations: List[NetworkLocationModel],
        filters: Dict[str, Any],
    ) -> List[NetworkLocationModel]:
        """Apply client-side filtering to the list of network locations.

        Args:
            locations: List of NetworkLocationModel objects
            filters: Dictionary of filter criteria

        Returns:
            List[NetworkLocationModel]: Filtered list of network locations

        """
        filtered_locations = locations

        # Filter by value
        if "value" in filters:
            value_filter = filters["value"]
            if isinstance(value_filter, list):
                # If the list is empty, no results should be returned
                if not value_filter:
                    return []
                filtered_locations = [
                    loc
                    for loc in filtered_locations
                    if loc.value.lower() in [v.lower() for v in value_filter]
                ]
            else:
                filtered_locations = [
                    loc for loc in filtered_locations if loc.value.lower() == value_filter.lower()
                ]

        # Filter by display
        if "display" in filters:
            display_filter = filters["display"]
            if isinstance(display_filter, list):
                # If the list is empty, no results should be returned
                if not display_filter:
                    return []
                filtered_locations = [
                    loc
                    for loc in filtered_locations
                    if loc.display.lower() in [d.lower() for d in display_filter]
                ]
            else:
                filtered_locations = [
                    loc
                    for loc in filtered_locations
                    if loc.display.lower() == display_filter.lower()
                ]

        # Filter by region
        if "region" in filters:
            region_filter = filters["region"]
            if isinstance(region_filter, list):
                # If the list is empty, no results should be returned
                if not region_filter:
                    return []
                filtered_locations = [
                    loc
                    for loc in filtered_locations
                    if loc.region and loc.region.lower() in [r.lower() for r in region_filter]
                ]
            else:
                filtered_locations = [
                    loc
                    for loc in filtered_locations
                    if loc.region and loc.region.lower() == region_filter.lower()
                ]

        # Filter by continent
        if "continent" in filters:
            continent_filter = filters["continent"]
            if isinstance(continent_filter, list):
                # If the list is empty, no results should be returned
                if not continent_filter:
                    return []
                filtered_locations = [
                    loc
                    for loc in filtered_locations
                    if loc.continent
                    and loc.continent.lower() in [c.lower() for c in continent_filter]
                ]
            else:
                filtered_locations = [
                    loc
                    for loc in filtered_locations
                    if loc.continent and loc.continent.lower() == continent_filter.lower()
                ]

        # Filter by aggregate_region
        if "aggregate_region" in filters:
            agg_region_filter = filters["aggregate_region"]
            if isinstance(agg_region_filter, list):
                # If the list is empty, no results should be returned
                if not agg_region_filter:
                    return []
                filtered_locations = [
                    loc
                    for loc in filtered_locations
                    if loc.aggregate_region
                    and loc.aggregate_region.lower() in [ar.lower() for ar in agg_region_filter]
                ]
            else:
                filtered_locations = [
                    loc
                    for loc in filtered_locations
                    if loc.aggregate_region
                    and loc.aggregate_region.lower() == agg_region_filter.lower()
                ]

        return filtered_locations

    def list(
        self,
        **filters,
    ) -> List[NetworkLocationModel]:
        """List network location objects with optional filtering.

        Args:
            **filters: Additional filters including:
                - value: str or List[str] - Filter by location value
                - display: str or List[str] - Filter by display name
                - region: str or List[str] - Filter by region
                - continent: str or List[str] - Filter by continent
                - aggregate_region: str or List[str] - Filter by aggregate region

        Returns:
            List[NetworkLocationModel]: A list of network location objects

        """
        # For network locations, the API returns a direct list rather than a paginated response
        # So we don't need to implement pagination here
        response = self.api_client.get(
            self.ENDPOINT,
        )

        # Verify the response is a list
        if not isinstance(response, list):
            raise InvalidObjectError(
                message="Invalid response format: expected list",
                error_code="E003",
                http_status_code=500,
                details={"error": "Response is not a list"},
            )

        # Convert each item to a NetworkLocationModel
        all_objects = [NetworkLocationModel(**item) for item in response]

        # Apply filters
        filtered_objects = self._apply_filters(
            all_objects,
            filters,
        )

        return filtered_objects

    def fetch(
        self,
        value: str,
    ) -> NetworkLocationModel:
        """Fetch a single network location by its value.

        Args:
            value: The system value of the network location to fetch

        Returns:
            NetworkLocationModel: The fetched network location object

        Raises:
            InvalidObjectError: If the network location is not found

        """
        if not value:
            raise MissingQueryParameterError(
                message="Field 'value' cannot be empty",
                error_code="E003",
                http_status_code=400,
                details={
                    "field": "value",
                    "error": '"value" is not allowed to be empty',
                },
            )

        # Get all network locations
        all_locations = self.list()

        # Find the location with the matching value (case-insensitive)
        matching_locations = [loc for loc in all_locations if loc.value.lower() == value.lower()]

        if not matching_locations:
            raise InvalidObjectError(
                message=f"Network location with value '{value}' not found",
                error_code="E005",
                http_status_code=404,
                details={"error": "Object not found"},
            )

        if len(matching_locations) > 1:
            self.logger.warning(
                f"Multiple network locations found with value '{value}'. Using the first one."
            )

        return matching_locations[0]
