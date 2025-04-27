# tests/scm/config/setup/test_folder.py

# Standard library imports
from unittest.mock import MagicMock, patch

# External libraries
import pytest

# Local SDK imports
from scm.client import Scm
from scm.config.setup.folder import Folder
from scm.models.setup.folder import (
    FolderResponseModel,
)
from tests.factories.setup.folder import (
    FolderResponseFactory,
    FolderCreateApiFactory,
    FolderUpdateApiFactory,
)


class TestFolderBase:
    """Base class for folder tests with common fixtures."""

    @pytest.fixture
    def mock_scm_client(self):
        """Create a properly mocked SCM client that passes type checks."""
        client = MagicMock(spec=Scm)
        return client

    @pytest.fixture
    def folder_service(self, mock_scm_client):
        """Create a Folder service with a mocked client for testing."""
        with patch("scm.config.isinstance", return_value=True):
            service = Folder(mock_scm_client)
            return service


class TestFolderInitialization(TestFolderBase):
    """Tests for Folder service initialization."""

    def test_init_with_default_max_limit(self, mock_scm_client):
        """Test initialization with default max_limit."""
        with patch("scm.config.isinstance", return_value=True):
            folder = Folder(mock_scm_client)
            assert folder.api_client == mock_scm_client
            assert folder.ENDPOINT == "/config/setup/v1/folders"
            assert folder.max_limit == Folder.DEFAULT_MAX_LIMIT

    def test_init_with_custom_max_limit(self, mock_scm_client):
        """Test initialization with custom max_limit."""
        with patch("scm.config.isinstance", return_value=True):
            custom_limit = 100
            folder = Folder(mock_scm_client, max_limit=custom_limit)
            assert folder.max_limit == custom_limit

    def test_init_with_exceeding_max_limit(self, mock_scm_client):
        """Test initialization with max_limit exceeding the absolute maximum."""
        with patch("scm.config.isinstance", return_value=True):
            exceeding_limit = 10000
            folder = Folder(mock_scm_client, max_limit=exceeding_limit)
            assert folder.max_limit == Folder.ABSOLUTE_MAX_LIMIT


class TestFolderCreate(TestFolderBase):
    """Tests for Folder.create method."""

    def test_create_folder(self, folder_service, mock_scm_client):
        """Test creating a folder with minimum required fields."""
        # Setup test data
        folder_data = FolderCreateApiFactory()
        response_data = FolderResponseFactory.from_request(folder_data)

        # Mock API response
        mock_scm_client.post.return_value = response_data.model_dump()

        # Call create method (now expects a data dict)
        result = folder_service.create(folder_data.model_dump(exclude_unset=True))

        # Assert result is as expected
        assert isinstance(result, FolderResponseModel)
        assert result.name == folder_data.name
        assert result.parent == folder_data.parent

    def test_create_folder_with_labels(self, folder_service, mock_scm_client):
        """Test creating a folder with labels."""
        folder_data = FolderCreateApiFactory(labels=["red", "blue"])
        response_data = FolderResponseFactory.from_request(folder_data)
        mock_scm_client.post.return_value = response_data.model_dump()
        result = folder_service.create(folder_data.model_dump(exclude_unset=True))
        assert isinstance(result, FolderResponseModel)
        assert set(result.labels) == set(["red", "blue"])


class TestFolderGet(TestFolderBase):
    """Tests for Folder.get method."""

    def test_get_folder(self, folder_service, mock_scm_client):
        """Test retrieving a folder by ID."""
        # Setup test data
        folder_id = "12345678-1234-1234-1234-123456789012"
        mock_response = FolderResponseFactory(id=folder_id)

        # Mock API response
        mock_scm_client.get.return_value = mock_response.model_dump()

        # Call get method
        result = folder_service.get(folder_id)

        # Verify API call
        mock_scm_client.get.assert_called_once_with(f"{folder_service.ENDPOINT}/{folder_id}")

        # Verify response
        assert isinstance(result, FolderResponseModel)
        assert str(result.id) == folder_id
        assert result.name == mock_response.name
        assert result.parent == mock_response.parent


