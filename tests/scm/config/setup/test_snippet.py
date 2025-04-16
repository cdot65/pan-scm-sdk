# tests/scm/config/setup/test_snippet.py

# Standard library imports
from unittest.mock import MagicMock, patch

# External libraries
import pytest

# Local SDK imports
from scm.client import Scm
from scm.config.setup.snippet import Snippet
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.setup.snippet_models import (
    SnippetResponseModel,
)
from tests.factories.setup.snippet import (
    SnippetCreateApiFactory,
    SnippetResponseFactory,
    SnippetResponseModelFactory,
    SnippetUpdateApiFactory,
)


class TestSnippetBase:
    """Base class for snippet tests with common fixtures."""

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

    def test_get_with_general_exception(self, snippet_service, mock_scm_client):
        """Test get with a non-404 exception to cover line 105."""
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
        """Test fetching a snippet when no match exists."""
        # Setup mock client to raise APIError with 404 status
        error = APIError("Snippet not found")
        error.http_status_code = 404
        mock_scm_client.get.side_effect = error

        # Mock the list method to return empty results
        with patch.object(snippet_service, "list", return_value=[]):
            result = snippet_service.fetch("nonexistent_snippet")
            assert result is None

    def test_fetch_multiple_matches(self, snippet_service, mock_scm_client):
        """Test behavior when multiple matches are found."""
        # Setup mock response for list method
        mock_response = [
            SnippetResponseFactory.build(name="test_snippet"),
            SnippetResponseFactory.build(name="test_snippet"),
        ]

        # Return dict for get call (direct query misses)
        mock_scm_client.get.return_value = {"data": mock_response}

        # Mock the list method to return multiple results
        with patch.object(snippet_service, "list", return_value=mock_response):
            with pytest.raises(APIError):
                snippet_service.fetch("test_snippet")

    def test_fetch_with_model_validation_error(self, snippet_service, mock_scm_client):
        """Test handling of model validation errors in fetch method (line 264)."""
        # Setup a response that will fail model validation
        mock_response = {"id": "123", "invalid_field": True}
        mock_scm_client.get.return_value = mock_response
        
        # Mock the model_validate method to raise a ValueError during validation
        with patch('scm.models.setup.snippet_models.SnippetResponseModel.model_validate', 
                  side_effect=ValueError("Model validation error")):
            # This should be handled gracefully
            result = snippet_service.fetch("test_snippet")
            assert result is None

    def test_fetch_fallback_lines_253_256(self, snippet_service, mock_scm_client):
        """Directly testing lines 253-256 in fetch method."""
        # Setup a 404 error for the get request
        error = APIError("Not found")
        error.http_status_code = 404
        mock_scm_client.get.side_effect = error
        
        # Setup the list method to return empty list
        with patch.object(snippet_service, 'list', return_value=[]):
            result = snippet_service.fetch("test_name")
            assert result is None

    def test_fetch_with_single_match(self, snippet_service, mock_scm_client):
        """Test the fetch method when list returns single match to cover line 262."""
        # Setup mock client to raise 404 when trying to get directly
        error = APIError("Not found")
        error.http_status_code = 404
        mock_scm_client.get.side_effect = error
        
        # Create a mock response for the fallback list
        mock_snippet = SnippetResponseFactory.build(name="test_snippet")
        mock_response = SnippetResponseModel.model_validate(mock_snippet)
        
        # Setup list method to return exactly one match
        with patch.object(snippet_service, 'list', return_value=[mock_response]):
            # Call fetch with the name
            result = snippet_service.fetch("test_snippet")
            
            # Result should be the mock response
            assert result == mock_response

    def test_fetch_with_type_error(self, snippet_service, mock_scm_client):
        """Test fetch method with response that causes a TypeError during model validation."""
        # Setup a response that will cause error during model validation
        mock_scm_client.get.return_value = {"id": 12345}  # ID should be a string, numeric will cause validation error
        
        # This should be handled gracefully - verify it doesn't crash
        result = snippet_service.fetch("test_snippet")
        assert result is None


