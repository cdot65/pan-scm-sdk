# tests/scm/models/security/test_application_filters_models.py

# External libraries
import pytest

# Local SDK imports
from scm.models.objects.application_filters import (
    ApplicationFilterCreateModel,
)
from tests.factories import (
    ApplicationFilterCreateModelFactory,
    ApplicationFilterCreateApiFactory,
)


# -------------------- Test Classes for Pydantic Models --------------------


class TestApplicationFilterCreateModel:
    """Tests for Application Filter Create model validation."""

    def test_application_filters_create_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = ApplicationFilterCreateModelFactory.build_with_multiple_containers()
        with pytest.raises(ValueError) as exc_info:
            ApplicationFilterCreateModel(**data)
        assert (
            "1 validation error for ApplicationFilterCreateModel\n  Value error, Exactly one of 'folder' or 'snippet' must be provided"
            in str(exc_info.value)
        )

    def test_application_filters_create_model_with_folder(self):
        """Test creation with folder container."""
        model = ApplicationFilterCreateApiFactory.with_folder()
        assert model.folder == "Texas"
        assert model.snippet is None

    def test_application_filters_create_model_with_snippet(self):
        """Test creation with snippet container."""
        model = ApplicationFilterCreateApiFactory.with_snippet()
        assert model.snippet == "TestSnippet"
        assert model.folder is None


# -------------------- End of Test Classes --------------------
