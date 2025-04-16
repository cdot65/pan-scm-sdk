# tests/scm/config/setup/test_folder.py

# Standard library imports
import json
from uuid import UUID

# External libraries
import pytest
from unittest.mock import MagicMock, patch

# Local SDK imports
from scm.client import Scm
from scm.config.setup.folder import Folder
from scm.models.setup.folder import (
    FolderCreateModel,
    FolderResponseModel,
    FolderUpdateModel,
)
from tests.factories.setup.folder import (
    FolderCreateApiFactory,
    FolderCreateModelFactory,
    FolderResponseFactory,
    FolderResponseModelFactory,
    FolderUpdateApiFactory,
    FolderUpdateModelFactory,
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
        
        # Call create method
        result = folder_service.create(
            name=folder_data.name,
            parent=folder_data.parent,
            description=folder_data.description,
            labels=folder_data.labels,
            snippets=folder_data.snippets,
        )
        
        # Verify API call
        mock_scm_client.post.assert_called_once()
        args, kwargs = mock_scm_client.post.call_args
        assert args[0] == folder_service.ENDPOINT
        
        # Verify request payload
        payload = kwargs["json"]
        assert payload["name"] == folder_data.name
        assert payload["parent"] == folder_data.parent
        
        # Verify response
        assert isinstance(result, FolderResponseModel)
        assert result.name == folder_data.name
        assert result.parent == folder_data.parent
        assert result.description == folder_data.description

    def test_create_folder_with_labels(self, folder_service, mock_scm_client):
        """Test creating a folder with labels."""
        # Setup test data
        labels = ["test", "development"]
        folder_data = FolderCreateApiFactory.with_labels(labels=labels)
        response_data = FolderResponseFactory.from_request(folder_data)
        
        # Mock API response
        mock_scm_client.post.return_value = response_data.model_dump()
        
        # Call create method
        result = folder_service.create(
            name=folder_data.name,
            parent=folder_data.parent,
            description=folder_data.description,
            labels=folder_data.labels,
        )
        
        # Verify request includes labels
        args, kwargs = mock_scm_client.post.call_args
        assert kwargs["json"]["labels"] == labels
        
        # Verify response includes labels
        assert result.labels == labels


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
        # Setup test data
        folder_name = "TestFolder"
        mock_folders = [
            FolderResponseFactory(name=folder_name).model_dump(),  # Exact match
            FolderResponseFactory(name="ChildFolder", parent=folder_name).model_dump(),  # Child folder
            FolderResponseFactory(name="AnotherFolder").model_dump(),  # Unrelated folder
        ]
        
        # Mock API response
        mock_scm_client.get.return_value = {"data": mock_folders}
        
        # Call fetch method
        result = folder_service.fetch(folder_name)
        
        # Verify API call
        mock_scm_client.get.assert_called_once()
        args, kwargs = mock_scm_client.get.call_args
        assert args[0] == folder_service.ENDPOINT
        assert kwargs["params"]["name"] == folder_name  # Name should be in params
        
        # Verify result
        assert isinstance(result, FolderResponseModel)
        assert result.name == folder_name

    def test_fetch_folder_not_found(self, folder_service, mock_scm_client):
        """Test fetching a folder when no match exists."""
        # Setup test data with folders but no exact match
        folder_name = "NonExistentFolder"
        mock_folders = [
            FolderResponseFactory(name="SomeFolder").model_dump(),
            FolderResponseFactory(name="AnotherFolder").model_dump(),
        ]
        
        # Mock API response
        mock_scm_client.get.return_value = {"data": mock_folders}
        
        # Call fetch method
        result = folder_service.fetch(folder_name)
        
        # Should return None when no match is found
        assert result is None

    def test_fetch_folder_empty_results(self, folder_service):
        """Test that fetch returns None when list returns empty results."""
        # Mock the list method to return an empty list
        with patch.object(folder_service, 'list') as mock_list:
            # Configure mock to return empty list
            mock_list.return_value = []
            
            # Test fetch returns None for empty results
            result = folder_service.fetch("any_name")
            assert result is None
            
            # Verify call
            mock_list.assert_called_once_with(name="any_name")

    def test_fetch_folder_with_mocked_list(self, folder_service):
        """Comprehensive test covering different behaviors using mocked list method."""
        # Test case 1: Empty results
        with patch.object(folder_service, 'list', return_value=[]):
            result = folder_service.fetch("test_name")
            assert result is None
        
        # Test case 2: One result matching the name
        test_folder = FolderResponseModel(
            id="12345678-1234-1234-1234-123456789012",
            name="TestFolder",
            parent="parent-id"
        )
        with patch.object(folder_service, 'list', return_value=[test_folder]):
            result = folder_service.fetch("TestFolder")
            assert result == test_folder
        
        # Test case 3: Multiple results including one exact match
        target_folder = FolderResponseModel(
            id="12345678-1234-1234-1234-123456789012",
            name="TargetFolder",
            parent="parent-id"
        )
        child_folder = FolderResponseModel(
            id="12345678-1234-1234-1234-123456789013",
            name="ChildFolder",
            parent="TargetFolder"
        )
        other_folder = FolderResponseModel(
            id="12345678-1234-1234-1234-123456789014",
            name="OtherFolder",
            parent="parent-id"
        )
        with patch.object(folder_service, 'list', return_value=[child_folder, target_folder, other_folder]):
            result = folder_service.fetch("TargetFolder")
            assert result == target_folder
        
        # Test case 4: Multiple results but no exact match
        folder1 = FolderResponseModel(
            id="12345678-1234-1234-1234-123456789012",
            name="Folder1",
            parent="parent-id"
        )
        folder2 = FolderResponseModel(
            id="12345678-1234-1234-1234-123456789013",
            name="Folder2",
            parent="parent-id"
        )
        with patch.object(folder_service, 'list', return_value=[folder1, folder2]):
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
        """Test listing folders with name filter."""
        # Setup test data
        mock_folders = [
            FolderResponseFactory().model_dump(),
            FolderResponseFactory().model_dump(),
        ]
        
        # Mock API response
        mock_scm_client.get.return_value = {"data": mock_folders}
        
        # Call list method with name parameter
        folder_service.list(name="test")
        
        # Verify API call includes name parameter
        args, kwargs = mock_scm_client.get.call_args
        assert "name" in kwargs["params"]
        assert kwargs["params"]["name"] == "test"

    def test_list_folders_parent_filter(self, folder_service, mock_scm_client):
        """Test listing folders with parent filter."""
        # Setup test data
        mock_folders = [
            FolderResponseFactory().model_dump(),
            FolderResponseFactory().model_dump(),
        ]
        
        # Mock API response
        mock_scm_client.get.return_value = {"data": mock_folders}
        
        # Call list method with parent parameter
        folder_service.list(parent="parent_id")
        
        # Verify API call includes parent parameter
        args, kwargs = mock_scm_client.get.call_args
        assert "parent" in kwargs["params"]
        assert kwargs["params"]["parent"] == "parent_id"

    def test_list_folders_exact_match_filter(self, folder_service, mock_scm_client):
        """Test listing folders with exact_match=True filter."""
        # Setup test data
        folder_name = "ExactMatchFolder"
        mock_folders = [
            FolderResponseFactory(name=folder_name).model_dump(),
            FolderResponseFactory(name="AnotherFolder").model_dump(),
        ]
        
        # Mock API response
        mock_scm_client.get.return_value = {"data": mock_folders}
        
        # Call list method with exact_match=True
        results = folder_service.list(name=folder_name, exact_match=True)
        
        # Verify results are filtered client-side
        assert len(results) == 1
        assert results[0].name == folder_name


class TestFolderUpdate(TestFolderBase):
    """Tests for Folder.update method."""

    def test_update_folder(self, folder_service, mock_scm_client):
        """Test updating a folder by direct mocking of BaseObject methods."""
        # Setup test data
        folder_id = "12345678-1234-1234-1234-123456789012"
        
        # Create patchers for BaseObject methods
        with patch('scm.config.BaseObject.get') as mock_get, \
             patch('scm.config.BaseObject.update') as mock_update:
            
            # Setup mock data
            existing_folder = {
                "id": folder_id,
                "name": "Original Folder",
                "parent": "parent-id",
                "description": "Original description",
                "labels": ["label1", "label2"],
                "snippets": ["snippet1", "snippet2"]
            }
            
            updated_folder = {
                "id": folder_id,
                "name": "Updated Folder",
                "parent": "parent-id",
                "description": "Updated description",
                "labels": ["label1", "label2"],
                "snippets": ["snippet1", "snippet2"]
            }
            
            # Configure mocks
            mock_get.return_value = existing_folder
            mock_update.return_value = updated_folder
            
            # Call update method
            result = folder_service.update(
                folder_id=folder_id,
                name="Updated Folder",
                description="Updated description"
            )
            
            # Verify get was called with correct ID
            mock_get.assert_called_once_with(folder_id)
            
            # Verify update was called with correct data
            update_data = mock_update.call_args[0][0]
            assert str(update_data["id"]) == folder_id  # Convert UUID to string for comparison
            assert update_data["name"] == "Updated Folder"
            assert update_data["description"] == "Updated description"
            
            # Verify result
            assert isinstance(result, FolderResponseModel)
            assert str(result.id) == folder_id
            assert result.name == "Updated Folder"
            assert result.description == "Updated description"


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
