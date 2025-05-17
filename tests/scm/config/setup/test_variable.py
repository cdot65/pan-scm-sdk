# tests/scm/config/setup/test_variable.py

"""Tests for variable setup configuration."""

# Standard library imports
from unittest.mock import MagicMock, patch
from uuid import UUID

from pydantic import ValidationError
import pytest

# Local SDK imports
from scm.client import Scm
from scm.config.setup.variable import Variable
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.setup.variable import (
    VariableBaseModel,
    VariableCreateModel,
    VariableResponseModel,
    VariableUpdateModel,
)
from tests.factories.setup.variable import (
    VariableCreateModelDictFactory,
    VariableResponseModelFactory,
    VariableUpdateModelFactory,
)


class TestVariableBase:
    """Base class for Variable service tests with common fixtures."""

    @pytest.fixture
    def mock_scm_client(self):
        """Create a properly mocked SCM client that passes type checks."""
        client = MagicMock(spec=Scm)
        return client

    @pytest.fixture
    def variable_service(self, mock_scm_client):
        """Create a Variable service with a mocked client for testing."""
        with patch("scm.config.isinstance", return_value=True):
            service = Variable(mock_scm_client)
            return service


class TestVariableInitialization(TestVariableBase):
    """Tests for Variable service initialization."""

    def test_init_with_default_max_limit(self, mock_scm_client):
        """Test initialization with default max_limit."""
        with patch("scm.config.isinstance", return_value=True):
            variable = Variable(mock_scm_client)
            assert variable.api_client == mock_scm_client
            assert variable.ENDPOINT == "/config/setup/v1/variables"
            assert variable.max_limit == Variable.DEFAULT_MAX_LIMIT

    def test_init_with_custom_max_limit(self, mock_scm_client):
        """Test initialization with custom max_limit."""
        with patch("scm.config.isinstance", return_value=True):
            custom_limit = 1000
            variable = Variable(mock_scm_client, max_limit=custom_limit)
            assert variable.max_limit == custom_limit

    def test_init_with_exceeding_max_limit(self, mock_scm_client):
        """Test initialization with max_limit exceeding the absolute maximum."""
        with patch("scm.config.isinstance", return_value=True):
            exceeding_limit = Variable.ABSOLUTE_MAX_LIMIT + 1000
            variable = Variable(mock_scm_client, max_limit=exceeding_limit)
            # For Variable, exceeding limit is capped at ABSOLUTE_MAX_LIMIT
            assert variable.max_limit == Variable.ABSOLUTE_MAX_LIMIT


class TestVariablePydanticModel:
    """Tests for the Variable model classes."""

    def test_validate_container_type_valid(self):
        """Test validate_container_type with valid container configuration."""
        # Test with folder only
        values_with_folder = {"folder": "test_folder", "snippet": None, "device": None}
        assert VariableBaseModel.validate_container_type(values_with_folder) == values_with_folder

        # Test with snippet only
        values_with_snippet = {"folder": None, "snippet": "test_snippet", "device": None}
        assert VariableBaseModel.validate_container_type(values_with_snippet) == values_with_snippet

        # Test with device only
        values_with_device = {"folder": None, "snippet": None, "device": "test_device"}
        assert VariableBaseModel.validate_container_type(values_with_device) == values_with_device

    def test_validate_container_type_multiple_containers(self):
        """Test validate_container_type with multiple containers set."""
        # Test with folder and snippet
        values = {"folder": "test_folder", "snippet": "test_snippet", "device": None}
        with pytest.raises(ValueError) as excinfo:
            VariableBaseModel.validate_container_type(values)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            excinfo.value
        )

        # Test with all three containers
        values = {"folder": "test_folder", "snippet": "test_snippet", "device": "test_device"}
        with pytest.raises(ValueError) as excinfo:
            VariableBaseModel.validate_container_type(values)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            excinfo.value
        )

    def test_validate_container_type_no_container(self):
        """Test validate_container_type with no container set."""
        values = {"folder": None, "snippet": None, "device": None}
        with pytest.raises(ValueError) as excinfo:
            VariableBaseModel.validate_container_type(values)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            excinfo.value
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
            assert VariableBaseModel.validate_type_enum(valid_type) == valid_type

    def test_validate_type_enum_invalid(self):
        """Test the type enum validator with invalid types."""
        with pytest.raises(ValueError) as excinfo:
            VariableBaseModel.validate_type_enum("invalid-type")
        assert "type must be one of" in str(excinfo.value)

    def test_variable_create_model_validate(self):
        """Test model validation for VariableCreateModel."""
        # Create a valid model
        valid_data = {
            "name": "test_var",
            "type": "fqdn",
            "value": "example.com",
            "folder": "test_folder",
        }
        model = VariableCreateModel.model_validate(valid_data)
        assert model.name == "test_var"
        assert model.type == "fqdn"
        assert model.value == "example.com"
        assert model.folder == "test_folder"

        # Test with invalid container (multiple containers set)
        invalid_data = valid_data.copy()
        invalid_data["snippet"] = "test_snippet"
        with pytest.raises(ValueError) as excinfo:
            VariableCreateModel.model_validate(invalid_data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            excinfo.value
        )

    def test_variable_update_model_validate(self):
        """Test model validation for VariableUpdateModel."""
        # Create a valid model
        valid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test_var",
            "type": "fqdn",
            "value": "example.com",
            "folder": "test_folder",
        }
        model = VariableUpdateModel.model_validate(valid_data)
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "test_var"
        assert model.type == "fqdn"
        assert model.value == "example.com"
        assert model.folder == "test_folder"

        # Test with invalid container (no container set)
        invalid_data = valid_data.copy()
        invalid_data["folder"] = None
        with pytest.raises(ValueError) as excinfo:
            VariableUpdateModel.model_validate(invalid_data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            excinfo.value
        )


