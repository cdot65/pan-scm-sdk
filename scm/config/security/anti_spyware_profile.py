# scm/config/security/anti_spyware_profile.py

from typing import List, Dict, Any, Optional
from scm.config import BaseObject
from scm.models.security import (
    AntiSpywareProfileRequestModel,
    AntiSpywareProfileResponseModel,
)
from scm.exceptions import ValidationError


class AntiSpywareProfile(BaseObject):
    """
    Manages Anti-Spyware Profiles in Palo Alto Networks' Strata Cloud Manager.

    This class provides methods to create, retrieve, update, delete, and list Anti-Spyware Profiles
    using the Strata Cloud Manager API. It supports operations within folders, snippets,
    or devices, and allows filtering of profiles based on various criteria.

    Attributes:
        ENDPOINT (str): The API endpoint for Anti-Spyware Profile operations.

    Errors:
        ValidationError: Raised when invalid container parameters are provided.

    Returns:
        AntiSpywareProfileResponseModel: For create, get, and update methods.
        List[AntiSpywareProfileResponseModel]: For the list method.
    """

    ENDPOINT = "/config/security/v1/anti-spyware-profiles"

    def __init__(self, api_client):
        super().__init__(api_client)

    def create(self, data: Dict[str, Any]) -> AntiSpywareProfileResponseModel:
        profile = AntiSpywareProfileRequestModel(**data)
        payload = profile.model_dump(exclude_unset=True)
        response = self.api_client.post(self.ENDPOINT, json=payload)
        return AntiSpywareProfileResponseModel(**response)

    def get(self, object_id: str) -> AntiSpywareProfileResponseModel:
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response = self.api_client.get(endpoint)
        return AntiSpywareProfileResponseModel(**response)

    def update(
        self, object_id: str, data: Dict[str, Any]
    ) -> AntiSpywareProfileResponseModel:
        profile = AntiSpywareProfileRequestModel(**data)
        payload = profile.model_dump(exclude_unset=True)
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response = self.api_client.put(endpoint, json=payload)
        return AntiSpywareProfileResponseModel(**response)

    def delete(self, object_id: str) -> None:
        endpoint = f"{self.ENDPOINT}/{object_id}"
        self.api_client.delete(endpoint)

    def list(
        self,
        folder: Optional[str] = None,
        snippet: Optional[str] = None,
        device: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        name: Optional[str] = None,
        **filters,
    ) -> List[AntiSpywareProfileResponseModel]:
        params = {}
        error_messages = []

        # Validate offset and limit
        if offset is not None:
            if not isinstance(offset, int) or offset < 0:
                error_messages.append("Offset must be a non-negative integer")
        if limit is not None:
            if not isinstance(limit, int) or limit <= 0:
                error_messages.append("Limit must be a positive integer")

        # If there are any validation errors, raise ValueError with all error messages
        if error_messages:
            raise ValueError(". ".join(error_messages))

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

        # Handle pagination parameters
        if offset is not None:
            params["offset"] = offset
        if limit is not None:
            params["limit"] = limit

        # Handle filters
        if name is not None:
            params["name"] = name

        # Include any additional filters provided
        params.update(
            {
                k: v
                for k, v in filters.items()
                if v is not None
                and k not in container_params
                and k not in ["offset", "limit", "name"]
            }
        )

        response = self.api_client.get(self.ENDPOINT, params=params)
        profiles = [
            AntiSpywareProfileResponseModel(**item) for item in response.get("data", [])
        ]
        return profiles
