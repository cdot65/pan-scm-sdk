# scm/config/objects/address_group.py

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
    AddressGroupCreateModel,
    AddressGroupResponseModel,
    AddressGroupUpdateModel,
)


class AddressGroup(BaseObject):
    """
    Manages Address Group objects in Palo Alto Networks' Strata Cloud Manager.
    """

    ENDPOINT = "/config/objects/v1/address-groups"
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
    ) -> AddressGroupResponseModel:
        """
        Creates a new address group object.

        Returns:
            AddressGroupResponseModel

        Raises:
            Custom Error Handling class response
        """
        try:
            # Use the dictionary "data" to pass into Pydantic and return a modeled object
            address_group = AddressGroupCreateModel(**data)

            # Convert back to a Python dictionary, removing any unset fields
            payload = address_group.model_dump(exclude_unset=True)

            # Send the updated object to the remote API as JSON, expecting a dictionary object to be returned.
            response: Dict[str, Any] = self.api_client.post(
                self.ENDPOINT,
                json=payload,
            )

            # Return the SCM API response as a new Pydantic object
            return AddressGroupResponseModel(**response)

        except HTTPError as e:
            # create an object of the type Response and store the contents of e.response within it
            response: Optional[Response] = e.response

            # if the response is not none, and there is data within response.content
            if response is not None and response.content:

                # Perform our custom exception handler by sending the response.json() object and http status code
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
    ) -> AddressGroupResponseModel:
        """
        Gets an address group object by ID.

        Returns:
            AddressGroupResponseModel

        Raises:
            Custom Error Handling class response
        """
        try:
            # Send the request to the remote API
            endpoint = f"{self.ENDPOINT}/{object_id}"
            response: Dict[str, Any] = self.api_client.get(endpoint)

            # Return the SCM API response as a new Pydantic object
            return AddressGroupResponseModel(**response)

        except HTTPError as e:
            # create an object of the type Response and store the contents of e.response within it
            response: Optional[Response] = e.response

            # if the response is not none, and there is data within response.content
            if response is not None and response.content:

                # Perform our custom exception handler by sending the response.json() object and http status code
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
    ) -> AddressGroupResponseModel:
        """
        Updates an existing address group object.

        Returns:
            AddressGroupResponseModel

        Raises:
            Custom Error Handling class response
        """
        try:
            # Use the dictionary "data" to pass into Pydantic and return a modeled object
            address = AddressGroupUpdateModel(**data)

            # Convert back to a Python dictionary, removing any unset fields
            payload = address.model_dump(exclude_unset=True)

            # Send the updated object to the remote API as JSON
            endpoint = f"{self.ENDPOINT}/{data['id']}"
            response: Dict[str, Any] = self.api_client.put(
                endpoint,
                json=payload,
            )

            # Return the SCM API response as a new Pydantic object
            return AddressGroupResponseModel(**response)

        except HTTPError as e:
            # create an object of the type Response and store the contents of e.response within it
            response: Optional[Response] = e.response

            # if the response is not none, and there is data within response.content
            if response is not None and response.content:

                # Perform our custom exception handler by sending the response.json() object and http status code
                ErrorHandler.raise_for_error(
                    response.json(),
                    response.status_code,
                )
            else:
                self.logger.error("No response content available for error parsing.")
                raise

    @staticmethod
    def _apply_filters(
        address_groups: List[AddressGroupResponseModel],
        filters: Dict[str, Any],
    ) -> List[AddressGroupResponseModel]:
        """
        Apply client-side filtering to the list of address groups.

        Args:
            address_groups: List of AddressGroupResponseModel objects
            filters: Dictionary of filter criteria

        Returns:
            List[AddressGroupResponseModel]: Filtered list of address groups

        Raises:
            InvalidObjectError: If filter criteria are invalid
        """

        filter_criteria = address_groups

        # Filter by types
        if "types" in filters:
            if not isinstance(filters["types"], list):
                raise InvalidObjectError(
                    message="'types' filter must be a list",
                    error_code="E003",
                    http_status_code=500,
                    details={"errorType": "Invalid Object"},
                )
            types = filters["types"]
            filter_criteria = [
                group
                for group in filter_criteria
                if any(
                    getattr(group, field) is not None
                    for field in ["static", "dynamic"]
                    if field in types
                )
            ]

        # Filter by values
        if "values" in filters:
            if not isinstance(filters["values"], list):
                raise InvalidObjectError(
                    message="'values' filter must be a list",
                    error_code="E003",
                    http_status_code=500,
                    details={"errorType": "Invalid Object"},
                )
            values = filters["values"]
            filter_criteria = [
                group
                for group in filter_criteria
                if (group.static and any(value in group.static for value in values))
                or (group.dynamic and group.dynamic.filter in values)
            ]

        # Filter by tags
        if "tags" in filters:
            if not isinstance(filters["tags"], list):
                raise InvalidObjectError(
                    message="'tags' filter must be a list",
                    error_code="E003",
                    http_status_code=500,
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
    ) -> List[AddressGroupResponseModel]:
        """
        Lists address group objects with optional filtering.

        Args:
            folder: Optional folder name
            snippet: Optional snippet name
            device: Optional device name
            **filters: Additional filters including:
                - types: List[str] - Filter by group types (e.g., ['static', 'dynamic'])
                - values: List[str] - Filter by group values
                - tags: List[str] - Filter by tags (e.g., ['Automation'])

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

            address_groups = [
                AddressGroupResponseModel(**item) for item in response["data"]
            ]
            return self._apply_filters(
                address_groups,
                filters,
            )

        except HTTPError as e:
            # create an object of the type Response and store the contents of e.response within it
            response: Optional[Response] = e.response

            # if the response is not none, and there is data within response.content
            if response is not None and response.content:

                # Perform our custom exception handler by sending the response.json() object and http status code
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
        Fetches a single address group by name.

        Args:
            name (str): The name of the address group to fetch.
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

            if "id" in response:
                address = AddressGroupResponseModel(**response)
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
            # create an object of the type Response and store the contents of e.response within it
            response: Optional[Response] = e.response

            # if the response is not none, and there is data within response.content
            if response is not None and response.content:

                # Perform our custom exception handler by sending the response.json() object and http status code
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
        Deletes an address group object.

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
            # create an object of the type Response and store the contents of e.response within it
            response: Optional[Response] = e.response

            # if the response is not none, and there is data within response.content
            if response is not None and response.content:

                # Perform our custom exception handler by sending the response.json() object and http status code
                ErrorHandler.raise_for_error(
                    response.json(),
                    response.status_code,
                )
            else:
                self.logger.error("No response content available for error parsing.")
                raise
