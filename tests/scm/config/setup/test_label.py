# tests/scm/config/setup/test_label.py

# Standard library imports
from unittest.mock import MagicMock, patch
from uuid import UUID

from pydantic import ValidationError
import pytest

# Local SDK imports
from scm.client import Scm
from scm.config.setup.label import Label
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.setup.label import (
    LabelCreateModel,
    LabelResponseModel,
    LabelUpdateModel,
)
from tests.factories.setup.label import (
    LabelCreateModelDictFactory,
    LabelResponseModelFactory,
    LabelUpdateModelFactory,
)


class TestLabelBase:
    """Base class for Label service tests with common fixtures."""

    @pytest.fixture
    def mock_scm_client(self):
        """Create a properly mocked SCM client that passes type checks."""
        client = MagicMock(spec=Scm)
        return client

    @pytest.fixture
    def label_service(self, mock_scm_client):
        """Create a Label service with a mocked client for testing."""
        with patch("scm.config.isinstance", return_value=True):
            service = Label(mock_scm_client)
            return service


class TestLabelInitialization(TestLabelBase):
    """Tests for Label service initialization."""

    def test_init_with_default_max_limit(self, mock_scm_client):
        """Test initialization with default max_limit."""
        with patch("scm.config.isinstance", return_value=True):
            label = Label(mock_scm_client)
            assert label.api_client == mock_scm_client
            assert label.ENDPOINT == "/config/setup/v1/labels"
            assert label.max_limit == Label.DEFAULT_MAX_LIMIT

    def test_init_with_custom_max_limit(self, mock_scm_client):
        """Test initialization with custom max_limit."""
        with patch("scm.config.isinstance", return_value=True):
            custom_limit = 1000
            label = Label(mock_scm_client, max_limit=custom_limit)
            assert label.max_limit == custom_limit

    def test_init_with_exceeding_max_limit(self, mock_scm_client):
        """Test initialization with max_limit exceeding the absolute maximum."""
        with patch("scm.config.isinstance", return_value=True):
            exceeding_limit = Label.ABSOLUTE_MAX_LIMIT + 1000
            label = Label(mock_scm_client, max_limit=exceeding_limit)
            # For Label, exceeding limit is capped at ABSOLUTE_MAX_LIMIT
            assert label.max_limit == Label.ABSOLUTE_MAX_LIMIT


class TestLabelPydanticModel:
    """Tests for the Label model classes."""

    def test_label_create_model_validate(self):
        """Test model validation for LabelCreateModel."""
        # Create a valid model
        valid_data = {"name": "test_label", "description": "Test label description"}
        model = LabelCreateModel.model_validate(valid_data)
        assert model.name == "test_label"
        assert model.description == "Test label description"

    def test_label_update_model_validate(self):
        """Test model validation for LabelUpdateModel."""
        # Create a valid model
        valid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test_label",
            "description": "Test label description",
        }
        model = LabelUpdateModel.model_validate(valid_data)
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "test_label"
        assert model.description == "Test label description"


class TestLabelCreate(TestLabelBase):
    """Tests for Label.create method."""

    def test_create_label(self, label_service, mock_scm_client):
        """Test creating a label with minimum required fields."""
        # Setup mock response
        mock_response = LabelResponseModelFactory.build()
        mock_scm_client.post.return_value = mock_response

        # Create the label
        data = LabelCreateModelDictFactory.build_valid_dict(name="test_label")
        result = label_service.create(data=data)

        # Assert the client was called correctly
        mock_scm_client.post.assert_called_once()
        call_args = mock_scm_client.post.call_args
        assert call_args[0][0] == "/config/setup/v1/labels"
        assert call_args[1]["json"]["name"] == "test_label"

        # Assert the result is a LabelResponseModel
        assert isinstance(result, LabelResponseModel)
        assert result.name == str(mock_response.name)
        assert str(result.id) == str(mock_response.id)

    def test_create_label_with_all_fields(self, label_service, mock_scm_client):
        """Test creating a label with all fields."""
        # Setup mock response
        mock_response = LabelResponseModelFactory.build()
        mock_scm_client.post.return_value = mock_response

        # Create the label with all fields
        data = {
            "name": "test_label",
            "description": "Test description",
        }
        result = label_service.create(data=data)

        # Assert the client was called correctly
        mock_scm_client.post.assert_called_once()
        call_args = mock_scm_client.post.call_args
        assert call_args[0][0] == "/config/setup/v1/labels"
        payload = call_args[1]["json"]
        assert payload["name"] == "test_label"
        assert payload["description"] == "Test description"

        # Assert the result is a LabelResponseModel
        assert isinstance(result, LabelResponseModel)

    def test_create_label_with_invalid_data(self, label_service):
        """Test creating a label with invalid data."""
        # Missing name (required field)
        with pytest.raises(ValidationError):
            data = {"description": "Missing name field"}
            label_service.create(data=data)


