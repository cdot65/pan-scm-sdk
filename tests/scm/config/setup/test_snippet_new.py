# tests/scm/config/setup/test_snippet_new.py

# Standard library imports
from unittest.mock import MagicMock, patch
from uuid import UUID

# External libraries
import pytest

# Local SDK imports
from scm.client import Scm
from scm.config.setup.snippet import Snippet
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.setup.snippet_models import (
    FolderReference,
    SnippetBaseModel,
    SnippetCreateModel,
    SnippetResponseModel,
    SnippetUpdateModel,
)
from tests.factories.setup.snippet import (
    FolderReferenceFactory,
    SnippetCreateModelFactory,
    SnippetResponseFactory,
    SnippetResponseModelFactory,
    SnippetUpdateModelFactory,
)


class TestFolderReference:
    """Tests for the FolderReference model."""

    def test_valid_construction(self):
        """Test that a valid FolderReference can be constructed."""
        data = {"id": "123e4567-e89b-12d3-a456-426614174000", "name": "test-folder"}

        model = FolderReference(**data)

        assert model.id == UUID(data["id"])
        assert model.name == data["name"]

    def test_name_validation(self):
        """Test that the name cannot be empty."""
        data = {"id": "123e4567-e89b-12d3-a456-426614174000", "name": ""}

        with pytest.raises(ValueError) as excinfo:
            FolderReference(**data)

        assert "name" in str(excinfo.value)
        assert "empty" in str(excinfo.value)


class TestSnippetBaseModel:
    """Tests for the SnippetBaseModel."""

    def test_valid_construction(self):
        """Test that a valid SnippetBaseModel can be constructed."""
        data = SnippetCreateModelFactory.build_valid()

        model = SnippetBaseModel(**data)

        assert model.name == data["name"]
        assert model.description == data["description"]
        assert model.labels == data["labels"]
        assert model.enable_prefix == data["enable_prefix"]

    def test_minimal_construction(self):
        """Test that a minimal SnippetBaseModel can be constructed."""
        data = {"name": "minimal_snippet"}

        model = SnippetBaseModel(**data)

        assert model.name == "minimal_snippet"
        assert model.description is None
        assert model.labels is None
        assert model.enable_prefix is None

    def test_name_validation(self):
        """Test that the name is validated."""
        with pytest.raises(ValueError) as excinfo:
            SnippetBaseModel(name="")

        assert "name" in str(excinfo.value)
        assert "empty" in str(excinfo.value)


class TestSnippetCreateModel:
    """Tests for the SnippetCreateModel."""

    def test_valid_construction(self):
        """Test that a valid SnippetCreateModel can be constructed."""
        data = SnippetCreateModelFactory.build_valid()

        model = SnippetCreateModel(**data)

        assert model.name == data["name"]
        assert model.description == data["description"]
        assert model.labels == data["labels"]
        assert model.enable_prefix == data["enable_prefix"]

    def test_required_fields(self):
        """Test that SnippetCreateModel requires name."""
        data = SnippetCreateModelFactory.build_without_name()

        with pytest.raises(ValueError) as excinfo:
            SnippetCreateModel(**data)

        assert "name" in str(excinfo.value)


class TestSnippetUpdateModel:
    """Tests for the SnippetUpdateModel."""

    def test_valid_construction(self):
        """Test that a valid SnippetUpdateModel can be constructed."""
        data = SnippetUpdateModelFactory.build_valid()

        model = SnippetUpdateModel(**data)

        assert model.id == UUID(data["id"])
        assert model.name == data["name"]
        assert model.description == data["description"]
        assert model.labels == data["labels"]
        assert model.enable_prefix == data["enable_prefix"]

    def test_required_fields(self):
        """Test that SnippetUpdateModel requires an id."""
        data = SnippetUpdateModelFactory.build_without_id()

        with pytest.raises(ValueError) as excinfo:
            SnippetUpdateModel(**data)

        assert "id" in str(excinfo.value)


