# tests/scm/models/setup/test_snippet.py

"""Tests for snippet setup models."""

# Standard library imports
from uuid import UUID

from pydantic import ValidationError
import pytest

# Local SDK imports
from scm.models.setup.snippet import (
    FolderReference,
    SnippetBaseModel,
    SnippetCreateModel,
    SnippetResponseModel,
    SnippetUpdateModel,
)
from tests.factories.setup.snippet import (
    SnippetCreateModelFactory,
    SnippetResponseModelFactory,
    SnippetUpdateModelFactory,
)


class TestSnippetBaseModel:
    """Tests for the SnippetBaseModel."""

    def test_valid_construction(self):
        """Test that a valid SnippetBaseModel can be constructed."""
        model_instance = SnippetCreateModelFactory.build_valid_model()
        data = model_instance.model_dump()
        model = SnippetBaseModel(**data)

        assert model.name == data["name"]
        assert model.description == data["description"]
        assert model.labels == data["labels"]
        assert model.enable_prefix == data["enable_prefix"]

    def test_minimal_construction(self):
        """Test that a minimal SnippetBaseModel can be constructed."""
        data = {
            "name": "minimal_snippet",
        }

        model = SnippetBaseModel(**data)

        assert model.name == "minimal_snippet"
        assert model.description is None
        assert model.labels is None
        assert model.enable_prefix is None

    def test_name_validation(self):
        """Test that name is validated."""
        # Valid name should pass
        valid_model = SnippetBaseModel(name="valid_name", labels=[])
        assert valid_model.name == "valid_name"  # Verify the return value is used

        # Empty name should fail
        with pytest.raises(ValueError):
            SnippetBaseModel(name="", labels=[])

        # Whitespace-only name should fail
        with pytest.raises(ValueError):
            SnippetBaseModel(name="   ", labels=[])

        # Test the validator function directly to ensure its return value is covered
        result = SnippetBaseModel.validate_name("test_name")
        assert result == "test_name"

        with pytest.raises(ValueError):
            SnippetBaseModel.validate_name("")

        with pytest.raises(ValueError):
            SnippetBaseModel.validate_name("   ")

    def test_labels_validation(self):
        """Test labels field validation."""
        # Valid labels
        model = SnippetBaseModel(name="test_snippet", labels=["tag1", "tag2"])
        assert model.labels == ["tag1", "tag2"]

        # Empty list is valid
        model = SnippetBaseModel(name="test_snippet", labels=[])
        assert model.labels == []

        # None is valid (becomes None)
        model = SnippetBaseModel(name="test_snippet", labels=None)
        assert model.labels is None


class TestSnippetCreateModel:
    """Tests for the SnippetCreateModel."""

    def test_valid_construction(self):
        """Test that a valid SnippetCreateModel can be constructed."""
        model_instance = SnippetCreateModelFactory.build_valid_model()
        data = model_instance.model_dump()
        model = SnippetBaseModel(**data)

        assert model.name == data["name"]
        assert model.description == data["description"]
        assert model.labels == data["labels"]
        assert model.enable_prefix == data["enable_prefix"]

    def test_required_fields(self):
        """Test that SnippetCreateModel requires name."""
        with pytest.raises(ValueError) as excinfo:
            # Missing name should fail validation
            SnippetCreateModel()
        assert "name" in str(excinfo.value).lower()

        with pytest.raises(ValueError) as excinfo:
            # Empty name should fail validation
            SnippetCreateModel(name="")
        assert "name" in str(excinfo.value).lower()


class TestSnippetUpdateModel:
    """Tests for the SnippetUpdateModel."""

    def test_valid_construction(self):
        """Test that a valid SnippetUpdateModel can be constructed."""
        model_instance = SnippetUpdateModelFactory.build_valid_model()
        data = model_instance.model_dump()
        model = SnippetUpdateModel(**data)

        assert model.id == data["id"]
        assert model.name == data["name"]
        assert model.description == data["description"]
        assert model.labels == data["labels"]
        assert model.enable_prefix == data["enable_prefix"]

    def test_required_fields(self):
        """Test that SnippetUpdateModel requires an id."""
        with pytest.raises(ValueError) as excinfo:
            # Missing id should fail validation
            SnippetUpdateModel(name="test_snippet")
        assert "id" in str(excinfo.value).lower()

        # Test with valid id but empty name
        with pytest.raises(ValueError) as excinfo:
            SnippetUpdateModel(id="123e4567-e89b-12d3-a456-426614174000", name="")
        assert "name" in str(excinfo.value).lower()

    def test_id_type_conversion(self):
        """Test that id is properly converted to UUID."""
        model_instance = SnippetUpdateModelFactory.build_valid_model()
        data = model_instance.model_dump()
        model = SnippetUpdateModel(**data)

        # Verify the id was converted to UUID
        assert isinstance(model.id, UUID)
        assert model.id == data["id"]


