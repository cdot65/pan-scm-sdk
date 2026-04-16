"""Tests for LocalConfig operations service."""

from unittest.mock import MagicMock, Mock

import pytest

from scm.models.operations.local_config import LocalConfigVersionModel
from scm.operations.local_config import LocalConfig


class TestLocalConfig:
    """Tests for the LocalConfig service."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock API client."""
        client = MagicMock()
        client.get = MagicMock()
        client.post = MagicMock()
        return client

    @pytest.fixture
    def local_config_service(self, mock_client):
        """Create a LocalConfig service instance with mock client."""
        return LocalConfig(mock_client)

    def test_list_versions(self, local_config_service, mock_client):
        """Test that list_versions returns parsed LocalConfigVersionModel list."""
        mock_client.get.return_value = [
            {
                "id": 1,
                "serial": "007951000123456",
                "local_version": "1.0.0",
                "timestamp": "2025-01-15T10:30:00Z",
                "xfmed_version": "1.0.0-transformed",
            },
            {
                "id": 2,
                "serial": "007951000123456",
                "local_version": "0.9.0",
                "timestamp": "2025-01-14T09:20:00Z",
                "xfmed_version": "0.9.0-transformed",
            },
        ]

        versions = local_config_service.list_versions(device="007951000123456")

        mock_client.get.assert_called_once_with(
            "/operations/v1/local-config/versions",
            params={"device": "007951000123456"},
        )
        assert len(versions) == 2
        assert isinstance(versions[0], LocalConfigVersionModel)
        assert versions[0].id == 1
        assert versions[1].local_version == "0.9.0"

    def test_list_versions_empty(self, local_config_service, mock_client):
        """Test that list_versions returns empty list when no versions exist."""
        mock_client.get.return_value = []

        versions = local_config_service.list_versions(device="007951000123456")

        assert versions == []

    def test_download(self, local_config_service, mock_client):
        """Test that download returns raw bytes content."""
        mock_response = Mock()
        mock_response.content = b"<config>xml content</config>"
        mock_client.get.return_value = mock_response

        result = local_config_service.download(device="007951000123456", version="1")

        mock_client.get.assert_called_once_with(
            "/operations/v1/local-config/download",
            params={"device": "007951000123456", "version": "1"},
            raw_response=True,
        )
        assert result == b"<config>xml content</config>"