class TestVariableCreate(TestVariableBase):
    """Tests for Variable.create method."""

    def test_create_variable(self, variable_service, mock_scm_client):
        """Test creating a variable with minimum required fields."""
        # Setup mock response
        mock_response = VariableResponseModelFactory.build()
        mock_scm_client.post.return_value = mock_response

        # Create the variable
        data = VariableCreateModelDictFactory.build_valid_dict(name="test_variable")
        result = variable_service.create(data=data)

        # Assert the client was called correctly
        mock_scm_client.post.assert_called_once()
        call_args = mock_scm_client.post.call_args
        assert call_args[0][0] == "/config/setup/v1/variables"
        assert call_args[1]["json"]["name"] == "test_variable"

        # Assert the result is a VariableResponseModel
        assert isinstance(result, VariableResponseModel)
        assert result.name == str(mock_response.name)
        assert str(result.id) == str(mock_response.id)

    def test_create_variable_with_all_fields(self, variable_service, mock_scm_client):
        """Test creating a variable with all fields."""
        # Setup mock response
        mock_response = VariableResponseModelFactory.build()
        mock_scm_client.post.return_value = mock_response

        # Create the variable with all fields
        data = VariableCreateModelDictFactory.build_valid_dict(
            name="test_variable",
            type="fqdn",
            value="example.com",
            description="Test description",
            folder="test_folder",
        )
        result = variable_service.create(data=data)

        # Assert the client was called correctly
        mock_scm_client.post.assert_called_once()
        call_args = mock_scm_client.post.call_args
        assert call_args[0][0] == "/config/setup/v1/variables"
        payload = call_args[1]["json"]
        assert payload["name"] == "test_variable"
        assert payload["type"] == "fqdn"
        assert payload["value"] == "example.com"
        assert payload["description"] == "Test description"
        assert payload["folder"] == "test_folder"

        # Assert the result is a VariableResponseModel
        assert isinstance(result, VariableResponseModel)

    def test_create_variable_with_invalid_data(self, variable_service):
        """Test creating a variable with invalid data."""
        # Missing type
        with pytest.raises(ValidationError):
            data = VariableCreateModelDictFactory.build_valid_dict()
            data.pop("type")
            variable_service.create(data=data)

        # Missing value
        with pytest.raises(ValidationError):
            data = VariableCreateModelDictFactory.build_valid_dict()
            data.pop("value")
            variable_service.create(data=data)

        # Invalid type
        with pytest.raises(ValidationError):
            data = VariableCreateModelDictFactory.build_valid_dict(type="invalid_type")
            variable_service.create(data=data)