class TestSnippetResponseModel:
    """Tests for the SnippetResponseModel."""

    def test_valid_construction(self):
        """Test that a valid SnippetResponseModel can be constructed."""
        data = SnippetResponseModelFactory.build_valid()

        model = SnippetResponseModel(**data)

        assert model.id == UUID(data["id"])
        assert model.name == data["name"]
        assert model.description == data["description"]
        assert model.labels == data["labels"]
        assert model.enable_prefix == data["enable_prefix"]
        assert model.type == data["type"]
        assert model.display_name == data["display_name"]
        assert model.last_update == data["last_update"]
        assert model.created_in == data["created_in"]
        assert model.shared_in == data["shared_in"]
        assert len(model.folders) == len(data["folders"])

    def test_with_folders(self):
        """Test construction with folders."""
        data = SnippetResponseModelFactory.build_with_folders(folder_count=2)

        model = SnippetResponseModel(**data)

        assert len(model.folders) == 2
        for folder in model.folders:
            assert isinstance(folder, FolderReference)


class TestSnippetBase:
    """Base class for Snippet service tests with common fixtures."""

    @pytest.fixture
    def mock_scm_client(self):
        """Create a properly mocked SCM client that passes type checks."""
        client = MagicMock(spec=Scm)
        return client

    @pytest.fixture
    def snippet_service(self, mock_scm_client):
        """Create a Snippet service with a mocked client for testing."""
        with patch("scm.config.isinstance", return_value=True):
            service = Snippet(mock_scm_client)
            return service


class TestSnippetInitialization(TestSnippetBase):
    """Tests for Snippet service initialization."""

    def test_init_with_default_max_limit(self, mock_scm_client):
        """Test initialization with default max_limit."""
        with patch("scm.config.isinstance", return_value=True):
            snippet = Snippet(mock_scm_client)
            assert snippet.api_client == mock_scm_client
            assert snippet.ENDPOINT == "/config/setup/v1/snippets"
            assert snippet.max_limit == Snippet.DEFAULT_MAX_LIMIT

    def test_init_with_custom_max_limit(self, mock_scm_client):
        """Test initialization with custom max_limit."""
        with patch("scm.config.isinstance", return_value=True):
            custom_limit = 1000
            snippet = Snippet(mock_scm_client, max_limit=custom_limit)
            assert snippet.max_limit == custom_limit

    def test_init_with_exceeding_max_limit(self, mock_scm_client):
        """Test initialization with max_limit exceeding the absolute maximum."""
        with patch("scm.config.isinstance", return_value=True):
            exceeding_limit = Snippet.ABSOLUTE_MAX_LIMIT + 1000
            snippet = Snippet(mock_scm_client, max_limit=exceeding_limit)
            assert snippet.max_limit == Snippet.ABSOLUTE_MAX_LIMIT


class TestSnippetCreate(TestSnippetBase):
    """Tests for Snippet.create method."""

    def test_create_snippet(self, snippet_service, mock_scm_client):
        """Test creating a snippet with minimum required fields."""
        # Setup mock response
        mock_response = SnippetResponseFactory.build()
        mock_scm_client.post.return_value = mock_response

        # Create the snippet
        result = snippet_service.create(name="test_snippet")

        # Assert the client was called correctly
        mock_scm_client.post.assert_called_once()
        call_args = mock_scm_client.post.call_args
        assert call_args[0][0] == "/config/setup/v1/snippets"
        assert call_args[1]["json"]["name"] == "test_snippet"

        # Assert the result is a SnippetResponseModel
        assert isinstance(result, SnippetResponseModel)
        assert result.name == mock_response["name"]
        assert str(result.id) == mock_response["id"]

    def test_create_snippet_with_all_fields(self, snippet_service, mock_scm_client):
        """Test creating a snippet with all fields."""
        # Setup mock response
        mock_response = SnippetResponseFactory.build()
        mock_scm_client.post.return_value = mock_response

        # Create the snippet with all fields
        result = snippet_service.create(
            name="test_snippet",
            description="Test description",
            labels=["tag1", "tag2"],
            enable_prefix=True,
        )

        # Assert the client was called correctly
        mock_scm_client.post.assert_called_once()
        call_args = mock_scm_client.post.call_args
        assert call_args[0][0] == "/config/setup/v1/snippets"
        payload = call_args[1]["json"]
        assert payload["name"] == "test_snippet"
        assert payload["description"] == "Test description"
        assert payload["labels"] == ["tag1", "tag2"]
        assert payload["enable_prefix"] is True

        # Assert the result is a SnippetResponseModel
        assert isinstance(result, SnippetResponseModel)

    def test_create_snippet_with_invalid_data(self, snippet_service):
        """Test creating a snippet with invalid data."""
        # Test with empty name
        with pytest.raises(InvalidObjectError):
            snippet_service.create(name="")

        # Test with None name
        with pytest.raises(InvalidObjectError):
            snippet_service.create(name=None)

        # Test with whitespace-only name
        with pytest.raises(InvalidObjectError):
            snippet_service.create(name="   ")


