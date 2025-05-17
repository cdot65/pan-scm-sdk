"""Service classes for interacting with Labels in Palo Alto Networks' Strata Cloud Manager.

This module provides the Label class for performing CRUD operations on Label resources
in the Strata Cloud Manager.
"""

# Standard library imports
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.setup.label import (
    LabelCreateModel,
    LabelResponseModel,
    LabelUpdateModel,
)


class Label(BaseObject):
    """Manages Label objects in Palo Alto Networks' Strata Cloud Manager.

    This class provides methods for creating, retrieving, updating, and deleting Label resources.

    Attributes:
        ENDPOINT: The API endpoint for Label resources.
        DEFAULT_MAX_LIMIT: The default maximum number of items to return in a single request.
        ABSOLUTE_MAX_LIMIT: The maximum allowed number of items to return in a single request.

    """

    ENDPOINT = "/config/setup/v1/labels"
    DEFAULT_MAX_LIMIT = 2500
    ABSOLUTE_MAX_LIMIT = 5000  # Maximum allowed by the API

    def __init__(
        self,
        api_client,
        max_limit: int = DEFAULT_MAX_LIMIT,
    ):
        """Initialize the Label service class.

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
    ) -> LabelResponseModel:
        """Create a new label object in the Strata Cloud Manager.

        Args:
            data: Dictionary containing label data.

        Returns:
            LabelResponseModel: The created label.

        Raises:
            InvalidObjectError: If the label data is invalid.
            APIError: If the API request fails.

        """
        # Validate and serialize input using Pydantic
        create_model = LabelCreateModel(**data)
        payload = create_model.model_dump(exclude_unset=True)
        response = self.api_client.post(self.ENDPOINT, json=payload)
        return LabelResponseModel.model_validate(response)

    def get(
        self,
        label_id: Union[str, UUID],
    ) -> LabelResponseModel:
        """Get a label object by ID.

        Args:
            label_id: The ID of the label to retrieve.

        Returns:
            LabelResponseModel: The requested label.

        Raises:
            ObjectNotPresentError: If the label doesn't exist.
            APIError: If the API request fails.

        """
        label_id_str = str(label_id)
        try:
            response = self.api_client.get(f"{self.ENDPOINT}/{label_id_str}")
            return LabelResponseModel.model_validate(response)
        except APIError as e:
            if e.http_status_code == 404:
                raise ObjectNotPresentError(f"Label with ID {label_id} not found")
            raise

    def update(
        self,
        label: Union[LabelUpdateModel, LabelResponseModel],
    ) -> LabelResponseModel:
        """Update an existing label object.

        Args:
            label: Either a LabelUpdateModel or LabelResponseModel containing the updated label data.

        Returns:
            LabelResponseModel: The updated label.

        Raises:
            InvalidObjectError: If the update data is invalid.
            ObjectNotPresentError: If the label doesn't exist.
            APIError: If the API request fails.

        """
        # Handle either model type appropriately
        if isinstance(label, LabelResponseModel):
            # Convert LabelResponseModel to a dict for model_dump compatibility
            data = {
                "id": label.id,
                "name": label.name,
                "description": label.description,
            }
            # Create a LabelUpdateModel from the LabelResponseModel fields
            update_model = LabelUpdateModel(**data)
            payload = update_model.model_dump(exclude_unset=True)
        else:
            # Already a LabelUpdateModel
            payload = label.model_dump(exclude_unset=True)

        object_id = str(label.id)
        payload.pop("id", None)
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response = self.api_client.put(endpoint, json=payload)

        # Handle the API returning a list instead of a single object
        if isinstance(response, list) and len(response) > 0:
            return LabelResponseModel.model_validate(response[0])
        else:
            return LabelResponseModel.model_validate(response)

    def delete(
        self,
        label_id: Union[str, UUID],
    ) -> None:
        """Delete a label object.

        Args:
            label_id: The ID of the label to delete.

        Raises:
            ObjectNotPresentError: If the label doesn't exist.
            APIError: If the API request fails.

        """
        try:
            object_id_str = str(label_id)
            self.api_client.delete(f"{self.ENDPOINT}/{object_id_str}")
        except APIError as e:
            if e.http_status_code == 404:
                raise ObjectNotPresentError(f"Label with ID {label_id} not found")
            raise

    def list(
        self,
        **filters: Any,
    ) -> List[LabelResponseModel]:
        """List label objects with optional filtering.

        Args:
            **filters: Additional filters for the API.

        Returns:
            List[LabelResponseModel]: A list of labels matching the filters.

        Raises:
            APIError: If the API request fails.

        """
        params: Dict[str, Any] = {}
        limit = self.max_limit
        offset = 0
        all_objects: List[LabelResponseModel] = []
        while True:
            params.update({"limit": limit, "offset": offset})
            params.update({k: v for k, v in filters.items() if v is not None})
            response = self.api_client.get(self.ENDPOINT, params=params)
            data_items = response["data"] if "data" in response else response
            object_instances = [LabelResponseModel.model_validate(item) for item in data_items]
            all_objects.extend(object_instances)
            if len(data_items) < limit:
                break
            offset += limit
        return all_objects

    def fetch(
        self,
        name: str,
    ) -> Optional[LabelResponseModel]:
        """Fetch a single label by name.

        Args:
            name: The name of the label to retrieve.

        Returns:
            Optional[LabelResponseModel]: The requested label (exact name match), or None if not found.

        """
        # Get all labels
        results = self.list()

        if not results:
            return None

        # Filter to exact matches
        exact_matches = [label for label in results if label.name == name]
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
