# tests/scm/models/setup/test_label.py

"""Tests for label setup models."""

# Standard library imports
from uuid import UUID

from pydantic import ValidationError
import pytest

# Local SDK imports
from scm.models.setup.label import (
    LabelBaseModel,
    LabelCreateModel,
    LabelResponseModel,
    LabelUpdateModel,
)


class TestLabelBaseModel:
    """Tests for the LabelBaseModel."""

    def test_valid_construction(self):
        """Test that a valid LabelBaseModel can be constructed."""
        data = {"name": "test_label", "description": "This is a test label"}
        model = LabelBaseModel(**data)

        assert model.name == "test_label"
        assert model.description == "This is a test label"

    def test_minimal_construction(self):
        """Test that a minimal LabelBaseModel can be constructed."""
        data = {
            "name": "minimal_label",
        }

        model = LabelBaseModel(**data)

        assert model.name == "minimal_label"
        assert model.description is None

    def test_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        data = {"name": "test_label", "unknown_field": "should_fail"}
        with pytest.raises(ValidationError) as exc_info:
            LabelBaseModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestLabelCreateModel:
    """Tests for the LabelCreateModel."""

    def test_valid_construction(self):
        """Test that a valid LabelCreateModel can be constructed."""
        data = {"name": "create_test_label", "description": "This is a test create label"}
        model = LabelCreateModel(**data)

        assert model.name == "create_test_label"
        assert model.description == "This is a test create label"

    def test_required_fields(self):
        """Test that LabelCreateModel requires name."""
        # Missing name should fail
        with pytest.raises(ValueError):
            LabelCreateModel(description="test description")

    def test_extra_fields_forbidden(self):
        """Test that extra fields are rejected on CreateModel."""
        data = {"name": "test_label", "unknown_field": "should_fail"}
        with pytest.raises(ValidationError) as exc_info:
            LabelCreateModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestLabelUpdateModel:
    """Tests for the LabelUpdateModel."""

    def test_valid_construction(self):
        """Test that a valid LabelUpdateModel can be constructed."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "update_test_label",
            "description": "This is a test update label",
        }
        model = LabelUpdateModel(**data)

        assert str(model.id) == "123e4567-e89b-12d3-a456-426655440000"
        assert model.name == "update_test_label"
        assert model.description == "This is a test update label"

    def test_required_fields(self):
        """Test that LabelUpdateModel requires id and name."""
        # Missing id should fail validation
        with pytest.raises(ValueError):
            LabelUpdateModel(name="test_label", description="test description")

        # Missing name should fail validation
        with pytest.raises(ValueError):
            LabelUpdateModel(
                id="123e4567-e89b-12d3-a456-426655440000", description="test description"
            )

    def test_id_type_conversion(self):
        """Test that id is properly converted to UUID."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "update_test_label",
        }
        model = LabelUpdateModel(**data)

        # Verify the id was converted to UUID
        assert isinstance(model.id, UUID)
        assert str(model.id) == "123e4567-e89b-12d3-a456-426655440000"

    def test_extra_fields_forbidden(self):
        """Test that extra fields are rejected on UpdateModel."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test_label",
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            LabelUpdateModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestLabelResponseModel:
    """Tests for the LabelResponseModel."""

    def test_valid_construction(self):
        """Test that a valid LabelResponseModel can be constructed."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "response_test_label",
            "description": "This is a test response label",
        }

        model = LabelResponseModel(**data)

        assert str(model.id) == "123e4567-e89b-12d3-a456-426655440000"
        assert model.name == "response_test_label"
        assert model.description == "This is a test response label"

    def test_id_type_conversion(self):
        """Test that id is properly converted to UUID."""
        id_str = "123e4567-e89b-12d3-a456-426655440000"
        data = {
            "id": id_str,
            "name": "response_test_label",
        }

        model = LabelResponseModel(**data)

        # Verify the id was converted to UUID
        assert isinstance(model.id, UUID)
        assert str(model.id) == id_str

    def test_from_request_model(self):
        """Test creating a response model from a request model."""
        create_data = {"name": "create_test_label", "description": "This is a test create label"}
        create_model = LabelCreateModel(**create_data)
        response_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": create_model.name,
            "description": create_model.description,
        }
        response_model = LabelResponseModel(**response_data)

        assert isinstance(response_model, LabelResponseModel)
        assert response_model.name == create_model.name
        if create_model.description:
            assert response_model.description == create_model.description

    def test_extra_fields_forbidden(self):
        """Test that extra fields are rejected on ResponseModel."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test_label",
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            LabelResponseModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)
