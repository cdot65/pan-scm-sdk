# tests/scm/models/security/test_url_categories.py

# External libraries
import pytest

# Local SDK imports
from scm.models.security.url_categories import (
    URLCategoriesCreateModel,
)
from tests.factories import (
    URLCategoriesCreateModelFactory,
    URLCategoriesCreateApiFactory,
)


# -------------------- Test Classes for Pydantic Models --------------------


class TestURLCategoriesCreateModel:
    """Tests for DNS Security Profile Create model validation."""

    def test_url_categories_create_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = URLCategoriesCreateModelFactory.build_with_multiple_containers()
        with pytest.raises(ValueError) as exc_info:
            URLCategoriesCreateModel(**data)
        assert (
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            in str(exc_info.value)
        )

    def test_url_categories_create_model_with_snippet(self):
        """Test creation with snippet container."""
        model = URLCategoriesCreateApiFactory.with_snippet()
        assert model.snippet == "TestSnippet"
        assert model.folder is None
        assert model.device is None

    def test_url_categories_create_model_with_device(self):
        """Test creation with device container."""
        model = URLCategoriesCreateApiFactory.with_device()
        assert model.device == "TestDevice"
        assert model.folder is None
        assert model.snippet is None


# -------------------- End of Test Classes --------------------
