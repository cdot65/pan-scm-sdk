# scm/config/security/decryption_profile.py
from types import NoneType
from typing import List, Dict, Any, Optional
from scm.config import BaseObject
from scm.models.security import (
    DecryptionProfileCreateModel,
    DecryptionProfileResponseModel,
)
from scm.exceptions import ValidationError, NotFoundError, APIError


class DecryptionProfile(BaseObject):
    """
    Manages Decryption Profiles in Palo Alto Networks' Strata Cloud Manager.

    This class provides methods to create, retrieve, update, delete, and list Decryption Profiles
    using the Strata Cloud Manager API. It supports operations within folders, snippets,
    or devices, and allows filtering of profiles based on various criteria.

    Attributes:
        ENDPOINT (str): The API endpoint for Anti-Spyware Profile operations.

    Errors:
        ValidationError: Raised when invalid container parameters are provided.

    Returns:
        DecryptionProfileResponseModel: For create, get, and update methods.
        List[DecryptionProfileResponseModel]: For the list method.
    """

    ENDPOINT = "/config/security/v1/decryption-profiles"

    def __init__(
        self,
        api_client,
    ):
        super().__init__(api_client)

    def create(
        self,
        data: Dict[str, Any],
    ) -> DecryptionProfileResponseModel:
        profile = DecryptionProfileCreateModel(**data)
        payload = profile.model_dump(exclude_unset=True)
        response = self.api_client.post(self.ENDPOINT, json=payload)
        return DecryptionProfileResponseModel(**response)

    def get(
        self,
        uuid: str,
    ) -> DecryptionProfileResponseModel:
        endpoint = f"{self.ENDPOINT}/{uuid}"
        response = self.api_client.get(endpoint)
        return DecryptionProfileResponseModel(**response)

    def update(
        self,
        data: Dict[str, Any],
    ) -> DecryptionProfileCreateModel | DecryptionProfileResponseModel:
        """
        Updates an existing Decryption Profile.

        Args:
            data (Dict[str, Any]): The Decryption Profile data including the 'id' key.

        Returns:
            DecryptionProfileResponseModel: The updated Decryption Profile.
        """
        if "id" not in data:
            raise ValueError("The 'id' field is required in the data for update.")

        uuid = data.pop("id")  # Extract 'id' and remove it from the data

        # Pass the remaining data into the model for validation
        profile = DecryptionProfileCreateModel(**data)

        # Set the endpoint API, leveraging the `uuid` in the path
        endpoint = f"{self.ENDPOINT}/{uuid}"

        # Perform the update operation
        response = self.api_client.put(
            endpoint,
            json=profile.model_dump(
                exclude_unset=True,
                exclude_none=True,
            ),
        )

        # Handle response
        if isinstance(response, dict) and "id" in response:
            profile = DecryptionProfileResponseModel(**response)
            return profile
        elif isinstance(response, dict) and "data" in response:
            data = response["data"]
            if len(data) == 1:
                profile = DecryptionProfileResponseModel(**data[0])
                return profile
            elif len(data) == 0:
                raise NotFoundError("Decryption profile not found")
            else:
                raise APIError("Multiple decryption profiles found with the same name")
        elif isinstance(response, NoneType):
            return profile
        else:
            raise APIError("Unexpected response format")

    def delete(
        self,
        uuid: str,
    ) -> None:
        endpoint = f"{self.ENDPOINT}/{uuid}"
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
    ) -> List[DecryptionProfileResponseModel]:
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
            raise ValueError(
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
            DecryptionProfileResponseModel(**item) for item in response.get("data", [])
        ]
        return profiles

    def fetch(
        self,
        name: str,
        folder: Optional[str] = None,
        snippet: Optional[str] = None,
        device: Optional[str] = None,
        **filters,
    ) -> Dict[str, Any]:
        """
        Fetches a single Decryption Profile object by name.

        Args:
            name (str): The name of the Decryption Profile to fetch.
            folder (str, optional): The folder in which the resource is defined.
            snippet (str, optional): The snippet in which the resource is defined.
            device (str, optional): The device in which the resource is defined.
            **filters: Additional filters to apply to the request.

        Returns:
            DecryptionProfileResponseModel: The fetched security rule object.

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

        # Since response is a single object when 'name' is provided
        # We can directly create the DecryptionProfileResponseModel
        profile = DecryptionProfileResponseModel(**response)
        return profile.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )
