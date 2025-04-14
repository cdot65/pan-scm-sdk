# tests/scm/models/objects/test_address_group.py

# External libraries
from pydantic import ValidationError
import pytest

# Local SDK imports
from scm.models.objects import AddressGroupCreateModel, AddressGroupUpdateModel
from scm.models.objects.address_group import DynamicFilter
from tests.test_factories import (
    AddressGroupCreateModelFactory,
    AddressGroupUpdateModelFactory,
)

# -------------------- Test Classes for Pydantic Models --------------------


class TestAddressGroupCreateModel:
    """Tests for AddressGroupCreateModel validation."""

    def test_address_group_create_model_no_type_provided(self):
        """Test validation when no group type (static or dynamic) is provided."""
        data = AddressGroupCreateModelFactory.build_without_type()
        with pytest.raises(ValidationError) as exc_info:
            AddressGroupCreateModel(**data)
        assert "1 validation error for AddressGroupCreateModel" in str(exc_info.value)
        assert "Exactly one of 'static' or 'dynamic' must be provided." in str(exc_info.value)

    def test_address_group_create_model_multiple_types_provided(self):
        """Test validation when both static and dynamic group types are provided."""
        data = AddressGroupCreateModelFactory.build_with_multiple_types()
        with pytest.raises(ValidationError) as exc_info:
            AddressGroupCreateModel(**data)
        assert "1 validation error for AddressGroupCreateModel" in str(exc_info.value)
        assert "Exactly one of 'static' or 'dynamic' must be provided." in str(exc_info.value)

    def test_address_group_create_model_invalid_data_error(self):
        """Test that ValidationError is raised when invalid data is provided."""
        data = {"invalid_field": "test"}
        with pytest.raises(ValidationError) as exc_info:
            AddressGroupCreateModel(**data)
        error_msg = str(exc_info.value)
        assert "1 validation error for AddressGroupCreateModel" in error_msg
        assert "name\n  Field required" in error_msg  # Name is required
        assert "{'invalid_field': 'test'}" in error_msg  # Group type required

    def test_address_group_create_model_multiple_containers_provided(self):
        """Test validation when multiple containers are provided."""
        data = AddressGroupCreateModelFactory.build_with_multiple_containers()
        with pytest.raises(ValidationError) as exc_info:
            AddressGroupCreateModel(**data)
        assert "1 validation error for AddressGroupCreateModel" in str(exc_info.value)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_address_group_create_model_missing_required_fields_error(self):
        """Test validation when required fields are missing."""
        data = {"static": ["address1", "address2"], "folder": "Texas"}
        with pytest.raises(ValidationError) as exc_info:
            AddressGroupCreateModel(**data)
        error_msg = str(exc_info.value)
        assert "1 validation error for AddressGroupCreateModel" in error_msg
        assert "name\n  Field required" in error_msg  # Name is required

    def test_address_group_create_model_valid_static(self):
        """Test validation with valid data for a static address group."""
        data = AddressGroupCreateModelFactory.build_valid_static()
        model = AddressGroupCreateModel(**data)
        assert model.name == data["name"]
        assert model.folder == data["folder"]
        assert model.static == data["static"]
        assert model.tag == data["tag"]
        assert model.description == data["description"]

    def test_address_group_create_model_valid_dynamic(self):
        """Test validation with valid data for a dynamic address group."""
        data = AddressGroupCreateModelFactory.build_valid_dynamic()
        model = AddressGroupCreateModel(**data)
        assert model.name == data["name"]
        assert model.folder == data["folder"]
        assert model.dynamic == DynamicFilter(**data["dynamic"])
        assert model.tag == data["tag"]
        assert model.description == data["description"]

    def test_tag_field_accepts_string(self):
        """Test that the 'tag' field accepts a single string and converts it to a list."""
        data = AddressGroupCreateModelFactory.build_valid_static()
        data["tag"] = "TestTag"
        model = AddressGroupCreateModel(**data)
        assert model.tag == ["TestTag"]

    def test_tag_field_accepts_list(self):
        """Test that the 'tag' field accepts a list of strings."""
        data = AddressGroupCreateModelFactory.build_valid_static()
        data["tag"] = ["Tag1", "Tag2"]
        model = AddressGroupCreateModel(**data)
        assert model.tag == ["Tag1", "Tag2"]

    def test_tag_field_rejects_invalid_type(self):
        """Test that the 'tag' field rejects invalid types."""
        data = AddressGroupCreateModelFactory.build_valid_static()
        data["tag"] = {"invalid": "type"}
        with pytest.raises(ValidationError) as exc_info:
            AddressGroupCreateModel(**data)
        assert "Tag must be a string or a list of strings" in str(exc_info.value)

    def test_tag_field_rejects_duplicate_items(self):
        """Test that the 'tag' field rejects duplicate items."""
        data = AddressGroupCreateModelFactory.build_valid_static()
        data["tag"] = ["TestTag", "TestTag"]
        with pytest.raises(ValidationError) as exc_info:
            AddressGroupCreateModel(**data)
        assert "List items must be unique" in str(exc_info.value)