class TestSnippetList(TestSnippetBase):
    """Tests for Snippet.list method."""

    def test_list_snippets(self, snippet_service, mock_scm_client):
        """Test listing snippets with default parameters."""
        # Setup mock response
        mock_response = SnippetResponseFactory.build_list_response(count=3)
        mock_scm_client.get.return_value = mock_response

        # Patch the _get_paginated_results method
        with patch.object(
            snippet_service, "_get_paginated_results", return_value=mock_response["data"]
        ):
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
        # Setup mock response
        mock_response = SnippetResponseFactory.build_list_response(count=1)
        mock_scm_client.get.return_value = mock_response

        # Patch the _get_paginated_results method
        with patch.object(
            snippet_service, "_get_paginated_results", return_value=mock_response["data"]
        ):
            # List the snippets with name filter
            results = snippet_service.list(name="test_snippet")

            # Assert _get_paginated_results was called correctly
            call_args = snippet_service._get_paginated_results.call_args
            assert call_args[1]["params"] == {"name": "test_snippet"}

            # Assert the results are correct
            assert len(results) == 1
            assert isinstance(results[0], SnippetResponseModel)

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
        # Setup mock response
        mock_response = SnippetResponseFactory.build_list_response(count=5)
        mock_scm_client.get.return_value = mock_response

        # Patch the _get_paginated_results method
        with patch.object(
            snippet_service, "_get_paginated_results", return_value=mock_response["data"]
        ):
            # List the snippets with pagination
            results = snippet_service.list(offset=10, limit=5)

            # Assert _get_paginated_results was called with correct pagination
            call_args = snippet_service._get_paginated_results.call_args
            assert call_args[1]["offset"] == 10
            assert call_args[1]["limit"] == 5

    def test_list_snippets_with_type_filter(self, snippet_service, mock_scm_client):
        """Test listing snippets with type filter."""
        # Setup mock response
        predefined_snippet = SnippetResponseFactory.build(type="predefined")
        custom_snippet = SnippetResponseFactory.build(type="custom")
        mock_data = [predefined_snippet, custom_snippet]

        # Patch the _get_paginated_results method
        with patch.object(snippet_service, "_get_paginated_results", return_value=mock_data):
            # List only predefined snippets
            results = snippet_service.list(type="predefined")

            # Verify results are filtered correctly in the call
            call_args = snippet_service._get_paginated_results.call_args
            assert call_args[1]["params"] == {"type": "predefined"}

    def test_list_snippets_empty_result(self, snippet_service, mock_scm_client):
        """Test listing snippets when no results are returned."""
        # Setup empty response
        empty_response = {"data": [], "limit": 50, "offset": 0, "total": 0}
        mock_scm_client.get.return_value = empty_response

        # List the snippets
        with patch.object(snippet_service, "_get_paginated_results", return_value=[]):
            results = snippet_service.list()

            # Assert empty list is returned
            assert isinstance(results, list)
            assert len(results) == 0


