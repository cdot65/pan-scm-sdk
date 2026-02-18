"""Test models for BGP Authentication Profiles."""

from uuid import UUID

from pydantic import ValidationError
import pytest

from scm.models.network import (
    BgpAuthProfileBaseModel,
    BgpAuthProfileResponseModel,
    BgpAuthProfileUpdateModel,
)


class TestBgpAuthProfileBaseModel:
    """Test BGP Authentication Profile base model validation."""

    def test_valid_minimal_fields(self):
        """Test valid model with only required fields."""
        model = BgpAuthProfileBaseModel(name="test-profile", folder="Test Folder")
        assert model.name == "test-profile"
        assert model.folder == "Test Folder"
        assert model.secret is None
        assert model.snippet is None
        assert model.device is None

    def test_valid_all_fields(self):
        """Test valid model with all fields populated."""
        model = BgpAuthProfileBaseModel(
            name="test-profile",
            folder="Test Folder",
            secret="my-bgp-secret",
        )
        assert model.name == "test-profile"
        assert model.folder == "Test Folder"
        assert model.secret == "my-bgp-secret"

    def test_missing_name_raises_error(self):
        """Test that missing name field raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            BgpAuthProfileBaseModel(folder="Test Folder")
        assert "name" in str(exc_info.value)

    def test_container_folder(self):
        """Test model with folder container."""
        model = BgpAuthProfileBaseModel(name="test", folder="MyFolder")
        assert model.folder == "MyFolder"
        assert model.snippet is None
        assert model.device is None

    def test_container_snippet(self):
        """Test model with snippet container."""
        model = BgpAuthProfileBaseModel(name="test", snippet="MySnippet")
        assert model.snippet == "MySnippet"
        assert model.folder is None

    def test_container_device(self):
        """Test model with device container."""
        model = BgpAuthProfileBaseModel(name="test", device="MyDevice")
        assert model.device == "MyDevice"
        assert model.folder is None

    def test_container_max_length(self):
        """Test container field max_length validation."""
        # Valid at max length (64 chars)
        model = BgpAuthProfileBaseModel(name="test", folder="A" * 64)
        assert len(model.folder) == 64

        # Invalid over max length
        with pytest.raises(ValidationError):
            BgpAuthProfileBaseModel(name="test", folder="A" * 65)

    def test_container_pattern_validation(self):
        """Test container field pattern validation."""
        # Valid patterns
        model = BgpAuthProfileBaseModel(name="test", folder="My-Folder_1.0")
        assert model.folder == "My-Folder_1.0"

        # Invalid pattern (special chars)
        with pytest.raises(ValidationError):
            BgpAuthProfileBaseModel(name="test", folder="Folder@#$")


class TestBgpAuthProfileUpdateModel:
    """Test BGP Authentication Profile update model."""

    def test_valid_update_model(self):
        """Test valid update model."""
        model = BgpAuthProfileUpdateModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="updated-profile",
            folder="Test Folder",
            secret="updated-secret",
        )
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "updated-profile"
        assert model.secret == "updated-secret"

    def test_invalid_uuid(self):
        """Test update model with invalid UUID."""
        with pytest.raises(ValidationError):
            BgpAuthProfileUpdateModel(
                id="not-a-uuid",
                name="test",
                folder="Test Folder",
            )

    def test_missing_id_raises_error(self):
        """Test that missing id field raises ValidationError."""
        with pytest.raises(ValidationError):
            BgpAuthProfileUpdateModel(
                name="test",
                folder="Test Folder",
            )


class TestBgpAuthProfileResponseModel:
    """Test BGP Authentication Profile response model."""

    def test_valid_response_model(self):
        """Test valid response model."""
        model = BgpAuthProfileResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="response-profile",
            folder="Test Folder",
            secret="my-secret",
        )
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "response-profile"
        assert model.secret == "my-secret"

    def test_missing_id_raises_error(self):
        """Test that missing id field raises ValidationError."""
        with pytest.raises(ValidationError):
            BgpAuthProfileResponseModel(
                name="test",
                folder="Test Folder",
            )


class TestExtraFieldsBgpAuthProfile:
    """Tests for extra field handling on BGP Authentication Profile models."""

    def test_base_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on BgpAuthProfileBaseModel."""
        with pytest.raises(ValidationError) as exc_info:
            BgpAuthProfileBaseModel(
                name="test",
                folder="Test Folder",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_update_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on BgpAuthProfileUpdateModel."""
        with pytest.raises(ValidationError) as exc_info:
            BgpAuthProfileUpdateModel(
                id="123e4567-e89b-12d3-a456-426655440000",
                name="test",
                folder="Test Folder",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_response_model_extra_fields_ignored(self):
        """Test that extra fields are silently ignored on BgpAuthProfileResponseModel."""
        model = BgpAuthProfileResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test",
            folder="Test Folder",
            unknown_field="should_be_ignored",
        )
        assert not hasattr(model, "unknown_field")
