# scm/config/objects/application.py

from typing import List, Dict, Any, Optional
import logging
from scm.config import BaseObject
from scm.models.objects import (
    ApplicationCreateModel,
    ApplicationResponseModel,
    ApplicationUpdateModel,
)
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
    ErrorHandler,
    APIError,
)


class Application(BaseObject):
    """
    Manages Application objects in Palo Alto Networks' Strata Cloud Manager.
    """

    ENDPOINT = "/config/objects/v1/applications"
    DEFAULT_LIMIT = 10000

    def __init__(
        self,
        api_client,
    ):
        super().__init__(api_client)
        self.logger = logging.getLogger(__name__)

    def create(
        self,
        data: Dict[str, Any],
    ) -> ApplicationResponseModel:
        """
        Creates a new application object.

        Returns:
            ApplicationResponseModel

        Raises:
            APIError: For any API-related errors
        """
        try:
            application = ApplicationCreateModel(**data)
            payload = application.model_dump(exclude_unset=True)
            response = self.api_client.post(
                self.ENDPOINT,
                json=payload,
            )
            return ApplicationResponseModel(**response)

        except Exception as e:
            if isinstance(e, APIError):
                self.logger.error(f"API error while creating application: {e}")
                raise
            else:
                self.logger.error(
                    f"An unexpected error occurred while creating application: {e}"
                )
                raise APIError("An unexpected error occurred") from e

    def get(
        self,
        object_id: str,
    ) -> ApplicationResponseModel:
        """
        Gets an application object by ID.

        Returns:
            ApplicationResponseModel

        Raises:
            APIError: For any API-related errors
        """
        try:
            endpoint = f"{self.ENDPOINT}/{object_id}"
            response = self.api_client.get(endpoint)
            return ApplicationResponseModel(**response)

        except Exception as e:
            self.logger.error(
                f"Error getting application: {e}",
                exc_info=True,
            )
            if hasattr(e, "response") and e.response is not None:  # noqa
                ErrorHandler.raise_for_error(
                    e.response.json(),
                    e.response.status_code,
                )
            else:
                raise APIError(f"An unexpected error occurred: {e}") from e

    def update(
        self,
        data: Dict[str, Any],
    ) -> ApplicationResponseModel:
        """
        Updates an existing application object.

        Returns:
            ApplicationResponseModel

        Raises:
            APIError: For any API-related errors
        """
        try:
            application = ApplicationUpdateModel(**data)
            payload = application.model_dump(exclude_unset=True)
            endpoint = f"{self.ENDPOINT}/{data['id']}"
            response = self.api_client.put(
                endpoint,
                json=payload,
            )
            return ApplicationResponseModel(**response)

        except Exception as e:
            self.logger.error(
                f"Error updating application: {e}",
                exc_info=True,
            )
            if hasattr(e, "response") and e.response is not None:  # noqa
                ErrorHandler.raise_for_error(
                    e.response.json(),
                    e.response.status_code,
                )
            else:
                raise APIError(f"An unexpected error occurred: {e}") from e

    @staticmethod
    def _apply_filters(
        applications: List[ApplicationResponseModel],
        filters: Dict[str, Any],
    ) -> List[ApplicationResponseModel]:
        """
        Apply client-side filtering to the list of applications.

        Args:
            applications: List of ApplicationResponseModel objects
            filters: Dictionary of filter criteria

        Returns:
            List[ApplicationResponseModel]: Filtered list of applications

        Raises:
            InvalidObjectError: If filter criteria are invalid
        """
        filter_criteria = applications

        if "category" in filters:
            if not isinstance(filters["category"], list):
                raise InvalidObjectError("'category' filter must be a list")
            categories = filters["category"]
            filter_criteria = [
                app for app in filter_criteria if app.category in categories
            ]

        if "subcategory" in filters:
            if not isinstance(filters["subcategory"], list):
                raise InvalidObjectError("'subcategory' filter must be a list")
            subcategories = filters["subcategory"]
            filter_criteria = [
                app for app in filter_criteria if app.subcategory in subcategories
            ]

        if "technology" in filters:
            if not isinstance(filters["technology"], list):
                raise InvalidObjectError("'technology' filter must be a list")
            technologies = filters["technology"]
            filter_criteria = [
                app for app in filter_criteria if app.technology in technologies
            ]

        if "risk" in filters:
            if not isinstance(filters["risk"], list):
                raise InvalidObjectError("'risk' filter must be a list")
            risks = filters["risk"]
            filter_criteria = [app for app in filter_criteria if app.risk in risks]

        return filter_criteria

    @staticmethod
    def _build_container_params(
        folder: Optional[str],
        snippet: Optional[str],
        device: Optional[str],
    ) -> dict:
        """Builds container parameters dictionary."""
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
        **filters,
    ) -> List[ApplicationResponseModel]:
        """
        Lists application objects with optional filtering.

        Args:
            folder: Optional folder name
            snippet: Optional snippet name
            device: Optional device name
            **filters: Additional filters including:
                - category: List[str] - Filter by category
                - subcategory: List[str] - Filter by subcategory
                - technology: List[str] - Filter by technology
                - risk: List[int] - Filter by risk level

        Raises:
            MissingQueryParameterError: If provided container fields are empty
            InvalidObjectError: If the container parameters are invalid
            APIError: If response format is invalid
        """
        if folder == "":
            raise MissingQueryParameterError(
                message="Field 'folder' cannot be empty",
                error_code="E003",
                http_status_code=400,
                details=['"folder" is not allowed to be empty'],  # noqa
            )

        params = {"limit": self.DEFAULT_LIMIT}
        container_parameters = self._build_container_params(
            folder,
            snippet,
            device,
        )

        if len(container_parameters) != 1:
            raise InvalidObjectError(
                "Exactly one of 'folder', 'snippet', or 'device' must be provided.",
                error_code="E003",
                http_status_code=400,
            )

        params.update(container_parameters)

        try:
            response = self.api_client.get(
                self.ENDPOINT,
                params=params,
            )

            if not isinstance(response, dict):
                raise APIError(
                    "Invalid response format: expected dictionary",
                    http_status_code=500,
                )

            if "data" not in response:
                raise APIError(
                    "Invalid response format: missing 'data' field",
                    http_status_code=500,
                )

            if not isinstance(response["data"], list):
                raise APIError(
                    "Invalid response format: 'data' field must be a list",
                    http_status_code=500,
                )

            applications = [
                ApplicationResponseModel(**item) for item in response["data"]
            ]
            return self._apply_filters(applications, filters)

        except Exception as e:
            if isinstance(e, APIError):
                self.logger.error(f"API error while listing applications: {e}")
                raise
            else:
                self.logger.error(
                    f"An unexpected error occurred while listing applications: {e}"
                )
                raise APIError("An unexpected error occurred") from e

    def fetch(
        self,
        name: str,
        folder: Optional[str] = None,
        snippet: Optional[str] = None,
        device: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Fetches a single application by name.

        Args:
            name (str): The name of the application to fetch.
            folder (str, optional): The folder in which the resource is defined.
            snippet (str, optional): The snippet in which the resource is defined.
            device (str, optional): The device in which the resource is defined.

        Returns:
            Dict: The fetched object.

        Raises:
            MissingQueryParameterError: If name or container fields are empty
            InvalidObjectError: If the parameters are invalid
            APIError: For other API-related errors
        """
        if not name:
            raise MissingQueryParameterError(
                message="Field 'name' cannot be empty",
                error_code="E003",
                http_status_code=400,
                details=['"name" is not allowed to be empty'],  # noqa
            )

        if folder == "":
            raise MissingQueryParameterError(
                message="Field 'folder' cannot be empty",
                error_code="E003",
                http_status_code=400,
                details=['"folder" is not allowed to be empty'],  # noqa
            )

        params = {}
        container_parameters = self._build_container_params(
            folder,
            snippet,
            device,
        )

        if len(container_parameters) != 1:
            raise InvalidObjectError(
                "Exactly one of 'folder', 'snippet', or 'device' must be provided.",
                error_code="E003",
                http_status_code=400,
            )

        params.update(container_parameters)
        params["name"] = name

        try:
            response = self.api_client.get(
                self.ENDPOINT,
                params=params,
            )

            if not isinstance(response, dict):
                raise APIError(
                    "Invalid response format: expected dictionary",
                    http_status_code=500,
                )

            if "_errors" in response:
                ErrorHandler.raise_for_error(response, http_status_code=400)

            if "id" in response:
                application = ApplicationResponseModel(**response)
                return application.model_dump(
                    exclude_unset=True,
                    exclude_none=True,
                )
            else:
                raise APIError(
                    "Invalid response format: missing 'id' field",
                    http_status_code=500,
                )

        except Exception as e:
            self.logger.error(
                f"Error fetching application: {e}",
                exc_info=True,
            )
            if hasattr(e, "response") and e.response is not None:  # noqa
                ErrorHandler.raise_for_error(
                    e.response.json(),
                    e.response.status_code,
                )
            else:
                raise APIError(f"An unexpected error occurred: {e}") from e

    def delete(
        self,
        object_id: str,
    ) -> None:
        """
        Deletes an application object.

        Args:
            object_id (str): The ID of the object to delete.

        Raises:
            ObjectNotPresentError: If the object doesn't exist
            ReferenceNotZeroError: If the object is still referenced by other objects
            MalformedCommandError: If the request is malformed
        """
        try:
            endpoint = f"{self.ENDPOINT}/{object_id}"
            self.api_client.delete(endpoint)

        except Exception as e:
            self.logger.error(
                f"Error deleting application: {e}",
                exc_info=True,
            )
            if hasattr(e, "response") and e.response is not None:  # noqa
                ErrorHandler.raise_for_error(
                    e.response.json(),
                    e.response.status_code,
                )
            else:
                raise APIError(f"An unexpected error occurred: {e}") from e
