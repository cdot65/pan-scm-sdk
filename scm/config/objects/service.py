# scm/config/objects/service.py

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
    ServiceCreateModel,
    ServiceResponseModel,
    ServiceUpdateModel,
)


class Service(BaseObject):
    """
    Manages Service objects in Palo Alto Networks' Strata Cloud Manager.
    """

    ENDPOINT = "/config/objects/v1/services"
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
    ) -> ServiceResponseModel:
        """
        Creates a new service object.

        Returns:
            ServiceResponseModel
        """
        # Use the dictionary "data" to pass into Pydantic and return a modeled object
        service = ServiceCreateModel(**data)

        # Convert back to a Python dictionary, removing any unset fields
        payload = service.model_dump(exclude_unset=True)

        # Send the updated object to the remote API as JSON, expecting a dictionary response
        response: Dict[str, Any] = self.api_client.post(
            self.ENDPOINT,
            json=payload,
        )

        # Return the SCM API response as a new Pydantic object
        return ServiceResponseModel(**response)

    def get(
        self,
        object_id: str,
    ) -> ServiceResponseModel:
        """
        Gets a service object by ID.

        Returns:
            ServiceResponseModel
        """
        # Send the request to the remote API
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.get(endpoint)

        # Return the SCM API response as a new Pydantic object
        return ServiceResponseModel(**response)

    def update(
        self,
        service: ServiceUpdateModel,
    ) -> ServiceResponseModel:
        """
        Updates an existing service object.

        Args:
            service: ServiceUpdateModel instance containing the update data

        Returns:
            ServiceResponseModel
        """
        # Convert to dict for API request, excluding unset fields
        payload = service.model_dump(exclude_unset=True)

        # Extract ID and remove from payload since it's in the URL
        object_id = str(service.id)
        payload.pop("id", None)

        # Send the updated object to the remote API as JSON
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.put(
            endpoint,
            json=payload,
        )

        # Return the SCM API response as a new Pydantic model
        return ServiceResponseModel(**response)

    @staticmethod
    def _apply_filters(
        services: List[ServiceResponseModel],
        filters: Dict[str, Any],
    ) -> List[ServiceResponseModel]:
        """
        Apply client-side filtering to the list of services.

        Args:
            services: List of ServiceResponseModel objects
            filters: Dictionary of filter criteria

        Returns:
            List[ServiceResponseModel]: Filtered list of services
        """
        filter_criteria = services

        # Filter by protocols
        if "protocols" in filters:
            if not isinstance(filters["protocols"], list):
                raise InvalidObjectError(
                    message="'protocols' filter must be a list",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Object"},
                )
            protocols = filters["protocols"]
            filter_criteria = [
                service
                for service in filter_criteria
                if any(
                    protocol_type in service.protocol.model_dump(exclude_none=True)
                    for protocol_type in protocols
                )
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
                addr
                for addr in filter_criteria
                if addr.tag and any(tag in addr.tag for tag in tags)
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
    ) -> List[ServiceResponseModel]:
        """
        Lists service objects with optional filtering.

        Args:
            folder: Optional folder name
            snippet: Optional snippet name
            device: Optional device name
            **filters: Additional filters including:
                - protocol: List[str] - Filter by protocol type (e.g., ['tcp', 'udp'])
                - tag: List[str] - Filter by tags
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

        services = [ServiceResponseModel(**item) for item in response["data"]]
        return self._apply_filters(
            services,
            filters,
        )

    def fetch(
        self,
        name: str,
        folder: Optional[str] = None,
        snippet: Optional[str] = None,
        device: Optional[str] = None,
    ) -> ServiceResponseModel:
        """
        Fetches a single service by name.

        Args:
            name (str): The name of the service to fetch.
            folder (str, optional): The folder in which the resource is defined.
            snippet (str, optional): The snippet in which the resource is defined.
            device (str, optional): The device in which the resource is defined.

        Returns:
            ServiceResponseModel: The fetched service object as a Pydantic model.
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
            return ServiceResponseModel(**response)
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
        Deletes a service object.

        Args:
            object_id (str): The ID of the object to delete.
        """
        endpoint = f"{self.ENDPOINT}/{object_id}"
        self.api_client.delete(endpoint)
