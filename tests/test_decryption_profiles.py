# tests/test_decryption_profiles.py

import pytest
from unittest.mock import MagicMock, patch

from pydantic import ValidationError
from scm.config.security.decryption_profile import DecryptionProfile
from scm.models.security.decryption_profiles import (
    DecryptionProfileRequestModel,
    DecryptionProfileResponseModel,
    SSLProtocolSettings,
    SSLForwardProxy,
    SSLInboundProxy,
    SSLNoProxy,
    SSLVersion,
    DecryptionProfilesResponse,
)


def test_list_decryption_profiles(load_env, mock_scm):
    """
    Test listing decryption profiles.
    """
    # Mock response from the API client
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
            },
            {
                "id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
                "name": "default",
                "folder": "All",
                "snippet": "predefined-snippet",
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
            },
        ],
        "offset": 0,
        "total": 2,
        "limit": 200,
    }

    # Mock the API client's get method
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of DecryptionProfile with the mocked Scm
    decryption_profile_client = DecryptionProfile(mock_scm)

    # Call the list method
    profiles = decryption_profile_client.list(folder="All")

    # Assertions
    mock_scm.get.assert_called_once_with(
        "/config/security/v1/decryption-profiles", params={"folder": "All"}
    )
    assert isinstance(profiles, list)
    assert len(profiles) == 2
    assert isinstance(profiles[0], DecryptionProfileResponseModel)
    assert profiles[0].name == "web-security-default"
    assert profiles[0].folder == "All"
    assert profiles[0].snippet == "Web-Security-Default"
    assert profiles[0].ssl_protocol_settings.min_version == SSLVersion.tls1_2
    assert profiles[0].ssl_protocol_settings.max_version == SSLVersion.max
    assert profiles[0].ssl_forward_proxy.auto_include_altname is True
    assert profiles[0].ssl_forward_proxy.block_client_cert is True


def test_create_decryption_profile(load_env, mock_scm):
    """
    Test creating a decryption profile.
    """
    # Prepare test data
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

    # Expected payload after model processing
    expected_payload = test_profile_data.copy()

    # Mock response from the API client
    mock_response = expected_payload.copy()
    mock_response["id"] = "444e4567-e89b-12d3-a456-426655440003"  # Mocked ID

    # Mock the API client's post method
    mock_scm.post = MagicMock(return_value=mock_response)

    # Create an instance of DecryptionProfile with the mocked Scm
    decryption_profile_client = DecryptionProfile(mock_scm)

    # Call the create method
    created_profile = decryption_profile_client.create(test_profile_data)

    # Assertions
    mock_scm.post.assert_called_once_with(
        "/config/security/v1/decryption-profiles", json=expected_payload
    )
    assert isinstance(created_profile, DecryptionProfileResponseModel)
    assert created_profile.id == "444e4567-e89b-12d3-a456-426655440003"
    assert created_profile.name == "NewDecryptionProfile"
    assert created_profile.ssl_protocol_settings.min_version == SSLVersion.tls1_2
    assert created_profile.ssl_protocol_settings.max_version == SSLVersion.tls1_3
    assert created_profile.ssl_protocol_settings.enc_algo_rc4 is False
    assert created_profile.ssl_protocol_settings.auth_algo_sha1 is False


def test_get_decryption_profile(load_env, mock_scm):
    """
    Test retrieving a decryption profile by ID.
    """
    # Mock response from the API client
    profile_id = "f6e434b2-f3f8-48bd-b84f-745e0daee648"
    mock_response = {
        "id": profile_id,
        "name": "ExistingDecryptionProfile",
        "folder": "All",
        "ssl_forward_proxy": {
            "block_expired_certificate": True,
            "block_untrusted_issuer": True,
        },
        "ssl_protocol_settings": {
            "min_version": "tls1-2",
            "max_version": "max",
            "enc_algo_rc4": False,
            "auth_algo_sha1": False,
        },
    }

    # Mock the API client's get method
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of DecryptionProfile with the mocked Scm
    decryption_profile_client = DecryptionProfile(mock_scm)

    # Call the get method
    profile = decryption_profile_client.get(profile_id)

    # Assertions
    mock_scm.get.assert_called_once_with(
        f"/config/security/v1/decryption-profiles/{profile_id}"
    )
    assert isinstance(profile, DecryptionProfileResponseModel)
    assert profile.id == profile_id
    assert profile.name == "ExistingDecryptionProfile"
    assert profile.ssl_protocol_settings.min_version == SSLVersion.tls1_2
    assert profile.ssl_protocol_settings.max_version == SSLVersion.max