class TestLabelGet(TestLabelBase):
    """Tests for Label.get method."""

    def test_get_label(self, label_service, mock_scm_client):
        """Test retrieving a label by ID."""
        # Setup mock response
        mock_response = LabelResponseModelFactory.build()
        mock_scm_client.get.return_value = mock_response
        label_id = "123e4567-e89b-12d3-a456-426614174000"

        # Get the label
        result = label_service.get(label_id)

        # Assert the client was called correctly
        mock_scm_client.get.assert_called_once_with(f"/config/setup/v1/labels/{label_id}")

        # Assert the result is a LabelResponseModel
        assert isinstance(result, LabelResponseModel)
        assert str(result.id) == str(mock_response.id)
        assert result.name == str(mock_response.name)

    def test_get_nonexistent_label(self, label_service, mock_scm_client):
        """Test retrieving a label that doesn't exist."""
        # Setup mock client to raise APIError with 404 status
        error = APIError("Label not found")
        error.http_status_code = 404
        mock_scm_client.get.side_effect = error
        label_id = "nonexistent-id"

        # Try to get the nonexistent label
        with pytest.raises(ObjectNotPresentError):
            label_service.get(label_id)

        # Assert the client was called correctly
        mock_scm_client.get.assert_called_once_with(f"/config/setup/v1/labels/{label_id}")

    def test_get_with_general_error(self, label_service, mock_scm_client):
        """Test get with a non-404 API error."""
        # Create a non-404 API error (e.g., 500 server error)
        error = APIError("Server error")
        error.http_status_code = 500
        mock_scm_client.get.side_effect = error

        # Test with a try-except to ensure the original error is re-raised
        try:
            label_service.get("123")
            pytest.fail("Expected APIError was not raised")
        except APIError as e:
            # Verify we got the same error that was injected
            assert e is error
            assert e.http_status_code == 500
            assert "Server error" in e.message


class TestLabelList(TestLabelBase):
    """Tests for Label.list method."""

    def test_list_labels(self, label_service, mock_scm_client):
        """Test listing labels with default parameters."""
        # Setup mock response with valid label data
        mock_labels = [LabelResponseModelFactory.build_valid_model().model_dump() for _ in range(3)]
        mock_response = {"data": mock_labels}

        # Patch the API client's get method
        with patch.object(label_service.api_client, "get", return_value=mock_response):
            results = label_service.list()
            assert isinstance(results, list)
            assert len(results) == 3

    def test_list_labels_pagination(self, label_service, mock_scm_client):
        """Test listing labels with pagination parameters."""
        # Setup two pages of response data
        page1 = {"data": [LabelResponseModelFactory.build().model_dump() for _ in range(5)]}
        page2 = {"data": [LabelResponseModelFactory.build().model_dump() for _ in range(3)]}

        # Mock the get method to return different responses for first and second calls
        mock_scm_client.get.side_effect = [page1, page2]

        # Set a low max_limit to force pagination
        label_service.max_limit = 5

        # Call list and verify pagination works
        results = label_service.list()

        # Verify expected results
        assert isinstance(results, list)
        assert len(results) == 8  # Combined total from both pages
        assert mock_scm_client.get.call_count == 2

        # Verify the second call had the correct offset
        second_call_args = mock_scm_client.get.call_args_list[1][1]
        assert second_call_args["params"]["offset"] == 5

    def test_list_empty_result(self, label_service, mock_scm_client):
        """Test listing labels when no results are returned."""
        mock_response = {"data": []}
        with patch.object(label_service.api_client, "get", return_value=mock_response):
            results = label_service.list()
            assert isinstance(results, list)
            assert len(results) == 0

    def test_list_with_filters(self, label_service, mock_scm_client):
        """Test listing labels with filters."""
        # Setup mock response
        mock_labels = [LabelResponseModelFactory.build_valid_model().model_dump() for _ in range(3)]
        mock_response = {"data": mock_labels}

        # Patch the API client's get method
        mock_get = MagicMock(return_value=mock_response)
        label_service.api_client.get = mock_get

        # Call list with a filter
        label_service.list(type="fqdn")

        # Verify filter was passed to API call
        call_args = mock_get.call_args[1]
        assert "params" in call_args
        assert call_args["params"]["type"] == "fqdn"


