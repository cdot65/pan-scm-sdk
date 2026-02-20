"""Test models for QoS Profiles."""

from uuid import UUID

from pydantic import ValidationError
import pytest

from scm.models.network import (
    QosProfileBaseModel,
    QosProfileCreateModel,
    QosProfileResponseModel,
    QosProfileUpdateModel,
)


class TestQosProfileBaseModel:
    """Test QoS Profile base model validation."""

    def test_valid_minimal_fields(self):
        """Test valid model with only required fields."""
        model = QosProfileBaseModel(name="test-profile", folder="Test Folder")
        assert model.name == "test-profile"
        assert model.folder == "Test Folder"
        assert model.aggregate_bandwidth is None
        assert model.class_bandwidth_type is None
        assert model.snippet is None
        assert model.device is None

    def test_valid_all_fields(self):
        """Test valid model with all fields populated."""
        model = QosProfileBaseModel(
            name="test-profile",
            folder="Test Folder",
            aggregate_bandwidth={
                "egress_max": 1000,
                "egress_guaranteed": 500,
            },
            class_bandwidth_type={"mbps": {"class": [{"name": "class1", "bandwidth": 100}]}},
        )
        assert model.name == "test-profile"
        assert model.folder == "Test Folder"
        assert model.aggregate_bandwidth["egress_max"] == 1000
        assert model.class_bandwidth_type is not None

    def test_missing_name_raises_error(self):
        """Test that missing name field raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            QosProfileBaseModel(folder="Test Folder")
        assert "name" in str(exc_info.value)

    def test_container_folder(self):
        """Test model with folder container."""
        model = QosProfileBaseModel(name="test", folder="MyFolder")
        assert model.folder == "MyFolder"
        assert model.snippet is None
        assert model.device is None

    def test_container_snippet(self):
        """Test model with snippet container."""
        model = QosProfileBaseModel(name="test", snippet="MySnippet")
        assert model.snippet == "MySnippet"
        assert model.folder is None

    def test_container_device(self):
        """Test model with device container."""
        model = QosProfileBaseModel(name="test", device="MyDevice")
        assert model.device == "MyDevice"
        assert model.folder is None

    def test_container_max_length(self):
        """Test container field max_length validation."""
        # Valid at max length (64 chars)
        model = QosProfileBaseModel(name="test", folder="A" * 64)
        assert len(model.folder) == 64

        # Invalid over max length
        with pytest.raises(ValidationError):
            QosProfileBaseModel(name="test", folder="A" * 65)

    def test_name_max_length(self):
        """Test name field max_length validation (31 chars)."""
        # Valid at max length
        model = QosProfileBaseModel(name="A" * 31, folder="Test Folder")
        assert len(model.name) == 31

        # Invalid over max length
        with pytest.raises(ValidationError):
            QosProfileBaseModel(name="A" * 32, folder="Test Folder")

    def test_container_pattern_validation(self):
        """Test container field pattern validation."""
        # Valid patterns
        model = QosProfileBaseModel(name="test", folder="My-Folder_1.0")
        assert model.folder == "My-Folder_1.0"

        # Invalid pattern (special chars)
        with pytest.raises(ValidationError):
            QosProfileBaseModel(name="test", folder="Folder@#$")


class TestQosProfileCreateModel:
    """Test QoS Profile create model."""

    def test_valid_create_with_folder(self):
        """Test valid create model with folder container."""
        model = QosProfileCreateModel(
            name="test-profile",
            folder="Test Folder",
        )
        assert model.name == "test-profile"
        assert model.folder == "Test Folder"

    def test_valid_create_with_snippet(self):
        """Test valid create model with snippet container."""
        model = QosProfileCreateModel(
            name="test-profile",
            snippet="MySnippet",
        )
        assert model.snippet == "MySnippet"

    def test_valid_create_with_device(self):
        """Test valid create model with device container."""
        model = QosProfileCreateModel(
            name="test-profile",
            device="MyDevice",
        )
        assert model.device == "MyDevice"

    def test_create_no_container_raises_error(self):
        """Test that create without any container raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            QosProfileCreateModel(name="test-profile")
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_create_multiple_containers_raises_error(self):
        """Test that create with multiple containers raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            QosProfileCreateModel(
                name="test-profile",
                folder="Test Folder",
                snippet="MySnippet",
            )
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_create_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on QosProfileCreateModel."""
        with pytest.raises(ValidationError) as exc_info:
            QosProfileCreateModel(
                name="test",
                folder="Test Folder",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_create_with_aggregate_bandwidth(self):
        """Test create model with aggregate bandwidth settings."""
        model = QosProfileCreateModel(
            name="test-profile",
            folder="Test Folder",
            aggregate_bandwidth={
                "egress_max": 1000,
                "egress_guaranteed": 500,
            },
        )
        assert model.aggregate_bandwidth["egress_max"] == 1000
        assert model.aggregate_bandwidth["egress_guaranteed"] == 500


class TestQosProfileUpdateModel:
    """Test QoS Profile update model."""

    def test_valid_update_model(self):
        """Test valid update model."""
        model = QosProfileUpdateModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="updated-profile",
            folder="Test Folder",
        )
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "updated-profile"

    def test_invalid_uuid(self):
        """Test update model with invalid UUID."""
        with pytest.raises(ValidationError):
            QosProfileUpdateModel(
                id="not-a-uuid",
                name="test",
                folder="Test Folder",
            )

    def test_missing_id_raises_error(self):
        """Test that missing id field raises ValidationError."""
        with pytest.raises(ValidationError):
            QosProfileUpdateModel(
                name="test",
                folder="Test Folder",
            )


class TestQosProfileResponseModel:
    """Test QoS Profile response model."""

    def test_valid_response_model(self):
        """Test valid response model."""
        model = QosProfileResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="response-profile",
            folder="Test Folder",
        )
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "response-profile"

    def test_missing_id_raises_error(self):
        """Test that missing id field raises ValidationError."""
        with pytest.raises(ValidationError):
            QosProfileResponseModel(
                name="test",
                folder="Test Folder",
            )


class TestExtraFieldsQosProfile:
    """Tests for extra field handling on QoS Profile models."""

    def test_base_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on QosProfileBaseModel."""
        with pytest.raises(ValidationError) as exc_info:
            QosProfileBaseModel(
                name="test",
                folder="Test Folder",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_update_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on QosProfileUpdateModel."""
        with pytest.raises(ValidationError) as exc_info:
            QosProfileUpdateModel(
                id="123e4567-e89b-12d3-a456-426655440000",
                name="test",
                folder="Test Folder",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_response_model_extra_fields_ignored(self):
        """Test that extra fields are silently ignored on QosProfileResponseModel."""
        model = QosProfileResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test",
            folder="Test Folder",
            unknown_field="should_be_ignored",
        )
        assert not hasattr(model, "unknown_field")
