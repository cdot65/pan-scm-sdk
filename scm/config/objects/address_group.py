# scm/config/objects/address_group.py

from typing import List, Dict, Any, Optional
from scm.config import BaseObject
from scm.models.objects import (
    AddressGroupCreateModel,
    AddressGroupResponseModel,
    AddressGroupUpdateModel,
)
from scm.exceptions import (
    ValidationError,
    EmptyFieldError,
    ErrorHandler,
    BadResponseError,
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

    def create(
        self,
        data: Dict[str, Any],
    ) -> AddressGroupResponseModel:
        """
        Creates a new address group object.

        Returns:
            AddressResponseModel

        Raises:
            Custom Error Handling class response
        """
        try:

            # Use the dictionary "data" to pass into Pydantic and return a modeled object
            address_group = AddressGroupCreateModel(**data)

            # Convert back to a Python dictionary, but removing any excluded object
            payload = address_group.model_dump(exclude_unset=True)

            # Send the updated object to the remote API as JSON
            response = self.api_client.post(self.ENDPOINT, json=payload)

            # Return the SCM API response as a new Pydantic object
            return AddressGroupResponseModel(**response)

        # Forward exceptions to our custom ErrorHandler object
        except Exception as e:
            if hasattr(e, "response") and e.response is not None:  # noqa
                ErrorHandler.raise_for_error(e.response.json())
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
            response = self.api_client.get(endpoint)

            # Return the SCM API response as a new Pydantic object
            return AddressGroupResponseModel(**response)

        # Forward exceptions to our custom ErrorHandler object
        except Exception as e:
            if hasattr(e, "response") and e.response is not None:  # noqa
                ErrorHandler.raise_for_error(e.response.json())
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

            # Convert back to a Python dictionary, but removing any excluded object
            payload = address.model_dump(exclude_unset=True)

            # Send the updated object to the remote API as JSON
            endpoint = f"{self.ENDPOINT}/{data['id']}"
            response = self.api_client.put(endpoint, json=payload)

            # Return the SCM API response as a new Pydantic object
            return AddressGroupResponseModel(**response)

        # Forward exceptions to our custom ErrorHandler object
        except Exception as e:
            if hasattr(e, "response") and e.response is not None:  # noqa
                ErrorHandler.raise_for_error(e.response.json())
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
        """

        # Build a list of what criteria we are looking to filter our response from
        filtered_groups = address_groups

        # Perform filtering if the presence of "types" is found within the filters
        if "types" in filters:
            if not isinstance(filters["types"], list):
                raise ValidationError("'types' filter must be a list")

            types = filters["types"]
            filtered_groups = [
                group
                for group in filtered_groups
                if any(
                    getattr(group, field) is not None
                    for field in ["static", "dynamic"]
                    if field in types
                )
            ]

        # Perform filtering if the presence of "values" is found within the filters
        if "values" in filters:
            if not isinstance(filters["values"], list):
                raise ValidationError("'values' filter must be a list")

            values = filters["values"]
            filtered_groups = [
                group
                for group in filtered_groups
                if (group.static and any(value in group.static for value in values))
                or (group.dynamic and group.dynamic.filter in values)
            ]

        # Perform filtering if the presence of "tags" is found within the filters
        if "tags" in filters:
            if not isinstance(filters["tags"], list):
                raise ValidationError("'tags' filter must be a list")

            tags = filters["tags"]
            filtered_groups = [
                group
                for group in filtered_groups
                if group.tag and any(tag in group.tag for tag in tags)
            ]

        return filtered_groups

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
                - tags: List[str] - Filter by tags
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
            address_groups = [
                AddressGroupResponseModel(**item) for item in response["data"]
            ]

            # Apply client-side filtering
            return self._apply_filters(address_groups, filters)

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
        Fetches a single address group by name.

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
                address = AddressGroupResponseModel(**response)

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
