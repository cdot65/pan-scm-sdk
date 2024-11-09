# scm/config/objects/address.py

from typing import List, Dict, Any, Optional
from scm.config import BaseObject
from scm.models.objects import (
    AddressCreateModel,
    AddressResponseModel,
    AddressUpdateModel,
)
from scm.exceptions import (
    ValidationError,
    EmptyFieldError,
    APIError,
    ErrorHandler,
    BadResponseError,
)


class Address(BaseObject):
    """
    Manages Address objects in Palo Alto Networks' Strata Cloud Manager.
    """

    ENDPOINT = "/config/objects/v1/addresses"
    DEFAULT_LIMIT = 10000

    def __init__(
        self,
        api_client,
    ):
        super().__init__(api_client)

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

            # Convert back to a Python dictionary, but removing any excluded object
            payload = address.model_dump(exclude_unset=True)

            # Send the updated object to the remote API as JSON
            response = self.api_client.post(self.ENDPOINT, json=payload)

            # Return the SCM API response as a new Pydantic object
            return AddressResponseModel(**response)

        # Forward exceptions to our custom ErrorHandler object
        except Exception as e:
            if hasattr(e, "response") and e.response is not None:  # noqa
                ErrorHandler.raise_for_error(e.response.json())
            raise

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

        # Forward exceptions to our custom ErrorHandler object
        except Exception as e:
            if hasattr(e, "response") and e.response is not None:  # noqa
                ErrorHandler.raise_for_error(e.response.json())
            raise

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

            # Convert back to a Python dictionary, but removing any excluded object
            payload = address.model_dump(exclude_unset=True)

            # Send the updated object to the remote API as JSON
            endpoint = f"{self.ENDPOINT}/{data['id']}"
            response = self.api_client.put(endpoint, json=payload)

            # Return the SCM API response as a new Pydantic object
            return AddressResponseModel(**response)

        # Forward exceptions to our custom ErrorHandler object
        except Exception as e:
            if hasattr(e, "response") and e.response is not None:  # noqa
                ErrorHandler.raise_for_error(e.response.json())
            raise

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

        # Build a list of what criteria we are looking to filter our response from
        filter_criteria = addresses

        # Perform filtering if the presence of "types" is found within the filters
        if "types" in filters:
            if not isinstance(filters["types"], list):
                raise ValidationError("'types' filter must be a list")

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

        # Perform filtering if the presence of "values" is found within the filters
        if "values" in filters:
            if not isinstance(filters["values"], list):
                raise ValidationError("'values' filter must be a list")

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

        # Perform filtering if the presence of "tags" is found within the filters
        if "tags" in filters:
            if not isinstance(filters["tags"], list):
                raise ValidationError("'tags' filter must be a list")

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
            EmptyFieldError: If provided container fields are empty
            FolderNotFoundError: If the specified folder doesn't exist
            ValidationError: If the container parameters are invalid
            APIError: If response format is invalid
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
                raise APIError("Invalid response format: expected dictionary")

            if "data" not in response:
                raise APIError("Invalid response format: missing 'data' field")

            if not isinstance(response["data"], list):
                raise APIError("Invalid response format: 'data' field must be a list")

            # Return a list object of the entries as Pydantic modeled objects
            addresses = [AddressResponseModel(**item) for item in response["data"]]

            # Apply client-side filtering
            return self._apply_filters(addresses, filters)

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
        Fetches a single object by name.

        Args:
            name (str): The name of the address group to fetch.
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
            APIError: For other API-related errors
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

        # Set the parameters, which will be empty for this type of request right now
        params = {}

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

        # Add name parameter
        params["name"] = name

        # Perform our request
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
                address = AddressResponseModel(**response)

                # Return an instance of the object as a Python dictionary
                # TODO:
                # move this model_dump logic into the update method.
                return address.model_dump(
                    exclude_unset=True,
                    exclude_none=True,
                )

            else:
                raise BadResponseError("Invalid response format: missing 'id' field")

        # Forward exceptions to our custom ErrorHandler object
        except Exception as e:
            if hasattr(e, "response") and e.response is not None:  # noqa
                ErrorHandler.raise_for_error(e.response.json())
            raise

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
            MalformedRequestError: If the request is malformed
        """

        # Perform our request
        try:
            endpoint = f"{self.ENDPOINT}/{object_id}"
            self.api_client.delete(endpoint)

        # Forward exceptions to our custom ErrorHandler object
        except Exception as e:
            if hasattr(e, "response") and e.response is not None:  # noqa
                ErrorHandler.raise_for_error(e.response.json())
            raise
