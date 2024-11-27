# scm/config/objects/application_group.py

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
    ApplicationGroupCreateModel,
    ApplicationGroupResponseModel,
    ApplicationGroupUpdateModel,
)


class ApplicationGroup(BaseObject):
    """
    Manages Application Group objects in Palo Alto Networks' Strata Cloud Manager.
    """

    ENDPOINT = "/config/objects/v1/application-groups"
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
    ) -> ApplicationGroupResponseModel:
        """
        Creates a new application group object.

        Returns:
            ApplicationGroupResponseModel
        """
        # Use the dictionary "data" to pass into Pydantic and return a modeled object
        app_group = ApplicationGroupCreateModel(**data)

        # Convert back to a Python dictionary, removing any unset fields
        payload = app_group.model_dump(exclude_unset=True)

        # Send the updated object to the remote API as JSON, expecting a dictionary object to be returned.
        response: Dict[str, Any] = self.api_client.post(
            self.ENDPOINT,
            json=payload,
        )

        # Return the SCM API response as a new Pydantic object
        return ApplicationGroupResponseModel(**response)

    def get(
        self,
        object_id: str,
    ) -> ApplicationGroupResponseModel:
        """
        Gets an application group object by ID.

        Returns:
            ApplicationGroupResponseModel
        """
        # Send the request to the remote API
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.get(endpoint)

        # Return the SCM API response as a new Pydantic object
        return ApplicationGroupResponseModel(**response)

    def update(
        self,
        app_group: ApplicationGroupUpdateModel,
    ) -> ApplicationGroupResponseModel:
        """
        Updates an existing application group object.

        Args:
            app_group: ApplicationGroupUpdateModel instance containing the update data

        Returns:
            ApplicationGroupResponseModel
        """
        # Convert to dict for API request, excluding unset fields
        payload = app_group.model_dump(exclude_unset=True)

        # Extract ID and remove from payload since it's in the URL
        object_id = str(app_group.id)
        payload.pop("id", None)

        # Send the updated object to the remote API as JSON
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.put(
            endpoint,
            json=payload,
        )

        # Return the SCM API response as a new Pydantic model
        return ApplicationGroupResponseModel(**response)

    @staticmethod
    def _apply_filters(
        app_groups: List[ApplicationGroupResponseModel],
        filters: Dict[str, Any],
    ) -> List[ApplicationGroupResponseModel]:
        """
        Apply client-side filtering to the list of application groups.

        Args:
            app_groups: List of ApplicationGroupResponseModel objects
            filters: Dictionary of filter criteria

        Returns:
            List[ApplicationGroupResponseModel]: Filtered list of application groups
        """
        filter_criteria = app_groups

        # Filter by members
        if "members" in filters:
            if not isinstance(filters["members"], list):
                raise InvalidObjectError(
                    message="'members' filter must be a list",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Object"},
                )
            members = filters["members"]
            filter_criteria = [
                group
                for group in filter_criteria
                if group.members and any(member in group.members for member in members)
            ]

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
    ) -> List[ApplicationGroupResponseModel]:
        """
        Lists application group objects with optional filtering.

        Args:
            folder: Optional folder name
            snippet: Optional snippet name
            device: Optional device name
            **filters: Additional filters including:
                - members: List[str] - Filter by member applications
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

        params = {"limit": self.DEFAULT_LIMIT}

        container_parameters = self._build_container_params(
            folder,
            snippet,
            device,
        )

        if len(container_parameters) != 1:
            raise InvalidObjectError(
                message="Exactly one of 'folder', 'snippet', or 'device' must be provided.",
                error_code="E003",
                http_status_code=400,
                details={"error": "Invalid container parameters"},
            )

        params.update(container_parameters)

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

        addresses = [ApplicationGroupResponseModel(**item) for item in response["data"]]

        return self._apply_filters(
            addresses,
            filters,
        )

    def fetch(
        self,
        name: str,
        folder: Optional[str] = None,
        snippet: Optional[str] = None,
        device: Optional[str] = None,
    ) -> ApplicationGroupResponseModel:
        """
        Fetches a single application group by name.

        Args:
            name (str): The name of the application group to fetch.
            folder (str, optional): The folder in which the resource is defined.
            snippet (str, optional): The snippet in which the resource is defined.
            device (str, optional): The device in which the resource is defined.

        Returns:
            ApplicationGroupResponseModel: The fetched application group object as a Pydantic model.
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
            device,
        )

        if len(container_parameters) != 1:
            raise InvalidObjectError(
                message="Exactly one of 'folder', 'snippet', or 'device' must be provided.",
                error_code="E003",
                http_status_code=400,
                details={
                    "error": "Exactly one of 'folder', 'snippet', or 'device' must be provided."
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
            return ApplicationGroupResponseModel(**response)
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
        Deletes an application group object.

        Args:
            object_id (str): The ID of the object to delete.
        """
        endpoint = f"{self.ENDPOINT}/{object_id}"
        self.api_client.delete(endpoint)
