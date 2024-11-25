# tests/scm/config/security/test_wildfire_antivirus_profile.py

import logging
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError as PydanticValidationError

from scm.config.security.wildfire_antivirus_profile import WildfireAntivirusProfile
from scm.exceptions import (
    APIError,
    InvalidObjectError,
    ObjectNotPresentError,
    MalformedCommandError,
    MissingQueryParameterError,
    ReferenceNotZeroError,
)
from scm.models.security.wildfire_antivirus_profiles import (
    WildfireAvProfileCreateModel,
    WildfireAvProfileResponseModel,
    WildfireAvAnalysis,
    WildfireAvDirection,
)
from scm.utils.logging import setup_logger

logger = setup_logger(__name__, logging.DEBUG)


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
        logger.debug("TestWildfireAntivirusProfileBase setup completed")


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
        with pytest.raises(PydanticValidationError) as exc_info:
            WildfireAvProfileCreateModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )
        logger.debug("Validation failed as expected for missing container")

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
        with pytest.raises(PydanticValidationError) as exc_info:
            WildfireAvProfileCreateModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )
        logger.debug("Validation failed as expected for multiple containers")

    def test_invalid_action_rules(self):
        """Test validation when invalid action provided in rules."""
        with pytest.raises(PydanticValidationError) as exc_info:
            WildfireAvProfileCreateModel(
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
        logger.debug("Validation failed as expected for invalid action rules")


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
        assert isinstance(existing_objects[0], WildfireAvProfileResponseModel)
        assert len(existing_objects) == 2
        assert existing_objects[0].name == "web-security-default"
        assert existing_objects[0].rules[0].direction == WildfireAvDirection.both
        logger.info(f"Successfully listed {len(existing_objects)} objects")

    def test_object_list_multiple_containers(self):
        """Test validation error when listing with multiple containers."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Prisma Access", snippet="TestSnippet")

        assert "HTTP error: 400 - API error: E003" in str(exc_info.value)
        logger.debug("List validation failed as expected for multiple containers")


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
        assert isinstance(created_profile, WildfireAvProfileResponseModel)
        assert str(created_profile.id) == "12345678-abcd-abcd-abcd-123456789012"
        assert created_profile.name == "NewWFProfile"
        assert created_profile.rules[0].analysis == WildfireAvAnalysis.public_cloud
        logger.info(f"Successfully created profile {created_profile.name}")

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

        with pytest.raises(APIError) as exc_info:
            self.client.create(test_data)
        logger.error(f"Creation failed: {str(exc_info.value)}")

    def test_create_generic_exception_handling(self):
        """
        **Objective:** Test generic exception handling in create method.
        **Workflow:**
            1. Mocks a generic exception without response attribute
            2. Verifies APIError is raised with correct message
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

        with pytest.raises(APIError) as exc_info:
            self.client.create(test_data)
        assert str(exc_info.value) == "An unexpected error occurred"
        logger.error(f"Creation failed with generic error: {str(exc_info.value)}")

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

        with pytest.raises(APIError) as exc_info:
            self.client.create(test_data)
        assert "An unexpected error occurred" in str(exc_info.value)
        logger.error(f"Creation failed with malformed response: {str(exc_info.value)}")


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
        assert isinstance(get_object, WildfireAvProfileResponseModel)
        assert str(get_object.id) == profile_id
        assert get_object.rules[0].analysis == WildfireAvAnalysis.private_cloud
        logger.info(f"Successfully retrieved profile {get_object.name}")

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
                    "code": "E005",
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

        with pytest.raises(ObjectNotPresentError) as exc_info:
            self.client.get(object_id)
        logger.error(f"Get operation failed: {str(exc_info.value)}")

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
        logger.error(f"Get operation failed with generic error: {str(exc_info.value)}")


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
                    "direction": WildfireAvDirection.upload,
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
                    "direction": "upload",
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
            json=expected_payload,
        )

        assert isinstance(updated_object, WildfireAvProfileResponseModel)
        assert isinstance(updated_object.id, UUID)
        assert updated_object.id == test_uuid
        assert str(updated_object.id) == update_data["id"]
        assert updated_object.name == "UpdatedProfile"
        assert updated_object.rules[0].direction == WildfireAvDirection.upload
        logger.info(f"Successfully updated profile {updated_object.name}")

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
                    "code": "E003",
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

        with pytest.raises(MalformedCommandError) as exc_info:
            self.client.update(update_data)
        logger.error(f"Update failed: {str(exc_info.value)}")

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

        with pytest.raises(APIError) as exc_info:
            self.client.update(invalid_data)
        logger.error(f"Update validation failed: {str(exc_info.value)}")

    def test_update_generic_exception_handling(self):
        """
        **Objective:** Test generic exception handling in update method.
        **Workflow:**
            1. Mocks a generic exception without response attribute
            2. Verifies APIError is raised with correct message
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

        with pytest.raises(APIError) as exc_info:
            self.client.update(update_data)
        assert str(exc_info.value) == "An unexpected error occurred: Generic error"
        logger.error(f"Update failed with generic error: {str(exc_info.value)}")


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
                    "code": "E009",
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

        # Configure mock with status code
        mock_exc = Exception()
        mock_exc.response = MagicMock()
        mock_exc.response.status_code = 409
        mock_exc.response.json.return_value = mock_error_response
        self.mock_scm.delete.side_effect = mock_exc

        with pytest.raises(ReferenceNotZeroError) as exc_info:
            self.client.delete(object_id)

        error = exc_info.value
        logger.error(f"Delete failed due to references: {str(error)}")

        # Verify the delete method was called with correct endpoint
        self.mock_scm.delete.assert_called_once_with(  # noqa
            f"/config/security/v1/wildfire-anti-virus-profiles/{object_id}"
        )

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
                    "code": "E005",
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

        with pytest.raises(ObjectNotPresentError) as exc_info:
            self.client.delete(object_id)
        logger.error(f"Delete failed: {str(exc_info.value)}")

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
        logger.error(f"Delete failed with generic error: {str(exc_info.value)}")


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
        logger.info(f"Successfully fetched profile {fetched_object['name']}")

    def test_fetch_object_not_found(self):
        """
        Test fetching an object by name that does not exist.

        **Objective:** Test that fetching a non-existent object raises ObjectNotPresentError.
        **Workflow:**
            1. Mocks the API response to indicate object not found
            2. Calls the `fetch` method with a name that does not exist
            3. Asserts that ObjectNotPresentError is raised
        """
        object_name = "NonExistent"
        folder_name = "Shared"
        mock_response = {
            "_errors": [
                {
                    "code": "E005",
                    "message": "Object not found",
                    "details": {"errorType": "Object Not Present"},
                }
            ],
            "_request_id": "12282b0f-eace-41c3-a8e2-4b28992979c4",
        }

        # Configure mock with status code
        mock_exc = Exception()
        mock_exc.response = MagicMock()
        mock_exc.response.status_code = 404
        mock_exc.response.json.return_value = mock_response
        self.mock_scm.get.side_effect = mock_exc

        with pytest.raises(ObjectNotPresentError) as exc_info:
            self.client.fetch(name=object_name, folder=folder_name)
        logger.error(f"Fetch failed: {str(exc_info.value)}")

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
        logger.error("Fetch failed: Empty name parameter provided")

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
        logger.error("Fetch failed: Empty folder parameter provided")

        # Test no container provided
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-profile")
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )
        logger.error("Fetch failed: No container provided")

        # Test multiple containers provided
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(
                name="test-profile", folder="Shared", snippet="TestSnippet"
            )
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )
        logger.error("Fetch failed: Multiple containers provided")

    def test_fetch_object_unexpected_response_format(self):
        """
        **Objective:** Test fetching an object when the API returns an unexpected format.
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
        logger.error(
            f"Fetch failed with unexpected response format: {str(exc_info.value)}"
        )

    def test_fetch_error_handler_json_error(self):
        """
        **Objective:** Test fetch method error handling when json() raises an error.
        **Workflow:**
            1. Mocks an exception with a response that raises error on json()
            2. Verifies proper error handling
        """
        # Create a mock exception that will be raised by the API call
        mock_exc = Exception("Original error")
        mock_exc.response = MagicMock()
        mock_exc.response.status_code = 500
        # When json() is called on the response, it should raise ValueError
        mock_exc.response.json = MagicMock(side_effect=ValueError("JSON parsing error"))

        # Configure the mock to raise our exception
        self.mock_scm.get.side_effect = mock_exc

        # The fetch method should catch the ValueError and wrap it in an APIError
        with pytest.raises(APIError) as exc_info:
            self.client.fetch(name="test", folder="Shared")

        # Verify the error message
        assert "JSON parsing error" in str(exc_info.value)
        logger.error(f"Fetch failed with JSON parsing error: {str(exc_info.value)}")


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
        logger.debug("List operation with filters completed successfully")

    def test_list_empty_folder_error(self):
        """
        **Objective:** Test that empty folder raises appropriate error.
        **Workflow:**
            1. Attempts to list objects with empty folder
            2. Verifies MissingQueryParameterError is raised
        """
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.list(folder="")
        assert "Field 'folder' cannot be empty" in str(exc_info.value)
        logger.error("List operation failed: Empty folder parameter provided")

    def test_list_multiple_containers_error(self):
        """
        **Objective:** Test validation of container parameters.
        **Workflow:**
            1. Attempts to list with multiple containers
            2. Verifies InvalidObjectError is raised
        """
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="folder1", snippet="snippet1")
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )
        logger.error("List operation failed: Multiple containers provided")

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
        logger.error("List operation failed: Invalid response format (list)")

        # Test with string response
        self.mock_scm.get.return_value = "string response"  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.list(folder="Shared")
        assert "Invalid response format: expected dictionary" in str(exc_info.value)
        logger.error("List operation failed: Invalid response format (string)")

        # Test with None response
        self.mock_scm.get.return_value = None  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.list(folder="Shared")
        assert "Invalid response format: expected dictionary" in str(exc_info.value)
        logger.error("List operation failed: Invalid response format (None)")

    def test_list_filters_type_validation(self):
        """
        **Objective:** Test validation of filter types in list method.
        **Workflow:**
            1. Tests various invalid filter type scenarios
            2. Verifies InvalidObjectError is raised with correct message
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
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Shared", rules="rule1")
        assert "'rules' filter must be a list" in str(exc_info.value)
        logger.error("List operation failed: Invalid rules filter type (string)")

        # Test invalid rules filter (dict instead of list)
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Shared", rules={"rule": "rule1"})
        assert "'rules' filter must be a list" in str(exc_info.value)
        logger.error("List operation failed: Invalid rules filter type (dict)")

        # Test that valid list filters pass validation
        try:
            self.client.list(
                folder="Shared",
                rules=["rule1"],
            )
            logger.debug("List operation with valid filters completed successfully")
        except InvalidObjectError:
            pytest.fail("Unexpected InvalidObjectError raised with valid list filters")


# -------------------- End of Test Classes --------------------
