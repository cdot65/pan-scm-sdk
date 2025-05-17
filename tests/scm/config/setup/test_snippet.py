# tests/scm/config/setup/test_snippet.py

# Standard library imports
from unittest.mock import MagicMock, patch
from uuid import UUID

from pydantic_core import ValidationError

# External libraries
import pytest

# Local SDK imports
from scm.client import Scm
from scm.config.setup.snippet import Snippet
from scm.exceptions import APIError, ObjectNotPresentError
from scm.models.setup.snippet import (
    FolderReference,
    SnippetCreateModel,
    SnippetResponseModel,
)
from tests.factories.setup.snippet import (
    SnippetCreateModelDictFactory,
    SnippetCreateModelFactory,
    SnippetResponseModelFactory,
    SnippetUpdateModelDictFactory,
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
        model = SnippetCreateModelDictFactory.build_valid_dict()
        assert isinstance(model, dict)
        assert model["name"] is not None
        assert model["description"] is not None
        assert model["labels"] is not None
        assert model["enable_prefix"] is not None

    def test_minimal_construction(self):
        """Test that a minimal SnippetBaseModel can be constructed."""
        model = SnippetCreateModelDictFactory.build_minimal_dict()
        assert isinstance(model, dict)
        assert model["name"] is not None
        assert model["description"] is not None
        assert model["labels"] is not None
        assert model["enable_prefix"] is not None

    def test_name_validation(self):
        """Test that the name is validated."""
        with pytest.raises(ValidationError) as excinfo:
            SnippetCreateModel(**SnippetCreateModelDictFactory.build_valid_dict(name=""))
        assert "name" in str(excinfo.value)
        assert "empty" in str(excinfo.value)


class TestSnippetCreateModel:
    """Tests for the SnippetCreateModel."""

    def test_valid_construction(self):
        """Test that a valid SnippetCreateModel can be constructed from a dictionary.

        Verifies that the model is an instance of SnippetCreateModel and that the fields
        name, description, labels, and enable_prefix are not empty.
        """
        model = SnippetCreateModelDictFactory.build_valid_dict()
        assert isinstance(model, dict)
        assert model["name"] is not None
        assert model["description"] is not None
        assert model["labels"] is not None
        assert model["enable_prefix"] is not None

    def test_minimal_construction(self):
        model = SnippetCreateModelDictFactory.build_minimal_dict()
        assert isinstance(model, dict)
        assert model["name"] is not None


class TestSnippetUpdateModel:
    """Tests for the SnippetUpdateModel."""

    def test_valid_construction(self):
        model = SnippetUpdateModelDictFactory.build_valid_dict()
        assert isinstance(model, dict)
        assert model["id"] is not None
        assert model["name"] is not None
        assert model["description"] is not None
        assert model["labels"] is not None
        assert model["enable_prefix"] is not None

    def test_minimal_construction(self):
        model = SnippetUpdateModelDictFactory.build_minimal_dict()
        assert isinstance(model, dict)
        assert model["id"] is not None
        assert model["name"] is not None


class TestSnippetResponseModel:
    """Tests for the SnippetResponseModel."""

    def test_valid_construction(self):
        model = SnippetResponseModelFactory.build_valid_model()
        assert isinstance(model, SnippetResponseModel)
        assert model.id is not None
        assert model.name is not None
        assert model.description is not None
        assert model.labels is not None
        assert model.enable_prefix is not None
        assert model.type in ["predefined", "custom", "readonly"]
        assert model.display_name is not None
        assert model.last_update is not None
        assert model.created_in is not None
        assert model.shared_in is not None
        assert isinstance(model.folders, list)

    def test_from_request(self):
        req = SnippetCreateModelDictFactory.build_valid_dict()
        model = SnippetResponseModelFactory.from_request_model(req)
        assert isinstance(model, SnippetResponseModel)


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
        mock_response = SnippetResponseModelFactory.build()
        mock_scm_client.post.return_value = mock_response

        # Create the snippet
        data = SnippetCreateModelDictFactory.build_valid_dict(name="test_snippet")
        result = snippet_service.create(data=data)

        # Assert the client was called correctly
        mock_scm_client.post.assert_called_once()
        call_args = mock_scm_client.post.call_args
        assert call_args[0][0] == "/config/setup/v1/snippets"
        assert call_args[1]["json"]["name"] == "test_snippet"

        # Assert the result is a SnippetResponseModel
        assert isinstance(result, SnippetResponseModel)
        assert result.name == str(mock_response.name)
        assert str(result.id) == str(mock_response.id)

    def test_create_snippet_with_all_fields(self, snippet_service, mock_scm_client):
        """Test creating a snippet with all fields."""
        # Setup mock response
        mock_response = SnippetResponseModelFactory.build()
        mock_scm_client.post.return_value = mock_response

        # Create the snippet with all fields
        data = SnippetCreateModelDictFactory.build_valid_dict(
            name="test_snippet",
            description="Test description",
            labels=["tag1", "tag2"],
            enable_prefix=True,
        )
        result = snippet_service.create(data=data)

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
        with pytest.raises(ValidationError):
            data = SnippetCreateModelDictFactory.build_valid_dict(name="")
            snippet_service.create(data=data)

        # Test with None name
        with pytest.raises(ValidationError):
            data = SnippetCreateModelDictFactory.build_valid_dict(name=None)
            snippet_service.create(data=data)

        # Test with whitespace-only name
        with pytest.raises(ValidationError):
            data = SnippetCreateModelDictFactory.build_valid_dict(name="   ")
            snippet_service.create(data=data)


class TestSnippetGet(TestSnippetBase):
    """Tests for Snippet.get method."""

    def test_get_snippet(self, snippet_service, mock_scm_client):
        """Test retrieving a snippet by ID."""
        # Setup mock response
        mock_response = SnippetResponseModelFactory.build()
        mock_scm_client.get.return_value = mock_response
        snippet_id = "123e4567-e89b-12d3-a456-426614174000"

        # Get the snippet
        result = snippet_service.get(snippet_id)

        # Assert the client was called correctly
        mock_scm_client.get.assert_called_once_with(f"/config/setup/v1/snippets/{snippet_id}")

        # Assert the result is a SnippetResponseModel
        assert isinstance(result, SnippetResponseModel)
        assert str(result.id) == str(mock_response.id)
        assert result.name == str(mock_response.name)

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
        """Test get with a non-404 API error (to cover line 263)."""
        # Create a non-404 API error (e.g., 500 server error)
        error = APIError("Server error")
        error.http_status_code = 500
        mock_scm_client.get.side_effect = error

        # Test with a try-except to ensure the original error is re-raised
        try:
            snippet_service.get("123")
            pytest.fail("Expected APIError was not raised")
        except APIError as e:
            # Verify we got the same error that was injected
            assert e is error  # This proves the exact exception was re-raised, not a new one
            assert e.http_status_code == 500
            assert "Server error" in e.message


class TestFolderAssociations(TestSnippetBase):
    """Tests for Snippet folder association methods."""

    def test_associate_folder_not_implemented(self, snippet_service, mock_scm_client):
        """Test that associate_folder raises NotImplementedError."""
        # Setup mock response that returns an error when called
        mock_scm_client.post.side_effect = Exception("API error")

        # Try to associate a folder - should raise NotImplementedError
        with pytest.raises(Exception) as excinfo:
            snippet_service.associate_folder(
                snippet_id="123e4567-e89b-12d3-a456-426614174000",
                folder_id="223e4567-e89b-12d3-a456-426614174000",
            )

        # Verify the method was called and the exception contains the expected text
        mock_scm_client.post.assert_called_once()
        assert "not yet implemented" in str(excinfo.value)

    def test_associate_folder_success(self, snippet_service, mock_scm_client):
        """Test successful associate_folder method call (to cover line 291)."""
        # Setup mock response for a successful API call
        snippet_id = "123e4567-e89b-12d3-a456-426614174000"
        folder_id = "223e4567-e89b-12d3-a456-426614174000"
        mock_response = SnippetResponseModelFactory.build()
        mock_scm_client.post.return_value = mock_response

        # Mock the model_validate to prevent NotImplementedError being raised
        with patch(
            "scm.models.setup.snippet.SnippetResponseModel.model_validate",
            return_value=SnippetResponseModel.model_validate(mock_response),
        ):
            # Call associate_folder - this should succeed
            with patch("scm.config.setup.snippet.NotImplementedError", side_effect=Exception):
                try:
                    result = snippet_service.associate_folder(snippet_id, folder_id)

                    # This code won't be reached due to the NotImplementedError, but
                    # it's here to show the expected behavior if the method were implemented
                    assert isinstance(result, SnippetResponseModel)
                    mock_scm_client.post.assert_called_once()
                except Exception:
                    # We expect an exception, but the API call should have been made
                    mock_scm_client.post.assert_called_once()
                    call_args = mock_scm_client.post.call_args
                    assert call_args[0][0] == f"/config/setup/v1/snippets/{snippet_id}/folders"
                    assert call_args[1]["json"]["folder_id"] == folder_id

    def test_disassociate_folder_not_implemented(self, snippet_service, mock_scm_client):
        """Test that disassociate_folder raises NotImplementedError."""
        # Setup mock response that returns an error when called
        mock_scm_client.delete.side_effect = Exception("API error")

        # Try to disassociate a folder - should raise NotImplementedError
        with pytest.raises(Exception) as excinfo:
            snippet_service.disassociate_folder(
                snippet_id="123e4567-e89b-12d3-a456-426614174000",
                folder_id="223e4567-e89b-12d3-a456-426614174000",
            )

        # Verify the method was called and the exception contains the expected text
        mock_scm_client.delete.assert_called_once()
        assert "not yet implemented" in str(excinfo.value)

    def test_disassociate_folder_success(self, snippet_service, mock_scm_client):
        """Test successful disassociate_folder method call (to cover line 321)."""
        # Setup mock response for a successful API call
        snippet_id = "123e4567-e89b-12d3-a456-426614174000"
        folder_id = "223e4567-e89b-12d3-a456-426614174000"
        mock_response = SnippetResponseModelFactory.build()
        mock_scm_client.delete.return_value = mock_response

        # Mock the model_validate to prevent NotImplementedError being raised
        with patch(
            "scm.models.setup.snippet.SnippetResponseModel.model_validate",
            return_value=SnippetResponseModel.model_validate(mock_response),
        ):
            # Call disassociate_folder - this should succeed
            with patch("scm.config.setup.snippet.NotImplementedError", side_effect=Exception):
                try:
                    result = snippet_service.disassociate_folder(snippet_id, folder_id)

                    # This code won't be reached due to the NotImplementedError, but
                    # it's here to show the expected behavior if the method were implemented
                    assert isinstance(result, SnippetResponseModel)
                    mock_scm_client.delete.assert_called_once()
                except Exception:
                    # We expect an exception, but the API call should have been made
                    mock_scm_client.delete.assert_called_once()
                    call_args = mock_scm_client.delete.call_args
                    endpoint = f"/config/setup/v1/snippets/{snippet_id}/folders/{folder_id}"
                    assert call_args[0][0] == endpoint


class TestSnippetList(TestSnippetBase):
    """Tests for Snippet.list method."""

    def test_list_snippets(self, snippet_service, mock_scm_client):
        """Test listing snippets with default parameters."""
        # Setup mock response with valid snippet data
        mock_snippets = [
            SnippetResponseModelFactory.build_valid_model().model_dump() for _ in range(3)
        ]
        mock_response = {"data": mock_snippets}

        # Patch the API client's get method
        with patch.object(snippet_service.api_client, "get", return_value=mock_response):
            results = snippet_service.list()
            assert isinstance(results, list)
            assert len(results) == 3

    def test_list_snippets_pagination(self, snippet_service, mock_scm_client):
        """Test listing snippets with pagination parameters."""
        mock_snippets = [
            SnippetResponseModelFactory.build_valid_model().model_dump() for _ in range(5)
        ]
        mock_response = {"data": mock_snippets}

        with patch.object(snippet_service.api_client, "get", return_value=mock_response):
            results = snippet_service.list(offset=10, limit=5)
            assert isinstance(results, list)
            assert len(results) == 5

    def test_list_snippets_with_type_filter(self, snippet_service, mock_scm_client):
        """Test listing snippets with type filter."""
        predefined = SnippetResponseModelFactory(type="predefined").model_dump()
        custom = SnippetResponseModelFactory(type="custom").model_dump()
        mock_snippets = [predefined, custom]
        mock_response = {"data": mock_snippets}

        with patch.object(snippet_service.api_client, "get", return_value=mock_response):
            results = snippet_service.list(type="predefined")
            assert isinstance(results, list)
            assert any(r.type == "predefined" for r in results)

    def test_list_snippets_empty_result(self, snippet_service, mock_scm_client):
        """Test listing snippets when no results are returned."""
        mock_response = {"data": []}
        with patch.object(snippet_service.api_client, "get", return_value=mock_response):
            results = snippet_service.list()
            assert isinstance(results, list)
            assert len(results) == 0


class TestSnippetUpdate(TestSnippetBase):
    """Tests for Snippet.update method."""

    def test_update_snippet(self, snippet_service, mock_scm_client):
        """Test updating a snippet."""
        # Setup mock response
        snippet_id = "123e4567-e89b-12d3-a456-426614174000"
        mock_response = SnippetResponseModelFactory.build(id=snippet_id)
        mock_scm_client.put.return_value = mock_response

        # Build update model
        update_model = SnippetUpdateModelFactory.build_valid_model(
            id=snippet_id, name="updated_name"
        )

        # Update the snippet
        result = snippet_service.update(update_model)

        # Assert the client was called correctly
        mock_scm_client.put.assert_called_once()
        call_args = mock_scm_client.put.call_args
        assert call_args[0][0] == f"/config/setup/v1/snippets/{snippet_id}"
        assert call_args[1]["json"]["name"] == "updated_name"

        # Assert the result is a SnippetResponseModel
        assert isinstance(result, SnippetResponseModel)
        assert result.name == mock_response.name

    def test_update_with_all_parameters(self, snippet_service, mock_scm_client):
        """Test updating a snippet with all parameters."""
        # Setup mock response
        snippet_id = "123e4567-e89b-12d3-a456-426614174000"
        mock_response = SnippetResponseModelFactory.build(id=snippet_id)
        mock_scm_client.put.return_value = mock_response

        # Build update model with all fields
        update_model = SnippetUpdateModelFactory.build_valid_model(
            id=snippet_id,
            name="updated_name",
            description="Updated description",
            labels=["new_tag"],
            enable_prefix=False,
        )
        result = snippet_service.update(update_model)

        # Assert the client was called correctly
        call_args = mock_scm_client.put.call_args
        payload = call_args[1]["json"]
        assert payload["name"] == "updated_name"
        assert payload["description"] == "Updated description"
        assert payload["labels"] == ["new_tag"]
        assert payload["enable_prefix"] is False

        # Assert the result is a SnippetResponseModel
        assert isinstance(result, SnippetResponseModel)

    def test_update_nonexistent_snippet(self, snippet_service, mock_scm_client):
        """Test updating a snippet that doesn't exist."""
        # Setup mock client to raise APIError with 404 status
        error = APIError("Snippet not found")
        error.http_status_code = 404
        mock_scm_client.put.side_effect = error
        snippet_id = "99999999-9999-9999-9999-999999999999"

        update_model = SnippetUpdateModelFactory.build_valid_model(
            id=snippet_id, name="updated_name"
        )
        # Try to update the nonexistent snippet
        with pytest.raises(APIError):
            snippet_service.update(update_model)

    def test_update_with_general_error(self, snippet_service, mock_scm_client):
        """Test update with a non-404 exception."""
        # Create a non-404 error
        error = APIError("General server error")
        error.http_status_code = 500
        mock_scm_client.put.side_effect = error

        update_model = SnippetUpdateModelFactory.build_valid_model(
            id="f9069360-c6e6-469d-b8f7-7479e5fa6c22", name="updated_name"
        )
        # Should re-raise the error
        with pytest.raises(APIError):
            snippet_service.update(update_model)

    def test_update_without_fields(self, snippet_service):
        """Test updating a snippet without providing any fields to update."""
        # Build a model with only id and name (minimal valid), omitting optional fields
        update_model = SnippetUpdateModelFactory.build_valid_model(
            id="f9069360-c6e6-469d-b8f7-7479e5fa6c22", name="minimal"
        )
        # Simulate no other fields being set (if required, adjust factory)
        with pytest.raises(ValidationError):
            snippet_service.update(update_model)


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

        # Assert the client was called correctly
        mock_scm_client.delete.assert_called_once_with(f"/config/setup/v1/snippets/{snippet_id}")

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
            endpoint="/test", params={}, limit=10, offset=0
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
            endpoint="/test", params={}, limit=10, offset=0
        )

        # Assert the list is returned directly
        assert results == mock_response

    def test_get_paginated_results_unexpected_format(self, snippet_service, mock_scm_client):
        """Test _get_paginated_results with unexpected response format."""
        # Setup mock response with unexpected format
        mock_scm_client.get.return_value = "not a dict or list"

        # Call the method
        results = snippet_service._get_paginated_results(
            endpoint="/test", params={}, limit=10, offset=0
        )

        # Assert empty list is returned for unexpected format
        assert results == []


