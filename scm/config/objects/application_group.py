# scm/config/objects/application_group.py

from typing import List, Dict, Any, Optional

from scm.config import BaseObject
from scm.models.objects import (
    ApplicationGroupRequestModel,
    ApplicationGroupResponseModel,
)
from scm.exceptions import ValidationError


class ApplicationGroup(BaseObject):
    """
    Manages ApplicationGroup objects in Palo Alto Networks' Strata Cloud Manager.

    This class provides methods to create, retrieve, update, and list ApplicationGroup objects
    using the Strata Cloud Manager API. It supports operations within folders, snippets,
    or devices, and allows filtering of ApplicationGroup objects based on various criteria.

    Attributes:
        ENDPOINT (str): The API endpoint for ApplicationGroup object operations.

    Error:
        ValueError: Raised when invalid container parameters are provided.

    Return:
        ApplicationGroupRequestModel: For create, get, and update methods.
        List[ApplicationGroup]: For the list method.
    """

    ENDPOINT = "/config/objects/v1/application-groups"

    def __init__(self, api_client):
        super().__init__(api_client)

    def create(self, data: Dict[str, Any]) -> ApplicationGroupResponseModel:
        app_group_request = ApplicationGroupRequestModel(**data)
        payload = app_group_request.model_dump(exclude_unset=True)
        response = self.api_client.post(self.ENDPOINT, json=payload)
        return ApplicationGroupResponseModel(**response)

    def get(self, object_id: str) -> ApplicationGroupResponseModel:
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response = self.api_client.get(endpoint)
        return ApplicationGroupResponseModel(**response)

    def update(
        self, object_id: str, data: Dict[str, Any]
    ) -> ApplicationGroupResponseModel:
        app_group = ApplicationGroupRequestModel(**data)
        payload = app_group.model_dump(exclude_unset=True)
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response = self.api_client.put(endpoint, json=payload)
        return ApplicationGroupResponseModel(**response)

    def list(
        self,
        folder: Optional[str] = None,
        snippet: Optional[str] = None,
        device: Optional[str] = None,
        **filters,
    ) -> List[ApplicationGroupResponseModel]:
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

        # Handle specific filters for applications
        if "names" in filters:
            params["name"] = ",".join(filters["names"])

        # Include any additional filters provided
        params.update(
            {
                k: v
                for k, v in filters.items()
                if k
                not in [
                    "members",
                    "names",
                ]
            }
        )

        response = self.api_client.get(self.ENDPOINT, params=params)
        applications = [
            ApplicationGroupResponseModel(**item) for item in response.get("data", [])
        ]
        return applications
