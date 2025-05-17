"""Mobile Agent Versions configuration service for Strata Cloud Manager SDK.

Provides service class for managing agent version objects via the SCM API.
"""

# scm/config/mobile_agent/agent_versions.py

# Standard library imports
import logging
from typing import Any, Dict, List, Optional

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.mobile_agent.agent_versions import AgentVersionsModel


class AgentVersions(BaseObject):
    """Manages GlobalProtect Agent Version objects in Palo Alto Networks' Strata Cloud Manager.

    Args:
        api_client: The API client instance
        max_limit (Optional[int]): Maximum number of objects to return in a single API request.
            Defaults to 200. Must be between 1 and 1000.

    """

    ENDPOINT = "/config/mobile-agent/v1/agent-versions"
    DEFAULT_MAX_LIMIT = 200
    ABSOLUTE_MAX_LIMIT = 1000

    def __init__(
        self,
        api_client,
        max_limit: Optional[int] = None,
    ):
        """Initialize the AgentVersions service with the given API client."""
        super().__init__(api_client)
        self.logger = logging.getLogger(__name__)

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
    def _apply_filters(
        versions: List[str],
        filters: Dict[str, Any],
    ) -> List[str]:
        """Apply client-side filtering to the list of agent versions.

        Args:
            versions: List of version strings
            filters: Dictionary of filter criteria

        Returns:
            List[str]: Filtered list of versions

        """
        filtered_versions = versions

        # Filter by version substring
        if "version" in filters:
            version_filter = filters["version"]
            if isinstance(version_filter, list):
                # If the list is empty, no results should be returned
                if not version_filter:
                    return []
                filtered_versions = [
                    ver
                    for ver in filtered_versions
                    if any(v.lower() in ver.lower() for v in version_filter)
                ]
            else:
                filtered_versions = [
                    ver for ver in filtered_versions if version_filter.lower() in ver.lower()
                ]

        # Filter by version prefix
        if "prefix" in filters:
            prefix_filter = filters["prefix"]
            if isinstance(prefix_filter, list):
                # If the list is empty, no results should be returned
                if not prefix_filter:
                    return []
                filtered_versions = [
                    ver
                    for ver in filtered_versions
                    if any(ver.lower().startswith(p.lower()) for p in prefix_filter)
                ]
            else:
                filtered_versions = [
                    ver
                    for ver in filtered_versions
                    if ver.lower().startswith(prefix_filter.lower())
                ]

        return filtered_versions

    def list(
        self,
        **filters,
    ) -> List[str]:
        """List all available GlobalProtect agent versions with optional filtering.

        Args:
            **filters: Additional filters including:
                - version: str or List[str] - Filter by version substring
                - prefix: str or List[str] - Filter by version prefix

        Returns:
            List[str]: A list of GlobalProtect agent version strings

        """
        response = self.api_client.get(
            self.ENDPOINT,
        )

        # Convert the response to the AgentVersionsModel
        agent_versions_model = AgentVersionsModel(**response)
        all_versions = agent_versions_model.agent_versions

        # Apply filters
        filtered_versions = self._apply_filters(
            all_versions,
            filters,
        )

        return filtered_versions

    def fetch(
        self,
        version: str,
    ) -> str:
        """Fetch a single agent version by exact match.

        Args:
            version: The exact version string to fetch

        Returns:
            str: The matched version string

        Raises:
            InvalidObjectError: If the version is not found
            MissingQueryParameterError: If the version parameter is empty

        """
        if not version:
            raise MissingQueryParameterError(
                message="Field 'version' cannot be empty",
                error_code="E003",
                http_status_code=400,
                details={
                    "field": "version",
                    "error": '"version" is not allowed to be empty',
                },
            )

        # Get all versions
        all_versions = self.list()

        # Find the version with the exact match (case-insensitive)
        matching_versions = [v for v in all_versions if v.lower() == version.lower()]

        if not matching_versions:
            raise InvalidObjectError(
                message=f"GlobalProtect agent version '{version}' not found",
                error_code="E005",
                http_status_code=404,
                details={"error": "Object not found"},
            )

        if len(matching_versions) > 1:
            self.logger.warning(
                f"Multiple agent versions found matching '{version}'. Using the first one."
            )

        return matching_versions[0]
