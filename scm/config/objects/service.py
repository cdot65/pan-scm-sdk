# scm/config/objects/service.py

from typing import List, Dict, Any, Optional

from scm.config import BaseObject
from scm.models import ServiceRequestModel, ServiceResponseModel
from scm.exceptions import ValidationError


class Service(BaseObject):
    """Manages Services in Palo Alto Networks' Strata Cloud Manager.'"""

    ENDPOINT = "/config/objects/v1/services"

    def __init__(self, api_client):
        super().__init__(api_client)

    def create(self, data: Dict[str, Any]) -> ServiceResponseModel:
        service_request = ServiceRequestModel(**data)
        payload = service_request.model_dump(exclude_unset=True)
        response = self.api_client.post(self.ENDPOINT, json=payload)
        return ServiceResponseModel(**response)

    def get(self, object_id: str) -> ServiceResponseModel:
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response = self.api_client.get(endpoint)
        return ServiceResponseModel(**response)

    def update(self, object_id: str, data: Dict[str, Any]) -> ServiceResponseModel:
        service = ServiceRequestModel(**data)
        payload = service.model_dump(exclude_unset=True)
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response = self.api_client.put(endpoint, json=payload)
        return ServiceResponseModel(**response)

    def list(
        self,
        folder: Optional[str] = None,
        snippet: Optional[str] = None,
        device: Optional[str] = None,
        **filters,
    ) -> List[ServiceResponseModel]:
        params = {}

        # Include container type parameters
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

        # Handle specific filters for services
        if "names" in filters:
            params["name"] = ",".join(filters["names"])

        # Add this block to handle 'tags' filter
        if "tags" in filters:
            params["tag"] = ",".join(filters["tags"])

        response = self.api_client.get(self.ENDPOINT, params=params)
        services = [ServiceResponseModel(**item) for item in response.get("data", [])]
        return services
