"""Bandwidth Allocations configuration service for Strata Cloud Manager SDK.

Provides service class for managing bandwidth allocation objects via the SCM API.
"""

# scm/config/deployment/bandwidth_allocations.py

# Standard library imports
import logging
from typing import Any, Dict, List, Optional

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.deployment import (
    BandwidthAllocationCreateModel,
    BandwidthAllocationListResponseModel,
    BandwidthAllocationResponseModel,
    BandwidthAllocationUpdateModel,
)


class BandwidthAllocations(BaseObject):
    """Manages Bandwidth Allocation objects in Palo Alto Networks' Strata Cloud Manager.

    Args:
        api_client: The API client instance
        max_limit (Optional[int]): Maximum number of objects to return in a single API request.
            Defaults to 200. Must be between 1 and 1000.

    """

    ENDPOINT = "/config/deployment/v1/bandwidth-allocations"
    DEFAULT_MAX_LIMIT = 200  # Default value from the OpenAPI spec
    ABSOLUTE_MAX_LIMIT = 1000  # Set a reasonable limit

    def __init__(
        self,
        api_client,
        max_limit: Optional[int] = None,
    ):
        """Initialize the BandwidthAllocations service with the given API client."""
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
    ) -> BandwidthAllocationResponseModel:
        """Create a new Bandwidth Allocation object.

        Args:
            data: Dictionary containing the bandwidth allocation configuration

        Returns:
            BandwidthAllocationResponseModel

        """
        # Use the dictionary "data" to pass into Pydantic and return a modeled object
        bandwidth_allocation = BandwidthAllocationCreateModel(**data)

        # Convert back to a Python dictionary, removing any unset fields
        payload = bandwidth_allocation.model_dump(exclude_unset=True)

        # Send the object to the remote API as JSON
        response: Dict[str, Any] = self.api_client.post(
            self.ENDPOINT,
            json=payload,
        )

        # Return the API response as a new Pydantic object
        return BandwidthAllocationResponseModel(**response)

    def update(
        self,
        data: Dict[str, Any],
    ) -> BandwidthAllocationResponseModel:
        """Update an existing Bandwidth Allocation object.

        Args:
            data: Dictionary containing the bandwidth allocation configuration

        Returns:
            BandwidthAllocationResponseModel

        """
        # Use the dictionary "data" to pass into Pydantic and return a modeled object
        bandwidth_allocation = BandwidthAllocationUpdateModel(**data)

        # Convert back to a Python dictionary, removing any unset fields
        payload = bandwidth_allocation.model_dump(exclude_unset=True)

        # Send the updated object to the remote API as JSON
        response: Dict[str, Any] = self.api_client.put(
            self.ENDPOINT,
            json=payload,
        )

        # Return the API response as a new Pydantic object
        return BandwidthAllocationResponseModel(**response)

    def delete(
        self,
        name: str,
        spn_name_list: str,
    ) -> None:
        """Delete a bandwidth allocation.

        Args:
            name: Name of the aggregated bandwidth region
            spn_name_list: Comma-separated list of SPN names in the region

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

        if not spn_name_list:
            raise MissingQueryParameterError(
                message="Field 'spn_name_list' cannot be empty",
                error_code="E003",
                http_status_code=400,
                details={
                    "field": "spn_name_list",
                    "error": '"spn_name_list" is not allowed to be empty',
                },
            )

        # Validate spn_name_list format
        spn_names = [spn.strip() for spn in spn_name_list.split(",")]
        if not all(spn_names):
            raise InvalidObjectError(
                message="Invalid 'spn_name_list' format",
                error_code="E003",
                http_status_code=400,
                details={
                    "field": "spn_name_list",
                    "error": "spn_name_list must be a non-empty, comma-separated list of SPN names",
                },
            )

        params = {
            "name": name,
            "spn_name_list": spn_name_list,
        }

        self.api_client.delete(
            self.ENDPOINT,
            params=params,
        )

    @staticmethod
    def _apply_filters(
        allocations: List[BandwidthAllocationResponseModel],
        filters: Dict[str, Any],
    ) -> List[BandwidthAllocationResponseModel]:
        """Apply client-side filtering to the list of bandwidth allocations.

        Args:
            allocations: List of BandwidthAllocationResponseModel objects
            filters: Dictionary of filter criteria

        Returns:
            List[BandwidthAllocationResponseModel]: Filtered list of bandwidth allocations

        """
        filtered_allocations = allocations

        # Filter by name
        if "name" in filters:
            name_filter = filters["name"]
            if isinstance(name_filter, list):
                # If the list is empty, no results should be returned
                if not name_filter:
                    return []
                filtered_allocations = [
                    alloc
                    for alloc in filtered_allocations
                    if alloc.name.lower() in [n.lower() for n in name_filter]
                ]
            else:
                filtered_allocations = [
                    alloc
                    for alloc in filtered_allocations
                    if alloc.name.lower() == name_filter.lower()
                ]

        # Filter by allocated_bandwidth
        if "allocated_bandwidth" in filters:
            bw_filter = filters["allocated_bandwidth"]
            if isinstance(bw_filter, list):
                # If the list is empty, no results should be returned
                if not bw_filter:
                    return []
                filtered_allocations = [
                    alloc
                    for alloc in filtered_allocations
                    if alloc.allocated_bandwidth in bw_filter
                ]
            else:
                filtered_allocations = [
                    alloc
                    for alloc in filtered_allocations
                    if alloc.allocated_bandwidth == bw_filter
                ]

        # Filter by spn_name_list
        if "spn_name_list" in filters:
            spn_filter = filters["spn_name_list"]
            if isinstance(spn_filter, list):
                # If the list is empty, no results should be returned
                if not spn_filter:
                    return []

                # Check if any of the SPN names in the filter match any in the allocation's list
                filtered_allocations = [
                    alloc
                    for alloc in filtered_allocations
                    if alloc.spn_name_list and any(spn in alloc.spn_name_list for spn in spn_filter)
                ]
            else:
                # Single string => check if it's in the allocation's spn_name_list
                filtered_allocations = [
                    alloc
                    for alloc in filtered_allocations
                    if alloc.spn_name_list and spn_filter in alloc.spn_name_list
                ]

        # Filter by QoS enabled status
        if "qos_enabled" in filters:
            qos_enabled = filters["qos_enabled"]
            if not isinstance(qos_enabled, bool):
                raise InvalidObjectError(
                    message="'qos_enabled' filter must be a boolean",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Object"},
                )

            filtered_allocations = [
                alloc
                for alloc in filtered_allocations
                if alloc.qos and alloc.qos.enabled == qos_enabled
            ]

        return filtered_allocations

    def list(
        self,
        **filters,
    ) -> List[BandwidthAllocationResponseModel]:
        """List bandwidth allocation objects with optional filtering.

        Args:
            **filters: Additional filters including:
                - name: str or List[str] - Filter by region name
                - allocated_bandwidth: float or List[float] - Filter by allocated bandwidth
                - spn_name_list: str or List[str] - Filter by SPN names
                - qos_enabled: bool - Filter by QoS enabled status

        Returns:
            List[BandwidthAllocationResponseModel]: A list of bandwidth allocation objects

        """
        # Pagination logic
        limit = self._max_limit
        offset = 0
        all_objects = []

        while True:
            params = {
                "limit": limit,
                "offset": offset,
            }

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

            # Parse the response into a list response model
            list_response = BandwidthAllocationListResponseModel(**response)

            all_objects.extend(list_response.data)

            # If we got fewer than 'limit' objects, we've reached the end
            if len(list_response.data) < limit:
                break

            offset += limit

        # Apply filters
        filtered_objects = self._apply_filters(
            all_objects,
            filters,
        )

        return filtered_objects

    def get(
        self,
        name: str,
    ) -> Optional[BandwidthAllocationResponseModel]:
        """Get a bandwidth allocation by name.

        Args:
            name: The name of the bandwidth allocation to retrieve

        Returns:
            Optional[BandwidthAllocationResponseModel]: The bandwidth allocation or None if not found

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

        params = {
            "name": name,
        }

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

        if "data" in response and isinstance(response["data"], list):
            data = response["data"]
            if data:
                # Return the first matching allocation
                return BandwidthAllocationResponseModel(**data[0])

        return None

    def fetch(
        self,
        name: str,
    ) -> BandwidthAllocationResponseModel:
        """Fetch a single bandwidth allocation by name.

        Args:
            name: The name of the bandwidth allocation to fetch

        Returns:
            BandwidthAllocationResponseModel: The fetched bandwidth allocation object

        Raises:
            InvalidObjectError: If the allocation is not found

        """
        allocation = self.get(name)

        if allocation is None:
            raise InvalidObjectError(
                message=f"Bandwidth allocation with name '{name}' not found",
                error_code="E005",
                http_status_code=404,
                details={"error": "Object not found"},
            )

        return allocation
