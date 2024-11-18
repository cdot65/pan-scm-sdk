# tests/scm/config/objects/test_address.py

# Standard library imports
import logging
from unittest.mock import MagicMock

# External libraries
import pytest
from pydantic import ValidationError as PydanticValidationError
from requests.exceptions import HTTPError

# Local SDK imports
from scm.config.objects import Address
from scm.exceptions import (
    APIError,
    BadRequestError,
    InvalidObjectError,
    ObjectNotPresentError,
    MalformedCommandError,
    MissingQueryParameterError,
)
from scm.models.objects import (
    AddressCreateModel,
    AddressResponseModel,
)
from tests.factories import AddressResponseFactory, AddressCreateFactory


@pytest.mark.usefixtures("load_env")
class TestAddressBase:
    """Base class for Address tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm  # noqa
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = Address(self.mock_scm)  # noqa


# -------------------- Test Classes Grouped by Functionality --------------------


class TestAddressModelValidation(TestAddressBase):
    """Tests for object model validation."""

    def test_object_model_no_type_provided(self):
        """Test validation when no type is provided."""
        data = {
            "name": "Test123",
            "folder": "Shared",
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            AddressCreateModel(**data)
        assert "1 validation error for AddressCreateModel" in str(exc_info.value)
        assert (
            "Value error, Exactly one of 'ip_netmask', 'ip_range', 'ip_wildcard', or 'fqdn' must be provided."
            in str(exc_info.value)
        )

    def test_object_model_multiple_types(self):
        """Test validation when multiple types are provided."""
        data = {
            "name": "Test123",
            "folder": "Shared",
            "ip_netmask": "10.5.0.11",
            "fqdn": "test.com",
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            AddressCreateModel(**data)
        assert (
            "Exactly one of 'ip_netmask', 'ip_range', 'ip_wildcard', or 'fqdn' must be provided."
            in str(exc_info.value)
        )

    def test_object_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = {
            "name": "internal_network",
            "ip_netmask": "192.168.1.0/24",
            "description": "Internal network segment",
            "tag": ["Python", "Automation"],
            "folder": "Shared",
            "snippet": "Test123",
        }
        with pytest.raises(ValueError) as exc_info:
            AddressCreateModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_object_model_no_container_provided(self):
        """Test validation when no container is provided."""
        data = {
            "name": "internal_network",
            "ip_netmask": "192.168.1.0/24",
            "description": "Internal network segment",
            "tag": ["Python", "Automation"],
        }

        with pytest.raises(ValueError) as exc_info:
            AddressCreateModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_object_model_create_model_valid(self):
        """Test validation with valid data."""
        data = {
            "name": "Test123",
            "folder": "Shared",
            "ip_netmask": "10.5.0.11",
        }
        model = AddressCreateModel(**data)
        assert model.name == "Test123"
        assert model.folder == "Shared"
        assert model.ip_netmask == "10.5.0.11"


class TestAddressList(TestAddressBase):
    """Tests for listing Address objects."""

    def test_object_list_valid(self):
        """
        **Objective:** Test listing all objects.
        """
        mock_response = {
            "data": [
                AddressResponseFactory.with_fqdn(
                    name="Palo Alto Networks Sinkhole",
                    folder="All",
                    snippet="default",
                    fqdn="sinkhole.paloaltonetworks.com",
                    description="Palo Alto Networks sinkhole",
                ).model_dump(),
                AddressResponseFactory.with_ip_netmask(
                    name="dallas-desktop1",
                    folder="cdot65",
                    snippet="cdot.io Best Practices",
                    ip_netmask="10.5.0.11",
                    description="test123456",
                    tag=["Decrypted"],
                ).model_dump(),
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response  # noqa
        existing_objects = self.client.list(folder="All")

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/addresses",
            params={
                "limit": 10000,
                "folder": "All",
            },
        )
        assert isinstance(existing_objects, list)
        assert isinstance(existing_objects[0], AddressResponseModel)
        assert len(existing_objects) == 2
        assert existing_objects[0].name == "Palo Alto Networks Sinkhole"

    def test_object_list_multiple_containers(self):
        """Test validation error when listing with multiple containers."""
        with pytest.raises(BadRequestError) as exc_info:
            self.client.list(
                folder="Prisma Access",
                snippet="TestSnippet",
            )

        assert "HTTP error: 400 - API error: E003" in str(exc_info.value)


class TestAddressCreate(TestAddressBase):
    """Tests for creating Address objects."""

    def test_create_object_type_ip_netmask(self):
        """
        **Objective:** Test creating an object with ip_netmask.
        """
        test_object = AddressCreateFactory.with_ip_netmask()
        mock_response = AddressResponseFactory.from_request(test_object)

        self.mock_scm.post.return_value = mock_response.model_dump()  # noqa
        created_object = self.client.create(test_object.model_dump(exclude_unset=True))

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/addresses",
            json=test_object.model_dump(exclude_unset=True),
        )
        assert str(created_object.id) == str(mock_response.id)
        assert created_object.name == test_object.name
        assert created_object.ip_netmask == test_object.ip_netmask
        assert created_object.folder == test_object.folder

    def test_create_object_type_fqdn(self):
        """
        **Objective:** Test creating an object of type fqdn.
        """
        test_object = AddressCreateFactory.with_fqdn()
        mock_response = AddressResponseFactory.from_request(test_object)

        self.mock_scm.post.return_value = mock_response.model_dump()  # noqa
        created_object = self.client.create(test_object.model_dump(exclude_unset=True))

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/addresses",
            json=test_object.model_dump(exclude_unset=True),
        )
        assert str(created_object.id) == str(mock_response.id)
        assert created_object.name == test_object.name
        assert created_object.fqdn == test_object.fqdn
        assert created_object.folder == test_object.folder

    def test_create_object_type_ip_range(self):
        """
        **Objective:** Test creating an object of type ip_range.
        """
        test_object = AddressCreateFactory.with_ip_range()
        mock_response = AddressResponseFactory.from_request(test_object)

        self.mock_scm.post.return_value = mock_response.model_dump()  # noqa
        created_object = self.client.create(test_object.model_dump(exclude_unset=True))

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/addresses",
            json=test_object.model_dump(exclude_unset=True),
        )
        assert str(created_object.id) == str(mock_response.id)
        assert created_object.name == test_object.name
        assert created_object.ip_range == test_object.ip_range
        assert created_object.folder == test_object.folder

    def test_create_object_type_ip_wildcard(self):
        """
        **Objective:** Test creating an object of type ip_wildcard.
        """
        test_object = AddressCreateFactory.with_ip_wildcard()
        mock_response = AddressResponseFactory.from_request(test_object)

        self.mock_scm.post.return_value = mock_response.model_dump()  # noqa
        created_object = self.client.create(test_object.model_dump(exclude_unset=True))

        self.mock_scm.post.assert_called_once_with(  # noqa
            "/config/objects/v1/addresses",
            json=test_object.model_dump(exclude_unset=True),
        )
        assert str(created_object.id) == str(mock_response.id)
        assert created_object.name == test_object.name
        assert created_object.ip_wildcard == test_object.ip_wildcard
        assert created_object.folder == test_object.folder

    def test_create_object_error_handling(self):
        """
        Test error handling when the API returns an error during creation.
        """
        self.mock_scm.post.side_effect = Exception()  # noqa

        with pytest.raises(PydanticValidationError) as exc_info:
            self.client.create(data={"name": "test"})
        assert "1 validation error for AddressCreateModel" in str(exc_info.value)
        assert (
            "Value error, Value error, Exactly one of 'ip_netmask', 'ip_range', 'ip_wildcard', or 'fqdn' must be provided."
            in str(exc_info.value)
        )

    def test_create_generic_exception_handling(self):
        """
        Test handling of a generic exception during create.
        """
        self.mock_scm.post.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(PydanticValidationError) as exc_info:
            self.client.create(data={"name": "test"})
        assert "1 validation error for AddressCreateModel" in str(exc_info.value)
        assert (
            "Value error, Value error, Exactly one of 'ip_netmask', 'ip_range', 'ip_wildcard', or 'fqdn' must be provided."
            in str(exc_info.value)
        )

    def test_create_malformed_response_handling(self):
        """
        Test handling of malformed response from the API.
        """
        self.mock_scm.post.return_value = {"unexpected": "format"}  # noqa

        with pytest.raises(PydanticValidationError) as exc_info:
            self.client.create(data={"name": "test"})
        assert "1 validation error for AddressCreateModel" in str(exc_info.value)
        assert (
            "Value error, Value error, Exactly one of 'ip_netmask', 'ip_range', 'ip_wildcard', or 'fqdn' must be provided."
            in str(exc_info.value)
        )

    def test_create_api_error_handling(self, caplog):
        """
        Test handling of APIError during address creation.
        """
        # Create an APIError instance
        api_error = APIError("Test API Error")
        self.mock_scm.post.side_effect = api_error  # noqa

        # Test data
        test_data = {
            "name": "test-address",
            "folder": "Shared",
            "ip_netmask": "10.0.0.0/24",
        }

        with pytest.raises(APIError) as exc_info:
            self.client.create(test_data)

        # Verify the same error was re-raised
        assert exc_info.value is api_error


class TestAddressGet(TestAddressBase):
    """Tests for retrieving a specific Address object."""

    def test_get_object(self):
        """
        **Objective:** Test retrieving a specific object.
        """
        # Use AddressResponseFactory to create a mock response
        mock_response = AddressResponseFactory.with_ip_netmask(
            id="b44a8c00-7555-4021-96f0-d59deecd54e8",
            name="TestAddress",
            ip_netmask="10.0.0.0/24",
            folder="Shared",
        )

        # Mock the get method to return the mock_response's dictionary representation
        self.mock_scm.get.return_value = mock_response.model_dump()  # noqa
        object_id = mock_response.id  # Use the same ID as in the mock response

        get_object = self.client.get(object_id)

        self.mock_scm.get.assert_called_once_with(  # noqa
            f"/config/objects/v1/addresses/{object_id}"
        )
        assert isinstance(get_object, AddressResponseModel)
        assert get_object.id == mock_response.id
        assert get_object.name == mock_response.name
        assert get_object.ip_netmask == mock_response.ip_netmask
        assert get_object.folder == mock_response.folder

    def test_get_object_error_handling(self):
        """
        **Objective:** Test error handling during object retrieval.
        """
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        # Mock error response data using a realistic error response
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

        # Create a mock response object
        mock_response = MagicMock()
        mock_response.content = True  # Simulate that there is content
        mock_response.json.return_value = mock_error_response
        mock_response.status_code = 404

        # Create an HTTPError with the mock response
        mock_http_error = HTTPError(response=mock_response)

        # Set the side effect of the get method to raise the HTTPError
        self.mock_scm.get.side_effect = mock_http_error  # noqa

        with pytest.raises(ObjectNotPresentError) as exc_info:
            self.client.get(object_id)

        # Optionally, assert that the exception message is correct
        assert (
            str(exc_info.value)
            == "{'errorType': 'Object Not Present'} - HTTP error: 404 - API error: API_I00013"
        )

    def test_get_generic_exception_handling(self):
        """
        **Objective:** Test generic exception handling in get method.
        """
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        # Mock a generic exception without response
        self.mock_scm.get.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.get(object_id)

        # Assert that the exception message is correct
        assert str(exc_info.value) == "Generic error"


class TestAddressUpdate(TestAddressBase):
    """Tests for updating Address objects."""

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
            "name": "TestAddress",
            "folder": "Shared",
            "ip_netmask": "10.0.0.0/24",
            "description": "Updated description",
            "tag": [
                "tag1",
                "tag2",
            ],
        }

        # Expected payload should not include the ID
        expected_payload = {
            "name": "TestAddress",
            "folder": "Shared",
            "ip_netmask": "10.0.0.0/24",
            "description": "Updated description",
            "tag": [
                "tag1",
                "tag2",
            ],
        }

        # Mock response should include the ID
        mock_response = update_data.copy()
        self.mock_scm.put.return_value = mock_response  # noqa

        # Perform update
        updated_object = self.client.update(update_data)

        # Verify correct endpoint and payload
        self.mock_scm.put.assert_called_once_with(  # noqa
            f"/config/objects/v1/addresses/{update_data['id']}",
            json=expected_payload,  # Should not include ID
        )

        # Verify response model
        assert isinstance(updated_object, AddressResponseModel)
        assert isinstance(updated_object.id, UUID)  # Verify it's a UUID object
        assert updated_object.id == test_uuid  # Compare against UUID object
        assert (
            str(updated_object.id) == update_data["id"]
        )  # Compare string representations
        assert updated_object.name == "TestAddress"
        assert updated_object.ip_netmask == "10.0.0.0/24"
        assert updated_object.folder == "Shared"

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
            "name": "test-address",
            "folder": "Shared",
            "ip_netmask": "10.0.0.0/24",
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
        Test updating an object with invalid data.
        """
        with pytest.raises(APIError) as exc_info:
            self.client.update(
                data={"invalid": "data"},
            )
        assert "validation error" in str(exc_info.value)

    def test_update_generic_exception_handling(self):
        """
        Test generic exception handling during update.
        """
        self.mock_scm.put.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.update(data={"name": "test"})
        assert (
            str(exc_info.value)
            == "An unexpected error occurred: 1 validation error for AddressUpdateModel\n  Value error, Value error, Exactly one of 'ip_netmask', 'ip_range', 'ip_wildcard', or 'fqdn' must be provided. [type=value_error, input_value={'name': 'test'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.9/v/value_error"
        )


