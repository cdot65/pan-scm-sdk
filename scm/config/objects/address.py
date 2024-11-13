# scm/config/objects/address.py

from typing import List, Dict, Any, Optional
import logging
from scm.config import BaseObject
from scm.models.objects import (
    AddressCreateModel,
    AddressResponseModel,
    AddressUpdateModel,
)
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
    ErrorHandler,
    APIError,
)
from scm.utils.logging import setup_logger


class Address(BaseObject):
    """
    Manages Address objects in Palo Alto Networks' Strata Cloud Manager.
    """

    ENDPOINT = "/config/objects/v1/addresses"
    DEFAULT_LIMIT = 10000

    def __init__(
        self,
        api_client,
        log_level: int = logging.ERROR,
    ):
        super().__init__(api_client)
        self.logger = setup_logger(__name__, log_level=log_level)

    def create(
        self,
        data: Dict[str, Any],
    ) -> AddressResponseModel:
        """
        Creates a new address object.

        Returns:
            AddressResponseModel

        Raises:
            Custom Error Handling class response
        """
        try:
            # Use the dictionary "data" to pass into Pydantic and return a modeled object
            address = AddressCreateModel(**data)

            # Convert back to a Python dictionary, removing any unset fields
            payload = address.model_dump(exclude_unset=True)

            # Send the updated object to the remote API as JSON
            response = self.api_client.post(self.ENDPOINT, json=payload)

            # Return the SCM API response as a new Pydantic object
            return AddressResponseModel(**response)

        except Exception as e:
            if isinstance(e, APIError):
                self.logger.error(f"API error while creating address: {e}")
                raise
            else:
                self.logger.error(
                    f"An unexpected error occurred while creating address: {e}"
                )
                raise APIError("An unexpected error occurred") from e

    def get(
        self,
        object_id: str,
    ) -> AddressResponseModel:
        """
        Gets an address object by ID.

        Returns:
            AddressResponseModel

        Raises:
            Custom Error Handling class response
        """
        try:
            # Send the request to the remote API
            endpoint = f"{self.ENDPOINT}/{object_id}"
            response = self.api_client.get(endpoint)

            # Return the SCM API response as a new Pydantic object
            return AddressResponseModel(**response)

        except Exception as e:
            self.logger.error(f"Error getting address: {e}", exc_info=True)
            if hasattr(e, "response") and e.response is not None:
                ErrorHandler.raise_for_error(e.response.json(), e.response.status_code)
            else:
                raise APIError(f"An unexpected error occurred: {e}") from e

    def update(
        self,
        data: Dict[str, Any],
    ) -> AddressResponseModel:
        """
        Updates an existing address object.

        Returns:
            AddressResponseModel

        Raises:
            Custom Error Handling class response
        """
        try:
            # Use the dictionary "data" to pass into Pydantic and return a modeled object
            address = AddressUpdateModel(**data)

            # Convert back to a Python dictionary, removing any unset fields
            payload = address.model_dump(exclude_unset=True)

            # Send the updated object to the remote API as JSON
            endpoint = f"{self.ENDPOINT}/{data['id']}"
            response = self.api_client.put(endpoint, json=payload)

            # Return the SCM API response as a new Pydantic object
            return AddressResponseModel(**response)

        except Exception as e:
            self.logger.error(f"Error updating address: {e}", exc_info=True)
            if hasattr(e, "response") and e.response is not None:
                ErrorHandler.raise_for_error(e.response.json(), e.response.status_code)
            else:
                raise APIError(f"An unexpected error occurred: {e}") from e

    @staticmethod
    def _apply_filters(
        addresses: List[AddressResponseModel],
        filters: Dict[str, Any],
    ) -> List[AddressResponseModel]:
        """
        Apply client-side filtering to the list of addresses.

        Args:
            addresses: List of AddressResponseModel objects
            filters: Dictionary of filter criteria

        Returns:
            List[AddressResponseModel]: Filtered list of addresses
        """

        filter_criteria = addresses

        # Filter by types
        if "types" in filters:
            if not isinstance(filters["types"], list):
                raise InvalidObjectError("'types' filter must be a list")
            types = filters["types"]
            filter_criteria = [
                addr
                for addr in filter_criteria
                if any(
                    getattr(addr, field) is not None
                    for field in ["ip_netmask", "ip_range", "ip_wildcard", "fqdn"]
                    if field.replace("ip_", "") in types
                )
            ]

        # Filter by values
        if "values" in filters:
            if not isinstance(filters["values"], list):
                raise InvalidObjectError("'values' filter must be a list")
            values = filters["values"]
            filter_criteria = [
                addr
                for addr in filter_criteria
                if any(
                    getattr(addr, field) in values
                    for field in ["ip_netmask", "ip_range", "ip_wildcard", "fqdn"]
                    if getattr(addr, field) is not None
                )
            ]

        # Filter by tags
        if "tags" in filters:
            if not isinstance(filters["tags"], list):
                raise InvalidObjectError("'tags' filter must be a list")
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
    ) -> List[AddressResponseModel]:
        """
        Lists address objects with optional filtering.

        Args:
            folder: Optional folder name
            snippet: Optional snippet name
            device: Optional device name
            **filters: Additional filters including:
                - types: List[str] - Filter by address types (e.g., ['netmask', 'range'])
                - values: List[str] - Filter by address values (e.g., ['10.0.0.0/24'])
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
                details=['"folder" is not allowed to be empty'],
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

            addresses = [AddressResponseModel(**item) for item in response["data"]]

            return self._apply_filters(addresses, filters)

        except Exception as e:
            if isinstance(e, APIError):
                # Already an APIError, re-raise it without logging traceback again
                self.logger.error(f"API error while listing addresses: {e}")
                raise
            else:
                # Log the unexpected exception and raise a new APIError
                self.logger.error(
                    f"An unexpected error occurred while listing addresses: {e}"
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
        Fetches a single object by name.

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
                details=['"name" is not allowed to be empty'],
            )

        if folder == "":
            raise MissingQueryParameterError(
                message="Field 'folder' cannot be empty",
                error_code="E003",
                http_status_code=400,
                details=['"folder" is not allowed to be empty'],
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
                address = AddressResponseModel(**response)
                return address.model_dump(
                    exclude_unset=True,
                    exclude_none=True,
                )
            else:
                raise APIError(
                    "Invalid response format: missing 'id' field",
                    http_status_code=500,
                )

        except Exception as e:
            self.logger.error(f"Error fetching address: {e}", exc_info=True)
            if hasattr(e, "response") and e.response is not None:
                ErrorHandler.raise_for_error(e.response.json(), e.response.status_code)
            else:
                raise APIError(f"An unexpected error occurred: {e}") from e

    def delete(
        self,
        object_id: str,
    ) -> None:
        """
        Deletes an address object.

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
            self.logger.error(f"Error deleting address: {e}", exc_info=True)
            if hasattr(e, "response") and e.response is not None:
                ErrorHandler.raise_for_error(e.response.json(), e.response.status_code)
            else:
                raise APIError(f"An unexpected error occurred: {e}") from e
