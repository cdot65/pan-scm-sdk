"""Unit tests for the DnsProxy class."""

from unittest.mock import MagicMock
import uuid

import pytest

from scm.config.network import DnsProxy
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.network import (
    DnsProxyCreateModel,
    DnsProxyResponseModel,
    DnsProxyUpdateModel,
)


@pytest.fixture
def sample_dns_proxy_dict():
    """Return a sample DNS proxy dictionary."""
    return {
        "id": str(uuid.uuid4()),
        "name": "test-dns-proxy",
        "folder": "Test Folder",
        "enabled": True,
        "default": {
            "primary": "8.8.8.8",
            "secondary": "8.8.4.4",
        },
    }


@pytest.fixture
def sample_dns_proxy_response(sample_dns_proxy_dict):
    """Return a sample DnsProxyResponseModel."""
    return DnsProxyResponseModel(**sample_dns_proxy_dict)


@pytest.mark.usefixtures("load_env")
class TestDnsProxyBase:
    """Base class for DnsProxy tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = DnsProxy(self.mock_scm, max_limit=5000)


class TestDnsProxy(TestDnsProxyBase):
    """Test suite for DnsProxy class."""

    def test_init(self):
        """Test initialization of DnsProxy class."""
        client = DnsProxy(self.mock_scm)
        assert client.api_client == self.mock_scm
        assert client.ENDPOINT == "/config/network/v1/dns-proxies"
        assert client.max_limit == client.DEFAULT_MAX_LIMIT

    def test_init_with_custom_max_limit(self):
        """Test initialization with custom max_limit."""
        client = DnsProxy(self.mock_scm, max_limit=1000)
        assert client.max_limit == 1000

    def test_init_with_invalid_max_limit(self):
        """Test initialization with invalid max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            DnsProxy(self.mock_scm, max_limit="invalid")
        assert "Invalid max_limit type" in str(excinfo.value)

    def test_init_with_negative_max_limit(self):
        """Test initialization with negative max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            DnsProxy(self.mock_scm, max_limit=-1)
        assert "Invalid max_limit value" in str(excinfo.value)

    def test_init_with_excessive_max_limit(self):
        """Test initialization with excessive max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            client = DnsProxy(self.mock_scm)
            client.max_limit = 10000
        assert "max_limit exceeds maximum allowed value" in str(excinfo.value)

    def test_create(self, sample_dns_proxy_dict):
        """Test create method."""
        self.mock_scm.post.return_value = sample_dns_proxy_dict

        # Create a copy without the ID for create operation
        create_data = sample_dns_proxy_dict.copy()
        create_data.pop("id")

        result = self.client.create(create_data)

        # Check that correct API call was made
        self.mock_scm.post.assert_called_once()
        call_args = self.mock_scm.post.call_args
        assert call_args[0][0] == self.client.ENDPOINT

        # Check payload validation
        payload = call_args[1]["json"]
        DnsProxyCreateModel(**payload)

        # Check result
        assert isinstance(result, DnsProxyResponseModel)
        assert result.name == sample_dns_proxy_dict["name"]
        assert result.folder == sample_dns_proxy_dict["folder"]

    def test_create_with_domain_servers(self):
        """Test create method with domain server rules."""
        response_dict = {
            "id": str(uuid.uuid4()),
            "name": "test-dns-proxy",
            "folder": "Test Folder",
            "enabled": True,
            "domain-servers": [
                {
                    "name": "rule1",
                    "primary": "10.0.0.1",
                    "domain-name": ["example.com", "test.com"],
                }
            ],
        }
        self.mock_scm.post.return_value = response_dict

        create_data = {
            "name": "test-dns-proxy",
            "folder": "Test Folder",
            "enabled": True,
            "domain_servers": [
                {
                    "name": "rule1",
                    "primary": "10.0.0.1",
                    "domain_name": ["example.com", "test.com"],
                }
            ],
        }

        result = self.client.create(create_data)

        assert isinstance(result, DnsProxyResponseModel)
        assert result.name == "test-dns-proxy"

    def test_get(self, sample_dns_proxy_dict):
        """Test get method."""
        self.mock_scm.get.return_value = sample_dns_proxy_dict
        object_id = sample_dns_proxy_dict["id"]

        result = self.client.get(object_id)

        # Check that correct API call was made
        expected_endpoint = f"{self.client.ENDPOINT}/{object_id}"
        self.mock_scm.get.assert_called_once_with(expected_endpoint)

        # Check result
        assert isinstance(result, DnsProxyResponseModel)
        assert result.id == uuid.UUID(object_id)
        assert result.name == sample_dns_proxy_dict["name"]

    def test_update(self, sample_dns_proxy_dict):
        """Test update method."""
        self.mock_scm.put.return_value = sample_dns_proxy_dict
        object_id = sample_dns_proxy_dict["id"]

        # Create update model
        update_model = DnsProxyUpdateModel(**sample_dns_proxy_dict)

        result = self.client.update(update_model)

        # Check that correct API call was made
        expected_endpoint = f"{self.client.ENDPOINT}/{object_id}"
        self.mock_scm.put.assert_called_once()
        call_args = self.mock_scm.put.call_args
        assert call_args[0][0] == expected_endpoint

        # ID should not be in the payload since it's in the URL
        assert "id" not in call_args[1]["json"]

        # Check result
        assert isinstance(result, DnsProxyResponseModel)
        assert result.id == uuid.UUID(object_id)
        assert result.name == sample_dns_proxy_dict["name"]

    def test_list(self, sample_dns_proxy_dict):
        """Test list method."""
        self.mock_scm.get.return_value = {
            "data": [sample_dns_proxy_dict],
            "limit": 20,
            "offset": 0,
            "total": 1,
        }

        result = self.client.list(folder="Test Folder")

        # Check that correct API call was made
        self.mock_scm.get.assert_called_once()
        call_args = self.mock_scm.get.call_args
        assert call_args[0][0] == self.client.ENDPOINT
        assert call_args[1]["params"]["folder"] == "Test Folder"

        # Check result
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], DnsProxyResponseModel)
        assert result[0].name == sample_dns_proxy_dict["name"]

    def test_list_response_errors(self):
        """Test list method error handling for invalid responses."""
        # Test non-list, non-dictionary response
        self.mock_scm.get.return_value = "not a dictionary"
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(folder="Test Folder")
        assert "Response is not a dictionary" in str(excinfo.value)

        # Test missing data field
        self.mock_scm.get.return_value = {"no_data": "field"}
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(folder="Test Folder")
        assert '"data" field missing in the response' in str(excinfo.value)

        # Test data field not a list
        self.mock_scm.get.return_value = {"data": "not a list"}
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(folder="Test Folder")
        assert '"data" field must be a list' in str(excinfo.value)

    def test_list_pagination(self, sample_dns_proxy_dict):
        """Test list method pagination."""
        proxy1 = sample_dns_proxy_dict.copy()
        proxy1["id"] = str(uuid.uuid4())
        proxy1["name"] = "proxy1"

        proxy2 = sample_dns_proxy_dict.copy()
        proxy2["id"] = str(uuid.uuid4())
        proxy2["name"] = "proxy2"

        self.mock_scm.get.side_effect = [
            {"data": [proxy1], "limit": 1, "offset": 0, "total": 2},
            {"data": [proxy2], "limit": 1, "offset": 1, "total": 2},
            {"data": [], "limit": 1, "offset": 2, "total": 2},
        ]

        self.client.max_limit = 1
        result = self.client.list(folder="Test Folder")

        assert self.mock_scm.get.call_count == 3
        assert len(result) == 2
        proxy_names = [p.name for p in result]
        assert "proxy1" in proxy_names
        assert "proxy2" in proxy_names

    def test_list_with_empty_folder(self):
        """Test list method with empty folder parameter."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            self.client.list(folder="")
        assert '"folder" is not allowed to be empty' in str(excinfo.value)

    def test_list_with_missing_container(self):
        """Test list method with missing container parameter."""
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list()
        assert "Invalid container parameters" in str(excinfo.value)

    def test_list_with_multiple_containers(self):
        """Test list method with multiple container parameters."""
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(folder="Test Folder", snippet="Test Snippet")
        assert "Invalid container parameters" in str(excinfo.value)

    def test_list_with_raw_list_response(self, sample_dns_proxy_dict):
        """Test list method when API returns raw list."""
        proxy1 = sample_dns_proxy_dict.copy()
        proxy1["id"] = str(uuid.uuid4())
        proxy1["name"] = "proxy1"

        proxy2 = sample_dns_proxy_dict.copy()
        proxy2["id"] = str(uuid.uuid4())
        proxy2["name"] = "proxy2"

        self.mock_scm.get.return_value = [proxy1, proxy2]

        result = self.client.list(folder="Test Folder")

        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(r, DnsProxyResponseModel) for r in result)

    def test_fetch(self, sample_dns_proxy_dict):
        """Test fetch method."""
        self.mock_scm.get.return_value = sample_dns_proxy_dict

        result = self.client.fetch(name="test-dns-proxy", folder="Test Folder")

        # Check that correct API call was made
        self.mock_scm.get.assert_called_once()
        call_args = self.mock_scm.get.call_args
        assert call_args[0][0] == self.client.ENDPOINT
        assert call_args[1]["params"]["name"] == "test-dns-proxy"
        assert call_args[1]["params"]["folder"] == "Test Folder"

        # Check result
        assert isinstance(result, DnsProxyResponseModel)
        assert result.name == sample_dns_proxy_dict["name"]

    def test_fetch_with_empty_name(self):
        """Test fetch method with empty name parameter."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            self.client.fetch(name="", folder="Test Folder")
        assert '"name" is not allowed to be empty' in str(excinfo.value)

    def test_fetch_with_empty_folder(self):
        """Test fetch method with empty folder parameter."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            self.client.fetch(name="test-dns-proxy", folder="")
        assert '"folder" is not allowed to be empty' in str(excinfo.value)

    def test_fetch_with_missing_container(self):
        """Test fetch method with missing container parameter."""
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-dns-proxy")
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            excinfo.value
        )

    def test_fetch_with_invalid_response(self):
        """Test fetch method with invalid response."""
        self.mock_scm.get.return_value = {"name": "test-dns-proxy"}

        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-dns-proxy", folder="Test Folder")
        assert "Response has invalid structure" in str(excinfo.value)

    def test_fetch_response_errors(self):
        """Test fetch method error handling for invalid responses."""
        # Test non-list, non-dictionary response
        self.mock_scm.get.return_value = "not a dictionary"
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-dns-proxy", folder="Test Folder")
        assert "Response is not a dictionary" in str(excinfo.value)

        # Test valid data list-style response
        valid_uuid = str(uuid.uuid4())
        self.mock_scm.get.return_value = {"data": [{"id": valid_uuid, "name": "test-dns-proxy"}]}
        result = self.client.fetch(name="test-dns-proxy", folder="Test Folder")
        assert isinstance(result, DnsProxyResponseModel)
        assert result.id == uuid.UUID(valid_uuid)

        # Test empty data list
        self.mock_scm.get.return_value = {"data": []}
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-dns-proxy", folder="Test Folder")
        assert "No matching DNS proxy found" in str(excinfo.value)

        # Test data item without id field
        self.mock_scm.get.return_value = {
            "data": [{"name": "test-dns-proxy", "folder": "Test Folder"}]
        }
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-dns-proxy", folder="Test Folder")
        assert "Response data item missing 'id' field" in str(excinfo.value)

    def test_fetch_with_raw_list_response(self, sample_dns_proxy_dict):
        """Test fetch method when API returns raw list."""
        proxy_data = sample_dns_proxy_dict.copy()
        self.mock_scm.get.return_value = [proxy_data]

        result = self.client.fetch(name=proxy_data["name"], folder=proxy_data["folder"])

        assert isinstance(result, DnsProxyResponseModel)
        assert result.id == uuid.UUID(proxy_data["id"])
        assert result.name == proxy_data["name"]

    def test_fetch_with_raw_list_response_empty(self):
        """Test fetch method when API returns empty raw list."""
        self.mock_scm.get.return_value = []

        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="nonexistent", folder="Test Folder")
        assert "No matching resource found" in str(excinfo.value)

    def test_fetch_with_raw_list_response_multiple(self, sample_dns_proxy_dict, monkeypatch):
        """Test fetch method when API returns raw list with multiple items."""
        proxy1 = sample_dns_proxy_dict.copy()
        proxy1["id"] = str(uuid.uuid4())
        proxy1["name"] = "proxy1"

        proxy2 = sample_dns_proxy_dict.copy()
        proxy2["id"] = str(uuid.uuid4())
        proxy2["name"] = "proxy2"

        self.mock_scm.get.return_value = [proxy1, proxy2]

        mock_warning = MagicMock()
        monkeypatch.setattr(self.client.logger, "warning", mock_warning)

        result = self.client.fetch(name="proxy1", folder="Test Folder")

        assert isinstance(result, DnsProxyResponseModel)
        assert result.id == uuid.UUID(proxy1["id"])
        mock_warning.assert_called_once()

    def test_delete(self, sample_dns_proxy_dict):
        """Test delete method."""
        object_id = sample_dns_proxy_dict["id"]

        self.client.delete(object_id)

        # Check that correct API call was made
        expected_endpoint = f"{self.client.ENDPOINT}/{object_id}"
        self.mock_scm.delete.assert_called_once_with(expected_endpoint)
