# scm/config/objects/service.py

from typing import List, Dict, Any, Optional

from scm.config import BaseObject
from scm.models.objects import ServiceCreateModel, ServiceResponseModel
from scm.exceptions import ValidationError


class Service(BaseObject):
    """Manages Services in Palo Alto Networks' Strata Cloud Manager.'"""

    ENDPOINT = "/config/objects/v1/services"

    def __init__(self, api_client):
        super().__init__(api_client)

    def create(self, data: Dict[str, Any]) -> ServiceResponseModel:
        service_request = ServiceCreateModel(**data)
        payload = service_request.model_dump(exclude_unset=True)
        response = self.api_client.post(self.ENDPOINT, json=payload)
        return ServiceResponseModel(**response)

    def get(self, object_id: str) -> ServiceResponseModel:
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response = self.api_client.get(endpoint)
        return ServiceResponseModel(**response)

    def update(
        self,
        data: Dict[str, Any],
    ) -> ServiceResponseModel:
        service = ServiceCreateModel(**data)
        payload = service.model_dump(exclude_unset=True)
        endpoint = f"{self.ENDPOINT}/{data['id']}"
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

        params.update(provided_containers)  # noqa

        # Handle specific filters for services
        if "names" in filters:
            params["name"] = ",".join(filters["names"])

        # Add this block to handle 'tags' filter
        if "tags" in filters:
            params["tag"] = ",".join(filters["tags"])

        response = self.api_client.get(self.ENDPOINT, params=params)
        services = [ServiceResponseModel(**item) for item in response.get("data", [])]
        return services

    def fetch(
        self,
        name: str,
        folder: Optional[str] = None,
        snippet: Optional[str] = None,
        device: Optional[str] = None,
        **filters,
    ) -> Dict[str, Any]:
        """
        Fetches a single service by name.

        Args:
            name (str): The name of the application group to fetch.
            folder (str, optional): The folder in which the resource is defined.
            snippet (str, optional): The snippet in which the resource is defined.
            device (str, optional): The device in which the resource is defined.
            **filters: Additional filters to apply to the request.

        Returns:
            ServiceResponseModel: The fetched security rule object.

        Raises:
            ValidationError: If invalid parameters are provided.
            NotFoundError: If the security rule object is not found.
        """
        if not name:
            raise ValidationError("Parameter 'name' must be provided for fetch method.")

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

        response = self.api_client.get(self.ENDPOINT, params=params)

        # Since response is a single object when 'name' is provided
        # We can directly create the ServiceResponseModel
        service = ServiceResponseModel(**response)
        return service.model_dump(exclude_unset=True, exclude_none=True)