class TestSnippetGet(TestSnippetBase):
    """Tests for Snippet.get method."""

    def test_get_snippet(self, snippet_service, mock_scm_client):
        """Test retrieving a snippet by ID."""
        # Setup mock response
        mock_response = SnippetResponseFactory.build()
        mock_scm_client.get.return_value = mock_response
        snippet_id = "123e4567-e89b-12d3-a456-426614174000"

        # Get the snippet
        result = snippet_service.get(snippet_id)

        # Assert the client was called correctly
        mock_scm_client.get.assert_called_once_with(f"/config/setup/v1/snippets/{snippet_id}")

        # Assert the result is a SnippetResponseModel
        assert isinstance(result, SnippetResponseModel)
        assert str(result.id) == mock_response["id"]
        assert result.name == mock_response["name"]

    def test_get_nonexistent_snippet(self, snippet_service, mock_scm_client):
        """Test retrieving a snippet that doesn't exist."""
        # Setup mock client to raise APIError with 404 status
        error = APIError("Snippet not found")
        error.http_status_code = 404
        mock_scm_client.get.side_effect = error
        snippet_id = "nonexistent-id"

        # Try to get the nonexistent snippet
        with pytest.raises(ObjectNotPresentError):
            snippet_service.get(snippet_id)

        # Assert the client was called correctly
        mock_scm_client.get.assert_called_once_with(f"/config/setup/v1/snippets/{snippet_id}")

    def test_get_with_general_error(self, snippet_service, mock_scm_client):
        """Test get with a non-404 exception."""
        object_id = "123e4567-e89b-12d3-a456-426614174000"
        
        # Create a non-404 error
        error = APIError("General server error")
        error.http_status_code = 500
        mock_scm_client.get.side_effect = error
        
        # Should re-raise the error
        with pytest.raises(APIError):
            snippet_service.get(object_id)


class TestSnippetFetch(TestSnippetBase):
    """Tests for Snippet.fetch method."""

    def test_fetch_snippet_found(self, snippet_service, mock_scm_client):
        """Test fetching a snippet by name when it's found."""
        # Setup mock response for direct query
        mock_response = {"data": [SnippetResponseFactory.build(name="test_snippet")]}
        mock_scm_client.get.return_value = mock_response

        # Fetch the snippet
        result = snippet_service.fetch("test_snippet")

        # Assert the client was called correctly
        mock_scm_client.get.assert_called_once()
        assert mock_scm_client.get.call_args[0][0] == "/config/setup/v1/snippets"
        assert mock_scm_client.get.call_args[1]["params"]["name"] == "test_snippet"

        # Assert the result is a SnippetResponseModel
        assert isinstance(result, SnippetResponseModel)
        assert result.name == "test_snippet"

    def test_fetch_snippet_not_found(self, snippet_service, mock_scm_client):
        """Test fetching a snippet by name when it's not found."""
        # Setup mock response for direct query with empty results
        mock_response = {"data": []}
        mock_scm_client.get.return_value = mock_response

        # Fetch the non-existent snippet
        result = snippet_service.fetch("nonexistent")

        # Assert the client was called correctly
        mock_scm_client.get.assert_called_once()
        
        # Assert the result is None
        assert result is None

    def test_fetch_multiple_matches(self, snippet_service, mock_scm_client):
        """Test fetching a snippet when multiple matches are found."""
        # Setup mock response with multiple results
        mock_response = {"data": [
            SnippetResponseFactory.build(name="same_name"),
            SnippetResponseFactory.build(name="same_name"),
        ]}
        mock_scm_client.get.return_value = mock_response

        # Should raise error for multiple matches
        with pytest.raises(APIError) as excinfo:
            snippet_service.fetch("same_name")
        
        # The message contains the text, even if str() doesn't show it
        assert "Multiple snippets" in excinfo.value.message

    def test_fetch_fallback_to_list(self, snippet_service, mock_scm_client):
        """Test fallback to list method when direct fetch fails with 404."""
        # Setup mock response for direct query to fail with 404
        error = APIError("Not found")
        error.http_status_code = 404
        mock_scm_client.get.side_effect = error
        
        # Setup mock response for list method fallback
        with patch.object(snippet_service, "list") as mock_list:
            mock_list.return_value = [SnippetResponseModel.model_validate(
                SnippetResponseFactory.build(name="test_snippet")
            )]
            
            # Fetch the snippet
            result = snippet_service.fetch("test_snippet")
            
            # Assert list was called with correct parameters
            mock_list.assert_called_once_with(name="test_snippet", exact_match=True)
            
            # Assert the result is a SnippetResponseModel
            assert isinstance(result, SnippetResponseModel)
            assert result.name == "test_snippet"

    def test_fetch_invalid_response_format(self, snippet_service, mock_scm_client):
        """Test handling of invalid response format."""
        # Setup mock response with unexpected format
        mock_scm_client.get.return_value = "not a dict or list"
        
        # Fetch should return None for unexpected format
        result = snippet_service.fetch("test_snippet")
        assert result is None