class TestVariableGet(TestVariableBase):
    """Tests for Variable.get method."""

    def test_get_variable(self, variable_service, mock_scm_client):
        """Test retrieving a variable by ID."""
        # Setup mock response
        mock_response = VariableResponseModelFactory.build()
        mock_scm_client.get.return_value = mock_response
        variable_id = "123e4567-e89b-12d3-a456-426614174000"

        # Get the variable
        result = variable_service.get(variable_id)

        # Assert the client was called correctly
        mock_scm_client.get.assert_called_once_with(f"/config/setup/v1/variables/{variable_id}")

        # Assert the result is a VariableResponseModel
        assert isinstance(result, VariableResponseModel)
        assert str(result.id) == str(mock_response.id)
        assert result.name == str(mock_response.name)

    def test_get_nonexistent_variable(self, variable_service, mock_scm_client):
        """Test retrieving a variable that doesn't exist."""
        # Setup mock client to raise APIError with 404 status
        error = APIError("Variable not found")
        error.http_status_code = 404
        mock_scm_client.get.side_effect = error
        variable_id = "nonexistent-id"

        # Try to get the nonexistent variable
        with pytest.raises(ObjectNotPresentError):
            variable_service.get(variable_id)

        # Assert the client was called correctly
        mock_scm_client.get.assert_called_once_with(f"/config/setup/v1/variables/{variable_id}")

    def test_get_with_general_error(self, variable_service, mock_scm_client):
        """Test get with a non-404 API error."""
        # Create a non-404 API error (e.g., 500 server error)
        error = APIError("Server error")
        error.http_status_code = 500
        mock_scm_client.get.side_effect = error

        # Test with a try-except to ensure the original error is re-raised
        try:
            variable_service.get("123")
            pytest.fail("Expected APIError was not raised")
        except APIError as e:
            # Verify we got the same error that was injected
            assert e is error
            assert e.http_status_code == 500
            assert "Server error" in e.message


class TestVariableList(TestVariableBase):
    """Tests for Variable.list method."""

    def test_list_variables(self, variable_service, mock_scm_client):
        """Test listing variables with default parameters."""
        # Setup mock response with valid variable data
        mock_variables = [
            VariableResponseModelFactory.build_valid_model().model_dump() for _ in range(3)
        ]
        mock_response = {"data": mock_variables}

        # Patch the API client's get method
        with patch.object(variable_service.api_client, "get", return_value=mock_response):
            results = variable_service.list()
            assert isinstance(results, list)
            assert len(results) == 3

    def test_list_variables_pagination(self, variable_service, mock_scm_client):
        """Test listing variables with pagination parameters."""
        # Setup two pages of response data
        page1 = {"data": [VariableResponseModelFactory.build().model_dump() for _ in range(5)]}
        page2 = {"data": [VariableResponseModelFactory.build().model_dump() for _ in range(3)]}

        # Mock the get method to return different responses for first and second calls
        mock_scm_client.get.side_effect = [page1, page2]

        # Set a low max_limit to force pagination
        variable_service.max_limit = 5

        # Call list and verify pagination works
        results = variable_service.list()

        # Verify expected results
        assert isinstance(results, list)
        assert len(results) == 8  # Combined total from both pages
        assert mock_scm_client.get.call_count == 2

        # Verify the second call had the correct offset
        second_call_args = mock_scm_client.get.call_args_list[1][1]
        assert second_call_args["params"]["offset"] == 5

    def test_list_empty_result(self, variable_service, mock_scm_client):
        """Test listing variables when no results are returned."""
        mock_response = {"data": []}
        with patch.object(variable_service.api_client, "get", return_value=mock_response):
            results = variable_service.list()
            assert isinstance(results, list)
            assert len(results) == 0

    def test_list_with_filters(self, variable_service, mock_scm_client):
        """Test listing variables with filters."""
        # Setup mock response
        mock_variables = [
            VariableResponseModelFactory.build_valid_model().model_dump() for _ in range(3)
        ]
        mock_response = {"data": mock_variables}

        # Patch the API client's get method
        mock_get = MagicMock(return_value=mock_response)
        variable_service.api_client.get = mock_get

        # Call list with a filter
        variable_service.list(type="fqdn")

        # Verify filter was passed to API call
        call_args = mock_get.call_args[1]
        assert "params" in call_args
        assert call_args["params"]["type"] == "fqdn"


