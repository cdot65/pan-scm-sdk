# scm/client.py

# Standard library imports
import logging
import sys
import time
from typing import Optional, Dict, Any, List

# External libraries
from requests.exceptions import HTTPError

# Local SDK imports
from scm.auth import OAuth2Client
from scm.exceptions import (
    APIError,
    ErrorHandler,
)
from scm.models.auth import AuthRequestModel
from scm.models.operations import (
    CandidatePushRequestModel,
    CandidatePushResponseModel,
    JobStatusResponse,
    JobListResponse,
)


class Scm:
    """
    A client for interacting with the Palo Alto Networks Strata Cloud Manager API.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        tsg_id: str,
        api_base_url: str = "https://api.strata.paloaltonetworks.com",
        log_level: str = "ERROR",
    ):
        self.api_base_url = api_base_url

        # Map string log level to numeric level
        numeric_level = getattr(logging, log_level.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError(f"Invalid log level: {log_level}")

        # Configure the 'scm' logger
        self.logger = logging.getLogger("scm")
        self.logger.setLevel(numeric_level)

        # Add a handler if the logger doesn't have one
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(numeric_level)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        # Create the AuthRequestModel object
        try:
            auth_request = AuthRequestModel(
                client_id=client_id,
                client_secret=client_secret,
                tsg_id=tsg_id,
            )
        except ValueError as e:
            # Let exception propagate
            raise APIError(f"Authentication initialization failed: {e}") from e

        self.logger.debug(f"Auth request: {auth_request.model_dump()}")
        self.oauth_client = OAuth2Client(auth_request)
        self.session = self.oauth_client.session
        self.logger.debug(f"Session created: {self.session.headers}")

    def request(
        self,
        method: str,
        endpoint: str,
        **kwargs,
    ):
        """
        Handles the API request and returns the response JSON or None if no content is present.

        Args:
            method: HTTP method to be used for the request (e.g., 'GET', 'POST').
            endpoint: The API endpoint to which the request is made.
            **kwargs: Additional arguments to be passed to the request (e.g., headers, params, data).
        """
        url = f"{self.api_base_url}{endpoint}"
        self.logger.debug(f"Making {method} request to {url} with params {kwargs}")

        try:
            response = self.session.request(
                method,
                url,
                **kwargs,
            )
            response.raise_for_status()

            if response.content and response.content.strip():
                return response.json()
            else:
                return None  # Return None or an empty dict

        except HTTPError as e:
            # Handle HTTP errors
            response = e.response
            if response is not None and response.content:
                error_content = response.json()
                ErrorHandler.raise_for_error(
                    error_content,
                    response.status_code,
                )
            else:
                raise APIError(f"HTTP error occurred: {e}") from e

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        """
        Sends a GET request to the SCM API.
        """
        if self.oauth_client.is_expired:
            self.oauth_client.refresh_token()
        return self.request(
            "GET",
            endpoint,
            params=params,
            **kwargs,
        )

    def post(
        self,
        endpoint: str,
        **kwargs,
    ):
        """
        Sends a POST request to the SCM API.
        """
        if self.oauth_client.is_expired:
            self.oauth_client.refresh_token()
        return self.request(
            "POST",
            endpoint,
            **kwargs,
        )

    def put(
        self,
        endpoint: str,
        **kwargs,
    ):
        """
        Sends a PUT request to the SCM API.
        """
        if self.oauth_client.is_expired:
            self.oauth_client.refresh_token()
        return self.request(
            "PUT",
            endpoint,
            **kwargs,
        )

    def delete(
        self,
        endpoint: str,
        **kwargs,
    ):
        """
        Sends a DELETE request to the SCM API.
        """
        if self.oauth_client.is_expired:
            self.oauth_client.refresh_token()
        return self.request(
            "DELETE",
            endpoint,
            **kwargs,
        )

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
        # Make API request with just pagination parameters
        response = self.get(
            "/config/operations/v1/jobs",
            params={
                "limit": limit,
                "offset": offset,
            },
        )

        # Convert to Pydantic model
        jobs_response = JobListResponse(**response)

        # If parent_id filter is specified, filter the jobs
        if parent_id is not None:
            filtered_data = [
                job for job in jobs_response.data if job.parent_id == parent_id
            ]
            jobs_response.data = filtered_data
            jobs_response.total = len(filtered_data)

        return jobs_response

    def get_job_status(self, job_id: str) -> JobStatusResponse:
        """
        Get the status of a job.

        Args:
            job_id: The ID of the job to check

        Returns:
            JobStatusResponse: The job status response
        """
        response = self.get(f"/config/operations/v1/jobs/{job_id}")
        return JobStatusResponse(**response)

    def wait_for_job(
        self, job_id: str, timeout: int = 300, poll_interval: int = 10
    ) -> Optional[JobStatusResponse]:
        """
        Wait for a job to complete.

        Args:
            job_id: The ID of the job to check
            timeout: Maximum time to wait in seconds (default: 300)
            poll_interval: Time between status checks in seconds (default: 10)

        Returns:
            JobStatusResponse: The final job status response

        Raises:
            TimeoutError: If the job doesn't complete within the timeout period
        """
        start_time = time.time()
        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError(
                    f"Job {job_id} did not complete within {timeout} seconds"
                )

            status = self.get_job_status(job_id)
            if not status.data:
                time.sleep(poll_interval)
                continue

            job_status = status.data[0]
            if job_status.status_str == "FIN":
                return status

            time.sleep(poll_interval)

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

        Args:
            folders: List of folder names to commit changes from
            description: Description of the commit
            admin: List of admin emails. Defaults to client_id if not provided
            sync: Whether to wait for job completion
            timeout: Maximum time to wait for job completion in seconds

        Returns:
            CandidatePushResponseModel: Response containing job information
        """
        if admin is None:
            admin = [self.oauth_client.auth_request.client_id]

        commit_request = CandidatePushRequestModel(
            folders=folders,
            admin=admin,
            description=description,
        )

        self.logger.debug(f"Commit request: {commit_request.model_dump()}")

        response = self.post(
            "/config/operations/v1/config-versions/candidate:push",
            json=commit_request.model_dump(),
        )

        commit_response = CandidatePushResponseModel(**response)

        if sync and commit_response.success and commit_response.job_id:
            try:
                final_status = self.wait_for_job(
                    commit_response.job_id, timeout=timeout
                )
                if final_status:
                    self.logger.info(
                        f"Commit job {commit_response.job_id} completed: "
                        f"{final_status.data[0].result_str}"
                    )
            except TimeoutError as e:
                self.logger.error(f"Commit job timed out: {str(e)}")
                raise

        return commit_response
