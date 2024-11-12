# scm/config/objects/application.py

from typing import List, Dict, Any, Optional
from scm.config import BaseObject
from scm.models.objects import (
    ApplicationCreateModel,
    ApplicationResponseModel,
    ApplicationUpdateModel,
)
from scm.exceptions import (
    ValidationError,
    EmptyFieldError,
    ErrorHandler,
    BadResponseError,
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

    def create(
        self,
        data: Dict[str, Any],
    ) -> ApplicationResponseModel:
        """
        Creates a new application object.

        Returns:
            ApplicationResponseModel

        Raises:
            Custom Error Handling class response
        """
        try:
            # Use the dictionary "data" to pass into Pydantic and return a modeled object
            application = ApplicationCreateModel(**data)

            # Convert back to a Python dictionary, but removing any excluded object
            payload = application.model_dump(exclude_unset=True)

            # Send the updated object to the remote API as JSON
            response = self.api_client.post(self.ENDPOINT, json=payload)

            # Return the SCM API response as a new Pydantic object
            return ApplicationResponseModel(**response)

        # Forward exceptions to our custom ErrorHandler object
        except Exception as e:
            if hasattr(e, "response") and e.response is not None:  # noqa
                ErrorHandler.raise_for_error(e.response.json())
            raise

    def get(
        self,
        object_id: str,
    ) -> ApplicationResponseModel:
        """
        Gets an application object by ID.

        Returns:
            ApplicationResponseModel

        Raises:
            Custom Error Handling class response
        """
        try:
            # Send the request to the remote API
            endpoint = f"{self.ENDPOINT}/{object_id}"
            response = self.api_client.get(endpoint)

            # Return the SCM API response as a new Pydantic object
            return ApplicationResponseModel(**response)

        # Forward exceptions to our custom ErrorHandler object
        except Exception as e:
            if hasattr(e, "response") and e.response is not None:  # noqa
                ErrorHandler.raise_for_error(e.response.json())
            raise

    def update(
        self,
        data: Dict[str, Any],
    ) -> ApplicationResponseModel:
        """
        Updates an existing application object.

        Returns:
            ApplicationResponseModel

        Raises:
            Custom Error Handling class response
        """
        try:
            # Use the dictionary "data" to pass into Pydantic and return a modeled object
            application = ApplicationUpdateModel(**data)

            # Convert back to a Python dictionary, but removing any excluded object
            payload = application.model_dump(exclude_unset=True)

            # Send the updated object to the remote API as JSON
            endpoint = f"{self.ENDPOINT}/{data['id']}"
            response = self.api_client.put(endpoint, json=payload)

            # Return the SCM API response as a new Pydantic object
            return ApplicationResponseModel(**response)

        # Forward exceptions to our custom ErrorHandler object
        except Exception as e:
            if hasattr(e, "response") and e.response is not None:  # noqa
                ErrorHandler.raise_for_error(e.response.json())
            raise

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
        """
        # Build a list of what criteria we are looking to filter our response from
        filter_criteria = applications

        # Perform filtering if the presence of "category" is found within the filters
        if "category" in filters:
            if not isinstance(filters["category"], list):
                raise ValidationError("'category' filter must be a list")
            categories = filters["category"]
            filter_criteria = [
                app for app in filter_criteria if app.category in categories
            ]

        # Perform filtering if the presence of "subcategory" is found within the filters
        if "subcategory" in filters:
            if not isinstance(filters["subcategory"], list):
                raise ValidationError("'subcategory' filter must be a list")
            subcategories = filters["subcategory"]
            filter_criteria = [
                app for app in filter_criteria if app.subcategory in subcategories
            ]

        # Perform filtering if the presence of "technology" is found within the filters
        if "technology" in filters:
            if not isinstance(filters["technology"], list):
                raise ValidationError("'technology' filter must be a list")
            technologies = filters["technology"]
            filter_criteria = [
                app for app in filter_criteria if app.technology in technologies
            ]

        # Perform filtering if the presence of "risk" is found within the filters
        if "risk" in filters:
            if not isinstance(filters["risk"], list):
                raise ValidationError("'risk' filter must be a list")
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
        # Only return a key of "folder", "snippet", or "device" if their value is not None
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
            EmptyFieldError: If provided container fields are empty
            FolderNotFoundError: If the specified folder doesn't exist
            ValidationError: If the container parameters are invalid
            BadResponseError: If response format is invalid
        """
        # If the folder object is empty, raise exception
        if folder == "":
            raise EmptyFieldError(
                message="Field 'folder' cannot be empty",
                error_code="API_I00035",
                details=['"folder" is not allowed to be empty'],  # noqa
            )

        # Set the parameters, starting with a high limit for more than the default 200
        params = {"limit": self.DEFAULT_LIMIT}

        # Build the configuration container object (folder, snippet, or device)
        container_parameters = self._build_container_params(
            folder,
            snippet,
            device,
        )

        # Ensure that we have only a single instance of "folder", "device", or "snippet"
        if len(container_parameters) != 1:
            raise ValidationError(
                "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            )

        # Add the resulting container object to our parameters
        params.update(container_parameters)

        # Perform our request
        try:
            response = self.api_client.get(
                self.ENDPOINT,
                params=params,
            )

            # return errors if invalid structure
            if not isinstance(response, dict):
                raise BadResponseError("Invalid response format: expected dictionary")

            if "data" not in response:
                raise BadResponseError("Invalid response format: missing 'data' field")

            if not isinstance(response["data"], list):
                raise BadResponseError(
                    "Invalid response format: 'data' field must be a list"
                )

            # Return a list object of the entries as Pydantic modeled objects
            applications = [
                ApplicationResponseModel(**item) for item in response["data"]
            ]

            # Apply client-side filtering
            return self._apply_filters(applications, filters)

        # Forward exceptions to our custom ErrorHandler object
        except Exception as e:
            if hasattr(e, "response") and e.response is not None:  # noqa
                ErrorHandler.raise_for_error(e.response.json())
            raise

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
            EmptyFieldError: If name or container fields are empty
            FolderNotFoundError: If the specified folder doesn't exist
            ObjectNotPresentError: If the object is not found
            ValidationError: If the parameters are invalid
            BadResponseError: For other API-related errors
        """
        if not name:
            raise EmptyFieldError(
                message="Field 'name' cannot be empty",
                error_code="API_I00035",
                details=['"name" is not allowed to be empty'],  # noqa
            )

        if folder == "":
            raise EmptyFieldError(
                message="Field 'folder' cannot be empty",
                error_code="API_I00035",
                details=['"folder" is not allowed to be empty'],  # noqa
            )

        # Build the configuration container object (folder, snippet, or device)
        container_parameters = self._build_container_params(
            folder,
            snippet,
            device,
        )

        # Ensure that we have only a single instance of "folder", "device", or "snippet"
        if len(container_parameters) != 1:
            raise ValidationError(
                "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            )

        # Start with container parameters
        params = container_parameters

        # Add name parameter
        params["name"] = name

        try:
            response = self.api_client.get(
                self.ENDPOINT,
                params=params,
            )

            # return errors if invalid structure
            if not isinstance(response, dict):
                raise BadResponseError("Invalid response format: expected dictionary")

            # If the response has a key of "_errors", pass to our custom error handler
            if "_errors" in response:
                ErrorHandler.raise_for_error(response)

            # If the response has a key of "id"
            elif "id" in response:
                # Create a new object by passing the response through our Pydantic model
                application = ApplicationResponseModel(**response)

                # Return an instance of the object as a Python dictionary
                return application.model_dump(
                    exclude_unset=True,
                    exclude_none=True,
                )

            else:
                raise BadResponseError("Invalid response format: missing 'id' field")

        except Exception as e:
            if hasattr(e, "response") and e.response is not None:  # noqa
                ErrorHandler.raise_for_error(e.response.json())
            raise

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
            MalformedRequestError: If the request is malformed
        """
        try:
            endpoint = f"{self.ENDPOINT}/{object_id}"
            self.api_client.delete(endpoint)

        except Exception as e:
            if hasattr(e, "response") and e.response is not None:  # noqa
                ErrorHandler.raise_for_error(e.response.json())
            raise
