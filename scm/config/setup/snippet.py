"""
Service classes for interacting with Snippets in Palo Alto Networks' Strata Cloud Manager.

This module provides the Snippet class for performing CRUD operations on Snippet resources
in the Strata Cloud Manager.
"""

from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from scm.config import BaseObject
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.setup.snippet_models import (
    SnippetCreateModel,
    SnippetResponseModel,
    SnippetUpdateModel,
)


class Snippet(BaseObject):
    """
    Manages Snippet objects in Palo Alto Networks' Strata Cloud Manager.

    This class provides methods for creating, retrieving, updating, deleting,
    and listing Snippet resources through the Strata Cloud Manager API.
    """

    ENDPOINT = "/config/setup/v1/snippets"
    DEFAULT_MAX_LIMIT = 2500
    ABSOLUTE_MAX_LIMIT = 5000  # Maximum allowed by the API

    def __init__(self, api_client, max_limit: int = DEFAULT_MAX_LIMIT):
        """
        Initialize the Snippet service class.

        Args:
            api_client: The API client instance for making HTTP requests.
            max_limit: Maximum number of items to return in a single request.
                      Defaults to DEFAULT_MAX_LIMIT.
        """
        super().__init__(api_client)
        self.max_limit = min(max_limit, self.ABSOLUTE_MAX_LIMIT)

    def create(
        self,
        name: str,
        description: Optional[str] = None,
        labels: Optional[List[str]] = None,
        enable_prefix: Optional[bool] = None,
    ) -> SnippetResponseModel:
        """
        Create a new snippet in Strata Cloud Manager.

        Args:
            name: The name of the snippet.
            description: Optional description of the snippet.
            labels: Optional list of labels to apply to the snippet.
            enable_prefix: Whether to enable prefix for this snippet.

        Returns:
            SnippetResponseModel: The created snippet.

        Raises:
            InvalidObjectError: If the snippet data is invalid.
            APIError: If the API request fails.
        """
        # Validate and prepare the data
        data = self._validate_and_prepare_data(
            name=name,
            description=description,
            labels=labels,
            enable_prefix=enable_prefix,
        )

        # Make the API call
        response = self.api_client.post(
            self.ENDPOINT,
            json=data,
        )

        # Return the model
        return SnippetResponseModel.model_validate(response)

    def get(self, object_id: Union[str, UUID]) -> SnippetResponseModel:
        """
        Get a snippet by ID.

        Args:
            object_id: The UUID of the snippet to retrieve.

        Returns:
            SnippetResponseModel: The requested snippet.

        Raises:
            ObjectNotPresentError: If the snippet doesn't exist.
            APIError: If the API request fails.
        """
        try:
            object_id_str = str(object_id)
            response = self.api_client.get(f"{self.ENDPOINT}/{object_id_str}")
            return SnippetResponseModel.model_validate(response)
        except APIError as e:
            if e.http_status_code == 404:
                raise ObjectNotPresentError(f"Snippet with ID {object_id} not found")
            raise

    def update(
        self,
        snippet_id: Union[str, UUID],
        name: Optional[str] = None,
        description: Optional[str] = None,
        labels: Optional[List[str]] = None,
        enable_prefix: Optional[bool] = None,
    ) -> SnippetResponseModel:
        """
        Update an existing snippet.

        Args:
            snippet_id: The ID of the snippet to update.
            name: The updated name of the snippet.
            description: The updated description of the snippet.
            labels: The updated list of labels.
            enable_prefix: Whether to enable prefix for this snippet.

        Returns:
            SnippetResponseModel: The updated snippet.

        Raises:
            InvalidObjectError: If the update data is invalid.
            ObjectNotPresentError: If the snippet doesn't exist.
            APIError: If the API request fails.
        """
        # Ensure at least one field is specified for update
        if all(v is None for v in [name, description, labels, enable_prefix]):
            raise InvalidObjectError("At least one field must be specified for update")

        # Prepare the update data
        update_data = {}
        if name is not None:
            update_data["name"] = self._validate_name(name)
        if description is not None:
            update_data["description"] = description
        if labels is not None:
            update_data["labels"] = self._validate_labels(labels)
        if enable_prefix is not None:
            update_data["enable_prefix"] = enable_prefix

        # Make the API call
        try:
            snippet_id_str = str(snippet_id)
            response = self.api_client.put(
                f"{self.ENDPOINT}/{snippet_id_str}",
                json=update_data,
            )
            return SnippetResponseModel.model_validate(response)
        except APIError as e:
            if e.http_status_code == 404:
                raise ObjectNotPresentError(f"Snippet with ID {snippet_id} not found")
            raise

    def delete(self, object_id: Union[str, UUID]) -> None:
        """
        Delete a snippet.

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

    def list(
        self,
        name: Optional[str] = None,
        type: Optional[str] = None,
        exact_match: bool = False,
        offset: int = 0,
        limit: Optional[int] = None,
    ) -> List[SnippetResponseModel]:
        """
        List snippets with optional filtering.

        Args:
            name: Optional filter for snippet name.
            type: Optional filter for snippet type.
            exact_match: If True, performs exact name matching rather than substring.
            offset: Starting position for pagination.
            limit: Maximum number of items to return (defaults to max_limit).

        Returns:
            List[SnippetResponseModel]: A list of snippets matching the filters.

        Raises:
            APIError: If the API request fails.
        """
        # Prepare filter parameters
        params = {}
        if name is not None:
            params["name"] = name
        if type is not None:
            params["type"] = type

        # Get paginated results
        snippets = self._get_paginated_results(
            endpoint=self.ENDPOINT,
            params=params,
            limit=limit or self.max_limit,
            offset=offset,
        )

        # Handle exact_match filter if specified
        if exact_match and name is not None and snippets:
            snippets = [s for s in snippets if s.get("name") == name]

        # Convert the results to models
        result = [SnippetResponseModel.model_validate(item) for item in snippets]
        return result

    def fetch(self, name: str) -> Optional[SnippetResponseModel]:
        """
        Fetch a single snippet by name.

        Args:
            name: The name of the snippet to fetch.

        Returns:
            Optional[SnippetResponseModel]: The snippet if found, None otherwise.

        Raises:
            APIError: If multiple snippets with the same name are found.
        """
        try:
            # First try direct query with name parameter
            response = self.api_client.get(
                self.ENDPOINT,
                params={"name": name},
            )
            
            if isinstance(response, dict) and "data" in response:
                snippets = response["data"]
                if len(snippets) == 1:
                    return SnippetResponseModel.model_validate(snippets[0])
                elif len(snippets) > 1:
                    raise APIError(f"Multiple snippets found with name {name}")
                return None
            
            # Unexpected response format
            return None
        except APIError as e:
            if e.http_status_code == 404:
                # Fall back to listing and filtering
                snippets = self.list(name=name, exact_match=True)
                if len(snippets) == 1:
                    return snippets[0]
                elif len(snippets) > 1:
                    raise APIError(f"Multiple snippets found with name {name}")
                return None
            raise

    def associate_folder(
        self, snippet_id: Union[str, UUID], folder_id: Union[str, UUID]
    ) -> SnippetResponseModel:
        """
        Associate a snippet with a folder.

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
        """
        Disassociate a snippet from a folder.

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

    def _validate_and_prepare_data(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        labels: Optional[List[str]] = None,
        enable_prefix: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Validate and prepare snippet data for API requests.

        Args:
            name: The name of the snippet.
            description: The description of the snippet.
            labels: The list of labels.
            enable_prefix: Whether to enable prefix for this snippet.

        Returns:
            Dict[str, Any]: The validated and prepared data.

        Raises:
            InvalidObjectError: If the data is invalid.
        """
        # Start with empty data
        data = {}

        # Add and validate the name if provided
        if name is not None:
            data["name"] = self._validate_name(name)

        # Add optional fields if provided
        if description is not None:
            data["description"] = description
        if labels is not None:
            data["labels"] = self._validate_labels(labels)
        if enable_prefix is not None:
            data["enable_prefix"] = enable_prefix

        # Ensure required fields are present
        if "name" not in data:
            raise InvalidObjectError("Name is required")

        return data

    def _validate_name(self, name: str) -> str:
        """
        Validate a snippet name.

        Args:
            name: The name to validate.

        Returns:
            str: The validated name.

        Raises:
            InvalidObjectError: If the name is invalid.
        """
        if not name or name.strip() == "":
            raise InvalidObjectError("Snippet name cannot be empty")
        if len(name) > 255:
            raise InvalidObjectError("Snippet name cannot exceed 255 characters")
        return name

    def _validate_labels(self, labels: Optional[List[str]]) -> Optional[List[str]]:
        """
        Validate snippet labels.

        Args:
            labels: The labels to validate.

        Returns:
            Optional[List[str]]: The validated labels.

        Raises:
            InvalidObjectError: If any label is invalid.
        """
        if labels is None:
            return None
        
        # Ensure all labels are strings
        validated_labels = []
        for label in labels:
            if not isinstance(label, str):
                raise InvalidObjectError(f"Label must be a string: {label}")
            validated_labels.append(label)
        
        return validated_labels

    def _get_paginated_results(
        self,
        endpoint: str,
        params: Dict[str, Any],
        limit: int,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Get paginated results from an API endpoint.

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