class TestVariableUpdate(TestVariableBase):
    """Tests for Variable.update method."""

    def test_update_variable(self, variable_service, mock_scm_client):
        """Test updating a variable."""
        # Setup mock response
        variable_id = "123e4567-e89b-12d3-a456-426614174000"
        mock_response = VariableResponseModelFactory.build(id=variable_id)
        mock_scm_client.put.return_value = mock_response

        # Build update model
        update_model = VariableUpdateModelFactory.build_valid_model(
            id=variable_id, name="updated_name"
        )

        # Update the variable
        result = variable_service.update(update_model)

        # Assert the client was called correctly
        mock_scm_client.put.assert_called_once()
        call_args = mock_scm_client.put.call_args
        assert call_args[0][0] == f"/config/setup/v1/variables/{variable_id}"
        assert call_args[1]["json"]["name"] == "updated_name"

        # Assert the result is a VariableResponseModel
        assert isinstance(result, VariableResponseModel)
        assert result.name == mock_response.name

    def test_update_with_all_parameters(self, variable_service, mock_scm_client):
        """Test updating a variable with all parameters."""
        # Setup mock response
        variable_id = "123e4567-e89b-12d3-a456-426614174000"
        mock_response = VariableResponseModelFactory.build(id=variable_id)
        mock_scm_client.put.return_value = mock_response

        # Build update model with all fields
        update_model = VariableUpdateModelFactory.build_valid_model(
            id=variable_id,
            name="updated_name",
            description="Updated description",
            type="fqdn",
            value="updated.example.com",
            folder="updated_folder",
        )
        result = variable_service.update(update_model)

        # Assert the client was called correctly
        call_args = mock_scm_client.put.call_args
        payload = call_args[1]["json"]
        assert payload["name"] == "updated_name"
        assert payload["description"] == "Updated description"
        assert payload["type"] == "fqdn"
        assert payload["value"] == "updated.example.com"
        assert payload["folder"] == "updated_folder"

        # Assert the result is a VariableResponseModel
        assert isinstance(result, VariableResponseModel)

    def test_update_nonexistent_variable(self, variable_service, mock_scm_client):
        """Test updating a variable that doesn't exist."""
        # Setup mock client to raise APIError with 404 status
        error = APIError("Variable not found")
        error.http_status_code = 404
        mock_scm_client.put.side_effect = error
        variable_id = "99999999-9999-9999-9999-999999999999"

        update_model = VariableUpdateModelFactory.build_valid_model(
            id=variable_id, name="updated_name"
        )
        # Try to update the nonexistent variable
        with pytest.raises(APIError):
            variable_service.update(update_model)

    def test_update_with_general_error(self, variable_service, mock_scm_client):
        """Test update with a non-404 exception."""
        # Create a non-404 error
        error = APIError("General server error")
        error.http_status_code = 500
        mock_scm_client.put.side_effect = error

        update_model = VariableUpdateModelFactory.build_valid_model(
            id="f9069360-c6e6-469d-b8f7-7479e5fa6c22", name="updated_name"
        )
        # Should re-raise the error
        with pytest.raises(APIError):
            variable_service.update(update_model)


class TestVariableDelete(TestVariableBase):
    """Tests for Variable.delete method."""

    def test_delete_variable(self, variable_service, mock_scm_client):
        """Test deleting a variable."""
        # Setup mock client
        variable_id = "123e4567-e89b-12d3-a456-426614174000"

        # Delete the variable
        variable_service.delete(variable_id)

        # Assert the client was called correctly
        mock_scm_client.delete.assert_called_once_with(f"/config/setup/v1/variables/{variable_id}")

    def test_delete_nonexistent_variable(self, variable_service, mock_scm_client):
        """Test deleting a variable that doesn't exist."""
        # Setup mock client to raise APIError with 404 status
        error = APIError("Variable not found")
        error.http_status_code = 404
        mock_scm_client.delete.side_effect = error
        variable_id = "nonexistent-id"

        # Try to delete the nonexistent variable
        with pytest.raises(ObjectNotPresentError):
            variable_service.delete(variable_id)

        # Assert the client was called correctly
        mock_scm_client.delete.assert_called_once_with(f"/config/setup/v1/variables/{variable_id}")

    def test_delete_with_general_error(self, variable_service, mock_scm_client):
        """Test delete with a non-404 exception."""
        # Create a non-404 error
        error = APIError("General server error")
        error.http_status_code = 500
        mock_scm_client.delete.side_effect = error

        # Should re-raise the error
        with pytest.raises(APIError):
            variable_service.delete("123")


