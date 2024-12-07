# scm/config/objects/auto_tag_actions.py

# Standard library imports
import logging
from typing import List, Dict, Any, Optional

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
)
from scm.models.objects.auto_tag_actions import (
    AutoTagActionCreateModel,
    AutoTagActionUpdateModel,
    AutoTagActionResponseModel,
)


class AutoTagAction(BaseObject):
    """
    Manages Auto-Tag Action objects in Palo Alto Networks' Strata Cloud Manager.
    """

    ENDPOINT = "/auto-tag-actions"
    DEFAULT_LIMIT = 10000

    def __init__(self, api_client):
        super().__init__(api_client)
        self.logger = logging.getLogger(__name__)

    def create(
        self,
        data: Dict[str, Any],
    ) -> AutoTagActionResponseModel:
        """
        Creates a new Auto-Tag Action object.

        Returns:
            AutoTagActionResponseModel
        """
        auto_tag_action = AutoTagActionCreateModel(**data)
        payload = auto_tag_action.model_dump(exclude_unset=True)
        response: Dict[str, Any] = self.api_client.post(
            self.ENDPOINT,
            json=payload,
        )
        return AutoTagActionResponseModel(**response)

    def update(
        self,
        auto_tag_action: AutoTagActionUpdateModel,
    ) -> AutoTagActionResponseModel:
        """
        Updates an existing auto-tag action object.

        Args:
            auto_tag_action: AutoTagActionUpdateModel instance containing the update data

        Returns:
            AutoTagActionResponseModel
        """
        payload = auto_tag_action.model_dump(exclude_unset=True)
        # Note: The API requires name to identify the object; no endpoint for id-based updates.
        # We send the request to the same endpoint without an object_id in the URL.
        if "id" in payload:
            payload.pop("id", None)

        response: Dict[str, Any] = self.api_client.put(
            self.ENDPOINT,
            json=payload,
        )

        return AutoTagActionResponseModel(**response)

    @staticmethod
    def _apply_filters(
        auto_tag_actions: List[AutoTagActionResponseModel],
        filters: Dict[str, Any],
    ) -> List[AutoTagActionResponseModel]:
        """
        Apply client-side filtering to the list of auto-tag actions.

        Args:
            auto_tag_actions: List of AutoTagActionResponseModel objects
            filters: Dictionary of filter criteria

        Returns:
            List[AutoTagActionResponseModel]: Filtered list of auto-tag actions
        """
        # No filters defined in this specification.
        return auto_tag_actions

    @staticmethod
    def _build_container_params(
        folder: Optional[str],
        snippet: Optional[str],
        device: Optional[str],
    ) -> dict:
        """
        Builds a dictionary of container parameters based on the provided arguments.
        """
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
    ) -> List[AutoTagActionResponseModel]:
        """
        Lists auto-tag action objects with optional filtering.

        Args:
            folder (str, optional): The folder in which the resource is defined.
            snippet (str, optional): The snippet in which the resource is defined.
            device (str, optional): The device in which the resource is defined.
            **filters: Additional filters (no filters defined for auto-tag actions).

        Returns:
            List[AutoTagActionResponseModel]: A list of auto-tag action objects.
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

        container_parameters = self._build_container_params(folder, snippet, device)
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

        auto_tag_actions = [
            AutoTagActionResponseModel(**item) for item in response["data"]
        ]
        return self._apply_filters(auto_tag_actions, filters)

    def fetch(
        self,
        name: str,
        folder: Optional[str] = None,
        snippet: Optional[str] = None,
        device: Optional[str] = None,
    ) -> AutoTagActionResponseModel:
        """
        Fetches a single auto-tag action by name.

        Args:
            name (str): The name of the auto-tag action to fetch.
            folder (str, optional): The folder in which the resource is defined.
            snippet (str, optional): The snippet in which the resource is defined.
            device (str, optional): The device in which the resource is defined.

        Returns:
            AutoTagActionResponseModel: The fetched auto-tag action object as a Pydantic model.
        """
        if not name:
            raise MissingQueryParameterError(
                message="Field 'name' cannot be empty",
                error_code="E003",
                http_status_code=400,
                details={"field": "name", "error": '"name" is not allowed to be empty'},
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
        container_parameters = self._build_container_params(folder, snippet, device)
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
            return AutoTagActionResponseModel(**response)
        else:
            raise InvalidObjectError(
                message="Invalid response format: missing 'id' field",
                error_code="E003",
                http_status_code=500,
                details={"error": "Response missing 'id' field"},
            )

    def delete(
        self,
        name: str,
        folder: Optional[str] = None,
        snippet: Optional[str] = None,
        device: Optional[str] = None,
    ) -> None:
        """
        Deletes an auto-tag action object by name.

        Args:
            name (str): The name of the auto-tag action to delete.
            folder (str, optional): The folder in which the resource is defined.
            snippet (str, optional): The snippet in which the resource is defined.
            device (str, optional): The device in which the resource is defined.
        """
        if not name:
            raise MissingQueryParameterError(
                message="Field 'name' cannot be empty",
                error_code="E003",
                http_status_code=400,
                details={"field": "name", "error": '"name" is not allowed to be empty'},
            )

        container_parameters = self._build_container_params(folder, snippet, device)
        if len(container_parameters) != 1:
            raise InvalidObjectError(
                message="Exactly one of 'folder', 'snippet', or 'device' must be provided.",
                error_code="E003",
                http_status_code=400,
                details={"error": "Invalid container parameters"},
            )

        params = {}
        params.update(container_parameters)
        params["name"] = name

        # Note: The API requires a 'name' query param to identify the action to delete.
        self.api_client.delete(self.ENDPOINT, params=params)
