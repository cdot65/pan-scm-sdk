# tests/scm/config/objects/test_address_group.py

import pytest
from unittest.mock import MagicMock

from scm.config.objects import AddressGroup
from scm.exceptions import (
    ValidationError,
    ObjectNotPresentError,
    ReferenceNotZeroError,
    EmptyFieldError,
    ObjectAlreadyExistsError,
    MalformedRequestError,
    FolderNotFoundError,
    BadResponseError,
)
from scm.models.objects import (
    AddressGroupCreateModel,
    AddressGroupResponseModel,
)

from tests.factories import (
    AddressGroupDynamicFactory,
    AddressGroupStaticFactory,
)

from pydantic import ValidationError as PydanticValidationError


@pytest.mark.usefixtures("load_env")
class TestAddressGroupBase:
    """Base class for Address Group tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm  # noqa
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = AddressGroup(self.mock_scm)  # noqa


# -------------------- Test Classes Grouped by Functionality --------------------


class TestAddressGroupList(TestAddressGroupBase):
    """Tests for listing Address Group objects."""

    def test_list_address_groups(self):
        """
        **Objective:** Test listing all address groups.
        **Workflow:**
            1. Sets up a mock response resembling the expected API response for listing address groups.
            2. Calls the `list` method of `self.client` with a filter parameter (`folder="All"`).
            3. Asserts that the mocked service was called correctly.
            4. Validates the returned list of address groups, checking their types and attributes.
        """
        mock_response = {
            "data": [
                {
                    "id": "123e4567-e89b-12d3-a456-426655440000",
                    "name": "DAG_test",
                    "folder": "All",
                    "description": "test123",
                    "dynamic": {
                        "filter": "'aws.ec2.key.Name.value.scm-test-scm-test-vpc'"
                    },
                },
                {
                    "id": "4ee5b3cd-0308-43ce-b5db-3722bdc2706c",
                    "name": "djs_DB",
                    "folder": "cdot65",
                    "dynamic": {"filter": "'aws.ec2.tag.Environment.DB'"},
                },
                {
                    "id": "630bfb3d-93a4-4cde-95ca-feed6d8dacad",
                    "name": "test - address group 1",
                    "folder": "Texas",
                    "description": "Test address group 1",
                    "static": ["test_network1"],
                    "tag": ["Automation"],
                },
            ],
            "offset": 0,
            "total": 3,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        address_groups = self.client.list(folder="All")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/address-groups",
            params={
                "limit": 10000,
                "folder": "All",
            },
        )
        assert isinstance(address_groups, list)
        assert isinstance(address_groups[0], AddressGroupResponseModel)
        assert len(address_groups) == 3
        assert address_groups[0].name == "DAG_test"


class TestAddressGroupCreate(TestAddressGroupBase):
    """Tests for creating Address Group objects."""

    def test_create_address_group_of_type_static(self):
        """
        **Objective:** Test creating an address group of type static.
        **Workflow:**
            1. Uses `AddressGroupStaticFactory` to create an object.
            2. Sets up a mock response with an added `id`.
            3. Calls the `create` method of `self.client` with the address data.
            4. Asserts that the mocked service was called with the correct parameters.
            5. Validates the created address group's attributes.
        """
        test_address_group_static = AddressGroupStaticFactory()
        mock_response = test_address_group_static.model_dump()
        mock_response["id"] = "12345678-abcd-abcd-abcd-123456789012"

        self.mock_scm.post.return_value = mock_response  # noqa
        created_group = self.client.create(
            test_address_group_static.model_dump(exclude_unset=True)
        )

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/address-groups",
            json=test_address_group_static.model_dump(exclude_unset=True),
        )
        assert created_group.id == "12345678-abcd-abcd-abcd-123456789012"
        assert created_group.name == test_address_group_static.name
        assert created_group.static == test_address_group_static.static
        assert created_group.folder == test_address_group_static.folder
        assert created_group.tag == test_address_group_static.tag

    def test_create_address_group_of_type_dynamic(self):
        """
        **Objective:** Test creating an address group object of type fqdn.
        **Workflow:**
            1. Uses `AddressGroupDynamicFactory` to create an object.
            2. Sets up a mock response with an added `id`.
            3. Calls the `create` method of `self.client` with the address data.
            4. Asserts that the mocked service was called with the correct parameters.
            5. Validates the created address group's attributes.
        """
        test_address_group_dynamic = AddressGroupDynamicFactory()
        mock_response = test_address_group_dynamic.model_dump()
        mock_response["id"] = "12345678-abcd-abcd-abcd-123456789012"

        self.mock_scm.post.return_value = mock_response  # noqa
        created_group = self.client.create(
            test_address_group_dynamic.model_dump(exclude_unset=True)
        )

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/address-groups",
            json=test_address_group_dynamic.model_dump(exclude_unset=True),
        )
        assert created_group.id == "12345678-abcd-abcd-abcd-123456789012"
        assert created_group.name == test_address_group_dynamic.name
        assert created_group.dynamic == test_address_group_dynamic.dynamic
        assert created_group.folder == test_address_group_dynamic.folder
        assert created_group.tag == test_address_group_dynamic.tag

    def test_create_object_error_handling(self):
        """
        **Objective:** Test error handling during object creation.
        **Workflow:**
            1. Mocks an error response from the API
            2. Attempts to create an object
            3. Verifies proper error handling and exception raising
        """
        test_data = AddressGroupStaticFactory()

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
        test_data = AddressGroupStaticFactory()

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
        test_data = AddressGroupStaticFactory()

        # Mock invalid JSON response
        self.mock_scm.post.return_value = {"malformed": "response"}  # noqa

        with pytest.raises(PydanticValidationError):
            self.client.create(test_data.model_dump())


class TestAddressGroupGet(TestAddressGroupBase):
    """Tests for retrieving a specific Address Group object."""

    def test_get_address_group(self):
        """
        **Objective:** Test retrieving an address group by its ID.
        **Workflow:**
            1. Sets up a mock response resembling the expected API response for fetching an address group by ID.
            2. Calls the `get` method of `self.client` with a specific group ID.
            3. Asserts that the mocked service was called with the correct URL.
            4. Validates the returned address group's attributes.
        """
        mock_response = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "DAG_test",
            "folder": "All",
            "description": "test123",
            "dynamic": {"filter": "'aws.ec2.key.Name.value.scm-test-scm-test-vpc'"},
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        address_group = self.client.get(mock_response["id"])

        self.mock_scm.get.assert_called_once_with(  # noqa
            f"/config/objects/v1/address-groups/{mock_response['id']}"
        )
        assert isinstance(address_group, AddressGroupResponseModel)
        assert address_group.id == mock_response["id"]
        assert address_group.name == mock_response["name"]
        assert address_group.description == mock_response["description"]

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


class TestAddressGroupUpdate(TestAddressGroupBase):
    """Tests for updating Address Group objects."""

    def test_update_address_group(self):
        """
        **Objective:** Test updating an existing object.
        **Workflow:**
            1. Sets up the update data for the object.
            2. Sets up a mock response that includes the updated data.
            3. Calls the `update` method of `self.client` with the update data.
            4. Asserts that the mocked service was called with the correct URL and data.
            5. Validates the updated object's attributes.
        """
        update_group_data = {
            "name": "DAG_test",
            "description": "test123",
            "dynamic": {"filter": "'aws.ec2.key.Name.value.scm-test-scm-test-vpc'"},
            "folder": "All",
            "id": "123e4567-e89b-12d3-a456-426655440000",
        }

        mock_response = update_group_data.copy()

        self.mock_scm.put.return_value = mock_response  # noqa
        updated_address_group = self.client.update(update_group_data)

        # Prepare the expected payload by excluding 'id'
        expected_payload = update_group_data.copy()
        expected_payload.pop("id")

        self.mock_scm.put.assert_called_once_with(  # noqa
            f"/config/objects/v1/address-groups/{update_group_data['id']}",
            json=expected_payload,
        )
        assert isinstance(updated_address_group, AddressGroupResponseModel)
        assert updated_address_group.id == mock_response["id"]
        assert updated_address_group.name == mock_response["name"]
        assert updated_address_group.description == mock_response["description"]

    def test_update_object_error_handling(self):
        """
        **Objective:** Test error handling during object update.
        **Workflow:**
            1. Mocks an error response from the API
            2. Attempts to update an object
            3. Verifies proper error handling and exception raising
        """
        update_group_data = {
            "name": "DAG_test",
            "description": "test123",
            "dynamic": {"filter": "'aws.ec2.key.Name.value.scm-test-scm-test-vpc'"},
            "folder": "All",
            "id": "123e4567-e89b-12d3-a456-426655440000",
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
            self.client.update(update_group_data)

    def test_update_generic_exception_handling(self):
        """
        **Objective:** Test generic exception handling in update method.
        **Workflow:**
            1. Mocks a generic exception without response attribute
            2. Verifies the original exception is re-raised
        """
        update_data = {
            "name": "DAG_test",
            "description": "test123",
            "dynamic": {"filter": "'aws.ec2.key.Name.value.scm-test-scm-test-vpc'"},
            "folder": "All",
            "id": "123e4567-e89b-12d3-a456-426655440000",
        }

        # Mock a generic exception without response
        self.mock_scm.put.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.update(update_data)
        assert str(exc_info.value) == "Generic error"


class TestAddressGroupDelete(TestAddressGroupBase):
    """Tests for deleting Address Groups."""

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


class TestAddressGroupFetch(TestAddressGroupBase):
    """Tests for fetching Address Group objects by name."""

    def test_fetch_address_group(self):
        """
        **Objective:** Test retrieving an object by its name using the `fetch` method.
        **Workflow:**
            1. Sets up a mock response resembling the expected API response for fetching an object by name.
            2. Calls the `fetch` method of `self.client` with a specific name and container.
            3. Asserts that the mocked service was called with the correct URL and parameters.
            4. Validates the returned object's attributes.
        """
        mock_response = {
            "name": "DAG_test",
            "description": "test123",
            "dynamic": {"filter": "'aws.ec2.key.Name.value.scm-test-scm-test-vpc'"},
            "folder": "All",
            "id": "123e4567-e89b-12d3-a456-426655440000",
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        # Call the fetch method
        address_group = self.client.fetch(
            name=mock_response["name"],
            folder=mock_response["folder"],
        )

        # Assert that the GET request was made with the correct parameters
        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/address-groups",
            params={
                "folder": mock_response["folder"],
                "name": mock_response["name"],
            },
        )

        # Validate the returned address
        assert isinstance(address_group, dict)
        assert address_group["id"] == mock_response["id"]
        assert address_group["name"] == mock_response["name"]
        assert address_group["description"] == mock_response["description"]
        assert address_group["dynamic"] == mock_response["dynamic"]

    def test_fetch_address_not_found(self):
        """
        Test fetching an object by name that does not exist.

        **Objective:** Test that fetching a non-existent object raises NotFoundError.
        **Workflow:**
            1. Mocks the API response to return an empty 'data' list.
            2. Calls the `fetch` method with a name that does not exist.
            3. Asserts that NotFoundError is raised.
        """
        address_name = "NonExistent"
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
                name=address_name,
                folder=folder_name,
            )

    def test_fetch_address_group_no_name(self):
        """
        Test fetching an address group without providing the 'name' parameter.

        **Objective:** Ensure that the fetch method raises ValidationError when 'name' is not provided.
        **Workflow:**
            1. Calls the `fetch` method without the 'name' parameter.
            2. Asserts that ValidationError is raised.
        """
        folder_name = "Shared"
        with pytest.raises(ValidationError) as exc_info:
            self.client.fetch(
                folder=folder_name,
                name="",
            )
        assert str(exc_info.value) == "Field 'name' cannot be empty"

    def test_fetch_address_group_unexpected_response_format(self):
        """
        Test fetching an address group when the API returns an unexpected response format.

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
            self.client.fetch(
                name=group_name,
                folder=folder_name,
            )
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
            self.client.fetch(
                name="test",
                folder="",
            )
        assert "Field 'folder' cannot be empty" in str(exc_info.value)

        # Test multiple containers
        with pytest.raises(ValidationError) as exc_info:
            self.client.fetch(
                name="test",
                folder="folder1",
                snippet="snippet1",
            )
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
            self.client.fetch(
                name="test",
                folder="Shared",
            )
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
            self.client.fetch(
                name="test",
                folder="Shared",
            )
        assert "Invalid response format: missing 'id' field" in str(exc_info.value)

        # Test response with both id and data fields (invalid format)
        self.mock_scm.get.return_value = {  # noqa
            "id": "some-id",
            "data": [{"some": "data"}],
        }  # noqa

        with pytest.raises(PydanticValidationError) as exc_info:
            self.client.fetch(
                name="test",
                folder="Shared",
            )
        assert "2 validation errors for AddressGroupResponseModel" in str(
            exc_info.value
        )
        assert "name\n  Field required" in str(exc_info.value)
        assert "id\n  Value error, Invalid UUID format for 'id'" in str(exc_info.value)

        # Test malformed response in list format
        self.mock_scm.get.return_value = [{"unexpected": "format"}]  # noqa
        with pytest.raises(BadResponseError) as exc_info:
            self.client.fetch(
                name="test",
                folder="Shared",
            )
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