class TestLabelUpdate(TestLabelBase):
    """Tests for Label.update method."""

    def test_update_label_with_update_model(self, label_service, mock_scm_client):
        """Test updating a label with LabelUpdateModel."""
        # Setup mock response
        label_id = "123e4567-e89b-12d3-a456-426614174000"
        mock_response = LabelResponseModelFactory.build(id=label_id)
        # Simulate the API returning a list instead of a single object
        mock_scm_client.put.return_value = [mock_response.model_dump()]

        # Build update model
        update_model = LabelUpdateModelFactory.build_valid_model(id=label_id, name="updated_name")

        # Update the label
        result = label_service.update(update_model)

        # Assert the client was called correctly
        mock_scm_client.put.assert_called_once()
        call_args = mock_scm_client.put.call_args
        assert call_args[0][0] == f"/config/setup/v1/labels/{label_id}"
        assert call_args[1]["json"]["name"] == "updated_name"

        # Assert the result is a LabelResponseModel
        assert isinstance(result, LabelResponseModel)
        assert result.name == mock_response.name

    def test_update_label_with_single_object_response(self, label_service, mock_scm_client):
        """Test updating a label when API returns a single object (not a list)."""
        # Setup mock response as a single object (not a list)
        label_id = "123e4567-e89b-12d3-a456-426614174000"
        mock_response = LabelResponseModelFactory.build(id=label_id)
        # Return a dictionary directly instead of a list
        mock_scm_client.put.return_value = mock_response.model_dump()

        # Build update model
        update_model = LabelUpdateModelFactory.build_valid_model(
            id=label_id, name="updated_name_single_object"
        )

        # Update the label
        result = label_service.update(update_model)

        # Assert the client was called correctly
        mock_scm_client.put.assert_called_once()
        call_args = mock_scm_client.put.call_args
        assert call_args[0][0] == f"/config/setup/v1/labels/{label_id}"
        assert call_args[1]["json"]["name"] == "updated_name_single_object"

        # Assert the result is a LabelResponseModel
        assert isinstance(result, LabelResponseModel)
        assert result.name == mock_response.name

    def test_update_label_with_response_model(self, label_service, mock_scm_client):
        """Test updating a label with LabelResponseModel."""
        # Setup mock response
        label_id = "123e4567-e89b-12d3-a456-426614174000"
        mock_response = LabelResponseModelFactory.build(id=label_id)
        # Simulate the API returning a list instead of a single object
        mock_scm_client.put.return_value = [mock_response.model_dump()]

        # Build response model for input
        input_response_model = LabelResponseModelFactory.build_valid_model(
            id=label_id, name="original_name", description="original_description"
        )

        # Update the label using response model
        result = label_service.update(input_response_model)

        # Assert the client was called correctly
        mock_scm_client.put.assert_called_once()
        call_args = mock_scm_client.put.call_args
        assert call_args[0][0] == f"/config/setup/v1/labels/{label_id}"

        # Verify payload has name and description from response model
        payload = call_args[1]["json"]
        assert payload["name"] == "original_name"
        assert payload["description"] == "original_description"

        # Assert the result is a LabelResponseModel
        assert isinstance(result, LabelResponseModel)
        assert result.name == mock_response.name

    def test_update_with_all_parameters(self, label_service, mock_scm_client):
        """Test updating a label with all parameters."""
        # Setup mock response
        label_id = "123e4567-e89b-12d3-a456-426614174000"
        mock_response = LabelResponseModelFactory.build(id=label_id)
        # Simulate the API returning a list instead of a single object
        mock_scm_client.put.return_value = [mock_response.model_dump()]

        # Build update model with all fields that the model actually supports
        update_model = LabelUpdateModelFactory.build_valid_model(
            id=label_id, name="updated_name", description="Updated description"
        )
        result = label_service.update(update_model)

        # Assert the client was called correctly
        call_args = mock_scm_client.put.call_args
        payload = call_args[1]["json"]
        assert payload["name"] == "updated_name"
        assert payload["description"] == "Updated description"

        # Note: The model definition in scm/models/setup/label.py doesn't include
        # type, value, or folder fields even though the tests were checking for them.
        # The actual model only has name and description.

        # Assert the result is a LabelResponseModel
        assert isinstance(result, LabelResponseModel)

    def test_update_nonexistent_label(self, label_service, mock_scm_client):
        """Test updating a label that doesn't exist."""
        # Setup mock client to raise APIError with 404 status
        error = APIError("Label not found")
        error.http_status_code = 404
        mock_scm_client.put.side_effect = error
        label_id = "99999999-9999-9999-9999-999999999999"

        update_model = LabelUpdateModelFactory.build_valid_model(id=label_id, name="updated_name")
        # Try to update the nonexistent label
        with pytest.raises(APIError):
            label_service.update(update_model)

    def test_update_with_general_error(self, label_service, mock_scm_client):
        """Test update with a non-404 exception."""
        # Create a non-404 error
        error = APIError("General server error")
        error.http_status_code = 500
        mock_scm_client.put.side_effect = error

        update_model = LabelUpdateModelFactory.build_valid_model(
            id="f9069360-c6e6-469d-b8f7-7479e5fa6c22", name="updated_name"
        )
        # Should re-raise the error
        with pytest.raises(APIError):
            label_service.update(update_model)


