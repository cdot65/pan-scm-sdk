# tests/scm/config/network/test_ipsec_crypto_profile.py

from unittest.mock import MagicMock
from uuid import UUID

import pytest

from scm.client import Scm
from scm.config.network import IPsecCryptoProfile
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.network import IPsecCryptoProfileResponseModel


class TestIPsecCryptoProfile:
    """Tests for IPsec Crypto Profile service."""

    @pytest.fixture
    def mock_client(self):
        """Setup a mock API client."""
        client = MagicMock(spec=Scm)
        return client

    @pytest.fixture
    def ipsec_crypto_profile_service(self, mock_client):
        """Setup an IPsec Crypto Profile service with a mock client."""
        return IPsecCryptoProfile(mock_client)

    @pytest.fixture
    def sample_profile_data(self):
        """Sample IPsec crypto profile data."""
        return {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-ipsec-profile",
            "lifetime": {"seconds": 3600},
            "esp": {"encryption": ["aes-128-cbc"], "authentication": ["sha1"]},
            "folder": "Test Folder",
        }

    def test_init(self, mock_client):
        """Test service initialization."""
        service = IPsecCryptoProfile(mock_client)
        assert service.api_client == mock_client
        assert service.max_limit == IPsecCryptoProfile.DEFAULT_MAX_LIMIT

        # Test with custom max_limit
        service = IPsecCryptoProfile(mock_client, max_limit=100)
        assert service.max_limit == 100

    def test_max_limit_property(self, ipsec_crypto_profile_service):
        """Test max_limit property."""
        assert ipsec_crypto_profile_service.max_limit == IPsecCryptoProfile.DEFAULT_MAX_LIMIT

        # Test setter
        ipsec_crypto_profile_service.max_limit = 200
        assert ipsec_crypto_profile_service.max_limit == 200

    def test_validate_max_limit(self, ipsec_crypto_profile_service):
        """Test validation of max_limit."""
        # Test valid value
        assert ipsec_crypto_profile_service._validate_max_limit(1000) == 1000

        # Test None defaults to DEFAULT_MAX_LIMIT
        assert (
            ipsec_crypto_profile_service._validate_max_limit(None)
            == IPsecCryptoProfile.DEFAULT_MAX_LIMIT
        )

        # Test invalid values - using try/except because we need to check the InvalidObjectError details
        try:
            ipsec_crypto_profile_service._validate_max_limit("not-an-int")
            pytest.fail("Should have raised InvalidObjectError")
        except InvalidObjectError:
            # Just check that the exception was raised, don't check the exact message
            pass

        try:
            ipsec_crypto_profile_service._validate_max_limit(0)
            pytest.fail("Should have raised InvalidObjectError")
        except InvalidObjectError:
            # Just check that the exception was raised, don't check the exact message
            pass

        try:
            ipsec_crypto_profile_service._validate_max_limit(
                IPsecCryptoProfile.ABSOLUTE_MAX_LIMIT + 1
            )
            pytest.fail("Should have raised InvalidObjectError")
        except InvalidObjectError:
            # Just check that the exception was raised, don't check the exact message
            pass

    def test_create(self, ipsec_crypto_profile_service, sample_profile_data, mock_client):
        """Test creating an IPsec crypto profile."""
        # Setup mock response
        mock_client.post.return_value = sample_profile_data

        # Create profile
        create_data = {
            "name": "test-ipsec-profile",
            "lifetime": {"seconds": 3600},
            "esp": {"encryption": ["aes-128-cbc"], "authentication": ["sha1"]},
            "folder": "Test Folder",
        }

        result = ipsec_crypto_profile_service.create(create_data)

        # Verify API was called correctly
        mock_client.post.assert_called_once_with(IPsecCryptoProfile.ENDPOINT, json=create_data)

        # Verify result
        assert isinstance(result, IPsecCryptoProfileResponseModel)
        assert result.id == UUID(sample_profile_data["id"])
        assert result.name == sample_profile_data["name"]
        assert result.lifetime == sample_profile_data["lifetime"]

    def test_get(self, ipsec_crypto_profile_service, sample_profile_data, mock_client):
        """Test getting an IPsec crypto profile by ID."""
        profile_id = sample_profile_data["id"]
        mock_client.get.return_value = sample_profile_data

        result = ipsec_crypto_profile_service.get(profile_id)

        # Verify API was called correctly
        mock_client.get.assert_called_once_with(f"{IPsecCryptoProfile.ENDPOINT}/{profile_id}")

        # Verify result
        assert isinstance(result, IPsecCryptoProfileResponseModel)
        assert result.id == UUID(profile_id)
        assert result.name == sample_profile_data["name"]

    def test_update(self, ipsec_crypto_profile_service, sample_profile_data, mock_client):
        """Test updating an IPsec crypto profile."""
        # Setup mock response
        mock_client.put.return_value = sample_profile_data

        # Create an update model
        update_data = {
            "id": sample_profile_data["id"],
            "name": "updated-profile",
            "lifetime": {"seconds": 7200},
            "esp": {"encryption": ["aes-256-cbc"], "authentication": ["sha256"]},
            "folder": "Updated Folder",
        }

        # Create the update model directly from the update_data
        from scm.models.network.ipsec_crypto_profile import \
            IPsecCryptoProfileUpdateModel

        update_model = IPsecCryptoProfileUpdateModel(
            id=UUID(update_data["id"]),
            name=update_data["name"],
            lifetime={"seconds": 7200},  # Using dict format
            esp={"encryption": ["aes-256-cbc"], "authentication": ["sha256"]},
            folder=update_data["folder"],
        )

        # Call update
        result = ipsec_crypto_profile_service.update(update_model)

        # Verify API was called correctly with ID in path and not in JSON
        expected_payload = {
            "name": "updated-profile",
            "lifetime": {"seconds": 7200},
            "esp": {"encryption": ["aes-256-cbc"], "authentication": ["sha256"]},
            "folder": "Updated Folder",
        }
        mock_client.put.assert_called_once_with(
            f"{IPsecCryptoProfile.ENDPOINT}/{sample_profile_data['id']}", json=expected_payload
        )

        # Verify result
        assert isinstance(result, IPsecCryptoProfileResponseModel)
        assert result.id == UUID(sample_profile_data["id"])

    def test_delete(self, ipsec_crypto_profile_service, mock_client):
        """Test deleting an IPsec crypto profile."""
        profile_id = "123e4567-e89b-12d3-a456-426655440000"
        ipsec_crypto_profile_service.delete(profile_id)

        # Verify API was called correctly
        mock_client.delete.assert_called_once_with(f"{IPsecCryptoProfile.ENDPOINT}/{profile_id}")

    def test_list(self, ipsec_crypto_profile_service, mock_client):
        """Test listing IPsec crypto profiles."""
        # Setup mock response
        mock_response = {
            "data": [
                {
                    "id": "123e4567-e89b-12d3-a456-426655440000",
                    "name": "profile1",
                    "lifetime": {"seconds": 3600},
                    "esp": {"encryption": ["aes-128-cbc"], "authentication": ["sha1"]},
                    "folder": "Test Folder",
                },
                {
                    "id": "223e4567-e89b-12d3-a456-426655440000",
                    "name": "profile2",
                    "lifetime": {"hours": 1},
                    "esp": {"encryption": ["aes-256-cbc"], "authentication": ["sha256"]},
                    "folder": "Test Folder",
                },
            ],
            "limit": 200,
            "offset": 0,
            "total": 2,
        }
        mock_client.get.return_value = mock_response

        # Call list method
        result = ipsec_crypto_profile_service.list(folder="Test Folder")

        # Verify API was called correctly
        mock_client.get.assert_called_once_with(
            IPsecCryptoProfile.ENDPOINT,
            params={
                "folder": "Test Folder",
                "limit": IPsecCryptoProfile.DEFAULT_MAX_LIMIT,
                "offset": 0,
            },
        )

        # Verify result
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(item, IPsecCryptoProfileResponseModel) for item in result)
        assert result[0].id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert result[1].id == UUID("223e4567-e89b-12d3-a456-426655440000")

    def test_list_with_pagination(self, ipsec_crypto_profile_service, mock_client):
        """Test listing IPsec crypto profiles with pagination."""
        # Create a multi-page response to test pagination
        first_page = {
            "data": [
                {
                    "id": "123e4567-e89b-12d3-a456-426655440000",
                    "name": "profile1",
                    "lifetime": {"seconds": 3600},
                    "esp": {"encryption": ["aes-128-cbc"], "authentication": ["sha1"]},
                    "folder": "Test Folder",
                }
            ],
            "limit": 1,
            "offset": 0,
            "total": 2,
        }

        second_page = {
            "data": [
                {
                    "id": "223e4567-e89b-12d3-a456-426655440000",
                    "name": "profile2",
                    "lifetime": {"hours": 1},
                    "esp": {"encryption": ["aes-256-cbc"], "authentication": ["sha256"]},
                    "folder": "Test Folder",
                }
            ],
            "limit": 1,
            "offset": 1,
            "total": 2,
        }

        # Use a small max_limit to force pagination
        ipsec_crypto_profile_service.max_limit = 1

        # Setup mock to return different responses for different calls
        # This will cause the pagination to execute multiple times and hit the offset increment
        mock_client.get.side_effect = [
            first_page,
            second_page,
            {"data": [], "limit": 1, "offset": 2, "total": 2},
        ]

        # Call list method
        result = ipsec_crypto_profile_service.list(folder="Test Folder")

        # Verify the pagination worked by checking call count
        assert mock_client.get.call_count == 3  # Should make 3 calls for complete pagination

        # Verify result
        assert isinstance(result, list)
        assert len(result) == 2

        # Verify IDs in results
        result_ids = [str(item.id) for item in result]
        assert "123e4567-e89b-12d3-a456-426655440000" in result_ids
        assert "223e4567-e89b-12d3-a456-426655440000" in result_ids

    def test_list_invalid_container(self, ipsec_crypto_profile_service):
        """Test listing with invalid container parameters."""
        # Test empty folder
        try:
            ipsec_crypto_profile_service.list(folder="")
            pytest.fail("Should have raised MissingQueryParameterError")
        except MissingQueryParameterError:
            # Just check that the exception was raised, don't check the exact message
            pass

        # Test no container
        try:
            ipsec_crypto_profile_service.list()
            pytest.fail("Should have raised InvalidObjectError")
        except InvalidObjectError:
            # Just check that the exception was raised, don't check the exact message
            pass

        # Test multiple containers
        try:
            ipsec_crypto_profile_service.list(folder="Test Folder", snippet="Test Snippet")
            pytest.fail("Should have raised InvalidObjectError")
        except InvalidObjectError:
            # Just check that the exception was raised, don't check the exact message
            pass

    def test_list_invalid_response_format(self, ipsec_crypto_profile_service, mock_client):
        """Test handling of invalid response formats."""
        # Test non-dictionary response
        mock_client.get.return_value = "not a dict"
        try:
            ipsec_crypto_profile_service.list(folder="Test Folder")
            pytest.fail("Should have raised InvalidObjectError")
        except InvalidObjectError:
            # Just check that the exception was raised, don't check the exact message
            pass

        # Test missing data field
        mock_client.get.return_value = {"limit": 200, "offset": 0}
        try:
            ipsec_crypto_profile_service.list(folder="Test Folder")
            pytest.fail("Should have raised InvalidObjectError")
        except InvalidObjectError:
            # Just check that the exception was raised, don't check the exact message
            pass

        # Test data field not a list
        mock_client.get.return_value = {"data": "not a list", "limit": 200, "offset": 0}
        try:
            ipsec_crypto_profile_service.list(folder="Test Folder")
            pytest.fail("Should have raised InvalidObjectError")
        except InvalidObjectError:
            # Just check that the exception was raised, don't check the exact message
            pass

    def test_list_with_filtering(self, ipsec_crypto_profile_service, mock_client):
        """Test listing with filtering options."""
        # Setup mock response with various container types
        mock_response = {
            "data": [
                {
                    "id": "123e4567-e89b-12d3-a456-426655440000",
                    "name": "profile1",
                    "lifetime": {"seconds": 3600},
                    "esp": {"encryption": ["aes-128-cbc"], "authentication": ["sha1"]},
                    "folder": "Test Folder",
                },
                {
                    "id": "223e4567-e89b-12d3-a456-426655440000",
                    "name": "profile2",
                    "lifetime": {"hours": 1},
                    "esp": {"encryption": ["aes-256-cbc"], "authentication": ["sha256"]},
                    "folder": "Test Folder",
                },
                {
                    "id": "323e4567-e89b-12d3-a456-426655440000",
                    "name": "profile3",
                    "lifetime": {"minutes": 30},
                    "esp": {"encryption": ["aes-128-cbc"], "authentication": ["sha1"]},
                    "folder": "Another Folder",
                },
                {
                    "id": "423e4567-e89b-12d3-a456-426655440000",
                    "name": "profile4",
                    "lifetime": {"days": 1},
                    "esp": {"encryption": ["aes-128-gcm"], "authentication": ["sha256"]},
                    "snippet": "Test Snippet",
                },
                {
                    "id": "523e4567-e89b-12d3-a456-426655440000",
                    "name": "profile5",
                    "lifetime": {"days": 1},
                    "esp": {"encryption": ["aes-256-gcm"], "authentication": ["sha512"]},
                    "device": "Test Device",
                },
            ],
            "limit": 200,
            "offset": 0,
            "total": 5,
        }
        mock_client.get.return_value = mock_response

        # Test exact_match
        result = ipsec_crypto_profile_service.list(folder="Test Folder", exact_match=True)
        assert len(result) == 2  # Only profiles with exact folder match

        # Test exclude_folders
        result = ipsec_crypto_profile_service.list(
            folder="Test Folder", exclude_folders=["Another Folder"]
        )
        assert len(result) == 4  # Exclude profiles in "Another Folder"

        # Test exclude_snippets - this covers line 320
        result = ipsec_crypto_profile_service.list(
            folder="Test Folder", exclude_snippets=["Test Snippet"]
        )
        assert len(result) == 4  # Exclude profiles with "Test Snippet"

        # Test exclude_devices - this covers line 328
        result = ipsec_crypto_profile_service.list(
            folder="Test Folder", exclude_devices=["Test Device"]
        )
        assert len(result) == 4  # Exclude profiles with "Test Device"

    def test_fetch(self, ipsec_crypto_profile_service, mock_client, sample_profile_data):
        """Test fetching a single IPsec crypto profile by name."""
        # Setup mock response
        mock_client.get.return_value = {
            "data": [sample_profile_data],
            "limit": 200,
            "offset": 0,
            "total": 1,
        }

        # Call fetch
        result = ipsec_crypto_profile_service.fetch(name="test-ipsec-profile", folder="Test Folder")

        # Verify API was called correctly
        mock_client.get.assert_called_once_with(
            IPsecCryptoProfile.ENDPOINT,
            params={"name": "test-ipsec-profile", "folder": "Test Folder"},
        )

        # Verify result
        assert isinstance(result, IPsecCryptoProfileResponseModel)
        assert result.id == UUID(sample_profile_data["id"])
        assert result.name == sample_profile_data["name"]

    def test_fetch_single_object(
        self, ipsec_crypto_profile_service, mock_client, sample_profile_data
    ):
        """Test fetching a single object response."""
        # Some API endpoints might return a single object instead of a list
        mock_client.get.return_value = sample_profile_data

        result = ipsec_crypto_profile_service.fetch(name="test-ipsec-profile", folder="Test Folder")

        assert isinstance(result, IPsecCryptoProfileResponseModel)
        assert result.id == UUID(sample_profile_data["id"])

    def test_fetch_invalid_params(self, ipsec_crypto_profile_service, mock_client):
        """Test fetching with invalid parameters."""
        # Test empty name
        try:
            ipsec_crypto_profile_service.fetch(name="", folder="Test Folder")
            pytest.fail("Should have raised MissingQueryParameterError")
        except MissingQueryParameterError:
            # Just check that the exception was raised, don't check the exact message
            pass

        # Test empty folder
        try:
            ipsec_crypto_profile_service.fetch(name="test-profile", folder="")
            pytest.fail("Should have raised MissingQueryParameterError")
        except MissingQueryParameterError:
            # Just check that the exception was raised, don't check the exact message
            pass

        # Test no container
        try:
            ipsec_crypto_profile_service.fetch(name="test-profile")
            pytest.fail("Should have raised InvalidObjectError")
        except InvalidObjectError:
            # Just check that the exception was raised, don't check the exact message
            pass

        # Test multiple containers
        try:
            ipsec_crypto_profile_service.fetch(
                name="test-profile", folder="Test Folder", snippet="Test Snippet"
            )
            pytest.fail("Should have raised InvalidObjectError")
        except InvalidObjectError:
            # Just check that the exception was raised, don't check the exact message
            pass

        # Test non-dictionary response - covers line 402
        mock_client.get.return_value = "not a dict"
        try:
            ipsec_crypto_profile_service.fetch(name="test-profile", folder="Test Folder")
            pytest.fail("Should have raised InvalidObjectError")
        except InvalidObjectError:
            # Just check that the exception was raised, don't check the exact message
            pass

        # Test missing required fields - covers line 435
        mock_client.get.return_value = {"some_field": "value"}  # No 'id' or 'data' field
        try:
            ipsec_crypto_profile_service.fetch(name="test-profile", folder="Test Folder")
            pytest.fail("Should have raised InvalidObjectError")
        except InvalidObjectError:
            # Just check that the exception was raised, don't check the exact message
            pass

    def test_fetch_not_found(self, ipsec_crypto_profile_service, mock_client):
        """Test fetching a profile that doesn't exist."""
        # Empty data list
        mock_client.get.return_value = {"data": [], "limit": 200, "offset": 0, "total": 0}

        try:
            ipsec_crypto_profile_service.fetch(name="nonexistent", folder="Test Folder")
            pytest.fail("Should have raised InvalidObjectError")
        except InvalidObjectError:
            # Just check that the exception was raised, don't check the exact message
            pass

    def test_fetch_no_exact_match(self, ipsec_crypto_profile_service, mock_client):
        """Test fetching when no exact name match is found."""
        # Return profiles but none match the exact name
        mock_client.get.return_value = {
            "data": [
                {
                    "id": "123e4567-e89b-12d3-a456-426655440000",
                    "name": "different-name",
                    "lifetime": {"seconds": 3600},
                    "esp": {"encryption": ["aes-128-cbc"], "authentication": ["sha1"]},
                    "folder": "Test Folder",
                }
            ],
            "limit": 200,
            "offset": 0,
            "total": 1,
        }

        try:
            ipsec_crypto_profile_service.fetch(name="test-profile", folder="Test Folder")
            pytest.fail("Should have raised InvalidObjectError")
        except InvalidObjectError:
            # Just check that the exception was raised, don't check the exact message
            pass

    def test_build_container_params(self, ipsec_crypto_profile_service):
        """Test building container parameters."""
        # Single container
        params = ipsec_crypto_profile_service._build_container_params(
            folder="Test Folder", snippet=None, device=None
        )
        assert params == {"folder": "Test Folder"}

        # Different container
        params = ipsec_crypto_profile_service._build_container_params(
            folder=None, snippet="Test Snippet", device=None
        )
        assert params == {"snippet": "Test Snippet"}

        # No containers
        params = ipsec_crypto_profile_service._build_container_params(
            folder=None, snippet=None, device=None
        )
        assert params == {}