class TestAddressGroupUpdateModel:
    """Tests for AddressGroupUpdateModel validation."""

    def test_address_group_update_model_invalid_data_error(self):
        """Test that ValidationError is raised when invalid data is provided."""
        data = {"invalid": "data"}
        with pytest.raises(ValidationError) as exc_info:
            AddressGroupUpdateModel(**data)
        error_msg = str(exc_info.value)
        assert (
            "2 validation errors for AddressGroupUpdateModel\nname\n  Field required [type=missing, input_value={'invalid': 'data'}, input_type=dict]"
            in error_msg
        )

    def test_address_group_update_model_multiple_types_provided(self):
        """Test validation when both static and dynamic group types are provided."""
        data = AddressGroupUpdateModelFactory.build_with_multiple_types()
        with pytest.raises(ValidationError) as exc_info:
            AddressGroupUpdateModel(**data)
        assert "1 validation error for AddressGroupUpdateModel" in str(exc_info.value)
        assert "Exactly one of 'static' or 'dynamic' must be provided." in str(exc_info.value)

    def test_address_group_update_model_valid_static(self):
        """Test validation with valid data for updating a static address group."""
        data = AddressGroupUpdateModelFactory.build_valid_static()
        model = AddressGroupUpdateModel(**data)
        assert model.name == data["name"]
        assert model.static == data["static"]
        assert model.tag == data["tag"]
        assert model.description == data["description"]

    def test_address_group_update_model_valid_dynamic(self):
        """Test validation with valid data for updating a dynamic address group."""
        data = AddressGroupUpdateModelFactory.build_valid_dynamic()
        model = AddressGroupUpdateModel(**data)
        assert model.name == data["name"]
        assert model.dynamic == DynamicFilter(**data["dynamic"])
        assert model.tag == data["tag"]
        assert model.description == data["description"]

    def test_tag_field_accepts_string(self):
        """Test that the 'tag' field accepts a single string and converts it to a list."""
        data = AddressGroupUpdateModelFactory.build_valid_static()
        data["tag"] = "TestTag"
        model = AddressGroupUpdateModel(**data)
        assert model.tag == ["TestTag"]

    def test_tag_field_accepts_list(self):
        """Test that the 'tag' field accepts a list of strings."""
        data = AddressGroupUpdateModelFactory.build_valid_static()
        data["tag"] = ["Tag1", "Tag2"]
        model = AddressGroupUpdateModel(**data)
        assert model.tag == ["Tag1", "Tag2"]

    def test_tag_field_rejects_invalid_type(self):
        """Test that the 'tag' field rejects invalid types."""
        data = AddressGroupUpdateModelFactory.build_valid_static()
        data["tag"] = {"invalid": "type"}
        with pytest.raises(ValidationError) as exc_info:
            AddressGroupUpdateModel(**data)
        assert "Tag must be a string or a list of strings" in str(exc_info.value)

    def test_tag_field_rejects_duplicate_items(self):
        """Test that the 'tag' field rejects duplicate items."""
        data = AddressGroupUpdateModelFactory.build_valid_static()
        data["tag"] = ["TestTag", "TestTag"]
        with pytest.raises(ValidationError) as exc_info:
            AddressGroupUpdateModel(**data)
        assert "List items must be unique" in str(exc_info.value)

    def test_address_group_update_model_missing_group_type(self):
        """Test validation when group type is missing in update model."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-address-group",
            "folder": "Texas",
        }
        with pytest.raises(ValidationError) as exc_info:
            AddressGroupUpdateModel(**data)
        error_msg = str(exc_info.value)
        assert "1 validation error for AddressGroupUpdateModel" in error_msg
        assert "Exactly one of 'static' or 'dynamic' must be provided." in error_msg


# -------------------- End of Test Classes --------------------
