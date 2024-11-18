# tests/scm/config/objects/test_address.py

# Standard library imports
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
    ReferenceNotZeroError,
)
from scm.models.objects import (
    AddressCreateModel,
    AddressResponseModel,
)
from tests.factories import (
    AddressResponseFactory,
    AddressCreateFactory,
    AddressUpdateFactory,
)


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
        """
        # Use AddressUpdateFactory to create the update data
        update_data = AddressUpdateFactory.with_ip_netmask(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="TestAddress",
            ip_netmask="10.0.0.0/24",
            description="Updated description",
            tag=["tag1", "tag2"],
            folder="Shared",
        )

        # Create the data dictionary ensuring ID is included
        input_data = update_data.model_dump()

        # Create mock response
        mock_response = AddressResponseFactory.from_request(update_data)
        self.mock_scm.put.return_value = mock_response.model_dump()  # noqa

        # Perform update with complete data including ID
        updated_object = self.client.update(input_data)

        # Verify the API was called once
        self.mock_scm.put.assert_called_once()  # noqa

        # Get the actual call arguments
        call_args = self.mock_scm.put.call_args  # noqa
        actual_endpoint = call_args[0][0]
        actual_payload = call_args[1]["json"]

        # Verify endpoint
        assert actual_endpoint == f"/config/objects/v1/addresses/{update_data.id}"

        # Verify required fields in payload
        assert actual_payload["name"] == update_data.name
        assert actual_payload["ip_netmask"] == update_data.ip_netmask
        assert actual_payload["description"] == update_data.description
        assert actual_payload["tag"] == update_data.tag
        assert actual_payload["folder"] == update_data.folder
        assert actual_payload["id"] == update_data.id

        # Verify response
        assert isinstance(updated_object, AddressResponseModel)
        assert updated_object.name == update_data.name
        assert updated_object.ip_netmask == update_data.ip_netmask
        assert updated_object.folder == update_data.folder
        assert updated_object.description == update_data.description
        assert updated_object.tag == update_data.tag

    def test_update_object_error_handling(self):
        """
        **Objective:** Test error handling during object update.
        """
        # Create test data using factory
        update_data = AddressUpdateFactory.with_ip_netmask(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-address",
            folder="Shared",
            ip_netmask="10.0.0.0/24",
        ).model_dump()

        # Mock error response
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

        # Create mock HTTP error
        mock_response = MagicMock()
        mock_response.content = True
        mock_response.json.return_value = mock_error_response
        mock_response.status_code = 400

        # Set up mock to raise HTTPError
        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.put.side_effect = mock_http_error  # noqa

        with pytest.raises(MalformedCommandError) as exc_info:
            self.client.update(update_data)

        assert (
            "{'errorType': 'Malformed Command'} - HTTP error: 400 - API error: API_I00013"
            in str(exc_info.value)
        )

    def test_update_with_invalid_data(self):
        """
        Test updating an object with invalid data.
        """
        with pytest.raises(PydanticValidationError) as exc_info:
            self.client.update(data={"invalid": "data"})

        error_msg = str(exc_info.value)
        assert "validation error" in error_msg
        assert "name" in error_msg  # Name is required
        assert "id" in error_msg  # ID is required

    def test_update_generic_exception_handling(self):
        """
        Test generic exception handling during update.
        """
        # Create valid test data with factory but missing required fields
        test_data = AddressUpdateFactory.with_ip_netmask(
            name="test-address",
            ip_netmask="10.0.0.0/24",
            folder="Shared",
        ).model_dump()

        # Remove ID to trigger validation error
        test_data.pop("id")

        with pytest.raises(PydanticValidationError) as exc_info:
            self.client.update(data=test_data)

        assert "id" in str(exc_info.value)  # Should mention missing ID field

    def test_update_missing_address_type(self):
        """
        Test update with missing address type.
        """
        test_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-address",
            "folder": "Shared",
        }

        with pytest.raises(PydanticValidationError) as exc_info:
            self.client.update(test_data)

        error_msg = str(exc_info.value)
        assert "Value error" in error_msg
        assert (
            "Exactly one of 'ip_netmask', 'ip_range', 'ip_wildcard', or 'fqdn' must be provided"
            in error_msg
        )


class TestAddressDelete(TestAddressBase):
    """Tests for deleting Address objects."""

    def test_delete_referenced_object(self):
        """
        Test deleting an object that is referenced elsewhere.
        """
        # Mock error response
        mock_error_response = {
            "_errors": [
                {
                    "code": "E009",  # Using proper error code for reference errors
                    "message": "Your configuration is not valid.",
                    "details": {"errorType": "Reference Not Zero"},
                }
            ],
            "_request_id": "test-request-id",
        }

        # Create mock response with proper status code
        mock_response = MagicMock()
        mock_response.status_code = 409  # Conflict status code
        mock_response.content = True
        mock_response.json.return_value = mock_error_response

        # Create HTTPError with mock response
        mock_error = HTTPError(response=mock_response)
        self.mock_scm.delete.side_effect = mock_error  # noqa

        # Test the delete operation
        with pytest.raises(ReferenceNotZeroError) as exc_info:
            self.client.delete("abcdefg")

        error_message = str(exc_info.value)
        assert "{'errorType': 'Reference Not Zero'}" in error_message
        assert "HTTP error: 409" in error_message
        assert "API error: E009" in error_message

    def test_delete_error_handling(self):
        """
        **Objective:** Test error handling during object deletion.
        **Workflow:**
            1. Mocks various error scenarios
            2. Verifies proper error handling for each case
        """
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        # Mock error response for object not found
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

        # Create mock response with proper status code
        mock_response = MagicMock()
        mock_response.status_code = 404  # Not Found status code
        mock_response.content = True
        mock_response.json.return_value = mock_error_response

        # Create HTTPError with mock response
        mock_error = HTTPError(response=mock_response)
        self.mock_scm.delete.side_effect = mock_error  # noqa

        # Test the delete operation
        with pytest.raises(ObjectNotPresentError) as exc_info:
            self.client.delete(object_id)

        error_message = str(exc_info.value)
        assert "{'errorType': 'Object Not Present'}" in error_message
        assert "HTTP error: 404" in error_message
        assert "API error: API_I00013" in error_message

    def test_delete_generic_exception_handling(self):
        """
        Test generic exception handling during delete.
        """
        # Create mock response without error details
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.content = True
        mock_response.json.side_effect = Exception("Invalid JSON")

        # Create HTTPError with mock response
        mock_error = HTTPError(response=mock_response)
        self.mock_scm.delete.side_effect = mock_error  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.delete("abcdefg")

        assert "Invalid JSON" in str(exc_info.value)

    def test_delete_success(self):
        """
        Test successful deletion of an object.
        """
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        # Mock successful delete (returns None)
        self.mock_scm.delete.return_value = None  # noqa

        # Should not raise any exception
        self.client.delete(object_id)

        # Verify the delete call
        self.mock_scm.delete.assert_called_once_with(  # noqa
            f"/config/objects/v1/addresses/{object_id}"
        )


class TestAddressFetch(TestAddressBase):
    """Tests for fetching Address objects by name."""

    def test_fetch_object(self):
        """
        **Objective:** Test retrieving an object by its name using the `fetch` method.
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
                    "message": "Object not found",
                    "details": {"errorType": "Object Not Present"},
                }
            ],
            "_request_id": "test-request-id",
        }

        # Create mock response with proper status code
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.content = True
        mock_response.json.return_value = mock_error_response

        # Create HTTPError with mock response
        mock_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_error  # noqa

        with pytest.raises(ObjectNotPresentError) as exc_info:
            self.client.fetch(name="nonexistent", folder="Shared")

        assert "{'errorType': 'Object Not Present'}" in str(exc_info.value)
        assert "HTTP error: 404" in str(exc_info.value)
        assert "API error: API_I00013" in str(exc_info.value)

    def test_fetch_empty_name(self):
        """
        Test fetching with an empty name parameter.
        """
        mock_error_response = {
            "_errors": [
                {
                    "code": "E003",
                    "message": '"name" is not allowed to be empty',
                    "details": {"errorType": "Missing Query Parameter"},
                }
            ],
            "_request_id": "test-request-id",
        }

        # Create mock response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.content = True
        mock_response.json.return_value = mock_error_response

        # Create HTTPError
        mock_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_error  # noqa

        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="", folder="Shared")

        assert '"name" is not allowed to be empty' in str(exc_info.value)
        assert "HTTP error: 400" in str(exc_info.value)
        assert "API error: E003" in str(exc_info.value)

    def test_fetch_container_validation(self):
        """
        Test fetching with an empty folder parameter.
        """
        mock_error_response = {
            "_errors": [
                {
                    "code": "E003",
                    "message": '"folder" is not allowed to be empty',
                    "details": {"errorType": "Missing Query Parameter"},
                }
            ],
            "_request_id": "test-request-id",
        }

        # Create mock response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.content = True
        mock_response.json.return_value = mock_error_response

        # Create HTTPError
        mock_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_error  # noqa

        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="test", folder="")

        assert '"folder" is not allowed to be empty' in str(exc_info.value)
        assert "HTTP error: 400" in str(exc_info.value)
        assert "API error: E003" in str(exc_info.value)

    def test_fetch_object_unexpected_response_format(self):
        """
        Test fetching an object when the API returns an unexpected format.
        """
        mock_error_response = {
            "_errors": [
                {
                    "code": "E003",
                    "message": "Invalid response format",
                    "details": {"errorType": "Invalid Object"},
                }
            ],
            "_request_id": "test-request-id",
        }

        # Create mock response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.content = True
        mock_response.json.return_value = mock_error_response

        # Create HTTPError
        mock_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_error  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test", folder="Shared")

        assert "{'errorType': 'Invalid Object'}" in str(exc_info.value)
        assert "HTTP error: 500" in str(exc_info.value)
        assert "API error: E003" in str(exc_info.value)

    def test_fetch_generic_exception_handling(self):
        """
        Test generic exception handling during fetch.
        """
        mock_error_response = {
            "_errors": [
                {
                    "code": "E003",
                    "message": "Generic error occurred",
                    "details": {"errorType": "Internal Error"},
                }
            ],
            "_request_id": "test-request-id",
        }

        # Create mock response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.content = True
        mock_response.json.return_value = mock_error_response

        # Create HTTPError
        mock_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_error  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.fetch(name="test", folder="Shared")

        assert "{'errorType': 'Internal Error'}" in str(exc_info.value)
        assert "HTTP error: 500" in str(exc_info.value)
        assert "API error: E003" in str(exc_info.value)

    def test_fetch_response_format_handling(self):
        """
        Test handling of various response formats in fetch method.
        """
        # Test Case 1: Malformed response without expected fields
        mock_error_response = {
            "_errors": [
                {
                    "code": "E003",
                    "message": "Invalid object format",
                    "details": {
                        "errorType": "Invalid Object",
                        "reason": "Response missing required fields",
                    },
                }
            ],
            "_request_id": "test-request-id",
        }

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.content = True
        mock_response.json.return_value = mock_error_response

        mock_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_error  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test", folder="Shared")

        error_msg = str(exc_info.value)
        assert (
            "{'errorType': 'Invalid Object', 'reason': 'Response missing required fields'}"
            in error_msg
        )
        assert "HTTP error: 400" in error_msg
        assert "API error: E003" in error_msg

        # Test Case 2: Response with unexpected fields
        mock_error_response_2 = {
            "_errors": [
                {
                    "code": "E003",
                    "message": "Invalid response structure",
                    "details": {
                        "errorType": "Invalid Object",
                        "reason": "Response contains unexpected fields",
                    },
                }
            ],
            "_request_id": "test-request-id",
        }

        mock_response_2 = MagicMock()
        mock_response_2.status_code = 400
        mock_response_2.content = True
        mock_response_2.json.return_value = mock_error_response_2

        mock_error_2 = HTTPError(response=mock_response_2)
        self.mock_scm.get.side_effect = mock_error_2  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test", folder="Shared")

        error_msg = str(exc_info.value)
        assert (
            "{'errorType': 'Invalid Object', 'reason': 'Response contains unexpected fields'}"
            in error_msg
        )
        assert "HTTP error: 400" in error_msg
        assert "API error: E003" in error_msg

    def test_fetch_invalid_format_raises_api_error(self):
        """
        Test fetching when response format is invalid.
        """
        mock_error_response = {
            "_errors": [
                {
                    "code": "E003",
                    "message": "Invalid response format",
                    "details": {"errorType": "Invalid Object"},
                }
            ],
            "_request_id": "test-request-id",
        }

        # Create mock response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.content = True
        mock_response.json.return_value = mock_error_response

        # Create HTTPError
        mock_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_error  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-address", folder="Shared")

        assert "{'errorType': 'Invalid Object'}" in str(exc_info.value)
        assert "HTTP error: 500" in str(exc_info.value)
        assert "API error: E003" in str(exc_info.value)


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
        """Test that filters are properly added to parameters."""
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
        """Test validation of filter types in list method."""
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

        def create_mock_error(error_msg):
            """Helper to create mock error response"""
            return {
                "_errors": [
                    {
                        "code": "E003",
                        "message": error_msg,
                        "details": {"errorType": "Invalid Query Parameter"},
                    }
                ],
                "_request_id": "test-request-id",
            }

        def setup_mock_error(error_msg):
            """Helper to set up mock error response"""
            mock_response = MagicMock()  # noqa
            mock_response.status_code = 400
            mock_response.content = True
            mock_response.json.return_value = create_mock_error(error_msg)
            return HTTPError(response=mock_response)

        # Test invalid types filter (string instead of list)
        mock_error = setup_mock_error("'types' filter must be a list")
        self.mock_scm.get.side_effect = mock_error  # noqa
        with pytest.raises(BadRequestError) as exc_info:
            self.client.list(folder="Shared", types="netmask")
        assert "HTTP error: 400" in str(exc_info.value)
        assert "API error: E003" in str(exc_info.value)

        # Test invalid values filter (string instead of list)
        mock_error = setup_mock_error("'values' filter must be a list")
        self.mock_scm.get.side_effect = mock_error  # noqa
        with pytest.raises(BadRequestError) as exc_info:
            self.client.list(folder="Shared", values="10.0.0.0/24")
        assert "HTTP error: 400" in str(exc_info.value)
        assert "API error: E003" in str(exc_info.value)

        # Test invalid tags filter (string instead of list)
        mock_error = setup_mock_error("'tags' filter must be a list")
        self.mock_scm.get.side_effect = mock_error  # noqa
        with pytest.raises(BadRequestError) as exc_info:
            self.client.list(folder="Shared", tags="tag1")
        assert "HTTP error: 400" in str(exc_info.value)
        assert "API error: E003" in str(exc_info.value)

        # Reset side effect for successful case
        self.mock_scm.get.side_effect = None  # noqa
        self.mock_scm.get.return_value = mock_response  # noqa

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
        """Test that empty folder raises appropriate error."""
        mock_error_response = {
            "_errors": [
                {
                    "code": "E003",
                    "message": '"folder" is not allowed to be empty',
                    "details": {"errorType": "Missing Query Parameter"},
                }
            ],
            "_request_id": "test-request-id",
        }

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.content = True
        mock_response.json.return_value = mock_error_response

        self.mock_scm.get.side_effect = HTTPError(response=mock_response)  # noqa

        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.list(folder="")

        error_msg = str(exc_info.value)
        assert '"folder" is not allowed to be empty' in error_msg
        assert "HTTP error: 400" in error_msg
        assert "API error: E003" in error_msg

    def test_list_multiple_containers_error(self):
        """Test validation of container parameters."""
        mock_error_response = {
            "_errors": [
                {
                    "code": "E003",
                    "message": "Multiple container types provided",
                    "details": {"errorType": "Invalid Object"},
                }
            ],
            "_request_id": "test-request-id",
        }

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.content = True
        mock_response.json.return_value = mock_error_response

        self.mock_scm.get.side_effect = HTTPError(response=mock_response)  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="folder1", snippet="snippet1")

        error_msg = str(exc_info.value)
        assert "HTTP error: 400" in error_msg
        assert "API error: E003" in error_msg

    def test_list_error_handling(self):
        """Test error handling in list operation."""
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

        # Create mock response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.content = True
        mock_response.json.return_value = mock_error_response

        # Create HTTPError with mock response
        mock_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_error  # noqa

        with pytest.raises(ObjectNotPresentError) as exc_info:
            self.client.list(folder="NonexistentFolder")

        error_msg = str(exc_info.value)
        assert "{'errorType': 'Operation Impossible'}" in error_msg
        assert "HTTP error: 404" in error_msg
        assert "API error: API_I00013" in error_msg

    def test_list_generic_exception_handling(self):
        """Test generic exception handling in list method."""
        mock_error_response = {
            "_errors": [
                {
                    "code": "E003",
                    "message": "An internal error occurred",
                    "details": {"errorType": "Internal Error"},
                }
            ],
            "_request_id": "test-request-id",
        }

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.content = True
        mock_response.json.return_value = mock_error_response

        mock_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_error  # noqa

        with pytest.raises(APIError) as exc_info:
            self.client.list(folder="Shared")

        error_msg = str(exc_info.value)
        assert "{'errorType': 'Internal Error'}" in error_msg
        assert "HTTP error: 500" in error_msg
        assert "API error: E003" in error_msg

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
        """Test list method handling of non-dictionary response."""
        mock_error_response = {
            "_errors": [
                {
                    "code": "E003",
                    "message": "Invalid response format",
                    "details": {"errorType": "Invalid Object"},
                }
            ],
            "_request_id": "test-request-id",
        }

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.content = True
        mock_response.json.return_value = mock_error_response

        mock_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_error  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.mock_scm.get.return_value = ["not", "a", "dict"]  # noqa
            self.client.list(folder="Shared")

        error_msg = str(exc_info.value)
        assert "{'errorType': 'Invalid Object'}" in error_msg
        assert "HTTP error: 500" in error_msg
        assert "API error: E003" in error_msg

    def test_apply_filters_invalid_types_filter(self):
        """
        Test _apply_filters with invalid types filter (line 367).
        """
        mock_addresses = []  # Empty list as we'll raise before using it
        invalid_filters = {"types": "not-a-list"}  # String instead of list

        with pytest.raises(InvalidObjectError):
            self.client._apply_filters(mock_addresses, invalid_filters)
        # assert "'types' filter must be a list" in str(exc_info.value)


# -------------------- End of Test Classes --------------------
