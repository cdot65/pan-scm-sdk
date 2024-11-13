# scm/config/objects/address_group.py

from typing import List, Dict, Any, Optional
import logging
from scm.config import BaseObject
from scm.models.objects import (
    AddressGroupCreateModel,
    AddressGroupResponseModel,
    AddressGroupUpdateModel,
)
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
    ErrorHandler,
    APIError,
)
from scm.utils.logging import setup_logger


class AddressGroup(BaseObject):
    """
    Manages Address Group objects in Palo Alto Networks' Strata Cloud Manager.
    """

    ENDPOINT = "/config/objects/v1/address-groups"
    DEFAULT_LIMIT = 10000

    def __init__(
        self,
        api_client,
        log_level: int = logging.ERROR,
    ):
        super().__init__(api_client)
        self.logger = setup_logger(
            __name__,
            log_level=log_level,
        )

    def create(
        self,
        data: Dict[str, Any],
    ) -> AddressGroupResponseModel:
        """
        Creates a new address group object.

        Returns:
            AddressGroupResponseModel

        Raises:
            APIError: For any API-related errors
        """
        try:
            address_group = AddressGroupCreateModel(**data)
            payload = address_group.model_dump(exclude_unset=True)
            response = self.api_client.post(
                self.ENDPOINT,
                json=payload,
            )
            return AddressGroupResponseModel(**response)

        except Exception as e:
            if isinstance(e, APIError):
                self.logger.error(f"API error while creating address group: {e}")
                raise
            else:
                self.logger.error(
                    f"An unexpected error occurred while creating address group: {e}"
                )
                raise APIError("An unexpected error occurred") from e

    def get(
        self,
        object_id: str,
    ) -> AddressGroupResponseModel:
        """
        Gets an address group object by ID.

        Returns:
            AddressGroupResponseModel

        Raises:
            APIError: For any API-related errors
        """
        try:
            endpoint = f"{self.ENDPOINT}/{object_id}"
            response = self.api_client.get(endpoint)
            return AddressGroupResponseModel(**response)

        except Exception as e:
            self.logger.error(f"Error getting address group: {e}", exc_info=True)
            if hasattr(e, "response") and e.response is not None:  # noqa
                ErrorHandler.raise_for_error(
                    e.response.json(),
                    e.response.status_code,
                )
            else:
                raise APIError(f"An unexpected error occurred: {e}") from e

    def update(
        self,
        data: Dict[str, Any],
    ) -> AddressGroupResponseModel:
        """
        Updates an existing address group object.

        Returns:
            AddressGroupResponseModel

        Raises:
            APIError: For any API-related errors
        """
        try:
            address = AddressGroupUpdateModel(**data)
            payload = address.model_dump(exclude_unset=True)
            endpoint = f"{self.ENDPOINT}/{data['id']}"
            response = self.api_client.put(endpoint, json=payload)
            return AddressGroupResponseModel(**response)

        except Exception as e:
            self.logger.error(f"Error updating address group: {e}", exc_info=True)
            if hasattr(e, "response") and e.response is not None:  # noqa
                ErrorHandler.raise_for_error(
                    e.response.json(),
                    e.response.status_code,
                )
            else:
                raise APIError(f"An unexpected error occurred: {e}") from e

    @staticmethod
    def _apply_filters(
        address_groups: List[AddressGroupResponseModel],
        filters: Dict[str, Any],
    ) -> List[AddressGroupResponseModel]:
        """
        Apply client-side filtering to the list of address groups.

        Args:
            address_groups: List of AddressGroupResponseModel objects
            filters: Dictionary of filter criteria

        Returns:
            List[AddressGroupResponseModel]: Filtered list of address groups

        Raises:
            InvalidObjectError: If filter criteria are invalid
        """
        filtered_groups = address_groups

        if "types" in filters:
            if not isinstance(filters["types"], list):
                raise InvalidObjectError("'types' filter must be a list")
            types = filters["types"]
            filtered_groups = [
                group
                for group in filtered_groups
                if any(
                    getattr(group, field) is not None
                    for field in ["static", "dynamic"]
                    if field in types
                )
            ]

        if "values" in filters:
            if not isinstance(filters["values"], list):
                raise InvalidObjectError("'values' filter must be a list")
            values = filters["values"]
            filtered_groups = [
                group
                for group in filtered_groups
                if (group.static and any(value in group.static for value in values))
                or (group.dynamic and group.dynamic.filter in values)
            ]

        if "tags" in filters:
            if not isinstance(filters["tags"], list):
                raise InvalidObjectError("'tags' filter must be a list")
            tags = filters["tags"]
            filtered_groups = [
                group
                for group in filtered_groups
                if group.tag and any(tag in group.tag for tag in tags)
            ]

        return filtered_groups

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
    ) -> List[AddressGroupResponseModel]:
        """
        Lists address group objects with optional filtering.

        Args:
            folder: Optional folder name
            snippet: Optional snippet name
            device: Optional device name
            **filters: Additional filters including:
                - types: List[str] - Filter by group types (e.g., ['static', 'dynamic'])
                - values: List[str] - Filter by group values
                - tags: List[str] - Filter by tags

        Raises:
            MissingQueryParameterError: If provided container fields are empty
            InvalidObjectError: If the container parameters are invalid
            APIError: If response format is invalid
        """
        if folder == "":
            raise MissingQueryParameterError(
                message="Field 'folder' cannot be empty",
                error_code="E003",
                http_status_code=400,
                details=['"folder" is not allowed to be empty'],  # noqa
            )

        params = {"limit": self.DEFAULT_LIMIT}
        container_parameters = self._build_container_params(
            folder,
            snippet,
            device,
        )

        if len(container_parameters) != 1:
            raise InvalidObjectError(
                "Exactly one of 'folder', 'snippet', or 'device' must be provided.",
                error_code="E003",
                http_status_code=400,
            )

        params.update(container_parameters)

        try:
            response = self.api_client.get(self.ENDPOINT, params=params)

            if not isinstance(response, dict):
                raise APIError(
                    "Invalid response format: expected dictionary",
                    http_status_code=500,
                )

            if "data" not in response:
                raise APIError(
                    "Invalid response format: missing 'data' field",
                    http_status_code=500,
                )

            if not isinstance(response["data"], list):
                raise APIError(
                    "Invalid response format: 'data' field must be a list",
                    http_status_code=500,
                )

            address_groups = [
                AddressGroupResponseModel(**item) for item in response["data"]
            ]
            return self._apply_filters(
                address_groups,
                filters,
            )

        except Exception as e:
            if isinstance(e, APIError):
                self.logger.error(f"API error while listing address groups: {e}")
                raise
            else:
                self.logger.error(
                    f"An unexpected error occurred while listing address groups: {e}"
                )
                raise APIError("An unexpected error occurred") from e

    def fetch(
        self,
        name: str,
        folder: Optional[str] = None,
        snippet: Optional[str] = None,
        device: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Fetches a single address group by name.

        Args:
            name (str): The name of the address group to fetch.
            folder (str, optional): The folder in which the resource is defined.
            snippet (str, optional): The snippet in which the resource is defined.
            device (str, optional): The device in which the resource is defined.

        Returns:
            Dict: The fetched object.

        Raises:
            MissingQueryParameterError: If name or container fields are empty
            InvalidObjectError: If the parameters are invalid
            APIError: For other API-related errors
        """
        if not name:
            raise MissingQueryParameterError(
                message="Field 'name' cannot be empty",
                error_code="E003",
                http_status_code=400,
                details=['"name" is not allowed to be empty'],  # noqa
            )

        if folder == "":
            raise MissingQueryParameterError(
                message="Field 'folder' cannot be empty",
                error_code="E003",
                http_status_code=400,
                details=['"folder" is not allowed to be empty'],  # noqa
            )

        params = {}
        container_parameters = self._build_container_params(
            folder,
            snippet,
            device,
        )

        if len(container_parameters) != 1:
            raise InvalidObjectError(
                "Exactly one of 'folder', 'snippet', or 'device' must be provided.",
                error_code="E003",
                http_status_code=400,
            )

        params.update(container_parameters)
        params["name"] = name

        try:
            response = self.api_client.get(
                self.ENDPOINT,
                params=params,
            )

            if not isinstance(response, dict):
                raise APIError(
                    "Invalid response format: expected dictionary",
                    http_status_code=500,
                )

            if "_errors" in response:
                ErrorHandler.raise_for_error(response, http_status_code=400)

            if "id" in response:
                address = AddressGroupResponseModel(**response)
                return address.model_dump(
                    exclude_unset=True,
                    exclude_none=True,
                )
            else:
                raise APIError(
                    "Invalid response format: missing 'id' field",
                    http_status_code=500,
                )

        except Exception as e:
            self.logger.error(
                f"Error fetching address group: {e}",
                exc_info=True,
            )
            if hasattr(e, "response") and e.response is not None:  # noqa
                ErrorHandler.raise_for_error(
                    e.response.json(),
                    e.response.status_code,
                )
            else:
                raise APIError(f"An unexpected error occurred: {e}") from e

    def delete(
        self,
        object_id: str,
    ) -> None:
        """
        Deletes an address group object.

        Args:
            object_id (str): The ID of the object to delete.

        Raises:
            ObjectNotPresentError: If the object doesn't exist
            ReferenceNotZeroError: If the object is still referenced by other objects
            MalformedCommandError: If the request is malformed
        """
        try:
            endpoint = f"{self.ENDPOINT}/{object_id}"
            self.api_client.delete(endpoint)

        except Exception as e:
            self.logger.error(
                f"Error deleting address group: {e}",
                exc_info=True,
            )
            if hasattr(e, "response") and e.response is not None:  # noqa
                ErrorHandler.raise_for_error(
                    e.response.json(),
                    e.response.status_code,
                )
            else:
                raise APIError(f"An unexpected error occurred: {e}") from e
