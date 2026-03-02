"""Certificate configuration service for Strata Cloud Manager SDK.

Provides service class for managing certificate objects via the SCM API.
Certificates use a non-standard pattern: generate (POST), import, export, list, get, delete.
There are no standard create or update operations.
"""

# scm/config/identity/certificate.py

# Standard library imports
import logging
from typing import Any, Dict, List, Optional

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.identity.certificates import (
    CertificateExportModel,
    CertificateGenerateModel,
    CertificateImportModel,
    CertificateResponseModel,
)


class Certificate(BaseObject):
    """Manages Certificate objects in Palo Alto Networks' Strata Cloud Manager.

    This service uses a non-standard pattern. Instead of create/update, it provides
    generate() for creating new certificates, import_cert() for importing existing
    certificates, and export() for exporting certificates. There is no update operation.

    Args:
        api_client: The API client instance
        max_limit (Optional[int]): Maximum number of objects to return in a single API request.
            Defaults to 2500. Must be between 1 and 5000.

    """

    ENDPOINT = "/config/identity/v1/certificates"
    DEFAULT_MAX_LIMIT = 2500
    ABSOLUTE_MAX_LIMIT = 5000  # Maximum allowed by the API

    def __init__(
        self,
        api_client,
        max_limit: Optional[int] = None,
    ):
        """Initialize the Certificate service with the given API client."""
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

    def generate(
        self,
        data: Dict[str, Any],
    ) -> CertificateResponseModel:
        """Generate a new certificate.

        Posts to the certificates endpoint to generate a new certificate with the
        specified parameters.

        Args:
            data: Dictionary containing certificate generation parameters

        Returns:
            CertificateResponseModel: The generated certificate response

        """
        # Use the dictionary "data" to pass into Pydantic and return a modeled object
        certificate = CertificateGenerateModel(**data)

        # Convert back to a Python dictionary, removing any unset fields
        payload = certificate.model_dump(exclude_unset=True)

        # Send the object to the remote API as JSON
        response: Dict[str, Any] = self.api_client.post(
            self.ENDPOINT,
            json=payload,
        )

        # Return the SCM API response as a new Pydantic object
        return CertificateResponseModel(**response)

    def import_cert(
        self,
        data: Dict[str, Any],
    ) -> CertificateResponseModel:
        """Import a certificate.

        Posts to the certificates:import endpoint to import an existing certificate.

        Args:
            data: Dictionary containing certificate import parameters

        Returns:
            CertificateResponseModel: The imported certificate response

        """
        # Use the dictionary "data" to pass into Pydantic and return a modeled object
        certificate = CertificateImportModel(**data)

        # Convert back to a Python dictionary, removing any unset fields
        payload = certificate.model_dump(exclude_unset=True)

        # Send the object to the remote API as JSON
        endpoint = f"{self.ENDPOINT}:import"
        response: Dict[str, Any] = self.api_client.post(
            endpoint,
            json=payload,
        )

        # Return the SCM API response as a new Pydantic object
        return CertificateResponseModel(**response)

    def export(
        self,
        certificate_id: str,
        data: Dict[str, Any],
    ) -> dict:
        """Export a certificate.

        Posts to the certificates/{id}:export endpoint to export a certificate.

        Args:
            certificate_id: The UUID of the certificate to export
            data: Dictionary containing export parameters (format, passphrase)

        Returns:
            dict: The export response data

        """
        # Use the dictionary "data" to pass into Pydantic and return a modeled object
        export_params = CertificateExportModel(**data)

        # Convert back to a Python dictionary, removing any unset fields
        payload = export_params.model_dump(exclude_unset=True)

        # Send the object to the remote API as JSON
        endpoint = f"{self.ENDPOINT}/{certificate_id}:export"
        response: Dict[str, Any] = self.api_client.post(
            endpoint,
            json=payload,
        )

        return response

    def get(
        self,
        object_id: str,
    ) -> CertificateResponseModel:
        """Get a certificate object by ID.

        Args:
            object_id: The UUID of the certificate to retrieve

        Returns:
            CertificateResponseModel: The certificate response

        """
        # Send the request to the remote API
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.get(endpoint)

        # Return the SCM API response as a new Pydantic object
        return CertificateResponseModel(**response)

    @staticmethod
    def _apply_filters(
        certificates: List[CertificateResponseModel],
        filters: Dict[str, Any],
    ) -> List[CertificateResponseModel]:
        """Apply client-side filtering to the list of certificates.

        Args:
            certificates: List of CertificateResponseModel objects
            filters: Dictionary of filter criteria

        Returns:
            List[CertificateResponseModel]: Filtered list of certificates

        """
        return certificates

    @staticmethod
    def _build_container_params(
        folder: Optional[str],
        snippet: Optional[str],
        device: Optional[str],
    ) -> dict:
        """Build container parameters dictionary."""
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
    ) -> List[CertificateResponseModel]:
        """List certificate objects with optional filtering.

        Args:
            folder: Optional folder name
            snippet: Optional snippet name
            device: Optional device name
            exact_match (bool): If True, only return objects whose container
                                exactly matches the provided container parameter.
            exclude_folders (List[str], optional): List of folder names to exclude from results.
            exclude_snippets (List[str], optional): List of snippet values to exclude from results.
            exclude_devices (List[str], optional): List of device values to exclude from results.
            **filters: Additional filters

        Returns:
            List[CertificateResponseModel]: A list of certificate objects

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

        container_parameters = self._build_container_params(
            folder,
            snippet,
            device,
        )

        if len(container_parameters) != 1:
            raise InvalidObjectError(
                message="Exactly one of 'folder', 'snippet', or 'device' must be provided.",
                error_code="E003",
                http_status_code=400,
                details={"error": "Invalid container parameters"},
            )

        # Pagination logic
        limit = self._max_limit
        offset = 0
        all_objects = []

        while True:
            params = container_parameters.copy()
            params["limit"] = limit
            params["offset"] = offset

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

            data = response["data"]
            object_instances = [CertificateResponseModel(**item) for item in data]
            all_objects.extend(object_instances)

            # If we got fewer than 'limit' objects, we've reached the end
            if len(data) < limit:
                break

            offset += limit

        # Apply existing filters first
        filtered_objects = self._apply_filters(
            all_objects,
            filters,
        )

        # Determine which container key and value we are filtering on
        container_key, container_value = next(iter(container_parameters.items()))

        # If exact_match is True, filter out filtered_objects that don't match exactly
        if exact_match:
            filtered_objects = [
                each for each in filtered_objects if getattr(each, container_key) == container_value
            ]

        # Exclude folders if provided
        if exclude_folders and isinstance(exclude_folders, list):
            filtered_objects = [
                each for each in filtered_objects if each.folder not in exclude_folders
            ]

        # Exclude snippets if provided
        if exclude_snippets and isinstance(exclude_snippets, list):
            filtered_objects = [
                each for each in filtered_objects if each.snippet not in exclude_snippets
            ]

        # Exclude devices if provided
        if exclude_devices and isinstance(exclude_devices, list):
            filtered_objects = [
                each for each in filtered_objects if each.device not in exclude_devices
            ]

        return filtered_objects

    def fetch(
        self,
        name: str,
        folder: Optional[str] = None,
        snippet: Optional[str] = None,
        device: Optional[str] = None,
    ) -> CertificateResponseModel:
        """Fetch a single certificate by name.

        Args:
            name (str): The name of the certificate to fetch.
            folder (str, optional): The folder in which the resource is defined.
            snippet (str, optional): The snippet in which the resource is defined.
            device (str, optional): The device in which the resource is defined.

        Returns:
            CertificateResponseModel: The fetched certificate object as a Pydantic model.

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

        container_parameters = self._build_container_params(
            folder,
            snippet,
            device,
        )

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
            return CertificateResponseModel(**response)
        else:
            raise InvalidObjectError(
                message="Invalid response format: missing 'id' field",
                error_code="E003",
                http_status_code=500,
                details={"error": "Response missing 'id' field"},
            )

    def delete(
        self,
        object_id: str,
    ) -> None:
        """Delete a certificate object.

        Args:
            object_id (str): The ID of the object to delete.

        """
        endpoint = f"{self.ENDPOINT}/{object_id}"
        self.api_client.delete(endpoint)
