# tests/scm/config/security/test_anti_spyware_profile.py

import pytest
from unittest.mock import MagicMock

from scm.config.security.anti_spyware_profile import AntiSpywareProfile
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
from scm.models.security.anti_spyware_profiles import (
    AntiSpywareProfileCreateModel,
    AntiSpywareProfileResponseModel,
    Severity,
    Category,
    ActionRequest,
    ActionResponse,
    AntiSpywareProfileUpdateModel,
    PacketCapture,
)

from tests.factories import (
    AntiSpywareProfileRequestFactory,
    AntiSpywareRuleCreateFactory,
    ThreatExceptionCreateFactory,
)

from pydantic import ValidationError as PydanticValidationError


@pytest.mark.usefixtures("load_env")
class TestAntiSpywareProfileBase:
    """Base class for Anti-Spyware Profile tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm  # noqa
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = AntiSpywareProfile(self.mock_scm)  # noqa


# -------------------- Test Classes Grouped by Functionality --------------------


class TestAntiSpywareProfileModelValidation(TestAntiSpywareProfileBase):
    """Tests for object model validation."""

    def test_object_model_no_container_provided(self):
        """Test validation when no container is provided."""
        data = {
            "name": "InvalidProfile",
            "rules": [],
        }
        with pytest.raises(ValueError) as exc_info:
            AntiSpywareProfileCreateModel(**data)
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
            "rules": [],
        }
        with pytest.raises(ValueError) as exc_info:
            AntiSpywareProfileCreateModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_rule_request_model_validation(self):
        """Test validation in RuleRequest model."""
        # Invalid severity
        with pytest.raises(ValueError) as exc_info:
            AntiSpywareRuleCreateFactory(severity=["nonexistent_severity"])
        assert (
            "Input should be 'critical', 'high', 'medium', 'low', 'informational' or "
            in str(exc_info.value)
        )

    def test_threat_exception_request_model_validation(self):
        """Test validation in ThreatExceptionBase model."""
        # Invalid packet_capture
        with pytest.raises(ValueError) as exc_info:
            ThreatExceptionCreateFactory(packet_capture="invalid_option")
        assert "1 validation error for ThreatExceptionBase" in str(exc_info.value)


class TestAntiSpywareProfileList(TestAntiSpywareProfileBase):
    """Tests for listing Anti-Spyware Profile objects."""

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
                    "id": "123e4567-e89b-12d3-a456-426655440000",
                    "name": "TestProfile1",
                    "folder": "Prisma Access",
                    "description": "A test anti-spyware profile",
                    "rules": [
                        {
                            "name": "TestRule1",
                            "severity": ["critical", "high"],
                            "category": "spyware",
                            "threat_name": "any",
                            "packet_capture": "disable",
                            "action": {"alert": {}},
                        }
                    ],
                    "threat_exception": [
                        {
                            "name": "TestException1",
                            "action": {"allow": {}},
                            "packet_capture": "single-packet",
                            "exempt_ip": [{"name": "192.168.1.1"}],
                            "notes": "Test note",
                        }
                    ],
                },
                {
                    "id": "223e4567-e89b-12d3-a456-426655440001",
                    "name": "TestProfile2",
                    "folder": "Prisma Access",
                    "rules": [],
                    "threat_exception": [],
                },
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        existing_objects = self.client.list(folder="Prisma Access")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/security/v1/anti-spyware-profiles",
            params={
                "limit": 10000,
                "folder": "Prisma Access",
            },
        )
        assert isinstance(existing_objects, list)
        assert isinstance(existing_objects[0], AntiSpywareProfileResponseModel)
        assert len(existing_objects) == 2
        assert existing_objects[0].name == "TestProfile1"
        assert existing_objects[0].rules[0].severity == [
            Severity.critical,
            Severity.high,
        ]
        assert existing_objects[0].rules[0].category == Category.spyware
        assert existing_objects[0].threat_exception[0].name == "TestException1"
        assert (
            existing_objects[0].threat_exception[0].exempt_ip[0].name == "192.168.1.1"
        )

    def test_object_list_multiple_containers(self):
        """Test validation error when listing with multiple containers."""
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Prisma Access", snippet="TestSnippet")

        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )


class TestAntiSpywareProfileCreate(TestAntiSpywareProfileBase):
    """Tests for creating Anti-Spyware Profile objects."""

    def test_create_object(self):
        """
        **Objective:** Test creating a new object.
        **Workflow:**
            1. Creates test data using AntiSpywareProfileRequestFactory.
            2. Mocks the API response.
            3. Verifies the creation request and response.
        """
        test_object = AntiSpywareProfileRequestFactory()
        mock_response = test_object.model_dump()
        mock_response["id"] = "12345678-abcd-abcd-abcd-123456789012"

        self.mock_scm.post.return_value = mock_response  # noqa
        created_object = self.client.create(test_object.model_dump(exclude_unset=True))

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/security/v1/anti-spyware-profiles",
            json=test_object.model_dump(exclude_unset=True),
        )
        assert str(created_object.id) == "12345678-abcd-abcd-abcd-123456789012"
        assert created_object.name == test_object.name
        assert created_object.threat_exception[0].name.startswith("exception_")

    def test_create_object_error_handling(self):
        """
        **Objective:** Test error handling during object creation.
        **Workflow:**
            1. Mocks an error response from the API
            2. Attempts to create an object
            3. Verifies proper error handling and exception raising
        """
        test_data = AntiSpywareProfileRequestFactory()

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
            self.client.create(test_data.model_dump())

    def test_create_generic_exception_handling(self):
        """
        **Objective:** Test generic exception handling in create method.
        **Workflow:**
            1. Mocks a generic exception without response attribute
            2. Verifies the original exception is re-raised
        """
        test_data = AntiSpywareProfileRequestFactory()

        # Mock a generic exception without response
        self.mock_scm.post.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.create(test_data.model_dump())
        assert str(exc_info.value) == "Generic error"

    def test_create_malformed_response_handling(self):
        """
        **Objective:** Test handling of malformed response in create method.
        **Workflow:**
            1. Mocks a response that would cause a parsing error
            2. Verifies appropriate error handling
        """
        test_data = AntiSpywareProfileRequestFactory()

        # Mock invalid JSON response
        self.mock_scm.post.return_value = {"malformed": "response"}  # noqa

        with pytest.raises(PydanticValidationError):
            self.client.create(test_data.model_dump())


class TestAntiSpywareProfileGet(TestAntiSpywareProfileBase):
    """Tests for retrieving a specific Anti-Spyware Profile object."""

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
            "folder": "Prisma Access",
            "description": "A test anti-spyware profile",
            "rules": [],
            "threat_exception": [],
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        get_object = self.client.get(profile_id)

        self.mock_scm.get.assert_called_once_with(  # noqa
            f"/config/security/v1/anti-spyware-profiles/{profile_id}"
        )
        assert isinstance(get_object, AntiSpywareProfileResponseModel)
        assert get_object.name == "TestProfile"
        assert get_object.description == "A test anti-spyware profile"

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


class TestAntiSpywareProfileUpdate(TestAntiSpywareProfileBase):
    """Tests for updating Anti-Spyware Profile objects."""

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
            "folder": "Prisma Access",
            "description": "An updated anti-spyware profile",
            "rules": [
                {
                    "name": "UpdatedRule",
                    "severity": [Severity.high],
                    "category": Category.botnet,
                    "packet_capture": PacketCapture.extended_capture,
                    "threat_name": "any",
                }
            ],
            "threat_exception": [],
        }

        # Mock response should include the ID
        mock_response = update_data.copy()
        self.mock_scm.put.return_value = mock_response  # noqa

        # Perform update
        updated_object = self.client.update(update_data)

        # Verify response model
        assert isinstance(updated_object, AntiSpywareProfileResponseModel)
        assert isinstance(updated_object.id, UUID)  # Verify it's a UUID object
        assert updated_object.id == test_uuid  # Compare against UUID object
        assert (
            str(updated_object.id) == update_data["id"]
        )  # Compare string representations
        assert updated_object.name == "UpdatedProfile"
        assert updated_object.description == "An updated anti-spyware profile"
        assert updated_object.rules[0].severity == [Severity.high]
        assert updated_object.rules[0].category == Category.botnet
        assert updated_object.rules[0].packet_capture == PacketCapture.extended_capture

        # Verify the API call
        self.mock_scm.put.assert_called_once()  # Just verify it was called once
        call_args = self.mock_scm.put.call_args
        assert (
            call_args[0][0]
            == f"/config/security/v1/anti-spyware-profiles/{update_data['id']}"
        )

        # Verify the payload structure but not exact enum values
        payload = call_args[1]["json"]
        assert payload["name"] == "UpdatedProfile"
        assert payload["folder"] == "Prisma Access"
        assert payload["description"] == "An updated anti-spyware profile"
        assert len(payload["rules"]) == 1
        assert payload["rules"][0]["name"] == "UpdatedRule"
        assert len(payload["threat_exception"]) == 0

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
            "rules": [],
            "threat_exception": [],
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
            "rules": [],
            "threat_exception": [],
        }

        # Mock a generic exception without response
        self.mock_scm.put.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.update(update_data)
        assert str(exc_info.value) == "Generic error"


class TestAntiSpywareProfileDelete(TestAntiSpywareProfileBase):
    """Tests for deleting Anti-Spyware Profile objects."""

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
                            " container -> Texas -> security-profile-group -> custom-group -> anti-spyware"
                        ],
                        "errors": [
                            {
                                "type": "NON_ZERO_REFS",
                                "message": "Node cannot be deleted because of references from",
                                "params": ["custom-profile"],
                                "extra": [
                                    "container/[Texas]/security-profile-group/[custom-group]/anti-spyware/[custom-profile]"
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
            f"/config/security/v1/anti-spyware-profiles/{object_id}"
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


class TestAntiSpywareProfileFetch(TestAntiSpywareProfileBase):
    """Tests for fetching Anti-Spyware Profile objects by name."""

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
            "description": "Test Anti-Spyware Profile",
            "rules": [
                {
                    "name": "TestRule",
                    "severity": ["critical"],
                    "category": "spyware",
                    "action": {"alert": {}},
                }
            ],
            "threat_exception": None,  # Should be excluded in the result
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        # Call the fetch method
        fetched_object = self.client.fetch(
            name=mock_response["name"],
            folder=mock_response["folder"],
        )

        # Assert that the GET request was made with the correct parameters
        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/security/v1/anti-spyware-profiles",
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
        assert fetched_object["rules"][0]["severity"] == ["critical"]

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
        assert "3 validation errors for AntiSpywareProfileResponseModel" in str(
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


class TestAntiSpywareListFilters(TestAntiSpywareProfileBase):
    """Tests for filtering during listing objects."""

    def test_list_with_filters(self):
        """
        **Objective:** Test that filters are properly added to parameters.
        **Workflow:**
            1. Calls list with various filters
            2. Verifies filters are properly formatted in the request
        """
        filters = {
            "rules": ["rule1", "rule2"],
        }

        mock_response = {"data": []}
        self.mock_scm.get.return_value = mock_response  # noqa

        self.client.list(folder="Shared", **filters)

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/security/v1/anti-spyware-profiles",
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
            2. Verifies ValidationError is raised with correct message
            3. Tests valid filter types pass validation
        """
        mock_response = {
            "data": [
                {
                    "id": "2987ebe8-a3f2-48ae-83c4-29bfcbee3e46",
                    "name": "web-security-default",
                    "folder": "All",
                    "snippet": "Web-Security-Default",
                    "rules": [
                        {"name": "adware", "severity": ["medium"], "category": "any"},
                        {"name": "autogen", "severity": ["medium"], "category": "any"},
                        {"name": "backdoor", "severity": ["medium"], "category": "any"},
                        {"name": "botnet", "severity": ["medium"], "category": "any"},
                        {
                            "name": "browser-hijack",
                            "severity": ["medium"],
                            "category": "any",
                        },
                        {
                            "name": "command-and-control",
                            "severity": ["medium"],
                            "category": "any",
                        },
                        {
                            "name": "cryptominer",
                            "severity": ["medium"],
                            "category": "any",
                        },
                        {
                            "name": "data-theft",
                            "severity": ["medium"],
                            "category": "any",
                        },
                        {
                            "name": "downloader",
                            "severity": ["medium"],
                            "category": "any",
                        },
                        {"name": "fraud", "severity": ["medium"], "category": "any"},
                        {"name": "hacktool", "severity": ["medium"], "category": "any"},
                        {
                            "name": "keylogger",
                            "severity": ["medium"],
                            "category": "any",
                        },
                        {"name": "net-worm", "severity": ["medium"], "category": "any"},
                        {
                            "name": "p2p-communication",
                            "severity": ["medium"],
                            "category": "any",
                        },
                        {
                            "name": "phishing-kit",
                            "severity": ["medium"],
                            "category": "any",
                        },
                        {
                            "name": "post-exploitation",
                            "severity": ["medium"],
                            "category": "any",
                        },
                        {"name": "spyware", "severity": ["medium"], "category": "any"},
                        {
                            "name": "tls-fingerprint",
                            "severity": ["medium"],
                            "category": "any",
                        },
                        {"name": "webshell", "severity": ["medium"], "category": "any"},
                    ],
                    "mica_engine_spyware_enabled": [
                        {
                            "name": "HTTP Command and Control detector",
                            "inline_policy_action": "reset-both",
                        },
                        {
                            "name": "HTTP2 Command and Control detector",
                            "inline_policy_action": "reset-both",
                        },
                        {
                            "name": "SSL Command and Control detector",
                            "inline_policy_action": "reset-both",
                        },
                        {
                            "name": "Unknown-TCP Command and Control detector",
                            "inline_policy_action": "reset-both",
                        },
                        {
                            "name": "Unknown-UDP Command and Control detector",
                            "inline_policy_action": "reset-both",
                        },
                    ],
                    "cloud_inline_analysis": True,
                },
                {
                    "id": "951a17dd-6522-4ac7-81a1-a90fcb2f994c",
                    "name": "best-practice",
                    "folder": "All",
                    "snippet": "predefined-snippet",
                    "description": "Best practice anti-spyware security profile",
                    "cloud_inline_analysis": True,
                    "mica_engine_spyware_enabled": [
                        {
                            "name": "HTTP Command and Control detector",
                            "inline_policy_action": "reset-both",
                        },
                        {
                            "name": "HTTP2 Command and Control detector",
                            "inline_policy_action": "reset-both",
                        },
                        {
                            "name": "SSL Command and Control detector",
                            "inline_policy_action": "reset-both",
                        },
                        {
                            "name": "Unknown-TCP Command and Control detector",
                            "inline_policy_action": "reset-both",
                        },
                        {
                            "name": "Unknown-UDP Command and Control detector",
                            "inline_policy_action": "reset-both",
                        },
                    ],
                    "rules": [
                        {
                            "name": "simple-critical",
                            "action": {"reset_both": {}},
                            "severity": ["critical"],
                            "threat_name": "any",
                            "category": "any",
                            "packet_capture": "single-packet",
                        },
                        {
                            "name": "simple-high",
                            "action": {"reset_both": {}},
                            "severity": ["high"],
                            "threat_name": "any",
                            "category": "any",
                            "packet_capture": "single-packet",
                        },
                        {
                            "name": "simple-medium",
                            "action": {"reset_both": {}},
                            "severity": ["medium"],
                            "threat_name": "any",
                            "category": "any",
                            "packet_capture": "single-packet",
                        },
                        {
                            "name": "simple-informational",
                            "action": {},
                            "severity": ["informational"],
                            "threat_name": "any",
                            "category": "any",
                            "packet_capture": "disable",
                        },
                        {
                            "name": "simple-low",
                            "action": {},
                            "severity": ["low"],
                            "threat_name": "any",
                            "category": "any",
                            "packet_capture": "disable",
                        },
                    ],
                },
                {
                    "id": "41f0f7d3-be0d-411a-bdc7-bd93085911f8",
                    "name": "test123",
                    "folder": "Texas",
                    "description": "updated123",
                    "mica_engine_spyware_enabled": [
                        {
                            "name": "HTTP Command and Control detector",
                            "inline_policy_action": "alert",
                        },
                        {
                            "name": "HTTP2 Command and Control detector",
                            "inline_policy_action": "alert",
                        },
                        {
                            "name": "SSL Command and Control detector",
                            "inline_policy_action": "alert",
                        },
                        {
                            "name": "Unknown-TCP Command and Control detector",
                            "inline_policy_action": "alert",
                        },
                        {
                            "name": "Unknown-UDP Command and Control detector",
                            "inline_policy_action": "alert",
                        },
                    ],
                    "rules": [
                        {
                            "name": "asdfasdfasdf",
                            "severity": ["any"],
                            "category": "any",
                            "threat_name": "Autorun User-Agent Traffic",
                            "packet_capture": "single-packet",
                        }
                    ],
                },
            ],
            "offset": 0,
            "total": 3,
            "limit": 200,
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test invalid types filter (string instead of list)
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Shared", rules="rule1")
        assert str(exc_info.value) == "'rules' filter must be a list"

        # Test invalid types filter (dict instead of list)
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Shared", rules={"type": "rule1"})
        assert str(exc_info.value) == "'rules' filter must be a list"

        # Test that valid list filters pass validation
        try:
            self.client.list(
                folder="Shared",
                rules=["rule1"],
            )
        except ValidationError:
            pytest.fail("Unexpected ValidationError raised with valid list filters")

    # def test_list_filter_combinations(self):
    #     """
    #     **Objective:** Test different combinations of valid filters.
    #     **Workflow:**
    #         1. Tests various combinations of valid filters
    #         2. Verifies filters are properly applied
    #         3. Checks that filtered results match expected criteria
    #     """
    #     mock_response = {
    #         "data": [
    #             {
    #                 "id": "123e4567-e89b-12d3-a456-426655440000",
    #                 "name": "test-address1",
    #                 "folder": "Shared",
    #                 "ip_netmask": "10.0.0.0/24",
    #                 "tag": ["tag1", "tag2"],
    #             },
    #             {
    #                 "id": "223e4567-e89b-12d3-a456-426655440000",
    #                 "name": "test-address2",
    #                 "folder": "Shared",
    #                 "ip_range": "10.0.0.1-10.0.0.10",
    #                 "tag": ["tag2", "tag3"],
    #             },
    #             {
    #                 "id": "323e4567-e89b-12d3-a456-426655440000",
    #                 "name": "test-address3",
    #                 "folder": "Shared",
    #                 "fqdn": "test.example.com",
    #                 "tag": ["tag1", "tag3"],
    #             },
    #         ]
    #     }
    #     self.mock_scm.get.return_value = mock_response  # noqa
    #
    #     # Test combining types and tags filters
    #     filtered_objects = self.client.list(
    #         folder="Shared",
    #         types=["netmask"],
    #         tags=["tag1"],
    #     )
    #     assert len(filtered_objects) == 1
    #     assert filtered_objects[0].name == "test-address1"
    #
    #     # Test combining values and tags filters
    #     filtered_objects = self.client.list(
    #         folder="Shared",
    #         values=["10.0.0.0/24"],
    #         tags=["tag2"],
    #     )
    #     assert len(filtered_objects) == 1
    #     assert filtered_objects[0].name == "test-address1"
    #
    #     # Test all filters together
    #     filtered_objects = self.client.list(
    #         folder="Shared",
    #         types=["netmask"],
    #         values=["10.0.0.0/24"],
    #         tags=["tag1"],
    #     )
    #     assert len(filtered_objects) == 1
    #     assert filtered_objects[0].name == "test-address1"
    #
    def test_list_empty_filter_lists(self):
        """
        **Objective:** Test behavior with empty filter lists.
        **Workflow:**
            1. Tests filters with empty lists
            2. Verifies appropriate handling of empty filters
        """
        mock_response = {
            "data": [
                {
                    "id": "2987ebe8-a3f2-48ae-83c4-29bfcbee3e46",
                    "name": "web-security-default",
                    "folder": "All",
                    "snippet": "Web-Security-Default",
                    "rules": [
                        {"name": "adware", "severity": ["medium"], "category": "any"},
                        {"name": "autogen", "severity": ["medium"], "category": "any"},
                        {"name": "backdoor", "severity": ["medium"], "category": "any"},
                        {"name": "botnet", "severity": ["medium"], "category": "any"},
                        {
                            "name": "browser-hijack",
                            "severity": ["medium"],
                            "category": "any",
                        },
                        {
                            "name": "command-and-control",
                            "severity": ["medium"],
                            "category": "any",
                        },
                        {
                            "name": "cryptominer",
                            "severity": ["medium"],
                            "category": "any",
                        },
                        {
                            "name": "data-theft",
                            "severity": ["medium"],
                            "category": "any",
                        },
                        {
                            "name": "downloader",
                            "severity": ["medium"],
                            "category": "any",
                        },
                        {"name": "fraud", "severity": ["medium"], "category": "any"},
                        {"name": "hacktool", "severity": ["medium"], "category": "any"},
                        {
                            "name": "keylogger",
                            "severity": ["medium"],
                            "category": "any",
                        },
                        {"name": "net-worm", "severity": ["medium"], "category": "any"},
                        {
                            "name": "p2p-communication",
                            "severity": ["medium"],
                            "category": "any",
                        },
                        {
                            "name": "phishing-kit",
                            "severity": ["medium"],
                            "category": "any",
                        },
                        {
                            "name": "post-exploitation",
                            "severity": ["medium"],
                            "category": "any",
                        },
                        {"name": "spyware", "severity": ["medium"], "category": "any"},
                        {
                            "name": "tls-fingerprint",
                            "severity": ["medium"],
                            "category": "any",
                        },
                        {"name": "webshell", "severity": ["medium"], "category": "any"},
                    ],
                    "mica_engine_spyware_enabled": [
                        {
                            "name": "HTTP Command and Control detector",
                            "inline_policy_action": "reset-both",
                        },
                        {
                            "name": "HTTP2 Command and Control detector",
                            "inline_policy_action": "reset-both",
                        },
                        {
                            "name": "SSL Command and Control detector",
                            "inline_policy_action": "reset-both",
                        },
                        {
                            "name": "Unknown-TCP Command and Control detector",
                            "inline_policy_action": "reset-both",
                        },
                        {
                            "name": "Unknown-UDP Command and Control detector",
                            "inline_policy_action": "reset-both",
                        },
                    ],
                    "cloud_inline_analysis": True,
                },
                {
                    "id": "951a17dd-6522-4ac7-81a1-a90fcb2f994c",
                    "name": "best-practice",
                    "folder": "All",
                    "snippet": "predefined-snippet",
                    "description": "Best practice anti-spyware security profile",
                    "cloud_inline_analysis": True,
                    "mica_engine_spyware_enabled": [
                        {
                            "name": "HTTP Command and Control detector",
                            "inline_policy_action": "reset-both",
                        },
                        {
                            "name": "HTTP2 Command and Control detector",
                            "inline_policy_action": "reset-both",
                        },
                        {
                            "name": "SSL Command and Control detector",
                            "inline_policy_action": "reset-both",
                        },
                        {
                            "name": "Unknown-TCP Command and Control detector",
                            "inline_policy_action": "reset-both",
                        },
                        {
                            "name": "Unknown-UDP Command and Control detector",
                            "inline_policy_action": "reset-both",
                        },
                    ],
                    "rules": [
                        {
                            "name": "simple-critical",
                            "action": {"reset_both": {}},
                            "severity": ["critical"],
                            "threat_name": "any",
                            "category": "any",
                            "packet_capture": "single-packet",
                        },
                        {
                            "name": "simple-high",
                            "action": {"reset_both": {}},
                            "severity": ["high"],
                            "threat_name": "any",
                            "category": "any",
                            "packet_capture": "single-packet",
                        },
                        {
                            "name": "simple-medium",
                            "action": {"reset_both": {}},
                            "severity": ["medium"],
                            "threat_name": "any",
                            "category": "any",
                            "packet_capture": "single-packet",
                        },
                        {
                            "name": "simple-informational",
                            "action": {},
                            "severity": ["informational"],
                            "threat_name": "any",
                            "category": "any",
                            "packet_capture": "disable",
                        },
                        {
                            "name": "simple-low",
                            "action": {},
                            "severity": ["low"],
                            "threat_name": "any",
                            "category": "any",
                            "packet_capture": "disable",
                        },
                    ],
                },
                {
                    "id": "41f0f7d3-be0d-411a-bdc7-bd93085911f8",
                    "name": "test123",
                    "folder": "Texas",
                    "description": "updated123",
                    "mica_engine_spyware_enabled": [
                        {
                            "name": "HTTP Command and Control detector",
                            "inline_policy_action": "alert",
                        },
                        {
                            "name": "HTTP2 Command and Control detector",
                            "inline_policy_action": "alert",
                        },
                        {
                            "name": "SSL Command and Control detector",
                            "inline_policy_action": "alert",
                        },
                        {
                            "name": "Unknown-TCP Command and Control detector",
                            "inline_policy_action": "alert",
                        },
                        {
                            "name": "Unknown-UDP Command and Control detector",
                            "inline_policy_action": "alert",
                        },
                    ],
                    "rules": [
                        {
                            "name": "asdfasdfasdf",
                            "severity": ["any"],
                            "category": "any",
                            "threat_name": "Autorun User-Agent Traffic",
                            "packet_capture": "single-packet",
                        }
                    ],
                },
            ],
            "offset": 0,
            "total": 3,
            "limit": 200,
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Empty lists should result in no matches
        filtered_objects = self.client.list(
            folder="Shared",
            rules=[],
        )
        assert len(filtered_objects) == 0

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


class TestActionValidation(TestAntiSpywareProfileBase):
    """Tests for Action Request and Response validation."""

    def test_action_request_string_conversion(self):
        """Test string to dict conversion in ActionRequest."""
        action = ActionRequest.model_validate("alert")
        assert action.root == {"alert": {}}

    def test_action_request_invalid_type(self):
        """Test invalid type handling in ActionRequest."""
        with pytest.raises(ValueError) as exc_info:
            ActionRequest.model_validate(123)  # Neither string nor dict
        assert (
            str(exc_info.value)
            == "1 validation error for ActionRequest\n  Value error, Invalid action format; must be a string or dict. [type=value_error, input_value=123, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.9/v/value_error"
        )

    def test_action_request_no_action(self):
        """Test validation when no action is provided."""
        with pytest.raises(ValueError) as exc_info:
            ActionRequest.model_validate({})
        assert (
            str(exc_info.value)
            == "1 validation error for ActionRequest\n  Value error, Exactly one action must be provided in 'action' field. [type=value_error, input_value={}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.9/v/value_error"
        )

    def test_action_request_multiple_actions(self):
        """Test validation when multiple actions are provided."""
        with pytest.raises(ValueError) as exc_info:
            ActionRequest.model_validate({"alert": {}, "drop": {}})
        assert (
            str(exc_info.value)
            == "1 validation error for ActionRequest\n  Value error, Exactly one action must be provided in 'action' field. [type=value_error, input_value={'alert': {}, 'drop': {}}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.9/v/value_error"
        )

    def test_action_request_get_action_name(self):
        """Test get_action_name method for ActionRequest."""
        # Test with valid action
        action = ActionRequest.model_validate({"alert": {}})
        assert action.get_action_name() == "alert"

    def test_action_response_string_conversion(self):
        """Test string to dict conversion in ActionResponse."""
        action = ActionResponse.model_validate("alert")
        assert action.root == {"alert": {}}

    def test_action_response_invalid_type(self):
        """Test invalid type handling in ActionResponse."""
        with pytest.raises(ValueError) as exc_info:
            ActionResponse.model_validate(123)  # Neither string nor dict
        assert (
            str(exc_info.value)
            == "1 validation error for ActionResponse\n  Value error, Invalid action format; must be a string or dict. [type=value_error, input_value=123, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.9/v/value_error"
        )

    def test_action_response_empty_dict(self):
        """Test that ActionResponse accepts empty dict."""
        action = ActionResponse.model_validate({})
        assert action.root == {}

    def test_action_response_single_action(self):
        """Test ActionResponse with single valid action."""
        action = ActionResponse.model_validate({"alert": {}})
        assert action.root == {"alert": {}}

    def test_action_response_multiple_actions(self):
        """Test validation when multiple actions are provided."""
        with pytest.raises(ValueError) as exc_info:
            ActionResponse.model_validate({"alert": {}, "drop": {}})
        assert (
            str(exc_info.value)
            == "1 validation error for ActionResponse\n  Value error, At most one action must be provided in 'action' field. [type=value_error, input_value={'alert': {}, 'drop': {}}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.9/v/value_error"
        )

    def test_action_response_get_action_name(self):
        """Test get_action_name method for ActionResponse."""
        # Test with valid action
        action = ActionResponse.model_validate({"alert": {}})
        assert action.get_action_name() == "alert"

        # Test with empty dict (should return "unknown")
        action = ActionResponse.model_validate({})
        assert action.get_action_name() == "unknown"

    def test_action_request_valid_actions(self):
        """Test all valid action types in ActionRequest."""
        valid_actions = [
            "allow",
            "alert",
            "drop",
            "reset_client",
            "reset_server",
            "reset_both",
            "block_ip",
            "default",
        ]
        for action_type in valid_actions:
            action = ActionRequest.model_validate({action_type: {}})
            assert action.get_action_name() == action_type

    def test_action_response_valid_actions(self):
        """Test all valid action types in ActionResponse."""
        valid_actions = [
            "allow",
            "alert",
            "drop",
            "reset_client",
            "reset_server",
            "reset_both",
            "block_ip",
            "default",
        ]
        for action_type in valid_actions:
            action = ActionResponse.model_validate({action_type: {}})
            assert action.get_action_name() == action_type

    def test_block_ip_action_validation(self):
        """Test BlockIpAction validation."""
        # Test valid block_ip action
        valid_action = {"block_ip": {"track_by": "source", "duration": 3600}}
        action = ActionRequest.model_validate(valid_action)
        assert action.root == valid_action


# -------------------- End of Test Classes --------------------
