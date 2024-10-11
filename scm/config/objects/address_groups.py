# scm/config/objects/address_groups.py

from typing import List, Dict, Any, Optional
from scm.config import BaseObject
from scm.models import AddressGroup
from scm.exceptions import ValidationError


class AddressGroups(BaseObject):
    """
    Manages Address Groups in Palo Alto Networks' Strata Cloud Manager.

    This class provides methods to create, retrieve, update, and list Address Groups
    using the Strata Cloud Manager API. It supports operations within folders, snippets,
    or devices, and allows filtering of Address Groups based on various criteria.

    Attributes:
        ENDPOINT (str): The API endpoint for Address Group operations.

    Error:
        ValueError: Raised when invalid container parameters are provided.

    Return:
        AddressGroup: For create, get, and update methods.
        List[Address]: For the list method.
    """

    ENDPOINT = "/config/objects/v1/address-groups"

    def __init__(self, api_client):
        super().__init__(api_client)

    def create(self, data: Dict[str, Any]) -> AddressGroup:
        address_group = AddressGroup(**data)
        payload = address_group.model_dump(exclude_unset=True)
        response = self.api_client.post(self.ENDPOINT, json=payload)
        return AddressGroup(**response)

    def get(self, object_id: str) -> AddressGroup:
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response = self.api_client.get(endpoint)
        return AddressGroup(**response)

    def update(self, object_id: str, data: Dict[str, Any]) -> AddressGroup:
        address = AddressGroup(**data)
        payload = address.model_dump(exclude_unset=True)
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response = self.api_client.put(endpoint, json=payload)
        return AddressGroup(**response)

    def list(
        self,
        folder: Optional[str] = None,
        snippet: Optional[str] = None,
        device: Optional[str] = None,
        **filters,
    ) -> List[AddressGroup]:
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
        addresses = [AddressGroup(**item) for item in response.get("data", [])]
        return addresses
