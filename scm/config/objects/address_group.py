# scm/config/objects/address_group.py

from typing import List, Dict, Any, Optional
from scm.config import BaseObject
from scm.models.objects import AddressGroupRequestModel, AddressGroupResponseModel
from scm.exceptions import ValidationError, NotFoundError, APIError


class AddressGroup(BaseObject):
    """
    Manages AddressRequestModel Groups in Palo Alto Networks' Strata Cloud Manager.

    This class provides methods to create, retrieve, update, and list AddressRequestModel Groups
    using the Strata Cloud Manager API. It supports operations within folders, snippets,
    or devices, and allows filtering of AddressRequestModel Groups based on various criteria.

    Attributes:
        ENDPOINT (str): The API endpoint for AddressRequestModel Group operations.

    Error:
        ValueError: Raised when invalid container parameters are provided.

    Return:
        AddressGroupResponseModel: For create, get, and update methods.
        List[AddressGroupResponseModel]: For the list method.
    """

    ENDPOINT = "/config/objects/v1/address-groups"

    def __init__(self, api_client):
        super().__init__(api_client)

    def create(self, data: Dict[str, Any]) -> AddressGroupResponseModel:
        address_group = AddressGroupRequestModel(**data)
        payload = address_group.model_dump(exclude_unset=True)
        response = self.api_client.post(self.ENDPOINT, json=payload)
        return AddressGroupResponseModel(**response)

    def get(self, object_id: str) -> AddressGroupResponseModel:
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response = self.api_client.get(endpoint)
        return AddressGroupResponseModel(**response)

    def update(
        self,
        data: Dict[str, Any],
    ) -> AddressGroupResponseModel:
        address = AddressGroupRequestModel(**data)
        payload = address.model_dump(exclude_unset=True)
        endpoint = f"{self.ENDPOINT}/{data['id']}"
        response = self.api_client.put(endpoint, json=payload)
        return AddressGroupResponseModel(**response)

    def list(
        self,
        folder: Optional[str] = None,
        snippet: Optional[str] = None,
        device: Optional[str] = None,
        **filters,
    ) -> List[AddressGroupResponseModel]:
        params = {}

        # Include container type parameter
        container_params = {"folder": folder, "snippet": snippet, "device": device}
        provided_containers = {
            k: v for k, v in container_params.items() if v is not None
        }

        if len(provided_containers) != 1:
            raise ValidationError(
                "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            )

        params.update(provided_containers)

        # Handle specific filters for addresses
        if "types" in filters:
            params["type"] = ",".join(filters["types"])
        if "values" in filters:
            params["value"] = ",".join(filters["values"])
        if "names" in filters:
            params["name"] = ",".join(filters["names"])
        if "tags" in filters:
            params["tag"] = ",".join(filters["tags"])

        # Include any additional filters provided
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

        response = self.api_client.get(self.ENDPOINT, params=params)
        addresses = [
            AddressGroupResponseModel(**item) for item in response.get("data", [])
        ]
        return addresses

    def fetch(
        self,
        name: str,
        folder: Optional[str] = None,
        snippet: Optional[str] = None,
        device: Optional[str] = None,
        **filters,
    ) -> Dict[str, Any]:
        """
        Fetches a single address group by name.

        Args:
            name (str): The name of the address group to fetch.
            folder (str, optional): The folder in which the resource is defined.
            snippet (str, optional): The snippet in which the resource is defined.
            device (str, optional): The device in which the resource is defined.
            **filters: Additional filters to apply to the request.

        Returns:
            AddressGroupResponseModel: The fetched security rule object.

        Raises:
            ValidationError: If invalid parameters are provided.
            NotFoundError: If the security rule object is not found.
        """
        if not name:
            raise ValidationError("Parameter 'name' must be provided for fetch method.")

        params = {}

        # Include container type parameter
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
        params["name"] = name  # Set the 'name' parameter

        # Include any additional filters provided
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

        response = self.api_client.get(
            self.ENDPOINT,
            params=params,
        )

        # Handle different response formats
        if isinstance(response, dict) and "id" in response:
            # Single object returned directly
            return response
        elif "data" in response:
            # List of objects returned under 'data'
            data = response["data"]
            if len(data) == 1:
                return data[0]
            elif len(data) == 0:
                raise NotFoundError(f"Address group '{name}' not found.")
            else:
                raise APIError(f"Multiple address groups found with the name '{name}'.")
        else:
            raise APIError("Unexpected response format.")
