# scm/config/objects/service.py

# Standard library imports
import logging
from typing import List, Dict, Any, Optional

# External libraries
from requests import Response
from requests.exceptions import HTTPError

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
    ErrorHandler,
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

        Raises:
            Custom Error Handling class response
        """
        try:
            # Use the dictionary "data" to pass into Pydantic and return a modeled object
            service = ServiceCreateModel(**data)

            # Convert back to a Python dictionary, removing any unset fields
            payload = service.model_dump(exclude_unset=True)

            # Send the updated object to the remote API as JSON
            response = self.api_client.post(
                self.ENDPOINT,
                json=payload,
            )

            # Extract JSON data from the response
            response_data = response.json()

            # Return the SCM API response as a new Pydantic object
            return ServiceResponseModel(**response_data)

        except HTTPError as e:
            response: Optional[Response] = e.response
            if response is not None and response.content:
                ErrorHandler.raise_for_error(
                    response.json(),
                    response.status_code,
                )
            else:
                self.logger.error("No response content available for error parsing.")
                raise

    def get(
        self,
        object_id: str,
    ) -> ServiceResponseModel:
        """
        Gets a service object by ID.

        Returns:
            ServiceResponseModel

        Raises:
            Custom Error Handling class response
        """
        try:
            # Send the request to the remote API
            endpoint = f"{self.ENDPOINT}/{object_id}"
            response = self.api_client.get(endpoint)

            # Extract JSON data from the response
            response_data = response.json()

            # Return the SCM API response as a new Pydantic object
            return ServiceResponseModel(**response_data)

        except HTTPError as e:
            response: Optional[Response] = e.response
            if response is not None and response.content:
                ErrorHandler.raise_for_error(
                    response.json(),
                    response.status_code,
                )
            else:
                self.logger.error("No response content available for error parsing.")
                raise

    def update(
        self,
        data: Dict[str, Any],
    ) -> ServiceResponseModel:
        """
        Updates an existing service object.

        Returns:
            ServiceResponseModel

        Raises:
            Custom Error Handling class response
        """
        try:
            # Use the dictionary "data" to pass into Pydantic and return a modeled object
            service = ServiceUpdateModel(**data)

            # Convert back to a Python dictionary, removing any unset fields
            payload = service.model_dump(exclude_unset=True)

            # Send the updated object to the remote API as JSON
            endpoint = f"{self.ENDPOINT}/{data['id']}"
            response = self.api_client.put(
                endpoint,
                json=payload,
            )

            # Extract JSON data from the response
            response_data = response.json()

            # Return the SCM API response as a new Pydantic object
            return ServiceResponseModel(**response_data)

        except HTTPError as e:
            response: Optional[Response] = e.response
            if response is not None and response.content:
                ErrorHandler.raise_for_error(
                    response.json(),
                    response.status_code,
                )
            else:
                self.logger.error("No response content available for error parsing.")
                raise

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

        Raises:
            InvalidObjectError: If filter criteria are invalid
        """

        filter_criteria = services

        # Filter by protocol
        if "protocol" in filters:
            if not isinstance(filters["protocol"], list):
                raise InvalidObjectError("'protocol' filter must be a list")
            protocols = filters["protocol"]
            filter_criteria = [
                svc
                for svc in filter_criteria
                if any(getattr(svc.protocol, proto) is not None for proto in protocols)
            ]

        # Filter by tag
        if "tag" in filters:
            if not isinstance(filters["tag"], list):
                raise InvalidObjectError("'tag' filter must be a list")
            tags = filters["tag"]
            filter_criteria = [
                svc
                for svc in filter_criteria
                if svc.tag and any(tag in svc.tag for tag in tags)
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
                raise InvalidObjectError(
                    "Invalid response format: expected dictionary",
                    error_code="E003",
                    http_status_code=500,
                )

            if "data" not in response:
                raise InvalidObjectError(
                    "Invalid response format: missing 'data' field",
                    error_code="E003",
                    http_status_code=500,
                )

            if not isinstance(response["data"], list):
                raise InvalidObjectError(
                    "Invalid response format: 'data' field must be a list",
                    error_code="E003",
                    http_status_code=500,
                )

            addresses = [ServiceResponseModel(**item) for item in response["data"]]

            return self._apply_filters(
                addresses,
                filters,
            )

        except HTTPError as e:
            response: Optional[Response] = e.response
            if response is not None and response.content:
                ErrorHandler.raise_for_error(
                    response.json(),
                    response.status_code,
                )
            else:
                self.logger.error("No response content available for error parsing.")
                raise

    def fetch(
        self,
        name: str,
        folder: Optional[str] = None,
        snippet: Optional[str] = None,
        device: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Fetches a single service by name.

        Args:
            name (str): The name of the service to fetch.
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
                raise InvalidObjectError(
                    "Invalid response format: expected dictionary",
                    error_code="E003",
                    http_status_code=500,
                )

            if "_errors" in response:
                ErrorHandler.raise_for_error(
                    response,
                    http_status_code=400,
                )

            if "id" in response:
                address = ServiceResponseModel(**response)
                return address.model_dump(
                    exclude_unset=True,
                    exclude_none=True,
                )
            else:
                raise InvalidObjectError(
                    "Invalid response format: missing 'id' field",
                    error_code="E003",
                    http_status_code=500,
                )

        except HTTPError as e:
            response: Optional[Response] = e.response
            if response is not None and response.content:
                ErrorHandler.raise_for_error(
                    response.json(),
                    response.status_code,
                )
            else:
                self.logger.error("No response content available for error parsing.")
                raise

    def delete(
        self,
        object_id: str,
    ) -> None:
        """
        Deletes a service object.

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

        except HTTPError as e:
            response: Optional[Response] = e.response
            if response is not None and response.content:
                ErrorHandler.raise_for_error(
                    response.json(),
                    response.status_code,
                )
            else:
                self.logger.error("No response content available for error parsing.")
                raise