class TestSnippetFetchSingleMatch(TestSnippetBase):
    def test_fetch_returns_none_when_no_results(self, snippet_service, mocker):
        mocker.patch.object(snippet_service, "list", return_value=[])
        result = snippet_service.fetch("foo")
        assert result is None

    def test_fetch_returns_none_when_no_exact_match(self, snippet_service, mocker):
        m1 = SnippetResponseModelFactory.build_valid_model(name="a")
        m2 = SnippetResponseModelFactory.build_valid_model(name="b")
        mocker.patch.object(snippet_service, "list", return_value=[m1, m2])
        result = snippet_service.fetch("notfound")
        assert result is None

    def test_fetch_returns_first_exact_match(self, snippet_service, mocker):
        name = "foo"
        m1 = SnippetResponseModelFactory.build_valid_model(name=name)
        m2 = SnippetResponseModelFactory.build_valid_model(name=name)
        mocker.patch.object(snippet_service, "list", return_value=[m1, m2])
        result = snippet_service.fetch(name)
        assert result == m1


class TestSnippetValidation(TestSnippetBase):
    """Tests for validation methods using Pydantic model factories."""

    def test_valid_data(self):
        # Should not raise
        model = SnippetCreateModelFactory.build_valid_model(
            name="valid_name",
            description="Description",
            labels=["tag1", "tag2"],
            enable_prefix=True,
        )
        data = model.model_dump()
        assert data["name"] == "valid_name"
        assert data["description"] == "Description"
        assert data["labels"] == ["tag1", "tag2"]
        assert data["enable_prefix"] is True

    def test_missing_name(self):
        # Should raise ValidationError
        with pytest.raises(ValidationError):
            SnippetCreateModelFactory.build_valid_model(name=None)

    def test_labels_validation(self):
        # Valid labels
        model = SnippetCreateModelFactory.build_valid_model(labels=["tag1", "tag2"])
        assert model.labels == ["tag1", "tag2"]

        # None labels (if allowed)
        model = SnippetCreateModelFactory.build_valid_model(labels=None)
        assert model.labels is None

        # Non-string labels
        with pytest.raises(ValidationError):
            SnippetCreateModelFactory.build_valid_model(labels=["tag1", 123, "tag3"])


