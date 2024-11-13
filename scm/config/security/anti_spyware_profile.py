# scm/config/security/anti_spyware_profile.py

from typing import List, Dict, Any, Optional
import logging
from scm.config import BaseObject
from scm.models.security import (
    AntiSpywareProfileCreateModel,
    AntiSpywareProfileResponseModel,
    AntiSpywareProfileUpdateModel,
)
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
    ErrorHandler,
    APIError,
)
from scm.utils.logging import setup_logger


class AntiSpywareProfile(BaseObject):
    """
    Manages Anti-Spyware Profile objects in Palo Alto Networks' Strata Cloud Manager.
    """

    ENDPOINT = "/config/security/v1/anti-spyware-profiles"
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
    ) -> AntiSpywareProfileResponseModel:
        """
        Creates a new anti-spyware profile object.

        Returns:
            AntiSpywareProfileResponseModel

        Raises:
            APIError: For any API-related errors
        """
        try:
            profile = AntiSpywareProfileCreateModel(**data)
            payload = profile.model_dump(exclude_unset=True)
            response = self.api_client.post(
                self.ENDPOINT,
                json=payload,
            )
            return AntiSpywareProfileResponseModel(**response)

        except Exception as e:
            if isinstance(e, APIError):
                self.logger.error(f"API error while creating anti-spyware profile: {e}")
                raise
            else:
                self.logger.error(
                    f"An unexpected error occurred while creating anti-spyware profile: {e}"
                )
                raise APIError("An unexpected error occurred") from e

    def get(
        self,
        object_id: str,
    ) -> AntiSpywareProfileResponseModel:
        """
        Gets an anti-spyware profile object by ID.

        Returns:
            AntiSpywareProfileResponseModel

        Raises:
            APIError: For any API-related errors
        """
        try:
            endpoint = f"{self.ENDPOINT}/{object_id}"
            response = self.api_client.get(endpoint)
            return AntiSpywareProfileResponseModel(**response)

        except Exception as e:
            self.logger.error(
                f"Error getting anti-spyware profile: {e}",
                exc_info=True,
            )
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
    ) -> AntiSpywareProfileResponseModel:
        """
        Updates an existing anti-spyware profile object.

        Returns:
            AntiSpywareProfileResponseModel

        Raises:
            APIError: For any API-related errors
        """
        try:
            profile = AntiSpywareProfileUpdateModel(**data)
            payload = profile.model_dump(exclude_unset=True)
            endpoint = f"{self.ENDPOINT}/{data['id']}"
            response = self.api_client.put(
                endpoint,
                json=payload,
            )
            return AntiSpywareProfileResponseModel(**response)

        except Exception as e:
            self.logger.error(
                f"Error updating anti-spyware profile: {e}",
                exc_info=True,
            )
            if hasattr(e, "response") and e.response is not None:  # noqa
                ErrorHandler.raise_for_error(
                    e.response.json(),
                    e.response.status_code,
                )
            else:
                raise APIError(f"An unexpected error occurred: {e}") from e

    @staticmethod
    def _apply_filters(
        profiles: List[AntiSpywareProfileResponseModel],
        filters: Dict[str, Any],
    ) -> List[AntiSpywareProfileResponseModel]:
        """
        Apply client-side filtering to the list of anti-spyware profiles.

        Args:
            profiles: List of AntiSpywareProfileResponseModel objects
            filters: Dictionary of filter criteria

        Returns:
            List[AntiSpywareProfileResponseModel]: Filtered list of profiles

        Raises:
            InvalidObjectError: If filter criteria are invalid
        """
        filter_criteria = profiles

        if "rules" in filters:
            if not isinstance(filters["rules"], list):
                raise InvalidObjectError("'rules' filter must be a list")
            rules = filters["rules"]
            filter_criteria = [
                profile
                for profile in filter_criteria
                if profile.rules and any(rule.name in rules for rule in profile.rules)
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
    ) -> List[AntiSpywareProfileResponseModel]:
        """
        Lists anti-spyware profile objects with optional filtering.

        Args:
            folder: Optional folder name
            snippet: Optional snippet name
            device: Optional device name
            **filters: Additional filters including:
                - rules: List[str] - Filter by rule names

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
            response = self.api_client.get(
                self.ENDPOINT,
                params=params,
            )

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

            profiles = [
                AntiSpywareProfileResponseModel(**item) for item in response["data"]
            ]
            return self._apply_filters(profiles, filters)

        except Exception as e:
            if isinstance(e, APIError):
                self.logger.error(f"API error while listing anti-spyware profiles: {e}")
                raise
            else:
                self.logger.error(
                    f"An unexpected error occurred while listing anti-spyware profiles: {e}"
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
        Fetches a single anti-spyware profile by name.

        Args:
            name (str): The name of the anti-spyware profile to fetch.
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
                profile = AntiSpywareProfileResponseModel(**response)
                return profile.model_dump(
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
                f"Error fetching anti-spyware profile: {e}",
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
        Deletes an anti-spyware profile object.

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
                f"Error deleting anti-spyware profile: {e}",
                exc_info=True,
            )
            if hasattr(e, "response") and e.response is not None:  # noqa
                ErrorHandler.raise_for_error(
                    e.response.json(),
                    e.response.status_code,
                )
            else:
                raise APIError(f"An unexpected error occurred: {e}") from e