def test_update_decryption_profile(load_env, mock_scm):
    """
    Test updating a decryption profile.
    """
    # Prepare test data
    profile_id = "f6e434b2-f3f8-48bd-b84f-745e0daee648"
    update_data = {
        "name": "UpdatedDecryptionProfile",
        "folder": "All",
        "ssl_forward_proxy": {
            "block_expired_certificate": False,
            "block_untrusted_issuer": False,
        },
        "ssl_protocol_settings": {
            "min_version": "tls1-1",
            "max_version": "tls1-2",
            "enc_algo_rc4": True,
            "auth_algo_sha1": True,
        },
    }

    # Expected payload after model processing
    expected_payload = update_data.copy()

    # Mock response from the API client
    mock_response = expected_payload.copy()
    mock_response["id"] = profile_id

    # Mock the API client's put method
    mock_scm.put = MagicMock(return_value=mock_response)

    # Create an instance of DecryptionProfile with the mocked Scm
    decryption_profile_client = DecryptionProfile(mock_scm)

    # Call the update method
    updated_profile = decryption_profile_client.update(profile_id, update_data)

    # Assertions
    mock_scm.put.assert_called_once_with(
        f"/config/security/v1/decryption-profiles/{profile_id}",
        json=expected_payload,
    )
    assert isinstance(updated_profile, DecryptionProfileResponseModel)
    assert updated_profile.id == profile_id
    assert updated_profile.name == "UpdatedDecryptionProfile"
    assert updated_profile.ssl_protocol_settings.min_version == SSLVersion.tls1_1
    assert updated_profile.ssl_protocol_settings.max_version == SSLVersion.tls1_2
    assert updated_profile.ssl_protocol_settings.enc_algo_rc4 is True
    assert updated_profile.ssl_protocol_settings.auth_algo_sha1 is True


def test_delete_decryption_profile(load_env, mock_scm):
    """
    Test deleting a decryption profile.
    """
    # Prepare test data
    profile_id = "f6e434b2-f3f8-48bd-b84f-745e0daee648"

    # Mock the API client's delete method
    mock_scm.delete = MagicMock(return_value=None)

    # Create an instance of DecryptionProfile with the mocked Scm
    decryption_profile_client = DecryptionProfile(mock_scm)

    # Call the delete method
    decryption_profile_client.delete(profile_id)

    # Assertions
    mock_scm.delete.assert_called_once_with(
        f"/config/security/v1/decryption-profiles/{profile_id}"
    )


def test_decryption_profile_request_model_validation_errors():
    """
    Test validation errors in DecryptionProfileRequestModel.
    """
    # No container provided
    data_no_container = {
        "name": "InvalidDecryptionProfile",
        "ssl_forward_proxy": {},
    }
    with pytest.raises(ValidationError) as exc_info:
        DecryptionProfileRequestModel(**data_no_container)
    assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
        exc_info.value
    )

    # Multiple containers provided
    data_multiple_containers = {
        "name": "InvalidDecryptionProfile",
        "folder": "Shared",
        "device": "Device1",
        "ssl_forward_proxy": {},
    }
    with pytest.raises(ValidationError) as exc_info:
        DecryptionProfileRequestModel(**data_multiple_containers)
    assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
        exc_info.value
    )

    # Invalid name pattern
    data_invalid_name = {
        "name": "Invalid Name!",  # Contains an exclamation mark
        "folder": "Shared",
        "ssl_forward_proxy": {},
    }
    with pytest.raises(ValidationError) as exc_info:
        DecryptionProfileRequestModel(**data_invalid_name)
    assert "1 validation error for DecryptionProfileRequestModel" in str(exc_info.value)

    # Invalid min_version and max_version (max_version less than min_version)
    data_invalid_versions = {
        "name": "InvalidVersionsProfile",
        "folder": "Shared",
        "ssl_protocol_settings": {
            "min_version": "tls1-2",
            "max_version": "tls1-0",  # Less than min_version
        },
    }
    with pytest.raises(ValueError) as exc_info:
        DecryptionProfileRequestModel(**data_invalid_versions)
    assert "max_version cannot be less than min_version" in str(exc_info.value)

    # Invalid SSLVersion value
    data_invalid_ssl_version = {
        "name": "InvalidSSLVersionProfile",
        "folder": "Shared",
        "ssl_protocol_settings": {
            "min_version": "tls1-5",  # Invalid SSL version
            "max_version": "max",
        },
    }
    with pytest.raises(ValueError) as exc_info:
        DecryptionProfileRequestModel(**data_invalid_ssl_version)
    assert "1 validation error for DecryptionProfileRequestModel" in str(exc_info.value)
    assert (
        "Input should be 'sslv3', 'tls1-0', 'tls1-1', 'tls1-2', 'tls1-3' or 'max'"
        in str(exc_info.value)
    )

    # Invalid UUID in id field (for response model)
    data_invalid_id = {
        "id": "invalid-uuid",
        "name": "TestProfile",
        "folder": "Shared",
        "ssl_forward_proxy": {},
    }
    with pytest.raises(ValueError) as exc_info:
        DecryptionProfileResponseModel(**data_invalid_id)
    assert "Invalid UUID format for 'id'" in str(exc_info.value)


