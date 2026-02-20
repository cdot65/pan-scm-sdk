"""Unit tests for the QosRule class."""

from unittest.mock import MagicMock
import uuid

import pytest

from scm.config.network import QosRule
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.network import (
    QosRulebase,
    QosRuleResponseModel,
    QosRuleUpdateModel,
)
from tests.factories.network.qos_rule import QosRuleMoveApiFactory


@pytest.fixture
def sample_qos_rule_dict():
    """Return a sample QoS rule dictionary."""
    return {
        "id": str(uuid.uuid4()),
        "name": "test-qos-rule",
        "folder": "Test Folder",
        "description": "A test QoS rule",
        "action": {"class": "class1"},
    }


@pytest.fixture
def sample_qos_rule_response(sample_qos_rule_dict):
    """Return a sample QosRuleResponseModel."""
    return QosRuleResponseModel(**sample_qos_rule_dict)


@pytest.mark.usefixtures("load_env")
class TestQosRuleBase:
    """Base class for QosRule tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = QosRule(self.mock_scm, max_limit=5000)


class TestQosRule(TestQosRuleBase):
    """Test suite for QosRule class."""

    def test_init(self):
        """Test initialization of QosRule class."""
        client = QosRule(self.mock_scm)
        assert client.api_client == self.mock_scm
        assert client.ENDPOINT == "/config/network/v1/qos-policy-rules"
        assert client.max_limit == client.DEFAULT_MAX_LIMIT

    def test_init_with_custom_max_limit(self):
        """Test initialization with custom max_limit."""
        client = QosRule(self.mock_scm, max_limit=1000)
        assert client.max_limit == 1000

    def test_init_with_invalid_max_limit(self):
        """Test initialization with invalid max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            QosRule(self.mock_scm, max_limit="invalid")
        assert "Invalid max_limit type" in str(excinfo.value)

    def test_init_with_negative_max_limit(self):
        """Test initialization with negative max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            QosRule(self.mock_scm, max_limit=-1)
        assert "Invalid max_limit value" in str(excinfo.value)

    def test_init_with_excessive_max_limit(self):
        """Test initialization with excessive max_limit."""
        with pytest.raises(InvalidObjectError) as excinfo:
            client = QosRule(self.mock_scm)
            client.max_limit = 10000
        assert "max_limit exceeds maximum allowed value" in str(excinfo.value)

    def test_create(self, sample_qos_rule_dict):
        """Test create method."""
        self.mock_scm.post.return_value = sample_qos_rule_dict

        result = self.client.create(
            {
                "name": sample_qos_rule_dict["name"],
                "folder": "ngfw-shared",
            }
        )

        self.mock_scm.post.assert_called_once()
        assert result.name == sample_qos_rule_dict["name"]

    def test_delete(self, sample_qos_rule_dict):
        """Test delete method."""
        object_id = sample_qos_rule_dict["id"]

        self.client.delete(object_id)

        self.mock_scm.delete.assert_called_once_with(
            f"/config/network/v1/qos-policy-rules/{object_id}"
        )

    def test_get(self, sample_qos_rule_dict):
        """Test get method."""
        self.mock_scm.get.return_value = sample_qos_rule_dict
        object_id = sample_qos_rule_dict["id"]

        result = self.client.get(object_id)

        # Check that correct API call was made
        expected_endpoint = f"{self.client.ENDPOINT}/{object_id}"
        self.mock_scm.get.assert_called_once_with(expected_endpoint)

        # Check result
        assert isinstance(result, QosRuleResponseModel)
        assert result.id == uuid.UUID(object_id)
        assert result.name == sample_qos_rule_dict["name"]

    def test_update(self, sample_qos_rule_dict):
        """Test update method."""
        self.mock_scm.put.return_value = sample_qos_rule_dict
        object_id = sample_qos_rule_dict["id"]

        # Create update model
        update_model = QosRuleUpdateModel(**sample_qos_rule_dict)

        result = self.client.update(update_model)

        # Check that correct API call was made
        expected_endpoint = f"{self.client.ENDPOINT}/{object_id}"
        self.mock_scm.put.assert_called_once()
        call_args = self.mock_scm.put.call_args
        assert call_args[0][0] == expected_endpoint

        # ID should not be in the payload since it's in the URL
        assert "id" not in call_args[1]["json"]

        # Check result
        assert isinstance(result, QosRuleResponseModel)
        assert result.id == uuid.UUID(object_id)
        assert result.name == sample_qos_rule_dict["name"]

    def test_list(self, sample_qos_rule_dict):
        """Test list method."""
        self.mock_scm.get.return_value = {
            "data": [sample_qos_rule_dict],
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
        assert isinstance(result[0], QosRuleResponseModel)
        assert result[0].name == sample_qos_rule_dict["name"]

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

    def test_list_pagination(self, sample_qos_rule_dict):
        """Test list method pagination."""
        rule1 = sample_qos_rule_dict.copy()
        rule1["id"] = str(uuid.uuid4())
        rule1["name"] = "rule1"

        rule2 = sample_qos_rule_dict.copy()
        rule2["id"] = str(uuid.uuid4())
        rule2["name"] = "rule2"

        self.mock_scm.get.side_effect = [
            {"data": [rule1], "limit": 1, "offset": 0, "total": 2},
            {"data": [rule2], "limit": 1, "offset": 1, "total": 2},
            {"data": [], "limit": 1, "offset": 2, "total": 2},
        ]

        self.client.max_limit = 1
        result = self.client.list(folder="Test Folder")

        assert self.mock_scm.get.call_count == 3
        assert len(result) == 2
        rule_names = [r.name for r in result]
        assert "rule1" in rule_names
        assert "rule2" in rule_names

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

    def test_list_with_raw_list_response(self, sample_qos_rule_dict):
        """Test list method when API returns raw list."""
        rule1 = sample_qos_rule_dict.copy()
        rule1["id"] = str(uuid.uuid4())
        rule1["name"] = "rule1"

        rule2 = sample_qos_rule_dict.copy()
        rule2["id"] = str(uuid.uuid4())
        rule2["name"] = "rule2"

        self.mock_scm.get.return_value = [rule1, rule2]

        result = self.client.list(folder="Test Folder")

        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(r, QosRuleResponseModel) for r in result)

    def test_fetch(self, sample_qos_rule_dict):
        """Test fetch method."""
        self.mock_scm.get.return_value = sample_qos_rule_dict

        result = self.client.fetch(name="test-qos-rule", folder="Test Folder")

        # Check that correct API call was made
        self.mock_scm.get.assert_called_once()
        call_args = self.mock_scm.get.call_args
        assert call_args[0][0] == self.client.ENDPOINT
        assert call_args[1]["params"]["name"] == "test-qos-rule"
        assert call_args[1]["params"]["folder"] == "Test Folder"

        # Check result
        assert isinstance(result, QosRuleResponseModel)
        assert result.name == sample_qos_rule_dict["name"]

    def test_fetch_with_empty_name(self):
        """Test fetch method with empty name parameter."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            self.client.fetch(name="", folder="Test Folder")
        assert '"name" is not allowed to be empty' in str(excinfo.value)

    def test_fetch_with_empty_folder(self):
        """Test fetch method with empty folder parameter."""
        with pytest.raises(MissingQueryParameterError) as excinfo:
            self.client.fetch(name="test-qos-rule", folder="")
        assert '"folder" is not allowed to be empty' in str(excinfo.value)

    def test_fetch_with_missing_container(self):
        """Test fetch method with missing container parameter."""
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-qos-rule")
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            excinfo.value
        )

    def test_fetch_with_invalid_response(self):
        """Test fetch method with invalid response."""
        self.mock_scm.get.return_value = {"name": "test-qos-rule"}

        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-qos-rule", folder="Test Folder")
        assert "Response has invalid structure" in str(excinfo.value)

    def test_fetch_response_errors(self):
        """Test fetch method error handling for invalid responses."""
        # Test non-list, non-dictionary response
        self.mock_scm.get.return_value = "not a dictionary"
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-qos-rule", folder="Test Folder")
        assert "Response is not a dictionary" in str(excinfo.value)

        # Test valid data list-style response
        valid_uuid = str(uuid.uuid4())
        self.mock_scm.get.return_value = {"data": [{"id": valid_uuid, "name": "test-qos-rule"}]}
        result = self.client.fetch(name="test-qos-rule", folder="Test Folder")
        assert isinstance(result, QosRuleResponseModel)
        assert result.id == uuid.UUID(valid_uuid)

        # Test empty data list
        self.mock_scm.get.return_value = {"data": []}
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-qos-rule", folder="Test Folder")
        assert "No matching QoS rule found" in str(excinfo.value)

        # Test data item without id field
        self.mock_scm.get.return_value = {
            "data": [{"name": "test-qos-rule", "folder": "Test Folder"}]
        }
        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="test-qos-rule", folder="Test Folder")
        assert "Response data item missing 'id' field" in str(excinfo.value)

    def test_fetch_with_raw_list_response(self, sample_qos_rule_dict):
        """Test fetch method when API returns raw list."""
        rule_data = sample_qos_rule_dict.copy()
        self.mock_scm.get.return_value = [rule_data]

        result = self.client.fetch(name=rule_data["name"], folder=rule_data["folder"])

        assert isinstance(result, QosRuleResponseModel)
        assert result.id == uuid.UUID(rule_data["id"])
        assert result.name == rule_data["name"]

    def test_fetch_with_raw_list_response_empty(self):
        """Test fetch method when API returns empty raw list."""
        self.mock_scm.get.return_value = []

        with pytest.raises(InvalidObjectError) as excinfo:
            self.client.fetch(name="nonexistent", folder="Test Folder")
        assert "No matching resource found" in str(excinfo.value)

    def test_fetch_with_raw_list_response_multiple(self, sample_qos_rule_dict, monkeypatch):
        """Test fetch method when API returns raw list with multiple items."""
        rule1 = sample_qos_rule_dict.copy()
        rule1["id"] = str(uuid.uuid4())
        rule1["name"] = "rule1"

        rule2 = sample_qos_rule_dict.copy()
        rule2["id"] = str(uuid.uuid4())
        rule2["name"] = "rule2"

        self.mock_scm.get.return_value = [rule1, rule2]

        mock_warning = MagicMock()
        monkeypatch.setattr(self.client.logger, "warning", mock_warning)

        result = self.client.fetch(name="rule1", folder="Test Folder")

        assert isinstance(result, QosRuleResponseModel)
        assert result.id == uuid.UUID(rule1["id"])
        mock_warning.assert_called_once()

    def test_list_with_exact_match(self, sample_qos_rule_dict):
        """Test list with exact_match filtering."""
        other = sample_qos_rule_dict.copy()
        other["id"] = str(uuid.uuid4())
        other["folder"] = "Other Folder"
        self.mock_scm.get.return_value = {
            "data": [sample_qos_rule_dict, other],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }

        result = self.client.list(folder="Test Folder", exact_match=True)

        assert len(result) == 1
        assert result[0].folder == "Test Folder"

    def test_list_with_exclude_folders(self, sample_qos_rule_dict):
        """Test list with exclude_folders filtering."""
        self.mock_scm.get.return_value = {
            "data": [sample_qos_rule_dict],
            "offset": 0,
            "total": 1,
            "limit": 200,
        }

        result = self.client.list(folder="Test Folder", exclude_folders=["Test Folder"])

        assert len(result) == 0

    def test_list_with_exclude_snippets(self, sample_qos_rule_dict):
        """Test list with exclude_snippets filtering."""
        item = sample_qos_rule_dict.copy()
        item["snippet"] = "TestSnippet"
        item.pop("folder", None)
        self.mock_scm.get.return_value = {"data": [item], "offset": 0, "total": 1, "limit": 200}

        result = self.client.list(snippet="TestSnippet", exclude_snippets=["TestSnippet"])

        assert len(result) == 0

    def test_list_with_exclude_devices(self, sample_qos_rule_dict):
        """Test list with exclude_devices filtering."""
        item = sample_qos_rule_dict.copy()
        item["device"] = "TestDevice"
        item.pop("folder", None)
        self.mock_scm.get.return_value = {"data": [item], "offset": 0, "total": 1, "limit": 200}

        result = self.client.list(device="TestDevice", exclude_devices=["TestDevice"])

        assert len(result) == 0

    def test_fetch_with_data_array_multiple_results(self, monkeypatch):
        """Test fetch when API returns data array with multiple results."""
        rule1 = {"id": str(uuid.uuid4()), "name": "rule1", "folder": "Test Folder"}
        rule2 = {"id": str(uuid.uuid4()), "name": "rule1", "folder": "Test Folder"}
        self.mock_scm.get.return_value = {"data": [rule1, rule2]}

        mock_warning = MagicMock()
        monkeypatch.setattr(self.client.logger, "warning", mock_warning)

        result = self.client.fetch(name="rule1", folder="Test Folder")

        assert isinstance(result, QosRuleResponseModel)
        assert result.id == uuid.UUID(rule1["id"])
        mock_warning.assert_called_once()