class TestAddressDelete(TestAddressBase):
    """Tests for deleting Address objects."""

    def test_delete_referenced_object(self):
        """
        Test deleting an object that is referenced elsewhere.
        """
        mock_error_response = {
            "_errors": [
                {
                    "code": "API_I00013",
                    "message": "Your configuration is not valid.",
                    "details": {"errorType": "Reference Error"},
                }
            ],
            "_request_id": "test-request-id",
        }
        self.mock_scm.delete.side_effect = Exception()  # noqa
        self.mock_scm.delete.side_effect.response = MagicMock()  # noqa
        self.mock_scm.delete.side_effect.response.json = MagicMock(  # noqa
            return_value=mock_error_response
        )

        with pytest.raises(APIError) as exc_info:
            self.client.delete("abcdefg")
        assert "Your configuration is not valid." in str(exc_info.value)

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
        Test generic exception handling during delete.
        """
        self.mock_scm.delete.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.delete("abcdefg")
        assert str(exc_info.value) == "An unexpected error occurred: Generic error"


class TestAddressFetch(TestAddressBase):
    """Tests for fetching Address objects by name."""

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
            "name": "dallas-desktop1",
            "folder": "Texas",
            "ip_netmask": "10.5.0.11",
            "description": "test123456",
            "tag": ["Decrypted"],
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        # Call the fetch method
        fetched_object = self.client.fetch(
            name=mock_response["name"],
            folder=mock_response["folder"],
        )

        # Assert that the GET request was made with the correct parameters
        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/addresses",
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
        assert fetched_object["tag"][0] == mock_response["tag"][0]

    def test_fetch_object_not_found(self):
        """
        Test fetching an object that does not exist.
        """
        mock_error_response = {
            "_errors": [
                {
                    "code": "API_I00013",
                    "message": "Object not found.",
                    "details": {"errorType": "Not Found"},
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
            self.client.fetch(name="nonexistent", folder="Shared")
        assert "Object not found." in str(exc_info.value)

    def test_fetch_empty_name(self):
        """
        Test fetching with an empty name parameter.
        """
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="", folder="Shared")
        assert "Field 'name' cannot be empty" in str(exc_info.value)

    def test_fetch_container_validation(self):
        """
        Test fetching with an empty folder parameter.
        """
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="test", folder="")
        assert "Field 'folder' cannot be empty" in str(exc_info.value)

    def test_fetch_object_unexpected_response_format(self):
        """
        Test fetching an object when the API returns an unexpected format.
        """
        self.mock_scm.get.return_value = {"unexpected": "format"}  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.fetch(name="test", folder="Shared")
        assert "Invalid response format: missing 'id' field" in str(exc_info.value)

    def test_fetch_validation_errors(self):
        """
        Test fetching with invalid parameters.
        """
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="test", folder="")
        assert "Field 'folder' cannot be empty" in str(exc_info.value)

    def test_fetch_generic_exception_handling(self):
        """
        Test generic exception handling during fetch.
        """
        self.mock_scm.get.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.fetch(name="test", folder="Shared")
        assert str(exc_info.value) == "An unexpected error occurred: Generic error"

    def test_fetch_response_format_handling(self):
        """
        Test handling of various response formats in fetch method.
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

    def test_fetch_invalid_format_raises_api_error(self):
        """
        Test fetching when response format is invalid (line 383).
        """
        # Mock response with invalid format (missing 'id' field)
        mock_response = {
            "name": "test-address",
            "folder": "Shared",
            # Missing 'id' field
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.fetch(name="test-address", folder="Shared")
        assert "Invalid response format: missing 'id' field" in str(exc_info.value)

    #
    # def test_fetch_error_response_handling(self, caplog):
    #     """
    #     Test handling of error response in fetch method.
    #     """
    #     # Mock an error response
    #     mock_error_response = {
    #         "_errors": [
    #             {
    #                 "message": "Test error",
    #                 "code": "API_I00013",
    #                 "details": {"errorType": "Invalid Object"},
    #             }
    #         ]
    #     }
    #     self.mock_scm.get.return_value = mock_error_response
    #
    #     with caplog.at_level(logging.ERROR, logger="scm"):
    #         with pytest.raises(InvalidObjectError) as exc_info:
    #             self.client.fetch(name="test-address", folder="Shared")
    #
    #     # Verify the error was logged
    #     assert "Error fetching address" in caplog.text
    #     # Optionally, check that the exception message is correct
    #     assert "Invalid Object" in str(exc_info.value)


class TestAddressTagValidation(TestAddressBase):
    """Tests for Address tag field validation."""

    def test_tag_string_to_list_conversion(self):
        """
        Test tag field validator converting a string to a list.

        **Objective:** Verify that a single string tag is properly converted to a list.
        **Workflow:**
            1. Creates an object with a single string tag
            2. Validates the tag is converted to a single-item list
        """
        data = {
            "name": "Test123",
            "folder": "Shared",
            "ip_netmask": "10.5.0.11",
            "tag": "TestTag",
        }
        model = AddressCreateModel(**data)
        assert isinstance(model.tag, list)
        assert model.tag == ["TestTag"]

    def test_tag_list_passed_through(self):
        """
        Test tag field validator passing through a list.

        **Objective:** Verify that a list of tags is properly handled.
        **Workflow:**
            1. Creates an object with multiple tags as a list
            2. Validates the tags remain as a list
        """
        data = {
            "name": "Test123",
            "folder": "Shared",
            "ip_netmask": "10.5.0.11",
            "tag": ["Tag1", "Tag2"],
        }
        model = AddressCreateModel(**data)
        assert isinstance(model.tag, list)
        assert model.tag == ["Tag1", "Tag2"]

    def test_tag_invalid_type(self):
        """
        Test tag field validator with invalid type.

        **Objective:** Verify that non-string/non-list tag values raise ValueError.
        **Workflow:**
            1. Attempts to create an object with an invalid tag type (dict)
            2. Validates that appropriate error is raised
        """
        data = {
            "name": "Test123",
            "folder": "Shared",
            "ip_netmask": "10.5.0.11",
            "tag": {"invalid": "type"},
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            AddressCreateModel(**data)
        assert "Tag must be a string or a list of strings" in str(exc_info.value)

    def test_tag_duplicate_items(self):
        """
        Test tag uniqueness validator.

        **Objective:** Verify that duplicate tags raise ValueError.
        **Workflow:**
            1. Attempts to create an object with duplicate tags
            2. Validates that appropriate error is raised
        """
        data = {
            "name": "Test123",
            "folder": "Shared",
            "ip_netmask": "10.5.0.11",
            "tag": ["TestTag", "TestTag"],
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            AddressCreateModel(**data)
        assert "List items must be unique" in str(exc_info.value)


class TestAddressListFilters(TestAddressBase):
    """Tests for filtering during listing Address objects."""

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
            "/config/objects/v1/addresses",
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
                    "id": "123e4567-e89b-12d3-a456-426655440000",
                    "name": "test-address",
                    "folder": "Shared",
                    "ip_netmask": "10.0.0.0/24",
                    "tag": ["tag1", "tag2"],
                }
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test invalid types filter (string instead of list)
        with pytest.raises(BadRequestError) as exc_info:
            self.client.list(folder="Shared", types="netmask")
        assert str(exc_info.value) == "'types' filter must be a list"

        # Test invalid values filter (string instead of list)
        with pytest.raises(BadRequestError) as exc_info:
            self.client.list(folder="Shared", values="10.0.0.0/24")
        assert str(exc_info.value) == "'values' filter must be a list"

        # Test invalid tags filter (string instead of list)
        with pytest.raises(BadRequestError) as exc_info:
            self.client.list(folder="Shared", tags="tag1")
        assert str(exc_info.value) == "'tags' filter must be a list"

        # Test invalid types filter (dict instead of list)
        with pytest.raises(BadRequestError) as exc_info:
            self.client.list(folder="Shared", types={"type": "netmask"})
        assert str(exc_info.value) == "'types' filter must be a list"

        # Test invalid values filter (dict instead of list)
        with pytest.raises(BadRequestError) as exc_info:
            self.client.list(folder="Shared", values={"value": "10.0.0.0/24"})
        assert str(exc_info.value) == "'values' filter must be a list"

        # Test invalid tags filter (dict instead of list)
        with pytest.raises(BadRequestError) as exc_info:
            self.client.list(folder="Shared", tags={"tag": "tag1"})
        assert str(exc_info.value) == "'tags' filter must be a list"

        # Test invalid types filter (integer instead of list)
        with pytest.raises(BadRequestError) as exc_info:
            self.client.list(folder="Shared", types=123)
        assert str(exc_info.value) == "'types' filter must be a list"

        # Test that valid list filters pass validation
        try:
            self.client.list(
                folder="Shared",
                types=["netmask"],
                values=["10.0.0.0/24"],
                tags=["tag1"],
            )
        except BadRequestError:
            pytest.fail("Unexpected BadRequestError raised with valid list filters")

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
                    "name": "test-address1",
                    "folder": "Shared",
                    "ip_netmask": "10.0.0.0/24",
                    "tag": ["tag1", "tag2"],
                },
                {
                    "id": "223e4567-e89b-12d3-a456-426655440000",
                    "name": "test-address2",
                    "folder": "Shared",
                    "ip_range": "10.0.0.1-10.0.0.10",
                    "tag": ["tag2", "tag3"],
                },
                {
                    "id": "323e4567-e89b-12d3-a456-426655440000",
                    "name": "test-address3",
                    "folder": "Shared",
                    "fqdn": "test.example.com",
                    "tag": ["tag1", "tag3"],
                },
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test combining types and tags filters
        filtered_objects = self.client.list(
            folder="Shared",
            types=["netmask"],
            tags=["tag1"],
        )
        assert len(filtered_objects) == 1
        assert filtered_objects[0].name == "test-address1"

        # Test combining values and tags filters
        filtered_objects = self.client.list(
            folder="Shared",
            values=["10.0.0.0/24"],
            tags=["tag2"],
        )
        assert len(filtered_objects) == 1
        assert filtered_objects[0].name == "test-address1"

        # Test all filters together
        filtered_objects = self.client.list(
            folder="Shared",
            types=["netmask"],
            values=["10.0.0.0/24"],
            tags=["tag1"],
        )
        assert len(filtered_objects) == 1
        assert filtered_objects[0].name == "test-address1"

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
                    "name": "test-address",
                    "folder": "Shared",
                    "ip_netmask": "10.0.0.0/24",
                    "tag": ["tag1"],
                }
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Empty lists should result in no matches
        filtered_objects = self.client.list(
            folder="Shared",
            types=[],
        )
        assert len(filtered_objects) == 0

        filtered_objects = self.client.list(
            folder="Shared",
            values=[],
        )
        assert len(filtered_objects) == 0

        filtered_objects = self.client.list(
            folder="Shared",
            tags=[],
        )
        assert len(filtered_objects) == 0

    def test_list_empty_folder_error(self):
        """
        Test that empty folder raises appropriate error.
        """
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.list(folder="")
        assert "Field 'folder' cannot be empty" in str(exc_info.value)

    def test_list_multiple_containers_error(self):
        """
        Test validation of container parameters.
        """
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="folder1", snippet="snippet1")
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_list_error_handling(self):
        """
        Test error handling in list operation.
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
            2. Verifies the original exception is re-raised
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

    def test_apply_filters_invalid_types_filter(self):
        """
        Test _apply_filters with invalid types filter (line 367).
        """
        mock_addresses = []  # Empty list as we'll raise before using it
        invalid_filters = {"types": "not-a-list"}  # String instead of list

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_addresses, invalid_filters)
        assert "'types' filter must be a list" in str(exc_info.value)


# -------------------- End of Test Classes --------------------
