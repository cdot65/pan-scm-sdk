# tests/scm/config/security/test_decryption_profile.py

import pytest
from unittest.mock import MagicMock

from scm.config.security.decryption_profile import DecryptionProfile
from scm.exceptions import (
    APIError,
    BadRequestError,
    InvalidObjectError,
    ObjectNotPresentError,
    MalformedCommandError,
    MissingQueryParameterError,
    ConflictError,
    ReferenceNotZeroError,
)
from scm.models.security.decryption_profiles import (
    DecryptionProfileCreateModel,
    DecryptionProfileResponseModel,
    SSLProtocolSettings,
    SSLVersion,
)

from pydantic import ValidationError as PydanticValidationError


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


# -------------------- Test Classes Grouped by Functionality --------------------


class TestDecryptionProfileModelValidation(TestDecryptionProfileBase):
    """Tests for object model validation."""

    def test_object_model_no_container_provided(self):
        """Test validation when no container is provided."""
        data = {
            "name": "InvalidProfile",
            "ssl_forward_proxy": {},
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            DecryptionProfileCreateModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_object_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = {
            "name": "TestProfile",
            "folder": "Shared",
            "snippet": "TestSnippet",
            "ssl_forward_proxy": {},
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            DecryptionProfileCreateModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

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


class TestDecryptionProfileList(TestDecryptionProfileBase):
    """Tests for listing Decryption Profile objects."""

    def test_list_objects(self):
        """
        **Objective:** Test listing all objects.
        **Workflow:**
            1. Sets up a mock response resembling the expected API response for listing objects.
            2. Calls the `list` method with a filter parameter.
            3. Asserts that the mocked service was called correctly.
            4. Validates the returned list of objects.
        """
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
        existing_objects = self.client.list(folder="All")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/security/v1/decryption-profiles",
            params={
                "limit": 10000,
                "folder": "All",
            },
        )
        assert isinstance(existing_objects, list)
        assert isinstance(existing_objects[0], DecryptionProfileResponseModel)
        assert existing_objects[0].name == "web-security-default"
        assert (
            existing_objects[0].ssl_protocol_settings.min_version == SSLVersion.tls1_2
        )

    def test_object_list_multiple_containers(self):
        """Test validation error when listing with multiple containers."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Prisma Access", snippet="TestSnippet")

        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )


class TestDecryptionProfileCreate(TestDecryptionProfileBase):
    """Tests for creating Decryption Profile objects."""

    def test_create_object(self):
        """
        **Objective:** Test creating a new object.
        **Workflow:**
            1. Creates test data.
            2. Mocks the API response.
            3. Verifies the creation request and response.
        """
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
        assert str(created_profile.id) == "444e4567-e89b-12d3-a456-426655440003"

    def test_create_object_error_handling(self):
        """
        **Objective:** Test error handling during object creation.
        **Workflow:**
            1. Mocks an error response from the API
            2. Attempts to create an object
            3. Verifies proper error handling and exception raising
        """
        test_data = {
            "name": "NewDecryptionProfile",
            "folder": "All",
            "ssl_forward_proxy": {
                "block_expired_certificate": True,
                "block_untrusted_issuer": True,
            },
        }

        # Mock error response
        mock_error_response = {
            "_errors": [
                {
                    "code": "API_I00013",
                    "message": "Object creation failed",
                    "details": {"errorType": "Object Already Exists"},
                }
            ],
            "_request_id": "test-request-id",
        }

        # Configure mock to raise exception
        self.mock_scm.post.side_effect = Exception()  # noqa
        self.mock_scm.post.side_effect.response = MagicMock()  # noqa
        self.mock_scm.post.side_effect.response.json = MagicMock(  # noqa
            return_value=mock_error_response
        )

        with pytest.raises(APIError):
            self.client.create(test_data)

    def test_create_generic_exception_handling(self):
        """
        **Objective:** Test generic exception handling in create method.
        **Workflow:**
            1. Mocks a generic exception without response attribute
            2. Verifies APIError is raised with correct message
        """
        test_data = {
            "name": "NewDecryptionProfile",
            "folder": "All",
            "ssl_forward_proxy": {
                "block_expired_certificate": True,
                "block_untrusted_issuer": True,
            },
        }

        # Mock a generic exception without response
        self.mock_scm.post.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.create(test_data)
        assert str(exc_info.value) == "An unexpected error occurred"

    def test_create_malformed_response_handling(self):
        """
        **Objective:** Test handling of malformed response in create method.
        **Workflow:**
            1. Mocks a response that would cause a parsing error
            2. Verifies appropriate error handling
        """
        test_data = {
            "name": "NewDecryptionProfile",
            "folder": "All",
            "ssl_forward_proxy": {
                "block_expired_certificate": True,
                "block_untrusted_issuer": True,
            },
        }

        # Mock invalid JSON response
        self.mock_scm.post.return_value = {"malformed": "response"}  # noqa

        with pytest.raises(APIError):
            self.client.create(test_data)


class TestDecryptionProfileGet(TestDecryptionProfileBase):
    """Tests for retrieving a specific Decryption Profile object."""

    def test_get_object(self):
        """
        **Objective:** Test retrieving a specific object.
        **Workflow:**
            1. Mocks the API response for a specific object.
            2. Verifies the get request and response handling.
        """
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
        get_object = self.client.get(profile_id)

        self.mock_scm.get.assert_called_once_with(  # noqa
            f"/config/security/v1/decryption-profiles/{profile_id}"
        )
        assert isinstance(get_object, DecryptionProfileResponseModel)
        assert str(get_object.id) == profile_id

    def test_get_object_error_handling(self):
        """
        **Objective:** Test error handling during object retrieval.
        **Workflow:**
            1. Mocks an error response from the API
            2. Attempts to get an object
            3. Verifies proper error handling and exception raising
        """
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        mock_error_response = {
            "_errors": [
                {
                    "code": "API_I00013",
                    "message": "Object not found",
                    "details": {"errorType": "Object Not Present"},
                }
            ],
            "_request_id": "test-request-id",
        }

        self.mock_scm.get.side_effect = Exception()  # noqa
        self.mock_scm.get.side_effect.response = MagicMock()  # noqa
        self.mock_scm.get.side_effect.response.json = MagicMock(  # noqa
            return_value=mock_error_response
        )

        with pytest.raises(ObjectNotPresentError):
            self.client.get(object_id)

    def test_get_generic_exception_handling(self):
        """
        **Objective:** Test generic exception handling in get method.
        **Workflow:**
            1. Mocks a generic exception without response attribute
            2. Verifies APIError is raised with correct message
        """
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        # Mock a generic exception without response
        self.mock_scm.get.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.get(object_id)
        assert str(exc_info.value) == "An unexpected error occurred: Generic error"


class TestDecryptionProfileUpdate(TestDecryptionProfileBase):
    """Tests for updating Decryption Profile objects."""

    def test_update_object(self):
        """
        **Objective:** Test updating an object.
        **Workflow:**
            1. Prepares update data and mocks response
            2. Verifies the update request and response
            3. Ensures payload transformation is correct
        """
        from uuid import UUID

        test_uuid = UUID("f6e434b2-f3f8-48bd-b84f-745e0daee648")

        # Test data including ID
        update_data = {
            "id": str(test_uuid),
            "name": "UpdatedDecryptionProfile",
            "folder": "All",
            "ssl_protocol_settings": {
                "min_version": "tls1-1",
                "max_version": "tls1-2",
            },
        }

        # Expected payload should not include the ID
        expected_payload = {
            "name": "UpdatedDecryptionProfile",
            "folder": "All",
            "ssl_protocol_settings": {
                "min_version": "tls1-1",
                "max_version": "tls1-2",
            },
        }

        # Mock response should include the ID
        mock_response = update_data.copy()
        self.mock_scm.put.return_value = mock_response  # noqa

        # Perform update
        updated_object = self.client.update(update_data)

        # Verify correct endpoint and payload
        self.mock_scm.put.assert_called_once_with(  # noqa
            f"/config/security/v1/decryption-profiles/{update_data['id']}",
            json=expected_payload,  # Should not include ID
        )

        # Verify response model
        assert isinstance(updated_object, DecryptionProfileResponseModel)
        assert isinstance(updated_object.id, UUID)  # Verify it's a UUID object
        assert updated_object.id == test_uuid  # Compare against UUID object
        assert (
            str(updated_object.id) == update_data["id"]
        )  # Compare string representations
        assert updated_object.name == "UpdatedDecryptionProfile"
        assert updated_object.ssl_protocol_settings.min_version == SSLVersion.tls1_1
        assert updated_object.ssl_protocol_settings.max_version == SSLVersion.tls1_2

    def test_update_object_error_handling(self):
        """
        **Objective:** Test error handling during object update.
        **Workflow:**
            1. Mocks an error response from the API
            2. Attempts to update an object
            3. Verifies proper error handling and exception raising
        """
        update_data = {
            "id": "f6e434b2-f3f8-48bd-b84f-745e0daee648",
            "name": "test-profile",
            "folder": "Shared",
            "ssl_protocol_settings": {
                "min_version": "tls1-1",
                "max_version": "tls1-2",
            },
        }

        mock_error_response = {
            "_errors": [
                {
                    "code": "API_I00013",
                    "message": "Update failed",
                    "details": {"errorType": "Malformed Command"},
                }
            ],
            "_request_id": "test-request-id",
        }

        self.mock_scm.put.side_effect = Exception()  # noqa
        self.mock_scm.put.side_effect.response = MagicMock()  # noqa
        self.mock_scm.put.side_effect.response.json = MagicMock(  # noqa
            return_value=mock_error_response
        )

        with pytest.raises(MalformedCommandError):
            self.client.update(update_data)

    def test_update_with_invalid_data(self):
        """
        **Objective:** Test update method with invalid data structure.
        **Workflow:**
            1. Attempts to update with invalid data
            2. Verifies proper validation error handling
        """
        invalid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "invalid_field": "test",
        }

        with pytest.raises(APIError):
            self.client.update(invalid_data)

    def test_update_generic_exception_handling(self):
        """
        **Objective:** Test generic exception handling in update method.
        **Workflow:**
            1. Mocks a generic exception without response attribute
            2. Verifies APIError is raised with correct message
        """
        update_data = {
            "id": "f6e434b2-f3f8-48bd-b84f-745e0daee648",
            "name": "test-profile",
            "folder": "Shared",
            "ssl_protocol_settings": {
                "min_version": "tls1-1",
                "max_version": "tls1-2",
            },
        }

        # Mock a generic exception without response
        self.mock_scm.put.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.update(update_data)
        assert str(exc_info.value) == "An unexpected error occurred: Generic error"


class TestDecryptionProfileDelete(TestDecryptionProfileBase):
    """Tests for deleting Decryption Profile objects."""

    def test_delete_referenced_object(self):
        """
        **Objective:** Test deleting an object that is referenced by other objects.
        **Workflow:**
            1. Sets up a mock error response for a referenced object deletion attempt
            2. Attempts to delete an object that is referenced by other objects
            3. Validates that ReferenceNotZeroError is raised with correct details
        """
        object_id = "3fecfe58-af0c-472b-85cf-437bb6df2929"

        # Mock the API error response
        mock_error_response = {
            "_errors": [
                {
                    "code": "E009",  # Changed from API_I00013 to E009
                    "message": "Your configuration is not valid. Please review the error message for more details.",
                    "details": {
                        "errorType": "Reference Not Zero",
                        "message": [
                            " container -> Texas -> security-profile-group -> custom-group -> decryption"
                        ],
                        "errors": [
                            {
                                "type": "NON_ZERO_REFS",
                                "message": "Node cannot be deleted because of references from",
                                "params": ["custom-profile"],
                                "extra": [
                                    "container/[Texas]/security-profile-group/[custom-group]/decryption/[custom-profile]"
                                ],
                            }
                        ],
                    },
                }
            ],
            "_request_id": "8fe3b025-feb7-41d9-bf88-3938c0b33116",
        }

        # Configure mock with status code
        mock_exc = Exception()
        mock_exc.response = MagicMock()
        mock_exc.response.status_code = 409  # Add status code
        mock_exc.response.json.return_value = mock_error_response
        self.mock_scm.delete.side_effect = mock_exc

        with pytest.raises(ReferenceNotZeroError) as exc_info:
            self.client.delete(object_id)

    def test_delete_error_handling(self):
        """
        **Objective:** Test error handling during object deletion.
        **Workflow:**
            1. Mocks various error scenarios
            2. Verifies proper error handling for each case
        """
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        # Test object not found
        mock_error_response = {
            "_errors": [
                {
                    "code": "API_I00013",
                    "message": "Object not found",
                    "details": {"errorType": "Object Not Present"},
                }
            ],
            "_request_id": "test-request-id",
        }

        self.mock_scm.delete.side_effect = Exception()  # noqa
        self.mock_scm.delete.side_effect.response = MagicMock()  # noqa
        self.mock_scm.delete.side_effect.response.json = MagicMock(  # noqa
            return_value=mock_error_response
        )

        with pytest.raises(ObjectNotPresentError):
            self.client.delete(object_id)

    def test_delete_generic_exception_handling(self):
        """
        **Objective:** Test generic exception handling in delete method.
        **Workflow:**
            1. Mocks a generic exception without response attribute
            2. Verifies APIError is raised with correct message
        """
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        # Mock a generic exception without response
        self.mock_scm.delete.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.delete(object_id)
        assert str(exc_info.value) == "An unexpected error occurred: Generic error"


class TestDecryptionProfileFetch(TestDecryptionProfileBase):
    """Tests for fetching Decryption Profile objects by name."""

    def test_fetch_object(self):
        """
        **Objective:** Test retrieving an object by its name using the `fetch` method.
        **Workflow:**
            1. Sets up a mock response resembling the expected API response for fetching an object by name.
            2. Calls the `fetch` method of `self.client` with a specific name and container.
            3. Asserts that the mocked service was called with the correct URL and parameters.
            4. Validates the returned object's attributes.
        """
        mock_response = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-profile",
            "folder": "Shared",
            "ssl_protocol_settings": {
                "min_version": "tls1-2",
                "max_version": "max",
            },
            "description": None,  # Should be excluded in the result
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        # Call the fetch method
        fetched_object = self.client.fetch(
            name=mock_response["name"],
            folder=mock_response["folder"],
        )

        # Assert that the GET request was made with the correct parameters
        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/security/v1/decryption-profiles",
            params={
                "folder": mock_response["folder"],
                "name": mock_response["name"],
            },
        )

        # Validate the returned object
        assert isinstance(fetched_object, dict)
        assert str(fetched_object["id"]) == mock_response["id"]
        assert fetched_object["name"] == mock_response["name"]
        assert fetched_object["ssl_protocol_settings"]["min_version"] == "tls1-2"

    def test_fetch_object_not_found(self):
        """
        Test fetching an object by name that does not exist.
        """
        object_name = "NonExistent"
        folder_name = "Shared"
        mock_response = {
            "_errors": [
                {
                    "code": "E005",  # Changed from API_I00013 to E005
                    "message": "Object not found",
                    "details": {"errorType": "Object Not Present"},
                }
            ],
            "_request_id": "12282b0f-eace-41c3-a8e2-4b28992979c4",
        }

        # Configure mock with status code
        mock_exc = Exception()
        mock_exc.response = MagicMock()
        mock_exc.response.status_code = 404  # Add status code
        mock_exc.response.json.return_value = mock_response
        self.mock_scm.get.side_effect = mock_exc

        with pytest.raises(ObjectNotPresentError):
            self.client.fetch(name=object_name, folder=folder_name)

    def test_fetch_empty_name(self):
        """
        **Objective:** Test fetch with empty name parameter.
        **Workflow:**
            1. Attempts to fetch with empty name
            2. Verifies MissingQueryParameterError is raised
        """
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="", folder="Shared")
        assert "Field 'name' cannot be empty" in str(exc_info.value)

    def test_fetch_container_validation(self):
        """
        **Objective:** Test container parameter validation in fetch.
        **Workflow:**
            1. Tests various invalid container combinations
            2. Verifies proper error handling
        """
        # Test empty folder
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="test", folder="")
        assert "Field 'folder' cannot be empty" in str(exc_info.value)

        # Test no container provided
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-profile")
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

        # Test multiple containers provided
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(
                name="test-profile", folder="Shared", snippet="TestSnippet"
            )
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_fetch_object_unexpected_response_format(self):
        """
        Test fetching an object when the API returns an unexpected response format.

        **Objective:** Ensure that the fetch method raises APIError when the response format is not as expected.
        **Workflow:**
            1. Mocks the API response to return an unexpected format.
            2. Calls the `fetch` method.
            3. Asserts that APIError is raised.
        """
        group_name = "TestGroup"
        folder_name = "Shared"
        # Mocking an unexpected response format
        mock_response = {"unexpected_key": "unexpected_value"}
        self.mock_scm.get.return_value = mock_response  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.fetch(name=group_name, folder=folder_name)
        assert "Invalid response format: missing 'id' field" in str(exc_info.value)

    def test_fetch_validation_errors(self):
        """
        **Objective:** Test fetch validation errors.
        **Workflow:**
            1. Tests various invalid input scenarios
            2. Verifies appropriate error handling
        """
        # Test empty folder
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="test", folder="")
        assert "Field 'folder' cannot be empty" in str(exc_info.value)

        # Test multiple containers
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test", folder="folder1", snippet="snippet1")
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_fetch_response_format_handling(self):
        """
        **Objective:** Test handling of various response formats in fetch method.
        **Workflow:**
            1. Tests different malformed response scenarios
            2. Verifies appropriate error handling for each case
        """
        # Test malformed response without expected fields
        self.mock_scm.get.return_value = {"unexpected": "format"}  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.fetch(name="test", folder="Shared")
        assert "Invalid response format: missing 'id' field" in str(exc_info.value)

        # Test response with both id and data fields (invalid format)
        self.mock_scm.get.return_value = {  # noqa
            "id": "some-id",
            "data": [{"some": "data"}],
        }  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.fetch(name="test", folder="Shared")
        assert "An unexpected error occurred: 2 validation errors" in str(
            exc_info.value
        )

        # Test malformed response in list format
        self.mock_scm.get.return_value = [{"unexpected": "format"}]  # noqa
        with pytest.raises(APIError) as exc_info:
            self.client.fetch(name="test", folder="Shared")
        assert "Invalid response format: expected dictionary" in str(exc_info.value)

    def test_fetch_error_handler_json_error(self):
        """
        **Objective:** Test fetch method error handling when json() raises an error.
        **Workflow:**
            1. Mocks an exception with a response that raises error on json()
            2. Verifies the original exception is re-raised
        """
        # Create mock exception
        mock_exc = Exception("Original error")
        mock_exc.response = MagicMock()
        mock_exc.response.status_code = 500
        mock_exc.response.json.side_effect = ValueError("JSON parsing error")

        # Configure mock
        self.mock_scm.get.side_effect = mock_exc

        with pytest.raises(ValueError) as exc_info:
            self.client.fetch(name="test", folder="Shared")
        assert str(exc_info.value) == "JSON parsing error"


class TestDecryptionProfileListFilters(TestDecryptionProfileBase):
    """Tests for filtering during listing Decryption Profile objects."""

    def test_list_with_filters(self):
        """
        **Objective:** Test that filters are properly added to parameters.
        **Workflow:**
            1. Calls list with various filters
            2. Verifies filters are properly formatted in the request
        """
        filters = {
            "ssl_protocol_settings": ["tls1-2", "tls1-3"],
            "ssl_forward_proxy": [
                "block_expired_certificate",
                "block_untrusted_issuer",
            ],
        }

        mock_response = {"data": []}
        self.mock_scm.get.return_value = mock_response  # noqa

        self.client.list(folder="Shared", **filters)

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/security/v1/decryption-profiles",
            params={
                "limit": 10000,
                "folder": "Shared",
            },
        )

    def test_list_filters_type_validation(self):
        """
        **Objective:** Test validation of filter types in list method.
        **Workflow:**
            1. Tests various invalid filter type scenarios
            2. Verifies BadRequestError is raised with correct message
            3. Tests valid filter types pass validation
        """
        mock_response = {
            "data": [
                {
                    "id": "1cbeeef0-59dd-49a3-9753-3b7c4d174cef",
                    "name": "Morrowind",
                    "folder": "Shared",
                    "ssl_forward_proxy": {
                        "auto_include_altname": True,
                        "block_client_cert": False,
                        "block_expired_certificate": True,
                        "block_timeout_cert": False,
                        "block_tls13_downgrade_no_resource": False,
                        "block_unknown_cert": False,
                        "block_unsupported_cipher": False,
                        "block_unsupported_version": False,
                        "block_untrusted_issuer": False,
                        "restrict_cert_exts": False,
                        "strip_alpn": False,
                    },
                    "ssl_protocol_settings": {
                        "auth_algo_md5": True,
                        "auth_algo_sha1": True,
                        "auth_algo_sha256": True,
                        "auth_algo_sha384": True,
                        "enc_algo_3des": True,
                        "enc_algo_aes_128_cbc": True,
                        "enc_algo_aes_128_gcm": True,
                        "enc_algo_aes_256_cbc": True,
                        "enc_algo_aes_256_gcm": True,
                        "enc_algo_chacha20_poly1305": True,
                        "enc_algo_rc4": True,
                        "keyxchg_algo_dhe": True,
                        "keyxchg_algo_ecdhe": True,
                        "keyxchg_algo_rsa": True,
                        "max_version": "tls1-2",
                        "min_version": "tls1-0",
                    },
                }
            ],
            "offset": 0,
            "total": 1,
            "limit": 200,
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test invalid types filter (string instead of list)
        with pytest.raises(BadRequestError) as exc_info:
            self.client.list(folder="Shared", types="ssl_forward_proxy")
        assert str(exc_info.value) == "'types' filter must be a list"

        # Test invalid types filter (dict instead of list)
        with pytest.raises(BadRequestError) as exc_info:
            self.client.list(folder="Shared", types={"type": "ssl_forward_proxy"})
        assert str(exc_info.value) == "'types' filter must be a list"

        # Test that valid list filters pass validation
        try:
            self.client.list(
                folder="Shared",
                types=["ssl_forward_proxy"],
            )
        except BadRequestError:
            pytest.fail("Unexpected BadRequestError raised with valid list filters")

    def test_list_empty_folder_error(self):
        """
        **Objective:** Test that empty folder raises appropriate error.
        **Workflow:**
            1. Attempts to list objects with empty folder
            2. Verifies MissingQueryParameterError is raised
        """
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.list(folder="")
        assert "HTTP 400: Error E003: Field 'folder' cannot be empty: Details" in str(
            exc_info.value
        )

    def test_list_error_handling(self):
        """
        **Objective:** Test error handling in list operation.
        **Workflow:**
            1. Mocks an error response from the API
            2. Attempts to list objects
            3. Verifies proper error handling
        """
        mock_error_response = {
            "_errors": [
                {
                    "code": "API_I00013",
                    "message": "Listing failed",
                    "details": {"errorType": "Operation Impossible"},
                }
            ],
            "_request_id": "test-request-id",
        }

        self.mock_scm.get.side_effect = Exception()  # noqa
        self.mock_scm.get.side_effect.response = MagicMock()  # noqa
        self.mock_scm.get.side_effect.response.json = MagicMock(  # noqa
            return_value=mock_error_response
        )

        with pytest.raises(APIError) as exc_info:
            self.client.list(folder="NonexistentFolder")
        assert "An unexpected error occurred" in str(exc_info.value)

    def test_list_generic_exception_handling(self):
        """
        **Objective:** Test generic exception handling in list method.
        **Workflow:**
            1. Mocks a generic exception without response attribute
            2. Verifies APIError is raised with correct message
        """
        # Mock a generic exception without response
        self.mock_scm.get.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.list(folder="Shared")
        assert str(exc_info.value) == "An unexpected error occurred"

    def test_list_response_format_handling(self):
        """
        **Objective:** Test handling of various response formats in list method.
        **Workflow:**
            1. Tests different malformed response scenarios
            2. Verifies appropriate error handling for each case
        """
        # Test malformed response
        self.mock_scm.get.return_value = {"malformed": "response"}  # noqa

        with pytest.raises(APIError):
            self.client.list(folder="Shared")

        # Test invalid data format
        self.mock_scm.get.return_value = {"data": "not-a-list"}  # noqa

        with pytest.raises(APIError):
            self.client.list(folder="Shared")

    def test_list_non_dict_response(self):
        """
        **Objective:** Test list method handling of non-dictionary response.
        **Workflow:**
            1. Mocks a non-dictionary response from the API
            2. Verifies that APIError is raised with correct message
            3. Tests different non-dict response types
        """
        # Test with list response
        self.mock_scm.get.return_value = ["not", "a", "dict"]  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.list(folder="Shared")
        assert "Invalid response format: expected dictionary" in str(exc_info.value)

        # Test with string response
        self.mock_scm.get.return_value = "string response"  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.list(folder="Shared")
        assert "Invalid response format: expected dictionary" in str(exc_info.value)

        # Test with None response
        self.mock_scm.get.return_value = None  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.list(folder="Shared")
        assert "Invalid response format: expected dictionary" in str(exc_info.value)


# -------------------- End of Test Classes --------------------
