"""LocalConfig service for Operations API."""

from typing import List

from scm.models.operations.local_config import LocalConfigVersionModel
from scm.services import ServiceBase


class LocalConfig(ServiceBase):
    """Service for retrieving local device configuration versions and downloads."""

    ENDPOINT = "/operations/v1/local-config"

    def list_versions(self, device: str) -> List[LocalConfigVersionModel]:
        """List local configuration versions for a device.

        Args:
            device: Device serial number (14-15 digits).

        Returns:
            List of configuration version entries.

        """
        response = self.api_client.get(
            f"{self.ENDPOINT}/versions",
            params={"device": device},
        )
        if not response:
            return []
        return [LocalConfigVersionModel(**item) for item in response]

    def download(self, device: str, version: str) -> bytes:
        """Download a local configuration file for a device.

        Args:
            device: Device serial number (14-15 digits).
            version: Configuration version ID.

        Returns:
            Raw bytes of the XML configuration file.

        """
        response = self.api_client.get(
            f"{self.ENDPOINT}/download",
            params={"device": device, "version": version},
            raw_response=True,
        )
        return response.content
