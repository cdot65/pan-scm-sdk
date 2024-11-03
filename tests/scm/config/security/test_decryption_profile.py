# tests/scm/config/security/test_decryption_profile.py

import pytest
from unittest.mock import MagicMock

from pydantic import ValidationError as PydanticValidationError
from scm.config.security.decryption_profile import DecryptionProfile
from scm.exceptions import NotFoundError, APIError, ValidationError
from scm.models.security.decryption_profiles import (
    DecryptionProfileCreateModel,
    DecryptionProfileResponseModel,
    SSLProtocolSettings,
    SSLVersion,
)


@pytest.mark.usefixtures("load_env")
class TestDecryptionProfileBase:
    """Base class for Decryption Profile tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm  # noqa
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = DecryptionProfile(self.mock_scm)  # noqa


class TestDecryptionProfileAPI(TestDecryptionProfileBase):
    """Tests for Decryption Profile API operations."""

    def test_list_decryption_profiles(self):
        """Test listing decryption profiles."""
        mock_response = {
            "data": [
                {
                    "id": "f6e434b2-f3f8-48bd-b84f-745e0daee648",
                    "name": "web-security-default",
                    "folder": "All",
                    "snippet": "Web-Security-Default",
                    "ssl_protocol_settings": {
                        "min_version": "tls1-2",
                        "max_version": "max",
                        "enc_algo_rc4": False,
                        "auth_algo_sha1": False,
                    },
                    "ssl_forward_proxy": {
                        "auto_include_altname": True,
                        "block_client_cert": True,
                        "block_expired_certificate": True,
                        "block_untrusted_issuer": True,
                    },
                }
            ]
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        profiles = self.client.list(folder="All")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/security/v1/decryption-profiles",
            params={"folder": "All"},
        )
        assert isinstance(profiles, list)
        assert isinstance(profiles[0], DecryptionProfileResponseModel)
        assert profiles[0].name == "web-security-default"
        assert profiles[0].ssl_protocol_settings.min_version == SSLVersion.tls1_2

    def test_create_decryption_profile(self):
        """Test creating a decryption profile."""
        test_profile_data = {
            "name": "NewDecryptionProfile",
            "folder": "All",
            "ssl_forward_proxy": {
                "block_expired_certificate": True,
                "block_untrusted_issuer": True,
            },
            "ssl_protocol_settings": {
                "min_version": "tls1-2",
                "max_version": "tls1-3",
                "enc_algo_rc4": False,
                "auth_algo_sha1": False,
            },
        }

        mock_response = test_profile_data.copy()
        mock_response["id"] = "444e4567-e89b-12d3-a456-426655440003"

        self.mock_scm.post.return_value = mock_response  # noqa
        created_profile = self.client.create(test_profile_data)

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/security/v1/decryption-profiles",
            json=test_profile_data,
        )
        assert isinstance(created_profile, DecryptionProfileResponseModel)
        assert created_profile.id == "444e4567-e89b-12d3-a456-426655440003"

    def test_get_decryption_profile(self):
        """Test retrieving a decryption profile by ID."""
        profile_id = "f6e434b2-f3f8-48bd-b84f-745e0daee648"
        mock_response = {
            "id": profile_id,
            "name": "ExistingDecryptionProfile",
            "folder": "All",
            "ssl_protocol_settings": {
                "min_version": "tls1-2",
                "max_version": "max",
            },
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        profile = self.client.get(profile_id)

        self.mock_scm.get.assert_called_once_with(  # noqa
            f"/config/security/v1/decryption-profiles/{profile_id}"
        )
        assert isinstance(profile, DecryptionProfileResponseModel)
        assert profile.id == profile_id

    def test_update_decryption_profile(self):
        """Test updating a decryption profile."""
        profile_id = "f6e434b2-f3f8-48bd-b84f-745e0daee648"
        update_data = {
            "id": profile_id,
            "name": "UpdatedDecryptionProfile",
            "folder": "All",
            "ssl_protocol_settings": {
                "min_version": "tls1-1",
                "max_version": "tls1-2",
            },
        }

        # Create mock response with ID
        mock_response = {
            "id": profile_id,
            "name": "UpdatedDecryptionProfile",
            "folder": "All",
            "ssl_protocol_settings": {
                "min_version": "tls1-1",
                "max_version": "tls1-2",
            },
        }
        self.mock_scm.put.return_value = mock_response  # noqa

        updated_profile = self.client.update(update_data)

        # Create expected payload without ID - do deep copy first
        expected_payload = {
            "name": "UpdatedDecryptionProfile",
            "folder": "All",
            "ssl_protocol_settings": {
                "min_version": "tls1-1",
                "max_version": "tls1-2",
            },
        }

        self.mock_scm.put.assert_called_once_with(  # noqa
            f"/config/security/v1/decryption-profiles/{profile_id}",
            json=expected_payload,
        )
        assert isinstance(updated_profile, DecryptionProfileResponseModel)
        assert updated_profile.id == profile_id

    def test_delete_decryption_profile(self):
        """Test deleting a decryption profile."""
        profile_id = "f6e434b2-f3f8-48bd-b84f-745e0daee648"
        self.client.delete(profile_id)
        self.mock_scm.delete.assert_called_once_with(  # noqa
            f"/config/security/v1/decryption-profiles/{profile_id}"
        )

    def test_update_missing_id(self):
        """Test update without ID field."""
        update_data = {
            "name": "UpdatedDecryptionProfile",
            "folder": "All",
        }

        with pytest.raises(ValueError) as exc_info:
            self.client.update(update_data)
        assert "The 'id' field is required in the data for update." in str(
            exc_info.value
        )

    def test_update_response_handling(self):
        """Test various response scenarios in update method."""
        profile_id = "f6e434b2-f3f8-48bd-b84f-745e0daee648"

        # Test single item in data array
        update_data = {
            "id": profile_id,
            "name": "UpdatedProfile",
            "folder": "All",
        }
        mock_response_single = {
            "data": [
                {
                    "id": profile_id,
                    "name": "UpdatedProfile",
                    "folder": "All",
                }
            ]
        }
        self.mock_scm.put.return_value = mock_response_single  # noqa
        result = self.client.update(update_data.copy())  # Use copy of update_data
        assert isinstance(result, DecryptionProfileResponseModel)
        assert result.id == profile_id

        # Test empty data array
        mock_response_empty = {"data": []}
        self.mock_scm.put.return_value = mock_response_empty  # noqa
        with pytest.raises(NotFoundError) as exc_info:
            self.client.update(update_data.copy())  # Use copy of update_data
        assert "Decryption profile not found" in str(exc_info.value)

        # Test multiple items in data array
        mock_response_multiple = {
            "data": [
                {"id": profile_id, "name": "Profile1"},
                {"id": "another-id", "name": "Profile2"},
            ]
        }
        self.mock_scm.put.return_value = mock_response_multiple  # noqa
        with pytest.raises(APIError) as exc_info:
            self.client.update(update_data.copy())  # Use copy of update_data
        assert "Multiple decryption profiles found with the same name" in str(
            exc_info.value
        )

        # Test None response
        self.mock_scm.put.return_value = None  # noqa
        result = self.client.update(update_data.copy())  # Use copy of update_data
        assert isinstance(result, DecryptionProfileCreateModel)

        # Test unexpected response format
        self.mock_scm.put.return_value = "unexpected"  # noqa
        with pytest.raises(APIError) as exc_info:
            self.client.update(update_data.copy())  # Use copy of update_data
        assert "Unexpected response format" in str(exc_info.value)

    def test_list_pagination_validation(self):
        """Test pagination parameter validation in list method."""
        # Test invalid offset
        with pytest.raises(ValueError) as exc_info:
            self.client.list(folder="All", offset=-1)
        assert "Offset must be a non-negative integer" in str(exc_info.value)

        # Test invalid limit
        with pytest.raises(ValueError) as exc_info:
            self.client.list(folder="All", limit=0)
        assert "Limit must be a positive integer" in str(exc_info.value)

        # Test both invalid
        with pytest.raises(ValueError) as exc_info:
            self.client.list(folder="All", offset=-1, limit=0)
        assert "Offset must be a non-negative integer" in str(exc_info.value)
        assert "Limit must be a positive integer" in str(exc_info.value)

    def test_list_container_validation(self):
        """Test container validation in list method."""
        # Test no container
        with pytest.raises(ValueError) as exc_info:
            self.client.list()
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

        # Test multiple containers
        with pytest.raises(ValueError) as exc_info:
            self.client.list(folder="All", snippet="test")
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_list_with_pagination_and_filters(self):
        """Test list method with pagination and filters."""
        mock_response = {"data": []}
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test with pagination
        self.client.list(folder="All", offset=10, limit=20)
        self.mock_scm.get.assert_called_with(  # noqa
            "/config/security/v1/decryption-profiles",
            params={"folder": "All", "offset": 10, "limit": 20},
        )

        # Test with name filter
        self.client.list(folder="All", name="test-profile")
        self.mock_scm.get.assert_called_with(  # noqa
            "/config/security/v1/decryption-profiles",
            params={"folder": "All", "name": "test-profile"},
        )

    def test_fetch_validations_and_filters(self):
        """Test fetch method validations and filters."""
        # Test empty name
        with pytest.raises(ValidationError) as exc_info:
            self.client.fetch(name="")
        assert "Parameter 'name' must be provided for fetch method." in str(
            exc_info.value
        )

        # Test container validation
        with pytest.raises(ValidationError) as exc_info:
            self.client.fetch(name="test", folder="All", snippet="test")
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

        # Test successful fetch with filters
        mock_response = {
            "id": "f6e434b2-f3f8-48bd-b84f-745e0daee648",
            "name": "test-profile",
            "folder": "All",
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        result = self.client.fetch(
            name="test-profile",
            folder="All",
            custom_filter="value",
            types=["excluded"],
            values=["excluded"],
        )

        self.mock_scm.get.assert_called_with(  # noqa
            "/config/security/v1/decryption-profiles",
            params={"folder": "All", "name": "test-profile", "custom_filter": "value"},
        )
        assert isinstance(result, dict)
        assert result["name"] == "test-profile"


class TestDecryptionProfileValidation(TestDecryptionProfileBase):
    """Tests for Decryption Profile validation."""

    def test_ssl_protocol_settings_validation(self):
        """Test SSL protocol settings validation."""
        valid_data = {
            "min_version": "tls1-0",
            "max_version": "tls1-2",
        }
        settings = SSLProtocolSettings(**valid_data)
        assert settings.min_version == SSLVersion.tls1_0
        assert settings.max_version == SSLVersion.tls1_2

        invalid_data = {
            "min_version": "tls1-2",
            "max_version": "tls1-1",
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            SSLProtocolSettings(**invalid_data)
        assert "max_version cannot be less than min_version" in str(exc_info.value)

    def test_container_validation(self):
        """Test container validation."""
        data_no_container = {
            "name": "InvalidProfile",
            "ssl_forward_proxy": {},
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            DecryptionProfileCreateModel(**data_no_container)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_name_pattern_validation(self):
        """Test name pattern validation."""
        invalid_name_data = {
            "name": "Invalid!Name",
            "folder": "Shared",
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            DecryptionProfileCreateModel(**invalid_name_data)
        assert "String should match pattern" in str(exc_info.value)

    def test_ssl_version_validation(self):
        """Test SSL version validation."""
        invalid_version_data = {
            "name": "InvalidSSLVersionProfile",
            "folder": "Shared",
            "ssl_protocol_settings": {
                "min_version": "tls1-5",
                "max_version": "max",
            },
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            DecryptionProfileCreateModel(**invalid_version_data)
        assert (
            "Input should be 'sslv3', 'tls1-0', 'tls1-1', 'tls1-2', 'tls1-3' or 'max'"
            in str(exc_info.value)
        )

    def test_uuid_validation(self):
        """Test UUID validation."""
        invalid_id_data = {
            "id": "invalid-uuid",
            "name": "ValidProfile",
            "folder": "Shared",
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            DecryptionProfileResponseModel(**invalid_id_data)
        assert "Invalid UUID format for 'id'" in str(exc_info.value)


class TestSuite(
    TestDecryptionProfileAPI,
    TestDecryptionProfileValidation,
):
    """Main test suite that combines all test classes."""

    pass