def test_decryption_profile_list_validation_error(load_env, mock_scm):
    """
    Test validation error when listing with multiple containers.
    """
    # Create an instance of DecryptionProfile with the mocked Scm
    decryption_profile_client = DecryptionProfile(mock_scm)

    # Attempt to call the list method with multiple containers
    with pytest.raises(ValueError) as exc_info:  # Change ValidationError to ValueError
        decryption_profile_client.list(folder="Shared", snippet="TestSnippet")

    # Assertions
    assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
        exc_info.value
    )


def test_decryption_profile_list_with_invalid_pagination(load_env, mock_scm):
    """
    Test validation error when invalid pagination parameters are provided.
    """
    # Create an instance of DecryptionProfile with the mocked Scm
    decryption_profile_client = DecryptionProfile(mock_scm)

    # Attempt to call the list method with invalid pagination parameters
    with pytest.raises(ValueError) as exc_info:
        decryption_profile_client.list(folder="All", offset=-1, limit=0)

    # Assertions
    assert "Offset must be a non-negative integer" in str(exc_info.value)
    assert "Limit must be a positive integer" in str(exc_info.value)


def test_list_decryption_profiles_with_pagination(load_env, mock_scm):
    """
    Test listing decryption profiles with pagination parameters.
    """
    # Mock response from the API client
    mock_response = {
        "data": [
            {
                "id": "223e4567-e89b-12d3-a456-426655440001",
                "name": "TestProfile2",
                "folder": "Prisma Access",
                "rules": [],
                "threat_exception": [],
            },
        ],
        "offset": 1,
        "total": 2,
        "limit": 1,
    }

    # Mock the API client's get method
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of DecryptionProfile with the mocked Scm
    decryption_profile_client = DecryptionProfile(mock_scm)

    # Call the list method with pagination parameters
    profiles = decryption_profile_client.list(folder="Prisma Access", offset=1, limit=1)

    # Assertions
    mock_scm.get.assert_called_once_with(
        "/config/security/v1/decryption-profiles",
        params={"folder": "Prisma Access", "offset": 1, "limit": 1},
    )
    assert isinstance(profiles, list)
    assert len(profiles) == 1
    assert profiles[0].name == "TestProfile2"
    assert profiles[0].id == "223e4567-e89b-12d3-a456-426655440001"


def test_decryption_profile_list_with_name_filter(load_env, mock_scm):
    """
    Test listing decryption profiles with name filter.
    """
    # Mock response from the API client
    mock_response = {
        "data": [
            {
                "id": "93c1ac24-39f0-4556-a446-f131f71a43b3",
                "name": "SpecificProfile",
                "folder": "All",
                "ssl_forward_proxy": {},
            },
        ],
        "offset": 0,
        "total": 1,
        "limit": 200,
    }

    # Mock the API client's get method
    mock_scm.get = MagicMock(return_value=mock_response)

    # Create an instance of DecryptionProfile with the mocked Scm
    decryption_profile_client = DecryptionProfile(mock_scm)

    # Call the list method with name filter
    profiles = decryption_profile_client.list(folder="All", name="SpecificProfile")

    # Assertions
    mock_scm.get.assert_called_once_with(
        "/config/security/v1/decryption-profiles",
        params={"folder": "All", "name": "SpecificProfile"},
    )
    assert isinstance(profiles, list)
    assert len(profiles) == 1
    assert profiles[0].name == "SpecificProfile"
    assert profiles[0].id == "93c1ac24-39f0-4556-a446-f131f71a43b3"


