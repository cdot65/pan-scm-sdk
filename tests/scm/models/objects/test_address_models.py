# tests/scm/models/objects/test_address.py

# External libraries
from pydantic import ValidationError
import pytest

# Local SDK imports
from scm.models.objects import AddressCreateModel, AddressUpdateModel
from tests.test_factories import AddressCreateModelFactory, AddressUpdateModelFactory

# -------------------- Test Classes for Pydantic Models --------------------


class TestAddressCreateModel:
    """Tests for object model validation."""

    def test_address_create_model_no_type_provided(self):
        """Test validation when no address type is provided."""
        data = AddressCreateModelFactory.build_without_type()
        with pytest.raises(ValidationError) as exc_info:
            AddressCreateModel(**data)
        assert "1 validation error for AddressCreateModel" in str(exc_info.value)
        assert (
            "Exactly one of 'ip_netmask', 'ip_range', 'ip_wildcard', or 'fqdn' must be provided."
            in str(exc_info.value)
        )

    def test_address_create_model_multiple_types_provided(self):
        """Test validation when multiple address types are provided."""
        data = AddressCreateModelFactory.build_with_multiple_types()
        with pytest.raises(ValidationError) as exc_info:
            AddressCreateModel(**data)
        assert (
            "Exactly one of 'ip_netmask', 'ip_range', 'ip_wildcard', or 'fqdn' must be provided."
            in str(exc_info.value)
        )

    def test_address_create_model_invalid_data_error(self):
        """Test that ValidationError is raised when invalid data is provided."""
        data = {"invalid_field": "test"}
        with pytest.raises(ValidationError) as exc_info:
            AddressCreateModel(**data)
        error_msg = str(exc_info.value)
        assert "1 validation error for AddressCreateModel" in error_msg
        assert "name\n  Field required" in error_msg  # Name is required

    def test_address_create_model_multiple_containers_provided(self):
        """Test validation when multiple containers are provided."""
        data = AddressCreateModelFactory.build_with_multiple_containers()
        with pytest.raises(ValueError) as exc_info:
            AddressCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_address_create_model_missing_required_fields_error(self):
        """Test validation when required fields are missing."""
        data = {"name": "test"}
        with pytest.raises(ValidationError) as exc_info:
            AddressCreateModel(**data)
        error_msg = str(exc_info.value)
        assert "1 validation error for AddressCreateModel" in error_msg
        assert (
            "Exactly one of 'ip_netmask', 'ip_range', 'ip_wildcard', or 'fqdn' must be provided."
            in error_msg
        )

    def test_address_create_model_missing_address_type(self):
        """Test validation when required address type is missing."""
        data = {"name": "test", "folder": "Texas"}
        with pytest.raises(ValidationError) as exc_info:
            AddressCreateModel(**data)
        assert "1 validation error for AddressCreateModel" in str(exc_info.value)
        assert (
            "Exactly one of 'ip_netmask', 'ip_range', 'ip_wildcard', or 'fqdn' must be provided."
            in str(exc_info.value)
        )

    def test_address_create_model_valid(self):
        """Test validation with valid data."""
        data = AddressCreateModelFactory.build_valid()
        model = AddressCreateModel(**data)
        assert model.name == data["name"]
        assert model.folder == data["folder"]
        assert model.ip_netmask == data["ip_netmask"]
        assert model.tag == data["tag"]
        assert model.description == data["description"]

    def test_tag_field_accepts_string(self):
        """Test that the 'tag' field accepts a single string and converts it to a list."""
        data = AddressCreateModelFactory.build_valid()
        data["tag"] = "TestTag"
        model = AddressCreateModel(**data)
        assert model.tag == ["TestTag"]

    def test_tag_field_accepts_list(self):
        """Test that the 'tag' field accepts a list of strings."""
        data = AddressCreateModelFactory.build_valid()
        data["tag"] = ["Tag1", "Tag2"]
        model = AddressCreateModel(**data)
        assert model.tag == ["Tag1", "Tag2"]

    def test_tag_field_rejects_invalid_type(self):
        """Test that the 'tag' field rejects invalid types."""
        data = AddressCreateModelFactory.build_valid()
        data["tag"] = {"invalid": "type"}
        with pytest.raises(ValidationError) as exc_info:
            AddressCreateModel(**data)
        assert "Tag must be a string or a list of strings" in str(exc_info.value)

    def test_tag_field_rejects_duplicate_items(self):
        """Test that the 'tag' field rejects duplicate items."""
        data = AddressCreateModelFactory.build_valid()
        data["tag"] = ["TestTag", "TestTag"]
        with pytest.raises(ValidationError) as exc_info:
            AddressCreateModel(**data)
        assert "List items must be unique" in str(exc_info.value)


