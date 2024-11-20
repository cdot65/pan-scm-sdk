# tests/scm/config/objects/test_address.py
import logging
# Standard library imports
from unittest.mock import MagicMock

# External libraries
import pytest
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
    AddressResponseModel,
)
from tests.factories import (
    AddressResponseFactory,
    AddressCreateApiFactory,
    AddressUpdateApiFactory,
)
from tests.utils import raise_mock_http_error


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


class TestAddressList(TestAddressBase):
    """Tests for listing Address objects."""

    def test_list_valid(self):
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

    def test_list_folder_empty_error(self):
        """Test that empty folder raises appropriate error."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="E003",
            message='"folder" is not allowed to be empty',
            error_type="Missing Query Parameter",
        )

        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.list(folder="")

        error_msg = str(exc_info.value)
        assert (
            "['\"folder\" is not allowed to be empty'] - HTTP error: 400 - API error: E003"
            in error_msg
        )

    def test_list_folder_nonexistent_error(self):
        """Test error handling in list operation."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Listing failed",
            error_type="Operation Impossible",
        )

        with pytest.raises(ObjectNotPresentError) as exc_info:
            self.client.list(folder="NonexistentFolder")

        error_msg = str(exc_info.value)
        assert (
            "{'errorType': 'Operation Impossible'} - HTTP error: 404 - API error: API_I00013"
            in error_msg
        )

    def test_list_container_missing_error(self):
        """
        Test that InvalidObjectError is raised when no container parameter is provided.
        """
        # Use the utility function to create the mock HTTP error
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="E003",
            message="Exactly one of 'folder', 'snippet', or 'device' must be provided.",
            error_type="Invalid Object",
        )

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list()
        error_msg = str(exc_info.value)
        assert "HTTP error: 400 - API error: E003" in error_msg

    def test_list_container_multiple_error(self):
        """Test validation of container parameters."""
        # Use the utility function to create the mock HTTP error
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="E003",
            message="Multiple container types provided",
            error_type="Invalid Object",
        )

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="folder1", snippet="snippet1")

        error_msg = str(exc_info.value)
        assert "HTTP error: 400 - API error: E003" in error_msg

    def test_list_filters_valid(self):
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

    def test_list_filters_lists_empty(self):
        """Test behavior with empty filter lists."""
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

    def test_list_filters_types(self):
        """Test validation of filter types in list method."""
        # Mock response for successful case
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

        # Test invalid types filter (string instead of list)
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="E003",
            message="'types' filter must be a list",
            error_type="Invalid Query Parameter",
        )
        with pytest.raises(BadRequestError) as exc_info:
            self.client.list(folder="Shared", types="netmask")
        assert (
            "{'errorType': 'Invalid Query Parameter'} - HTTP error: 400 - API error: E003"
            in str(exc_info.value)
        )

        # Reset side effect for next test
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="E003",
            message="'values' filter must be a list",
            error_type="Invalid Query Parameter",
        )
        with pytest.raises(BadRequestError) as exc_info:
            self.client.list(folder="Shared", values="10.0.0.0/24")
        assert (
            "{'errorType': 'Invalid Query Parameter'} - HTTP error: 400 - API error: E003"
            in str(exc_info.value)
        )

        # Reset side effect for next test
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="E003",
            message="'tags' filter must be a list",
            error_type="Invalid Query Parameter",
        )
        with pytest.raises(BadRequestError) as exc_info:
            self.client.list(folder="Shared", tags="tag1")
        assert (
            "{'errorType': 'Invalid Query Parameter'} - HTTP error: 400 - API error: E003"
            in str(exc_info.value)
        )

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

    def test_list_filters_types_validation(self):
        """Test validation of 'types' filter specifically."""
        mock_addresses = []

        # Test with string instead of list
        invalid_filters = {"types": "type1"}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_addresses, invalid_filters)

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        assert error.error_code == "E003"
        assert "{'errorType': 'Invalid Object'}" in str(error)

        # Test with dict instead of list
        invalid_filters = {"types": {"types": "type1"}}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_addresses, invalid_filters)

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        assert "{'errorType': 'Invalid Object'}" in str(error)

    def test_list_filters_tags_validation(self):
        """Test validation of 'tags' filter specifically."""
        mock_addresses = []

        # Test with string instead of list
        invalid_filters = {"tags": "tag1"}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_addresses, invalid_filters)

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        assert error.error_code == "E003"
        assert "{'errorType': 'Invalid Object'}" in str(error)

        # Test with dict instead of list
        invalid_filters = {"tags": {"tag": "tag1"}}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_addresses, invalid_filters)

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        assert "{'errorType': 'Invalid Object'}" in str(error)

    def test_list_filters_values_validation(self):
        """Test validation of 'values' filter specifically."""
        mock_addresses = []

        # Test with string instead of list
        invalid_filters = {"values": "10.0.0.0/24"}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_addresses, invalid_filters)

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        assert error.error_code == "E003"
        assert error.http_status_code == 500
        assert "{'errorType': 'Invalid Object'}" in str(error)

        # Test with dict instead of list
        invalid_filters = {"values": {"value": "10.0.0.0/24"}}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_addresses, invalid_filters)

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        assert error.error_code == "E003"
        assert error.http_status_code == 500
        assert "{'errorType': 'Invalid Object'}" in str(error)

    def test_list_filters_combinations(self):
        """Test different combinations of valid filters."""
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

    def test_list_response_invalid_format(self):
        """
        Test that InvalidObjectError is raised when the response is not a dictionary.
        """
        # Mock the API client to return a non-dictionary response
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Shared")

        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500
        assert "HTTP error: 500 - API error: E003" in str(exc_info.value)

    def test_list_response_invalid_data_field_missing(self):
        """
        Test that InvalidObjectError is raised when API returns response with missing data field.

        This tests the case where the API response is a dictionary but missing the required 'data' field,
        expecting an InvalidObjectError with specific error details.
        """
        # Mock the API to return a dictionary without 'data' field
        self.mock_scm.get.return_value = {"wrong_field": "value"}  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Shared")

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        assert error.error_code == "E003"
        assert error.http_status_code == 500
        assert "HTTP error: 500 - API error: E003" in str(error)

    def test_list_response_invalid_data_field_type(self):
        """
        Test that InvalidObjectError is raised when API returns non-list data field.

        This tests the case where the API response's 'data' field is not a list,
        expecting an InvalidObjectError with specific error details.
        """
        # Mock the API to return a response where 'data' is not a list
        self.mock_scm.get.return_value = {"data": "not a list"}  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Shared")

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        assert error.error_code == "E003"
        assert error.http_status_code == 500

    def test_list_response_no_content(self):
        """Test that an HTTPError without response content in list() re-raises the exception."""
        mock_response = MagicMock()
        mock_response.content = None  # Simulate no content
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.list(folder="Shared")

    def test_list_server_error(self):
        """Test generic exception handling in list method."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )

        with pytest.raises(APIError) as exc_info:
            self.client.list(folder="Shared")

        error_msg = str(exc_info.value)
        assert (
            "{'errorType': 'Internal Error'} - HTTP error: 500 - API error: E003"
            in error_msg
        )


class TestAddressCreate(TestAddressBase):
    """Tests for creating Address objects."""

    def test_create_valid_type_ip_netmask(self):
        """Test creating an object with ip_netmask."""
        test_object = AddressCreateApiFactory.with_ip_netmask()
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

    def test_create_valid_type_fqdn(self):
        """Test creating an object of type fqdn."""
        test_object = AddressCreateApiFactory.with_fqdn()
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

    def test_create_valid_type_ip_range(self):
        """Test creating an object of type ip_range."""
        test_object = AddressCreateApiFactory.with_ip_range()
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

    def test_create_valid_type_ip_wildcard(self):
        """Test creating an object of type ip_wildcard."""
        test_object = AddressCreateApiFactory.with_ip_wildcard()
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

    def test_create_no_response_content(self):
        """Test create method when HTTP error has no response content."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_error = HTTPError(response=mock_response)
        self.mock_scm.post.side_effect = mock_error  # noqa

        with pytest.raises(HTTPError):
            self.client.create(
                {"name": "test", "ip_netmask": "10.0.0.0/24", "folder": "test"}
            )

    def test_create_http_error_with_response(self):
        """
        Test that an HTTPError with response content in create() triggers ErrorHandler.raise_for_error().
        """
        test_data = {
            "name": "test-address",
            "folder": "Shared",
            "ip_netmask": "10.0.0.0/24",
        }

        # Mock error response data
        mock_error_response = {
            "_errors": [
                {
                    "code": "API_I00013",
                    "message": "Create failed",
                    "details": {"errorType": "Malformed Command"},
                }
            ],
            "_request_id": "test-request-id",
        }

        # Create a mock response object with content
        mock_response = MagicMock()
        mock_response.content = True  # Simulate that there is content
        mock_response.json.return_value = mock_error_response
        mock_response.status_code = 400

        # Create an HTTPError with the mock response
        mock_http_error = HTTPError(response=mock_response)

        # Set the side effect of the post method to raise the HTTPError
        self.mock_scm.post.side_effect = mock_http_error  # noqa

        with pytest.raises(MalformedCommandError) as exc_info:
            self.client.create(test_data)

        # Verify that the exception message contains the expected error
        assert (
            "{'errorType': 'Malformed Command'} - HTTP error: 400 - API error: API_I00013"
            in str(exc_info.value)
        )


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

    def test_get_http_error_no_response_content(self, caplog):
        """
        Test that an HTTPError without response content in get() logs an error and re-raises the exception.
        """
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        # Create a mock response object without content
        mock_response = MagicMock()
        mock_response.content = None  # Simulate no content
        mock_response.status_code = 500

        # Create an HTTPError with the mock response
        mock_http_error = HTTPError(response=mock_response)

        # Set the side effect of the get method to raise the HTTPError
        self.mock_scm.get.side_effect = mock_http_error  # noqa

        with caplog.at_level(logging.ERROR, logger=self.client.logger.name):
            with pytest.raises(HTTPError):
                self.client.get(object_id)

        # Check that the log message was emitted
        assert "No response content available for error parsing." in caplog.text


