# tests/scm/models/setup/test_label.py

# Standard library imports
from uuid import UUID

import pytest

# Local SDK imports
from scm.models.setup.label import (
    LabelBaseModel,
    LabelCreateModel,
    LabelResponseModel,
    LabelUpdateModel,
)
from tests.factories.setup.label import (
    LabelCreateModelFactory,
    LabelResponseModelFactory,
    LabelUpdateModelFactory,
)


class TestLabelBaseModel:
    """Tests for the LabelBaseModel."""

    def test_valid_construction(self):
        """Test that a valid LabelBaseModel can be constructed."""
        model_instance = LabelCreateModelFactory.build_valid_model()
        data = model_instance.model_dump()
        model = LabelBaseModel(**data)

        assert model.name == data["name"]
        assert model.type == data["type"]
        assert model.value == data["value"]
        assert model.description == data["description"]
        assert model.folder == data["folder"]

    def test_minimal_construction(self):
        """Test that a minimal LabelBaseModel can be constructed."""
        data = {
            "name": "minimal_label",
            "type": "ip-netmask",
            "value": "192.168.1.0/24",
            "folder": "test_folder",
        }

        model = LabelBaseModel(**data)

        assert model.name == "minimal_label"
        assert model.type == "ip-netmask"
        assert model.value == "192.168.1.0/24"
        assert model.folder == "test_folder"
        assert model.description is None
        assert model.snippet is None
        assert model.device is None

    def test_type_validation(self):
        """Test that type is validated."""
        # Valid type should pass
        valid_model = LabelBaseModel(
            name="valid_name",
            type="ip-netmask",
            value="192.168.1.0/24",
            folder="test_folder",
        )
        assert valid_model.type == "ip-netmask"

        # Invalid type should fail
        with pytest.raises(ValueError):
            LabelBaseModel(
                name="invalid_type",
                type="invalid_type",
                value="test",
                folder="test_folder",
            )

    def test_container_validation(self):
        """Test container validation."""
        # Valid: one container field
        model1 = LabelBaseModel(
            name="test1", type="ip-netmask", value="192.168.1.0/24", folder="folder1"
        )
        assert model1.folder == "folder1"

        model2 = LabelBaseModel(
            name="test2", type="ip-netmask", value="192.168.1.0/24", snippet="snippet1"
        )
        assert model2.snippet == "snippet1"

        model3 = LabelBaseModel(
            name="test3", type="ip-netmask", value="192.168.1.0/24", device="device1"
        )
        assert model3.device == "device1"


class TestLabelCreateModel:
    """Tests for the LabelCreateModel."""

    def test_valid_construction(self):
        """Test that a valid LabelCreateModel can be constructed."""
        model_instance = LabelCreateModelFactory.build_valid_model()
        data = model_instance.model_dump()
        model = LabelCreateModel(**data)

        assert model.name == data["name"]
        assert model.type == data["type"]
        assert model.value == data["value"]
        assert model.description == data["description"]
        assert model.folder == data["folder"]

    def test_required_fields(self):
        """Test that LabelCreateModel requires name, type, value, and one container field."""
        # Missing name
        with pytest.raises(ValueError):
            LabelCreateModel(type="ip-netmask", value="192.168.1.0/24", folder="test")

        # Missing type
        with pytest.raises(ValueError):
            LabelCreateModel(name="test", value="192.168.1.0/24", folder="test")

        # Missing value
        with pytest.raises(ValueError):
            LabelCreateModel(name="test", type="ip-netmask", folder="test")


class TestLabelUpdateModel:
    """Tests for the LabelUpdateModel."""

    def test_valid_construction(self):
        """Test that a valid LabelUpdateModel can be constructed."""
        model_instance = LabelUpdateModelFactory.build_valid_model()
        data = model_instance.model_dump()
        model = LabelUpdateModel(**data)

        assert model.id == data["id"]
        assert model.name == data["name"]
        assert model.type == data["type"]
        assert model.value == data["value"]
        assert model.description == data["description"]
        assert model.folder == data["folder"]

    def test_required_fields(self):
        """Test that LabelUpdateModel requires id."""
        with pytest.raises(ValueError):
            # Missing id should fail validation
            LabelUpdateModel(
                name="test_label",
                type="ip-netmask",
                value="192.168.1.0/24",
                folder="test",
            )

    def test_id_type_conversion(self):
        """Test that id is properly converted to UUID."""
        model_instance = LabelUpdateModelFactory.build_valid_model()
        data = model_instance.model_dump()
        model = LabelUpdateModel(**data)

        # Verify the id was converted to UUID
        assert isinstance(model.id, UUID)
        assert model.id == data["id"]


class TestLabelResponseModel:
    """Tests for the LabelResponseModel."""

    def test_valid_construction(self):
        """Test that a valid LabelResponseModel can be constructed."""
        data = LabelResponseModelFactory.build()

        model = LabelResponseModel(**data.model_dump())

        assert str(model.id) == str(data.id)
        assert model.name == data.name
        assert model.type == data.type
        assert model.value == data.value
        assert model.description == data.description
        assert hasattr(model, "overridden")

    def test_id_type_conversion(self):
        """Test that id is properly converted to UUID."""
        data = LabelResponseModelFactory.build()
        id_str = data.id  # Save original string representation

        model = LabelResponseModel(**data.model_dump())

        # Verify the id was converted to UUID
        assert isinstance(model.id, UUID)
        assert str(model.id) == str(id_str)

    def test_from_request_model(self):
        """Test creating a response model from a request model."""
        create_model = LabelCreateModelFactory.build_valid_model()
        response_model = LabelResponseModelFactory.from_request_model(create_model)

        assert isinstance(response_model, LabelResponseModel)
        assert response_model.name == create_model.name
        assert response_model.type == create_model.type
        assert response_model.value == create_model.value
        if create_model.description:
            assert response_model.description == create_model.description

    def test_label_type_values(self):
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
            model = LabelResponseModelFactory.build(type=valid_type)
            assert model.type == valid_type
