"""Service classes for interacting with Variables in Palo Alto Networks' Strata Cloud Manager.

This module provides the Variable class for performing CRUD operations on Variable resources
in the Strata Cloud Manager.
"""

# Standard library imports
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.setup.variable import (
    VariableCreateModel,
    VariableResponseModel,
    VariableUpdateModel,
)


class Variable(BaseObject):
    """Manages Variable objects in Palo Alto Networks' Strata Cloud Manager.

    This class provides methods for creating, retrieving, updating, and deleting Variable resources.

    Attributes:
        ENDPOINT: The API endpoint for Variable resources.
        DEFAULT_MAX_LIMIT: The default maximum number of items to return in a single request.
        ABSOLUTE_MAX_LIMIT: The maximum allowed number of items to return in a single request.

    """

    ENDPOINT = "/config/setup/v1/variables"
    DEFAULT_MAX_LIMIT = 2500
    ABSOLUTE_MAX_LIMIT = 5000  # Maximum allowed by the API

    def __init__(
        self,
        api_client,
        max_limit: int = DEFAULT_MAX_LIMIT,
    ):
        """Initialize the Variable service class.

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
    ) -> VariableResponseModel:
        """Create a new Variable in the Strata Cloud Manager.

        Args:
            data: Dictionary containing variable data.

        Returns:
            VariableResponseModel: The created variable.

        Raises:
            InvalidObjectError: If the variable data is invalid.
            APIError: If the API request fails.

        """
        # Validate and serialize input using Pydantic
        create_model = VariableCreateModel(**data)
        payload = create_model.model_dump(exclude_unset=True)
        response = self.api_client.post(self.ENDPOINT, json=payload)
        return VariableResponseModel.model_validate(response)

    def get(
        self,
        variable_id: Union[str, UUID],
    ) -> VariableResponseModel:
        """Get a variable by its ID.

        Args:
            variable_id: The ID of the variable to retrieve.

        Returns:
            VariableResponseModel: The requested variable.

        Raises:
            ObjectNotPresentError: If the variable doesn't exist.
            APIError: If the API request fails.

        """
        variable_id_str = str(variable_id)
        try:
            response = self.api_client.get(f"{self.ENDPOINT}/{variable_id_str}")
            return VariableResponseModel.model_validate(response)
        except APIError as e:
            if e.http_status_code == 404:
                raise ObjectNotPresentError(f"Variable with ID {variable_id} not found")
            raise

    def update(
        self,
        variable: VariableUpdateModel,
    ) -> VariableResponseModel:
        """Update an existing variable.

        Args:
            variable: The VariableUpdateModel containing the updated variable data.

        Returns:
            VariableResponseModel: The updated variable.

        Raises:
            InvalidObjectError: If the update data is invalid.
            ObjectNotPresentError: If the variable doesn't exist.
            APIError: If the API request fails.

        """
        payload = variable.model_dump(exclude_unset=True)
        object_id = str(variable.id)
        payload.pop("id", None)
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response = self.api_client.put(endpoint, json=payload)
        return VariableResponseModel.model_validate(response)

    def delete(
        self,
        variable_id: Union[str, UUID],
    ) -> None:
        """Delete a variable.

        Args:
            variable_id: The ID of the variable to delete.

        Raises:
            ObjectNotPresentError: If the variable doesn't exist.
            APIError: If the API request fails.

        """
        try:
            object_id_str = str(variable_id)
            self.api_client.delete(f"{self.ENDPOINT}/{object_id_str}")
        except APIError as e:
            if e.http_status_code == 404:
                raise ObjectNotPresentError(f"Variable with ID {variable_id} not found")
            raise

    def list(
        self,
        **filters: Any,
    ) -> List[VariableResponseModel]:
        """List variables with optional filters.

        Args:
            **filters: Additional filters for the API.

        Returns:
            List[VariableResponseModel]: A list of variables matching the filters.

        Raises:
            APIError: If the API request fails.

        """
        params: Dict[str, Any] = {}
        limit = self.max_limit
        offset = 0
        all_objects: List[VariableResponseModel] = []
        while True:
            params.update({"limit": limit, "offset": offset})
            params.update({k: v for k, v in filters.items() if v is not None})
            response = self.api_client.get(self.ENDPOINT, params=params)
            data_items = response["data"] if "data" in response else response
            object_instances = [VariableResponseModel.model_validate(item) for item in data_items]
            all_objects.extend(object_instances)
            if len(data_items) < limit:
                break
            offset += limit
        return all_objects

    def fetch(
        self,
        name: str,
        folder: str,
    ) -> Optional[VariableResponseModel]:
        """Get a variable by its name and folder.

        Args:
            name: The name of the variable to retrieve.
            folder: The folder in which the variable is defined.

        Returns:
            Optional[VariableResponseModel]: The requested variable (exact name match), or None if not found.

        Raises:
            MissingQueryParameterError: If name or folder is empty.
            InvalidObjectError: If the response format is invalid.

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

        # Use the folder parameter in the API request
        results = self.list(folder=folder)

        if not results:
            return None

        # Filter to exact matches
        exact_matches = [variable for variable in results if variable.name == name]
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

    @staticmethod
    def _apply_filters(
        data: List["VariableResponseModel"],
        filters: Dict[str, Any],
    ) -> List["VariableResponseModel"]:
        """Apply client-side filters to a list of variables."""
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
