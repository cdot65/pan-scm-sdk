"""Mobile Agent Agent Profiles (Application Settings) configuration service for Strata Cloud Manager SDK.

Provides service class for managing GlobalProtect agent profiles via the SCM API. The
SCM UI refers to this resource as "App Settings" / "Application Settings".
"""

# scm/config/mobile_agent/agent_profiles.py

# Standard library imports
import logging
from typing import Any, Dict, List, Optional

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.mobile_agent import (
    AgentProfilesCreateModel,
    AgentProfilesResponseModel,
    AgentProfilesUpdateModel,
)


class AgentProfiles(BaseObject):
    """Manages GlobalProtect Agent Profiles (Application Settings) in Palo Alto Networks' Strata Cloud Manager.

    Agent profiles are addressed by name within the 'Mobile Users' folder. Unlike most
    SDK resources, the API exposes no `/{id}` paths for this resource: updates are
    performed against the collection endpoint and deletes are performed by name.

    Args:
        api_client: The API client instance
        max_limit (Optional[int]): Maximum number of objects to return in a single API request.
            Defaults to 2500. Must be between 1 and 5000.

    """

    ENDPOINT = "/config/mobile-agent/v1/agent-profiles"
    DEFAULT_MAX_LIMIT = 2500
    ABSOLUTE_MAX_LIMIT = 5000  # Maximum allowed by the API

    def __init__(
        self,
        api_client,
        max_limit: Optional[int] = None,
    ):
        """Initialize the AgentProfiles service with the given API client.

        Args:
            api_client: The API client instance.
            max_limit: Maximum number of items per API request. Defaults to API maximum.

        """
        super().__init__(api_client)
        self.logger = logging.getLogger(__name__)

        # Validate and set max_limit
        self._max_limit = self._validate_max_limit(max_limit)

    @property
    def max_limit(self) -> int:
        """Get the current maximum limit for API requests.

        Returns:
            int

        """
        return self._max_limit

    @max_limit.setter
    def max_limit(self, value: int) -> None:
        """Set a new maximum limit for API requests.

        Args:
            value: The maximum number of items to return in a single API request.

        """
        self._max_limit = self._validate_max_limit(value)

    def _validate_max_limit(self, limit: Optional[int]) -> int:
        """Validate the max_limit parameter.

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

    @staticmethod
    def _validate_folder(folder: str) -> None:
        """Validate that folder is 'Mobile Users'.

        Args:
            folder: The folder value to validate

        Raises:
            InvalidObjectError: If the folder is not 'Mobile Users'

        """
        if folder != "Mobile Users":
            raise InvalidObjectError(
                message="Folder must be 'Mobile Users' for GlobalProtect Agent Profiles",
                error_code="E003",
                http_status_code=400,
                details={"error": "Invalid folder value"},
            )

    def create(
        self,
        data: Dict[str, Any],
    ) -> AgentProfilesResponseModel:
        """Create a new GlobalProtect Agent Profile object.

        Args:
            data: Dictionary containing the agent profile configuration. Must include
                'folder' set to 'Mobile Users' (sent as a query parameter).

        Returns:
            AgentProfilesResponseModel

        """
        # Use the dictionary "data" to pass into Pydantic and return a modeled object
        profile = AgentProfilesCreateModel(**data)

        # Convert back to a Python dictionary, removing any unset fields and using aliases
        payload = profile.model_dump(
            exclude_unset=True,
            by_alias=True,
        )

        # Send the new object to the remote API as JSON; folder is a query parameter
        response: Dict[str, Any] = self.api_client.post(
            self.ENDPOINT,
            params={"folder": profile.folder},
            json=payload,
        )

        # Return the API response as a new Pydantic object
        return AgentProfilesResponseModel(**response)

    def update(
        self,
        data: Dict[str, Any],
    ) -> Optional[AgentProfilesResponseModel]:
        """Update an existing GlobalProtect Agent Profile object.

        The agent-profiles API has no `/{id}` path: the object is addressed by its
        name within the folder, both carried in the request body / query parameters.

        Args:
            data: Dictionary containing the agent profile configuration. Must include
                'name' and 'folder' set to 'Mobile Users'.

        Returns:
            Optional[AgentProfilesResponseModel]: The updated agent profile if the API
                returns a body, otherwise None (the API returns 200 OK with no content).

        """
        # Use the dictionary "data" to pass into Pydantic and return a modeled object
        profile = AgentProfilesUpdateModel(**data)

        # Convert back to a Python dictionary, removing any unset fields and using aliases
        payload = profile.model_dump(
            exclude_unset=True,
            by_alias=True,
        )

        # Send the updated object to the remote API as JSON; folder is a query parameter
        response = self.api_client.put(
            self.ENDPOINT,
            params={"folder": profile.folder},
            json=payload,
        )

        # The API returns 200 OK with no body for updates
        if isinstance(response, dict) and response:
            return AgentProfilesResponseModel(**response)
        return None

    def list(
        self,
        folder: str = "Mobile Users",
        name: Optional[str] = None,
        **filters,
    ) -> List[AgentProfilesResponseModel]:
        """List GlobalProtect Agent Profile objects with optional filtering.

        Args:
            folder: Folder name (defaults to "Mobile Users" as it's the only valid value)
            name: Optional name to filter on server-side
            **filters: Additional filters (not currently used but included for future expansion)

        Returns:
            List[AgentProfilesResponseModel]: A list of agent profile objects

        Raises:
            InvalidObjectError: If the provided data or response format is invalid.

        """
        self._validate_folder(folder)

        params: Dict[str, Any] = {"folder": folder}
        if name is not None:
            params["name"] = name

        limit = self._max_limit
        offset = 0
        all_objects: List[AgentProfilesResponseModel] = []

        try:
            while True:
                params.update({"limit": limit, "offset": offset})
                response = self.api_client.get(
                    self.ENDPOINT,
                    params=params,
                )

                # Handle direct list response (no pagination metadata available)
                if isinstance(response, list):
                    all_objects.extend(AgentProfilesResponseModel(**item) for item in response)
                    break

                # Handle dict response with data array
                if (
                    isinstance(response, dict)
                    and "data" in response
                    and isinstance(response["data"], list)
                ):
                    data_items = response["data"]
                    all_objects.extend(AgentProfilesResponseModel(**item) for item in data_items)
                    if len(data_items) < limit:
                        break
                    offset += limit
                    continue

                # Handle unexpected response format
                raise InvalidObjectError(
                    message="Invalid response format: expected list or dictionary with 'data' field",
                    error_code="E003",
                    http_status_code=500,
                    details={"error": "Response has invalid structure"},
                )
        except Exception as e:
            self.logger.error(f"Error listing agent profiles: {str(e)}")
            raise

        return all_objects

    def fetch(
        self,
        name: str,
        folder: str = "Mobile Users",
    ) -> AgentProfilesResponseModel:
        """Fetch a single GlobalProtect Agent Profile by name.

        Args:
            name: The name of the agent profile to fetch
            folder: The folder in which the resource is defined (must be "Mobile Users")

        Returns:
            AgentProfilesResponseModel: The fetched agent profile object

        Raises:
            MissingQueryParameterError: If a required query parameter is missing or empty.
            InvalidObjectError: If the provided data or response format is invalid.

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

        self._validate_folder(folder)

        # Filter server-side by name, then confirm the exact match client-side
        matching_profiles = [
            profile for profile in self.list(folder=folder, name=name) if profile.name == name
        ]

        if not matching_profiles:
            raise InvalidObjectError(
                message=f"Agent profile '{name}' not found",
                error_code="E002",
                http_status_code=404,
                details={"error": "No matching agent profile found"},
            )

        if len(matching_profiles) > 1:
            self.logger.warning(f"Multiple agent profiles found for '{name}'. Using the first one.")

        return matching_profiles[0]

    def delete(
        self,
        name: str,
        folder: str = "Mobile Users",
    ) -> None:
        """Delete a GlobalProtect Agent Profile object.

        The agent-profiles API has no `/{id}` path: the object is deleted by its name
        within the folder, both passed as query parameters.

        Args:
            name: The name of the agent profile to delete
            folder: The folder in which the resource is defined (must be "Mobile Users")

        Raises:
            MissingQueryParameterError: If a required query parameter is missing or empty.
            InvalidObjectError: If the folder is not 'Mobile Users'.

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

        self._validate_folder(folder)

        self.api_client.delete(
            self.ENDPOINT,
            params={"name": name, "folder": folder},
        )