def test_ssl_protocol_settings_model_validation():
    """
    Test validation in SSLProtocolSettings model.
    """
    # Valid data
    valid_data = {
        "min_version": "tls1-0",
        "max_version": "tls1-2",
    }
    settings = SSLProtocolSettings(**valid_data)
    assert settings.min_version == SSLVersion.tls1_0
    assert settings.max_version == SSLVersion.tls1_2

    # Invalid min_version (not in SSLVersion)
    invalid_min_version = {
        "min_version": "tls1-5",
        "max_version": "tls1-2",
    }
    with pytest.raises(ValidationError) as exc_info:
        SSLProtocolSettings(**invalid_min_version)
    assert (
        "Input should be 'sslv3', 'tls1-0', 'tls1-1', 'tls1-2', 'tls1-3' or 'max'"
        in str(exc_info.value)
    )

    # Invalid max_version less than min_version
    invalid_version_order = {
        "min_version": "tls1-2",
        "max_version": "tls1-0",
    }
    with pytest.raises(ValidationError) as exc_info:
        SSLProtocolSettings(**invalid_version_order)
    assert "max_version cannot be less than min_version" in str(exc_info.value)

    # Test default values
    default_settings = SSLProtocolSettings()
    assert default_settings.auth_algo_md5 is True
    assert default_settings.enc_algo_rc4 is True
    assert default_settings.min_version == SSLVersion.tls1_0
    assert default_settings.max_version == SSLVersion.tls1_2

    # Test custom settings
    custom_settings = SSLProtocolSettings(
        auth_algo_md5=False,
        enc_algo_rc4=False,
        keyxchg_algo_dhe=False,
        min_version="tls1-1",
        max_version="tls1-3",
    )
    assert custom_settings.auth_algo_md5 is False
    assert custom_settings.enc_algo_rc4 is False
    assert custom_settings.keyxchg_algo_dhe is False
    assert custom_settings.min_version == SSLVersion.tls1_1
    assert custom_settings.max_version == SSLVersion.tls1_3


def test_ssl_forward_proxy_model():
    """
    Test SSLForwardProxy model.
    """
    # Test default values
    default_proxy = SSLForwardProxy()
    assert default_proxy.auto_include_altname is False
    assert default_proxy.block_client_cert is False

    # Test custom values
    custom_proxy = SSLForwardProxy(
        auto_include_altname=True,
        block_client_cert=True,
        block_expired_certificate=True,
        block_untrusted_issuer=True,
    )
    assert custom_proxy.auto_include_altname is True
    assert custom_proxy.block_client_cert is True
    assert custom_proxy.block_expired_certificate is True
    assert custom_proxy.block_untrusted_issuer is True


def test_ssl_inbound_proxy_model():
    """
    Test SSLInboundProxy model.
    """
    # Test default values
    default_inbound_proxy = SSLInboundProxy()
    assert default_inbound_proxy.block_if_hsm_unavailable is False

    # Test custom values
    custom_inbound_proxy = SSLInboundProxy(
        block_if_hsm_unavailable=True,
        block_if_no_resource=True,
    )
    assert custom_inbound_proxy.block_if_hsm_unavailable is True
    assert custom_inbound_proxy.block_if_no_resource is True


def test_ssl_no_proxy_model():
    """
    Test SSLNoProxy model.
    """
    # Test default values
    default_no_proxy = SSLNoProxy()
    assert default_no_proxy.block_expired_certificate is False

    # Test custom values
    custom_no_proxy = SSLNoProxy(
        block_expired_certificate=True,
        block_untrusted_issuer=True,
    )
    assert custom_no_proxy.block_expired_certificate is True
    assert custom_no_proxy.block_untrusted_issuer is True


