# scm/config/objects/application_filters.py

# Standard library imports
import logging
from typing import List, Dict, Any, Optional

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
)
from scm.models.objects import (
    ApplicationFiltersCreateModel,
    ApplicationFiltersResponseModel,
    ApplicationFiltersUpdateModel,
)


class ApplicationFilters(BaseObject):
    """
    Manages Application filters in Palo Alto Networks' Strata Cloud Manager.
    Args:
        api_client: The API client instance
        max_limit (Optional[int]): Maximum number of objects to return in a single API request.
            Defaults to 5000. Must be between 1 and 10000.
    """

    ENDPOINT = "/config/objects/v1/application-filters"
    DEFAULT_MAX_LIMIT = 2500
    ABSOLUTE_MAX_LIMIT = 5000  # Maximum allowed by the API

    def __init__(
        self,
        api_client,
        max_limit: Optional[int] = None,
    ):
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
        """
        Validates the max_limit parameter.

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
    ) -> ApplicationFiltersResponseModel:
        """
        Creates a new application filter object.

        Returns:
            ApplicationFiltersResponseModel
        """
        # Use the dictionary "data" to pass into Pydantic and return a modeled object
        application_filter = ApplicationFiltersCreateModel(**data)

        # Convert back to a Python dictionary, removing any unset fields
        payload = application_filter.model_dump(exclude_unset=True)

        # Send the updated object to the remote API as JSON
        response: Dict[str, Any] = self.api_client.post(
            self.ENDPOINT,
            json=payload,
        )

        # Return the SCM API response as a new Pydantic object
        return ApplicationFiltersResponseModel(**response)

    def get(
        self,
        object_id: str,
    ) -> ApplicationFiltersResponseModel:
        """
        Gets an application filter object by ID.

        Returns:
            ApplicationFiltersResponseModel
        """
        # Send the request to the remote API
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.get(endpoint)

        # Return the SCM API response as a new Pydantic object
        return ApplicationFiltersResponseModel(**response)

    def update(
        self,
        application: ApplicationFiltersUpdateModel,
    ) -> ApplicationFiltersResponseModel:
        """
        Updates an existing application filter object.

        Args:
            application: ApplicationFiltersUpdateModel instance containing the update data

        Returns:
            ApplicationFiltersResponseModel
        """
        # Convert to dict for API request, excluding unset fields
        payload = application.model_dump(exclude_unset=True)

        # Extract ID and remove from payload since it's in the URL
        object_id = str(application.id)
        payload.pop("id", None)

        # Send the updated object to the remote API as JSON
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.put(
            endpoint,
            json=payload,
        )

        # Return the SCM API response as a new Pydantic model
        return ApplicationFiltersResponseModel(**response)

    @staticmethod
    def _apply_filters(
        application_filters: List[ApplicationFiltersResponseModel],
        filters: Dict[str, Any],
    ) -> List[ApplicationFiltersResponseModel]:
        """
        Apply client-side filtering to the list of application filters.

        Args:
            application_filters: List of ApplicationFilterResponseModel objects
            filters: Dictionary of filter criteria

        Returns:
            List[ApplicationFiltersResponseModel]: Filtered list of application filters
        """
        filter_criteria = application_filters

        # Filter by category
        if "category" in filters:
            if not isinstance(filters["category"], list):
                raise InvalidObjectError(
                    message="'category' filter must be a list",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Object"},
                )
            categories = filters["category"]
            filter_criteria = [
                app
                for app in filter_criteria
                if app.category is not None
                and any(cat in app.category for cat in categories)
            ]

        # Filter by subcategory
        if "subcategory" in filters:
            if not isinstance(filters["subcategory"], list):
                raise InvalidObjectError(
                    message="'subcategory' filter must be a list",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Object"},
                )
            subcategories = filters["subcategory"]
            filter_criteria = [
                app
                for app in filter_criteria
                if app.sub_category is not None
                and any(sub in app.sub_category for sub in subcategories)
            ]

        # Filter by technology
        if "technology" in filters:
            if not isinstance(filters["technology"], list):
                raise InvalidObjectError(
                    message="'technology' filter must be a list",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Object"},
                )
            technologies = filters["technology"]
            filter_criteria = [
                app
                for app in filter_criteria
                if app.technology is not None
                and any(tech in app.technology for tech in technologies)
            ]

        # Filter by risk
        if "risk" in filters:
            if not isinstance(filters["risk"], list):
                raise InvalidObjectError(
                    message="'risk' filter must be a list",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Object"},
                )
            risks = filters["risk"]
            filter_criteria = [
                app
                for app in filter_criteria
                if app.risk is not None and any(risk in app.risk for risk in risks)
            ]

        return filter_criteria

    @staticmethod
    def _build_container_params(
        folder: Optional[str],
        snippet: Optional[str],
    ) -> dict:
        """Builds container parameters dictionary."""
        return {
            k: v
            for k, v in {"folder": folder, "snippet": snippet}.items()
            if v is not None
        }

    def list(
        self,
        folder: Optional[str] = None,
        snippet: Optional[str] = None,
        exact_match: bool = False,
        exclude_folders: Optional[List[str]] = None,
        exclude_snippets: Optional[List[str]] = None,
        **filters,
    ) -> List[ApplicationFiltersResponseModel]:
        """
        Lists application objects with optional filtering.

        Args:
            folder: Optional folder name
            snippet: Optional snippet name
            exact_match (bool): If True, only return objects whose container
                                exactly matches the provided container parameter.
            exclude_folders (List[str], optional): List of folder names to exclude from results.
            exclude_snippets (List[str], optional): List of snippet values to exclude from results.
            **filters: Additional filters including:
                - category: List[str] - Filter by category
                - subcategory: List[str] - Filter by subcategory
                - technology: List[str] - Filter by technology
                - risk: List[int] - Filter by risk level

        Returns:
            List[ApplicationFiltersResponseModel]: A list of application filter objects
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
        )

        if len(container_parameters) != 1:
            raise InvalidObjectError(
                message="Exactly one of 'folder' or 'snippet' must be provided.",
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
            object_instances = [
                ApplicationFiltersResponseModel(**item) for item in data
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
                each
                for each in filtered_objects
                if getattr(each, container_key) == container_value
            ]

        # Exclude folders if provided
        if exclude_folders and isinstance(exclude_folders, list):
            filtered_objects = [
                each for each in filtered_objects if each.folder not in exclude_folders
            ]

        # Exclude snippets if provided
        if exclude_snippets and isinstance(exclude_snippets, list):
            filtered_objects = [
                each
                for each in filtered_objects
                if each.snippet not in exclude_snippets
            ]

        return filtered_objects

    def fetch(
        self,
        name: str,
        folder: Optional[str] = None,
        snippet: Optional[str] = None,
    ) -> ApplicationFiltersResponseModel:
        """
        Fetches a single application filter by name.

        Args:
            name (str): The name of the application filter to fetch.
            folder (str, optional): The folder in which the resource is defined.
            snippet (str, optional): The snippet in which the resource is defined.

        Returns:
            ApplicationFiltersResponseModel: The fetched application filter object as a Pydantic model.
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
        )

        if len(container_parameters) != 1:
            raise InvalidObjectError(
                message="Exactly one of 'folder' or 'snippet' must be provided.",
                error_code="E003",
                http_status_code=400,
                details={
                    "error": "Exactly one of 'folder' or 'snippet' must be provided."
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
            return ApplicationFiltersResponseModel(**response)
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
        """
        Deletes an application filter object.

        Args:
            object_id (str): The ID of the object to delete.
        """
        endpoint = f"{self.ENDPOINT}/{object_id}"
        self.api_client.delete(endpoint)