class TestSnippetUpdate(TestSnippetBase):
    """Tests for Snippet.update method."""

    def test_update_snippet(self, snippet_service, mock_scm_client):
        """Test updating a snippet by direct mocking of client methods."""
        # Setup mock response
        mock_response = SnippetResponseFactory.build()
        mock_scm_client.put.return_value = mock_response
        snippet_id = "123e4567-e89b-12d3-a456-426614174000"

        # Update the snippet
        result = snippet_service.update(
            snippet_id=snippet_id,
            name="updated_name",
            description="Updated description",
        )

        # Assert the client was called correctly
        mock_scm_client.put.assert_called_once()
        call_args = mock_scm_client.put.call_args
        assert call_args[0][0] == f"/config/setup/v1/snippets/{snippet_id}"
        payload = call_args[1]["json"]
        assert payload["name"] == "updated_name"
        assert payload["description"] == "Updated description"

        # Assert the result is a SnippetResponseModel
        assert isinstance(result, SnippetResponseModel)

    def test_update_with_all_parameters(self, snippet_service, mock_scm_client):
        """Test updating snippet with all parameters to cover line 144."""
        # Setup
        snippet_id = "123e4567-e89b-12d3-a456-426614174000"
        mock_response = SnippetResponseFactory.build()
        mock_scm_client.put.return_value = mock_response
        
        # Call update with all parameters
        result = snippet_service.update(
            snippet_id=snippet_id,
            name="updated_snippet",
            description="Updated description",
            labels=["updated", "tags"],
            enable_prefix=True
        )
        
        # Verify result
        assert isinstance(result, SnippetResponseModel)
        
        # Verify the request payload contained all parameters
        request_json = mock_scm_client.put.call_args[1]["json"]
        assert "name" in request_json
        assert "description" in request_json
        assert "labels" in request_json
        assert "enable_prefix" in request_json

    def test_update_nonexistent_snippet(self, snippet_service, mock_scm_client):
        """Test updating a snippet that doesn't exist."""
        # Setup mock client to raise APIError with 404 status
        error = APIError("Snippet not found")
        error.http_status_code = 404
        mock_scm_client.put.side_effect = error
        snippet_id = "nonexistent-id"

        # Try to update the nonexistent snippet
        with pytest.raises(ObjectNotPresentError):
            snippet_service.update(
                snippet_id=snippet_id,
                name="updated_name",
            )

    def test_update_with_nonexistent_raising_non404(self, snippet_service, mock_scm_client):
        """Test update with a non-404 exception to cover line 159."""
        snippet_id = "123e4567-e89b-12d3-a456-426614174000"
        
        # Create a non-404 error
        error = APIError("General server error")
        error.http_status_code = 500
        mock_scm_client.put.side_effect = error
        
        # Should re-raise the error
        with pytest.raises(APIError):
            snippet_service.update(snippet_id=snippet_id, name="updated_name")

    def test_update_without_fields(self, snippet_service):
        """Test updating a snippet without providing any fields to update."""
        snippet_id = "123e4567-e89b-12d3-a456-426614174000"

        # Try to update without providing any fields
        with pytest.raises(InvalidObjectError):
            snippet_service.update(snippet_id=snippet_id)


class TestSnippetDelete(TestSnippetBase):
    """Tests for Snippet.delete method."""

    def test_delete_snippet(self, snippet_service, mock_scm_client):
        """Test deleting a snippet."""
        # Setup mock client with a successful deletion
        mock_scm_client.delete.return_value = None
        snippet_id = "123e4567-e89b-12d3-a456-426614174000"

        # Delete the snippet
        result = snippet_service.delete(snippet_id)

        # Assert the client was called correctly
        mock_scm_client.delete.assert_called_once_with(f"/config/setup/v1/snippets/{snippet_id}")

        # Assert the result is None
        assert result is None

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

    def test_delete_with_nonexistent_raising_non404(self, snippet_service, mock_scm_client):
        """Test delete with a non-404 exception to cover line 178."""
        object_id = "123e4567-e89b-12d3-a456-426614174000"
        
        # Create a non-404 error
        error = APIError("General server error")
        error.http_status_code = 500
        mock_scm_client.delete.side_effect = error
        
        # Should re-raise the error
        with pytest.raises(APIError):
            snippet_service.delete(object_id)


class TestSnippetFolderAssociations(TestSnippetBase):
    """Tests for Snippet folder association methods."""

    def test_associate_folder(self, snippet_service, mock_scm_client):
        """Test associating a snippet with a folder."""
        # Setup mock response
        snippet_id = "123e4567-e89b-12d3-a456-426614174000"
        folder_id = "abcdef12-3456-7890-abcd-ef1234567890"
        mock_response = SnippetResponseModelFactory.build_with_folders(folder_count=1)
        
        # Simulate an API error that will be caught by associate_folder
        error = Exception("API endpoint not implemented")
        mock_scm_client.post.side_effect = error
        
        # Associate the folder
        with pytest.raises(NotImplementedError):
            snippet_service.associate_folder(snippet_id, folder_id)

    def test_disassociate_folder(self, snippet_service, mock_scm_client):
        """Test disassociating a snippet from a folder."""
        # Setup mock response
        snippet_id = "123e4567-e89b-12d3-a456-426614174000"
        folder_id = "abcdef12-3456-7890-abcd-ef1234567890"
        mock_response = SnippetResponseModelFactory.build()
        mock_scm_client.delete.return_value = mock_response

        # Disassociate the folder
        with pytest.raises(NotImplementedError):
            snippet_service.disassociate_folder(snippet_id, folder_id)

    def test_disassociate_folder_with_api_error(self, snippet_service, mock_scm_client):
        """Test disassociate_folder method with API error to cover lines 439-457."""
        snippet_id = "123e4567-e89b-12d3-a456-426614174000"
        folder_id = "abcdef12-3456-7890-abcd-ef1234567890"
        
        # Mock the API client to raise an exception
        mock_scm_client.delete.side_effect = ValueError("API error")
        
        # This should raise a NotImplementedError
        with pytest.raises(NotImplementedError) as excinfo:
            snippet_service.disassociate_folder(snippet_id, folder_id)
        
        # Verify the error message
        assert "Disassociating snippets from folders is not yet implemented" in str(excinfo.value)


