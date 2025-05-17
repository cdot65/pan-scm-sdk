# tests/scm/models/setup/test_variable.py

"""Tests for variable setup models."""

# Standard library imports
from uuid import UUID

import pytest

# Local SDK imports
from scm.models.setup.variable import (
    VariableBaseModel,
    VariableCreateModel,
    VariableResponseModel,
    VariableUpdateModel,
)
from tests.factories.setup.variable import (
    VariableCreateModelFactory,
    VariableResponseModelFactory,
    VariableUpdateModelFactory,
)


class TestVariableBaseModel:
    """Tests for the VariableBaseModel."""

    def test_valid_construction(self):
        """Test that a valid VariableBaseModel can be constructed."""
        model_instance = VariableCreateModelFactory.build_valid_model()
        data = model_instance.model_dump()
        model = VariableBaseModel(**data)

        assert model.name == data["name"]
        assert model.type == data["type"]
        assert model.value == data["value"]
        assert model.description == data["description"]
        assert model.folder == data["folder"]

    def test_minimal_construction(self):
        """Test that a minimal VariableBaseModel can be constructed."""
        data = {
            "name": "minimal_variable",
            "type": "ip-netmask",
            "value": "192.168.1.0/24",
            "folder": "test_folder",
        }

        model = VariableBaseModel(**data)

        assert model.name == "minimal_variable"
        assert model.type == "ip-netmask"
        assert model.value == "192.168.1.0/24"
        assert model.folder == "test_folder"
        assert model.description is None
        assert model.snippet is None
        assert model.device is None

    def test_type_validation(self):
        """Test that type is validated."""
        # Valid type should pass
        valid_model = VariableBaseModel(
            name="valid_name", type="ip-netmask", value="192.168.1.0/24", folder="test_folder"
        )
        assert valid_model.type == "ip-netmask"

        # Invalid type should fail
        with pytest.raises(ValueError):
            VariableBaseModel(
                name="invalid_type", type="invalid_type", value="test", folder="test_folder"
            )

    def test_container_validation(self):
        """Test container validation."""
        # Valid: one container field
        model1 = VariableBaseModel(
            name="test1", type="ip-netmask", value="192.168.1.0/24", folder="folder1"
        )
        assert model1.folder == "folder1"

        model2 = VariableBaseModel(
            name="test2", type="ip-netmask", value="192.168.1.0/24", snippet="snippet1"
        )
        assert model2.snippet == "snippet1"

        model3 = VariableBaseModel(
            name="test3", type="ip-netmask", value="192.168.1.0/24", device="device1"
        )
        assert model3.device == "device1"


class TestVariableCreateModel:
    """Tests for the VariableCreateModel."""

    def test_valid_construction(self):
        """Test that a valid VariableCreateModel can be constructed."""
        model_instance = VariableCreateModelFactory.build_valid_model()
        data = model_instance.model_dump()
        model = VariableCreateModel(**data)

        assert model.name == data["name"]
        assert model.type == data["type"]
        assert model.value == data["value"]
        assert model.description == data["description"]
        assert model.folder == data["folder"]

    def test_required_fields(self):
        """Test that VariableCreateModel requires name, type, value, and one container field."""
        # Missing name
        with pytest.raises(ValueError):
            VariableCreateModel(type="ip-netmask", value="192.168.1.0/24", folder="test")

        # Missing type
        with pytest.raises(ValueError):
            VariableCreateModel(name="test", value="192.168.1.0/24", folder="test")

        # Missing value
        with pytest.raises(ValueError):
            VariableCreateModel(name="test", type="ip-netmask", folder="test")


class TestVariableUpdateModel:
    """Tests for the VariableUpdateModel."""

    def test_valid_construction(self):
        """Test that a valid VariableUpdateModel can be constructed."""
        model_instance = VariableUpdateModelFactory.build_valid_model()
        data = model_instance.model_dump()
        model = VariableUpdateModel(**data)

        assert model.id == data["id"]
        assert model.name == data["name"]
        assert model.type == data["type"]
        assert model.value == data["value"]
        assert model.description == data["description"]
        assert model.folder == data["folder"]

    def test_required_fields(self):
        """Test that VariableUpdateModel requires id."""
        with pytest.raises(ValueError):
            # Missing id should fail validation
            VariableUpdateModel(
                name="test_variable", type="ip-netmask", value="192.168.1.0/24", folder="test"
            )

    def test_id_type_conversion(self):
        """Test that id is properly converted to UUID."""
        model_instance = VariableUpdateModelFactory.build_valid_model()
        data = model_instance.model_dump()
        model = VariableUpdateModel(**data)

        # Verify the id was converted to UUID
        assert isinstance(model.id, UUID)
        assert model.id == data["id"]


class TestVariableResponseModel:
    """Tests for the VariableResponseModel."""

    def test_valid_construction(self):
        """Test that a valid VariableResponseModel can be constructed."""
        data = VariableResponseModelFactory.build()

        model = VariableResponseModel(**data.model_dump())

        assert str(model.id) == str(data.id)
        assert model.name == data.name
        assert model.type == data.type
        assert model.value == data.value
        assert model.description == data.description
        assert hasattr(model, "overridden")

    def test_id_type_conversion(self):
        """Test that id is properly converted to UUID."""
        data = VariableResponseModelFactory.build()
        id_str = data.id  # Save original string representation

        model = VariableResponseModel(**data.model_dump())

        # Verify the id was converted to UUID
        assert isinstance(model.id, UUID)
        assert str(model.id) == str(id_str)

    def test_from_request_model(self):
        """Test creating a response model from a request model."""
        create_model = VariableCreateModelFactory.build_valid_model()
        response_model = VariableResponseModelFactory.from_request_model(create_model)

        assert isinstance(response_model, VariableResponseModel)
        assert response_model.name == create_model.name
        assert response_model.type == create_model.type
        assert response_model.value == create_model.value
        if create_model.description:
            assert response_model.description == create_model.description

    def test_variable_type_values(self):
        """Test different valid type values."""
        valid_types = [
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
        ]

        for valid_type in valid_types:
            model = VariableResponseModelFactory.build(type=valid_type)
            assert model.type == valid_type
