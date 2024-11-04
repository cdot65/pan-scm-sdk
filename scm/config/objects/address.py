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
    ObjectNotPresentError,
)


class Address(BaseObject):
    """
    Manages Address objects in Palo Alto Networks' Strata Cloud Manager.
    """

    ENDPOINT = "/config/objects/v1/addresses"

    def __init__(self, api_client):
        super().__init__(api_client)

    def create(self, data: Dict[str, Any]) -> AddressResponseModel:
        """
        Creates a new address object.

        Raises:
            EmptyFieldError: If required fields are empty
            ObjectAlreadyExistsError: If an object with the same name already exists
            ValidationError: If the data is invalid
            FolderNotFoundError: If the specified folder doesn't exist
        """
        try:
            address = AddressCreateModel(**data)
            payload = address.model_dump(exclude_unset=True)
            response = self.api_client.post(self.ENDPOINT, json=payload)
            return AddressResponseModel(**response)
        except Exception as e:
            if hasattr(e, "response") and e.response is not None:  # noqa
                ErrorHandler.raise_for_error(e.response.json())
            raise

    def get(self, object_id: str) -> AddressResponseModel:
        """
        Gets an address object by ID.

        Raises:
            ObjectNotPresentError: If the object with given ID doesn't exist
            MalformedRequestError: If the request is malformed
        """
        try:
            endpoint = f"{self.ENDPOINT}/{object_id}"
            response = self.api_client.get(endpoint)
            return AddressResponseModel(**response)
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

        Raises:
            ObjectNotPresentError: If the object doesn't exist
            EmptyFieldError: If required fields are empty
            ValidationError: If the data is invalid
        """
        try:
            address = AddressUpdateModel(**data)
            payload = address.model_dump(exclude_unset=True)
            endpoint = f"{self.ENDPOINT}/{data['id']}"
            response = self.api_client.put(endpoint, json=payload)
            return AddressResponseModel(**response)
        except Exception as e:
            if hasattr(e, "response") and e.response is not None:  # noqa
                ErrorHandler.raise_for_error(e.response.json())
            raise

    def list(
        self,
        folder: Optional[str] = None,
        snippet: Optional[str] = None,
        device: Optional[str] = None,
        **filters,
    ) -> List[AddressResponseModel]:
        """
        Lists address objects with optional filtering.

        Raises:
            EmptyFieldError: If provided container fields are empty
            FolderNotFoundError: If the specified folder doesn't exist
            ValidationError: If the container parameters are invalid
            APIError: If response format is invalid
        """

        if folder == "":
            raise EmptyFieldError(
                message="Field 'folder' cannot be empty",
                error_code="API_I00035",
                details=['"folder" is not allowed to be empty'],  # noqa
            )

        params = {}
        container_params = {"folder": folder, "snippet": snippet, "device": device}
        provided_containers = {
            k: v for k, v in container_params.items() if v is not None
        }

        if len(provided_containers) != 1:
            raise ValidationError(
                "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            )

        params.update(provided_containers)  # noqa

        # Handle specific filters
        if "types" in filters:
            params["type"] = ",".join(filters["types"])
        if "values" in filters:
            params["value"] = ",".join(filters["values"])
        if "names" in filters:
            params["name"] = ",".join(filters["names"])
        if "tags" in filters:
            params["tag"] = ",".join(filters["tags"])

        params.update(
            {
                k: v
                for k, v in filters.items()
                if k
                not in [
                    "types",
                    "values",
                    "names",
                    "tags",
                    "folder",
                    "snippet",
                    "device",
                ]
            }
        )

        try:
            response = self.api_client.get(self.ENDPOINT, params=params)

            # Validate response format
            if not isinstance(response, dict):
                raise APIError("Invalid response format: expected dictionary")

            if "data" not in response:
                raise APIError("Invalid response format: missing 'data' field")

            if not isinstance(response["data"], list):
                raise APIError("Invalid response format: 'data' field must be a list")

            addresses = [AddressResponseModel(**item) for item in response["data"]]
            return addresses

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
        **filters,
    ) -> Dict[str, Any]:
        """
        Fetches a single object by name.

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

        params = {}
        container_params = {
            "folder": folder,
            "snippet": snippet,
            "device": device,
        }
        provided_containers = {
            k: v for k, v in container_params.items() if v is not None
        }

        if len(provided_containers) != 1:
            raise ValidationError(
                "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            )

        params.update(provided_containers)
        params["name"] = name

        params.update(
            {
                k: v
                for k, v in filters.items()
                if k
                not in [
                    "types",
                    "values",
                    "names",
                    "tags",
                    "folder",
                    "snippet",
                    "device",
                    "name",
                ]
            }
        )

        try:
            response = self.api_client.get(
                self.ENDPOINT,
                params=params,
            )
        except Exception as e:
            if hasattr(e, "response") and e.response is not None:  # noqa
                ErrorHandler.raise_for_error(e.response.json())
            raise

        if isinstance(response, dict):
            if "_errors" in response:
                ErrorHandler.raise_for_error(response)
            elif "id" in response:
                address = AddressResponseModel(**response)
                return address.model_dump(
                    exclude_unset=True,
                    exclude_none=True,
                )
            elif "data" in response:
                data = response["data"]
                if len(data) == 1:
                    return data[0]
                elif len(data) == 0:
                    raise ObjectNotPresentError(
                        message=f"Address '{name}' not found.",
                        error_code="API_I00013",
                        details={"errorType": "Object Not Present"},
                    )
                else:
                    raise APIError(
                        f"Multiple address groups found with the name '{name}'."
                    )

        raise APIError("Unexpected response format.")

    def delete(self, object_id: str) -> None:
        """
        Deletes an address object.

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
