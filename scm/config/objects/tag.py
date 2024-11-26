# scm/config/objects/tag.py

# Standard library imports
import logging
from typing import List, Dict, Any, Optional

# External libraries
from requests import Response
from requests.exceptions import HTTPError

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
    ErrorHandler,
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

    def __init__(
        self,
        api_client,
    ):
        super().__init__(api_client)
        self.logger = logging.getLogger(__name__)

    def create(
        self,
        data: Dict[str, Any],
    ) -> TagResponseModel:
        """
        Creates a new tag object.

        Returns:
            TagResponseModel

        Raises:
            Custom Error Handling class response
        """
        try:
            # Use the dictionary "data" to pass into Pydantic and return a modeled object
            tag = TagCreateModel(**data)

            # Convert back to a Python dictionary, removing any unset fields
            payload = tag.model_dump(exclude_unset=True)

            # Send the updated object to the remote API as JSON
            response: Dict[str, Any] = self.api_client.post(
                self.ENDPOINT,
                json=payload,
            )

            # Return the SCM API response as a new Pydantic object
            return TagResponseModel(**response)

        except HTTPError as e:
            # create an object of the type Response and store the contents of e.response within it
            response: Optional[Response] = e.response

            # if the response is not none, and there is data within response.content
            if response is not None and response.content:

                # Perform our custom exception handler by sending the response.json() object and http status code
                ErrorHandler.raise_for_error(
                    response.json(),
                    response.status_code,
                )
            else:
                self.logger.error("No response content available for error parsing.")
                raise

    def get(
        self,
        object_id: str,
    ) -> TagResponseModel:
        """
        Gets a tag object by ID.

        Returns:
            TagResponseModel

        Raises:
            Custom Error Handling class response
        """
        try:
            # Send the request to the remote API
            endpoint = f"{self.ENDPOINT}/{object_id}"
            response: Dict[str, Any] = self.api_client.get(endpoint)

            # Return the SCM API response as a new Pydantic object
            return TagResponseModel(**response)

        except HTTPError as e:
            # create an object of the type Response and store the contents of e.response within it
            response: Optional[Response] = e.response

            # if the response is not none, and there is data within response.content
            if response is not None and response.content:

                # Perform our custom exception handler by sending the response.json() object and http status code
                ErrorHandler.raise_for_error(
                    response.json(),
                    response.status_code,
                )
            else:
                self.logger.error("No response content available for error parsing.")
                raise

    def update(
        self,
        data: Dict[str, Any],
    ) -> TagResponseModel:
        """
        Updates an existing tag object.

        Returns:
            TagResponseModel

        Raises:
            Custom Error Handling class response
        """
        try:
            # Use the dictionary "data" to pass into Pydantic and return a modeled object
            tag = TagUpdateModel(**data)

            # Convert back to a Python dictionary, removing any unset fields
            payload = tag.model_dump(exclude_unset=True)

            # Send the updated object to the remote API as JSON
            endpoint = f"{self.ENDPOINT}/{data['id']}"
            response: Dict[str, Any] = self.api_client.put(
                endpoint,
                json=payload,
            )

            # Return the SCM API response as a new Pydantic object
            return TagResponseModel(**response)

        except HTTPError as e:
            # create an object of the type Response and store the contents of e.response within it
            response: Optional[Response] = e.response

            # if the response is not none, and there is data within response.content
            if response is not None and response.content:

                # Perform our custom exception handler by sending the response.json() object and http status code
                ErrorHandler.raise_for_error(
                    response.json(),
                    response.status_code,
                )
            else:
                self.logger.error("No response content available for error parsing.")
                raise

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

        Raises:
            InvalidObjectError: If filter criteria are invalid
        """

        filter_criteria = tags

        # Filter by colors
        if "colors" in filters:
            if not isinstance(filters["colors"], list):
                raise InvalidObjectError(
                    message="'colors' filter must be a list",
                    error_code="E003",
                    http_status_code=500,
                    details={"errorType": "Invalid Object"},
                )
            colors = filters["colors"]

            # Normalize and validate the filter colors
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
                # Add the standard color name to the set
                normalized_filter_colors.add(standard_color_name)

            # Now filter the tags
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
        **filters,
    ) -> List[TagResponseModel]:
        """
        Lists tag objects with optional filtering.

        Raises:
            EmptyFieldError: If provided container fields are empty
            FolderNotFoundError: If the specified folder doesn't exist
            ValidationError: If the container parameters are invalid
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
            response = self.api_client.get(
                self.ENDPOINT,
                params=params,
            )

            if not isinstance(response, dict):
                raise InvalidObjectError(
                    "Invalid response format: expected dictionary",
                    error_code="E003",
                    http_status_code=500,
                )

            if "data" not in response:
                raise InvalidObjectError(
                    "Invalid response format: missing 'data' field",
                    error_code="E003",
                    http_status_code=500,
                )

            if not isinstance(response["data"], list):
                raise InvalidObjectError(
                    "Invalid response format: 'data' field must be a list",
                    error_code="E003",
                    http_status_code=500,
                )

            tags = [TagResponseModel(**item) for item in response["data"]]

            return self._apply_filters(
                tags,
                filters,
            )

        except HTTPError as e:
            # create an object of the type Response and store the contents of e.response within it
            response: Optional[Response] = e.response

            # if the response is not none, and there is data within response.content
            if response is not None and response.content:

                # Perform our custom exception handler by sending the response.json() object and http status code
                ErrorHandler.raise_for_error(
                    response.json(),
                    response.status_code,
                )
            else:
                self.logger.error("No response content available for error parsing.")
                raise

    def fetch(
        self,
        name: str,
        folder: Optional[str] = None,
        snippet: Optional[str] = None,
        device: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Fetches a single object by name.

        Raises:
            EmptyFieldError: If name or container fields are empty
            FolderNotFoundError: If the specified folder doesn't exist
            ObjectNotPresentError: If the object is not found
            ValidationError: If the parameters are invalid
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
                raise InvalidObjectError(
                    "Invalid response format: expected dictionary",
                    error_code="E003",
                    http_status_code=500,
                )

            if "id" in response:
                tag = TagResponseModel(**response)
                return tag.model_dump(
                    exclude_unset=True,
                    exclude_none=True,
                )
            else:
                raise InvalidObjectError(
                    "Invalid response format: missing 'id' field",
                    error_code="E003",
                    http_status_code=500,
                )

        except HTTPError as e:
            # create an object of the type Response and store the contents of e.response within it
            response: Optional[Response] = e.response

            # if the response is not none, and there is data within response.content
            if response is not None and response.content:

                # Perform our custom exception handler by sending the response.json() object and http status code
                ErrorHandler.raise_for_error(
                    response.json(),
                    response.status_code,
                )
            else:
                self.logger.error("No response content available for error parsing.")
                raise

    def delete(
        self,
        object_id: str,
    ) -> None:
        """
        Deletes a tag object.

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

        except HTTPError as e:
            # create an object of the type Response and store the contents of e.response within it
            response: Optional[Response] = e.response

            # if the response is not none, and there is data within response.content
            if response is not None and response.content:

                # Perform our custom exception handler by sending the response.json() object and http status code
                ErrorHandler.raise_for_error(
                    response.json(),
                    response.status_code,
                )
            else:
                self.logger.error("No response content available for error parsing.")
                raise
