# tests/scm/config/setup/test_label.py

# Standard library imports
from unittest.mock import MagicMock, patch
from uuid import UUID

import pytest
from pydantic import ValidationError

# Local SDK imports
from scm.client import Scm
from scm.config.setup.label import Label
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.setup.label import (
    LabelBaseModel,
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

    def test_validate_container_type_valid(self):
        """Test validate_container_type with valid container configuration."""
        # Test with folder only
        values_with_folder = {"folder": "test_folder", "snippet": None, "device": None}
        assert (
            LabelBaseModel.validate_container_type(values_with_folder)
            == values_with_folder
        )

        # Test with snippet only
        values_with_snippet = {
            "folder": None,
            "snippet": "test_snippet",
            "device": None,
        }
        assert (
            LabelBaseModel.validate_container_type(values_with_snippet)
            == values_with_snippet
        )

        # Test with device only
        values_with_device = {"folder": None, "snippet": None, "device": "test_device"}
        assert (
            LabelBaseModel.validate_container_type(values_with_device)
            == values_with_device
        )

    def test_validate_container_type_multiple_containers(self):
        """Test validate_container_type with multiple containers set."""
        # Test with folder and snippet
        values = {"folder": "test_folder", "snippet": "test_snippet", "device": None}
        with pytest.raises(ValueError) as excinfo:
            LabelBaseModel.validate_container_type(values)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided"
            in str(excinfo.value)
        )

        # Test with all three containers
        values = {
            "folder": "test_folder",
            "snippet": "test_snippet",
            "device": "test_device",
        }
        with pytest.raises(ValueError) as excinfo:
            LabelBaseModel.validate_container_type(values)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided"
            in str(excinfo.value)
        )

    def test_validate_container_type_no_container(self):
        """Test validate_container_type with no container set."""
        values = {"folder": None, "snippet": None, "device": None}
        with pytest.raises(ValueError) as excinfo:
            LabelBaseModel.validate_container_type(values)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided"
            in str(excinfo.value)
        )

    def test_validate_type_enum_valid(self):
        """Test the type enum validator with valid types."""
        for valid_type in [
            "percent",
            "count",
            "ip-netmask",
            "zone",
            "ip-range",
            "ip-wildcard",
            "device-priority",
            "device-id",
            "egress-max",
            "as-number",
            "fqdn",
            "port",
            "link-tag",
            "group-id",
            "rate",
            "router-id",
            "qos-profile",
            "timer",
        ]:
            assert LabelBaseModel.validate_type_enum(valid_type) == valid_type

    def test_validate_type_enum_invalid(self):
        """Test the type enum validator with invalid types."""
        with pytest.raises(ValueError) as excinfo:
            LabelBaseModel.validate_type_enum("invalid-type")
        assert "type must be one of" in str(excinfo.value)

    def test_label_create_model_validate(self):
        """Test model validation for LabelCreateModel."""
        # Create a valid model
        valid_data = {
            "name": "test_var",
            "type": "fqdn",
            "value": "example.com",
            "folder": "test_folder",
        }
        model = LabelCreateModel.model_validate(valid_data)
        assert model.name == "test_var"
        assert model.type == "fqdn"
        assert model.value == "example.com"
        assert model.folder == "test_folder"

        # Test with invalid container (multiple containers set)
        invalid_data = valid_data.copy()
        invalid_data["snippet"] = "test_snippet"
        with pytest.raises(ValueError) as excinfo:
            LabelCreateModel.model_validate(invalid_data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided"
            in str(excinfo.value)
        )

    def test_label_update_model_validate(self):
        """Test model validation for LabelUpdateModel."""
        # Create a valid model
        valid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test_var",
            "type": "fqdn",
            "value": "example.com",
            "folder": "test_folder",
        }
        model = LabelUpdateModel.model_validate(valid_data)
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "test_var"
        assert model.type == "fqdn"
        assert model.value == "example.com"
        assert model.folder == "test_folder"

        # Test with invalid container (no container set)
        invalid_data = valid_data.copy()
        invalid_data["folder"] = None
        with pytest.raises(ValueError) as excinfo:
            LabelUpdateModel.model_validate(invalid_data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided"
            in str(excinfo.value)
        )


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
        data = LabelCreateModelDictFactory.build_valid_dict(
            name="test_label",
            type="fqdn",
            value="example.com",
            description="Test description",
            folder="test_folder",
        )
        result = label_service.create(data=data)

        # Assert the client was called correctly
        mock_scm_client.post.assert_called_once()
        call_args = mock_scm_client.post.call_args
        assert call_args[0][0] == "/config/setup/v1/labels"
        payload = call_args[1]["json"]
        assert payload["name"] == "test_label"
        assert payload["type"] == "fqdn"
        assert payload["value"] == "example.com"
        assert payload["description"] == "Test description"
        assert payload["folder"] == "test_folder"

        # Assert the result is a LabelResponseModel
        assert isinstance(result, LabelResponseModel)

    def test_create_label_with_invalid_data(self, label_service):
        """Test creating a label with invalid data."""
        # Missing type
        with pytest.raises(ValidationError):
            data = LabelCreateModelDictFactory.build_valid_dict()
            data.pop("type")
            label_service.create(data=data)

        # Missing value
        with pytest.raises(ValidationError):
            data = LabelCreateModelDictFactory.build_valid_dict()
            data.pop("value")
            label_service.create(data=data)

        # Invalid type
        with pytest.raises(ValidationError):
            data = LabelCreateModelDictFactory.build_valid_dict(type="invalid_type")
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
        mock_scm_client.get.assert_called_once_with(
            f"/config/setup/v1/labels/{label_id}"
        )

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
        mock_scm_client.get.assert_called_once_with(
            f"/config/setup/v1/labels/{label_id}"
        )

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
        mock_labels = [
            LabelResponseModelFactory.build_valid_model().model_dump() for _ in range(3)
        ]
        mock_response = {"data": mock_labels}

        # Patch the API client's get method
        with patch.object(label_service.api_client, "get", return_value=mock_response):
            results = label_service.list()
            assert isinstance(results, list)
            assert len(results) == 3

    def test_list_labels_pagination(self, label_service, mock_scm_client):
        """Test listing labels with pagination parameters."""
        # Setup two pages of response data
        page1 = {
            "data": [LabelResponseModelFactory.build().model_dump() for _ in range(5)]
        }
        page2 = {
            "data": [LabelResponseModelFactory.build().model_dump() for _ in range(3)]
        }

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
        mock_labels = [
            LabelResponseModelFactory.build_valid_model().model_dump() for _ in range(3)
        ]
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
        update_model = LabelUpdateModelFactory.build_valid_model(
            id=label_id, name="updated_name"
        )

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
            id=label_id,
            name="updated_name",
            description="Updated description"
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

        update_model = LabelUpdateModelFactory.build_valid_model(
            id=label_id, name="updated_name"
        )
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
        mock_scm_client.delete.assert_called_once_with(
            f"/config/setup/v1/labels/{label_id}"
        )

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
        mock_scm_client.delete.assert_called_once_with(
            f"/config/setup/v1/labels/{label_id}"
        )

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
        # Create two mock labels with the same name
        var1 = LabelResponseModelFactory.build_valid_model(name=name, value="value1")
        var2 = LabelResponseModelFactory.build_valid_model(name=name, value="value2")

        # Mock the list method to return both labels
        with patch.object(label_service, "list", return_value=[var1, var2]):
            result = label_service.fetch(name)

            # Assert first matching label is returned
            assert result is not None
            assert result.name == name
            assert result.value == "value1"  # Should be the first one

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
        mock_response = {
            "data": [{"id": "1", "name": "test1"}, {"id": "2", "name": "test2"}]
        }
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

    def test_get_paginated_results_unexpected_format(
        self, label_service, mock_scm_client
    ):
        """Test _get_paginated_results with unexpected response format."""
        # Setup mock response with unexpected format
        mock_scm_client.get.return_value = "not a dict or list"

        # Call the method
        results = label_service._get_paginated_results(
            endpoint="/test", params={}, limit=10, offset=0
        )

        # Assert empty list is returned for unexpected format
        assert results == []


