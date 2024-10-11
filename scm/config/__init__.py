# scm/config/__init__.py

from scm.client import Scm
from typing import List, Dict, Any


class BaseObject:
    """
    Base class for configuration objects in the SDK, providing CRUD operations.

    This class implements common methods for creating, retrieving, updating, deleting,
    and listing configuration objects through the API client.

    Attributes:
        ENDPOINT (str): API endpoint for the object, to be defined in subclasses.
        api_client (Scm): Instance of the API client for making HTTP requests.

    Error:
        APIError: May be raised for any API-related errors during operations.

    Return:
        Dict[str, Any] or List[Dict[str, Any]]: API response data for CRUD operations.
    """

    ENDPOINT: str  # Should be defined in subclasses

    def __init__(self, api_client: Scm):
        self.api_client = api_client

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        response = self.api_client.post(self.ENDPOINT, json=data)
        return response

    def get(self, object_id: str) -> Dict[str, Any]:
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response = self.api_client.get(endpoint)
        return response

    def update(self, object_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response = self.api_client.put(endpoint, json=data)
        return response

    def delete(self, object_id: str) -> None:
        endpoint = f"{self.ENDPOINT}/{object_id}"
        self.api_client.delete(endpoint)

    def list(self, **filters) -> List[Dict[str, Any]]:
        params = {k: v for k, v in filters.items() if v is not None}
        response = self.api_client.get(self.ENDPOINT, params=params)
        return response.get("data", [])