class TestAddressUpdateModel:
    def test_address_update_model_invalid_data_error(self):
        """Test that ValidationError is raised when invalid data is provided."""
        data = {"invalid": "data"}
        with pytest.raises(ValidationError) as exc_info:
            AddressUpdateModel(**data)
        error_msg = str(exc_info.value)
        assert "validation error" in error_msg
        assert "name\n  Field required" in error_msg
        assert "id\n  Field required" in error_msg

    def test_address_update_model_missing_id(self):
        """Test validation when 'id' field is missing."""
        data = AddressCreateModelFactory.build_valid()
        with pytest.raises(ValidationError) as exc_info:
            AddressUpdateModel(**data)
        assert "id\n  Field required" in str(exc_info.value)

    def test_address_update_model_missing_address_type(self):
        """Test validation when required address type is missing."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-address",
            "folder": "Texas",
        }
        with pytest.raises(ValidationError) as exc_info:
            AddressUpdateModel(**data)
        error_msg = str(exc_info.value)
        assert "1 validation error for AddressUpdateModel" in error_msg
        assert (
            "Exactly one of 'ip_netmask', 'ip_range', 'ip_wildcard', or 'fqdn' must be provided"
            in error_msg
        )

    def test_address_update_model_missing_required_fields(self):
        """Test validation when required fields are missing in update model."""
        data = {"name": "test"}
        with pytest.raises(ValidationError) as exc_info:
            AddressUpdateModel(**data)
        error_msg = str(exc_info.value)
        assert "1 validation error for AddressUpdateModel\nid\n  Field required" in error_msg

    def test_address_update_model_valid(self):
        """Test validation with valid data in update model."""
        data = AddressUpdateModelFactory.build_valid()
        model = AddressUpdateModel(**data)
        assert model.name == data["name"]
        assert model.folder == data["folder"]
        assert model.ip_netmask == data["ip_netmask"]

    def test_tag_field_accepts_string(self):
        """Test that the 'tag' field accepts a single string and converts it to a list."""
        data = AddressUpdateModelFactory.build_valid()
        data["tag"] = "TestTag"
        model = AddressUpdateModel(**data)
        assert model.tag == ["TestTag"]

    def test_tag_field_accepts_list(self):
        """Test that the 'tag' field accepts a list of strings."""
        data = AddressUpdateModelFactory.build_valid()
        data["tag"] = ["Tag1", "Tag2"]
        model = AddressUpdateModel(**data)
        assert model.tag == ["Tag1", "Tag2"]

    def test_tag_field_rejects_invalid_type(self):
        """Test that the 'tag' field rejects invalid types."""
        data = AddressUpdateModelFactory.build_valid()
        data["tag"] = {"invalid": "type"}
        with pytest.raises(ValidationError) as exc_info:
            AddressUpdateModel(**data)
        assert "Tag must be a string or a list of strings" in str(exc_info.value)

    def test_tag_field_rejects_duplicate_items(self):
        """Test that the 'tag' field rejects duplicate items."""
        data = AddressUpdateModelFactory.build_valid()
        data["tag"] = ["TestTag", "TestTag"]
        with pytest.raises(ValidationError) as exc_info:
            AddressUpdateModel(**data)
        assert "List items must be unique" in str(exc_info.value)


# -------------------- End of Test Classes --------------------