class TestQosRuleMove(TestQosRuleBase):
    """Tests for moving QoS Rule objects."""

    def test_move_to_top(self):
        """Test moving a rule to the top."""
        source_rule = "123e4567-e89b-12d3-a456-426655440000"
        move_data = {
            "destination": "top",
            "rulebase": "pre",
        }

        self.mock_scm.post.return_value = None
        self.client.move(source_rule, move_data)

        self.mock_scm.post.assert_called_once_with(
            f"/config/network/v1/qos-policy-rules/{source_rule}:move",
            json=move_data,
        )

    def test_move_to_bottom(self):
        """Test moving a rule to the bottom."""
        source_rule = "123e4567-e89b-12d3-a456-426655440000"
        move_data = {
            "destination": "bottom",
            "rulebase": "post",
        }

        self.mock_scm.post.return_value = None
        self.client.move(source_rule, move_data)

        self.mock_scm.post.assert_called_once_with(
            f"/config/network/v1/qos-policy-rules/{source_rule}:move",
            json=move_data,
        )

    def test_move_before_rule(self):
        """Test moving a rule before another rule."""
        source_rule = "123e4567-e89b-12d3-a456-426655440000"
        dest_rule_id = "987fcdeb-54ba-3210-9876-fedcba098765"
        move_config = QosRuleMoveApiFactory.before_rule(
            dest_rule=dest_rule_id,
            rulebase=QosRulebase.PRE,
        )

        # Get the data as a dictionary
        move_data = move_config.model_dump(exclude_none=True)

        # Expected data - with destination_rule as string
        expected_data = move_data.copy()
        if "destination_rule" in expected_data:
            expected_data["destination_rule"] = str(expected_data["destination_rule"])

        self.mock_scm.post.return_value = None
        self.client.move(source_rule, move_data)

        self.mock_scm.post.assert_called_once_with(
            f"/config/network/v1/qos-policy-rules/{source_rule}:move",
            json=expected_data,
        )

    def test_move_after_rule(self):
        """Test moving a rule after another rule."""
        source_rule = "123e4567-e89b-12d3-a456-426655440000"
        dest_rule_id = "987fcdeb-54ba-3210-9876-fedcba098765"
        move_config = QosRuleMoveApiFactory.after_rule(
            dest_rule=dest_rule_id,
            rulebase=QosRulebase.PRE,
        )

        # Get the data as a dictionary
        move_data = move_config.model_dump(exclude_none=True)

        # Expected data - with destination_rule as string
        expected_data = move_data.copy()
        if "destination_rule" in expected_data:
            expected_data["destination_rule"] = str(expected_data["destination_rule"])

        self.mock_scm.post.return_value = None
        self.client.move(source_rule, move_data)

        self.mock_scm.post.assert_called_once_with(
            f"/config/network/v1/qos-policy-rules/{source_rule}:move",
            json=expected_data,
        )
