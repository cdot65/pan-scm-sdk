"""Service classes for interacting with Resources in Palo Alto Networks' Strata Cloud Manager.

This module provides the Resource class for performing CRUD operations on Resource
objects in the Strata Cloud Manager.

Usage:
    1. Copy this file to scm/config/{category}/resource.py
    2. Replace all occurrences of "Resource" with your resource name (e.g., "Address")
    3. Replace all occurrences of "resource" with lowercase name (e.g., "address")
    4. Update ENDPOINT to match the API path
    5. Update model imports to match your models
    6. Implement any resource-specific filtering in _apply_filters()
    7. Create corresponding models in scm/models/{category}/resource.py
"""

# Standard library imports
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError

# TODO: Update these imports to match your models
from scm.models.category.resource import (
    ResourceCreateModel,
    ResourceResponseModel,
    ResourceUpdateModel,
)


class Resource(BaseObject):
    """Manages Resource objects in Palo Alto Networks' Strata Cloud Manager.

    This class provides methods for creating, retrieving, updating, and deleting
    Resource objects.

    Attributes:
        ENDPOINT: The API endpoint for Resource resources.
        DEFAULT_MAX_LIMIT: The default maximum number of items per request.
        ABSOLUTE_MAX_LIMIT: The maximum allowed items per request.

    """

    # TODO: Update endpoint to match your resource
    ENDPOINT = "/config/category/v1/resources"
    DEFAULT_MAX_LIMIT = 2500
    ABSOLUTE_MAX_LIMIT = 5000  # Maximum allowed by the API

    def __init__(
        self,
        api_client,
        max_limit: int = DEFAULT_MAX_LIMIT,
    ):
        """Initialize the Resource service class.

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
            limit: The limit to validate.

        Returns:
            int: The validated limit.

        Raises:
            InvalidObjectError: If the limit is invalid.

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

    def create(
        self,
        data: Dict[str, Any],
    ) -> ResourceResponseModel:
        """Create a new resource in the Strata Cloud Manager.

        Args:
            data: Dictionary containing resource data.

        Returns:
            ResourceResponseModel: The created resource.

        Raises:
            InvalidObjectError: If the resource data is invalid.
            APIError: If the API request fails.

        """
        create_model = ResourceCreateModel(**data)
        payload = create_model.model_dump(exclude_unset=True)
        response = self.api_client.post(self.ENDPOINT, json=payload)
        return ResourceResponseModel.model_validate(response)

    def get(
        self,
        object_id: Union[str, UUID],
    ) -> ResourceResponseModel:
        """Get a resource by its ID.

        Args:
            object_id: The ID of the resource to retrieve.

        Returns:
            ResourceResponseModel: The requested resource.

        Raises:
            ObjectNotPresentError: If the resource doesn't exist.
            APIError: If the API request fails.

        """
        object_id_str = str(object_id)
        try:
            response = self.api_client.get(f"{self.ENDPOINT}/{object_id_str}")
            return ResourceResponseModel.model_validate(response)
        except APIError as e:
            if e.http_status_code == 404:
                raise ObjectNotPresentError(f"Resource with ID {object_id} not found")
            raise

    def update(
        self,
        resource: ResourceUpdateModel,
    ) -> ResourceResponseModel:
        """Update an existing resource.

        Args:
            resource: The ResourceUpdateModel containing the updated data.

        Returns:
            ResourceResponseModel: The updated resource.

        Raises:
            InvalidObjectError: If the update data is invalid.
            ObjectNotPresentError: If the resource doesn't exist.
            APIError: If the API request fails.

        """
        payload = resource.model_dump(exclude_unset=True)
        object_id = str(resource.id)
        payload.pop("id", None)
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response = self.api_client.put(endpoint, json=payload)
        return ResourceResponseModel.model_validate(response)

    def delete(
        self,
        object_id: Union[str, UUID],
    ) -> None:
        """Delete a resource.

        Args:
            object_id: The ID of the resource to delete.

        Raises:
            ObjectNotPresentError: If the resource doesn't exist.
            APIError: If the API request fails.

        """
        try:
            object_id_str = str(object_id)
            self.api_client.delete(f"{self.ENDPOINT}/{object_id_str}")
        except APIError as e:
            if e.http_status_code == 404:
                raise ObjectNotPresentError(f"Resource with ID {object_id} not found")
            raise

    def list(
        self,
        **filters: Any,
    ) -> List[ResourceResponseModel]:
        """List resources with optional filters.

        Args:
            **filters: Additional filters for the API.
                Common filters include:
                - folder (str): Filter by folder name (server-side)
                - labels (List[str]): Filter by labels (client-side)
                - type (str): Filter by type (client-side)

        Returns:
            List[ResourceResponseModel]: A list of resources matching the filters.

        Raises:
            APIError: If the API request fails.

        """
        params: Dict[str, Any] = {}
        limit = self.max_limit
        offset = 0
        all_objects: List[ResourceResponseModel] = []

        # TODO: Add server-side filter handling here
        # Example:
        # if "folder" in filters:
        #     params["folder"] = filters["folder"]

        while True:
            params.update({"limit": limit, "offset": offset})
            params.update({k: v for k, v in filters.items() if v is not None})
            response = self.api_client.get(self.ENDPOINT, params=params)
            data_items = response["data"] if "data" in response else response
            object_instances = [
                ResourceResponseModel.model_validate(item) for item in data_items
            ]
            all_objects.extend(object_instances)

            if len(data_items) < limit:
                break
            offset += limit

        # Apply client-side filters
        # TODO: Customize filters based on your resource
        filtered_results = self._apply_filters(
            all_objects,
            {k: v for k, v in filters.items() if k not in ["folder"]},
        )

        return filtered_results

    def fetch(
        self,
        name: str,
        folder: str,
    ) -> Optional[ResourceResponseModel]:
        """Get a resource by its name and folder.

        Args:
            name: The name of the resource to retrieve.
            folder: The folder in which the resource is defined.

        Returns:
            Optional[ResourceResponseModel]: The requested resource, or None if not found.

        Raises:
            InvalidObjectError: If name or folder is empty.

        """
        if not name:
            raise InvalidObjectError(
                message="Field 'name' cannot be empty",
                error_code="E003",
                http_status_code=400,
                details={
                    "field": "name",
                    "error": '"name" is not allowed to be empty',
                },
            )

        if not folder:
            raise InvalidObjectError(
                message="Field 'folder' cannot be empty",
                error_code="E003",
                http_status_code=400,
                details={
                    "field": "folder",
                    "error": '"folder" is not allowed to be empty',
                },
            )

        results = self.list(folder=folder)

        if not results:
            return None

        exact_matches = [r for r in results if r.name == name]
        return exact_matches[0] if exact_matches else None

    @staticmethod
    def _apply_filters(
        data: List["ResourceResponseModel"],
        filters: Dict[str, Any],
    ) -> List["ResourceResponseModel"]:
        """Apply client-side filters to a list of resources.

        Args:
            data: The list of resources to filter.
            filters: Dictionary of filter criteria.

        Returns:
            List[ResourceResponseModel]: Filtered list of resources.

        """
        filtered = data

        if not filters:
            return filtered

        # TODO: Implement resource-specific filters
        # Example filters:

        # Filter by labels (intersection: any label matches)
        if "labels" in filters:
            required_labels = set(filters["labels"])
            filtered = [
                f
                for f in filtered
                if getattr(f, "labels", None)
                and required_labels.intersection(set(f.labels))
            ]

        # Filter by type (exact match)
        if "type" in filters:
            type_val = filters["type"]
            filtered = [f for f in filtered if getattr(f, "type", None) == type_val]

        # Filter by parent (exact match)
        if "parent" in filters:
            parent_val = filters["parent"]
            filtered = [f for f in filtered if getattr(f, "parent", None) == parent_val]

        return filtered

    def _get_paginated_results(
        self,
        endpoint: str,
        params: Dict[str, Any],
        limit: int,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Get paginated results from an API endpoint.

        Args:
            endpoint: The API endpoint URL.
            params: Query parameters for the request.
            limit: Maximum number of items to return.
            offset: Starting position for pagination.

        Returns:
            List[Dict[str, Any]]: List of result items.

        Raises:
            APIError: If the API request fails.

        """
        request_params = params.copy()
        request_params["limit"] = limit
        request_params["offset"] = offset

        response = self.api_client.get(endpoint, params=request_params)

        if isinstance(response, dict) and "data" in response:
            return response["data"]

        if isinstance(response, list):
            return response

        return []
