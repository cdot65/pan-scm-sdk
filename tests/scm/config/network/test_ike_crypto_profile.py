"""Test the IKE Crypto Profile configuration class."""

from unittest.mock import MagicMock

import pytest

from scm.config.network import IKECryptoProfile
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.network import (IKECryptoProfileResponseModel,
                                IKECryptoProfileUpdateModel)


@pytest.mark.usefixtures("load_env")
class TestIKECryptoProfileBase:
    """Base test class for IKE Crypto Profile tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()

    @pytest.fixture
    def ike_crypto_profile(self):
        """Return an IKE Crypto Profile instance with a mock API client."""
        return IKECryptoProfile(self.mock_scm)

    @pytest.fixture
    def sample_profile_data(self):
        """Return sample IKE crypto profile data."""
        return {
            "name": "test-profile",
            "hash": ["sha1", "sha256"],
            "encryption": ["aes-128-cbc", "aes-256-cbc"],
            "dh_group": ["group2", "group5"],
            "folder": "test-folder",
        }

    @pytest.fixture
    def sample_profile_response(self, sample_profile_data):
        """Return a sample IKE crypto profile response with ID."""
        response = sample_profile_data.copy()
        response["id"] = "123e4567-e89b-12d3-a456-426655440000"
        return response


class TestIKECryptoProfileInit(TestIKECryptoProfileBase):
    """Test IKE Crypto Profile initialization."""

    def test_init_with_default_max_limit(self):
        """Test initialization with default max_limit."""
        profile = IKECryptoProfile(self.mock_scm)
        assert profile.max_limit == 2500

    def test_init_with_custom_max_limit(self):
        """Test initialization with custom max_limit."""
        profile = IKECryptoProfile(self.mock_scm, max_limit=1000)
        assert profile.max_limit == 1000

    def test_init_with_invalid_max_limit_type(self):
        """Test initialization with invalid max_limit type."""
        with pytest.raises(InvalidObjectError) as exc:
            IKECryptoProfile(self.mock_scm, max_limit="invalid")
        assert "Invalid max_limit type" in str(exc.value)

    def test_init_with_zero_max_limit(self):
        """Test initialization with zero max_limit."""
        with pytest.raises(InvalidObjectError) as exc:
            IKECryptoProfile(self.mock_scm, max_limit=0)
        assert "Invalid max_limit value" in str(exc.value)

    def test_init_with_excessive_max_limit(self):
        """Test initialization with excessive max_limit."""
        with pytest.raises(InvalidObjectError) as exc:
            IKECryptoProfile(self.mock_scm, max_limit=6000)
        assert "max_limit exceeds maximum allowed value" in str(exc.value)

    def test_max_limit_property(self):
        """Test max_limit property."""
        profile = IKECryptoProfile(self.mock_scm, max_limit=1000)
        assert profile.max_limit == 1000

        profile.max_limit = 2000
        assert profile.max_limit == 2000

        with pytest.raises(InvalidObjectError) as exc:
            profile.max_limit = 0
        assert "Invalid max_limit value" in str(exc.value)


class TestIKECryptoProfileCreate(TestIKECryptoProfileBase):
    """Test IKE Crypto Profile create method."""

    def test_create_ike_crypto_profile(
        self, ike_crypto_profile, sample_profile_data, sample_profile_response
    ):
        """Test creating an IKE crypto profile."""
        # Mock the API response
        self.mock_scm.post.return_value = sample_profile_response

        result = ike_crypto_profile.create(sample_profile_data)

        self.mock_scm.post.assert_called_once()
        assert isinstance(result, IKECryptoProfileResponseModel)
        assert result.name == "test-profile"
        assert result.folder == "test-folder"
        assert "sha1" in result.hash
        assert "sha256" in result.hash
        assert "aes-128-cbc" in result.encryption
        assert "aes-256-cbc" in result.encryption
        assert "group2" in result.dh_group
        assert "group5" in result.dh_group
        assert str(result.id) == "123e4567-e89b-12d3-a456-426655440000"


class TestIKECryptoProfileGet(TestIKECryptoProfileBase):
    """Test IKE Crypto Profile get method."""

    def test_get_ike_crypto_profile(self, ike_crypto_profile, sample_profile_response):
        """Test getting an IKE crypto profile by ID."""
        self.mock_scm.get.return_value = sample_profile_response

        result = ike_crypto_profile.get("123e4567-e89b-12d3-a456-426655440000")

        self.mock_scm.get.assert_called_once_with(
            "/config/network/v1/ike-crypto-profiles/123e4567-e89b-12d3-a456-426655440000"
        )
        assert isinstance(result, IKECryptoProfileResponseModel)
        assert result.name == "test-profile"
        assert str(result.id) == "123e4567-e89b-12d3-a456-426655440000"


class TestIKECryptoProfileUpdate(TestIKECryptoProfileBase):
    """Test IKE Crypto Profile update method."""

    def test_update_ike_crypto_profile(self, ike_crypto_profile, sample_profile_response):
        """Test updating an IKE crypto profile."""
        self.mock_scm.put.return_value = sample_profile_response

        # Create an update model
        update_data = sample_profile_response.copy()
        # Add description for update model
        update_data["description"] = "Updated test profile"
        update_model = IKECryptoProfileUpdateModel(**update_data)

        result = ike_crypto_profile.update(update_model)

        # Check API client was called correctly
        self.mock_scm.put.assert_called_once()
        call_args = self.mock_scm.put.call_args
        assert (
            call_args[0][0]
            == "/config/network/v1/ike-crypto-profiles/123e4567-e89b-12d3-a456-426655440000"
        )
        assert "id" not in call_args[1]["json"], "ID should not be in the request payload"
        # Verify description is in the update payload
        assert "description" in call_args[1]["json"], "Description should be in the request payload"

        assert isinstance(result, IKECryptoProfileResponseModel)
        assert result.name == "test-profile"
        assert str(result.id) == "123e4567-e89b-12d3-a456-426655440000"


class TestIKECryptoProfileDelete(TestIKECryptoProfileBase):
    """Test IKE Crypto Profile delete method."""

    def test_delete_ike_crypto_profile(self, ike_crypto_profile):
        """Test deleting an IKE crypto profile."""
        ike_crypto_profile.delete("123e4567-e89b-12d3-a456-426655440000")

        self.mock_scm.delete.assert_called_once_with(
            "/config/network/v1/ike-crypto-profiles/123e4567-e89b-12d3-a456-426655440000"
        )


class TestIKECryptoProfileList(TestIKECryptoProfileBase):
    """Test IKE Crypto Profile list method."""

    @pytest.fixture
    def list_response(self, sample_profile_response):
        """Return a sample list response with multiple profiles."""
        profile1 = sample_profile_response.copy()
        profile2 = sample_profile_response.copy()
        profile2["id"] = "223e4567-e89b-12d3-a456-426655440000"
        profile2["name"] = "test-profile-2"

        return {
            "data": [profile1, profile2],
            "limit": 2500,
            "offset": 0,
            "total": 2,
        }

    def test_list_ike_crypto_profiles(self, ike_crypto_profile, list_response):
        """Test listing IKE crypto profiles."""
        self.mock_scm.get.return_value = list_response

        result = ike_crypto_profile.list(folder="test-folder")

        self.mock_scm.get.assert_called_once()
        call_args = self.mock_scm.get.call_args
        assert call_args[0][0] == "/config/network/v1/ike-crypto-profiles"
        assert call_args[1]["params"]["folder"] == "test-folder"
        assert call_args[1]["params"]["limit"] == 2500
        assert call_args[1]["params"]["offset"] == 0

        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(item, IKECryptoProfileResponseModel) for item in result)
        assert result[0].name == "test-profile"
        assert result[1].name == "test-profile-2"

    def test_list_with_pagination(self, ike_crypto_profile):
        """Test list with pagination."""
        # First response has max limit items
        first_page = {
            "data": [
                {
                    "id": f"123e4567-e89b-12d3-a456-42665544{i:04d}",
                    "name": f"profile-{i}",
                    "hash": ["sha1"],
                    "encryption": ["aes-128-cbc"],
                    "dh_group": ["group2"],
                    "folder": "test-folder",
                }
                for i in range(1, 2501)
            ],
            "limit": 2500,
            "offset": 0,
            "total": 3000,
        }

        # Second response has remaining items
        second_page = {
            "data": [
                {
                    "id": f"123e4567-e89b-12d3-a456-42665544{i:04d}",
                    "name": f"profile-{i}",
                    "hash": ["sha1"],
                    "encryption": ["aes-128-cbc"],
                    "dh_group": ["group2"],
                    "folder": "test-folder",
                }
                for i in range(2501, 3001)
            ],
            "limit": 2500,
            "offset": 2500,
            "total": 3000,
        }

        self.mock_scm.get.side_effect = [first_page, second_page]

        result = ike_crypto_profile.list(folder="test-folder")

        assert self.mock_scm.get.call_count == 2
        assert len(result) == 3000

    def test_list_with_empty_folder(self, ike_crypto_profile):
        """Test list with empty folder."""
        with pytest.raises(MissingQueryParameterError) as exc:
            ike_crypto_profile.list(folder="")
        assert '"folder" is not allowed to be empty' in str(exc.value)

    def test_list_with_no_container(self, ike_crypto_profile):
        """Test list with no container."""
        with pytest.raises(InvalidObjectError) as exc:
            ike_crypto_profile.list()
        assert "Invalid container parameters" in str(exc.value)

    def test_list_with_multiple_containers(self, ike_crypto_profile):
        """Test list with multiple containers."""
        with pytest.raises(InvalidObjectError) as exc:
            ike_crypto_profile.list(folder="test-folder", snippet="test-snippet")
        assert "Invalid container parameters" in str(exc.value)

    def test_list_with_invalid_response_format(self, ike_crypto_profile):
        """Test list with invalid response format."""
        self.mock_scm.get.return_value = "invalid"

        with pytest.raises(InvalidObjectError) as exc:
            ike_crypto_profile.list(folder="test-folder")
        assert "Response is not a dictionary" in str(exc.value)

    def test_list_with_missing_data_field(self, ike_crypto_profile):
        """Test list with missing data field."""
        self.mock_scm.get.return_value = {}

        with pytest.raises(InvalidObjectError) as exc:
            ike_crypto_profile.list(folder="test-folder")
        assert '"data" field missing in the response' in str(exc.value)

    def test_list_with_invalid_data_type(self, ike_crypto_profile):
        """Test list with invalid data type."""
        self.mock_scm.get.return_value = {"data": "invalid"}

        with pytest.raises(InvalidObjectError) as exc:
            ike_crypto_profile.list(folder="test-folder")
        assert '"data" field must be a list' in str(exc.value)

    def test_list_with_exact_match(self, ike_crypto_profile, list_response):
        """Test list with exact_match."""
        # Modify second profile to have different folder
        list_response["data"][1]["folder"] = "different-folder"
        self.mock_scm.get.return_value = list_response

        result = ike_crypto_profile.list(folder="test-folder", exact_match=True)

        assert len(result) == 1
        assert result[0].name == "test-profile"
        assert result[0].folder == "test-folder"

    def test_list_with_exclude_folders(self, ike_crypto_profile, list_response):
        """Test list with exclude_folders."""
        # Modify second profile to have different folder
        list_response["data"][1]["folder"] = "exclude-folder"
        self.mock_scm.get.return_value = list_response

        result = ike_crypto_profile.list(
            folder="test-folder",
            exclude_folders=["exclude-folder"],
        )

        assert len(result) == 1
        assert result[0].name == "test-profile"
        assert result[0].folder == "test-folder"

    def test_list_with_exclude_snippets(self, ike_crypto_profile, list_response):
        """Test list with exclude_snippets."""
        # Add snippet field to profiles
        list_response["data"][0]["snippet"] = "keep-snippet"
        list_response["data"][1]["snippet"] = "exclude-snippet"
        self.mock_scm.get.return_value = list_response

        result = ike_crypto_profile.list(
            folder="test-folder",
            exclude_snippets=["exclude-snippet"],
        )

        assert len(result) == 1
        assert result[0].name == "test-profile"
        assert result[0].snippet == "keep-snippet"

    def test_list_with_exclude_devices(self, ike_crypto_profile, list_response):
        """Test list with exclude_devices."""
        # Add device field to profiles
        list_response["data"][0]["device"] = "keep-device"
        list_response["data"][1]["device"] = "exclude-device"
        self.mock_scm.get.return_value = list_response

        result = ike_crypto_profile.list(
            folder="test-folder",
            exclude_devices=["exclude-device"],
        )

        assert len(result) == 1
        assert result[0].name == "test-profile"
        assert result[0].device == "keep-device"


class TestIKECryptoProfileFetch(TestIKECryptoProfileBase):
    """Test IKE Crypto Profile fetch method."""

    def test_fetch_ike_crypto_profile(self, ike_crypto_profile, sample_profile_response):
        """Test fetching an IKE crypto profile by name."""
        self.mock_scm.get.return_value = sample_profile_response

        result = ike_crypto_profile.fetch("test-profile", folder="test-folder")

        self.mock_scm.get.assert_called_once()
        call_args = self.mock_scm.get.call_args
        assert call_args[0][0] == "/config/network/v1/ike-crypto-profiles"
        assert call_args[1]["params"]["name"] == "test-profile"
        assert call_args[1]["params"]["folder"] == "test-folder"

        assert isinstance(result, IKECryptoProfileResponseModel)
        assert result.name == "test-profile"
        assert str(result.id) == "123e4567-e89b-12d3-a456-426655440000"

    def test_fetch_with_empty_name(self, ike_crypto_profile):
        """Test fetch with empty name."""
        with pytest.raises(MissingQueryParameterError) as exc:
            ike_crypto_profile.fetch("", folder="test-folder")
        assert '"name" is not allowed to be empty' in str(exc.value)

    def test_fetch_with_empty_folder(self, ike_crypto_profile):
        """Test fetch with empty folder."""
        with pytest.raises(MissingQueryParameterError) as exc:
            ike_crypto_profile.fetch("test-profile", folder="")
        assert '"folder" is not allowed to be empty' in str(exc.value)

    def test_fetch_with_no_container(self, ike_crypto_profile):
        """Test fetch with no container."""
        with pytest.raises(InvalidObjectError) as exc:
            ike_crypto_profile.fetch("test-profile")
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(exc.value)

    def test_fetch_with_multiple_containers(self, ike_crypto_profile):
        """Test fetch with multiple containers."""
        with pytest.raises(InvalidObjectError) as exc:
            ike_crypto_profile.fetch("test-profile", folder="test-folder", snippet="test-snippet")
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(exc.value)

    def test_fetch_with_invalid_response_format(self, ike_crypto_profile):
        """Test fetch with invalid response format."""
        self.mock_scm.get.return_value = "invalid"

        with pytest.raises(InvalidObjectError) as exc:
            ike_crypto_profile.fetch("test-profile", folder="test-folder")
        assert "Response is not a dictionary" in str(exc.value)

    def test_fetch_with_missing_id_field(self, ike_crypto_profile):
        """Test fetch with missing id field."""
        self.mock_scm.get.return_value = {"name": "test-profile"}

        with pytest.raises(InvalidObjectError) as exc:
            ike_crypto_profile.fetch("test-profile", folder="test-folder")
        assert "Response missing 'id' field" in str(exc.value)
