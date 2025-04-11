# tests/scm/models/security/test_url_categories.py

# External libraries
from uuid import UUID

import pytest

# Local SDK imports
from scm.models.security.url_categories import (
    URLCategoriesCreateModel,
    URLCategoriesResponseModel,
    URLCategoriesUpdateModel,
)
from tests.test_factories.security.url_categories import (
    URLCategoriesCreateModelFactory,
    URLCategoriesResponseModelFactory,
    URLCategoriesUpdateModelFactory,
)

# -------------------- Test Classes for Pydantic Models --------------------


class TestURLCategoriesCreateModel:
    """Tests for URL Categories Create model validation."""

    def test_url_categories_create_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = URLCategoriesCreateModelFactory.build_with_multiple_containers()
        with pytest.raises(ValueError) as exc_info:
            URLCategoriesCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_url_categories_create_model_with_snippet(self):
        """Test creation with snippet container."""
        model = URLCategoriesCreateModelFactory.with_snippet()
        assert model.snippet == "TestSnippet"
        assert model.folder is None
        assert model.device is None
        assert isinstance(model.list, list)
        assert len(model.list) > 0

    def test_url_categories_create_model_with_device(self):
        """Test creation with device container."""
        model = URLCategoriesCreateModelFactory.with_device()
        assert model.device == "TestDevice"
        assert model.folder is None
        assert model.snippet is None
        assert isinstance(model.list, list)
        assert len(model.list) > 0


class TestURLCategoriesUpdateModel:
    """Tests for URL Categories Update model validation."""

    def test_url_categories_update_model_with_updated_list(self):
        """Test updating with a new list of URLs."""
        model = URLCategoriesUpdateModelFactory.with_updated_list()
        assert isinstance(model.list, list)
        assert len(model.list) > 0

    def test_url_categories_update_model_with_category_match(self):
        """Test updating with category match type."""
        model = URLCategoriesUpdateModelFactory.with_category_match()
        assert model.type == "Category Match"
        assert "hacking" in model.list
        assert "low-risk" in model.list

    def test_url_categories_update_model_with_invalid_type(self):
        """Test validation with invalid type."""
        with pytest.raises(ValueError):
            URLCategoriesUpdateModelFactory.with_invalid_type()


class TestURLCategoriesResponseModel:
    """Tests for URL Categories Response model validation."""

    def test_url_categories_response_model_with_folder(self):
        """Test response model with folder container."""
        model = URLCategoriesResponseModelFactory()
        assert model.folder == "Shared"
        assert model.snippet is None
        assert model.device is None
        assert isinstance(model.id, UUID)
        assert isinstance(model.list, list)

    def test_url_categories_response_model_with_snippet(self):
        """Test response model with snippet container."""
        model = URLCategoriesResponseModelFactory.with_snippet()
        assert model.snippet == "TestSnippet"
        assert model.folder is None
        assert model.device is None
        assert isinstance(model.list, list)

    def test_url_categories_response_model_with_device(self):
        """Test response model with device container."""
        model = URLCategoriesResponseModelFactory.with_device()
        assert model.device == "TestDevice"
        assert model.folder is None
        assert model.snippet is None
        assert isinstance(model.list, list)

    def test_url_categories_response_model_with_custom_urls(self):
        """Test response model with custom URLs."""
        test_urls = ["example1.com", "example2.org"]
        model = URLCategoriesResponseModelFactory.with_custom_urls(urls=test_urls)
        assert model.list == test_urls


# -------------------- End of Test Classes --------------------
