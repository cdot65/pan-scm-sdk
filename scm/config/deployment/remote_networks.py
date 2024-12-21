# scm/config/deployment/remote_networks.py

# Standard library imports
import logging
from typing import List, Dict, Any, Optional

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
)
from scm.models.deployment import (
    RemoteNetworkCreateModel,
    RemoteNetworkResponseModel,
    RemoteNetworkUpdateModel,
)


class RemoteNetworks(BaseObject):
    """
    Manages Remote Network objects.
    Args:
        api_client: The API client instance
        max_limit (Optional[int]): Maximum number of objects to return in a single API request.
            Defaults to 5000. Must be between 1 and 10000.
    """

    ENDPOINT = "/sse/config/v1/remote-networks"
    DEFAULT_MAX_LIMIT = 2500
    ABSOLUTE_MAX_LIMIT = 5000  # Maximum allowed by the API

    def __init__(
        self,
        api_client,
        max_limit: Optional[int] = None,
    ):
        super().__init__(api_client)
        self.logger = logging.getLogger(__name__)

        # Override the api_base_url for this object
        self.api_client.api_base_url = "https://api.sase.paloaltonetworks.com"

        # Validate and set max_limit
        self._max_limit = self._validate_max_limit(max_limit)

    @property
    def max_limit(self) -> int:
        """Get the current maximum limit for API requests."""
        return self._max_limit

    @max_limit.setter
    def max_limit(self, value: int) -> None:
        """Set a new maximum limit for API requests."""
        self._max_limit = self._validate_max_limit(value)

    def _validate_max_limit(self, limit: Optional[int]) -> int:
        """
        Validates the max_limit parameter.

        Args:
            limit: The limit to validate

        Returns:
            int: The validated limit

        Raises:
            InvalidObjectError: If the limit is invalid
        """
        if limit is None:
            return self.DEFAULT_MAX_LIMIT

        try:
            limit_int = int(limit)
        except (TypeError, ValueError):
            raise InvalidObjectError(
                message="max_limit must be an integer",
                error_code="E003",
                http_status_code=400,
                details={"error": "Invalid max_limit type"},
            )

        if limit_int < 1:
            raise InvalidObjectError(
                message="max_limit must be greater than 0",
                error_code="E003",
                http_status_code=400,
                details={"error": "Invalid max_limit value"},
            )

        if limit_int > self.ABSOLUTE_MAX_LIMIT:
            raise InvalidObjectError(
                message=f"max_limit cannot exceed {self.ABSOLUTE_MAX_LIMIT}",
                error_code="E003",
                http_status_code=400,
                details={"error": "max_limit exceeds maximum allowed value"},
            )

        return limit_int

    def create(
        self,
        data: Dict[str, Any],
    ) -> RemoteNetworkResponseModel:
        """
        Creates a new Remote Network object.

        Returns:
            RemoteNetworkResponseModel
        """
        remote_network = RemoteNetworkCreateModel(**data)
        payload = remote_network.model_dump(exclude_unset=True)
        response: Dict[str, Any] = self.api_client.post(
            self.ENDPOINT,
            json=payload,
        )
        return RemoteNetworkResponseModel(**response)

    def get(
        self,
        object_id: str,
    ) -> RemoteNetworkResponseModel:
        """
        Gets a Remote Network object by ID.

        Returns:
            RemoteNetworkResponseModel
        """
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.get(endpoint)
        return RemoteNetworkResponseModel(**response)

    def update(
        self,
        remote_network: RemoteNetworkUpdateModel,
    ) -> RemoteNetworkResponseModel:
        """
        Updates an existing Remote Network object.

        Args:
            remote_network: RemoteNetworkUpdateModel instance containing the update data

        Returns:
            RemoteNetworkResponseModel
        """
        payload = remote_network.model_dump(exclude_unset=True)
        object_id = str(remote_network.id)
        payload.pop("id", None)
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.put(
            endpoint,
            json=payload,
        )
        return RemoteNetworkResponseModel(**response)

    @staticmethod
    def _apply_filters(
        remote_networks: List[RemoteNetworkResponseModel],
        filters: Dict[str, Any],
    ) -> List[RemoteNetworkResponseModel]:
        """
        Apply client-side filtering to the list of remote networks.

        Args:
            remote_networks: List of RemoteNetworkResponseModel objects
            filters: Dictionary of filter criteria

        Returns:
            List[RemoteNetworkResponseModel]: Filtered list of remote networks
        """
        # Implement filtering logic if needed, similar to address_group.
        # For now, we assume no advanced filtering is required.
        return remote_networks

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
        exact_match: bool = False,
        exclude_folders: Optional[List[str]] = None,
        exclude_snippets: Optional[List[str]] = None,
        exclude_devices: Optional[List[str]] = None,
        **filters,
    ) -> List[RemoteNetworkResponseModel]:
        """
        Lists remote networks with optional filtering.

        Args:
            folder: Optional folder name
            snippet: Optional snippet name
            device: Optional device name
            exact_match (bool): If True, only return objects whose container
                                exactly matches the provided container parameter.
            exclude_folders (List[str], optional): List of folder names to exclude.
            exclude_snippets (List[str], optional): List of snippet values to exclude.
            exclude_devices (List[str], optional): List of device values to exclude.
            **filters: Additional filters if needed

        Returns:
            List[RemoteNetworkResponseModel]: A list of remote network objects
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

        limit = self._max_limit
        offset = 0
        all_objects = []

        while True:
            params = container_parameters.copy()
            params["limit"] = limit
            params["offset"] = offset

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

            data = response["data"]
            object_instances = [RemoteNetworkResponseModel(**item) for item in data]
            all_objects.extend(object_instances)

            if len(data) < limit:
                break

            offset += limit

        # Apply filters
        filtered_objects = self._apply_filters(
            all_objects,
            filters,
        )

        container_key, container_value = next(iter(container_parameters.items()))

        if exact_match:
            filtered_objects = [
                each
                for each in filtered_objects
                if getattr(each, container_key) == container_value
            ]

        if exclude_folders and isinstance(exclude_folders, list):
            filtered_objects = [
                each for each in filtered_objects if each.folder not in exclude_folders
            ]

        if exclude_snippets and isinstance(exclude_snippets, list):
            filtered_objects = [
                each
                for each in filtered_objects
                if each.snippet not in exclude_snippets
            ]

        if exclude_devices and isinstance(exclude_devices, list):
            filtered_objects = [
                each for each in filtered_objects if each.device not in exclude_devices
            ]

        return filtered_objects

    def fetch(
        self,
        name: str,
        folder: Optional[str] = None,
        snippet: Optional[str] = None,
        device: Optional[str] = None,
    ) -> RemoteNetworkResponseModel:
        """
        Fetches a single remote network by name.

        Args:
            name (str): The name of the remote network to fetch.
            folder (str, optional): The folder in which the resource is defined.
            snippet (str, optional): The snippet in which the resource is defined.
            device (str, optional): The device in which the resource is defined.

        Returns:
            RemoteNetworkResponseModel: The fetched remote network object.
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

        params = container_parameters.copy()
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
            return RemoteNetworkResponseModel(**response)
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
        Deletes a remote network object.

        Args:
            object_id (str): The ID of the object to delete.
        """
        endpoint = f"{self.ENDPOINT}/{object_id}"
        self.api_client.delete(endpoint)
