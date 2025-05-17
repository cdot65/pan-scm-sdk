"""Service classes for interacting with Snippets in Palo Alto Networks' Strata Cloud Manager.

This module provides the Snippet class for performing CRUD operations on Snippet resources
in the Strata Cloud Manager.
"""

# Standard library imports
import logging
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.setup.snippet import (
    SnippetCreateModel,
    SnippetResponseModel,
    SnippetUpdateModel,
)


class Snippet(BaseObject):
    """Manages Snippet objects in Palo Alto Networks' Strata Cloud Manager.

    This class provides methods for creating, retrieving, updating, and deleting Snippet resources.

    Attributes:
        ENDPOINT: The API endpoint for Snippet resources.
        DEFAULT_MAX_LIMIT: The default maximum number of items to return in a single request.
        ABSOLUTE_MAX_LIMIT: The maximum allowed number of items to return in a single request.

    """

    ENDPOINT = "/config/setup/v1/snippets"
    DEFAULT_MAX_LIMIT = 2500
    ABSOLUTE_MAX_LIMIT = 5000  # Maximum allowed by the API

    def __init__(
        self,
        api_client,
        max_limit: Optional[int] = DEFAULT_MAX_LIMIT,
    ):
        """Initialize the Snippet service class.

        Args:
            api_client: The API client instance for making HTTP requests.
            max_limit: Maximum number of items to return in a single request.
                      Defaults to DEFAULT_MAX_LIMIT.

        """
        super().__init__(api_client)
        self.logger = logging.getLogger(__name__)

        # Validate and set max_limit
        self._max_limit = self._validate_max_limit(max_limit)

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
    ) -> SnippetResponseModel:
        """Create a new snippet object in Strata Cloud Manager.

        Args:
            data: Dictionary containing snippet data.

        Returns:
            SnippetResponseModel: The created snippet.

        Raises:
            InvalidObjectError: If the snippet data is invalid.
            APIError: If the API request fails.

        """
        # Build and validate request payload
        create_model = SnippetCreateModel(**data)

        # Convert back to a Python dictionary, removing any unset fields
        payload = create_model.model_dump(exclude_unset=True)

        # Send the updated object to the remote API as JSON, expecting a dictionary object to be returned.
        response: Dict[str, Any] = self.api_client.post(
            self.ENDPOINT,
            json=payload,
        )

        # Return the SCM API response as a new Pydantic object
        return SnippetResponseModel.model_validate(response)

    def get(
        self,
        object_id: Union[str, UUID],
    ) -> SnippetResponseModel:
        """Get a snippet object by ID.

        Args:
            object_id: The UUID of the snippet to retrieve.

        Returns:
            SnippetResponseModel: The requested snippet.

        Raises:
            ObjectNotPresentError: If the snippet doesn't exist.
            APIError: If the API request fails.

        """
        # Convert UUID to string if necessary
        object_id_str = str(object_id)

        # Send the request to the remote API
        try:
            response: Dict[str, Any] = self.api_client.get(f"{self.ENDPOINT}/{object_id_str}")

            # Return the SCM API response as a new Pydantic object
            return SnippetResponseModel.model_validate(response)

        # Handle API errors
        except APIError as e:
            if e.http_status_code == 404:
                raise ObjectNotPresentError(f"Snippet with ID {object_id} not found")
            raise

    @staticmethod
    def _apply_filters(
        data: List["SnippetResponseModel"],
        filters: Dict[str, Any],
    ) -> List["SnippetResponseModel"]:
        """Apply client-side filters to a list of snippets."""
        filtered_data = data

        if not filters:
            return filtered_data

        # Filter by labels (client-side)
        if "labels" in filters:
            if not isinstance(filters["labels"], list):
                raise InvalidObjectError(
                    message="'labels' filter must be a list",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Filter Type"},
                )

            required_labels = set(filters["labels"])
            if required_labels:  # Only filter if labels list is not empty
                filtered_data = [
                    item
                    for item in filtered_data
                    if item.labels and required_labels.intersection(set(item.labels))
                ]

        # Filter by types (client-side)
        if "types" in filters:
            required_types = filters["types"]
            # Validate that required_types is a list of strings
            if not isinstance(required_types, list) or not all(
                isinstance(t, str) for t in required_types
            ):
                raise InvalidObjectError(
                    message="'types' filter must be a list of strings",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Filter Type"},
                )

            if required_types:  # Only filter if the list is not empty
                # Convert to set for efficient lookup
                required_types_set = set(required_types)
                filtered_data = [
                    item for item in filtered_data if item.type and item.type in required_types_set
                ]

        return filtered_data

    def list(
        self,
        **filters: Any,  # Accept arbitrary filters ('labels', 'types')
    ) -> List[SnippetResponseModel]:
        """List snippet objects with optional server-side and client-side filtering.

        Args:
            **filters: Additional filters:
                - labels (List[str]): Filter by labels (server-side if supported).
                - types (List[str]): Filter by snippet type (server-side if supported).

        Returns:
            List[SnippetResponseModel]: A list of snippets matching the filters.

        Raises:
            APIError: If the API request fails.
            InvalidObjectError: If filter parameters are invalid.

        """
        # Prepare API parameters
        params: Dict[str, Any] = {}

        # Add server-side filters if supported by the API
        if "labels" in filters:
            params["labels"] = ",".join(filters["labels"])
        if "types" in filters:
            params["types"] = ",".join(filters["types"])

        # Pagination logic using instance max_limit
        limit = self._max_limit
        offset = 0
        all_objects = []

        while True:
            params["limit"] = limit
            params["offset"] = offset

            # Get paginated results from the API
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

            # Handle single-item response when name filter returns one object
            if "data" not in response:
                # API returned a single object; wrap it into a list
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

            object_instances = [SnippetResponseModel.model_validate(item) for item in data_items]
            all_objects.extend(object_instances)

            # If we got fewer than 'limit' objects, we've reached the end
            if len(data_items) < limit:
                break

            offset += limit

        # Apply any remaining client-side filters
        filtered_snippets = self._apply_filters(
            all_objects,
            {k: v for k, v in filters.items() if k not in ["labels", "types"]},
        )

        return filtered_snippets

    def fetch(
        self,
        name: str,
    ) -> Optional[SnippetResponseModel]:
        """Get a snippet by its name.

        Args:
            name: The name of the snippet to retrieve.

        Returns:
            Optional[SnippetResponseModel]: The requested snippet (exact name match), or None if not found.

        """
        # Get snippets
        results = self.list()

        if not results:
            return None

        # Filter to exact matches
        exact_matches = [snippet for snippet in results if snippet.name == name]
        if not exact_matches:
            return None
        return exact_matches[0]

    def associate_folder(
        self, snippet_id: Union[str, UUID], folder_id: Union[str, UUID]
    ) -> SnippetResponseModel:
        """Associate a snippet with a folder.

        Args:
            snippet_id: The ID of the snippet.
            folder_id: The ID of the folder to associate.

        Returns:
            SnippetResponseModel: The updated snippet.

        Raises:
            NotImplementedError: This method is not yet implemented.

        """
        # This is a placeholder for future implementation
        snippet_id_str = str(snippet_id)
        folder_id_str = str(folder_id)

        try:
            response = self.api_client.post(
                f"{self.ENDPOINT}/{snippet_id_str}/folders",
                json={"folder_id": folder_id_str},
            )
            return SnippetResponseModel.model_validate(response)
        except Exception as e:
            raise NotImplementedError(
                f"Associating snippets with folders is not yet implemented: {str(e)}"
            )

    def disassociate_folder(
        self, snippet_id: Union[str, UUID], folder_id: Union[str, UUID]
    ) -> SnippetResponseModel:
        """Disassociate a snippet from a folder.

        Args:
            snippet_id: The ID of the snippet.
            folder_id: The ID of the folder to disassociate.

        Returns:
            SnippetResponseModel: The updated snippet.

        Raises:
            NotImplementedError: This method is not yet implemented.

        """
        # This is a placeholder for future implementation
        snippet_id_str = str(snippet_id)
        folder_id_str = str(folder_id)

        try:
            response = self.api_client.delete(
                f"{self.ENDPOINT}/{snippet_id_str}/folders/{folder_id_str}"
            )
            return SnippetResponseModel.model_validate(response)
        except Exception as e:
            raise NotImplementedError(
                f"Disassociating snippets from folders is not yet implemented: {str(e)}"
            )

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
        snippet: SnippetUpdateModel,
    ) -> SnippetResponseModel:
        """Update an existing snippet object.

        Args:
            snippet: The SnippetUpdateModel containing the updated snippet data.

        Returns:
            SnippetResponseModel: The updated snippet.

        Raises:
            InvalidObjectError: If the update data is invalid.
            ObjectNotPresentError: If the snippet doesn't exist.
            APIError: If the API request fails.

        """
        # Convert to dict for API request, excluding unset fields
        payload = snippet.model_dump(exclude_unset=True)

        # Extract ID and remove from payload since it's in the URL
        object_id = str(snippet.id)
        payload.pop("id", None)

        # Send the updated object to the remote API as JSON
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.put(
            endpoint,
            json=payload,
        )

        # Return the SCM API response as a new Pydantic object
        return SnippetResponseModel.model_validate(response)

    def delete(
        self,
        object_id: Union[str, UUID],
    ) -> None:
        """Delete a snippet object.

        Args:
            object_id: The ID of the snippet to delete.

        Raises:
            ObjectNotPresentError: If the snippet doesn't exist.
            APIError: If the API request fails.

        """
        try:
            object_id_str = str(object_id)
            self.api_client.delete(f"{self.ENDPOINT}/{object_id_str}")
        except APIError as e:
            if e.http_status_code == 404:
                raise ObjectNotPresentError(f"Snippet with ID {object_id} not found")
            raise
