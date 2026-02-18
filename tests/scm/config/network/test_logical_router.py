"""Unit tests for the LogicalRouter class."""

from unittest.mock import MagicMock
import uuid

import pytest

from scm.config.network import LogicalRouter
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.network import (
    LogicalRouterCreateModel,
    LogicalRouterResponseModel,
    LogicalRouterUpdateModel,
)


@pytest.fixture
def sample_logical_router_dict():
    """Return a sample logical router dictionary."""
    return {
        "id": str(uuid.uuid4()),
        "name": "LR-Production",
        "folder": "PANDA",
        "routing_stack": "advanced",
        "vrf": [
            {
                "name": "default",
                "interface": ["ethernet1/1", "ethernet1/2"],
            }
        ],
    }


@pytest.fixture
def sample_logical_router_response(sample_logical_router_dict):
    """Return a sample LogicalRouterResponseModel."""
    return LogicalRouterResponseModel(**sample_logical_router_dict)


@pytest.mark.usefixtures("load_env")
class TestLogicalRouterBase:
    """Base class for LogicalRouter tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = LogicalRouter(self.mock_scm, max_limit=5000)


class TestLogicalRouter(TestLogicalRouterBase):
    """Test suite for LogicalRouter class."""

    # --- Initialization Tests ---

    def test_init(self):
        """Test initialization of LogicalRouter class."""
        lr = LogicalRouter(self.mock_scm)
        assert lr.api_client == self.mock_scm
        assert lr.ENDPOINT == "/config/network/v1/logical-routers"
        assert lr.max_limit == lr.DEFAULT_MAX_LIMIT

    def test_init_with_custom_max_limit(self):
        """Test initialization with custom max_limit."""
        lr = LogicalRouter(self.mock_scm, max_limit=1000)
        assert lr.max_limit == 1000

    def test_init_with_invalid_max_limit(self):
        """Test initialization with invalid max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            LogicalRouter(self.mock_scm, max_limit="invalid")
        assert "Invalid max_limit type" in str(excinfo.value)

    def test_init_with_negative_max_limit(self):
        """Test initialization with negative max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            LogicalRouter(self.mock_scm, max_limit=-1)
        assert "Invalid max_limit value" in str(excinfo.value)

    def test_init_with_excessive_max_limit(self):
        """Test initialization with excessive max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            lr = LogicalRouter(self.mock_scm)
            lr.max_limit = 10000
        assert "max_limit exceeds maximum allowed value" in str(excinfo.value)

    # --- CRUD Tests ---

    def test_create(self, sample_logical_router_dict):
        """Test create method."""
        self.mock_scm.post.return_value = sample_logical_router_dict

        # Create a copy without the ID for create operation
        create_data = sample_logical_router_dict.copy()
        create_data.pop("id")

        result = self.client.create(create_data)

        # Check that correct API call was made
        self.mock_scm.post.assert_called_once()
        call_args = self.mock_scm.post.call_args
        assert call_args[0][0] == self.client.ENDPOINT

        # Check payload validation
        payload = call_args[1]["json"]
        LogicalRouterCreateModel(**payload)

        # Check result
        assert isinstance(result, LogicalRouterResponseModel)
        assert result.name == sample_logical_router_dict["name"]
        assert result.folder == sample_logical_router_dict["folder"]

    def test_get(self, sample_logical_router_dict):
        """Test get method."""
        self.mock_scm.get.return_value = sample_logical_router_dict
        object_id = sample_logical_router_dict["id"]

        result = self.client.get(object_id)

        # Check that correct API call was made
        expected_endpoint = f"{self.client.ENDPOINT}/{object_id}"
        self.mock_scm.get.assert_called_once_with(expected_endpoint)

        # Check result
        assert isinstance(result, LogicalRouterResponseModel)
        assert result.id == uuid.UUID(object_id)
        assert result.name == sample_logical_router_dict["name"]

    def test_update(self, sample_logical_router_dict):
        """Test update method."""
        self.mock_scm.put.return_value = sample_logical_router_dict
        object_id = sample_logical_router_dict["id"]

        # Create update model
        update_model = LogicalRouterUpdateModel(**sample_logical_router_dict)

        result = self.client.update(update_model)

        # Check that correct API call was made
        expected_endpoint = f"{self.client.ENDPOINT}/{object_id}"
        self.mock_scm.put.assert_called_once()
        call_args = self.mock_scm.put.call_args
        assert call_args[0][0] == expected_endpoint

        # ID should not be in the payload since it's in the URL
        assert "id" not in call_args[1]["json"]

        # Check result
        assert isinstance(result, LogicalRouterResponseModel)
        assert result.id == uuid.UUID(object_id)
        assert result.name == sample_logical_router_dict["name"]

    def test_delete(self, sample_logical_router_dict):
        """Test delete method."""
        object_id = sample_logical_router_dict["id"]

        self.client.delete(object_id)

        # Check that correct API call was made
        expected_endpoint = f"{self.client.ENDPOINT}/{object_id}"
        self.mock_scm.delete.assert_called_once_with(expected_endpoint)

    # --- List Tests ---

    def test_list(self, sample_logical_router_dict):
        """Test list method."""
        self.mock_scm.get.return_value = {
            "data": [sample_logical_router_dict],
            "limit": 20,
            "offset": 0,
            "total": 1,
        }

        result = self.client.list(folder="PANDA")

        # Check that correct API call was made
        self.mock_scm.get.assert_called_once()
        call_args = self.mock_scm.get.call_args
        assert call_args[0][0] == self.client.ENDPOINT
        assert call_args[1]["params"]["folder"] == "PANDA"

        # Check result
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], LogicalRouterResponseModel)
        assert result[0].name == sample_logical_router_dict["name"]

    def test_list_response_errors(self):
        """Test list method error handling for invalid responses."""
        # Test non-dictionary response
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(folder="PANDA")
        assert "Response is not a dictionary" in str(excinfo.value)

        # Test missing data field
        self.mock_scm.get.return_value = {"no_data": "field"}
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(folder="PANDA")
        assert '"data" field missing in the response' in str(excinfo.value)

        # Test data field not a list
        self.mock_scm.get.return_value = {"data": "not a list"}
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(folder="PANDA")
        assert '"data" field must be a list' in str(excinfo.value)

    def test_list_pagination(self, sample_logical_router_dict):
        """Test list method pagination."""
        # Create multiple pages of data
        lr1 = sample_logical_router_dict.copy()
        lr1["id"] = str(uuid.uuid4())
        lr1["name"] = "LR-1"

        lr2 = sample_logical_router_dict.copy()
        lr2["id"] = str(uuid.uuid4())
        lr2["name"] = "LR-2"

        # Mock responses for pagination
        self.mock_scm.get.side_effect = [
            # First page
            {"data": [lr1], "limit": 1, "offset": 0, "total": 2},
            # Second page
            {"data": [lr2], "limit": 1, "offset": 1, "total": 2},
            # Empty page (to end pagination)
            {"data": [], "limit": 1, "offset": 2, "total": 2},
        ]

        # Set a small limit to force pagination
        self.client.max_limit = 1
        result = self.client.list(folder="PANDA")

        # Should have made 3 calls (2 pages + 1 empty page to end pagination)
        assert self.mock_scm.get.call_count == 3

        # We should get both routers in the result
        assert len(result) == 2
        router_names = [r.name for r in result]
        assert "LR-1" in router_names
        assert "LR-2" in router_names

    def test_list_with_exclusions(self, sample_logical_router_dict):
        """Test list method with exclusion filters."""
        # Create multiple routers with different containers
        lr1 = sample_logical_router_dict.copy()
        lr1["id"] = str(uuid.uuid4())
        lr1["name"] = "LR-1"
        lr1["folder"] = "Folder1"

        lr2 = sample_logical_router_dict.copy()
        lr2["id"] = str(uuid.uuid4())
        lr2["name"] = "LR-2"
        lr2["folder"] = "Folder2"

        lr3 = sample_logical_router_dict.copy()
        lr3["id"] = str(uuid.uuid4())
        lr3["name"] = "LR-3"
        lr3["folder"] = "Folder1"
        lr3["snippet"] = "Snippet1"

        lr4 = sample_logical_router_dict.copy()
        lr4["id"] = str(uuid.uuid4())
        lr4["name"] = "LR-4"
        lr4["folder"] = "Folder1"
        lr4["device"] = "Device1"

        self.mock_scm.get.return_value = {
            "data": [lr1, lr2, lr3, lr4],
            "limit": 100,
            "offset": 0,
            "total": 4,
        }

        # Test exact_match filter
        result = self.client.list(folder="Folder1", exact_match=True)
        assert len(result) == 3  # Should match lr1, lr3, lr4

        # Test exclude_folders filter
        result = self.client.list(folder="Folder1", exclude_folders=["Folder2"])
        assert len(result) == 3  # Should exclude only lr2

        # Test exclude_snippets filter
        result = self.client.list(folder="Folder1", exclude_snippets=["Snippet1"])
        assert len(result) == 3  # Should exclude lr3

        # Test exclude_devices filter
        result = self.client.list(folder="Folder1", exclude_devices=["Device1"])
        assert len(result) == 3  # Should exclude lr4

        # Test combining multiple exclusions
        result = self.client.list(
            folder="Folder1", exclude_snippets=["Snippet1"], exclude_devices=["Device1"]
        )
        assert len(result) == 2  # Should exclude lr3 and lr4

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
            self.client.list(folder="PANDA", snippet="MySnippet")
        assert "Invalid container parameters" in str(excinfo.value)

    def test_list_filtering_by_routing_stack(self, sample_logical_router_dict):
        """Test list method with routing_stack filtering."""
        lr1 = sample_logical_router_dict.copy()
        lr1["id"] = str(uuid.uuid4())
        lr1["name"] = "LR-Advanced"
        lr1["routing_stack"] = "advanced"

        lr2 = sample_logical_router_dict.copy()
        lr2["id"] = str(uuid.uuid4())
        lr2["name"] = "LR-Legacy"
        lr2["routing_stack"] = "legacy"

        lr3 = sample_logical_router_dict.copy()
        lr3["id"] = str(uuid.uuid4())
        lr3["name"] = "LR-None"
        lr3.pop("routing_stack", None)

        self.mock_scm.get.return_value = {
            "data": [lr1, lr2, lr3],
            "limit": 100,
            "offset": 0,
            "total": 3,
        }

        # Filter by advanced only
        result = self.client.list(folder="PANDA", routing_stack=["advanced"])
        assert len(result) == 1
        assert result[0].name == "LR-Advanced"

        # Filter by legacy only
        result = self.client.list(folder="PANDA", routing_stack=["legacy"])
        assert len(result) == 1
        assert result[0].name == "LR-Legacy"

        # Filter by both
        result = self.client.list(folder="PANDA", routing_stack=["advanced", "legacy"])
        assert len(result) == 2

        # Invalid filter type
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.list(folder="PANDA", routing_stack="not_a_list")
        assert "Invalid Object" in str(excinfo.value)

    # --- Fetch Tests ---

    def test_fetch(self, sample_logical_router_dict):
        """Test fetch method."""
        self.mock_scm.get.return_value = sample_logical_router_dict

        result = self.client.fetch(name="LR-Production", folder="PANDA")

        # Check that correct API call was made
        self.mock_scm.get.assert_called_once()
        call_args = self.mock_scm.get.call_args
        assert call_args[0][0] == self.client.ENDPOINT
        assert call_args[1]["params"]["name"] == "LR-Production"
        assert call_args[1]["params"]["folder"] == "PANDA"

        # Check result
        assert isinstance(result, LogicalRouterResponseModel)
        assert result.name == sample_logical_router_dict["name"]

    def test_fetch_with_empty_name(self):
        """Test fetch method with empty name parameter."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            self.client.fetch(name="", folder="PANDA")
        assert '"name" is not allowed to be empty' in str(excinfo.value)

    def test_fetch_with_empty_folder(self):
        """Test fetch method with empty folder parameter."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            self.client.fetch(name="LR-Production", folder="")
        assert '"folder" is not allowed to be empty' in str(excinfo.value)

    def test_fetch_with_missing_container(self):
        """Test fetch method with missing container parameter."""
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="LR-Production")
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            excinfo.value
        )

    def test_fetch_with_invalid_response(self):
        """Test fetch method with invalid response."""
        # Response without an ID field or data field
        self.mock_scm.get.return_value = {"name": "LR-Production"}

        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="LR-Production", folder="PANDA")
        assert "Response has invalid structure" in str(excinfo.value)

    def test_fetch_response_errors(self):
        """Test fetch method error handling for invalid responses."""
        # Test non-dict/non-list response (e.g., string)
        self.mock_scm.get.return_value = "not a dictionary or list"
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="LR-Production", folder="PANDA")
        assert "Response is not a dictionary or list" in str(excinfo.value)

        # Test empty list response (API returns raw array)
        self.mock_scm.get.return_value = []
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="LR-Production", folder="PANDA")
        assert "No matching logical router found" in str(excinfo.value)

        # Test valid data list-style response
        valid_uuid = str(uuid.uuid4())
        self.mock_scm.get.return_value = {"data": [{"id": valid_uuid, "name": "LR-Production"}]}
        result = self.client.fetch(name="LR-Production", folder="PANDA")
        assert isinstance(result, LogicalRouterResponseModel)
        assert result.id == uuid.UUID(valid_uuid)
        assert result.name == "LR-Production"

        # Test empty data list
        self.mock_scm.get.return_value = {"data": []}
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="LR-Production", folder="PANDA")
        assert "No matching logical router found" in str(excinfo.value)

        # Test data item without id field
        self.mock_scm.get.return_value = {"data": [{"name": "LR-Production", "folder": "PANDA"}]}
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="LR-Production", folder="PANDA")
        assert "Response data item missing 'id' field" in str(excinfo.value)

    def test_fetch_with_original_response_format(self, sample_logical_router_dict):
        """Test fetch method with original response format (direct object with id field)."""
        self.mock_scm.get.return_value = sample_logical_router_dict

        result = self.client.fetch(
            name=sample_logical_router_dict["name"],
            folder=sample_logical_router_dict["folder"],
        )

        assert isinstance(result, LogicalRouterResponseModel)
        assert result.id == uuid.UUID(sample_logical_router_dict["id"])
        assert result.name == sample_logical_router_dict["name"]
        assert result.folder == sample_logical_router_dict["folder"]

        self.mock_scm.get.assert_called_once()
        call_args = self.mock_scm.get.call_args
        assert call_args[0][0] == self.client.ENDPOINT
        assert call_args[1]["params"]["name"] == sample_logical_router_dict["name"]
        assert call_args[1]["params"]["folder"] == sample_logical_router_dict["folder"]

    def test_fetch_with_list_response_format(self, sample_logical_router_dict):
        """Test fetch method with list response format (data array with objects)."""
        lr_data = sample_logical_router_dict.copy()

        self.mock_scm.get.return_value = {
            "data": [lr_data],
            "limit": 20,
            "offset": 0,
            "total": 1,
        }

        result = self.client.fetch(name=lr_data["name"], folder=lr_data["folder"])

        assert isinstance(result, LogicalRouterResponseModel)
        assert result.id == uuid.UUID(lr_data["id"])
        assert result.name == lr_data["name"]
        assert result.folder == lr_data["folder"]

    def test_fetch_with_multiple_objects_in_data(self, sample_logical_router_dict, monkeypatch):
        """Test fetch method when data array contains multiple objects."""
        from unittest.mock import MagicMock

        lr1 = sample_logical_router_dict.copy()
        lr1["id"] = str(uuid.uuid4())
        lr1["name"] = "LR-1"

        lr2 = sample_logical_router_dict.copy()
        lr2["id"] = str(uuid.uuid4())
        lr2["name"] = "LR-2"

        self.mock_scm.get.return_value = {
            "data": [lr1, lr2],
            "limit": 20,
            "offset": 0,
            "total": 2,
        }

        mock_warning = MagicMock()
        monkeypatch.setattr(self.client.logger, "warning", mock_warning)

        result = self.client.fetch(name=lr1["name"], folder=lr1["folder"])

        assert isinstance(result, LogicalRouterResponseModel)
        assert result.id == uuid.UUID(lr1["id"])
        assert result.name == lr1["name"]

        assert result.name != lr2["name"]
        assert result.id != uuid.UUID(lr2["id"])

        mock_warning.assert_called_once()
        call_args = mock_warning.call_args[0][0]
        assert "Multiple logical routers found" in call_args

    # --- Create with nested config tests ---

    def test_create_with_vrf_and_routing(self):
        """Test create with VRF and routing configuration."""
        response_dict = {
            "id": str(uuid.uuid4()),
            "name": "LR-Full",
            "folder": "PANDA",
            "routing_stack": "advanced",
            "vrf": [
                {
                    "name": "default",
                    "interface": ["ethernet1/1"],
                    "routing_table": {
                        "ip": {
                            "static_route": [
                                {
                                    "name": "default-route",
                                    "destination": "0.0.0.0/0",
                                    "nexthop": {"ip_address": "10.0.0.1"},
                                }
                            ]
                        }
                    },
                    "bgp": {
                        "enable": True,
                        "router_id": "10.0.0.1",
                        "local_as": "65000",
                        "peer_group": [
                            {
                                "name": "EBGP-Peers",
                                "enable": True,
                                "type": {"ebgp": {}},
                                "peer": [
                                    {
                                        "name": "ISP-1",
                                        "enable": True,
                                        "peer_as": "65001",
                                        "peer_address": {"ip": "10.0.1.1"},
                                    }
                                ],
                            }
                        ],
                    },
                    "ospf": {
                        "enable": True,
                        "router_id": "10.0.0.1",
                        "area": [
                            {
                                "name": "0.0.0.0",
                                "type": {"normal": {}},
                                "interface": [
                                    {
                                        "name": "ethernet1/1",
                                        "enable": True,
                                        "link_type": {"broadcast": {}},
                                    }
                                ],
                            }
                        ],
                    },
                    "ecmp": {
                        "enable": True,
                        "algorithm": {
                            "ip_hash": {
                                "src_only": False,
                                "use_port": True,
                                "hash_seed": 12345,
                            }
                        },
                        "max_path": 4,
                    },
                }
            ],
        }
        self.mock_scm.post.return_value = response_dict

        create_data = response_dict.copy()
        create_data.pop("id")

        result = self.client.create(create_data)

        assert isinstance(result, LogicalRouterResponseModel)
        assert result.name == "LR-Full"
        assert result.routing_stack.value == "advanced"
        assert len(result.vrf) == 1
        assert result.vrf[0].name == "default"
        assert result.vrf[0].bgp.enable is True
        assert result.vrf[0].ospf.enable is True
        assert result.vrf[0].ecmp.enable is True

    def test_create_minimal(self):
        """Test create with minimal configuration."""
        response_dict = {
            "id": str(uuid.uuid4()),
            "name": "LR-Minimal",
            "folder": "PANDA",
        }
        self.mock_scm.post.return_value = response_dict

        create_data = {"name": "LR-Minimal", "folder": "PANDA"}
        result = self.client.create(create_data)

        assert isinstance(result, LogicalRouterResponseModel)
        assert result.name == "LR-Minimal"
        assert result.folder == "PANDA"
        assert result.routing_stack is None
        assert result.vrf is None
