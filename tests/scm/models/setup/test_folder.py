# tests/scm/models/setup/test_folder.py

# Standard library imports
from uuid import UUID

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
