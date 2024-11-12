# tests/scm/config/security/test_wildfire_antivirus_profile.py

import pytest
from unittest.mock import MagicMock

from scm.config.security.wildfire_antivirus_profile import WildfireAntivirusProfile
from scm.exceptions import (
    ValidationError,
    ObjectNotPresentError,
    EmptyFieldError,
    ObjectAlreadyExistsError,
    MalformedRequestError,
    FolderNotFoundError,
    BadResponseError,
    ReferenceNotZeroError,
)
from scm.models.security.wildfire_antivirus_profiles import (
    WildfireAntivirusProfileCreateModel,
    WildfireAntivirusProfileResponseModel,
    RuleBase,
    Analysis,
    Direction,
)

from pydantic import ValidationError as PydanticValidationError


@pytest.mark.usefixtures("load_env")
class TestWildfireAntivirusProfileBase:
    """Base class for Wildfire Antivirus Profile tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm  # noqa
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = WildfireAntivirusProfile(self.mock_scm)  # noqa


# -------------------- Test Classes Grouped by Functionality --------------------


class TestWildfireAntivirusProfileModelValidation(TestWildfireAntivirusProfileBase):
    """Tests for object model validation."""

    def test_object_model_no_container_provided(self):
        """Test validation when no container is provided."""
        data = {
            "name": "InvalidProfile",
            "rules": [
                {
                    "name": "NewRule",
                    "analysis": "public-cloud",
                    "direction": "both",
                    "application": ["any"],
                    "file_type": ["any"],
                }
            ],
        }
        with pytest.raises(ValueError) as exc_info:
            WildfireAntivirusProfileCreateModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_object_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = {
            "name": "InvalidProfile",
            "folder": "Shared",
            "device": "Device1",
            "rules": [
                {
                    "name": "NewRule",
                    "analysis": "public-cloud",
                    "direction": "both",
                    "application": ["any"],
                    "file_type": ["any"],
                }
            ],
        }
        with pytest.raises(ValueError) as exc_info:
            WildfireAntivirusProfileCreateModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_invalid_action_rules(self):
        """Test validation when invalid action provided in rules."""
        with pytest.raises(ValueError) as exc_info:
            WildfireAntivirusProfileCreateModel(
                name="InvalidProfile",
                folder="Shared",
                rules=[
                    {
                        "name": "NewRule",
                        "analysis": "invalid-cloud",
                        "direction": "both",
                        "application": ["any"],
                        "file_type": ["any"],
                    }
                ],
            )
        assert "Input should be 'public-cloud' or 'private-cloud'" in str(
            exc_info.value
        )


class TestWildfireAntivirusProfileList(TestWildfireAntivirusProfileBase):
    """Tests for listing Wildfire Antivirus Profile objects."""

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
                    "id": "dd0f80ce-9345-4cf1-9979-bce99da27888",
                    "name": "web-security-default",
                    "folder": "All",
                    "snippet": "Web-Security-Default",
                    "rules": [
                        {
                            "name": "default-fawkes",
                            "direction": "both",
                            "file_type": ["any"],
                            "application": ["any"],
                        }
                    ],
                },
                {
                    "id": "e2a5dfc4-d8c8-489a-9661-092032796e09",
                    "name": "best-practice",
                    "folder": "All",
                    "snippet": "predefined-snippet",
                    "rules": [
                        {
                            "name": "default",
                            "application": ["any"],
                            "file_type": ["any"],
                            "direction": "both",
                            "analysis": "public-cloud",
                        }
                    ],
                    "description": "Best practice profile",
                },
            ]
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        existing_objects = self.client.list(folder="All")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/security/v1/wildfire-anti-virus-profiles",
            params={
                "limit": 10000,
                "folder": "All",
            },
        )
        assert isinstance(existing_objects, list)
        assert isinstance(existing_objects[0], WildfireAntivirusProfileResponseModel)
        assert len(existing_objects) == 2
        assert existing_objects[0].name == "web-security-default"
        assert existing_objects[0].rules[0].direction == Direction.both

    def test_object_list_multiple_containers(self):
        """Test validation error when listing with multiple containers."""
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Prisma Access", snippet="TestSnippet")

        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )


class TestWildfireAntivirusProfileCreate(TestWildfireAntivirusProfileBase):
    """Tests for creating Wildfire Antivirus Profile objects."""

    def test_create_object(self):
        """
        **Objective:** Test creating a new object.
        **Workflow:**
            1. Creates test data.
            2. Mocks the API response.
            3. Verifies the creation request and response.
        """
        test_profile_data = {
            "name": "NewWFProfile",
            "folder": "All",
            "description": "A new test profile",
            "packet_capture": True,
            "rules": [
                {
                    "name": "NewRule",
                    "analysis": "public-cloud",
                    "direction": "both",
                    "application": ["any"],
                    "file_type": ["any"],
                }
            ],
            "mlav_exception": [
                {
                    "name": "Exception1",
                    "description": "An exception",
                    "filename": "malicious.exe",
                }
            ],
            "threat_exception": [
                {
                    "name": "ThreatException1",
                    "notes": "Some notes",
                }
            ],
        }

        mock_response = test_profile_data.copy()
        mock_response["id"] = "12345678-abcd-abcd-abcd-123456789012"

        self.mock_scm.post.return_value = mock_response  # noqa
        created_profile = self.client.create(test_profile_data)

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/security/v1/wildfire-anti-virus-profiles",
            json=test_profile_data,
        )
        assert isinstance(created_profile, WildfireAntivirusProfileResponseModel)
        assert str(created_profile.id) == "12345678-abcd-abcd-abcd-123456789012"
        assert created_profile.name == "NewWFProfile"
        assert created_profile.rules[0].analysis == Analysis.public_cloud

    def test_create_object_error_handling(self):
        """
        **Objective:** Test error handling during object creation.
        **Workflow:**
            1. Mocks an error response from the API
            2. Attempts to create an object
            3. Verifies proper error handling and exception raising
        """
        test_data = {
            "name": "NewWFProfile",
            "folder": "All",
            "rules": [
                {
                    "name": "NewRule",
                    "analysis": "public-cloud",
                    "direction": "both",
                    "application": ["any"],
                    "file_type": ["any"],
                }
            ],
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

        with pytest.raises(ObjectAlreadyExistsError):
            self.client.create(test_data)

    def test_create_generic_exception_handling(self):
        """
        **Objective:** Test generic exception handling in create method.
        **Workflow:**
            1. Mocks a generic exception without response attribute
            2. Verifies the original exception is re-raised
        """
        test_data = {
            "name": "NewWFProfile",
            "folder": "All",
            "rules": [
                {
                    "name": "NewRule",
                    "analysis": "public-cloud",
                    "direction": "both",
                    "application": ["any"],
                    "file_type": ["any"],
                }
            ],
        }

        # Mock a generic exception without response
        self.mock_scm.post.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.create(test_data)
        assert str(exc_info.value) == "Generic error"

    def test_create_malformed_response_handling(self):
        """
        **Objective:** Test handling of malformed response in create method.
        **Workflow:**
            1. Mocks a response that would cause a parsing error
            2. Verifies appropriate error handling
        """
        test_data = {
            "name": "NewWFProfile",
            "folder": "All",
            "rules": [
                {
                    "name": "NewRule",
                    "analysis": "public-cloud",
                    "direction": "both",
                    "application": ["any"],
                    "file_type": ["any"],
                }
            ],
        }

        # Mock invalid JSON response
        self.mock_scm.post.return_value = {"malformed": "response"}  # noqa

        with pytest.raises(PydanticValidationError):
            self.client.create(test_data)


class TestWildfireAntivirusProfileGet(TestWildfireAntivirusProfileBase):
    """Tests for retrieving a specific Wildfire Antivirus Profile object."""

    def test_get_object(self):
        """
        **Objective:** Test retrieving a specific object.
        **Workflow:**
            1. Mocks the API response for a specific object.
            2. Verifies the get request and response handling.
        """
        profile_id = "123e4567-e89b-12d3-a456-426655440000"
        mock_response = {
            "id": profile_id,
            "name": "TestProfile",
            "folder": "All",
            "description": "A test profile",
            "rules": [
                {
                    "name": "TestRule",
                    "direction": "download",
                    "application": ["app1", "app2"],
                    "file_type": ["pdf", "exe"],
                    "analysis": "private-cloud",
                }
            ],
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        get_object = self.client.get(profile_id)

        self.mock_scm.get.assert_called_once_with(  # noqa
            f"/config/security/v1/wildfire-anti-virus-profiles/{profile_id}"
        )
        assert isinstance(get_object, WildfireAntivirusProfileResponseModel)
        assert str(get_object.id) == profile_id
        assert get_object.rules[0].analysis == Analysis.private_cloud

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
            2. Verifies the original exception is re-raised
        """
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        # Mock a generic exception without response
        self.mock_scm.get.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.get(object_id)
        assert str(exc_info.value) == "Generic error"