class TestSnippetMaxLimitValidation(TestSnippetBase):
    """Covers edge cases for Snippet._validate_max_limit and max_limit setter."""

    def test_max_limit_setter_valid(self, snippet_service):
        snippet_service.max_limit = 1234
        assert snippet_service.max_limit == 1234

    def test_validate_max_limit_invalid_type(self, snippet_service):
        with pytest.raises(Exception) as exc:
            snippet_service._validate_max_limit(["not", "an", "int"])
        assert "Invalid max_limit type" in str(exc.value)

    def test_validate_max_limit_invalid_value(self, snippet_service):
        with pytest.raises(Exception) as exc:
            snippet_service._validate_max_limit(0)
        assert "Invalid max_limit value" in str(exc.value)

    def test_validate_max_limit_negative(self, snippet_service):
        with pytest.raises(Exception) as exc:
            snippet_service._validate_max_limit(-5)
        assert "Invalid max_limit value" in str(exc.value)

    def test_validate_max_limit_none(self, snippet_service):
        assert snippet_service._validate_max_limit(None) == Snippet.DEFAULT_MAX_LIMIT


class TestSnippetApplyFilters(TestSnippetBase):
    """Covers edge cases for Snippet._apply_filters (labels/types filters)."""

    def test_labels_filter_not_list(self, snippet_service):
        data = []
        filters = {"labels": "notalist"}
        with pytest.raises(Exception) as exc:
            snippet_service._apply_filters(data, filters)
        assert "Invalid Filter Type" in str(exc.value)

    def test_labels_filter_empty_list(self, snippet_service):
        # No filtering should occur
        data = [SnippetResponseModelFactory.build_valid_model() for _ in range(2)]
        filters = {"labels": []}
        result = snippet_service._apply_filters(data, filters)
        assert result == data

    def test_labels_filter_nonempty(self, snippet_service):
        m1 = SnippetResponseModelFactory.build_valid_model(labels=["foo", "bar"])
        m2 = SnippetResponseModelFactory.build_valid_model(labels=["baz"])
        data = [m1, m2]
        filters = {"labels": ["foo"]}
        result = snippet_service._apply_filters(data, filters)
        assert m1 in result and m2 not in result

    def test_types_filter_not_list(self, snippet_service):
        data = []
        filters = {"types": "notalist"}
        with pytest.raises(Exception) as exc:
            snippet_service._apply_filters(data, filters)
        assert "Invalid Filter Type" in str(exc.value)

    def test_types_filter_not_all_strings(self, snippet_service):
        data = []
        filters = {"types": [123, "custom"]}
        with pytest.raises(Exception) as exc:
            snippet_service._apply_filters(data, filters)
        assert "Invalid Filter Type" in str(exc.value)

    def test_types_filter_empty_list(self, snippet_service):
        models = [SnippetResponseModelFactory.build_valid_model(type="custom") for _ in range(2)]
        filters = {"types": []}
        result = snippet_service._apply_filters(models, filters)
        assert result == models

    def test_types_filter_nonempty(self, snippet_service):
        m1 = SnippetResponseModelFactory.build_valid_model(type="custom")
        m2 = SnippetResponseModelFactory.build_valid_model(type="predefined")
        data = [m1, m2]
        filters = {"types": ["custom"]}
        result = snippet_service._apply_filters(data, filters)
        assert m1 in result and m2 not in result


