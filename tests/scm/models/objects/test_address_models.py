# tests/scm/config/objects/test_address.py

# Standard library imports

# External libraries
import pytest
from pydantic import ValidationError as PydanticValidationError

# Local SDK imports
from scm.models.objects import (
    AddressCreateModel,
)
from tests.factories import AddressCreateDataFactory


# -------------------- Test Classes for Pydantic Models --------------------


class TestAddressModelValidation:
    """Tests for object model validation."""

    def test_object_model_no_type_provided(self):
        """Test validation when no type is provided."""
        data = AddressCreateDataFactory.build_without_type()
        with pytest.raises(PydanticValidationError) as exc_info:
            AddressCreateModel(**data)
        assert "1 validation error for AddressCreateModel" in str(exc_info.value)
        assert (
            "Value error, Exactly one of 'ip_netmask', 'ip_range', 'ip_wildcard', or 'fqdn' must be provided."
            in str(exc_info.value)
        )

    def test_object_model_multiple_types(self):
        """Test validation when multiple types are provided."""
        data = AddressCreateDataFactory.build_with_multiple_types()
        with pytest.raises(PydanticValidationError) as exc_info:
            AddressCreateModel(**data)
        assert (
            "Exactly one of 'ip_netmask', 'ip_range', 'ip_wildcard', or 'fqdn' must be provided."
            in str(exc_info.value)
        )

    def test_object_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = AddressCreateDataFactory.build_with_multiple_containers()
        with pytest.raises(ValueError) as exc_info:
            AddressCreateModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_object_model_no_container_provided(self):
        """Test validation when no container is provided."""
        data = AddressCreateDataFactory.build_with_multiple_containers()

        with pytest.raises(ValueError) as exc_info:
            AddressCreateModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_object_model_create_model_valid(self):
        """Test validation with valid data."""
        data = AddressCreateDataFactory.build_valid()
        model = AddressCreateModel(**data)
        assert model.name == data["name"]
        assert model.folder == data["folder"]
        assert model.ip_netmask == data["ip_netmask"]
        assert model.tag == data["tag"]
        assert model.description == data["description"]


# -------------------- End of Test Classes --------------------