class TestLabelDelete(TestLabelBase):
    """Tests for Label.delete method."""

    def test_delete_label(self, label_service, mock_scm_client):
        """Test deleting a label."""
        # Setup mock client
        label_id = "123e4567-e89b-12d3-a456-426614174000"

        # Delete the label
        label_service.delete(label_id)

        # Assert the client was called correctly
        mock_scm_client.delete.assert_called_once_with(f"/config/setup/v1/labels/{label_id}")

    def test_delete_nonexistent_label(self, label_service, mock_scm_client):
        """Test deleting a label that doesn't exist."""
        # Setup mock client to raise APIError with 404 status
        error = APIError("Label not found")
        error.http_status_code = 404
        mock_scm_client.delete.side_effect = error
        label_id = "nonexistent-id"

        # Try to delete the nonexistent label
        with pytest.raises(ObjectNotPresentError):
            label_service.delete(label_id)

        # Assert the client was called correctly
        mock_scm_client.delete.assert_called_once_with(f"/config/setup/v1/labels/{label_id}")

    def test_delete_with_general_error(self, label_service, mock_scm_client):
        """Test delete with a non-404 exception."""
        # Create a non-404 error
        error = APIError("General server error")
        error.http_status_code = 500
        mock_scm_client.delete.side_effect = error

        # Should re-raise the error
        with pytest.raises(APIError):
            label_service.delete("123")


