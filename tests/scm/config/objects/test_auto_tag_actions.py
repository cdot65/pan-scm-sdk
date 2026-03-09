# tests/scm/config/objects/test_auto_tag_actions.py

"""Tests for auto tag actions configuration objects."""

# Standard library imports
from unittest.mock import MagicMock

# External libraries
import pytest

# Local SDK imports
from scm.config.objects import AutoTagActions
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.objects import AutoTagActionResponseModel

# Import factories
from tests.factories.objects.auto_tag_actions import (
    AutoTagActionCreateApiFactory,
    AutoTagActionResponseFactory,
    AutoTagActionUpdateApiFactory,
)


@pytest.mark.usefixtures("load_env")
class TestAutoTagActionBase:
    """Base class for AutoTagAction tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm  # noqa
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = AutoTagActions(self.mock_scm, max_limit=5000)  # noqa


class TestAutoTagActionMaxLimit(TestAutoTagActionBase):
    """Tests for max_limit functionality."""

    def test_default_max_limit(self):
        """Test that default max_limit is set correctly."""
        client = AutoTagActions(self.mock_scm)  # noqa
        assert client.max_limit == AutoTagActions.DEFAULT_MAX_LIMIT
        assert client.max_limit == 2500

    def test_custom_max_limit(self):
        """Test setting a custom max_limit."""
        client = AutoTagActions(self.mock_scm, max_limit=1000)  # noqa
        assert client.max_limit == 1000

    def test_max_limit_setter(self):
        """Test the max_limit property setter."""
        client = AutoTagActions(self.mock_scm)  # noqa
        client.max_limit = 3000
        assert client.max_limit == 3000

    def test_invalid_max_limit_type(self):
        """Test that invalid max_limit type raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            AutoTagActions(self.mock_scm, max_limit="invalid")  # noqa
        assert "{'error': 'Invalid max_limit type'} - HTTP error: 400 - API error: E003" in str(
            exc_info.value
        )

    def test_max_limit_too_low(self):
        """Test that max_limit below 1 raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            AutoTagActions(self.mock_scm, max_limit=0)  # noqa
        assert "{'error': 'Invalid max_limit value'} - HTTP error: 400 - API error: E003" in str(
            exc_info.value
        )

    def test_max_limit_too_high(self):
        """Test that max_limit above ABSOLUTE_MAX_LIMIT raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            AutoTagActions(self.mock_scm, max_limit=6000)  # noqa
        assert "max_limit exceeds maximum allowed value" in str(exc_info.value)


