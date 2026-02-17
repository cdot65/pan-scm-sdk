# tests/scm/models/setup/test_folder.py

"""Tests for folder setup models."""

# Standard library imports
from uuid import UUID

from pydantic import ValidationError
import pytest

# Local SDK imports
from scm.models.setup.folder import (
    FolderBaseModel,
    FolderCreateModel,
    FolderResponseModel,
    FolderUpdateModel,
)
from tests.factories.setup.folder import (
    FolderCreateModelFactory,
    FolderResponseModelFactory,
    FolderUpdateModelFactory,
)


class TestFolderBaseModel:
    """Tests for the FolderBaseModel."""

    def test_valid_construction(self):
        """Test that a valid FolderBaseModel can be constructed."""
        data = FolderCreateModelFactory.build_valid()

        model = FolderBaseModel(**data)

        assert model.name == data["name"]
        assert model.parent == data["parent"]
        assert model.description == data["description"]
        assert model.labels == data["labels"]
        assert model.snippets == data["snippets"]

    def test_minimal_construction(self):
        """Test that a minimal FolderBaseModel can be constructed."""
        data = {
            "name": "minimal_folder",
            "parent": "parent_id",
        }

        model = FolderBaseModel(**data)

        assert model.name == "minimal_folder"
        assert model.parent == "parent_id"
        assert model.description is None
        assert model.labels is None
        assert model.snippets is None

    def test_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        data = {
            "name": "test_folder",
            "parent": "parent_id",
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            FolderBaseModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestFolderCreateModel:
    """Tests for the FolderCreateModel."""

    def test_valid_construction(self):
        """Test that a valid FolderCreateModel can be constructed."""
        data = FolderCreateModelFactory.build_valid()

        model = FolderCreateModel(**data)

        assert model.name == data["name"]
        assert model.parent == data["parent"]
        assert model.description == data["description"]
        assert model.labels == data["labels"]
        assert model.snippets == data["snippets"]

    def test_required_fields(self):
        """Test that FolderCreateModel requires name and parent."""
        data = FolderCreateModelFactory.build_without_parent()

        with pytest.raises(ValueError) as excinfo:
            FolderCreateModel(**data)

        assert "parent" in str(excinfo.value)

    def test_extra_fields_forbidden(self):
        """Test that extra fields are rejected on CreateModel."""
        data = FolderCreateModelFactory.build_valid()
        data["unknown_field"] = "should_fail"
        with pytest.raises(ValidationError) as exc_info:
            FolderCreateModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestFolderUpdateModel:
    """Tests for the FolderUpdateModel."""

    def test_valid_construction(self):
        """Test that a valid FolderUpdateModel can be constructed."""
        data = FolderUpdateModelFactory.build_valid()

        model = FolderUpdateModel(**data)

        assert model.id == UUID(data["id"])
        assert model.name == data["name"]
        assert model.parent == data["parent"]
        assert model.description == data["description"]
        assert model.labels == data["labels"]
        assert model.snippets == data["snippets"]

    def test_required_fields(self):
        """Test that FolderUpdateModel requires an id."""
        data = FolderUpdateModelFactory.build_without_id()

        with pytest.raises(ValueError) as excinfo:
            FolderUpdateModel(**data)

        assert "id" in str(excinfo.value)

    def test_extra_fields_forbidden(self):
        """Test that extra fields are rejected on UpdateModel."""
        data = FolderUpdateModelFactory.build_valid()
        data["unknown_field"] = "should_fail"
        with pytest.raises(ValidationError) as exc_info:
            FolderUpdateModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestFolderResponseModel:
    """Tests for the FolderResponseModel."""

    def test_valid_construction(self):
        """Test that a valid FolderResponseModel can be constructed."""
        data = FolderResponseModelFactory.build_valid()

        model = FolderResponseModel(**data)

        assert model.id == UUID(data["id"])
        assert model.name == data["name"]
        assert model.parent == data["parent"]
        assert model.description == data["description"]
        assert model.labels == data["labels"]
        assert model.snippets == data["snippets"]

    def test_root_folder_construction(self):
        """Test that a root folder can be constructed with empty parent."""
        data = FolderResponseModelFactory.build_root_folder()

        model = FolderResponseModel(**data)

        assert model.id == UUID(data["id"])
        assert model.name == data["name"]
        assert model.parent == ""  # Empty parent for root folder

    def test_extra_fields_ignored(self):
        """Test that extra fields are silently ignored on ResponseModel."""
        data = FolderResponseModelFactory.build_valid()
        data["unknown_field"] = "should_be_ignored"
        model = FolderResponseModel(**data)
        assert not hasattr(model, "unknown_field")