class TestLabelApplyFilters(TestLabelBase):
    """Tests for _apply_filters helper method."""

    def test_apply_no_filters(self, label_service):
        """Test _apply_filters with no filters."""
        # Create test data
        labels = [LabelResponseModelFactory.build_valid_model() for _ in range(3)]

        # Apply no filters
        result = label_service._apply_filters(labels, {})

        # Should return all labels unchanged
        assert result == labels

    def test_apply_labels_filter(self, label_service):
        """Test _apply_filters with labels filter."""
        # Create test labels with different labels
        var1 = LabelResponseModelFactory.build_valid_model(labels=["label1", "label2"])
        var2 = LabelResponseModelFactory.build_valid_model(labels=["label3"])
        var3 = LabelResponseModelFactory.build_valid_model(labels=["label1", "label3"])

        labels = [var1, var2, var3]

        # Apply labels filter
        result = label_service._apply_filters(labels, {"labels": ["label1"]})

        # Should return only labels with matching labels
        assert len(result) == 2
        assert var1 in result
        assert var2 not in result
        assert var3 in result

    def test_apply_parent_filter(self, label_service):
        """Test _apply_filters with parent filter."""
        # Create test labels with different parent values
        var1 = LabelResponseModelFactory.build_valid_model(parent="parent1")
        var2 = LabelResponseModelFactory.build_valid_model(parent="parent2")
        var3 = LabelResponseModelFactory.build_valid_model(parent="parent1")

        labels = [var1, var2, var3]

        # Apply parent filter
        result = label_service._apply_filters(labels, {"parent": "parent1"})

        # Should return only labels with matching parent
        assert len(result) == 2
        assert var1 in result
        assert var2 not in result
        assert var3 in result

    def test_apply_type_filter(self, label_service):
        """Test _apply_filters with type filter."""
        # Create test labels with different types
        var1 = LabelResponseModelFactory.build_valid_model(type="fqdn")
        var2 = LabelResponseModelFactory.build_valid_model(type="ip-netmask")
        var3 = LabelResponseModelFactory.build_valid_model(type="fqdn")

        labels = [var1, var2, var3]

        # Apply type filter
        result = label_service._apply_filters(labels, {"type": "fqdn"})

        # Should return only labels with matching type
        assert len(result) == 2
        assert var1 in result
        assert var2 not in result
        assert var3 in result

    def test_apply_snippets_filter(self, label_service):
        """Test _apply_filters with snippets filter."""
        # Create test labels with different snippets
        var1 = LabelResponseModelFactory.build_valid_model(
            snippets=["snippet1", "snippet2"]
        )
        var2 = LabelResponseModelFactory.build_valid_model(snippets=["snippet3"])
        var3 = LabelResponseModelFactory.build_valid_model(
            snippets=["snippet1", "snippet3"]
        )

        labels = [var1, var2, var3]

        # Apply snippets filter
        result = label_service._apply_filters(labels, {"snippets": ["snippet1"]})

        # Should return only labels with matching snippets
        assert len(result) == 2
        assert var1 in result
        assert var2 not in result
        assert var3 in result

    def test_apply_model_filter(self, label_service):
        """Test _apply_filters with model filter."""
        # Create test labels with different models
        var1 = LabelResponseModelFactory.build_valid_model(model="model1")
        var2 = LabelResponseModelFactory.build_valid_model(model="model2")
        var3 = LabelResponseModelFactory.build_valid_model(model="model1")

        labels = [var1, var2, var3]

        # Apply model filter
        result = label_service._apply_filters(labels, {"model": "model1"})

        # Should return only labels with matching model
        assert len(result) == 2
        assert var1 in result
        assert var2 not in result
        assert var3 in result

    def test_apply_serial_number_filter(self, label_service):
        """Test _apply_filters with serial_number filter."""
        # Create test labels with different serial_numbers
        var1 = LabelResponseModelFactory.build_valid_model(serial_number="sn1")
        var2 = LabelResponseModelFactory.build_valid_model(serial_number="sn2")
        var3 = LabelResponseModelFactory.build_valid_model(serial_number="sn1")

        labels = [var1, var2, var3]

        # Apply serial_number filter
        result = label_service._apply_filters(labels, {"serial_number": "sn1"})

        # Should return only labels with matching serial_number
        assert len(result) == 2
        assert var1 in result
        assert var2 not in result
        assert var3 in result

    def test_apply_device_only_filter(self, label_service):
        """Test _apply_filters with device_only filter."""
        # Create test labels with different device_only values
        var1 = LabelResponseModelFactory.build_valid_model(device_only=True)
        var2 = LabelResponseModelFactory.build_valid_model(device_only=False)
        var3 = LabelResponseModelFactory.build_valid_model(device_only=True)

        labels = [var1, var2, var3]

        # Apply device_only filter
        result = label_service._apply_filters(labels, {"device_only": True})

        # Should return only labels with matching device_only
        assert len(result) == 2
        assert var1 in result
        assert var2 not in result
        assert var3 in result

    def test_apply_multiple_filters(self, label_service):
        """Test _apply_filters with multiple filters."""
        # Create test labels with different combinations of attributes
        var1 = LabelResponseModelFactory.build_valid_model(
            type="fqdn", model="model1", device_only=True
        )
        var2 = LabelResponseModelFactory.build_valid_model(
            type="ip-netmask", model="model1", device_only=True
        )
        var3 = LabelResponseModelFactory.build_valid_model(
            type="fqdn", model="model2", device_only=True
        )
        var4 = LabelResponseModelFactory.build_valid_model(
            type="fqdn", model="model1", device_only=False
        )

        labels = [var1, var2, var3, var4]

        # Apply multiple filters
        result = label_service._apply_filters(
            labels, {"type": "fqdn", "model": "model1", "device_only": True}
        )

        # Should return only var1 which matches all filters
        assert len(result) == 1
        assert var1 in result
        assert var2 not in result  # Doesn't match type
        assert var3 not in result  # Doesn't match model
        assert var4 not in result  # Doesn't match device_only

    def test_filter_with_missing_attribute(self, label_service):
        """Test filtering when labels don't have the filtered attribute."""
        # Create labels without the filtered attributes
        var1 = LabelResponseModelFactory.build_valid_model()
        var2 = LabelResponseModelFactory.build_valid_model()

        labels = [var1, var2]

        # Try filtering by attributes that don't exist on the labels
        result = label_service._apply_filters(labels, {"labels": ["label1"]})

        # Should not match any labels since they don't have labels attribute
        assert len(result) == 0