class TestSnippetValidation(TestSnippetBase):
    """Tests for Snippet validation methods."""

    def test_validate_and_prepare_data(self, snippet_service):
        """Test validate_and_prepare_data method."""
        # Test with valid data
        data = snippet_service._validate_and_prepare_data(
            name="test_snippet",
            description="Test description",
            labels=["tag1", "tag2"],
            enable_prefix=True,
        )

        # Assert data is prepared correctly
        assert data["name"] == "test_snippet"
        assert data["description"] == "Test description"
        assert data["labels"] == ["tag1", "tag2"]
        assert data["enable_prefix"] is True

        # Test with minimal data
        data = snippet_service._validate_and_prepare_data(name="test_snippet")
        assert data == {"name": "test_snippet"}

        # Test with invalid data
        with pytest.raises(InvalidObjectError):
            snippet_service._validate_and_prepare_data(name="")

        with pytest.raises(InvalidObjectError):
            snippet_service._validate_and_prepare_data(name=None)

    def test_name_validation(self, snippet_service):
        """Test name validation rules."""
        # Valid name
        assert snippet_service._validate_name("valid_name") == "valid_name"

        # Too long name
        with pytest.raises(InvalidObjectError):
            snippet_service._validate_name("x" * 256)  # Assuming max length is 255

        # Empty name
        with pytest.raises(InvalidObjectError):
            snippet_service._validate_name("")

        # Whitespace-only name
        with pytest.raises(InvalidObjectError):
            snippet_service._validate_name("   ")

    def test_labels_validation(self, snippet_service):
        """Test labels validation rules."""
        # Valid labels
        assert snippet_service._validate_labels(["tag1", "tag2"]) == ["tag1", "tag2"]

        # Empty list is valid
        assert snippet_service._validate_labels([]) == []

        # None is valid
        assert snippet_service._validate_labels(None) is None

    def test_line_411_validate_labels(self, snippet_service):
        """Test _validate_labels with non-string values to cover line 411."""
        # Create labels with a non-string item to trigger the validation code
        labels = ["valid", 123, "also_valid"]
        
        # Call validate_labels - should raise InvalidObjectError
        with pytest.raises(InvalidObjectError):
            snippet_service._validate_labels(labels)


class TestSnippetLineSpecificCoverage(TestSnippetBase):
    """Tests specifically targeting uncovered lines."""
    
    def test_line_293_associate_folder_exception(self, snippet_service, mock_scm_client):
        """Test the exception handling in associate_folder (line 293)."""
        # Setup
        snippet_id = "123e4567-e89b-12d3-a456-426614174000"
        folder_id = "abcdef12-3456-7890-abcd-ef1234567890"
        
        # Make the API call raise an exception
        mock_scm_client.post.side_effect = ValueError("Test error")
        
        # This should raise NotImplementedError with the wrapped exception
        with pytest.raises(NotImplementedError):
            snippet_service.associate_folder(snippet_id, folder_id)
    
    def test_line_388_name_validation_return(self, snippet_service):
        """Test the return statement in _validate_name (line 388)."""
        valid_name = "test-name-123"
        
        # This should pass validation and return the name (line 388)
        result = snippet_service._validate_name(valid_name)
        
        # Verify the name was returned unchanged
        assert result == valid_name