class TestAddressGroupValidation(TestAddressGroupBase):
    """Tests for Address model validation."""

    def test_address_create_model_no_type_provided(self):
        """Test validation when no type is provided."""
        data = {
            "name": "Test123",
            "folder": "Shared",
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            AddressGroupCreateModel(**data)
        assert "1 validation error for AddressGroupCreateModel" in str(exc_info.value)
        assert (
            "Value error, Exactly one of 'static' or 'dynamic' must be provided."
            in str(exc_info.value)
        )

    def test_address_group_create_model_multiple_types_provided(self):
        """Test validation when multiple types are provided."""
        data = {
            "name": "DAG_test",
            "description": "test123",
            "dynamic": {"filter": "'aws.ec2.key.Name.value.scm-test-scm-test-vpc'"},
            "static": ["None"],
            "folder": "All",
        }

        with pytest.raises(PydanticValidationError) as exc_info:
            AddressGroupCreateModel(**data)
        assert "Exactly one of 'static' or 'dynamic' must be provided." in str(
            exc_info.value
        )

    def test_address_group_create_model_valid(self):
        """Test validation with valid data."""
        data = {
            "name": "DAG_test",
            "description": "test123",
            "dynamic": {"filter": "'aws.ec2.key.Name.value.scm-test-scm-test-vpc'"},
            "folder": "All",
        }

        model = AddressGroupCreateModel(**data)
        assert model.name == data["name"]
        assert model.folder == data["folder"]

    def test_address_group_create_model_invalid_container(self):
        """Test validation with multiple container types."""
        data = {
            "name": "DAG_test",
            "description": "test123",
            "dynamic": {"filter": "'aws.ec2.key.Name.value.scm-test-scm-test-vpc'"},
            "folder": "All",
            "snippet": "Test",
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            AddressGroupCreateModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_invalid_uuid_format(self):
        """
        Test UUID format validator.

        **Objective:** Verify that invalid UUID formats raise ValueError.
        **Workflow:**
            1. Attempts to create/update an address with invalid UUID
            2. Validates that appropriate error is raised
        """
        data = {
            "name": "DAG_test",
            "description": "test123",
            "dynamic": {"filter": "'aws.ec2.key.Name.value.scm-test-scm-test-vpc'"},
            "folder": "All",
            "id": "fsad",
        }

        with pytest.raises(PydanticValidationError) as exc_info:
            AddressGroupResponseModel(**data)
        assert "Invalid UUID format for 'id'" in str(exc_info.value)

    def test_valid_uuid_format(self):
        """
        Test valid UUID format.

        **Objective:** Verify that valid UUID formats are accepted.
        **Workflow:**
            1. Creates/updates an address with valid UUID
            2. Validates that the UUID is accepted
        """
        data = {
            "name": "DAG_test",
            "description": "test123",
            "dynamic": {"filter": "'aws.ec2.key.Name.value.scm-test-scm-test-vpc'"},
            "folder": "All",
            "id": "123e4567-e89b-12d3-a456-426655440000",
        }
        model = AddressGroupResponseModel(**data)
        assert model.id == "123e4567-e89b-12d3-a456-426655440000"


class TestAddressGroupTagValidation(TestAddressGroupBase):
    """Tests for Address tag field validation."""

    def test_tag_string_to_list_conversion(self):
        """
        Test tag field validator converting a string to a list.

        **Objective:** Verify that a single string tag is properly converted to a list.
        **Workflow:**
            1. Creates an address with a single string tag
            2. Validates the tag is converted to a single-item list
        """
        data = {
            "name": "DAG_test",
            "description": "test123",
            "tag": "TestTag",
            "dynamic": {"filter": "'aws.ec2.key.Name.value.scm-test-scm-test-vpc'"},
            "folder": "All",
            "id": "123e4567-e89b-12d3-a456-426655440000",
        }
        model = AddressGroupCreateModel(**data)
        assert isinstance(model.tag, list)
        assert model.tag == ["TestTag"]

    def test_tag_list_passed_through(self):
        """
        Test tag field validator passing through a list.

        **Objective:** Verify that a list of tags is properly handled.
        **Workflow:**
            1. Creates an address with multiple tags as a list
            2. Validates the tags remain as a list
        """
        data = {
            "name": "DAG_test",
            "description": "test123",
            "tag": ["Tag1", "Tag2"],
            "dynamic": {"filter": "'aws.ec2.key.Name.value.scm-test-scm-test-vpc'"},
            "folder": "All",
            "id": "123e4567-e89b-12d3-a456-426655440000",
        }
        model = AddressGroupCreateModel(**data)
        assert isinstance(model.tag, list)
        assert model.tag == ["Tag1", "Tag2"]

    def test_tag_invalid_type(self):
        """
        Test tag field validator with invalid type.

        **Objective:** Verify that non-string/non-list tag values raise ValueError.
        **Workflow:**
            1. Attempts to create an address with an invalid tag type (dict)
            2. Validates that appropriate error is raised
        """
        data = {
            "name": "DAG_test",
            "description": "test123",
            "tag": {"invalid": "type"},
            "dynamic": {"filter": "'aws.ec2.key.Name.value.scm-test-scm-test-vpc'"},
            "folder": "All",
            "id": "123e4567-e89b-12d3-a456-426655440000",
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            AddressGroupCreateModel(**data)
        assert "1 validation error for AddressGroupCreateModel" in str(exc_info.value)

    def test_tag_duplicate_items(self):
        """
        Test tag uniqueness validator.

        **Objective:** Verify that duplicate tags raise ValueError.
        **Workflow:**
            1. Attempts to create an address with duplicate tags
            2. Validates that appropriate error is raised
        """
        data = {
            "name": "DAG_test",
            "description": "test123",
            "tag": ["Tag1", "Tag1"],
            "dynamic": {"filter": "'aws.ec2.key.Name.value.scm-test-scm-test-vpc'"},
            "folder": "All",
            "id": "123e4567-e89b-12d3-a456-426655440000",
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            AddressGroupCreateModel(**data)
        assert "List items must be unique" in str(exc_info.value)


class TestAddressGroupListFilters(TestAddressGroupBase):
    """Tests for filtering during listing Address Group objects."""

    def test_list_with_filters(self):
        """
        **Objective:** Test that filters are properly added to parameters.
        **Workflow:**
            1. Calls list with various filters
            2. Verifies filters are properly formatted in the request
        """
        filters = {
            "types": ["type1", "type2"],
            "values": ["value1", "value2"],
            "tags": ["tag1", "tag2"],
        }

        mock_response = {"data": []}
        self.mock_scm.get.return_value = mock_response  # noqa

        self.client.list(folder="Shared", **filters)

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/address-groups",
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
                    "id": "123e4567-e89b-12d3-a456-426655440000",
                    "name": "DAG_test",
                    "folder": "All",
                    "description": "test123",
                    "dynamic": {
                        "filter": "'aws.ec2.key.Name.value.scm-test-scm-test-vpc'"
                    },
                },
                {
                    "id": "4ee5b3cd-0308-43ce-b5db-3722bdc2706c",
                    "name": "djs_DB",
                    "folder": "cdot65",
                    "dynamic": {"filter": "'aws.ec2.tag.Environment.DB'"},
                },
                {
                    "id": "630bfb3d-93a4-4cde-95ca-feed6d8dacad",
                    "name": "test - address group 1",
                    "folder": "Texas",
                    "description": "Test address group 1",
                    "static": ["test_network1"],
                    "tag": ["Automation"],
                },
            ],
            "offset": 0,
            "total": 3,
            "limit": 200,
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test invalid types filter (string instead of list)
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Shared", types="static")
        assert str(exc_info.value) == "'types' filter must be a list"

        # Test invalid values filter (string instead of list)
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Shared", values="test_network1")
        assert str(exc_info.value) == "'values' filter must be a list"

        # Test invalid tags filter (string instead of list)
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Shared", tags="tag1")
        assert str(exc_info.value) == "'tags' filter must be a list"

        # Test invalid types filter (dict instead of list)
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Shared", types={"type": "static"})
        assert str(exc_info.value) == "'types' filter must be a list"

        # Test invalid values filter (dict instead of list)
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Shared", values={"value": "test_network1"})
        assert str(exc_info.value) == "'values' filter must be a list"

        # Test invalid tags filter (dict instead of list)
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Shared", tags={"tag": "tag1"})
        assert str(exc_info.value) == "'tags' filter must be a list"

        # Test invalid types filter (integer instead of list)
        with pytest.raises(ValidationError) as exc_info:
            self.client.list(folder="Shared", types=123)
        assert str(exc_info.value) == "'types' filter must be a list"

        # Test that valid list filters pass validation
        try:
            self.client.list(
                folder="Shared",
                types=["static"],
                values=["test_network1"],
                tags=["Automation"],
            )
        except ValidationError:
            pytest.fail("Unexpected ValidationError raised with valid list filters")

    def test_list_filter_combinations(self):
        """
        **Objective:** Test different combinations of valid filters.
        **Workflow:**
            1. Tests various combinations of valid filters
            2. Verifies filters are properly applied
            3. Checks that filtered results match expected criteria
        """
        mock_response = {
            "data": [
                {
                    "id": "123e4567-e89b-12d3-a456-426655440000",
                    "name": "DAG_test",
                    "folder": "All",
                    "description": "test123",
                    "dynamic": {
                        "filter": "'aws.ec2.key.Name.value.scm-test-scm-test-vpc'"
                    },
                },
                {
                    "id": "4ee5b3cd-0308-43ce-b5db-3722bdc2706c",
                    "name": "djs_DB",
                    "folder": "cdot65",
                    "dynamic": {"filter": "'aws.ec2.tag.Environment.DB'"},
                },
                {
                    "id": "630bfb3d-93a4-4cde-95ca-feed6d8dacad",
                    "name": "test - address group 1",
                    "folder": "Texas",
                    "description": "Test address group 1",
                    "static": ["test_network1"],
                    "tag": ["Automation"],
                },
            ],
            "offset": 0,
            "total": 3,
            "limit": 200,
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test combining types and tags filters
        filtered_address_groups = self.client.list(
            folder="Shared",
            types=["static"],
            tags=["Automation"],
        )
        assert len(filtered_address_groups) == 1
        assert filtered_address_groups[0].name == "test - address group 1"

        # Test combining values and tags filters
        filtered_address_groups = self.client.list(
            folder="Shared",
            values=["test_network1"],
            tags=["Automation"],
        )
        assert len(filtered_address_groups) == 1
        assert filtered_address_groups[0].name == "test - address group 1"

        # Test all filters together
        filtered_address_groups = self.client.list(
            folder="Shared",
            types=["static"],
            values=["test_network1"],
            tags=["Automation"],
        )
        assert len(filtered_address_groups) == 1
        assert filtered_address_groups[0].name == "test - address group 1"

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
                    "id": "123e4567-e89b-12d3-a456-426655440000",
                    "name": "DAG_test",
                    "folder": "All",
                    "description": "test123",
                    "dynamic": {
                        "filter": "'aws.ec2.key.Name.value.scm-test-scm-test-vpc'"
                    },
                },
                {
                    "id": "4ee5b3cd-0308-43ce-b5db-3722bdc2706c",
                    "name": "djs_DB",
                    "folder": "cdot65",
                    "dynamic": {"filter": "'aws.ec2.tag.Environment.DB'"},
                },
                {
                    "id": "630bfb3d-93a4-4cde-95ca-feed6d8dacad",
                    "name": "test - address group 1",
                    "folder": "Texas",
                    "description": "Test address group 1",
                    "static": ["test_network1"],
                    "tag": ["Automation"],
                },
            ],
            "offset": 0,
            "total": 3,
            "limit": 200,
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Empty lists should result in no matches
        filtered_address_groups = self.client.list(
            folder="Shared",
            types=[],
        )
        assert len(filtered_address_groups) == 0

        filtered_address_groups = self.client.list(
            folder="Shared",
            values=[],
        )
        assert len(filtered_address_groups) == 0

        filtered_address_groups = self.client.list(
            folder="Shared",
            tags=[],
        )
        assert len(filtered_address_groups) == 0

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


class TestAddressGroupExceptionHandling(TestAddressGroupBase):
    """Tests for generic exception handling across Address methods."""

    def test_create_generic_exception_handling(self):
        """
        **Objective:** Test generic exception handling in create method.
        **Workflow:**
            1. Mocks a generic exception without response attribute
            2. Verifies the original exception is re-raised
        """
        test_data = AddressGroupStaticFactory()

        # Mock a generic exception without response
        self.mock_scm.post.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.create(test_data.model_dump())
        assert str(exc_info.value) == "Generic error"

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

    def test_update_generic_exception_handling(self):
        """
        **Objective:** Test generic exception handling in update method.
        **Workflow:**
            1. Mocks a generic exception without response attribute
            2. Verifies the original exception is re-raised
        """
        update_data = {
            "id": "630bfb3d-93a4-4cde-95ca-feed6d8dacad",
            "name": "test - address group 1",
            "folder": "Texas",
            "description": "Test address group 1",
            "static": ["test_network1"],
            "tag": ["Automation"],
        }

        # Mock a generic exception without response
        self.mock_scm.put.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.update(update_data)
        assert str(exc_info.value) == "Generic error"

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

    def test_error_handler_raise_through(self):
        """
        **Objective:** Test that ErrorHandler properly raises through original exceptions.
        **Workflow:**
            1. Mocks various exception scenarios
            2. Verifies exceptions are properly propagated
        """

        # Test with non-JSON response
        class MockResponse:
            def json(self):
                raise ValueError("API Error")

        mock_exception = Exception("API Error")
        mock_exception.response = MockResponse()

        self.mock_scm.get.side_effect = mock_exception  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.get("test-id")
        assert "API Error" in str(exc_info.value)


# -------------------- End of Test Classes --------------------
