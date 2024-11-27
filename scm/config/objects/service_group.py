# scm/config/objects/service_group.py

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
    ServiceGroupCreateModel,
    ServiceGroupResponseModel,
    ServiceGroupUpdateModel,
)


class ServiceGroup(BaseObject):
    """
    Manages Service Group objects in Palo Alto Networks' Strata Cloud Manager.
    """

    ENDPOINT = "/config/objects/v1/service-groups"
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
    ) -> ServiceGroupResponseModel:
        """
        Creates a new service group object.

        Returns:
            ServiceGroupResponseModel
        """
        # Use the dictionary "data" to pass into Pydantic and return a modeled object
        service_group = ServiceGroupCreateModel(**data)

        # Convert back to a Python dictionary, removing any unset fields
        payload = service_group.model_dump(exclude_unset=True)

        # Send the updated object to the remote API as JSON, expecting a dictionary object to be returned.
        response: Dict[str, Any] = self.api_client.post(
            self.ENDPOINT,
            json=payload,
        )

        # Return the SCM API response as a new Pydantic object
        return ServiceGroupResponseModel(**response)

    def get(
        self,
        object_id: str,
    ) -> ServiceGroupResponseModel:
        """
        Gets a service group object by ID.

        Returns:
            ServiceGroupResponseModel
        """
        # Send the request to the remote API
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.get(endpoint)

        # Return the SCM API response as a new Pydantic object
        return ServiceGroupResponseModel(**response)

    def update(
        self,
        service_group: ServiceGroupUpdateModel,
    ) -> ServiceGroupResponseModel:
        """
        Updates an existing service group object.

        Args:
            service_group (ServiceGroupUpdateModel):

        Returns:
            ServiceGroupResponseModel
        """
        # Convert to dict for API request, excluding unset fields
        payload = service_group.model_dump(exclude_unset=True)

        # Extract ID and remove from payload since it's in the URL
        object_id = str(service_group.id)
        payload.pop("id", None)

        # Send the updated object to the remote API as JSON
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.put(
            endpoint,
            json=payload,
        )

        # Return the SCM API response as a new Pydantic object
        return ServiceGroupResponseModel(**response)

    @staticmethod
    def _apply_filters(
        service_groups: List[ServiceGroupResponseModel],
        filters: Dict[str, Any],
    ) -> List[ServiceGroupResponseModel]:
        """
        Apply client-side filtering to the list of service groups.

        Args:
            service_groups: List of ServiceGroupResponseModel objects
            filters: Dictionary of filter criteria

        Returns:
            List[ServiceGroupResponseModel]: Filtered list of service groups
        """

        filter_criteria = service_groups

        # Filter by values
        if "values" in filters:
            if not isinstance(filters["values"], list):
                raise InvalidObjectError(
                    message="'values' filter must be a list",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Object"},
                )
            values = filters["values"]
            filter_criteria = [
                group
                for group in filter_criteria
                if (group.members and any(value in group.members for value in values))
            ]

        # Filter by tags
        if "tags" in filters:
            if not isinstance(filters["tags"], list):
                raise InvalidObjectError(
                    message="'tags' filter must be a list",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Object"},
                )
            tags = filters["tags"]
            filter_criteria = [
                group
                for group in filter_criteria
                if group.tag and any(tag in group.tag for tag in tags)
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
    ) -> List[ServiceGroupResponseModel]:
        """
        Lists service group objects with optional filtering.

        Args:
            folder: Optional folder name
            snippet: Optional snippet name
            device: Optional device name
            **filters: Additional filters including:
                - values: List[str] - Filter by group values
                - tags: List[str] - Filter by tags (e.g., ['Automation'])
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
                "Exactly one of 'folder', 'snippet', or 'device' must be provided.",
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
                "Invalid response format: expected dictionary",
                error_code="E003",
                http_status_code=500,
                details={"error": "Response is not a dictionary"},
            )

        if "data" not in response:
            raise InvalidObjectError(
                "Invalid response format: missing 'data' field",
                error_code="E003",
                http_status_code=500,
                details={
                    "field": "data",
                    "error": '"data" field missing in the response',
                },
            )

        if not isinstance(response["data"], list):
            raise InvalidObjectError(
                "Invalid response format: 'data' field must be a list",
                error_code="E003",
                http_status_code=500,
                details={
                    "field": "data",
                    "error": '"data" field must be a list',
                },
            )

        service_groups = [
            ServiceGroupResponseModel(**item) for item in response["data"]
        ]

        return self._apply_filters(
            service_groups,
            filters,
        )

    def fetch(
        self,
        name: str,
        folder: Optional[str] = None,
        snippet: Optional[str] = None,
        device: Optional[str] = None,
    ) -> ServiceGroupResponseModel:
        """
        Fetches a single service group by name.

        Args:
            name (str): The name of the service group to fetch.
            folder (str, optional): The folder in which the resource is defined.
            snippet (str, optional): The snippet in which the resource is defined.
            device (str, optional): The device in which the resource is defined.

        Returns:
            ServiceGroupResponseModel
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
                "Exactly one of 'folder', 'snippet', or 'device' must be provided.",
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
                "Invalid response format: expected dictionary",
                error_code="E003",
                http_status_code=500,
                details={"error": "Response is not a dictionary"},
            )

        if "id" in response:
            return ServiceGroupResponseModel(**response)
        else:
            raise InvalidObjectError(
                "Invalid response format: missing 'id' field",
                error_code="E003",
                http_status_code=500,
                details={"error": "Response missing 'id' field"},
            )

    def delete(
        self,
        object_id: str,
    ) -> None:
        """
        Deletes a service group object.

        Args:
            object_id (str): The ID of the object to delete.

        """
        endpoint = f"{self.ENDPOINT}/{object_id}"
        self.api_client.delete(endpoint)
