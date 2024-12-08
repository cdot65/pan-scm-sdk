# scm/config/objects/tag.py

# Standard library imports
import logging
from typing import List, Dict, Any, Optional

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
)
from scm.models.objects import (
    TagCreateModel,
    TagResponseModel,
    TagUpdateModel,
)
from scm.models.objects.tag import Colors
from scm.utils.tag_colors import normalize_color_name


class Tag(BaseObject):
    """
    Manages Tag objects in Palo Alto Networks' Strata Cloud Manager.
    """

    ENDPOINT = "/config/objects/v1/tags"
    DEFAULT_LIMIT = 10000

    def __init__(self, api_client):
        super().__init__(api_client)
        self.logger = logging.getLogger(__name__)

    def create(self, data: Dict[str, Any]) -> TagResponseModel:
        """
        Creates a new tag object.

        Returns:
            TagResponseModel
        """
        tag = TagCreateModel(**data)
        payload = tag.model_dump(exclude_unset=True)
        response: Dict[str, Any] = self.api_client.post(
            self.ENDPOINT,
            json=payload,
        )
        return TagResponseModel(**response)

    def get(self, object_id: str) -> TagResponseModel:
        """
        Gets a tag object by ID.

        Returns:
            TagResponseModel
        """
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.get(endpoint)
        return TagResponseModel(**response)

    def update(self, tag: TagUpdateModel) -> TagResponseModel:
        """
        Updates an existing tag object.

        Args:
            tag: TagUpdateModel instance containing the update data

        Returns:
            TagResponseModel
        """
        payload = tag.model_dump(exclude_unset=True)
        object_id = str(tag.id)
        payload.pop("id", None)

        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.put(
            endpoint,
            json=payload,
        )
        return TagResponseModel(**response)

    @staticmethod
    def _apply_filters(
        tags: List[TagResponseModel],
        filters: Dict[str, Any],
    ) -> List[TagResponseModel]:
        """
        Apply client-side filtering to the list of tags.

        Args:
            tags: List of TagResponseModel objects
            filters: Dictionary of filter criteria

        Returns:
            List[TagResponseModel]: Filtered list of tags
        """
        filter_criteria = tags

        # Filter by colors if provided
        if "colors" in filters:
            colors = filters["colors"]
            if not isinstance(colors, list):
                raise InvalidObjectError(
                    message="'colors' filter must be a list",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Object"},
                )

            normalized_filter_colors = set()
            for color_name in colors:
                normalized_name = normalize_color_name(color_name)
                standard_color_name = Colors.from_normalized_name(normalized_name)
                if standard_color_name is None:
                    valid_colors = [color for color in Colors]
                    raise InvalidObjectError(
                        message=f"Invalid color '{color_name}'. Valid colors are: {', '.join(valid_colors)}",
                        error_code="E003",
                        http_status_code=400,
                        details={"errorType": "Invalid Color"},
                    )
                normalized_filter_colors.add(standard_color_name)

            filter_criteria = [
                tag for tag in filter_criteria if tag.color in normalized_filter_colors
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
        exact_match: bool = False,
        exclude_folders: Optional[List[str]] = None,
        exclude_snippets: Optional[List[str]] = None,
        exclude_devices: Optional[List[str]] = None,
        **filters,
    ) -> List[TagResponseModel]:
        """
        Lists tag objects with optional filtering.

        Args:
            folder: Optional folder name
            snippet: Optional snippet name
            device: Optional device name
            exact_match (bool): If True, only return objects whose container (folder/snippet/device)
                                exactly matches the provided container parameter.
            exclude_folders (List[str], optional): List of folder names to exclude from results.
            exclude_snippets (List[str], optional): List of snippet values to exclude from results.
            exclude_devices (List[str], optional): List of device values to exclude from results.
            **filters: Additional filters including:
                - colors: List[str] - Filter by tag colors

        Returns:
            List[TagResponseModel]: A list of tag objects
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

        response = self.api_client.get(self.ENDPOINT, params=params)

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
                details={"field": "data", "error": '"data" field must be a list'},
            )

        tags = [TagResponseModel(**item) for item in response["data"]]

        # Apply standard filters first
        tags = self._apply_filters(tags, filters)

        # Determine which container key we are matching exactly, if exact_match is True
        # We know exactly one of folder/snippet/device is provided
        container_key, container_value = next(iter(container_parameters.items()))

        # If exact_match is True, filter out tags that don't match exactly
        if exact_match:
            tags = [t for t in tags if getattr(t, container_key) == container_value]

        # Exclude folders if provided
        if exclude_folders and isinstance(exclude_folders, list):
            tags = [t for t in tags if t.folder not in exclude_folders]

        # Exclude snippets if provided
        if exclude_snippets and isinstance(exclude_snippets, list):
            tags = [t for t in tags if t.snippet not in exclude_snippets]

        # Exclude devices if provided
        if exclude_devices and isinstance(exclude_devices, list):
            tags = [t for t in tags if t.device not in exclude_devices]

        return tags

    def fetch(
        self,
        name: str,
        folder: Optional[str] = None,
        snippet: Optional[str] = None,
        device: Optional[str] = None,
    ) -> TagResponseModel:
        """
        Fetches a single tag by name.

        Args:
            name (str): The name of the tag to fetch.
            folder (str, optional): The folder in which the resource is defined.
            snippet (str, optional): The snippet in which the resource is defined.
            device (str, optional): The device in which the resource is defined.

        Returns:
            TagResponseModel: The fetched tag object as a Pydantic model.
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

        response = self.api_client.get(self.ENDPOINT, params=params)

        if not isinstance(response, dict):
            raise InvalidObjectError(
                message="Invalid response format: expected dictionary",
                error_code="E003",
                http_status_code=500,
                details={"error": "Response is not a dictionary"},
            )

        if "id" in response:
            return TagResponseModel(**response)
        else:
            raise InvalidObjectError(
                message="Invalid response format: missing 'id' field",
                error_code="E003",
                http_status_code=500,
                details={"error": "Response missing 'id' field"},
            )

    def delete(self, object_id: str) -> None:
        """
        Deletes a tag object.

        Args:
            object_id (str): The ID of the object to delete.
        """
        endpoint = f"{self.ENDPOINT}/{object_id}"
        self.api_client.delete(endpoint)
