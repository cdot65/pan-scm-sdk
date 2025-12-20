# tests/scm/models/objects/test_application_filters_models.py

"""Tests for application filter models."""

# External libraries
from pydantic import ValidationError
import pytest

# Local SDK imports
from scm.models.objects.application_filters import (
    ApplicationFiltersCreateModel,
    ApplicationFiltersResponseModel,
    ApplicationFiltersUpdateModel,
)
from tests.factories.objects.application_filters import (
    ApplicationFiltersCreateApiFactory,
    ApplicationFiltersCreateModelFactory,
    ApplicationFiltersResponseModelFactory,
    ApplicationFiltersUpdateModelFactory,
)

# -------------------- Test Classes for Pydantic Models --------------------


class TestApplicationFilterCreateModel:
    """Tests for Application Filter Create model validation."""

    def test_application_filters_create_model_valid(self):
        """Test validation with valid data."""
        data = ApplicationFiltersCreateModelFactory.build_valid()
        model = ApplicationFiltersCreateModel(**data)
        assert model.name.startswith("application_filters_")
        assert model.folder == "Texas"
        assert model.snippet is None

    def test_application_filters_create_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = ApplicationFiltersCreateModelFactory.build_with_multiple_containers()
        with pytest.raises(ValidationError) as exc_info:
            ApplicationFiltersCreateModel(**data)
        assert "Exactly one of 'folder' or 'snippet' must be provided" in str(exc_info.value)

    def test_application_filters_create_model_no_containers(self):
        """Test validation when no containers are provided."""
        data = ApplicationFiltersCreateModelFactory.build_with_no_containers()
        with pytest.raises(ValidationError) as exc_info:
            ApplicationFiltersCreateModel(**data)
        assert "Exactly one of 'folder' or 'snippet' must be provided" in str(exc_info.value)

    def test_application_filters_create_model_with_folder(self):
        """Test creation with folder container."""
        model = ApplicationFiltersCreateApiFactory.with_folder()
        assert model.folder == "Texas"
        assert model.snippet is None

    def test_application_filters_create_model_with_snippet(self):
        """Test creation with snippet container."""
        model = ApplicationFiltersCreateApiFactory.with_snippet()
        assert model.snippet == "TestSnippet"
        assert model.folder is None

    def test_application_filters_create_model_with_boolean_flags(self):
        """Test creation with all boolean flags set."""
        model = ApplicationFiltersCreateApiFactory.with_all_boolean_flags()
        assert model.evasive is True
        assert model.used_by_malware is True
        assert model.transfers_files is True
        assert model.has_known_vulnerabilities is True
        assert model.tunnels_other_apps is True
        assert model.prone_to_misuse is True
        assert model.pervasive is True
        assert model.is_saas is True
        assert model.new_appid is True
        # Remove the excessive_bandwidth_use assertion since it doesn't exist in the model


class TestApplicationFilterUpdateModel:
    """Tests for Application Filter Update model validation."""

    def test_application_filters_update_model_valid(self):
        """Test validation with valid update data."""
        data = ApplicationFiltersUpdateModelFactory.build_valid()
        model = ApplicationFiltersUpdateModel(**data)
        assert model.name.startswith("application_filters_updated_")
        assert model.id is not None

    def test_application_filters_update_model_minimal(self):
        """Test validation with minimal update data."""
        data = ApplicationFiltersUpdateModelFactory.build_minimal_update()
        model = ApplicationFiltersUpdateModel(**data)
        assert model.name == "MinimalUpdate"
        assert model.id is not None

    def test_application_filters_update_model_invalid_fields(self):
        """Test validation with invalid fields."""
        data = ApplicationFiltersUpdateModelFactory.build_with_invalid_fields()
        with pytest.raises(ValidationError) as exc_info:
            ApplicationFiltersUpdateModel(**data)
        error_msg = str(exc_info.value)
        assert "Input should be a valid UUID" in error_msg or "Invalid UUID format" in error_msg


class TestApplicationFilterResponseModel:
    """Tests for Application Filter Response model validation."""

    def test_application_filters_response_model_valid(self):
        """Test validation with valid response data."""
        data = ApplicationFiltersResponseModelFactory.build_valid()
        model = ApplicationFiltersResponseModel(**data)
        assert model.name.startswith("application_filters_")
        assert model.id is not None
        assert model.folder == "Texas"
        assert model.snippet is None
        assert len(model.category) > 0
        assert len(model.sub_category) > 0
        assert len(model.technology) > 0


class TestExtraFieldsForbidden:
    """Test that extra fields are rejected by all models."""

    def test_application_filters_create_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected in ApplicationFiltersCreateModel."""
        data = ApplicationFiltersCreateModelFactory.build_valid()
        data["unknown_field"] = "should fail"
        with pytest.raises(ValidationError) as exc_info:
            ApplicationFiltersCreateModel(**data)
        assert "extra" in str(exc_info.value).lower()

    def test_application_filters_update_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected in ApplicationFiltersUpdateModel."""
        data = ApplicationFiltersUpdateModelFactory.build_valid()
        data["unknown_field"] = "should fail"
        with pytest.raises(ValidationError) as exc_info:
            ApplicationFiltersUpdateModel(**data)
        assert "extra" in str(exc_info.value).lower()

    def test_application_filters_response_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected in ApplicationFiltersResponseModel."""
        data = ApplicationFiltersResponseModelFactory.build_valid()
        data["unknown_field"] = "should fail"
        with pytest.raises(ValidationError) as exc_info:
            ApplicationFiltersResponseModel(**data)
        assert "extra" in str(exc_info.value).lower()


# -------------------- End of Test Classes --------------------
