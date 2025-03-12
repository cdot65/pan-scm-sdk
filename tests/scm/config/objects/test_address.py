# tests/scm/config/objects/test_address.py

# Standard library imports
from unittest.mock import MagicMock
import uuid

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
    AddressUpdateModel,
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
        self.client = Address(self.mock_scm, max_limit=5000)  # noqa


# -------------------- Unit Tests --------------------


@pytest.mark.unit
class TestAddressMaxLimit(TestAddressBase):
    """Unit tests for max_limit functionality."""

    def test_default_max_limit(self):
        """Test that default max_limit is set correctly."""
        client = Address(self.mock_scm)  # noqa
        assert client.max_limit == Address.DEFAULT_MAX_LIMIT
        assert client.max_limit == 2500

    def test_custom_max_limit(self):
        """Test setting a custom max_limit."""
        client = Address(self.mock_scm, max_limit=1000)  # noqa
        assert client.max_limit == 1000

    def test_max_limit_setter(self):
        """Test the max_limit property setter."""
        client = Address(self.mock_scm)  # noqa
        client.max_limit = 3000
        assert client.max_limit == 3000

    def test_invalid_max_limit_type(self):
        """Test that invalid max_limit type raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            Address(self.mock_scm, max_limit="invalid")  # noqa
        assert (
            "{'error': 'Invalid max_limit type'} - HTTP error: 400 - API error: E003"
            in str(exc_info.value)
        )

    def test_max_limit_too_low(self):
        """Test that max_limit below 1 raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            Address(self.mock_scm, max_limit=0)  # noqa
        assert (
            "{'error': 'Invalid max_limit value'} - HTTP error: 400 - API error: E003"
            in str(exc_info.value)
        )

    def test_max_limit_too_high(self):
        """Test that max_limit above ABSOLUTE_MAX_LIMIT raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            Address(self.mock_scm, max_limit=6000)  # noqa
        assert "max_limit exceeds maximum allowed value" in str(exc_info.value)


@pytest.mark.unit
class TestAddressFilters(TestAddressBase):
    """Unit tests for filter validation."""

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
        
    def test_list_filters_with_valid_data(self):
        """Test the filtering functionality with different types of objects."""
        # Test filtering by types
        mock_addresses = [
            AddressResponseModel(
                id=uuid.uuid4(), name="addr1", folder="test", ip_netmask="10.0.0.0/24"
            ),
            AddressResponseModel(
                id=uuid.uuid4(), name="addr2", folder="test", ip_range="10.0.0.1-10.0.0.10"
            ),
            AddressResponseModel(
                id=uuid.uuid4(), name="addr3", folder="test", fqdn="example.com"
            ),
        ]
        
        # Test types filter (lines 197-200)
        filters = {"types": ["netmask"]}
        filtered = self.client._apply_filters(mock_addresses, filters)
        assert len(filtered) == 1
        assert filtered[0].name == "addr1"
        
        # Test values filter (lines 219-220)
        filters = {"values": ["10.0.0.0/24"]}
        filtered = self.client._apply_filters(mock_addresses, filters)
        assert len(filtered) == 1
        assert filtered[0].name == "addr1"
        
        # Test tags filter (lines 239-240)
        mock_addresses_with_tags = [
            AddressResponseModel(
                id=uuid.uuid4(), name="addr1", folder="test", ip_netmask="10.0.0.0/24", tag=["tag1", "tag2"]
            ),
            AddressResponseModel(
                id=uuid.uuid4(), name="addr2", folder="test", ip_range="10.0.0.1-10.0.0.10", tag=["tag3"]
            ),
        ]
        
        filters = {"tags": ["tag1"]}
        filtered = self.client._apply_filters(mock_addresses_with_tags, filters)
        assert len(filtered) == 1
        assert filtered[0].name == "addr1"


# -------------------- Integration Tests --------------------


@pytest.mark.integration
class TestAddressList(TestAddressBase):
    """Integration tests for listing Address objects."""

    def test_list_valid(self):
        """Test listing all objects."""
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
                "folder": "All",
                "limit": 5000,
                "offset": 0,
            },
        )
        assert isinstance(existing_objects, list)
        assert isinstance(existing_objects[0], AddressResponseModel)
        assert len(existing_objects) == 2
        assert existing_objects[0].name == "Palo Alto Networks Sinkhole"

    def test_list_exact_match(self):
        """Test that exact_match=True returns only objects that match the container exactly."""
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
        """Test that exclude_folders removes objects from those folders."""
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

        filtered = self.client.list(folder="Texas", exclude_folders=["All"])
        assert len(filtered) == 1
        assert all(a.folder != "All" for a in filtered)

    def test_list_exclude_snippets(self):
        """Test that exclude_snippets removes objects with those snippets."""
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
        self.mock_scm.get.return_value = mock_response  # noqa

        filtered = self.client.list(folder="Texas", exclude_snippets=["default"])
        assert len(filtered) == 1
        assert all(a.snippet != "default" for a in filtered)

    def test_list_exclude_devices(self):
        """Test that exclude_devices removes objects with those devices."""
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
        self.mock_scm.get.return_value = mock_response  # noqa

        filtered = self.client.list(folder="Texas", exclude_devices=["DeviceA"])
        assert len(filtered) == 1
        assert all(a.device != "DeviceA" for a in filtered)

    def test_list_exact_match_and_exclusions(self):
        """Test combining exact_match with exclusions."""
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
        self.mock_scm.get.return_value = mock_response  # noqa

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
        
    def test_list_pagination_offset_increment(self):
        """Test that pagination offset is properly incremented (line 370)."""
        # Configure client with a smaller max_limit to test pagination more easily
        client = Address(self.mock_scm, max_limit=10)
        
        # Generate valid UUID strings for the mock data
        uuids = [str(uuid.uuid4()) for _ in range(15)]
        
        # First page has full data - should trigger offset increment
        page1 = {"data": [{"id": uuids[i], "name": f"test{i}", "folder": "Test", "ip_netmask": f"10.0.0.{i}/32"} for i in range(10)]}
        # Second page has less data - should end loop
        page2 = {"data": [{"id": uuids[i+10], "name": f"test{i+10}", "folder": "Test", "ip_netmask": f"10.0.0.{i+10}/32"} for i in range(5)]}
        
        self.mock_scm.get.side_effect = [page1, page2]
        
        results = client.list(folder="Test")
        
        # Verify the API was called twice with different offsets
        assert self.mock_scm.get.call_count == 2
        # First call with offset 0
        assert self.mock_scm.get.call_args_list[0][1]["params"]["offset"] == 0
        # Second call with offset 10 (after increment)
        assert self.mock_scm.get.call_args_list[1][1]["params"]["offset"] == 10
        
        # Total results should be 15 (10 from page 1 + 5 from page 2)
        assert len(results) == 15


@pytest.mark.integration
class TestAddressCreate(TestAddressBase):
    """Integration tests for creating Address objects."""

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


@pytest.mark.integration
class TestAddressGet(TestAddressBase):
    """Integration tests for retrieving a specific Address object."""

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


@pytest.mark.integration
class TestAddressUpdate(TestAddressBase):
    """Integration tests for updating Address objects."""

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


@pytest.mark.integration
class TestAddressDelete(TestAddressBase):
    """Integration tests for deleting Address objects."""

    def test_delete_success(self):
        """Test successful deletion of an object."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"

        self.mock_scm.delete.return_value = None  # noqa

        # Should not raise any exception
        self.client.delete(object_id)

        self.mock_scm.delete.assert_called_once_with(  # noqa
            f"/config/objects/v1/addresses/{object_id}"
        )