class TestAddressUpdate(TestAddressBase):
    """Tests for updating Address objects."""

    def test_update_object(self):
        """
        **Objective:** Test updating an object.
        """
        # Use AddressUpdateFactory to create the update data
        update_data = AddressUpdateApiFactory.with_ip_netmask(
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
        update_data = AddressUpdateApiFactory.with_ip_netmask(
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

    def test_update_no_response_content(self):
        """Test update method when HTTP error has no response content."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_error = HTTPError(response=mock_response)
        self.mock_scm.put.side_effect = mock_error  # noqa

        with pytest.raises(HTTPError):
            self.client.update(
                {"id": "test-id", "name": "test", "ip_netmask": "10.0.0.0/24"}
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

    def test_delete_http_error_no_response_content(self, caplog):
        """
        Test that an HTTPError without response content in delete() logs an error and re-raises the exception.
        """
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        # Create a mock response object without content
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        # Create an HTTPError with the mock response
        mock_http_error = HTTPError(response=mock_response)

        # Set the side effect of the delete method to raise the HTTPError
        self.mock_scm.delete.side_effect = mock_http_error  # noqa

        with caplog.at_level(logging.ERROR, logger=self.client.logger.name):
            with pytest.raises(HTTPError):
                self.client.delete(object_id)

        # Check that the log message was emitted
        assert "No response content available for error parsing." in caplog.text

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

    def test_delete_no_response_content(self):
        """Test delete method when HTTP error has no response content."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_error = HTTPError(response=mock_response)
        self.mock_scm.delete.side_effect = mock_error  # noqa

        with pytest.raises(HTTPError):
            self.client.delete("test-id")


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

    def test_fetch_missing_id_field(self):
        """
        Test that InvalidObjectError is raised when the response is missing 'id' field.
        """
        # Mock response without 'id' field
        mock_response = {
            "name": "test-address",
            "folder": "Shared",
            "ip_netmask": "10.0.0.0/24",
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-address", folder="Shared")

        assert "HTTP error: 500 - API error: E003" in str(exc_info.value)
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500

    def test_fetch_http_error_no_response_content(self, caplog):
        """
        Test that an HTTPError without response content in fetch() logs an error and re-raises the exception.
        """
        # Create a mock response object without content
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        # Create an HTTPError with the mock response
        mock_http_error = HTTPError(response=mock_response)

        # Set the side effect of the get method to raise the HTTPError
        self.mock_scm.get.side_effect = mock_http_error  # noqa

        with caplog.at_level(logging.ERROR, logger=self.client.logger.name):
            with pytest.raises(HTTPError):
                self.client.fetch(name="test-address", folder="Shared")

        # Check that the log message was emitted
        assert "No response content available for error parsing." in caplog.text

    def test_fetch_response_contains_errors(self):
        """
        Test that ErrorHandler.raise_for_error is called when response contains '_errors' field.
        """
        # Mock response with '_errors' field
        mock_response = {
            "_errors": [
                {
                    "code": "E003",
                    "message": "Invalid request",
                    "details": {"errorType": "Invalid Object"},
                }
            ],
            "_request_id": "test-request-id",
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-address", folder="Shared")

        assert (
            "{'errorType': 'Invalid Object'} - HTTP error: 400 - API error: E003"
            in str(exc_info.value)
        )
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 400

    def test_fetch_no_container_provided(self):
        """
        Test that InvalidObjectError is raised when no container parameter is provided.
        """
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-address")
        assert "HTTP error: 400 - API error: E003" in str(exc_info.value)
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 400

    def test_fetch_multiple_containers_provided(self):
        """
        Test that InvalidObjectError is raised when multiple container parameters are provided.
        """
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(
                folder="Shared", snippet="TestSnippet", name="test-address"
            )
        assert "HTTP error: 400 - API error: E003" in str(exc_info.value)
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 400

    def test_list_invalid_response_format(self):
        """
        Test that InvalidObjectError is raised when the response is not a dictionary.
        """
        # Mock the API client to return a non-dictionary response
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(folder="Shared", name="test123")

        assert "HTTP error: 500 - API error: E003" in str(exc_info.value)
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500
