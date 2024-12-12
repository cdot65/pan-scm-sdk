# tests/scm/config/objects/test_address.py

# Standard library imports
from unittest.mock import MagicMock

# External libraries
import pytest
from requests.exceptions import HTTPError

# Local SDK imports
from scm.config.objects import Address
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
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
            "{'field': 'folder', 'error': '\"folder\" is not allowed to be empty'} - HTTP error: 400 - API error: E003"
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

        with pytest.raises(HTTPError):
            self.client.list(folder="NonexistentFolder")

    def test_list_container_missing_error(self):
        """
        Test that InvalidObjectError is raised when no container parameter is provided.
        """
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

        self.client.list(folder="Texas", **filters)

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/addresses",
            params={
                "limit": 10000,
                "folder": "Texas",
            },
        )

    def test_list_filters_lists_empty(self):
        """Test behavior with empty filter lists."""
        mock_response = {
            "data": [
                {
                    "id": "123e4567-e89b-12d3-a456-426655440000",
                    "name": "test-address",
                    "folder": "Texas",
                    "ip_netmask": "10.0.0.0/24",
                    "tag": ["tag1"],
                }
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Empty lists should result in no matches (since filters remove results)
        filtered_objects = self.client.list(
            folder="Texas",
            types=[],
        )
        assert len(filtered_objects) == 0

        filtered_objects = self.client.list(
            folder="Texas",
            values=[],
        )
        assert len(filtered_objects) == 0

        filtered_objects = self.client.list(
            folder="Texas",
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
                    "folder": "Texas",
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
        with pytest.raises(HTTPError) as exc_info:
            self.client.list(folder="Texas", types="netmask")
        error_response = exc_info.value.response.json()
        assert (
            error_response["_errors"][0]["message"] == "'types' filter must be a list"
        )
        assert (
            error_response["_errors"][0]["details"]["errorType"]
            == "Invalid Query Parameter"
        )

        # Reset side effect for next test
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="E003",
            message="'values' filter must be a list",
            error_type="Invalid Query Parameter",
        )
        with pytest.raises(HTTPError) as exc_info:
            self.client.list(folder="Texas", values="10.0.0.0/24")
        error_response = exc_info.value.response.json()
        assert (
            error_response["_errors"][0]["message"] == "'values' filter must be a list"
        )
        assert (
            error_response["_errors"][0]["details"]["errorType"]
            == "Invalid Query Parameter"
        )

        # Reset side effect for next test
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="E003",
            message="'tags' filter must be a list",
            error_type="Invalid Query Parameter",
        )
        with pytest.raises(HTTPError) as exc_info:
            self.client.list(folder="Texas", tags="tag1")
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "'tags' filter must be a list"
        assert (
            error_response["_errors"][0]["details"]["errorType"]
            == "Invalid Query Parameter"
        )

        # Reset side effect for successful case
        self.mock_scm.get.side_effect = None  # noqa
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test that valid list filters pass validation
        try:
            self.client.list(
                folder="Texas",
                types=["netmask"],
                values=["10.0.0.0/24"],
                tags=["tag1"],
            )
        except HTTPError:
            pytest.fail("Unexpected HTTPError raised with valid list filters")

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
        assert error.http_status_code == 400
        assert "{'errorType': 'Invalid Object'}" in str(error)

        # Test with dict instead of list
        invalid_filters = {"values": {"value": "10.0.0.0/24"}}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client._apply_filters(mock_addresses, invalid_filters)

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        assert error.error_code == "E003"
        assert error.http_status_code == 400
        assert "{'errorType': 'Invalid Object'}" in str(error)

    def test_list_filters_combinations(self):
        """Test different combinations of valid filters."""
        mock_response = {
            "data": [
                {
                    "id": "123e4567-e89b-12d3-a456-426655440000",
                    "name": "test-address1",
                    "folder": "Texas",
                    "ip_netmask": "10.0.0.0/24",
                    "tag": ["tag1", "tag2"],
                },
                {
                    "id": "223e4567-e89b-12d3-a456-426655440000",
                    "name": "test-address2",
                    "folder": "Texas",
                    "ip_range": "10.0.0.1-10.0.0.10",
                    "tag": ["tag2", "tag3"],
                },
                {
                    "id": "323e4567-e89b-12d3-a456-426655440000",
                    "name": "test-address3",
                    "folder": "Texas",
                    "fqdn": "test.example.com",
                    "tag": ["tag1", "tag3"],
                },
            ]
        }
        self.mock_scm.get.return_value = mock_response  # noqa

        # Test combining types and tags filters
        filtered_objects = self.client.list(
            folder="Texas",
            types=["netmask"],
            tags=["tag1"],
        )
        assert len(filtered_objects) == 1
        assert filtered_objects[0].name == "test-address1"

        # Test combining values and tags filters
        filtered_objects = self.client.list(
            folder="Texas",
            values=["10.0.0.0/24"],
            tags=["tag2"],
        )
        assert len(filtered_objects) == 1
        assert filtered_objects[0].name == "test-address1"

        # Test all filters together
        filtered_objects = self.client.list(
            folder="Texas",
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
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Texas")

        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500
        assert "HTTP error: 500 - API error: E003" in str(exc_info.value)

    def test_list_response_invalid_data_field_missing(self):
        """
        Test that InvalidObjectError is raised when API returns response with missing data field.
        """
        self.mock_scm.get.return_value = {"wrong_field": "value"}  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Texas")

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        assert error.error_code == "E003"
        assert error.http_status_code == 500
        assert "HTTP error: 500 - API error: E003" in str(exc_info.value)

    def test_list_response_invalid_data_field_type(self):
        """
        Test that InvalidObjectError is raised when API returns non-list data field.
        """
        self.mock_scm.get.return_value = {"data": "not a list"}  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Texas")

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
            self.client.list(folder="Texas")

    def test_list_server_error(self):
        """Test generic exception handling in list method."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.list(folder="Texas")
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "An internal error occurred"
        assert error_response["_errors"][0]["details"]["errorType"] == "Internal Error"

    # -------------------- New Tests for exact_match and Exclusions --------------------

    def test_list_exact_match(self):
        """
        Test that exact_match=True returns only objects that match the container exactly.
        """
        mock_response = {
            "data": [
                AddressResponseFactory.with_ip_netmask(
                    name="addr_in_texas",
                    folder="Texas",
                    ip_netmask="192.168.1.0/24",
                ).model_dump(),
                AddressResponseFactory.with_ip_netmask(
                    name="addr_in_all",
                    folder="All",
                    ip_netmask="10.0.0.0/24",
                ).model_dump(),
            ]
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        # exact_match should exclude the one from "All"
        filtered = self.client.list(folder="Texas", exact_match=True)
        assert len(filtered) == 1
        assert filtered[0].folder == "Texas"
        assert filtered[0].name == "addr_in_texas"

    def test_list_exclude_folders(self):
        """
        Test that exclude_folders removes objects from those folders.
        """
        mock_response = {
            "data": [
                AddressResponseFactory.with_ip_netmask(
                    name="addr_in_texas",
                    folder="Texas",
                    ip_netmask="192.168.1.0/24",
                ).model_dump(),
                AddressResponseFactory.with_ip_netmask(
                    name="addr_in_all",
                    folder="All",
                    ip_netmask="10.0.0.0/24",
                ).model_dump(),
            ]
        }
        self.mock_scm.get.return_value = mock_response

        filtered = self.client.list(folder="Texas", exclude_folders=["All"])
        assert len(filtered) == 1
        assert all(a.folder != "All" for a in filtered)

    def test_list_exclude_snippets(self):
        """
        Test that exclude_snippets removes objects with those snippets.
        """
        mock_response = {
            "data": [
                AddressResponseFactory.with_fqdn(
                    name="addr_with_default_snippet",
                    folder="Texas",
                    snippet="default",
                    fqdn="example.com",
                ).model_dump(),
                AddressResponseFactory.with_ip_netmask(
                    name="addr_with_special_snippet",
                    folder="Texas",
                    snippet="special",
                    ip_netmask="10.0.1.0/24",
                ).model_dump(),
            ]
        }
        self.mock_scm.get.return_value = mock_response

        filtered = self.client.list(folder="Texas", exclude_snippets=["default"])
        assert len(filtered) == 1
        assert all(a.snippet != "default" for a in filtered)

    def test_list_exclude_devices(self):
        """
        Test that exclude_devices removes objects with those devices.
        """
        mock_response = {
            "data": [
                {
                    "id": "223e4567-e89b-12d3-a456-426655440000",
                    "name": "addr_deviceA",
                    "folder": "Texas",
                    "device": "DeviceA",
                    "ip_netmask": "192.168.1.0/24",
                },
                {
                    "id": "334e4567-e89b-12d3-a456-426655440000",
                    "name": "addr_deviceB",
                    "folder": "Texas",
                    "device": "DeviceB",
                    "ip_netmask": "10.0.0.0/24",
                },
            ]
        }
        self.mock_scm.get.return_value = mock_response

        filtered = self.client.list(folder="Texas", exclude_devices=["DeviceA"])
        assert len(filtered) == 1
        assert all(a.device != "DeviceA" for a in filtered)

    def test_list_exact_match_and_exclusions(self):
        """
        Test combining exact_match with exclusions.
        """
        mock_response = {
            "data": [
                {
                    "id": "223e4567-e89b-12d3-a456-426655440000",
                    "name": "addr_in_texas_default",
                    "folder": "Texas",
                    "snippet": "default",
                    "device": "DeviceA",
                    "ip_netmask": "192.168.1.0/24",
                },
                {
                    "id": "334e4567-e89b-12d3-a456-426655440000",
                    "name": "addr_in_texas_special",
                    "folder": "Texas",
                    "snippet": "special",
                    "device": "DeviceB",
                    "ip_netmask": "192.168.2.0/24",
                },
                {
                    "id": "434e4567-e89b-12d3-a456-426655440000",
                    "name": "addr_in_all",
                    "folder": "All",
                    "snippet": "default",
                    "device": "DeviceA",
                    "ip_netmask": "10.0.0.0/24",
                },
            ]
        }
        self.mock_scm.get.return_value = mock_response

        filtered = self.client.list(
            folder="Texas",
            exact_match=True,
            exclude_folders=["All"],
            exclude_snippets=["default"],
            exclude_devices=["DeviceA"],
        )
        # Only addr_in_texas_special should remain
        assert len(filtered) == 1
        obj = filtered[0]
        assert obj.folder == "Texas"
        assert obj.snippet != "default"
        assert obj.device != "DeviceA"


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

    def test_create_http_error_no_response_content(self):
        """Test create method when HTTP error has no response content."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500
        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.post.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.create(
                {"name": "test", "ip_netmask": "10.0.0.0/24", "folder": "test"}
            )

    def test_create_http_error_with_response(self):
        """Test that HTTPError with response content triggers proper error handling."""
        test_data = {
            "name": "test-address",
            "folder": "Texas",
            "ip_netmask": "10.0.0.0/24",
        }

        self.mock_scm.post.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="API_I00013",
            message="Create failed",
            error_type="Malformed Command",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.create(test_data)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Create failed"
        assert (
            error_response["_errors"][0]["details"]["errorType"] == "Malformed Command"
        )

    def test_create_generic_exception_handling(self):
        """Test handling of a generic exception during create."""
        self.mock_scm.post.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.create(
                {"name": "test", "ip_netmask": "10.0.0.0/24", "folder": "test"}
            )
        assert str(exc_info.value) == "Generic error"


class TestAddressGet(TestAddressBase):
    """Tests for retrieving a specific Address object."""

    def test_get_valid_object(self):
        """Test retrieving a specific object."""
        mock_response = AddressResponseFactory.with_ip_netmask(
            id="b44a8c00-7555-4021-96f0-d59deecd54e8",
            name="TestAddress",
            ip_netmask="10.0.0.0/24",
            folder="Texas",
        )

        self.mock_scm.get.return_value = mock_response.model_dump()  # noqa
        object_id = mock_response.id

        retrieved_object = self.client.get(object_id)

        self.mock_scm.get.assert_called_once_with(  # noqa
            f"/config/objects/v1/addresses/{object_id}"
        )
        assert isinstance(retrieved_object, AddressResponseModel)
        assert retrieved_object.id == mock_response.id
        assert retrieved_object.name == mock_response.name
        assert retrieved_object.ip_netmask == mock_response.ip_netmask
        assert retrieved_object.folder == mock_response.folder

    def test_get_object_not_present_error(self):
        """Test error handling when the object is not present."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.get(object_id)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Object not found"
        assert (
            error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"
        )

    def test_get_generic_exception_handling(self):
        """Test generic exception handling in get method."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.get.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.get(object_id)

        assert str(exc_info.value) == "Generic error"

    def test_get_http_error_no_response_content(self):
        """Test get method when HTTP error has no response content."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.get(object_id)

    def test_get_server_error(self):
        """Test handling of server errors during get method."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.get(object_id)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "An internal error occurred"
        assert error_response["_errors"][0]["details"]["errorType"] == "Internal Error"


class TestAddressUpdate(TestAddressBase):
    """Tests for updating Address objects."""

    def test_update_valid_object(self):
        """Test updating an object with valid data."""
        update_data = AddressUpdateApiFactory.with_ip_netmask(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="TestAddress",
            ip_netmask="10.0.0.0/24",
            description="Updated description",
            tag=["tag1", "tag2"],
            folder="Texas",
        )

        mock_response = AddressResponseFactory.from_request(update_data)
        self.mock_scm.put.return_value = mock_response.model_dump()  # noqa

        updated_object = self.client.update(update_data)

        self.mock_scm.put.assert_called_once()  # noqa
        call_args = self.mock_scm.put.call_args  # noqa
        assert call_args[0][0] == f"/config/objects/v1/addresses/{update_data.id}"

        payload = call_args[1]["json"]
        assert payload["name"] == "TestAddress"
        assert payload["ip_netmask"] == "10.0.0.0/24"
        assert payload["description"] == "Updated description"
        assert payload["tag"] == ["tag1", "tag2"]
        assert payload["folder"] == "Texas"

        assert isinstance(updated_object, AddressResponseModel)
        assert str(updated_object.id) == str(mock_response.id)
        assert updated_object.name == mock_response.name
        assert updated_object.ip_netmask == mock_response.ip_netmask
        assert updated_object.description == mock_response.description
        assert updated_object.tag == mock_response.tag
        assert updated_object.folder == mock_response.folder

    def test_update_malformed_command_error(self):
        """Test error handling when update fails due to malformed command."""
        update_data = AddressUpdateApiFactory.with_ip_netmask(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-address",
            folder="Texas",
            ip_netmask="10.0.0.0/24",
        )

        self.mock_scm.put.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="API_I00013",
            message="Update failed",
            error_type="Malformed Command",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.update(update_data)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Update failed"
        assert (
            error_response["_errors"][0]["details"]["errorType"] == "Malformed Command"
        )

    def test_update_object_not_present_error(self):
        """Test error handling when the object to update is not present."""
        update_data = AddressUpdateApiFactory.with_ip_netmask(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-address",
            folder="Texas",
            ip_netmask="10.0.0.0/24",
        )

        self.mock_scm.put.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.update(update_data)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Object not found"
        assert (
            error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"
        )

    def test_update_http_error_no_response_content(self):
        """Test update method when HTTP error has no response content."""
        update_data = AddressUpdateApiFactory.with_ip_netmask(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test",
            ip_netmask="10.0.0.0/24",
        )

        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.put.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.update(update_data)

    def test_update_generic_exception_handling(self):
        """Test handling of a generic exception during update."""
        update_data = AddressUpdateApiFactory.with_ip_netmask(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test",
            ip_netmask="10.0.0.0/24",
        )

        self.mock_scm.put.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.update(update_data)
        assert str(exc_info.value) == "Generic error"

    def test_update_server_error(self):
        """Test handling of server errors during update."""
        update_data = AddressUpdateApiFactory.with_ip_netmask(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test-address",
            folder="Texas",
            ip_netmask="10.0.0.0/24",
        )

        self.mock_scm.put.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.update(update_data)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "An internal error occurred"
        assert error_response["_errors"][0]["details"]["errorType"] == "Internal Error"


class TestAddressDelete(TestAddressBase):
    """Tests for deleting Address objects."""

    def test_delete_success(self):
        """Test successful deletion of an object."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.return_value = None  # noqa

        # Should not raise any exception
        self.client.delete(object_id)

        self.mock_scm.delete.assert_called_once_with(  # noqa
            f"/config/objects/v1/addresses/{object_id}"
        )

    def test_delete_referenced_object(self):
        """Test deleting an object that is referenced elsewhere."""
        object_id = "3fecfe58-af0c-472b-85cf-437bb6df2929"

        self.mock_scm.delete.side_effect = raise_mock_http_error(  # noqa
            status_code=409,
            error_code="E009",
            message="Your configuration is not valid.",
            error_type="Reference Not Zero",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.delete(object_id)
        error_response = exc_info.value.response.json()
        assert (
            error_response["_errors"][0]["message"]
            == "Your configuration is not valid."
        )
        assert (
            error_response["_errors"][0]["details"]["errorType"] == "Reference Not Zero"
        )

    def test_delete_object_not_present_error(self):
        """Test error handling when the object to delete is not present."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.delete(object_id)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Object not found"
        assert (
            error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"
        )

    def test_delete_http_error_no_response_content(self):
        """Test delete method when HTTP error has no response content."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.delete.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.delete(object_id)

    def test_delete_generic_exception_handling(self):
        """Test handling of a generic exception during delete."""
        self.mock_scm.delete.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.delete("abcdefg")

        assert str(exc_info.value) == "Generic error"

    def test_delete_server_error(self):
        """Test handling of server errors during delete."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.delete(object_id)
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "An internal error occurred"
        assert error_response["_errors"][0]["details"]["errorType"] == "Internal Error"


class TestAddressFetch(TestAddressBase):
    """Tests for fetching Address objects by name."""

    def test_fetch_valid_object(self):
        """Test retrieving an object by its name using the `fetch` method."""
        mock_response_model = AddressResponseFactory.with_ip_netmask(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="dallas-desktop1",
            folder="Texas",
            ip_netmask="10.5.0.11",
            description="test123456",
            tag=["Decrypted"],
        )
        mock_response_data = mock_response_model.model_dump()

        self.mock_scm.get.return_value = mock_response_data  # noqa

        fetched_object = self.client.fetch(
            name=mock_response_model.name,
            folder=mock_response_model.folder,
        )

        self.mock_scm.get.assert_called_once_with(  # noqa
            "/config/objects/v1/addresses",
            params={
                "folder": mock_response_model.folder,
                "name": mock_response_model.name,
            },
        )

        assert isinstance(fetched_object, AddressResponseModel)
        assert str(fetched_object.id) == str(mock_response_model.id)
        assert fetched_object.name == mock_response_model.name
        assert fetched_object.description == mock_response_model.description
        assert fetched_object.tag == mock_response_model.tag
        assert fetched_object.ip_netmask == mock_response_model.ip_netmask
        assert fetched_object.folder == mock_response_model.folder

    def test_fetch_object_not_present_error(self):
        """Test fetching an object that does not exist."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.fetch(name="nonexistent", folder="Texas")
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Object not found"
        assert (
            error_response["_errors"][0]["details"]["errorType"] == "Object Not Present"
        )

    def test_fetch_empty_name_error(self):
        """Test fetching with an empty name parameter."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="E003",
            message='"name" is not allowed to be empty',
            error_type="Missing Query Parameter",
        )

        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="", folder="Texas")

        error_msg = str(exc_info.value)
        assert '"name" is not allowed to be empty' in error_msg
        assert "HTTP error: 400" in error_msg
        assert "API error: E003" in error_msg

    def test_fetch_empty_container_error(self):
        """Test fetching with an empty folder parameter."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=400,
            error_code="E003",
            message='"folder" is not allowed to be empty',
            error_type="Missing Query Parameter",
        )

        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="test", folder="")

        error_msg = str(exc_info.value)
        assert '"folder" is not allowed to be empty' in error_msg
        assert "HTTP error: 400" in error_msg
        assert "API error: E003" in error_msg

    def test_fetch_invalid_response_format_error(self):
        """Test fetching an object when the API returns an unexpected format."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="E003",
            message="Invalid response format",
            error_type="Invalid Object",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.fetch(name="test", folder="Texas")
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "Invalid response format"
        assert error_response["_errors"][0]["details"]["errorType"] == "Invalid Object"

    def test_fetch_generic_exception_handling(self):
        """Test generic exception handling during fetch."""
        self.mock_scm.get.side_effect = Exception("Generic error")  # noqa

        with pytest.raises(Exception) as exc_info:
            self.client.fetch(name="test", folder="Texas")

        assert str(exc_info.value) == "Generic error"

    def test_fetch_http_error_no_response_content(self):
        """Test that an HTTPError without response content in fetch() re-raises the exception."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500
        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.fetch(name="test-address", folder="Texas")

    def test_fetch_server_error(self):
        """Test handling of server errors during fetch."""
        self.mock_scm.get.side_effect = raise_mock_http_error(  # noqa
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )

        with pytest.raises(HTTPError) as exc_info:
            self.client.fetch(name="test", folder="Texas")
        error_response = exc_info.value.response.json()
        assert error_response["_errors"][0]["message"] == "An internal error occurred"
        assert error_response["_errors"][0]["details"]["errorType"] == "Internal Error"

    def test_fetch_missing_id_field_error(self):
        """Test that InvalidObjectError is raised when the response is missing 'id' field."""
        mock_response = {
            "name": "test-address",
            "folder": "Texas",
            "ip_netmask": "10.0.0.0/24",
        }

        self.mock_scm.get.return_value = mock_response  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-address", folder="Texas")

        error_msg = str(exc_info.value)
        assert "HTTP error: 500 - API error: E003" in error_msg
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500

    def test_fetch_no_container_provided_error(self):
        """Test that InvalidObjectError is raised when no container parameter is provided."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-address")

        error_msg = str(exc_info.value)
        assert "HTTP error: 400 - API error: E003" in error_msg
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 400

    def test_fetch_multiple_containers_provided_error(self):
        """Test that InvalidObjectError is raised when multiple container parameters are provided."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(
                name="test-address",
                folder="Texas",
                snippet="TestSnippet",
            )

        error_msg = str(exc_info.value)
        assert "HTTP error: 400 - API error: E003" in error_msg
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 400

    def test_fetch_invalid_response_type_error(self):
        """Test that InvalidObjectError is raised when the response is not a dictionary."""
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test123", folder="Texas")

        error_msg = str(exc_info.value)
        assert "HTTP error: 500 - API error: E003" in error_msg
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500


# -------------------- End of Test Classes --------------------