class TestWildfireAntivirusProfileUpdate(TestWildfireAntivirusProfileBase):
    """Tests for updating Wildfire Antivirus Profile objects."""

    def test_update_object(self):
        """
        **Objective:** Test updating an object.
        **Workflow:**
            1. Prepares update data and mocks response
            2. Verifies the update request and response
            3. Ensures payload transformation is correct
        """
        from uuid import UUID

        test_uuid = UUID("123e4567-e89b-12d3-a456-426655440000")

        # Test data including ID
        update_data = {
            "id": str(test_uuid),
            "name": "UpdatedProfile",
            "folder": "All",
            "description": "An updated profile",
            "rules": [
                {
                    "name": "UpdatedRule",
                    "direction": Direction.upload,  # Use the enum directly
                    "application": ["app3"],
                    "file_type": ["docx"],
                }
            ],
            "packet_capture": False,
        }

        # Expected payload should not include the ID
        expected_payload = {
            "name": "UpdatedProfile",
            "folder": "All",
            "description": "An updated profile",
            "rules": [
                {
                    "name": "UpdatedRule",
                    "direction": "upload",  # Use string value for expected payload
                    "application": ["app3"],
                    "file_type": ["docx"],
                }
            ],
            "packet_capture": False,
        }

        # Mock response should include the ID
        mock_response = update_data.copy()
        self.mock_scm.put.return_value = mock_response  # noqa

        # Perform update
        updated_object = self.client.update(update_data)

        # Verify correct endpoint and payload
        self.mock_scm.put.assert_called_once_with(  # noqa
            f"/config/security/v1/wildfire-anti-virus-profiles/{update_data['id']}",
            json=expected_payload,  # Should not include ID
        )

        # Verify response model
        assert isinstance(updated_object, WildfireAntivirusProfileResponseModel)
        assert isinstance(updated_object.id, UUID)  # Verify it's a UUID object
        assert updated_object.id == test_uuid  # Compare against UUID object
        assert (
            str(updated_object.id) == update_data["id"]
        )  # Compare string representations
        assert updated_object.name == "UpdatedProfile"
        assert updated_object.rules[0].direction == Direction.upload

    def test_update_object_error_handling(self):
        """
        **Objective:** Test error handling during object update.
        **Workflow:**
            1. Mocks an error response from the API
            2. Attempts to update an object
            3. Verifies proper error handling and exception raising
        """
        update_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-profile",
            "folder": "Shared",
            "rules": [
                {
                    "name": "TestRule",
                    "direction": "both",
                    "application": ["any"],
                    "file_type": ["any"],
                }
            ],
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

        with pytest.raises(MalformedRequestError):
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

        with pytest.raises(PydanticValidationError):
            self.client.update(invalid_data)

    def test_update_generic_exception_handling(self):
        """
        **Objective:** Test generic exception handling in update method.
        **Workflow:**
            1. Mocks a generic exception without response attribute
            2. Verifies the original exception is re-raised
        """
        update_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-profile",
            "folder": "Shared",
            "rules": [
                {
                    "name": "TestRule",
                    "direction": "both",
                    "application": ["any"],
                    "file_type": ["any"],
                }
            ],
        }

        # Mock a generic exception without response
        self.mock_scm.put.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.update(update_data)
        assert str(exc_info.value) == "Generic error"