class TestAutoTagActionList(TestAutoTagActionBase):
    """Tests for listing AutoTagAction objects."""

    def test_list_valid(self):
        """Test listing all auto tag actions without filters."""
        mock_response = {
            "data": [
                AutoTagActionResponseFactory(
                    name="TestAction1",
                    folder="Texas",
                ).model_dump(),
                AutoTagActionResponseFactory(
                    name="TestAction2",
                    folder="Texas",
                ).model_dump(),
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response
        existing = self.client.list(folder="Texas")

        self.mock_scm.get.assert_called_once_with(
            "/config/objects/v1/auto-tag-actions",
            params={
                "limit": 5000,
                "folder": "Texas",
                "offset": 0,
            },
        )
        assert isinstance(existing, list)
        assert len(existing) == 2
        assert existing[0].name == "TestAction1"
        assert existing[1].name == "TestAction2"

    def test_list_exact_match(self):
        """Test exact_match=True ensures only objects with the exact folder match are returned."""
        mock_response = {
            "data": [
                AutoTagActionResponseFactory.build(name="ExactMatch", folder="Texas").model_dump(),
                AutoTagActionResponseFactory.build(name="Inherited", folder="All").model_dump(),
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response
        result = self.client.list(folder="Texas", exact_match=True)
        assert len(result) == 1
        assert result[0].name == "ExactMatch"
        assert result[0].folder == "Texas"

    def test_list_exclude_folders(self):
        """Test that exclude_folders filters out the specified folders."""
        mock_response = {
            "data": [
                AutoTagActionResponseFactory.build(name="Action1", folder="Texas").model_dump(),
                AutoTagActionResponseFactory.build(name="Action2", folder="All").model_dump(),
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response
        result = self.client.list(folder="Texas", exclude_folders=["All"])
        assert len(result) == 1
        assert result[0].folder == "Texas"

    def test_list_exclude_snippets(self):
        """Test that exclude_snippets filters out the specified snippets."""
        mock_response = {
            "data": [
                AutoTagActionResponseFactory.build(
                    name="Action1", folder="Texas", snippet=None
                ).model_dump(),
                AutoTagActionResponseFactory.build(
                    name="Action2", folder="Texas", snippet="default"
                ).model_dump(),
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response
        result = self.client.list(folder="Texas", exclude_snippets=["default"])
        assert len(result) == 1
        assert result[0].name == "Action1"

    def test_list_exclude_devices(self):
        """Test that exclude_devices filters out the specified devices."""
        mock_response = {
            "data": [
                AutoTagActionResponseFactory.build(
                    name="Action1", folder="Texas", device=None
                ).model_dump(),
                AutoTagActionResponseFactory.build(
                    name="Action2", folder="Texas", device="DeviceA"
                ).model_dump(),
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }

        self.mock_scm.get.return_value = mock_response
        result = self.client.list(folder="Texas", exclude_devices=["DeviceA"])
        assert len(result) == 1
        assert result[0].name == "Action1"

    def test_list_empty_folder_error(self):
        """Test that empty folder raises MissingQueryParameterError."""
        with pytest.raises(MissingQueryParameterError):
            self.client.list(folder="")

    def test_list_no_container_error(self):
        """Test that no container raises InvalidObjectError."""
        with pytest.raises(InvalidObjectError):
            self.client.list()

    def test_list_multiple_containers_error(self):
        """Test that multiple containers raises InvalidObjectError."""
        with pytest.raises(InvalidObjectError):
            self.client.list(folder="Texas", snippet="MySnippet")

    def test_list_response_not_dict(self):
        """Test that non-dict response raises InvalidObjectError."""
        self.mock_scm.get.return_value = "not a dict"
        with pytest.raises(InvalidObjectError):
            self.client.list(folder="Texas")

    def test_list_response_missing_data(self):
        """Test that response missing 'data' raises InvalidObjectError."""
        self.mock_scm.get.return_value = {"total": 0}
        with pytest.raises(InvalidObjectError):
            self.client.list(folder="Texas")

    def test_list_response_data_not_list(self):
        """Test that response with non-list 'data' raises InvalidObjectError."""
        self.mock_scm.get.return_value = {"data": "not a list"}
        with pytest.raises(InvalidObjectError):
            self.client.list(folder="Texas")

    def test_list_pagination(self):
        """Test that pagination works correctly."""
        page1 = {
            "data": [
                AutoTagActionResponseFactory.build(name=f"Action{i}", folder="Texas").model_dump()
                for i in range(5000)
            ],
            "offset": 0,
            "total": 7000,
            "limit": 5000,
        }
        page2 = {
            "data": [
                AutoTagActionResponseFactory.build(name=f"Action{i}", folder="Texas").model_dump()
                for i in range(5000, 7000)
            ],
            "offset": 5000,
            "total": 7000,
            "limit": 5000,
        }

        self.mock_scm.get.side_effect = [page1, page2]
        result = self.client.list(folder="Texas")
        assert len(result) == 7000
        assert self.mock_scm.get.call_count == 2


class TestAutoTagActionCreate(TestAutoTagActionBase):
    """Tests for creating AutoTagAction objects."""

    def test_create_valid(self):
        """Test creating a valid auto tag action."""
        test_object = AutoTagActionCreateApiFactory.with_folder(
            name="TestAction",
            description="Test action",
        )

        mock_response = AutoTagActionResponseFactory.from_request(test_object)
        self.mock_scm.post.return_value = mock_response.model_dump()

        created = self.client.create(
            test_object.model_dump(exclude_unset=True),
        )

        self.mock_scm.post.assert_called_once()
        assert isinstance(created, AutoTagActionResponseModel)
        assert created.name == "TestAction"
        assert created.folder == "Texas"

    def test_create_with_snippet(self):
        """Test creating an auto tag action in a snippet container."""
        test_object = AutoTagActionCreateApiFactory.with_snippet(
            name="SnippetAction",
        )

        mock_response = AutoTagActionResponseFactory.from_request(test_object)
        self.mock_scm.post.return_value = mock_response.model_dump()

        created = self.client.create(
            test_object.model_dump(exclude_unset=True),
        )

        assert isinstance(created, AutoTagActionResponseModel)
        assert created.snippet == "TestSnippet"


class TestAutoTagActionGet(TestAutoTagActionBase):
    """Tests for getting AutoTagAction objects by ID."""

    def test_get_valid(self):
        """Test getting an auto tag action by ID."""
        mock_response = AutoTagActionResponseFactory(
            name="TestAction",
            folder="Texas",
        )
        self.mock_scm.get.return_value = mock_response.model_dump()

        object_id = str(mock_response.id)
        result = self.client.get(object_id)

        self.mock_scm.get.assert_called_once_with(
            f"/config/objects/v1/auto-tag-actions/{object_id}"
        )
        assert isinstance(result, AutoTagActionResponseModel)
        assert result.name == "TestAction"


class TestAutoTagActionUpdate(TestAutoTagActionBase):
    """Tests for updating AutoTagAction objects."""

    def test_update_valid(self):
        """Test updating an auto tag action."""
        update_data = AutoTagActionUpdateApiFactory(
            name="UpdatedAction",
            description="Updated description",
        )

        mock_response = AutoTagActionResponseFactory.from_request(update_data)
        self.mock_scm.put.return_value = mock_response.model_dump()

        result = self.client.update(update_data)

        self.mock_scm.put.assert_called_once()
        assert isinstance(result, AutoTagActionResponseModel)
        assert result.name == "UpdatedAction"


class TestAutoTagActionDelete(TestAutoTagActionBase):
    """Tests for deleting AutoTagAction objects."""

    def test_delete_valid(self):
        """Test deleting an auto tag action by ID."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"
        self.client.delete(object_id)

        self.mock_scm.delete.assert_called_once_with(
            f"/config/objects/v1/auto-tag-actions/{object_id}"
        )


class TestAutoTagActionFetch(TestAutoTagActionBase):
    """Tests for fetching AutoTagAction objects by name."""

    def test_fetch_valid(self):
        """Test fetching an auto tag action by name."""
        mock_response = AutoTagActionResponseFactory(
            name="TestAction",
            folder="Texas",
        ).model_dump()

        self.mock_scm.get.return_value = mock_response

        result = self.client.fetch(name="TestAction", folder="Texas")

        self.mock_scm.get.assert_called_once_with(
            "/config/objects/v1/auto-tag-actions",
            params={
                "folder": "Texas",
                "name": "TestAction",
            },
        )
        assert isinstance(result, AutoTagActionResponseModel)
        assert result.name == "TestAction"

    def test_fetch_empty_name_error(self):
        """Test that empty name raises MissingQueryParameterError."""
        with pytest.raises(MissingQueryParameterError):
            self.client.fetch(name="", folder="Texas")

    def test_fetch_empty_folder_error(self):
        """Test that empty folder raises MissingQueryParameterError."""
        with pytest.raises(MissingQueryParameterError):
            self.client.fetch(name="TestAction", folder="")

    def test_fetch_no_container_error(self):
        """Test that no container raises InvalidObjectError."""
        with pytest.raises(InvalidObjectError):
            self.client.fetch(name="TestAction")

    def test_fetch_response_not_dict(self):
        """Test that non-dict response raises InvalidObjectError."""
        self.mock_scm.get.return_value = "not a dict"
        with pytest.raises(InvalidObjectError):
            self.client.fetch(name="TestAction", folder="Texas")

    def test_fetch_response_missing_id(self):
        """Test that response missing 'id' raises InvalidObjectError."""
        self.mock_scm.get.return_value = {"name": "TestAction"}
        with pytest.raises(InvalidObjectError):
            self.client.fetch(name="TestAction", folder="Texas")
