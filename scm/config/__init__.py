# scm/config/__init__.py

from typing import List, Dict, Any, Optional

from scm.client import Scm
from scm.models.operations import (
    CandidatePushResponseModel,
    JobStatusResponse,
    JobListResponse,
)


class BaseObject:
    """
    Base class for configuration objects in the SDK, providing CRUD operations.

    This class implements common methods for creating, retrieving, updating, deleting,
    and listing configuration objects through the API client.

    Attributes:
        ENDPOINT (str): API endpoint for the object, to be defined in subclasses.
        api_client (Scm): Instance of the API client for making HTTP requests.

    Error:
        APIError: May be raised for any API-related errors during operations.

    Return:
        Dict[str, Any] or List[Dict[str, Any]]: API response data for CRUD operations.
    """

    ENDPOINT: str  # Should be defined in subclasses

    def __init__(self, api_client: Scm):
        # Check if ENDPOINT is defined
        if not hasattr(self, "ENDPOINT"):
            raise AttributeError("ENDPOINT must be defined in the subclass")

        # Validate api_client type
        if not isinstance(api_client, Scm):
            raise TypeError("api_client must be an instance of Scm")

        self.api_client = api_client

    # CRUD methods
    def create(
        self,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        response = self.api_client.post(
            self.ENDPOINT,
            json=data,
        )
        return response

    def get(
        self,
        object_id: str,
    ) -> Dict[str, Any]:
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response = self.api_client.get(endpoint)
        return response

    def update(
        self,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        endpoint = f"{self.ENDPOINT}/{data['id']}"
        response = self.api_client.put(
            endpoint,
            json=data,
        )
        return response

    def delete(
        self,
        object_id: str,
    ) -> None:
        endpoint = f"{self.ENDPOINT}/{object_id}"
        self.api_client.delete(endpoint)

    def list(
        self,
        **filters,
    ) -> List[Dict[str, Any]]:
        params = {k: v for k, v in filters.items() if v is not None}
        response = self.api_client.get(
            self.ENDPOINT,
            params=params,
        )
        return response.get("data", [])

    def list_jobs(
        self,
        limit: int = 100,
        offset: int = 0,
        parent_id: Optional[str] = None,
    ) -> JobListResponse:
        """
        List jobs in SCM with pagination support and optional parent ID filtering.

        Args:
            limit: Maximum number of jobs to return (default: 100)
            offset: Number of jobs to skip (default: 0)
            parent_id: Filter jobs by parent job ID (default: None)

        Returns:
            JobListResponse: Paginated list of jobs
        """
        return self.api_client.list_jobs(
            limit=limit,
            offset=offset,
            parent_id=parent_id,
        )

    def get_job_status(self, job_id: str) -> JobStatusResponse:
        """
        Get the status of a job.

        Args:
            job_id: The ID of the job to check

        Returns:
            JobStatusResponse: The job status response
        """
        return self.api_client.get_job_status(job_id)

    def commit(
        self,
        folders: List[str],
        description: str,
        admin: Optional[List[str]] = None,
        sync: bool = False,
        timeout: int = 300,
    ) -> CandidatePushResponseModel:
        """
        Commits configuration changes to SCM.

        This method proxies to the api_client's commit method.

        Args:
            folders: List of folder names to commit changes from
            description: Description of the commit
            admin: List of admin emails
            sync: Whether to wait for job completion
            timeout: Maximum time to wait for job completion in seconds

        Returns:
            CandidatePushResponseModel: Response containing job information
        """
        return self.api_client.commit(
            folders=folders,
            description=description,
            admin=admin,
            sync=sync,
            timeout=timeout,
        )
