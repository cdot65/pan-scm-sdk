# pan_scm_sdk/resources/address.py

from typing import List, Optional
from pan_scm_sdk.client import APIClient
from pan_scm_sdk.models.address import Address
from pan_scm_sdk.endpoints.addresses import ADDRESSES_ENDPOINTS
from pan_scm_sdk.utils.logging import setup_logger

logger = setup_logger(__name__)


class AddressClient:
    """
    A client class for managing addresses in Palo Alto Networks' Strata Cloud Manager.

    This class provides methods to list, get, create, update, and delete addresses
    using the Strata Cloud Manager API.

    Attributes:
        api_client (APIClient): An instance of the APIClient for making API requests.

    Error:
        APIError: May be raised for any API-related errors during requests.

    Return:
        Various methods return Address objects or lists of Address objects.
    """

    def __init__(self, api_client: APIClient):
        self.api_client = api_client

    def list_addresses(
        self,
        name: Optional[str] = None,
        folder: str = "Shared",
        snippet: Optional[str] = None,
        device: Optional[str] = None,
        offset: int = 0,
        limit: int = 200,
    ) -> List[Address]:
        endpoint = ADDRESSES_ENDPOINTS["list_addresses"]
        params = {
            "name": name,
            "folder": folder,
            "snippet": snippet,
            "device": device,
            "offset": offset,
            "limit": limit,
        }
        params = {k: v for k, v in params.items() if v is not None}

        response = self.api_client.get(endpoint, params=params)
        addresses = [Address(**item) for item in response.get("data", [])]
        return addresses

    def get_address(self, address_id: str) -> Address:
        endpoint = ADDRESSES_ENDPOINTS["get_address"].format(id=address_id)
        response = self.api_client.get(endpoint)
        return Address(**response)

    def create_address(self, address: Address) -> Address:
        endpoint = ADDRESSES_ENDPOINTS["create_address"]
        payload = address.model_dump(exclude_unset=True)
        response = self.api_client.post(endpoint, json=payload)
        return Address(**response)

    def update_address(self, address_id: str, address: Address) -> Address:
        endpoint = ADDRESSES_ENDPOINTS["update_address"].format(id=address_id)
        payload = address.model_dump(exclude_unset=True)
        response = self.api_client.put(endpoint, json=payload)
        return Address(**response)

    def delete_address(self, address_id: str) -> None:
        endpoint = ADDRESSES_ENDPOINTS["delete_address"].format(id=address_id)
        self.api_client.delete(endpoint)