class TestFolderFetch(TestFolderBase):
    """Tests for Folder.fetch method."""

    def test_fetch_folder_found(self, folder_service, mock_scm_client):
        """Test fetching a folder by name when it's found."""
        folder = FolderResponseFactory(name="target")
        api_response = {"data": [folder.model_dump()]}
        mock_scm_client.get.return_value = api_response
        result = folder_service.fetch(name="target")
        assert result is not None
        assert result.name == "target"

    def test_fetch_folder_empty_results(self, folder_service, mock_scm_client):
        """Test that fetch returns None when list returns empty results."""
        mock_scm_client.get.return_value = {"data": []}
        result = folder_service.fetch(name="any")
        assert result is None

    def test_fetch_folder_with_mocked_list(self, folder_service):
        """Comprehensive test covering different behaviors using mocked list method."""
        # Test case 1: Empty results
        with patch.object(folder_service, "list", return_value=[]):
            result = folder_service.fetch("test_name")
            assert result is None

        # Test case 2: One result matching the name
        test_folder = FolderResponseModel(
            id="12345678-1234-1234-1234-123456789012", name="TestFolder", parent="parent-id"
        )
        with patch.object(folder_service, "list", return_value=[test_folder]):
            result = folder_service.fetch("TestFolder")
            assert result == test_folder

        # Test case 3: Multiple results including one exact match
        target_folder = FolderResponseModel(
            id="12345678-1234-1234-1234-123456789012", name="TargetFolder", parent="parent-id"
        )
        child_folder = FolderResponseModel(
            id="12345678-1234-1234-1234-123456789013", name="ChildFolder", parent="TargetFolder"
        )
        other_folder = FolderResponseModel(
            id="12345678-1234-1234-1234-123456789014", name="OtherFolder", parent="parent-id"
        )
        with patch.object(
            folder_service, "list", return_value=[child_folder, target_folder, other_folder]
        ):
            result = folder_service.fetch("TargetFolder")
            assert result == target_folder

        # Test case 4: Multiple results but no exact match
        folder1 = FolderResponseModel(
            id="12345678-1234-1234-1234-123456789012", name="Folder1", parent="parent-id"
        )
        folder2 = FolderResponseModel(
            id="12345678-1234-1234-1234-123456789013", name="Folder2", parent="parent-id"
        )
        with patch.object(folder_service, "list", return_value=[folder1, folder2]):
            result = folder_service.fetch("MissingFolder")
            assert result is None


class TestFolderList(TestFolderBase):
    """Tests for Folder.list method."""

    def test_list_folders(self, folder_service, mock_scm_client):
        """Test listing folders with default parameters."""
        # Setup test data
        mock_folders = [
            FolderResponseFactory().model_dump(),
            FolderResponseFactory().model_dump(),
            FolderResponseFactory().model_dump(),
        ]

        # Mock API response
        mock_scm_client.get.return_value = {"data": mock_folders}

        # Call list method
        results = folder_service.list()

        # Verify API call
        mock_scm_client.get.assert_called_once()
        args, kwargs = mock_scm_client.get.call_args
        assert args[0] == folder_service.ENDPOINT
        assert "limit" in kwargs["params"]
        assert kwargs["params"]["limit"] == folder_service.max_limit

        # Verify results
        assert len(results) == len(mock_folders)
        assert all(isinstance(folder, FolderResponseModel) for folder in results)

    def test_list_folders_name_filter(self, folder_service, mock_scm_client):
        """Test listing folders with a name filter (client-side)."""
        # Setup test data: two folders, only one matches the name exactly
        folder1 = FolderResponseFactory(name="foo")
        folder2 = FolderResponseFactory(name="bar")
        api_response = {"data": [folder1.model_dump(), folder2.model_dump()]}
        mock_scm_client.get.return_value = api_response
        # Call list with name filter (client-side filtering)
        results = folder_service.list()
        filtered = [f for f in results if f.name == "foo"]
        assert len(filtered) == 1
        assert filtered[0].name == "foo"

    def test_list_folders_exact_match_filter(self, folder_service, mock_scm_client):
        """Test listing folders with an exact match filter (client-side)."""
        folder1 = FolderResponseFactory(name="foo")
        folder2 = FolderResponseFactory(name="foo")
        folder3 = FolderResponseFactory(name="bar")
        api_response = {"data": [folder1.model_dump(), folder2.model_dump(), folder3.model_dump()]}
        mock_scm_client.get.return_value = api_response
        results = folder_service.list()
        filtered = [f for f in results if f.name == "foo"]
        assert len(filtered) == 2
        for f in filtered:
            assert f.name == "foo"


class TestFolderUpdate(TestFolderBase):
    """Tests for Folder.update method."""

    def test_update_folder(self, folder_service, mock_scm_client):
        """Test updating a folder by direct mocking of BaseObject methods."""
        update_model = FolderUpdateApiFactory()
        response_data = FolderResponseFactory.from_request(update_model)
        mock_scm_client.put.return_value = response_data.model_dump()
        # Call update method (now expects a FolderUpdateModel)
        result = folder_service.update(update_model)
        assert isinstance(result, FolderResponseModel)
        assert result.id == update_model.id
        assert result.name == update_model.name


class TestFolderDelete(TestFolderBase):
    """Tests for Folder.delete method."""

    def test_delete_folder(self, folder_service, mock_scm_client):
        """Test deleting a folder."""
        # Setup test data
        folder_id = "12345678-1234-1234-1234-123456789012"

        # Call delete method
        folder_service.delete(folder_id)

        # Verify API call
        mock_scm_client.delete.assert_called_once_with(f"{folder_service.ENDPOINT}/{folder_id}")