class TestSnippetList(TestSnippetBase):
    """Tests for Snippet.list method."""

    def test_list_snippets(self, snippet_service, mock_scm_client):
        """Test listing snippets with default parameters."""
        # Setup mock response with valid snippet data
        mock_data = [SnippetResponseFactory.build() for _ in range(3)]
        
        # Patch the _get_paginated_results method
        with patch.object(snippet_service, "_get_paginated_results", return_value=mock_data):
            # List the snippets
            results = snippet_service.list()
            
            # Assert _get_paginated_results was called correctly
            snippet_service._get_paginated_results.assert_called_once()
            call_args = snippet_service._get_paginated_results.call_args
            assert call_args[1]["endpoint"] == "/config/setup/v1/snippets"
            assert call_args[1]["params"] == {}
            assert call_args[1]["limit"] == snippet_service.max_limit
            assert call_args[1]["offset"] == 0
            
            # Assert the results are correct
            assert len(results) == 3
            for result in results:
                assert isinstance(result, SnippetResponseModel)

    def test_list_snippets_name_filter(self, snippet_service, mock_scm_client):
        """Test listing snippets with name filter."""
        # Setup mock response with valid snippet data
        mock_data = [SnippetResponseFactory.build(name="test_snippet")]
        
        # Patch the _get_paginated_results method
        with patch.object(snippet_service, "_get_paginated_results", return_value=mock_data):
            # List the snippets with name filter
            results = snippet_service.list(name="test_snippet")
            
            # Assert parameters were passed correctly
            call_args = snippet_service._get_paginated_results.call_args
            assert call_args[1]["params"] == {"name": "test_snippet"}
            
            # Verify results
            assert len(results) == 1
            assert results[0].name == "test_snippet"

    def test_list_snippets_exact_match_filter(self, snippet_service, mock_scm_client):
        """Test listing snippets with exact_match=True filter."""
        # Setup mock response with 3 snippets, one matching exactly
        snippet1 = SnippetResponseFactory.build(name="test_snippet_1")
        snippet2 = SnippetResponseFactory.build(name="test_snippet_2")
        exact_match = SnippetResponseFactory.build(name="exact_match")
        mock_data = [snippet1, snippet2, exact_match]
        
        # Patch the _get_paginated_results method
        with patch.object(snippet_service, "_get_paginated_results", return_value=mock_data):
            # List the snippets with exact_match filter
            results = snippet_service.list(name="exact_match", exact_match=True)
            
            # Assert exactly one result with matching name
            assert len(results) == 1
            assert results[0].name == "exact_match"

    def test_list_snippets_pagination(self, snippet_service, mock_scm_client):
        """Test listing snippets with pagination parameters."""
        # Setup mock response with valid snippet data
        mock_data = [SnippetResponseFactory.build() for _ in range(5)]
        
        # Patch the _get_paginated_results method
        with patch.object(snippet_service, "_get_paginated_results", return_value=mock_data):
            # List the snippets with pagination
            results = snippet_service.list(offset=10, limit=5)
            
            # Assert pagination parameters were passed correctly
            call_args = snippet_service._get_paginated_results.call_args
            assert call_args[1]["offset"] == 10
            assert call_args[1]["limit"] == 5
            
            # Verify results are correctly processed
            assert len(results) == 5
            for result in results:
                assert isinstance(result, SnippetResponseModel)

    def test_list_snippets_with_type_filter(self, snippet_service, mock_scm_client):
        """Test listing snippets with type filter."""
        # Setup mock response with properly structured data
        predefined = SnippetResponseFactory.build(type="predefined")
        custom = SnippetResponseFactory.build(type="custom")
        mock_data = [predefined, custom]
        
        # Patch the _get_paginated_results method
        with patch.object(snippet_service, "_get_paginated_results", return_value=mock_data):
            # List only predefined snippets
            snippet_service.list(type="predefined")
            
            # Verify type parameter was passed correctly
            call_args = snippet_service._get_paginated_results.call_args
            assert call_args[1]["params"] == {"type": "predefined"}

    def test_list_snippets_empty_result(self, snippet_service, mock_scm_client):
        """Test listing snippets when no results are returned."""
        # Patch the _get_paginated_results method to return an empty list
        with patch.object(snippet_service, "_get_paginated_results", return_value=[]):
            results = snippet_service.list()
            
            # Assert empty list is returned
            assert isinstance(results, list)
            assert len(results) == 0