class TestVariableFetch(TestVariableBase):
    """Tests for Variable.fetch method."""

    def test_fetch_variable_by_name(self, variable_service):
        """Test fetching a variable by name and folder."""
        name = "test_variable"
        folder = "test_folder"
        # Create a mock variable response
        mock_variable = VariableResponseModelFactory.build_valid_model(name=name, folder=folder)

        # Mock the list method to return our test variable
        with patch.object(variable_service, "list", return_value=[mock_variable]):
            result = variable_service.fetch(name=name, folder=folder)

            # Assert correct variable is returned
            assert result is not None
            assert result.name == name
            assert result.folder == folder

    def test_fetch_nonexistent_variable(self, variable_service):
        """Test fetching a variable that doesn't exist."""
        folder = "test_folder"
        # Mock the list method to return empty list
        with patch.object(variable_service, "list", return_value=[]):
            result = variable_service.fetch(name="nonexistent", folder=folder)

            # Assert None is returned
            assert result is None

    def test_fetch_with_multiple_matches(self, variable_service):
        """Test fetch returns only the first match when multiple exist."""
        name = "duplicate_name"
        folder = "test_folder"
        # Create two mock variables with the same name
        var1 = VariableResponseModelFactory.build_valid_model(
            name=name, folder=folder, value="value1"
        )
        var2 = VariableResponseModelFactory.build_valid_model(
            name=name, folder=folder, value="value2"
        )

        # Mock the list method to return both variables
        with patch.object(variable_service, "list", return_value=[var1, var2]):
            result = variable_service.fetch(name=name, folder=folder)

            # Assert first matching variable is returned
            assert result is not None
            assert result.name == name
            assert result.value == "value1"  # Should be the first one

    def test_fetch_no_exact_match(self, variable_service):
        """Test fetch with no exact matches."""
        folder = "test_folder"
        # Create mock variables with different names
        var1 = VariableResponseModelFactory.build_valid_model(name="name1", folder=folder)
        var2 = VariableResponseModelFactory.build_valid_model(name="name2", folder=folder)

        # Mock the list method to return these variables
        with patch.object(variable_service, "list", return_value=[var1, var2]):
            result = variable_service.fetch(name="different_name", folder=folder)

            # Assert None is returned (no match)
            assert result is None

    def test_fetch_empty_name(self, variable_service):
        """Test fetch with empty name raises error."""
        folder = "test_folder"
        with pytest.raises(InvalidObjectError):
            variable_service.fetch(name="", folder=folder)

    def test_fetch_empty_folder(self, variable_service):
        """Test fetch with empty folder raises error."""
        name = "test_variable"
        with pytest.raises(InvalidObjectError):
            variable_service.fetch(name=name, folder="")


class TestVariableMaxLimitValidation(TestVariableBase):
    """Tests for max_limit validation in Variable class."""

    def test_validate_max_limit_none(self, variable_service):
        """Test validating None max_limit."""
        result = variable_service._validate_max_limit(None)
        assert result == Variable.DEFAULT_MAX_LIMIT

    def test_validate_max_limit_invalid_type(self, variable_service):
        """Test validating invalid type for max_limit."""
        with pytest.raises(InvalidObjectError):
            variable_service._validate_max_limit("not_an_int")

    def test_validate_max_limit_too_low(self, variable_service):
        """Test validating max_limit that is too low."""
        with pytest.raises(InvalidObjectError):
            variable_service._validate_max_limit(0)

    def test_validate_max_limit_too_high(self, variable_service):
        """Test validating max_limit that is too high."""
        # In Variable, this returns ABSOLUTE_MAX_LIMIT instead of raising an error
        result = variable_service._validate_max_limit(Variable.ABSOLUTE_MAX_LIMIT + 100)
        assert result == Variable.ABSOLUTE_MAX_LIMIT

    def test_max_limit_setter(self, variable_service):
        """Test setting max_limit property."""
        variable_service.max_limit = 500
        assert variable_service.max_limit == 500
        assert variable_service._max_limit == 500