class TestSnippetResponseModel:
    """Tests for the SnippetResponseModel."""

    def test_valid_construction(self):
        """Test that a valid SnippetResponseModel can be constructed."""
        data = SnippetResponseModelFactory.build()

        model = SnippetResponseModel(**data.model_dump())

        assert str(model.id) == str(data.id)
        assert model.name == data.name
        assert model.description == data.description
        assert model.labels == data.labels
        assert model.enable_prefix == data.enable_prefix
        assert model.type == data.type
        assert model.display_name == data.display_name
        assert model.last_update == data.last_update
        assert model.created_in == data.created_in
        assert model.folders == data.folders
        assert model.shared_in == data.shared_in

    def test_name_validation(self):
        """Test that name validation works."""
        data = SnippetResponseModelFactory.build()

        # Valid name should work
        model = SnippetResponseModel(**data.model_dump())
        assert model.name == data.name

        # Empty name should fail validation
        invalid_data = data.model_dump()
        invalid_data["name"] = ""
        with pytest.raises(ValueError) as excinfo:
            SnippetResponseModel(**invalid_data)
        assert "name" in str(excinfo.value).lower()

        # Whitespace-only name should fail validation
        invalid_data["name"] = "   "
        with pytest.raises(ValueError) as excinfo:
            SnippetResponseModel(**invalid_data)
        assert "name" in str(excinfo.value).lower()

    def test_folders_construction(self):
        """Test that a SnippetResponseModel with folders can be constructed."""
        folders = [{"id": str(UUID(int=i)), "name": f"folder_{i}"} for i in range(2)]
        data = SnippetResponseModelFactory.build(folders=folders)

        model = SnippetResponseModel(**data.model_dump())

        assert len(model.folders) == 2
        assert isinstance(model.folders[0], FolderReference)
        assert "id" in folders[0]
        assert "name" in folders[0]

    def test_id_type_conversion(self):
        """Test that id is properly converted to UUID."""
        data = SnippetResponseModelFactory.build()
        id_str = data.id  # Save original string representation

        model = SnippetResponseModel(**data.model_dump())

        # Verify the id was converted to UUID
        assert isinstance(model.id, UUID)
        assert str(model.id) == str(id_str)

    def test_predefined_snippet(self):
        """Test construction of a predefined snippet."""
        data = SnippetResponseModelFactory.build(type="predefined")

        model = SnippetResponseModel(**data.model_dump())

        assert model.type == "predefined"

    def test_custom_snippet(self):
        """Test construction of a custom snippet."""
        data = SnippetResponseModelFactory.build(type="custom")

        model = SnippetResponseModel(**data.model_dump())

        assert model.type == "custom"


class TestFolderReference:
    """Tests for the FolderReference model."""

    def test_valid_construction(self):
        """Test that a valid FolderReference can be constructed."""
        data = {"id": "123e4567-e89b-12d3-a456-426614174000", "name": "test_folder"}

        model = FolderReference(**data)

        assert str(model.id) == data["id"]
        assert model.name == data["name"]

    def test_required_fields(self):
        """Test that id and name are required fields."""
        # Missing id
        with pytest.raises(ValidationError):
            FolderReference(name="test_folder")

        # Missing name
        with pytest.raises(ValidationError):
            FolderReference(id="123e4567-e89b-12d3-a456-426614174000")

    def test_id_uuid_validation(self):
        """Test that id is validated as a proper UUID."""
        # Valid UUID should work
        valid_data = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "name": "test_folder",
        }
        model = FolderReference(**valid_data)
        assert str(model.id) == valid_data["id"]

        # Invalid UUID should fail
        invalid_data = {"id": "not-a-uuid", "name": "test_folder"}
        with pytest.raises(ValueError) as excinfo:
            FolderReference(**invalid_data)
        assert "id" in str(excinfo.value).lower()

    def test_name_validator_directly(self):
        """Test the name validator function directly to ensure coverage."""
        # Test that valid name is returned by the validator
        valid_name = "test_folder"
        result = FolderReference.validate_name(valid_name)
        assert result == valid_name

        # Test that invalid names raise ValueError
        with pytest.raises(ValueError) as exc_info:
            FolderReference.validate_name("")
        assert "folder name cannot be empty" in str(exc_info.value).lower()

        with pytest.raises(ValueError) as exc_info:
            FolderReference.validate_name("   ")
        assert "folder name cannot be empty" in str(exc_info.value).lower()