class TestSnippetUpdate(TestSnippetBase):
    """Tests for Snippet.update method."""

    def test_update_snippet(self, snippet_service, mock_scm_client):
        """Test updating a snippet."""
        # Setup mock response
        snippet_id = "123e4567-e89b-12d3-a456-426614174000"
        mock_response = SnippetResponseFactory.build(id=snippet_id)
        mock_scm_client.put.return_value = mock_response

        # Update the snippet
        result = snippet_service.update(
            snippet_id=snippet_id,
            name="updated_name",
        )

        # Assert the client was called correctly
        mock_scm_client.put.assert_called_once()
        call_args = mock_scm_client.put.call_args
        assert call_args[0][0] == f"/config/setup/v1/snippets/{snippet_id}"
        assert call_args[1]["json"]["name"] == "updated_name"

        # Assert the result is a SnippetResponseModel
        assert isinstance(result, SnippetResponseModel)
        assert result.name == mock_response["name"]

    def test_update_with_all_parameters(self, snippet_service, mock_scm_client):
        """Test updating a snippet with all parameters."""
        # Setup mock response
        snippet_id = "123e4567-e89b-12d3-a456-426614174000"
        mock_response = SnippetResponseFactory.build(id=snippet_id)
        mock_scm_client.put.return_value = mock_response

        # Update the snippet with all fields
        result = snippet_service.update(
            snippet_id=snippet_id,
            name="updated_name",
            description="Updated description",
            labels=["new_tag"],
            enable_prefix=False,
        )

        # Assert the client was called correctly
        call_args = mock_scm_client.put.call_args
        payload = call_args[1]["json"]
        assert payload["name"] == "updated_name"
        assert payload["description"] == "Updated description"
        assert payload["labels"] == ["new_tag"]
        assert payload["enable_prefix"] is False

    def test_update_nonexistent_snippet(self, snippet_service, mock_scm_client):
        """Test updating a snippet that doesn't exist."""
        # Setup mock client to raise APIError with 404 status
        error = APIError("Snippet not found")
        error.http_status_code = 404
        mock_scm_client.put.side_effect = error
        snippet_id = "nonexistent-id"

        # Try to update the nonexistent snippet
        with pytest.raises(ObjectNotPresentError):
            snippet_service.update(snippet_id=snippet_id, name="updated_name")

    def test_update_with_general_error(self, snippet_service, mock_scm_client):
        """Test update with a non-404 exception."""
        # Create a non-404 error
        error = APIError("General server error")
        error.http_status_code = 500
        mock_scm_client.put.side_effect = error
        
        # Should re-raise the error
        with pytest.raises(APIError):
            snippet_service.update(snippet_id="123", name="updated_name")

    def test_update_without_fields(self, snippet_service):
        """Test updating a snippet without providing any fields to update."""
        with pytest.raises(InvalidObjectError) as excinfo:
            snippet_service.update(snippet_id="123")
        
        # Check message content instead of string representation
        assert "field" in excinfo.value.message