class TestVariableGetPaginatedResults(TestVariableBase):
    """Tests for _get_paginated_results helper method."""

    def test_get_paginated_results_dict_with_data(self, variable_service, mock_scm_client):
        """Test _get_paginated_results with dict response containing 'data'."""
        # Setup mock response
        mock_response = {"data": [{"id": "1", "name": "test1"}, {"id": "2", "name": "test2"}]}
        mock_scm_client.get.return_value = mock_response

        # Call the method
        results = variable_service._get_paginated_results(
            endpoint="/test", params={}, limit=10, offset=0
        )

        # Assert correct data is extracted
        assert results == mock_response["data"]

    def test_get_paginated_results_list_response(self, variable_service, mock_scm_client):
        """Test _get_paginated_results with list response."""
        # Setup mock response
        mock_response = [{"id": "1", "name": "test1"}, {"id": "2", "name": "test2"}]
        mock_scm_client.get.return_value = mock_response

        # Call the method
        results = variable_service._get_paginated_results(
            endpoint="/test", params={}, limit=10, offset=0
        )

        # Assert the list is returned directly
        assert results == mock_response

    def test_get_paginated_results_unexpected_format(self, variable_service, mock_scm_client):
        """Test _get_paginated_results with unexpected response format."""
        # Setup mock response with unexpected format
        mock_scm_client.get.return_value = "not a dict or list"

        # Call the method
        results = variable_service._get_paginated_results(
            endpoint="/test", params={}, limit=10, offset=0
        )

        # Assert empty list is returned for unexpected format
        assert results == []


