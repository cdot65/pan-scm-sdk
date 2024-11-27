# scm/config/security/dns_security_profile.py

# Standard library imports
import logging
from typing import List, Dict, Any, Optional

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
)
from scm.models.security import (
    DNSSecurityProfileCreateModel,
    DNSSecurityProfileResponseModel,
    DNSSecurityProfileUpdateModel,
)


class DNSSecurityProfile(BaseObject):
    """
    Manages DNS Security Profile objects in Palo Alto Networks' Strata Cloud Manager.
    """

    ENDPOINT = "/config/security/v1/dns-security-profiles"
    DEFAULT_LIMIT = 10000

    def __init__(
        self,
        api_client,
    ):
        super().__init__(api_client)
        self.logger = logging.getLogger(__name__)

    def create(
        self,
        data: Dict[str, Any],
    ) -> DNSSecurityProfileResponseModel:
        """
        Creates a new DNS security profile object.

        Returns:
            DNSSecurityProfileResponseModel
        """
        # Use the dictionary "data" to pass into Pydantic and return a modeled object
        profile = DNSSecurityProfileCreateModel(**data)

        # Convert back to a Python dictionary, removing any unset fields
        payload = profile.model_dump(exclude_unset=True)

        # Send the updated object to the remote API as JSON, expecting a dictionary object to be returned.
        response: Dict[str, Any] = self.api_client.post(
            self.ENDPOINT,
            json=payload,
        )

        # Return the SCM API response as a new Pydantic object
        return DNSSecurityProfileResponseModel(**response)

    def get(
        self,
        object_id: str,
    ) -> DNSSecurityProfileResponseModel:
        """
        Gets a DNS security profile object by ID.

        Returns:
            DNSSecurityProfileResponseModel
        """
        # Send the request to the remote API
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.get(endpoint)

        # Return the SCM API response as a new Pydantic object
        return DNSSecurityProfileResponseModel(**response)

    def update(
        self,
        profile: DNSSecurityProfileUpdateModel,
    ) -> DNSSecurityProfileResponseModel:
        """
        Updates an existing DNS security profile object.

        Args:
            profile: DNSSecurityProfileUpdateModel instance containing the update data

        Returns:
            DNSSecurityProfileResponseModel
        """
        # Convert to dict for API request, excluding unset fields
        payload = profile.model_dump(exclude_unset=True)

        # Extract ID and remove from payload since it's in the URL
        object_id = str(profile.id)
        payload.pop("id", None)

        # Send the updated object to the remote API as JSON
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.put(
            endpoint,
            json=payload,
        )

        # Return the SCM API response as a new Pydantic model
        return DNSSecurityProfileResponseModel(**response)

    @staticmethod
    def _apply_filters(
        profiles: List[DNSSecurityProfileResponseModel],
        filters: Dict[str, Any],
    ) -> List[DNSSecurityProfileResponseModel]:
        """
        Apply client-side filtering to the list of DNS security profiles.

        Args:
            profiles: List of DNSSecurityProfileResponseModel objects
            filters: Dictionary of filter criteria

        Returns:
            List[DNSSecurityProfileResponseModel]: Filtered list of profiles
        """
        filter_criteria = profiles

        # Filter by dns_security_categories
        if "dns_security_categories" in filters:
            if not isinstance(filters["dns_security_categories"], list):
                raise InvalidObjectError(
                    message="'dns_security_categories' filter must be a list",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Object"},
                )

            categories = filters["dns_security_categories"]
            filter_criteria = [
                profile
                for profile in filter_criteria
                if profile.botnet_domains
                and profile.botnet_domains.dns_security_categories
                and any(
                    category.name in categories
                    for category in profile.botnet_domains.dns_security_categories
                )
            ]

        return filter_criteria

    @staticmethod
    def _build_container_params(
        folder: Optional[str],
        snippet: Optional[str],
        device: Optional[str],
    ) -> dict:
        """Builds container parameters dictionary."""
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
    ) -> List[DNSSecurityProfileResponseModel]:
        """
        Lists DNS security profile objects with optional filtering.

        Args:
            folder: Optional folder name
            snippet: Optional snippet name
            device: Optional device name
            **filters: Additional filters including:
                - dns_security_categories: List[str] - Filter by DNS security category names
        """
        if folder == "":
            raise MissingQueryParameterError(
                message="Field 'folder' cannot be empty",
                error_code="E003",
                http_status_code=400,
                details={
                    "field": "folder",
                    "error": '"folder" is not allowed to be empty',
                },
            )

        params = {"limit": self.DEFAULT_LIMIT}

        container_parameters = self._build_container_params(
            folder,
            snippet,
            device,
        )

        if len(container_parameters) != 1:
            raise InvalidObjectError(
                message="Exactly one of 'folder', 'snippet', or 'device' must be provided.",
                error_code="E003",
                http_status_code=400,
                details={"error": "Invalid container parameters"},
            )

        params.update(container_parameters)

        response = self.api_client.get(
            self.ENDPOINT,
            params=params,
        )

        if not isinstance(response, dict):
            raise InvalidObjectError(
                message="Invalid response format: expected dictionary",
                error_code="E003",
                http_status_code=500,
                details={"error": "Response is not a dictionary"},
            )

        if "data" not in response:
            raise InvalidObjectError(
                message="Invalid response format: missing 'data' field",
                error_code="E003",
                http_status_code=500,
                details={
                    "field": "data",
                    "error": '"data" field missing in the response',
                },
            )

        if not isinstance(response["data"], list):
            raise InvalidObjectError(
                message="Invalid response format: 'data' field must be a list",
                error_code="E003",
                http_status_code=500,
                details={
                    "field": "data",
                    "error": '"data" field must be a list',
                },
            )

        profiles = [
            DNSSecurityProfileResponseModel(**item) for item in response["data"]
        ]
        return self._apply_filters(
            profiles,
            filters,
        )

    def fetch(
        self,
        name: str,
        folder: Optional[str] = None,
        snippet: Optional[str] = None,
        device: Optional[str] = None,
    ) -> DNSSecurityProfileResponseModel:
        """
        Fetches a single DNS security profile by name.

        Args:
            name (str): The name of the DNS security profile to fetch.
            folder (str, optional): The folder in which the resource is defined.
            snippet (str, optional): The snippet in which the resource is defined.
            device (str, optional): The device in which the resource is defined.

        Returns:
            DNSSecurityProfileResponseModel: The fetched DNS security profile object as a Pydantic model.
        """
        if not name:
            raise MissingQueryParameterError(
                message="Field 'name' cannot be empty",
                error_code="E003",
                http_status_code=400,
                details={
                    "field": "name",
                    "error": '"name" is not allowed to be empty',
                },
            )

        if folder == "":
            raise MissingQueryParameterError(
                message="Field 'folder' cannot be empty",
                error_code="E003",
                http_status_code=400,
                details={
                    "field": "folder",
                    "error": '"folder" is not allowed to be empty',
                },
            )

        params = {}

        container_parameters = self._build_container_params(
            folder,
            snippet,
            device,
        )

        if len(container_parameters) != 1:
            raise InvalidObjectError(
                message="Exactly one of 'folder', 'snippet', or 'device' must be provided.",
                error_code="E003",
                http_status_code=400,
                details={
                    "error": "Exactly one of 'folder', 'snippet', or 'device' must be provided."
                },
            )

        params.update(container_parameters)
        params["name"] = name

        response = self.api_client.get(
            self.ENDPOINT,
            params=params,
        )

        if not isinstance(response, dict):
            raise InvalidObjectError(
                message="Invalid response format: expected dictionary",
                error_code="E003",
                http_status_code=500,
                details={"error": "Response is not a dictionary"},
            )

        if "id" in response:
            return DNSSecurityProfileResponseModel(**response)
        else:
            raise InvalidObjectError(
                message="Invalid response format: missing 'id' field",
                error_code="E003",
                http_status_code=500,
                details={"error": "Response missing 'id' field"},
            )

    def delete(
        self,
        object_id: str,
    ) -> None:
        """
        Deletes a DNS security profile object.

        Args:
            object_id (str): The ID of the object to delete.
        """
        endpoint = f"{self.ENDPOINT}/{object_id}"
        self.api_client.delete(endpoint)