class TestSnippetDelete(TestSnippetBase):
    """Tests for Snippet.delete method."""

    def test_delete_snippet(self, snippet_service, mock_scm_client):
        """Test deleting a snippet."""
        # Setup mock client
        snippet_id = "123e4567-e89b-12d3-a456-426614174000"
        
        # Delete the snippet
        snippet_service.delete(snippet_id)
        
        # Assert the client was called correctly
        mock_scm_client.delete.assert_called_once_with(f"/config/setup/v1/snippets/{snippet_id}")

    def test_delete_nonexistent_snippet(self, snippet_service, mock_scm_client):
        """Test deleting a snippet that doesn't exist."""
        # Setup mock client to raise APIError with 404 status
        error = APIError("Snippet not found")
        error.http_status_code = 404
        mock_scm_client.delete.side_effect = error
        snippet_id = "nonexistent-id"
        
        # Try to delete the nonexistent snippet
        with pytest.raises(ObjectNotPresentError):
            snippet_service.delete(snippet_id)

    def test_delete_with_general_error(self, snippet_service, mock_scm_client):
        """Test delete with a non-404 exception."""
        # Create a non-404 error
        error = APIError("General server error")
        error.http_status_code = 500
        mock_scm_client.delete.side_effect = error
        
        # Should re-raise the error
        with pytest.raises(APIError):
            snippet_service.delete("123")


class TestPaginatedResults(TestSnippetBase):
    """Tests for the _get_paginated_results helper method."""
    
    def test_get_paginated_results_dict_with_data(self, snippet_service, mock_scm_client):
        """Test _get_paginated_results with dict response containing 'data'."""
        # Setup mock response
        mock_response = {"data": [{"id": "1", "name": "test1"}, {"id": "2", "name": "test2"}]}
        mock_scm_client.get.return_value = mock_response
        
        # Call the method
        results = snippet_service._get_paginated_results(
            endpoint="/test",
            params={},
            limit=10,
            offset=0
        )
        
        # Assert correct data is extracted
        assert results == mock_response["data"]
        
    def test_get_paginated_results_list_response(self, snippet_service, mock_scm_client):
        """Test _get_paginated_results with list response."""
        # Setup mock response
        mock_response = [{"id": "1", "name": "test1"}, {"id": "2", "name": "test2"}]
        mock_scm_client.get.return_value = mock_response
        
        # Call the method
        results = snippet_service._get_paginated_results(
            endpoint="/test",
            params={},
            limit=10,
            offset=0
        )
        
        # Assert the list is returned directly
        assert results == mock_response
        
    def test_get_paginated_results_unexpected_format(self, snippet_service, mock_scm_client):
        """Test _get_paginated_results with unexpected response format."""
        # Setup mock response with unexpected format
        mock_scm_client.get.return_value = "not a dict or list"
        
        # Call the method
        results = snippet_service._get_paginated_results(
            endpoint="/test",
            params={},
            limit=10,
            offset=0
        )
        
        # Assert empty list is returned for unexpected format
        assert results == []


class TestSnippetValidation(TestSnippetBase):
    """Tests for validation methods."""
    
    def test_validate_and_prepare_data(self, snippet_service):
        """Test validate_and_prepare_data method."""
        # Test with valid data
        data = snippet_service._validate_and_prepare_data(
            name="valid_name",
            description="Description",
            labels=["tag1", "tag2"],
            enable_prefix=True
        )
        
        assert data["name"] == "valid_name"
        assert data["description"] == "Description"
        assert data["labels"] == ["tag1", "tag2"]
        assert data["enable_prefix"] is True
        
        # Test with missing name
        with pytest.raises(InvalidObjectError):
            snippet_service._validate_and_prepare_data(
                description="Description only"
            )
    
    def test_name_validation(self, snippet_service):
        """Test name validation rules."""
        # Valid name
        valid_name = snippet_service._validate_name("valid_name")
        assert valid_name == "valid_name"
        
        # Empty name
        with pytest.raises(InvalidObjectError):
            snippet_service._validate_name("")
            
        # Whitespace-only name
        with pytest.raises(InvalidObjectError):
            snippet_service._validate_name("   ")
            
        # Name too long
        with pytest.raises(InvalidObjectError):
            snippet_service._validate_name("a" * 256)  # Longer than 255 chars
    
    def test_labels_validation(self, snippet_service):
        """Test labels validation rules."""
        # Valid labels
        valid_labels = snippet_service._validate_labels(["tag1", "tag2"])
        assert valid_labels == ["tag1", "tag2"]
        
        # None labels
        assert snippet_service._validate_labels(None) is None
        
        # Non-string labels
        with pytest.raises(InvalidObjectError):
            snippet_service._validate_labels(["tag1", 123, "tag3"])