class TestVariableApplyFilters(TestVariableBase):
    """Tests for _apply_filters helper method."""

    def test_apply_no_filters(self, variable_service):
        """Test _apply_filters with no filters."""
        # Create test data
        variables = [VariableResponseModelFactory.build_valid_model() for _ in range(3)]

        # Apply no filters
        result = variable_service._apply_filters(variables, {})

        # Should return all variables unchanged
        assert result == variables

    def test_apply_labels_filter(self, variable_service):
        """Test _apply_filters with labels filter."""
        # Create test variables with different labels
        var1 = VariableResponseModelFactory.build_valid_model(labels=["label1", "label2"])
        var2 = VariableResponseModelFactory.build_valid_model(labels=["label3"])
        var3 = VariableResponseModelFactory.build_valid_model(labels=["label1", "label3"])

        variables = [var1, var2, var3]

        # Apply labels filter
        result = variable_service._apply_filters(variables, {"labels": ["label1"]})

        # Should return only variables with matching labels
        assert len(result) == 2
        assert var1 in result
        assert var2 not in result
        assert var3 in result

    def test_apply_parent_filter(self, variable_service):
        """Test _apply_filters with parent filter."""
        # Create test variables with different parent values
        var1 = VariableResponseModelFactory.build_valid_model(parent="parent1")
        var2 = VariableResponseModelFactory.build_valid_model(parent="parent2")
        var3 = VariableResponseModelFactory.build_valid_model(parent="parent1")

        variables = [var1, var2, var3]

        # Apply parent filter
        result = variable_service._apply_filters(variables, {"parent": "parent1"})

        # Should return only variables with matching parent
        assert len(result) == 2
        assert var1 in result
        assert var2 not in result
        assert var3 in result

    def test_apply_type_filter(self, variable_service):
        """Test _apply_filters with type filter."""
        # Create test variables with different types
        var1 = VariableResponseModelFactory.build_valid_model(type="fqdn")
        var2 = VariableResponseModelFactory.build_valid_model(type="ip-netmask")
        var3 = VariableResponseModelFactory.build_valid_model(type="fqdn")

        variables = [var1, var2, var3]

        # Apply type filter
        result = variable_service._apply_filters(variables, {"type": "fqdn"})

        # Should return only variables with matching type
        assert len(result) == 2
        assert var1 in result
        assert var2 not in result
        assert var3 in result

    def test_apply_snippets_filter(self, variable_service):
        """Test _apply_filters with snippets filter."""
        # Create test variables with different snippets
        var1 = VariableResponseModelFactory.build_valid_model(snippets=["snippet1", "snippet2"])
        var2 = VariableResponseModelFactory.build_valid_model(snippets=["snippet3"])
        var3 = VariableResponseModelFactory.build_valid_model(snippets=["snippet1", "snippet3"])

        variables = [var1, var2, var3]

        # Apply snippets filter
        result = variable_service._apply_filters(variables, {"snippets": ["snippet1"]})

        # Should return only variables with matching snippets
        assert len(result) == 2
        assert var1 in result
        assert var2 not in result
        assert var3 in result

    def test_apply_model_filter(self, variable_service):
        """Test _apply_filters with model filter."""
        # Create test variables with different models
        var1 = VariableResponseModelFactory.build_valid_model(model="model1")
        var2 = VariableResponseModelFactory.build_valid_model(model="model2")
        var3 = VariableResponseModelFactory.build_valid_model(model="model1")

        variables = [var1, var2, var3]

        # Apply model filter
        result = variable_service._apply_filters(variables, {"model": "model1"})

        # Should return only variables with matching model
        assert len(result) == 2
        assert var1 in result
        assert var2 not in result
        assert var3 in result

    def test_apply_serial_number_filter(self, variable_service):
        """Test _apply_filters with serial_number filter."""
        # Create test variables with different serial_numbers
        var1 = VariableResponseModelFactory.build_valid_model(serial_number="sn1")
        var2 = VariableResponseModelFactory.build_valid_model(serial_number="sn2")
        var3 = VariableResponseModelFactory.build_valid_model(serial_number="sn1")

        variables = [var1, var2, var3]

        # Apply serial_number filter
        result = variable_service._apply_filters(variables, {"serial_number": "sn1"})

        # Should return only variables with matching serial_number
        assert len(result) == 2
        assert var1 in result
        assert var2 not in result
        assert var3 in result

    def test_apply_device_only_filter(self, variable_service):
        """Test _apply_filters with device_only filter."""
        # Create test variables with different device_only values
        var1 = VariableResponseModelFactory.build_valid_model(device_only=True)
        var2 = VariableResponseModelFactory.build_valid_model(device_only=False)
        var3 = VariableResponseModelFactory.build_valid_model(device_only=True)

        variables = [var1, var2, var3]

        # Apply device_only filter
        result = variable_service._apply_filters(variables, {"device_only": True})

        # Should return only variables with matching device_only
        assert len(result) == 2
        assert var1 in result
        assert var2 not in result
        assert var3 in result

    def test_apply_multiple_filters(self, variable_service):
        """Test _apply_filters with multiple filters."""
        # Create test variables with different combinations of attributes
        var1 = VariableResponseModelFactory.build_valid_model(
            type="fqdn", model="model1", device_only=True
        )
        var2 = VariableResponseModelFactory.build_valid_model(
            type="ip-netmask", model="model1", device_only=True
        )
        var3 = VariableResponseModelFactory.build_valid_model(
            type="fqdn", model="model2", device_only=True
        )
        var4 = VariableResponseModelFactory.build_valid_model(
            type="fqdn", model="model1", device_only=False
        )

        variables = [var1, var2, var3, var4]

        # Apply multiple filters
        result = variable_service._apply_filters(
            variables, {"type": "fqdn", "model": "model1", "device_only": True}
        )

        # Should return only var1 which matches all filters
        assert len(result) == 1
        assert var1 in result
        assert var2 not in result  # Doesn't match type
        assert var3 not in result  # Doesn't match model
        assert var4 not in result  # Doesn't match device_only

    def test_filter_with_missing_attribute(self, variable_service):
        """Test filtering when variables don't have the filtered attribute."""
        # Create variables without the filtered attributes
        var1 = VariableResponseModelFactory.build_valid_model()
        var2 = VariableResponseModelFactory.build_valid_model()

        variables = [var1, var2]

        # Try filtering by attributes that don't exist on the variables
        result = variable_service._apply_filters(variables, {"labels": ["label1"]})

        # Should not match any variables since they don't have labels attribute
        assert len(result) == 0
