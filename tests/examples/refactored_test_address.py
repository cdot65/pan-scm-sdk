# tests/examples/refactored_test_address.py

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
    """Unit tests for filter methods."""
    
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


# -------------------- Mock Tests --------------------

@pytest.mark.mock
class TestAddressErrorHandling(TestAddressBase):
    """Mock tests for API error handling."""

    def test_list_http_error_no_response_content(self):
        """Test that an HTTPError without response content in list() re-raises the exception."""
        mock_response = MagicMock()
        mock_response.content = None  # Simulate no content
        mock_response.status_code = 500

        mock_http_error = HTTPError(response=mock_response)
        self.mock_scm.get.side_effect = mock_http_error  # noqa

        with pytest.raises(HTTPError):
            self.client.list(folder="Texas")

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


# -------------------- Parametrized Tests --------------------

@pytest.mark.parametrized
class TestAddressParametrized(TestAddressBase):
    """Parametrized tests for Address functionality."""

    @pytest.mark.parametrize(
        "address_type,address_value,factory_method", [
            ("ip_netmask", "10.0.0.0/24", AddressCreateApiFactory.with_ip_netmask),
            ("ip_range", "10.0.0.1-10.0.0.10", AddressCreateApiFactory.with_ip_range),
            ("ip_wildcard", "10.0.0.0/0.0.0.255", AddressCreateApiFactory.with_ip_wildcard),
            ("fqdn", "example.com", AddressCreateApiFactory.with_fqdn),
        ]
    )
    def test_create_address_types(self, address_type, address_value, factory_method):
        """Test creating addresses with different types."""
        test_object = factory_method()
        mock_response = AddressResponseFactory.from_request(test_object)

        self.mock_scm.post.return_value = mock_response.model_dump()  # noqa
        created_object = self.client.create(test_object.model_dump(exclude_unset=True))

        # Verify the address type attribute exists and matches the expected value
        assert getattr(created_object, address_type) == address_value


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
    
    # Generate test data
    address_id = str(uuid.uuid4())
    test_name = "test-address-lifecycle"
    test_folder = "Texas"
    test_ip = "10.0.0.1/32"

    # 1. Create address
    create_data = {
        "name": test_name,
        "folder": test_folder,
        "ip_netmask": test_ip,
        "description": "Lifecycle test address"
    }
    
    mock_create_response = {
        "id": address_id,
        "name": test_name,
        "folder": test_folder,
        "ip_netmask": test_ip,
        "description": "Lifecycle test address"
    }
    mock_scm.post.return_value = mock_create_response
    
    created = client.create(create_data)
    assert created.id == address_id
    assert created.name == test_name
    
    # 2. List addresses
    mock_list_response = {
        "data": [mock_create_response],
        "offset": 0,
        "total": 1,
        "limit": 100
    }
    mock_scm.get.return_value = mock_list_response
    
    addresses = client.list(folder=test_folder)
    assert len(addresses) == 1
    assert addresses[0].id == address_id
    
    # 3. Get specific address
    mock_scm.get.return_value = mock_create_response
    
    retrieved = client.get(address_id)
    assert retrieved.id == address_id
    
    # 4. Update address
    update_data = {
        "id": address_id,
        "name": test_name,
        "folder": test_folder,
        "ip_netmask": test_ip,
        "description": "Updated lifecycle test address" 
    }
    
    mock_update_response = {
        "id": address_id,
        "name": test_name,
        "folder": test_folder,
        "ip_netmask": test_ip,
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


# -------------------- Configuration Tests --------------------

@pytest.mark.configuration
def test_address_client_initialization():
    """Configuration test for Address client initialization options."""
    # Test with default configuration
    mock_scm = MagicMock()
    default_client = Address(mock_scm)
    assert default_client.max_limit == 2500
    
    # Test with custom configuration
    custom_client = Address(mock_scm, max_limit=1000)
    assert custom_client.max_limit == 1000
    
    # Test with environment variables (simulated)
    with patch.dict('os.environ', {'SCM_MAX_LIMIT': '3000'}):
        env_client = Address(mock_scm)
        assert env_client.max_limit == 3000