"""Insights API integration for SCM SDK."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar

from pydantic import BaseModel
import requests

from scm.models.insights.common import InsightsResponse

T = TypeVar("T", bound=BaseModel)


class InsightsBaseObject(ABC):
    """Base class for Insights API services.

    This class provides common functionality for all Insights services
    which use a query-based API pattern instead of standard CRUD operations.
    """

    INSIGHTS_BASE_URL = "https://api.strata.paloaltonetworks.com/insights/v3.0"
    REGION_HEADER = "americas"  # Fixed region header for v3.0

    def __init__(self, api_client):
        """Initialize InsightsBaseObject with API client."""
        self._client = api_client

    @abstractmethod
    def get_resource_endpoint(self) -> str:
        """Get the specific resource endpoint for this service.

        Returns:
            str: The resource-specific part of the endpoint (e.g., "resource/query/alerts")
        """
        pass

    def _prepare_headers(self) -> Dict[str, str]:
        """Prepare headers for Insights API requests.

        Returns:
            Dict[str, str]: Headers including region header
        """
        headers = {"X-PANW-Region": self.REGION_HEADER, "Content-Type": "application/json"}

        # Add Prisma-Tenant header with TSG ID
        if hasattr(self._client, "oauth_client") and self._client.oauth_client:
            tsg_id = self._client.oauth_client.auth_request.tsg_id
            if tsg_id:
                headers["prisma-tenant"] = tsg_id

        return headers

    def query(
        self,
        *,
        properties: Optional[List[Dict[str, Any]]] = None,
        filter: Optional[Dict[str, Any]] = None,
        count: Optional[int] = None,
        histogram: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> InsightsResponse:
        """Execute a query against the Insights API.

        Args:
            properties: List of properties to include in the response
            filter: Filter rules for the query
            count: Maximum number of results to return
            histogram: Histogram configuration for time-series data
            **kwargs: Additional query parameters

        Returns:
            InsightsResponse: Typed response with header and data
        """
        # Build query payload
        payload = {}

        if properties is not None:
            payload["properties"] = properties

        if filter is not None:
            payload["filter"] = filter

        if count is not None:
            payload["count"] = count

        if histogram is not None:
            payload["histogram"] = histogram

        # Add any additional parameters
        payload.update(kwargs)

        # Build the full URL for Insights API
        endpoint = f"{self.INSIGHTS_BASE_URL}/{self.get_resource_endpoint()}"

        # Get additional headers
        headers = self._prepare_headers()

        # Make a direct request since Insights API uses a different base URL
        # Get the auth token from the client
        auth_headers = {}

        # Check if using OAuth2 client
        if hasattr(self._client, "oauth_client") and self._client.oauth_client:
            if self._client.oauth_client.session.token:
                token = self._client.oauth_client.session.token.get("access_token")
                if token:
                    auth_headers["Authorization"] = f"Bearer {token}"
        # Check if using bearer token mode
        elif (
            hasattr(self._client.session, "headers")
            and "Authorization" in self._client.session.headers
        ):
            auth_headers["Authorization"] = self._client.session.headers["Authorization"]

        # Combine headers
        all_headers = {**auth_headers, **headers}

        # Make the request
        response = requests.post(
            endpoint, json=payload, headers=all_headers, verify=self._client.verify_ssl
        )

        # Handle response
        response.raise_for_status()
        data = response.json()

        # Return typed response
        return InsightsResponse(**data)

    def list(self, **kwargs) -> List[Dict[str, Any]]:
        """List resources using the query API.

        This is a convenience method that wraps the query method
        with common list operation parameters.

        Args:
            **kwargs: Query parameters

        Returns:
            List[Dict[str, Any]]: List of resources
        """
        # Extract common list parameters
        max_results = kwargs.pop("max_results", 100)

        # Set default count if not provided
        if "count" not in kwargs:
            kwargs["count"] = max_results

        # Execute query
        result = self.query(**kwargs)

        # Extract data from response
        # result is now an InsightsResponse object
        return result.data

    def get(self, resource_id: str, **kwargs) -> Dict[str, Any]:
        """Get a specific resource by ID.

        Note: Not all Insights resources support direct ID lookup.
        This method attempts to filter by common ID fields.

        Args:
            resource_id: The resource ID to retrieve
            **kwargs: Additional query parameters

        Returns:
            Dict[str, Any]: The resource data

        Raises:
            ValueError: If resource not found
        """
        # Build filter for specific ID
        # Try common ID field names
        id_fields = ["id", "alert_id", "tunnel_id", "connection_id", "user_id", "location_id"]

        for id_field in id_fields:
            filter_rules = [{"property": id_field, "operator": "equals", "values": [resource_id]}]

            kwargs["filter"] = {"rules": filter_rules}
            kwargs["count"] = 1

            results = self.list(**kwargs)
            if results:
                return results[0]

        raise ValueError(f"Resource with ID '{resource_id}' not found")

    # Override methods that don't apply to Insights API
    def create(self, *args, **kwargs):
        """Create operation not supported for Insights API."""
        raise NotImplementedError("Create operation is not supported for Insights resources")

    def update(self, *args, **kwargs):
        """Update operation not supported for Insights API."""
        raise NotImplementedError("Update operation is not supported for Insights resources")

    def delete(self, *args, **kwargs):
        """Delete operation not supported for Insights API."""
        raise NotImplementedError("Delete operation is not supported for Insights resources")