class TestWildfireAntivirusProfileDelete(TestWildfireAntivirusProfileBase):
    """Tests for deleting Wildfire Antivirus Profile objects."""

    def test_delete_referenced_object(self):
        """
        **Objective:** Test deleting an object that is referenced by other objects.
        **Workflow:**
            1. Sets up a mock error response for a referenced object deletion attempt
            2. Attempts to delete an object that is referenced by other objects
            3. Validates that ReferenceNotZeroError is raised with correct details
            4. Verifies the error contains proper reference information
        """
        object_id = "3fecfe58-af0c-472b-85cf-437bb6df2929"

        # Mock the API error response
        mock_error_response = {
            "_errors": [
                {
                    "code": "API_I00013",
                    "message": "Your configuration is not valid. Please review the error message for more details.",
                    "details": {
                        "errorType": "Reference Not Zero",
                        "message": [
                            " container -> Texas -> security-profile-group -> custom-group -> wildfire-antivirus"
                        ],
                        "errors": [
                            {
                                "type": "NON_ZERO_REFS",
                                "message": "Node cannot be deleted because of references from",
                                "params": ["custom-profile"],
                                "extra": [
                                    "container/[Texas]/security-profile-group/[custom-group]/wildfire-antivirus/[custom-profile]"
                                ],
                            }
                        ],
                    },
                }
            ],
            "_request_id": "8fe3b025-feb7-41d9-bf88-3938c0b33116",
        }

        # Configure mock to raise HTTPError with our custom error response
        self.mock_scm.delete.side_effect = Exception()  # noqa
        self.mock_scm.delete.side_effect.response = MagicMock()  # noqa
        self.mock_scm.delete.side_effect.response.json = MagicMock(  # noqa
            return_value=mock_error_response
        )

        # Attempt to delete the object and expect ReferenceNotZeroError
        with pytest.raises(ReferenceNotZeroError) as exc_info:
            self.client.delete(object_id)

        error = exc_info.value

        # Verify the error contains the expected information
        assert error.error_code == "API_I00013"
        assert "custom-profile" in error.references
        assert any("Texas" in path for path in error.reference_paths)
        assert "Cannot delete object due to existing references" in str(error)

        # Verify the delete method was called with correct endpoint
        self.mock_scm.delete.assert_called_once_with(  # noqa
            f"/config/security/v1/wildfire-anti-virus-profiles/{object_id}"
        )

        # Verify detailed error message includes reference path
        assert "custom-group" in error.detailed_message
        assert "container/[Texas]" in error.detailed_message

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
            2. Verifies the original exception is re-raised
        """
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        # Mock a generic exception without response
        self.mock_scm.delete.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.delete(object_id)
        assert str(exc_info.value) == "Generic error"


class TestWildfireAntivirusProfileFetch(TestWildfireAntivirusProfileBase):
    """Tests for fetching Wildfire Antivirus Profile objects by name."""

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
            "folder": "All",
            "description": "Test profile",
            "rules": [
                {
                    "name": "TestRule",
                    "direction": "both",
                    "application": ["any"],
                    "file_type": ["any"],
                }
            ],
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        # Call the fetch method
        fetched_object = self.client.fetch(
            name=mock_response["name"],
            folder=mock_response["folder"],
        )

        # Assert that the GET request was made with the correct parameters
        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/security/v1/wildfire-anti-virus-profiles",
            params={
                "folder": mock_response["folder"],
                "name": mock_response["name"],
            },
        )

        # Validate the returned object
        assert isinstance(fetched_object, dict)
        assert str(fetched_object["id"]) == mock_response["id"]
        assert fetched_object["name"] == mock_response["name"]
        assert fetched_object["description"] == mock_response["description"]
        assert fetched_object["rules"][0]["direction"] == "both"

    def test_fetch_object_not_found(self):
        """
        Test fetching an object by name that does not exist.

        **Objective:** Test that fetching a non-existent object raises NotFoundError.
        **Workflow:**
            1. Mocks the API response to return an empty 'data' list.
            2. Calls the `fetch` method with a name that does not exist.
            3. Asserts that NotFoundError is raised.
        """
        object_name = "NonExistent"
        folder_name = "Shared"
        mock_response = {
            "_errors": [
                {
                    "code": "API_I00013",
                    "message": "Your configuration is not valid. Please review the error message for more details.",
                    "details": {"errorType": "Object Not Present"},
                }
            ],
            "_request_id": "12282b0f-eace-41c3-a8e2-4b28992979c4",
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        # Call the fetch method and expect a NotFoundError
        with pytest.raises(ObjectNotPresentError) as exc_info:  # noqa
            self.client.fetch(
                name=object_name,
                folder=folder_name,
            )

    def test_fetch_empty_name(self):
        """
        **Objective:** Test fetch with empty name parameter.
        **Workflow:**
            1. Attempts to fetch with empty name
            2. Verifies ValidationError is raised
        """
        with pytest.raises(ValidationError) as exc_info:
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
        with pytest.raises(EmptyFieldError) as exc_info:
            self.client.fetch(name="test", folder="")
        assert "Field 'folder' cannot be empty" in str(exc_info.value)

        # Test no container provided
        with pytest.raises(ValidationError) as exc_info:
            self.client.fetch(name="test-profile")
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

        # Test multiple containers provided
        with pytest.raises(ValidationError) as exc_info:
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

        **Objective:** Ensure that the fetch method raises BadResponseError when the response format is not as expected.
        **Workflow:**
            1. Mocks the API response to return an unexpected format.
            2. Calls the `fetch` method.
            3. Asserts that BadResponseError is raised.
        """
        group_name = "TestGroup"
        folder_name = "Shared"
        # Mocking an unexpected response format
        mock_response = {"unexpected_key": "unexpected_value"}
        self.mock_scm.get.return_value = mock_response  # noqa

        with pytest.raises(BadResponseError) as exc_info:
            self.client.fetch(name=group_name, folder=folder_name)
        assert str(exc_info.value) == "Invalid response format: missing 'id' field"

    def test_fetch_validation_errors(self):
        """
        **Objective:** Test fetch validation errors.
        **Workflow:**
            1. Tests various invalid input scenarios
            2. Verifies appropriate error handling
        """
        # Test empty folder
        with pytest.raises(EmptyFieldError) as exc_info:
            self.client.fetch(name="test", folder="")
        assert "Field 'folder' cannot be empty" in str(exc_info.value)

        # Test multiple containers
        with pytest.raises(ValidationError) as exc_info:
            self.client.fetch(name="test", folder="folder1", snippet="snippet1")
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided"
            in str(exc_info.value)
        )

    def test_fetch_generic_exception_handling(self):
        """
        **Objective:** Test generic exception handling in fetch method.
        **Workflow:**
            1. Mocks a generic exception without response attribute
            2. Verifies the original exception is re-raised
        """
        # Mock a generic exception without response
        self.mock_scm.get.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.fetch(name="test", folder="Shared")
        assert str(exc_info.value) == "Generic error"

    def test_fetch_response_format_handling(self):
        """
        **Objective:** Test handling of various response formats in fetch method.
        **Workflow:**
            1. Tests different malformed response scenarios
            2. Verifies appropriate error handling for each case
        """
        # Test malformed response without expected fields
        self.mock_scm.get.return_value = {"unexpected": "format"}  # noqa

        with pytest.raises(BadResponseError) as exc_info:
            self.client.fetch(name="test", folder="Shared")
        assert "Invalid response format: missing 'id' field" in str(exc_info.value)

        # Test response with both id and data fields (invalid format)
        self.mock_scm.get.return_value = {  # noqa
            "id": "some-id",
            "data": [{"some": "data"}],
        }  # noqa

        with pytest.raises(PydanticValidationError) as exc_info:
            self.client.fetch(name="test", folder="Shared")
        assert "3 validation errors for WildfireAntivirusProfileResponseModel" in str(
            exc_info.value
        )
        assert "name\n  Field required" in str(exc_info.value)

        # Test malformed response in list format
        self.mock_scm.get.return_value = [{"unexpected": "format"}]  # noqa
        with pytest.raises(BadResponseError) as exc_info:
            self.client.fetch(name="test", folder="Shared")
        assert "Invalid response format: expected dictionary" in str(exc_info.value)

    def test_fetch_error_handler_json_error(self):
        """
        **Objective:** Test fetch method error handling when json() raises an error.
        **Workflow:**
            1. Mocks an exception with a response that raises error on json()
            2. Verifies the original exception is re-raised
        """

        class MockResponse:
            @property
            def response(self):
                return self

            def json(self):
                raise ValueError("Original error")

        # Create mock exception with our special response
        mock_exception = Exception("Original error")
        mock_exception.response = MockResponse()

        # Configure mock to raise our custom exception
        self.mock_scm.get.side_effect = mock_exception  # noqa

        # The original exception should be raised since json() failed
        with pytest.raises(Exception) as exc_info:
            self.client.fetch(name="test", folder="Shared")
        assert "Original error" in str(exc_info.value)