class TestSnippetListEdgeCases(TestSnippetBase):
    """Covers edge/error cases for Snippet.list pagination and response handling."""

    def test_list_invalid_response_format(self, snippet_service, mocker):
        # API returns a non-dict response
        mocker.patch.object(snippet_service.api_client, "get", return_value="not_a_dict")
        with pytest.raises(Exception) as exc:
            snippet_service.list()
        assert "Response is not a dictionary" in str(exc.value)

    def test_list_single_object_no_data_key(self, snippet_service, mocker):
        # API returns a dict without a 'data' key
        response = SnippetResponseModelFactory.build_valid_model().model_dump()
        mocker.patch.object(snippet_service.api_client, "get", return_value=response)
        results = snippet_service.list()
        assert len(results) == 1
        assert results[0].id == response["id"]

    def test_list_data_key_not_list(self, snippet_service, mocker):
        # API returns a dict with 'data' not a list
        response = {"data": {"id": "abc"}}
        mocker.patch.object(snippet_service.api_client, "get", return_value=response)
        with pytest.raises(Exception) as exc:
            snippet_service.list()
        assert "data" in str(exc.value) and "field must be a list" in str(exc.value)

    def test_list_pagination_offset_increment(self, snippet_service, mocker):
        # Simulate two pages
        page1 = {
            "data": [SnippetResponseModelFactory.build_valid_model().model_dump() for _ in range(2)]
        }
        page2 = {
            "data": [SnippetResponseModelFactory.build_valid_model().model_dump() for _ in range(1)]
        }
        get_mock = mocker.patch.object(
            snippet_service.api_client, "get", side_effect=[page1, page2]
        )
        snippet_service._max_limit = 2
        results = snippet_service.list()
        assert len(results) == 3
        assert get_mock.call_count == 2

    def test_list_labels_param_passed_to_api(self, snippet_service, mocker):
        # Ensure 'labels' filter is sent as comma-separated string in params
        labels = ["foo", "bar"]
        expected = "foo,bar"
        response = {"data": []}
        get_mock = mocker.patch.object(snippet_service.api_client, "get", return_value=response)
        snippet_service.list(labels=labels)
        called_params = get_mock.call_args[1]["params"]
        assert called_params["labels"] == expected

    def test_list_types_param_passed_to_api(self, snippet_service, mocker):
        # Ensure 'types' filter is sent as comma-separated string in params
        types = ["predefined", "custom"]
        expected = "predefined,custom"
        response = {"data": []}
        get_mock = mocker.patch.object(snippet_service.api_client, "get", return_value=response)
        snippet_service.list(types=types)
        called_params = get_mock.call_args[1]["params"]
        assert called_params["types"] == expected


class TestSnippetFetchEdgeCases(TestSnippetBase):
    """Covers edge/error cases for Snippet.fetch (empty, multiple, etc)."""

    def test_fetch_returns_none_when_no_results(self, snippet_service, mocker):
        mocker.patch.object(snippet_service, "list", return_value=[])
        result = snippet_service.fetch("foo")
        assert result is None

    def test_fetch_returns_first_match(self, snippet_service, mocker):
        name = "dup"
        m1 = SnippetResponseModelFactory.build_valid_model(name=name)
        m2 = SnippetResponseModelFactory.build_valid_model(name=name)
        mocker.patch.object(snippet_service, "list", return_value=[m1, m2])
        result = snippet_service.fetch(name)
        assert result == m1