def test_decryption_profile_request_model():
    """
    Test DecryptionProfileRequestModel.
    """
    # Valid data
    valid_data = {
        "name": "ValidProfile",
        "folder": "Shared",
        "ssl_forward_proxy": {
            "block_expired_certificate": True,
        },
        "ssl_protocol_settings": {
            "min_version": "tls1-2",
            "max_version": "tls1-3",
        },
    }
    profile = DecryptionProfileRequestModel(**valid_data)
    assert profile.name == "ValidProfile"
    assert profile.folder == "Shared"
    assert profile.ssl_forward_proxy.block_expired_certificate is True
    assert profile.ssl_protocol_settings.min_version == SSLVersion.tls1_2

    # Invalid container validation (no container provided)
    invalid_data_no_container = {
        "name": "InvalidProfile",
        "ssl_forward_proxy": {},
    }
    with pytest.raises(ValueError) as exc_info:
        DecryptionProfileRequestModel(**invalid_data_no_container)
    assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
        exc_info.value
    )

    # Invalid name pattern
    invalid_name_data = {
        "name": "Invalid!Name",  # Contains invalid character '!'
        "folder": "Shared",
    }
    with pytest.raises(ValueError) as exc_info:
        DecryptionProfileRequestModel(**invalid_name_data)
    assert "1 validation error for DecryptionProfileRequestModel" in str(exc_info.value)
    assert "String should match pattern" in str(exc_info.value)

    # Test that 'folder', 'snippet', or 'device' fields accept valid patterns
    valid_folder_data = {
        "name": "ValidProfile",
        "folder": "My_Folder-1.0",
    }
    profile = DecryptionProfileRequestModel(**valid_folder_data)
    assert profile.folder == "My_Folder-1.0"

    # Invalid pattern in 'folder' field
    invalid_folder_data = {
        "name": "ValidProfile",
        "folder": "Invalid Folder!",  # Contains '!'
    }
    with pytest.raises(ValueError) as exc_info:
        DecryptionProfileRequestModel(**invalid_folder_data)
    assert "1 validation error for DecryptionProfileRequestModel" in str(exc_info.value)
    assert "String should match pattern" in str(exc_info.value)


def test_decryption_profile_response_model():
    """
    Test DecryptionProfileResponseModel.
    """
    # Valid data
    valid_data = {
        "id": "f6e434b2-f3f8-48bd-b84f-745e0daee648",
        "name": "ValidProfile",
        "folder": "Shared",
    }
    profile = DecryptionProfileResponseModel(**valid_data)
    assert profile.id == "f6e434b2-f3f8-48bd-b84f-745e0daee648"
    assert profile.name == "ValidProfile"
    assert profile.folder == "Shared"

    # Invalid UUID in 'id' field
    invalid_id_data = {
        "id": "invalid-uuid",
        "name": "ValidProfile",
        "folder": "Shared",
    }
    with pytest.raises(ValueError) as exc_info:
        DecryptionProfileResponseModel(**invalid_id_data)
    assert "Invalid UUID format for 'id'" in str(exc_info.value)


def test_decryption_profiles_response_model():
    """
    Test DecryptionProfilesResponse model.
    """
    # Valid data
    valid_data = {
        "data": [
            {
                "id": "f6e434b2-f3f8-48bd-b84f-745e0daee648",
                "name": "Profile1",
                "folder": "Shared",
            },
            {
                "id": "93c1ac24-39f0-4556-a446-f131f71a43b3",
                "name": "Profile2",
                "folder": "Shared",
            },
        ],
        "offset": 0,
        "total": 2,
        "limit": 200,
    }
    response = DecryptionProfilesResponse(**valid_data)
    assert len(response.data) == 2
    assert response.data[0].name == "Profile1"
    assert response.offset == 0
    assert response.total == 2
    assert response.limit == 200


def test_ssl_protocol_settings_validator_with_max_version_less_than_min_version():
    """
    Test that validator raises error when max_version is less than min_version.
    """
    invalid_data = {
        "min_version": "tls1-2",
        "max_version": "tls1-1",
    }
    with pytest.raises(ValidationError) as exc_info:
        SSLProtocolSettings(**invalid_data)
    assert "max_version cannot be less than min_version" in str(exc_info.value)


def test_decryption_profile_create_with_invalid_ssl_versions(load_env, mock_scm):
    """
    Test creating a decryption profile with invalid SSL versions.
    """
    # Prepare test data with invalid SSL versions
    test_profile_data = {
        "name": "InvalidSSLVersionsProfile",
        "folder": "All",
        "ssl_protocol_settings": {
            "min_version": "tls1-3",
            "max_version": "tls1-0",
        },
    }

    # Create an instance of DecryptionProfile with the mocked Scm
    decryption_profile_client = DecryptionProfile(mock_scm)

    # Attempt to call the create method
    with pytest.raises(ValidationError) as exc_info:
        DecryptionProfileRequestModel(**test_profile_data)
    assert "max_version cannot be less than min_version" in str(exc_info.value)

    # Ensure that the create method is not called when validation fails
    with patch.object(mock_scm, "post", autospec=True) as mock_post:
        try:
            decryption_profile_client.create(test_profile_data)
        except ValidationError:
            pass
        mock_post.assert_not_called()