class TestFinalCoverageItems(TestSnippetBase):
    """Tests targeting specific uncovered lines."""
    
    def test_fetch_fallback_empty_list(self, snippet_service, mock_scm_client):
        """Test fetch fallback when list returns empty to cover line 253."""
        # Setup mock to raise 404 on direct get
        error = APIError("Not found")
        error.http_status_code = 404
        mock_scm_client.get.side_effect = error
        
        # Setup empty response for list fallback
        with patch.object(snippet_service, 'list', return_value=[]):
            result = snippet_service.fetch("test_name")
            assert result is None
            
    def test_associate_folder_exception_handler(self, snippet_service, mock_scm_client):
        """Test associate_folder exception handler to cover line 293."""
        snippet_id = "123e4567-e89b-12d3-a456-426614174000"
        folder_id = "abcdef12-3456-7890-abcd-ef1234567890"
        
        # Set up a specific exception type
        mock_scm_client.post.side_effect = RuntimeError("API call failed")
        
        # Should wrap the exception in NotImplementedError
        with pytest.raises(NotImplementedError) as excinfo:
            snippet_service.associate_folder(snippet_id, folder_id)
            
        # Check error message contains original exception
        assert "API call failed" in str(excinfo.value)
            
    def test_disassociate_folder_exception_handler(self, snippet_service, mock_scm_client):
        """Test disassociate_folder exception handler to cover lines 439-457."""
        snippet_id = "123e4567-e89b-12d3-a456-426614174000"
        folder_id = "abcdef12-3456-7890-abcd-ef1234567890"
        
        # Set up a specific exception type
        mock_scm_client.delete.side_effect = RuntimeError("API call failed")
        
        # Should wrap the exception in NotImplementedError
        with pytest.raises(NotImplementedError) as excinfo:
            snippet_service.disassociate_folder(snippet_id, folder_id)
            
        # Check error message contains original exception
        assert "API call failed" in str(excinfo.value)

class TestSnippetAdditionalCoverage(TestSnippetBase):
    """Tests for additional coverage."""
    
    def test_fetch_with_model_validation_error(self, snippet_service, mock_scm_client):
        """Test handling of model validation errors in fetch method (line 264)."""
        # Setup a response that will fail model validation
        mock_response = {"id": "123", "invalid_field": True}
        mock_scm_client.get.return_value = mock_response
        
        # Mock the model_validate method to raise a ValueError during validation
        with patch('scm.models.setup.snippet_models.SnippetResponseModel.model_validate', 
                  side_effect=ValueError("Model validation error")):
            # This should be handled gracefully
            result = snippet_service.fetch("test_snippet")
            assert result is None

    def test_fetch_fallback_lines_253_256(self, snippet_service, mock_scm_client):
        """Directly testing lines 253-256 in fetch method."""
        # Setup a 404 error for the get request
        error = APIError("Not found")
        error.http_status_code = 404
        mock_scm_client.get.side_effect = error
        
        # Setup the list method to return empty list
        with patch.object(snippet_service, 'list', return_value=[]):
            result = snippet_service.fetch("test_name")
            assert result is None
    
    def test_associate_folder_line_293(self, snippet_service, mock_scm_client):
        """Directly testing line 293 in associate_folder method."""
        snippet_id = "123e4567-e89b-12d3-a456-426614174000"
        folder_id = "abcdef12-3456-7890-abcd-ef1234567890"
        
        # Setup specific exception for post
        mock_scm_client.post.side_effect = Exception("Specific test exception")
        
        # This should wrap the exception in NotImplementedError
        with pytest.raises(NotImplementedError) as excinfo:
            snippet_service.associate_folder(snippet_id, folder_id)
            
        assert "Specific test exception" in str(excinfo.value)
    
    def test_disassociate_folder_lines_446_448(self, snippet_service, mock_scm_client):
        """Directly testing lines 446-448 in disassociate_folder method."""
        snippet_id = "123e4567-e89b-12d3-a456-426614174000"
        folder_id = "abcdef12-3456-7890-abcd-ef1234567890"
        
        # Setup specific exception for delete
        mock_scm_client.delete.side_effect = Exception("Specific test exception")
        
        # This should wrap the exception in NotImplementedError
        with pytest.raises(NotImplementedError) as excinfo:
            snippet_service.disassociate_folder(snippet_id, folder_id)
            
        assert "Specific test exception" in str(excinfo.value)