@pytest.mark.integration
class TestAddressFetch(TestAddressBase):
    """Integration tests for fetching Address objects by name."""

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
    
    def test_fetch_empty_name(self):
        """Test that empty name raises an error (line 427)."""
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="", folder="Test")
        
        error_msg = str(exc_info.value)
        assert '"name" is not allowed to be empty' in error_msg
        assert "HTTP error: 400" in error_msg
        
    def test_fetch_empty_folder(self):
        """Test that empty folder raises an error (line 438)."""
        with pytest.raises(MissingQueryParameterError) as exc_info:
            self.client.fetch(name="test", folder="")
        
        error_msg = str(exc_info.value)
        assert '"folder" is not allowed to be empty' in error_msg
        assert "HTTP error: 400" in error_msg
        
    def test_fetch_no_container(self):
        """Test that missing container parameter raises an error (line 457)."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test")
        
        error_msg = str(exc_info.value)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in error_msg
        assert "HTTP error: 400" in error_msg
        
    def test_fetch_invalid_response_format(self):
        """Test that invalid response format raises an error (line 475)."""
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]  # noqa
        
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test", folder="Test")
            
        error_msg = str(exc_info.value)
        assert "Response is not a dictionary" in error_msg
        assert "HTTP error: 500" in error_msg
        
    def test_fetch_missing_id(self):
        """Test that response missing ID field raises an error (line 485)."""
        self.mock_scm.get.return_value = {"name": "test", "folder": "Test"}  # noqa
        
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test", folder="Test")
            
        error_msg = str(exc_info.value)
        assert "Response missing 'id' field" in error_msg
        assert "HTTP error: 500" in error_msg


# -------------------- Mock Tests --------------------


@pytest.mark.mock
class TestAddressListErrorHandling(TestAddressBase):
    """Mock tests for error handling in list operations."""

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
        """Test that InvalidObjectError is raised when no container parameter is provided."""
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

    def test_list_filters_types(self):
        """Test validation of filter types in list method."""
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

    def test_list_response_invalid_format(self):
        """Test that InvalidObjectError is raised when the response is not a dictionary."""
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Texas")

        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500
        assert "HTTP error: 500 - API error: E003" in str(exc_info.value)

    def test_list_response_invalid_data_field_missing(self):
        """Test that InvalidObjectError is raised when API returns response with missing data field."""
        self.mock_scm.get.return_value = {"wrong_field": "value"}  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Texas")

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        assert error.error_code == "E003"
        assert error.http_status_code == 500
        assert "HTTP error: 500 - API error: E003" in str(exc_info.value)
        
    def test_list_response_invalid_data_type(self):
        """Test that InvalidObjectError is raised when 'data' is not a list (line 352)."""
        self.mock_scm.get.return_value = {"data": "not a list"}  # noqa

        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Texas")

        error = exc_info.value
        assert isinstance(error, InvalidObjectError)
        assert error.error_code == "E003"
        assert error.http_status_code == 500
        assert '"data" field must be a list' in str(exc_info.value)

    def test_list_response_no_content(self):
        """Test that an HTTPError without response content in list() re-raises the exception."""
        mock_response = MagicMock()
        mock_response.content = None  # Simulate no content
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.list(folder="Texas")


@pytest.mark.mock
class TestAddressCreateErrorHandling(TestAddressBase):
    """Mock tests for error handling in create operations."""

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


@pytest.mark.mock
class TestAddressUpdateErrorHandling(TestAddressBase):
    """Mock tests for error handling in update operations."""

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


@pytest.mark.mock
class TestAddressDeleteErrorHandling(TestAddressBase):
    """Mock tests for error handling in delete operations."""

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


# -------------------- Parametrized Tests --------------------


@pytest.mark.parametrized
class TestAddressParametrized(TestAddressBase):
    """Parametrized tests for Address functionality."""

    @pytest.mark.parametrize(
        "create_factory,address_type,expected_value",
        [
            (
                AddressCreateApiFactory.with_ip_netmask,
                "ip_netmask",
                "10.0.0.0/24",
            ),
            (
                AddressCreateApiFactory.with_ip_range,
                "ip_range",
                "10.0.0.1-10.0.0.10",
            ),
            (
                AddressCreateApiFactory.with_ip_wildcard,
                "ip_wildcard",
                "10.0.0.0/0.0.0.255",
            ),
            (
                AddressCreateApiFactory.with_fqdn,
                "fqdn",
                "example.com",
            ),
        ],
    )
    def test_create_address_types(self, create_factory, address_type, expected_value):
        """Test creating addresses with different types."""
        test_object = create_factory()
        setattr(test_object, address_type, expected_value)
        mock_response = AddressResponseFactory.from_request(test_object)

        self.mock_scm.post.return_value = mock_response.model_dump()  # noqa
        created_object = self.client.create(test_object.model_dump(exclude_unset=True))

        # Verify the address type attribute exists and matches the expected value
        assert getattr(created_object, address_type) == expected_value


# -------------------- Functional Tests --------------------


@pytest.mark.functional
def test_address_lifecycle(mock_scm):
    """Functional test for complete address object lifecycle (CRUD)."""
    # Setup
    mock_scm.get = MagicMock()
    mock_scm.post = MagicMock()
    mock_scm.put = MagicMock()
    mock_scm.delete = MagicMock()
    client = Address(mock_scm, max_limit=5000)
    
    # 1. Create address
    create_data = {
        "name": "test-address-lifecycle",
        "folder": "Texas",
        "ip_netmask": "10.0.0.1/32",
        "description": "Lifecycle test address"
    }
    
    address_id = "123e4567-e89b-12d3-a456-426655440000"
    mock_create_response = {
        "id": address_id,
        "name": "test-address-lifecycle",
        "folder": "Texas",
        "ip_netmask": "10.0.0.1/32",
        "description": "Lifecycle test address"
    }
    mock_scm.post.return_value = mock_create_response
    
    created = client.create(create_data)
    assert str(created.id) == address_id
    assert created.name == "test-address-lifecycle"
    
    # 2. List addresses
    mock_list_response = {
        "data": [mock_create_response],
        "offset": 0,
        "total": 1,
        "limit": 100
    }
    mock_scm.get.return_value = mock_list_response
    
    addresses = client.list(folder="Texas")
    assert len(addresses) == 1
    assert str(addresses[0].id) == address_id
    
    # 3. Get specific address
    mock_scm.get.return_value = mock_create_response
    
    retrieved = client.get(address_id)
    assert str(retrieved.id) == address_id
    
    # 4. Update address
    update_data = AddressUpdateModel(
        id=address_id,
        name="test-address-lifecycle",
        folder="Texas",
        ip_netmask="10.0.0.1/32",
        description="Updated lifecycle test address"
    )
    
    mock_update_response = {
        "id": address_id,
        "name": "test-address-lifecycle",
        "folder": "Texas",
        "ip_netmask": "10.0.0.1/32",
        "description": "Updated lifecycle test address"
    }
    mock_scm.put.return_value = mock_update_response
    
    updated = client.update(update_data)
    assert updated.description == "Updated lifecycle test address"
    
    # 5. Delete address
    mock_scm.delete.return_value = None
    
    # Should not raise any exceptions
    client.delete(address_id)
    mock_scm.delete.assert_called_once_with(f"/config/objects/v1/addresses/{address_id}")


# -------------------- End of Test Classes --------------------