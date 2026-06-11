# tests/scm/models/mobile_agent/test_forwarding_profile_source_applications_models.py

"""Tests for forwarding profile source application models."""

# External libraries
from pydantic import ValidationError
import pytest

# Local SDK imports
from scm.models.mobile_agent.forwarding_profile_source_applications import (
    ForwardingProfileSourceApplicationBaseModel,
    ForwardingProfileSourceApplicationCreateModel,
    ForwardingProfileSourceApplicationResponseModel,
    ForwardingProfileSourceApplicationUpdateModel,
)
from tests.scm.models.mobile_agent.factories import (
    ForwardingProfileSourceApplicationCreateModelFactory,
    ForwardingProfileSourceApplicationResponseModelFactory,
)

TEST_ID = "123e4567-e89b-12d3-a456-426655440000"


class TestForwardingProfileSourceApplicationBaseModel:
    """Tests for ForwardingProfileSourceApplicationBaseModel validation."""

    def test_base_model_minimal(self):
        """Test that a minimal base model can be created."""
        model = ForwardingProfileSourceApplicationBaseModel(
            name="saas-apps",
            applications=["office365-enterprise-access"],
        )
        assert model.name == "saas-apps"
        assert model.applications == ["office365-enterprise-access"]
        assert model.description is None

    def test_base_model_complete(self):
        """Test that a complete base model can be created."""
        model = ForwardingProfileSourceApplicationBaseModel(
            name="saas-apps",
            description="SaaS applications",
            applications=["slack", "zoom"],
        )
        assert model.description == "SaaS applications"
        assert len(model.applications) == 2

    def test_base_model_invalid_name(self):
        """Test validation when name has invalid format."""
        with pytest.raises(ValidationError) as exc_info:
            ForwardingProfileSourceApplicationBaseModel(
                name="invalid name!",
                applications=["slack"],
            )
        assert "name\n  String should match pattern" in str(exc_info.value)

    def test_base_model_name_too_long(self):
        """Test name length validation."""
        with pytest.raises(ValidationError) as exc_info:
            ForwardingProfileSourceApplicationBaseModel(
                name="a" * 65,  # Max length is 64
                applications=["slack"],
            )
        assert "name\n  String should have at most 64 characters" in str(exc_info.value)

    def test_base_model_missing_required_fields(self):
        """Test validation when required fields are missing."""
        with pytest.raises(ValidationError) as exc_info:
            ForwardingProfileSourceApplicationBaseModel(name="saas-apps")
        assert "applications\n  Field required" in str(exc_info.value)

    def test_base_model_description_too_long(self):
        """Test description length validation."""
        with pytest.raises(ValidationError) as exc_info:
            ForwardingProfileSourceApplicationBaseModel(
                name="saas-apps",
                description="a" * 1024,  # Max length is 1023
                applications=["slack"],
            )
        assert "description\n  String should have at most 1023 characters" in str(exc_info.value)

    def test_base_model_rejects_extra_fields(self):
        """Test that unknown fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ForwardingProfileSourceApplicationBaseModel(
                name="saas-apps",
                applications=["slack"],
                unknown_field="value",
            )
        assert "unknown_field" in str(exc_info.value)

    def test_model_dump_exclude_unset(self):
        """Test model dumping with exclude_unset."""
        model = ForwardingProfileSourceApplicationBaseModel(
            name="saas-apps",
            applications=["slack"],
        )
        model_dict = model.model_dump(exclude_unset=True)
        assert model_dict == {"name": "saas-apps", "applications": ["slack"]}


class TestForwardingProfileSourceApplicationCreateModel:
    """Tests for ForwardingProfileSourceApplicationCreateModel validation."""

    def test_create_model_valid(self):
        """Test validation with valid data."""
        data = ForwardingProfileSourceApplicationCreateModelFactory.build_valid()
        model = ForwardingProfileSourceApplicationCreateModel(**data)
        assert model.name == data["name"]
        assert model.applications == data["applications"]

    def test_create_model_invalid_name(self):
        """Test validation with invalid name."""
        data = ForwardingProfileSourceApplicationCreateModelFactory.build_invalid_name()
        with pytest.raises(ValidationError):
            ForwardingProfileSourceApplicationCreateModel(**data)


class TestForwardingProfileSourceApplicationUpdateModel:
    """Tests for ForwardingProfileSourceApplicationUpdateModel validation."""

    def test_update_model_requires_id(self):
        """Test that the update model requires an id."""
        with pytest.raises(ValidationError) as exc_info:
            ForwardingProfileSourceApplicationUpdateModel(
                name="saas-apps",
                applications=["slack"],
            )
        assert "id\n  Field required" in str(exc_info.value)

    def test_update_model_valid(self):
        """Test validation with valid update data."""
        model = ForwardingProfileSourceApplicationUpdateModel(
            id=TEST_ID,
            name="saas-apps",
            applications=["slack"],
        )
        assert str(model.id) == TEST_ID


class TestForwardingProfileSourceApplicationResponseModel:
    """Tests for ForwardingProfileSourceApplicationResponseModel validation."""

    def test_response_model_valid(self):
        """Test validation with valid response data."""
        model = ForwardingProfileSourceApplicationResponseModel(
            id=TEST_ID,
            name="saas-apps",
            applications=["slack"],
        )
        assert str(model.id) == TEST_ID

    def test_response_model_from_factory(self):
        """Test that the response model factory produces valid models."""
        model = ForwardingProfileSourceApplicationResponseModelFactory()
        assert model.name is not None
        assert model.id is not None

    def test_response_model_ignores_extra_fields(self):
        """Test that unknown fields in API responses are ignored."""
        model = ForwardingProfileSourceApplicationResponseModel(
            id=TEST_ID,
            name="saas-apps",
            applications=["slack"],
            future_field="ignored",
        )
        assert not hasattr(model, "future_field")
