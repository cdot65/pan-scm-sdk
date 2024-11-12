# tests/scm/config/security/test_security_rules.py

import pytest
from unittest.mock import MagicMock

from scm.config.security import SecurityRule
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
from scm.models.security.security_rules import (
    SecurityRuleResponseModel,
    SecurityRuleCreateModel,
    SecurityRuleUpdateModel,
    ProfileSetting,
    Action,
    Rulebase,
    RuleMoveDestination,
    SecurityRuleMoveModel,
)

from tests.factories import (
    SecurityRuleRequestFactory,
    SecurityRuleResponseFactory,
)

from pydantic import ValidationError as PydanticValidationError


@pytest.mark.usefixtures("load_env")
class TestSecurityRuleBase:
    """Base class for Security Rule tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm  # noqa
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = SecurityRule(self.mock_scm)  # noqa


# -------------------- Test Classes Grouped by Functionality --------------------


class TestSecurityRuleModelValidation(TestSecurityRuleBase):
    """Tests for object model validation."""

    def test_object_model_no_container_provided(self):
        """Test validation when no container is provided."""
        data = {
            "name": "TestRule",
            "action": "allow",
            # No 'folder', 'snippet', or 'device' provided
        }
        with pytest.raises(ValueError) as exc_info:
            SecurityRuleCreateModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_object_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = {
            "name": "TestRule",
            "action": "allow",
            "folder": "Shared",
            "snippet": "TestSnippet",
            # Multiple containers provided
        }
        with pytest.raises(ValueError) as exc_info:
            SecurityRuleCreateModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_ensure_list_of_strings_single_string(self):
        """Test that a single string is converted to a list containing that string."""
        data = {
            "name": "TestRule",
            "action": "allow",
            "folder": "Shared",
            "from": "zone1",  # single string
            "to": "zone2",  # single string
        }
        model = SecurityRuleCreateModel(**data)
        assert model.from_ == ["zone1"]
        assert model.to_ == ["zone2"]

    def test_ensure_list_of_strings_invalid_type(self):
        """Test that a non-string, non-list input raises ValueError."""
        data = {
            "name": "TestRule",
            "action": "allow",
            "folder": "Shared",
            "from": 123,  # invalid type
        }
        with pytest.raises(ValueError) as exc_info:
            SecurityRuleCreateModel(**data)
        assert "Value must be a list of strings" in str(exc_info.value)

    def test_ensure_list_of_strings_non_string_items(self):
        """Test that a list containing non-string items raises ValueError."""
        data = {
            "name": "TestRule",
            "action": "allow",
            "folder": "Shared",
            "from": ["zone1", 123],  # list with non-string item
        }
        with pytest.raises(ValueError) as exc_info:
            SecurityRuleCreateModel(**data)
        assert "All items must be strings" in str(exc_info.value)

    def test_ensure_unique_items(self):
        """Test that duplicate items in lists raise ValueError."""
        data = {
            "name": "TestRule",
            "action": "allow",
            "folder": "Shared",
            "from": ["zone1", "zone1"],  # duplicate item
        }
        with pytest.raises(ValueError) as exc_info:
            SecurityRuleCreateModel(**data)
        assert "List items must be unique" in str(exc_info.value)


class TestSecurityRuleList(TestSecurityRuleBase):
    """Tests for listing Security Rule objects."""

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
                    "id": "721c065c-0966-4aab-84ae-d70f55e9c5a7",
                    "name": "default",
                    "folder": "All",
                    "log_setting": "Cortex Data Lake",
                    "log_end": True,
                },
                {
                    "id": "980a0e95-9c14-4383-bf19-dd8f03c41943",
                    "name": "Web-Security-Default",
                    "folder": "All",
                    "log_setting": "Cortex Data Lake",
                    "log_end": True,
                },
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        existing_objects = self.client.list(folder="All")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/security/v1/security-rules",
            params={
                "position": "pre",
                "limit": 10000,
                "folder": "All",
            },
        )
        assert isinstance(existing_objects, list)
        assert isinstance(existing_objects[0], SecurityRuleResponseModel)
        assert len(existing_objects) == 2
        assert existing_objects[0].name == "default"

    def test_object_list_multiple_containers(self):
        """Test validation error when listing with multiple containers."""
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Prisma Access", snippet="TestSnippet")

        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )


class TestSecurityRuleCreate(TestSecurityRuleBase):
    """Tests for creating Security Rule objects."""

    def test_create_object(self):
        """
        **Objective:** Test creating a new object.
        **Workflow:**
            1. Creates test data using SecurityRuleRequestFactory.
            2. Mocks the API response.
            3. Verifies the creation request and response.
        """
        test_rule = SecurityRuleRequestFactory()
        mock_response = test_rule.model_dump()
        mock_response["id"] = "12345678-abcd-abcd-abcd-123456789012"

        self.mock_scm.post.return_value = mock_response  # noqa
        created_rule = self.client.create(
            test_rule.model_dump(exclude_none=True, by_alias=True)
        )

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/security/v1/security-rules",
            params={"position": "pre"},
            json=test_rule.model_dump(exclude_none=True, by_alias=True),
        )
        assert isinstance(created_rule, SecurityRuleResponseModel)
        assert str(created_rule.id) == "12345678-abcd-abcd-abcd-123456789012"

    def test_create_object_error_handling(self):
        """
        **Objective:** Test error handling during object creation.
        **Workflow:**
            1. Mocks an error response from the API
            2. Attempts to create an object
            3. Verifies proper error handling and exception raising
        """
        test_data = SecurityRuleRequestFactory()

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
        test_data = SecurityRuleRequestFactory()

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
        test_data = SecurityRuleRequestFactory()

        # Mock invalid JSON response
        self.mock_scm.post.return_value = {"malformed": "response"}  # noqa

        with pytest.raises(PydanticValidationError):
            self.client.create(test_data.model_dump())


class TestSecurityRuleGet(TestSecurityRuleBase):
    """Tests for retrieving a specific Security Rule object."""

    def test_get_object(self):
        """
        **Objective:** Test retrieving a specific object.
        **Workflow:**
            1. Mocks the API response for a specific object.
            2. Verifies the get request and response handling.
        """
        mock_response = {
            "id": "b44a8c00-7555-4021-96f0-d59deecd54e8",
            "name": "TestRule",
            "folder": "Shared",
            "action": "allow",
            "from": ["any"],
            "to": ["any"],
            "source": ["any"],
            "destination": ["any"],
            "application": ["any"],
            "service": ["any"],
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        object_id = "b44a8c00-7555-4021-96f0-d59deecd54e8"
        get_object = self.client.get(object_id)

        self.mock_scm.get.assert_called_once_with(  # noqa
            f"/config/security/v1/security-rules/{object_id}",
            params={"position": "pre"},
        )
        assert isinstance(get_object, SecurityRuleResponseModel)
        assert get_object.name == "TestRule"
        assert get_object.action == "allow"

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


class TestSecurityRuleUpdate(TestSecurityRuleBase):
    """Tests for updating Security Rule objects."""

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
            "name": "UpdatedRule",
            "folder": "Shared",
            "action": "allow",
            "from": ["any"],
            "to": ["any"],
            "source": ["any"],
            "destination": ["any"],
            "application": ["any"],
            "service": ["any"],
        }

        # Expected payload should not include the ID
        expected_payload = update_data.copy()
        expected_payload.pop("id")

        # Mock response should include the ID
        mock_response = update_data.copy()
        self.mock_scm.put.return_value = mock_response  # noqa

        # Perform update
        updated_object = self.client.update(update_data)

        # Verify correct endpoint and payload
        self.mock_scm.put.assert_called_once_with(  # noqa
            f"/config/security/v1/security-rules/{update_data['id']}",
            params={"position": "pre"},
            json=expected_payload,  # Should not include ID
        )

        # Verify response model
        assert isinstance(updated_object, SecurityRuleResponseModel)
        assert isinstance(updated_object.id, UUID)  # Verify it's a UUID object
        assert updated_object.id == test_uuid  # Compare against UUID object
        assert (
            str(updated_object.id) == update_data["id"]
        )  # Compare string representations
        assert updated_object.name == "UpdatedRule"
        assert updated_object.action == "allow"

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
            "name": "test-rule",
            "folder": "Shared",
            "action": "allow",
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
            "name": "test-rule",
            "folder": "Shared",
            "action": "allow",
        }

        # Mock a generic exception without response
        self.mock_scm.put.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.update(update_data)
        assert str(exc_info.value) == "Generic error"


class TestSecurityRuleDelete(TestSecurityRuleBase):
    """Tests for deleting Security Rule objects."""

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
                            " container -> Texas -> security-rule-group -> custom-group -> rules"
                        ],
                        "errors": [
                            {
                                "type": "NON_ZERO_REFS",
                                "message": "Node cannot be deleted because of references from",
                                "params": ["custom-rule"],
                                "extra": [
                                    "container/[Texas]/security-rule-group/[custom-group]/rules/[custom-rule]"
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
        assert "custom-rule" in error.references
        assert any("Texas" in path for path in error.reference_paths)
        assert "Cannot delete object due to existing references" in str(error)

        # Verify the delete method was called with correct endpoint
        self.mock_scm.delete.assert_called_once_with(  # noqa
            f"/config/security/v1/security-rules/{object_id}",
            params={"position": "pre"},
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


class TestSecurityRuleFetch(TestSecurityRuleBase):
    """Tests for fetching Security Rule objects by name."""

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
            "name": "Allow_HTTP",
            "folder": "Shared",
            "action": "allow",
            "from": ["zone1"],
            "to": ["zone2"],
            "source": ["10.0.0.0/24"],
            "destination": ["0.0.0.0/0"],
            "application": ["web-browsing"],
            "service": ["application-default"],
            "log_setting": "Cortex Data Lake",
            "description": "Allow HTTP traffic",
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        # Call the fetch method
        fetched_object = self.client.fetch(
            name=mock_response["name"],
            folder=mock_response["folder"],
        )

        # Assert that the GET request was made with the correct parameters
        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/security/v1/security-rules",
            params={
                "folder": mock_response["folder"],
                "name": mock_response["name"],
                "position": "pre",
            },
        )

        # Validate the returned object
        assert isinstance(fetched_object, dict)
        assert str(fetched_object["id"]) == mock_response["id"]
        assert fetched_object["name"] == mock_response["name"]
        assert fetched_object["action"] == mock_response["action"]
        assert fetched_object["from_"] == mock_response["from"]
        assert fetched_object["to_"] == mock_response["to"]

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
            self.client.fetch(name="test-rule")
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

        # Test multiple containers provided
        with pytest.raises(ValidationError) as exc_info:
            self.client.fetch(name="test-rule", folder="Shared", snippet="TestSnippet")
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
        assert "2 validation errors for SecurityRuleResponseModel" in str(
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


class TestSecurityRuleListFilters(TestSecurityRuleBase):
    """Tests for filtering during listing Security Rule objects."""

    def test_list_with_filters(self):
        """
        **Objective:** Test that filters are properly added to parameters.
        **Workflow:**
            1. Calls list with various filters
            2. Verifies filters are properly formatted in the request
        """
        filters = {
            "action": ["allow"],
            "source": ["10.0.0.0/24"],
            "destination": ["any"],
        }

        mock_response = {"data": []}
        self.mock_scm.get.return_value = mock_response  # noqa

        self.client.list(folder="Shared", **filters)

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/security/v1/security-rules",
            params={
                "position": "pre",
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


class TestRulebaseValidation(TestSecurityRuleBase):
    """Tests for rulebase validation across different methods."""

    def test_create_invalid_rulebase(self):
        """Test create method with invalid rulebase value."""
        test_data = {
            "name": "TestRule",
            "folder": "Shared",
            "action": Action.allow,
        }

        with pytest.raises(ValueError) as exc_info:
            self.client.create(test_data, rulebase="invalid")
        assert "rulebase must be either 'pre' or 'post'" in str(exc_info.value)

    def test_get_invalid_rulebase(self):
        """Test get method with invalid rulebase value."""
        test_id = "123e4567-e89b-12d3-a456-426655440000"

        with pytest.raises(ValueError) as exc_info:
            self.client.get(test_id, rulebase="invalid")
        assert "rulebase must be either 'pre' or 'post'" in str(exc_info.value)

    def test_update_invalid_rulebase(self):
        """Test update method with invalid rulebase value."""
        test_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestRule",
            "folder": "Shared",
            "action": Action.allow,
        }

        with pytest.raises(ValueError) as exc_info:
            self.client.update(test_data, rulebase="invalid")
        assert "rulebase must be either 'pre' or 'post'" in str(exc_info.value)

    def test_list_invalid_rulebase(self):
        """Test list method with invalid rulebase value."""
        with pytest.raises(ValueError) as exc_info:
            self.client.list(folder="Shared", rulebase="invalid")
        assert "rulebase must be either 'pre' or 'post'" in str(exc_info.value)

    def test_delete_invalid_rulebase(self):
        """Test delete method with invalid rulebase value."""
        test_id = "123e4567-e89b-12d3-a456-426655440000"

        with pytest.raises(ValueError) as exc_info:
            self.client.delete(test_id, rulebase="invalid")
        assert "rulebase must be either 'pre' or 'post'" in str(exc_info.value)

    def test_valid_rulebase_values(self):
        """Test that valid rulebase values are accepted."""
        test_data = {
            "name": "TestRule",
            "folder": "Shared",
            "action": Action.allow,
        }

        # Mock successful responses with a valid UUID
        mock_response = {"id": "123e4567-e89b-12d3-a456-426655440000", **test_data}
        self.mock_scm.post.return_value = mock_response  # noqa

        # Test both 'pre' and 'post' values
        for value in ["pre", "post", Rulebase.PRE, Rulebase.POST]:
            try:
                self.client.create(test_data, rulebase=value)
            except ValueError:
                pytest.fail(f"Valid rulebase value '{value}' raised ValueError")

    def test_fetch_invalid_rulebase(self):
        """
        Test fetch method with invalid rulebase value.
        Verifies that the correct ValueError is raised when an invalid rulebase is provided.
        """
        with pytest.raises(ValueError) as exc_info:
            self.client.fetch(name="test-rule", folder="Shared", rulebase="invalid")
        assert "rulebase must be either 'pre' or 'post'" in str(exc_info.value)

    def test_fetch_rulebase_validation(self):
        """
        Test comprehensive rulebase validation in fetch method.
        Tests various invalid rulebase values and ensures proper error handling.
        """
        # Mock a valid response
        self.mock_scm.get.return_value = {  # noqa
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-rule",
            "folder": "Shared",
            "action": Action.allow,
        }

        test_cases = [
            "invalid",
            "both",
            "123",
            "prepost",
            "postpre",
            "preview",
            "postview",
            "prepre",
            "postpost",
        ]

        for invalid_rulebase in test_cases:
            with pytest.raises(ValueError) as exc_info:
                self.client.fetch(
                    name="test-rule", folder="Shared", rulebase=invalid_rulebase
                )
            assert "rulebase must be either 'pre' or 'post'" in str(exc_info.value)

    def test_fetch_rulebase_case_handling(self):
        """
        Test that valid rulebase values in different cases are accepted.
        Verifies that the case conversion works correctly.
        """
        # Mock a valid response
        self.mock_scm.get.return_value = {  # noqa
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-rule",
            "folder": "Shared",
            "action": Action.allow,
        }

        valid_cases = [
            "pre",
            "PRE",
            "Pre",
            "pRe",
            "post",
            "POST",
            "Post",
            "pOsT",
        ]

        for valid_rulebase in valid_cases:
            try:
                self.client.fetch(
                    name="test-rule", folder="Shared", rulebase=valid_rulebase
                )
            except ValueError:
                pytest.fail(
                    f"Valid rulebase value '{valid_rulebase}' raised ValueError"
                )


class TestProfileSettingValidation(TestSecurityRuleBase):
    """Tests for ProfileSetting model validation."""

    def test_group_unique_items(self):
        """
        Test that duplicate items in group list raise ValueError.
        Verifies that the unique items validation works correctly.
        """
        # Test with duplicate items
        with pytest.raises(ValueError) as exc_info:
            ProfileSetting(group=["best-practice", "best-practice"])
        assert "List items in 'group' must be unique" in str(exc_info.value)

        with pytest.raises(ValueError) as exc_info:
            ProfileSetting(group=["strict", "moderate", "strict"])
        assert "List items in 'group' must be unique" in str(exc_info.value)

    def test_group_valid_items(self):
        """Test that unique items in group list are accepted."""
        # Test with unique items
        valid_cases = [
            ["best-practice"],
            ["strict"],
            ["best-practice", "strict"],
            ["moderate", "strict", "best-practice"],
            [],  # Empty list should be valid
            None,  # None should be valid and default to ["best-practice"]
        ]

        for case in valid_cases:
            try:
                profile = ProfileSetting(group=case)
                if case is None:
                    assert profile.group == ProfileSetting(group=None).group
                else:
                    assert profile.group == case
            except ValueError:
                pytest.fail(f"Valid group value {case} raised ValueError")

    def test_group_default_value(self):
        """Test that default value is set correctly when no group is specified."""
        profile = ProfileSetting()
        assert profile.group == ["best-practice"]


class TestSecurityRuleFilters(TestSecurityRuleBase):
    """Tests for security rule filtering functionality."""

    @pytest.fixture(autouse=True)
    def init_sample_rules(self):
        """Initialize sample rules for testing filters."""
        self.sample_rules = [
            SecurityRuleResponseModel(
                id="123e4567-e89b-12d3-a456-426655440000",
                name="rule1",
                folder="Shared",
                action=Action.allow,
                source=["10.0.0.0/24"],
                destination=["any"],
                application=["web-browsing"],
                service=["application-default"],
                from_=["trust"],
                to_=["untrust"],
                tag=["tag1"],
                disabled=False,
                profile_setting=ProfileSetting(group=["best-practice"]),
                log_setting="default",
            ),
            SecurityRuleResponseModel(
                id="987ffedc-ba98-7654-3210-abcdef123456",
                name="rule2",
                folder="Shared",
                action=Action.deny,
                source=["any"],
                destination=["192.168.1.0/24"],
                application=["any"],
                service=["service1"],
                from_=["untrust"],
                to_=["trust"],
                tag=["tag2"],
                disabled=True,
                profile_setting=ProfileSetting(group=["strict"]),
                log_setting="custom",
            ),
        ]

    def test_filter_non_list_values(self):
        """Test that non-list values raise ValidationError for list fields."""
        filter_fields = [
            "action",
            "category",
            "service",
            "application",
            "destination",
            "to_",
            "source",
            "from_",
            "tag",
            "profile_setting",
            "log_setting",
        ]

        for field in filter_fields:
            with pytest.raises(ValidationError) as exc_info:
                self.client._apply_filters(self.sample_rules, {field: "not-a-list"})
            assert f"'{field}' filter must be a list" in str(exc_info.value)

    def test_filter_non_boolean_disabled(self):
        """Test that non-boolean values raise ValidationError for disabled field."""
        with pytest.raises(ValidationError) as exc_info:
            self.client._apply_filters(self.sample_rules, {"disabled": "not-a-boolean"})
        assert "'disabled' filter must be a boolean" in str(exc_info.value)

    def test_filter_criteria(self):
        """Test filter criteria application."""
        test_cases = [
            ({"action": [Action.allow]}, 1),
            ({"source": ["10.0.0.0/24"]}, 1),
            ({"destination": ["any"]}, 1),
            ({"application": ["web-browsing"]}, 1),
            ({"service": ["application-default"]}, 1),
            ({"from_": ["trust"]}, 1),
            ({"to_": ["untrust"]}, 1),
            ({"tag": ["tag1"]}, 1),
            ({"disabled": True}, 1),
            ({"profile_setting": ["best-practice"]}, 1),
            ({"log_setting": ["default"]}, 1),
        ]

        for filters, expected_count in test_cases:
            filtered_rules = self.client._apply_filters(self.sample_rules, filters)
            assert len(filtered_rules) == expected_count, f"Filter {filters} failed"

    def test_multiple_filters(self):
        """Test applying multiple filters simultaneously."""
        filters = {
            "action": [Action.allow],
            "application": ["web-browsing"],
            "source": ["10.0.0.0/24"],
        }

        filtered_rules = self.client._apply_filters(self.sample_rules, filters)
        assert len(filtered_rules) == 1
        assert filtered_rules[0].name == "rule1"

    def test_filter_no_matches(self):
        """Test filtering with criteria that match no rules."""
        filters = {
            "action": [Action.reset_both],
        }

        filtered_rules = self.client._apply_filters(self.sample_rules, filters)
        assert len(filtered_rules) == 0

    def test_category_filter(self):
        """
        Test category filtering functionality.
        Tests that category filtering works correctly with different category values.
        """
        # Create test rules with specific categories
        test_rules = [
            SecurityRuleResponseModel(
                id="123e4567-e89b-12d3-a456-426655440000",
                name="rule1",
                folder="Shared",
                action=Action.allow,
                category=["social-networking", "gaming"],
            ),
            SecurityRuleResponseModel(
                id="987ffedc-ba98-7654-3210-abcdef123456",
                name="rule2",
                folder="Shared",
                action=Action.allow,
                category=["any"],
            ),
            SecurityRuleResponseModel(
                id="456e7890-cdef-4abc-9012-34567890abcd",
                name="rule3",
                folder="Shared",
                action=Action.allow,
                category=["streaming", "social-networking"],
            ),
        ]

        # Test single category filter
        filters = {"category": ["social-networking"]}
        filtered_rules = self.client._apply_filters(test_rules, filters)
        assert len(filtered_rules) == 2
        assert all("social-networking" in rule.category for rule in filtered_rules)

        # Test multiple categories
        filters = {"category": ["gaming", "streaming"]}
        filtered_rules = self.client._apply_filters(test_rules, filters)
        assert len(filtered_rules) == 2
        assert any("gaming" in rule.category for rule in filtered_rules)
        assert any("streaming" in rule.category for rule in filtered_rules)

        # Test category not present
        filters = {"category": ["non-existent-category"]}
        filtered_rules = self.client._apply_filters(test_rules, filters)
        assert len(filtered_rules) == 0

        # Test with empty category list
        filters = {"category": []}
        filtered_rules = self.client._apply_filters(test_rules, filters)
        assert len(filtered_rules) == 0

        # Test with 'any' category
        filters = {"category": ["any"]}
        filtered_rules = self.client._apply_filters(test_rules, filters)
        assert len(filtered_rules) == 1
        assert "any" in filtered_rules[0].category

    def test_category_filter_invalid_input(self):
        """
        Test category filtering with invalid input.
        Verifies that appropriate errors are raised for invalid category filters.
        """
        # Test with non-list category
        with pytest.raises(ValidationError) as exc_info:
            self.client._apply_filters(
                self.sample_rules, {"category": "social-networking"}
            )
        assert "'category' filter must be a list" in str(exc_info.value)

        # Test with None value
        with pytest.raises(ValidationError) as exc_info:
            self.client._apply_filters(self.sample_rules, {"category": None})
        assert "'category' filter must be a list" in str(exc_info.value)


class TestSecurityRuleMove(TestSecurityRuleBase):
    """Tests for security rule move operations."""

    def test_move_rule_to_top(self):
        """Test moving a rule to the top of the rulebase."""
        rule_id = "123e4567-e89b-12d3-a456-426655440000"
        move_data = {
            "destination": RuleMoveDestination.TOP,
            "rulebase": Rulebase.PRE,
        }

        self.client.move(rule_id, move_data)

        expected_payload = {
            "source_rule": rule_id,
            "destination": "top",
            "rulebase": "pre",
        }

        self.mock_scm.post.assert_called_once_with(  # noqa
            f"/config/security/v1/security-rules/{rule_id}:move",
            json=expected_payload,
        )

    def test_move_rule_before(self):
        """Test moving a rule before another rule."""
        rule_id = "123e4567-e89b-12d3-a456-426655440000"
        target_rule = "987ffedc-ba98-7654-3210-abcdef123456"
        move_data = {
            "destination": RuleMoveDestination.BEFORE,
            "rulebase": Rulebase.PRE,
            "destination_rule": target_rule,
        }

        self.client.move(rule_id, move_data)

        expected_payload = {
            "source_rule": rule_id,
            "destination": "before",
            "rulebase": "pre",
            "destination_rule": target_rule,
        }

        self.mock_scm.post.assert_called_once_with(  # noqa
            f"/config/security/v1/security-rules/{rule_id}:move",
            json=expected_payload,
        )

    def test_move_rule_validation_error(self):
        """Test validation error when moving a rule with invalid parameters."""
        rule_id = "123e4567-e89b-12d3-a456-426655440000"
        # Missing destination_rule for BEFORE operation
        move_data = {
            "destination": RuleMoveDestination.BEFORE,
            "rulebase": Rulebase.PRE,
        }

        with pytest.raises(ValueError) as exc_info:
            self.client.move(rule_id, move_data)
        assert "destination_rule is required" in str(exc_info.value)

    def test_move_rule_error_handling(self):
        """Test error handling during rule move operation."""
        rule_id = "123e4567-e89b-12d3-a456-426655440000"
        move_data = {
            "destination": RuleMoveDestination.TOP,
            "rulebase": Rulebase.PRE,
        }

        # Mock error response
        mock_error_response = {
            "_errors": [
                {
                    "code": "API_I00013",
                    "message": "Move failed",
                    "details": {"errorType": "Object Not Present"},
                }
            ],
            "_request_id": "test-request-id",
        }

        self.mock_scm.post.side_effect = Exception()  # noqa
        self.mock_scm.post.side_effect.response = MagicMock()  # noqa
        self.mock_scm.post.side_effect.response.json = MagicMock(  # noqa
            return_value=mock_error_response
        )

        with pytest.raises(ObjectNotPresentError):
            self.client.move(rule_id, move_data)

    def test_move_invalid_destination(self):
        """Test moving a rule with invalid destination type."""
        rule_id = "123e4567-e89b-12d3-a456-426655440000"
        move_data = {
            "destination": "invalid",
            "rulebase": Rulebase.PRE,
        }

        with pytest.raises(ValueError):
            self.client.move(rule_id, move_data)

    def test_move_rule_invalid_destination_rule(self):
        """
        Test validation when destination_rule is provided for TOP/BOTTOM moves.
        Verifies that providing destination_rule for destinations that don't require it raises ValueError.
        """
        rule_id = "123e4567-e89b-12d3-a456-426655440000"
        target_rule = "987ffedc-ba98-7654-3210-abcdef123456"

        # Test with TOP destination
        move_data = {
            "destination": RuleMoveDestination.TOP,
            "rulebase": Rulebase.PRE,
            "destination_rule": target_rule,  # This should raise error for TOP
        }

        with pytest.raises(ValueError) as exc_info:
            self.client.move(rule_id, move_data)
        assert (
            "destination_rule should not be provided when destination is 'top'"
            in str(exc_info.value)
        )

        # Test with BOTTOM destination
        move_data = {
            "destination": RuleMoveDestination.BOTTOM,
            "rulebase": Rulebase.PRE,
            "destination_rule": target_rule,  # This should raise error for BOTTOM
        }

        with pytest.raises(ValueError) as exc_info:
            self.client.move(rule_id, move_data)
        assert (
            "destination_rule should not be provided when destination is 'bottom'"
            in str(exc_info.value)
        )


# -------------------- End of Test Classes --------------------