class TestWildfireAntivirusProfileListFilters(TestWildfireAntivirusProfileBase):
    """Tests for filtering during listing Wildfire Antivirus Profile objects."""

    def test_list_with_filters(self):
        """
        **Objective:** Test that filters are properly added to parameters.
        **Workflow:**
            1. Calls list with various filters
            2. Verifies filters are properly formatted in the request
        """
        filters = {
            "rules": ["rule1", "rule2"],
            "analysis": ["public-cloud", "private-cloud"],
        }

        mock_response = {"data": []}
        self.mock_scm.get.return_value = mock_response  # noqa

        self.client.list(folder="Shared", **filters)

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/security/v1/wildfire-anti-virus-profiles",
            params={
                "limit": 10000,
                "folder": "Shared",
            },
        )

    def test_list_empty_folder_error(self):
        """
        **Objective:** Test that empty folder raises appropriate error.
        **Workflow:**
            1. Attempts to list objects with empty folder
            2. Verifies EmptyFieldError is raised
        """
        with pytest.raises(EmptyFieldError) as exc_info:
            self.client.list(folder="")
        assert str(exc_info.value) == "Field 'folder' cannot be empty"

    def test_list_multiple_containers_error(self):
        """
        **Objective:** Test validation of container parameters.
        **Workflow:**
            1. Attempts to list with multiple containers
            2. Verifies ValidationError is raised
        """
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="folder1", snippet="snippet1")
        assert (
            str(exc_info.value)
            == "Exactly one of 'folder', 'snippet', or 'device' must be provided."
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

        with pytest.raises(FolderNotFoundError):
            self.client.list(folder="NonexistentFolder")

    def test_list_generic_exception_handling(self):
        """
        **Objective:** Test generic exception handling in list method.
        **Workflow:**
            1. Mocks a generic exception without response attribute
            2. Verifies the original exception is re-raised
        """
        # Mock a generic exception without response
        self.mock_scm.get.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.list(folder="Shared")
        assert str(exc_info.value) == "Generic error"

    def test_list_response_format_handling(self):
        """
        **Objective:** Test handling of various response formats in list method.
        **Workflow:**
            1. Tests different malformed response scenarios
            2. Verifies appropriate error handling for each case
        """
        # Test malformed response
        self.mock_scm.get.return_value = {"malformed": "response"}  # noqa

        with pytest.raises(BadResponseError):
            self.client.list(folder="Shared")

        # Test invalid data format
        self.mock_scm.get.return_value = {"data": "not-a-list"}  # noqa

        with pytest.raises(BadResponseError):
            self.client.list(folder="Shared")

    def test_list_non_dict_response(self):
        """
        **Objective:** Test list method handling of non-dictionary response.
        **Workflow:**
            1. Mocks a non-dictionary response from the API
            2. Verifies that BadResponseError is raised with correct message
            3. Tests different non-dict response types
        """
        # Test with list response
        self.mock_scm.get.return_value = ["not", "a", "dict"]  # noqa

        with pytest.raises(BadResponseError) as exc_info:
            self.client.list(folder="Shared")
        assert "Invalid response format: expected dictionary" in str(exc_info.value)

        # Test with string response
        self.mock_scm.get.return_value = "string response"  # noqa

        with pytest.raises(BadResponseError) as exc_info:
            self.client.list(folder="Shared")
        assert "Invalid response format: expected dictionary" in str(exc_info.value)

        # Test with None response
        self.mock_scm.get.return_value = None  # noqa

        with pytest.raises(BadResponseError) as exc_info:
            self.client.list(folder="Shared")
        assert "Invalid response format: expected dictionary" in str(exc_info.value)

    def test_list_filters_type_validation(self):
        """
        **Objective:** Test validation of filter types in list method.
        **Workflow:**
            1. Tests various invalid filter type scenarios
            2. Verifies ValidationError is raised with correct message
            3. Tests valid filter types pass validation
        """
        mock_response = {
            "data": [
                {
                    "id": "dd0f80ce-9345-4cf1-9979-bce99da27888",
                    "name": "web-security-default",
                    "folder": "All",
                    "rules": [
                        {
                            "name": "default-fawkes",
                            "direction": "both",
                            "file_type": ["any"],
                            "application": ["any"],
                        }
                    ],
                }
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test invalid rules filter (string instead of list)
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Shared", rules="rule1")
        assert str(exc_info.value) == "'rules' filter must be a list"

        # Test invalid rules filter (dict instead of list)
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Shared", rules={"rule": "rule1"})
        assert str(exc_info.value) == "'rules' filter must be a list"

        # Test invalid rules filter (integer instead of list)
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Shared", rules=123)
        assert str(exc_info.value) == "'rules' filter must be a list"

        # Test that valid list filters pass validation
        try:
            self.client.list(
                folder="Shared",
                rules=["rule1"],
            )
        except ValidationError:
            pytest.fail("Unexpected ValidationError raised with valid list filters")


# -------------------- End of Test Classes --------------------
