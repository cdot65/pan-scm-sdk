"""Service classes for interacting with Folders in Palo Alto Networks' Strata Cloud Manager.

This module provides the Folder class for performing CRUD operations on Folder resources
in the Strata Cloud Manager.
"""

# Standard library imports
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.setup.folder import (
    FolderCreateModel,
    FolderResponseModel,
    FolderUpdateModel,
)


class Folder(BaseObject):
    """Manages Folder objects in Palo Alto Networks' Strata Cloud Manager.

    This class provides methods for creating, retrieving, updating, and deleting Folder resources.

    Attributes:
        ENDPOINT: The API endpoint for Folder resources.
        DEFAULT_MAX_LIMIT: The default maximum number of items to return in a single request.
        ABSOLUTE_MAX_LIMIT: The maximum allowed number of items to return in a single request.

    """

    ENDPOINT = "/config/setup/v1/folders"
    DEFAULT_MAX_LIMIT = 2500
    ABSOLUTE_MAX_LIMIT = 5000  # Maximum allowed by the API

    def __init__(
        self,
        api_client,
        max_limit: int = DEFAULT_MAX_LIMIT,
    ):
        """Initialize the Folder service class.

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
            return self.ABSOLUTE_MAX_LIMIT

        return limit_int

    def create(
        self,
        data: Dict[str, Any],
    ) -> FolderResponseModel:
        """Create a new Folder in the Strata Cloud Manager.

        Args:
            data: Dictionary containing folder data.

        Returns:
            FolderResponseModel: The created folder.

        Raises:
            InvalidObjectError: If the folder data is invalid.
            APIError: If the API request fails.

        """
        # Build and validate request payload
        create_model = FolderCreateModel(**data)

        # Convert back to a Python dictionary, removing any unset fields
        payload = create_model.model_dump(exclude_unset=True)

        # Send the updated object to the remote API as JSON, expecting a dictionary object to be returned.
        response: Dict[str, Any] = self.api_client.post(
            self.ENDPOINT,
            json=payload,
        )

        # Return the SCM API response as a new Pydantic object
        return FolderResponseModel.model_validate(response)

    def get(
        self,
        folder_id: Union[str, UUID],
    ) -> FolderResponseModel:
        """Get a folder by its ID.

        Args:
            folder_id: The ID of the folder to retrieve.

        Returns:
            FolderResponseModel: The requested folder.

        Raises:
            ObjectNotPresentError: If the folder doesn't exist.
            APIError: If the API request fails.

        """
        # Convert UUID to string if necessary
        folder_id_str = str(folder_id)

        # Send the request to the remote API
        try:
            response: Dict[str, Any] = self.api_client.get(f"{self.ENDPOINT}/{folder_id_str}")

            # Return the SCM API response as a new Pydantic object
            return FolderResponseModel.model_validate(response)

        # Handle API errors
        except APIError as e:
            if e.http_status_code == 404:
                raise ObjectNotPresentError(f"Folder with ID {folder_id} not found")
            raise

    @staticmethod
    def _apply_filters(
        data: List["FolderResponseModel"],
        filters: Dict[str, Any],
    ) -> List["FolderResponseModel"]:
        """Apply client-side filters to a list of folders."""
        filtered = data

        if not filters:
            return filtered

        # Filter by labels (intersection: any label matches)
        if "labels" in filters:
            required_labels = set(filters["labels"])
            filtered = [
                f
                for f in filtered
                if getattr(f, "labels", None) and required_labels.intersection(set(f.labels))
            ]

        # Filter by parent (exact match)
        if "parent" in filters:
            parent_val = filters["parent"]
            filtered = [f for f in filtered if getattr(f, "parent", None) == parent_val]

        # Filter by type (exact match)
        if "type" in filters:
            type_val = filters["type"]
            filtered = [f for f in filtered if getattr(f, "type", None) == type_val]

        # Filter by snippets (intersection: any snippet matches)
        if "snippets" in filters:
            required_snippets = set(filters["snippets"])
            filtered = [
                f
                for f in filtered
                if getattr(f, "snippets", None) and required_snippets.intersection(set(f.snippets))
            ]

        # Filter by model (exact match)
        if "model" in filters:
            model_val = filters["model"]
            filtered = [f for f in filtered if getattr(f, "model", None) == model_val]

        # Filter by serial_number (exact match)
        if "serial_number" in filters:
            serial_val = filters["serial_number"]
            filtered = [f for f in filtered if getattr(f, "serial_number", None) == serial_val]

        # Filter by device_only (boolean match)
        if "device_only" in filters:
            device_only_val = filters["device_only"]
            filtered = [f for f in filtered if getattr(f, "device_only", None) == device_only_val]

        return filtered

    def list(
        self,
        **filters: Any,  # Accept arbitrary filters (labels, parent, type, etc.)
    ) -> List[FolderResponseModel]:
        """List folders with optional server-side and client-side filtering.

        Args:
            **filters: Additional filters (labels, parent, type, snippets, etc.).

        Returns:
            List[FolderResponseModel]: A list of folders matching the filters.

        Raises:
            APIError: If the API request fails.
            InvalidObjectError: If filter parameters are invalid.

        """
        # Prepare API parameters for server-side filtering (if supported)
        params: Dict[str, Any] = {}
        if "labels" in filters:
            params["labels"] = ",".join(filters["labels"])
        if "type" in filters:
            params["type"] = filters["type"]
        if "parent" in filters:
            params["parent"] = filters["parent"]

        # Pagination logic
        limit = self.max_limit
        offset = 0
        all_objects = []

        while True:
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

            # Handle single-item response when filters return one object
            if "data" not in response:
                data_items = [response]
            else:
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
                data_items = response["data"]

            object_instances = [FolderResponseModel.model_validate(item) for item in data_items]
            all_objects.extend(object_instances)

            if len(data_items) < limit:
                break
            offset += limit

        # Apply any remaining client-side filters
        filtered_folders = self._apply_filters(
            all_objects,
            {k: v for k, v in filters.items() if k not in ["labels", "type", "parent"]},
        )
        return filtered_folders

    def fetch(
        self,
        name: str,
    ) -> Optional[FolderResponseModel]:
        """Get a folder by its name.

        Args:
            name: The name of the folder to retrieve.

        Returns:
            Optional[FolderResponseModel]: The requested folder (exact name match), or None if not found.

        """
        # Get all folders
        results = self.list()

        if not results:
            return None

        # Filter to exact matches
        exact_matches = [folder for folder in results if folder.name == name]
        if not exact_matches:
            return None
        return exact_matches[0]

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
        # Create a copy of the params to avoid modifying the input
        request_params = params.copy()

        # Add pagination parameters
        request_params["limit"] = limit
        request_params["offset"] = offset

        # Make the API call
        response = self.api_client.get(endpoint, params=request_params)

        # Handle the response
        if isinstance(response, dict) and "data" in response:
            return response["data"]

        # If we got a list directly, return it
        if isinstance(response, list):
            return response

        # Unexpected response format
        return []

    def update(
        self,
        folder: FolderUpdateModel,
    ) -> FolderResponseModel:
        """Update an existing folder.

        Args:
            folder: The FolderUpdateModel containing the updated folder data.

        Returns:
            FolderResponseModel: The updated folder.

        Raises:
            InvalidObjectError: If the update data is invalid.
            ObjectNotPresentError: If the folder doesn't exist.
            APIError: If the API request fails.

        """
        # Convert to dict for API request, excluding unset fields
        payload = folder.model_dump(exclude_unset=True)

        # Extract ID and remove from payload since it's in the URL
        object_id = str(folder.id)
        payload.pop("id", None)

        # Send the updated object to the remote API as JSON
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.put(
            endpoint,
            json=payload,
        )

        # Return the SCM API response as a new Pydantic object
        return FolderResponseModel.model_validate(response)

    def delete(
        self,
        folder_id: Union[str, UUID],
    ) -> None:
        """Delete a folder.

        Args:
            folder_id: The ID of the folder to delete.

        Raises:
            ObjectNotPresentError: If the snippet doesn't exist.
            APIError: If the API request fails.

        """
        try:
            object_id_str = str(folder_id)
            self.api_client.delete(f"{self.ENDPOINT}/{object_id_str}")
        except APIError as e:
            if e.http_status_code == 404:
                raise ObjectNotPresentError(f"Snippet with ID {folder_id} not found")
            raise
