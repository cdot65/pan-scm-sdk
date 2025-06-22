"""SCM API client for Strata Cloud Manager SDK.

This module defines the main Scm client class, supporting authentication and
HTTP operations for interacting with the Palo Alto Networks Strata Cloud Manager REST API.
"""

# scm/client.py

# Standard library imports
import importlib
import logging
import sys
import time
from typing import Any, Dict, List, Optional

# External libraries
# trunk-ignore(mypy/note)
# trunk-ignore(mypy/import-untyped)
from requests.exceptions import HTTPError

# Local SDK imports
from scm.auth import OAuth2Client
from scm.exceptions import APIError, ErrorHandler
from scm.models.auth import AuthRequestModel
from scm.models.operations import (
    CandidatePushRequestModel,
    CandidatePushResponseModel,
    JobListResponse,
    JobStatusResponse,
)

# External dependency for HTTP


# Ensure requests is imported at module level for patching in tests


class Scm:
    """A client for interacting with the Palo Alto Networks Strata Cloud Manager API.

    This client supports two authentication methods:
    1. OAuth2 client credentials flow (requires client_id, client_secret, and tsg_id)
    2. Bearer token authentication (requires access_token)

    Args:
        client_id: OAuth client ID for authentication (required when not using access_token)
        client_secret: OAuth client secret for authentication (required when not using access_token)
        tsg_id: Tenant Service Group ID for scope construction (required when not using access_token)
        api_base_url: Base URL for the SCM API (default: "https://api.strata.paloaltonetworks.com")
        token_url: URL for obtaining OAuth tokens (default: "https://auth.apps.paloaltonetworks.com/am/oauth2/access_token")
        log_level: Logging level (default: "ERROR")
        access_token: Pre-acquired OAuth2 bearer token for stateless authentication
            When provided, client_id, client_secret, and tsg_id are not required.
            Token refresh is the caller's responsibility when using this mode.
        verify_ssl: Whether to verify TLS certificates for all requests (default: True). Set to False to bypass TLS verification (insecure!).

    """

    # trunk-ignore(bandit/B107)
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        tsg_id: Optional[str] = None,
        api_base_url: str = "https://api.strata.paloaltonetworks.com",
        token_url: str = "https://auth.apps.paloaltonetworks.com/am/oauth2/access_token",
        log_level: str = "ERROR",
        access_token: Optional[str] = None,
        verify_ssl: bool = True,
    ):
        """Initialize the ScmClient with the provided client_id, client_secret, tsg_id, API URLs, log level, access token, and TLS verification flag."""
        self.api_base_url = api_base_url
        self.verify_ssl = verify_ssl
        self.oauth_client = None

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
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        # Initialize service cache for unified client access
        self._services = {}

        # Warn and suppress urllib3 InsecureRequestWarning if TLS verification is disabled
        if not self.verify_ssl:
            import warnings

            import urllib3

            warnings.simplefilter("always", urllib3.exceptions.InsecureRequestWarning)
            warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)
            self.logger.warning(
                "TLS certificate verification is disabled (verify_ssl=False). "
                "This is insecure and exposes you to man-in-the-middle attacks. "
                "See: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#tls-warnings"
            )

        # Bearer token authentication mode
        if access_token:
            self.logger.debug("Using bearer token authentication mode")

            # Create a standard requests session with the bearer token
            import requests

            self.session = requests.Session()
            self.session.headers["Authorization"] = f"Bearer {access_token}"
            self.session.verify = self.verify_ssl
            self.logger.debug(
                f"Session created with bearer token: {self.session.headers}, verify_ssl={self.verify_ssl}"
            )
            return

        # OAuth2 client credentials flow authentication mode
        if not all([client_id, client_secret, tsg_id]):
            raise APIError(
                "When not using access_token, client_id, client_secret, and tsg_id are required"
            )

        self.logger.debug("Using OAuth2 client credentials authentication mode")

        # Create the AuthRequestModel object
        auth_request = AuthRequestModel(
            client_id=client_id,
            client_secret=client_secret,
            tsg_id=tsg_id,
            token_url=token_url,
        )

        self.logger.debug(f"Auth request: {auth_request.model_dump()}")
        self.oauth_client = OAuth2Client(auth_request, verify_ssl=self.verify_ssl)
        self.session = self.oauth_client.session
        self.logger.debug(f"Session created: {self.session.headers}, verify_ssl={self.verify_ssl}")

    def request(
        self,
        method: str,
        endpoint: str,
        **kwargs,
    ):
        """Handle the API request and return the response JSON or None if no content is present.

        Args:
            method: HTTP method to be used for the request (e.g., 'GET', 'POST').
            endpoint: The API endpoint to which the request is made.
            **kwargs: Additional arguments to be passed to the request (e.g., headers, params, data).

        """
        url = f"{self.api_base_url}{endpoint}"
        self.logger.debug(f"Making {method} request to {url} with params {kwargs}")

        # Always pass verify unless explicitly set by caller
        if "verify" not in kwargs:
            kwargs["verify"] = self.verify_ssl
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
        """Send a GET request to the SCM API.

        In OAuth2 client credentials mode, automatically refreshes the token if expired.
        In bearer token mode, the token is used as-is with no refresh capability.
        """
        # Only check token expiration if using OAuth2 client credentials flow
        if self.oauth_client and self.oauth_client.is_expired:
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
        """Send a POST request to the SCM API.

        In OAuth2 client credentials mode, automatically refreshes the token if expired.
        In bearer token mode, the token is used as-is with no refresh capability.
        """
        # Only check token expiration if using OAuth2 client credentials flow
        if self.oauth_client and self.oauth_client.is_expired:
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
        """Send a PUT request to the SCM API.

        In OAuth2 client credentials mode, automatically refreshes the token if expired.
        In bearer token mode, the token is used as-is with no refresh capability.
        """
        # Only check token expiration if using OAuth2 client credentials flow
        if self.oauth_client and self.oauth_client.is_expired:
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
        """Send a DELETE request to the SCM API.

        In OAuth2 client credentials mode, automatically refreshes the token if expired.
        In bearer token mode, the token is used as-is with no refresh capability.
        """
        # Only check token expiration if using OAuth2 client credentials flow
        if self.oauth_client and self.oauth_client.is_expired:
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
        """List jobs in SCM with pagination support and optional parent ID filtering.

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
            filtered_data = [job for job in jobs_response.data if job.parent_id == parent_id]
            jobs_response.data = filtered_data
            jobs_response.total = len(filtered_data)

        return jobs_response

    def get_job_status(self, job_id: str) -> JobStatusResponse:
        """Get the status of a job.

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
        """Wait for a job to complete.

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
                raise TimeoutError(f"Job {job_id} did not complete within {timeout} seconds")

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
        """Commit configuration changes to SCM.

        Args:
            folders: List of folder names to commit changes from
            description: Description of the commit
            admin: List of admin emails. Defaults to client_id if not provided
            sync: Whether to wait for job completion
            timeout: Maximum time to wait for job completion in seconds

        Returns:
            CandidatePushResponseModel: Response containing job information

        """
        # If using bearer token mode and admin is None, we need to specify an admin
        if admin is None:
            if self.oauth_client:
                admin = [self.oauth_client.auth_request.client_id]
            else:
                # When using a bearer token, we need to provide an admin explicitly
                raise APIError(
                    "When using bearer token authentication, 'admin' must be provided for commit operations"
                )

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
                final_status = self.wait_for_job(commit_response.job_id, timeout=timeout)
                if final_status:
                    self.logger.info(
                        f"Commit job {commit_response.job_id} completed: "
                        f"{final_status.data[0].result_str}"
                    )
            except TimeoutError as e:
                self.logger.error(f"Commit job timed out: {str(e)}")
                raise

        return commit_response

    def __getattr__(self, name: str) -> Any:
        """Dynamic attribute access to support unified client access pattern (api_client.service).

        This method allows accessing service objects as attributes like:
        api_client.address, api_client.tag, etc.

        Args:
            name: The name of the service to access

        Returns:
            An instance of the service object

        Raises:
            AttributeError: If the service doesn't exist

        """
        # If we already have an instance of this service, return it from cache
        if name in self._services:
            return self._services[name]

        # Registry of available services with their module and class names
        # IMPORTANT: All keys must be in singular form for consistent client usage
        # Even if the module or class has a plural name, the attribute should be singular
        # Example: "nat_rule" for NATRule in nat_rules.py
        service_imports = {
            "address": (
                "scm.config.objects.address",
                "Address",
            ),
            "address_group": (
                "scm.config.objects.address_group",
                "AddressGroup",
            ),
            "alerts": (
                "scm.insights.alerts",
                "Alerts",
            ),
            "agent_version": (
                "scm.config.mobile_agent.agent_versions",
                "AgentVersions",
            ),
            "anti_spyware_profile": (
                "scm.config.security.anti_spyware_profile",
                "AntiSpywareProfile",
            ),
            "application": (
                "scm.config.objects.application",
                "Application",
            ),
            "application_filter": (
                "scm.config.objects.application_filters",
                "ApplicationFilters",
            ),
            "application_group": (
                "scm.config.objects.application_group",
                "ApplicationGroup",
            ),
            "auth_setting": (
                "scm.config.mobile_agent.auth_settings",
                "AuthSettings",
            ),
            "auto_tag_action": (
                "scm.config.objects.auto_tag_actions",
                "AutoTagActions",
            ),
            "bandwidth_allocation": (
                "scm.config.deployment.bandwidth_allocations",
                "BandwidthAllocations",
            ),
            "bgp_routing": (
                "scm.config.deployment.bgp_routing",
                "BGPRouting",
            ),
            "decryption_profile": (
                "scm.config.security.decryption_profile",
                "DecryptionProfile",
            ),
            "device": (
                "scm.config.setup.device",
                "Device",
            ),
            "dns_security_profile": (
                "scm.config.security.dns_security_profile",
                "DNSSecurityProfile",
            ),
            "dynamic_user_group": (
                "scm.config.objects.dynamic_user_group",
                "DynamicUserGroup",
            ),
            "external_dynamic_list": (
                "scm.config.objects.external_dynamic_lists",
                "ExternalDynamicLists",
            ),
            "folder": (
                "scm.config.setup.folder",
                "Folder",
            ),
            "hip_object": (
                "scm.config.objects.hip_object",
                "HIPObject",
            ),
            "hip_profile": (
                "scm.config.objects.hip_profile",
                "HIPProfile",
            ),
            "http_server_profile": (
                "scm.config.objects.http_server_profiles",
                "HTTPServerProfile",
            ),
            "ike_crypto_profile": (
                "scm.config.network.ike_crypto_profile",
                "IKECryptoProfile",
            ),
            "ike_gateway": (
                "scm.config.network.ike_gateway",
                "IKEGateway",
            ),
            "internal_dns_server": (
                "scm.config.deployment.internal_dns_servers",
                "InternalDnsServers",
            ),
            "ipsec_crypto_profile": (
                "scm.config.network.ipsec_crypto_profile",
                "IPsecCryptoProfile",
            ),
            "label": (
                "scm.config.setup.label",
                "Label",
            ),
            "log_forwarding_profile": (
                "scm.config.objects.log_forwarding_profile",
                "LogForwardingProfile",
            ),
            "nat_rule": (
                "scm.config.network.nat_rules",
                "NatRule",
            ),
            "network_location": (
                "scm.config.deployment.network_locations",
                "NetworkLocations",
            ),
            "quarantined_device": (
                "scm.config.objects.quarantined_devices",
                "QuarantinedDevices",
            ),
            "region": (
                "scm.config.objects.region",
                "Region",
            ),
            "remote_network": (
                "scm.config.deployment.remote_networks",
                "RemoteNetworks",
            ),
            "schedule": (
                "scm.config.objects.schedules",
                "Schedule",
            ),
            "security_rule": (
                "scm.config.security.security_rule",
                "SecurityRule",
            ),
            "security_zone": (
                "scm.config.network.security_zone",
                "SecurityZone",
            ),
            "service": (
                "scm.config.objects.service",
                "Service",
            ),
            "service_connection": (
                "scm.config.deployment.service_connections",
                "ServiceConnection",
            ),
            "service_group": (
                "scm.config.objects.service_group",
                "ServiceGroup",
            ),
            "snippet": (
                "scm.config.setup.snippet",
                "Snippet",
            ),
            "syslog_server_profile": (
                "scm.config.objects.syslog_server_profiles",
                "SyslogServerProfile",
            ),
            "tag": (
                "scm.config.objects.tag",
                "Tag",
            ),
            "url_category": (
                "scm.config.security.url_categories",
                "URLCategories",
            ),
            "vulnerability_protection_profile": (
                "scm.config.security.vulnerability_protection_profile",
                "VulnerabilityProtectionProfile",
            ),
            "variable": (
                "scm.config.setup.variable",
                "Variable",
            ),
            "wildfire_antivirus_profile": (
                "scm.config.security.wildfire_antivirus_profile",
                "WildfireAntivirusProfile",
            ),
        }

        # Check if the requested service exists in our registry
        if name not in service_imports:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        try:
            # Import the module and class dynamically
            module_name, class_name = service_imports[name]
            module = importlib.import_module(module_name)
            service_class = getattr(module, class_name)

            # Create an instance of the service class, passing self as the API client
            service_instance = service_class(self)

            # Cache the instance for future use
            self._services[name] = service_instance

            return service_instance
        except (ImportError, AttributeError) as e:
            raise AttributeError(f"Failed to load service '{name}': {str(e)}")


class ScmClient(Scm):
    """Alias for the Scm class to provide a more explicit naming option.

    This class provides all the same functionality as Scm.

    This client supports two authentication methods:
    1. OAuth2 client credentials flow (requires client_id, client_secret, and tsg_id)
    2. Bearer token authentication (requires access_token)

    Args:
        client_id: OAuth client ID for authentication (required when not using access_token)
        client_secret: OAuth client secret for authentication (required when not using access_token)
        tsg_id: Tenant Service Group ID for scope construction (required when not using access_token)
        api_base_url: Base URL for the SCM API (default: "https://api.strata.paloaltonetworks.com")
        token_url: URL for obtaining OAuth tokens (default: "https://auth.apps.paloaltonetworks.com/am/oauth2/access_token")
        log_level: Logging level (default: "ERROR")
        access_token: Pre-acquired OAuth2 bearer token for stateless authentication
            When provided, client_id, client_secret, and tsg_id are not required.
            Token refresh is the caller's responsibility when using this mode.

    """

    pass