class TestLabelFetch(TestLabelBase):
    """Tests for Label.fetch method."""

    def test_fetch_label_by_name(self, label_service):
        """Test fetching a label by name."""
        name = "test_label"
        # Create a mock label response
        mock_label = LabelResponseModelFactory.build_valid_model(name=name)

        # Mock the list method to return our test label
        with patch.object(label_service, "list", return_value=[mock_label]):
            result = label_service.fetch(name)

            # Assert correct label is returned
            assert result is not None
            assert result.name == name

    def test_fetch_nonexistent_label(self, label_service):
        """Test fetching a label that doesn't exist."""
        # Mock the list method to return empty list
        with patch.object(label_service, "list", return_value=[]):
            result = label_service.fetch("nonexistent")

            # Assert None is returned
            assert result is None

    def test_fetch_with_multiple_matches(self, label_service):
        """Test fetch returns only the first match when multiple exist."""
        name = "duplicate_name"
        # Create two mock labels with the same name but different descriptions
        label1 = LabelResponseModel(
            id=UUID("11111111-e89b-12d3-a456-426655440000"), name=name, description="Description 1"
        )
        label2 = LabelResponseModel(
            id=UUID("22222222-e89b-12d3-a456-426655440000"), name=name, description="Description 2"
        )

        # Mock the list method to return both labels
        with patch.object(label_service, "list", return_value=[label1, label2]):
            result = label_service.fetch(name)

            # Assert first matching label is returned
            assert result is not None
            assert result.name == name
            assert result.description == "Description 1"  # Should be the first one

    def test_fetch_no_exact_match(self, label_service):
        """Test fetch with no exact matches."""
        # Create mock labels with different names
        var1 = LabelResponseModelFactory.build_valid_model(name="name1")
        var2 = LabelResponseModelFactory.build_valid_model(name="name2")

        # Mock the list method to return these labels
        with patch.object(label_service, "list", return_value=[var1, var2]):
            result = label_service.fetch("different_name")

            # Assert None is returned (no match)
            assert result is None


class TestLabelMaxLimitValidation(TestLabelBase):
    """Tests for max_limit validation in Label class."""

    def test_validate_max_limit_none(self, label_service):
        """Test validating None max_limit."""
        result = label_service._validate_max_limit(None)
        assert result == Label.DEFAULT_MAX_LIMIT

    def test_validate_max_limit_invalid_type(self, label_service):
        """Test validating invalid type for max_limit."""
        with pytest.raises(InvalidObjectError):
            label_service._validate_max_limit("not_an_int")

    def test_validate_max_limit_too_low(self, label_service):
        """Test validating max_limit that is too low."""
        with pytest.raises(InvalidObjectError):
            label_service._validate_max_limit(0)

    def test_validate_max_limit_too_high(self, label_service):
        """Test validating max_limit that is too high."""
        # In Label, this returns ABSOLUTE_MAX_LIMIT instead of raising an error
        result = label_service._validate_max_limit(Label.ABSOLUTE_MAX_LIMIT + 100)
        assert result == Label.ABSOLUTE_MAX_LIMIT

    def test_max_limit_setter(self, label_service):
        """Test setting max_limit property."""
        label_service.max_limit = 500
        assert label_service.max_limit == 500
        assert label_service._max_limit == 500


class TestLabelGetPaginatedResults(TestLabelBase):
    """Tests for _get_paginated_results helper method."""

    def test_get_paginated_results_dict_with_data(self, label_service, mock_scm_client):
        """Test _get_paginated_results with dict response containing 'data'."""
        # Setup mock response
        mock_response = {"data": [{"id": "1", "name": "test1"}, {"id": "2", "name": "test2"}]}
        mock_scm_client.get.return_value = mock_response

        # Call the method
        results = label_service._get_paginated_results(
            endpoint="/test", params={}, limit=10, offset=0
        )

        # Assert correct data is extracted
        assert results == mock_response["data"]

    def test_get_paginated_results_list_response(self, label_service, mock_scm_client):
        """Test _get_paginated_results with list response."""
        # Setup mock response
        mock_response = [{"id": "1", "name": "test1"}, {"id": "2", "name": "test2"}]
        mock_scm_client.get.return_value = mock_response

        # Call the method
        results = label_service._get_paginated_results(
            endpoint="/test", params={}, limit=10, offset=0
        )

        # Assert the list is returned directly
        assert results == mock_response

    def test_get_paginated_results_unexpected_format(self, label_service, mock_scm_client):
        """Test _get_paginated_results with unexpected response format."""
        # Setup mock response with unexpected format
        mock_scm_client.get.return_value = "not a dict or list"

        # Call the method
        results = label_service._get_paginated_results(
            endpoint="/test", params={}, limit=10, offset=0
        )

        # Assert empty list is returned for unexpected format
        assert results == []
