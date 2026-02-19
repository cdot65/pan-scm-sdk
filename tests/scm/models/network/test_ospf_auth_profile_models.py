"""Test models for OSPF Authentication Profiles."""

from uuid import UUID

from pydantic import ValidationError
import pytest

from scm.models.network import (
    OspfAuthProfileBaseModel,
    OspfAuthProfileCreateModel,
    OspfAuthProfileMd5Key,
    OspfAuthProfileMd5KeyResponse,
    OspfAuthProfileResponseModel,
    OspfAuthProfileUpdateModel,
)


class TestOspfAuthProfileMd5Key:
    """Test OSPF auth profile MD5 key nested model."""

    def test_valid_md5_key(self):
        """Test valid MD5 key configuration."""
        key = OspfAuthProfileMd5Key(name=1, key="secret123", preferred=True)
        assert key.name == 1
        assert key.key == "secret123"
        assert key.preferred is True

    def test_md5_key_optional_fields(self):
        """Test MD5 key with no fields set."""
        key = OspfAuthProfileMd5Key()
        assert key.name is None
        assert key.key is None
        assert key.preferred is None

    def test_md5_key_name_range(self):
        """Test MD5 key name (ID) boundary values."""
        # Valid min
        key = OspfAuthProfileMd5Key(name=1)
        assert key.name == 1

        # Valid max
        key = OspfAuthProfileMd5Key(name=255)
        assert key.name == 255

        # Out of range
        with pytest.raises(ValidationError):
            OspfAuthProfileMd5Key(name=0)

        with pytest.raises(ValidationError):
            OspfAuthProfileMd5Key(name=256)

    def test_md5_key_max_length(self):
        """Test MD5 key enforces max_length=16 on input."""
        key = OspfAuthProfileMd5Key(key="A" * 16)
        assert len(key.key) == 16

        with pytest.raises(ValidationError):
            OspfAuthProfileMd5Key(key="A" * 17)

    def test_md5_key_extra_fields_forbidden(self):
        """Test that extra fields are rejected on OspfAuthProfileMd5Key."""
        with pytest.raises(ValidationError) as exc_info:
            OspfAuthProfileMd5Key(name=1, unknown_field="should_fail")
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestOspfAuthProfileMd5KeyResponse:
    """Test OSPF auth profile MD5 key response model (accepts encrypted values)."""

    def test_accepts_encrypted_key(self):
        """Test response key model accepts long encrypted values from API."""
        encrypted = "-AQ==MzoT6FsyFbec2rckK2QehR0O5nc=T4nfel3vRF8QGRrgx9f93Q=="
        key = OspfAuthProfileMd5KeyResponse(name=1, key=encrypted)
        assert key.key == encrypted
        assert len(key.key) == 57

    def test_accepts_short_key(self):
        """Test response key model also accepts short plaintext keys."""
        key = OspfAuthProfileMd5KeyResponse(name=1, key="short")
        assert key.key == "short"

    def test_extra_fields_ignored(self):
        """Test that extra fields are ignored on response model."""
        key = OspfAuthProfileMd5KeyResponse(name=1, key="test", unknown="field")
        assert key.name == 1


class TestOspfAuthProfileBaseModel:
    """Test OSPF Authentication Profile base model validation."""

    def test_valid_minimal_fields(self):
        """Test valid model with only required fields."""
        model = OspfAuthProfileBaseModel(name="test-ospf", folder="Test Folder")
        assert model.name == "test-ospf"
        assert model.folder == "Test Folder"
        assert model.password is None
        assert model.md5 is None

    def test_valid_with_password(self):
        """Test valid model with password auth."""
        model = OspfAuthProfileBaseModel(
            name="test-ospf",
            folder="Test Folder",
            password="ospf-secret",
        )
        assert model.password == "ospf-secret"
        assert model.md5 is None

    def test_valid_with_md5(self):
        """Test valid model with MD5 auth."""
        model = OspfAuthProfileBaseModel(
            name="test-ospf",
            folder="Test Folder",
            md5=[
                OspfAuthProfileMd5Key(name=1, key="key1", preferred=True),
                OspfAuthProfileMd5Key(name=2, key="key2", preferred=False),
            ],
        )
        assert model.password is None
        assert len(model.md5) == 2
        assert model.md5[0].name == 1
        assert model.md5[1].key == "key2"

    def test_password_and_md5_mutually_exclusive(self):
        """Test that password and md5 are mutually exclusive."""
        with pytest.raises(ValueError) as exc_info:
            OspfAuthProfileBaseModel(
                name="test-ospf",
                folder="Test Folder",
                password="ospf-secret",
                md5=[OspfAuthProfileMd5Key(name=1, key="key1")],
            )
        assert "'password' and 'md5' are mutually exclusive" in str(exc_info.value)

    def test_missing_name_raises_error(self):
        """Test that missing name field raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            OspfAuthProfileBaseModel(folder="Test Folder")
        assert "name" in str(exc_info.value)

    def test_container_folder(self):
        """Test model with folder container."""
        model = OspfAuthProfileBaseModel(name="test", folder="MyFolder")
        assert model.folder == "MyFolder"
        assert model.snippet is None
        assert model.device is None

    def test_container_snippet(self):
        """Test model with snippet container."""
        model = OspfAuthProfileBaseModel(name="test", snippet="MySnippet")
        assert model.snippet == "MySnippet"
        assert model.folder is None

    def test_container_device(self):
        """Test model with device container."""
        model = OspfAuthProfileBaseModel(name="test", device="MyDevice")
        assert model.device == "MyDevice"
        assert model.folder is None

    def test_container_max_length(self):
        """Test container field max_length validation."""
        model = OspfAuthProfileBaseModel(name="test", folder="A" * 64)
        assert len(model.folder) == 64

        with pytest.raises(ValidationError):
            OspfAuthProfileBaseModel(name="test", folder="A" * 65)

    def test_container_pattern_validation(self):
        """Test container field pattern validation."""
        model = OspfAuthProfileBaseModel(name="test", folder="My-Folder_1.0")
        assert model.folder == "My-Folder_1.0"

        with pytest.raises(ValidationError):
            OspfAuthProfileBaseModel(name="test", folder="Folder@#$")


class TestOspfAuthProfileCreateModel:
    """Test OSPF Authentication Profile create model."""

    def test_valid_create_with_folder(self):
        """Test valid create model with folder container."""
        model = OspfAuthProfileCreateModel(
            name="test-ospf",
            folder="Test Folder",
            password="ospf-secret",
        )
        assert model.name == "test-ospf"
        assert model.folder == "Test Folder"

    def test_valid_create_with_snippet(self):
        """Test valid create model with snippet container."""
        model = OspfAuthProfileCreateModel(
            name="test-ospf",
            snippet="MySnippet",
        )
        assert model.snippet == "MySnippet"

    def test_valid_create_with_device(self):
        """Test valid create model with device container."""
        model = OspfAuthProfileCreateModel(
            name="test-ospf",
            device="MyDevice",
        )
        assert model.device == "MyDevice"

    def test_create_no_container_raises_error(self):
        """Test that create without any container raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            OspfAuthProfileCreateModel(name="test-ospf")
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_create_multiple_containers_raises_error(self):
        """Test that create with multiple containers raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            OspfAuthProfileCreateModel(
                name="test-ospf",
                folder="Test Folder",
                snippet="MySnippet",
            )
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_create_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on OspfAuthProfileCreateModel."""
        with pytest.raises(ValidationError) as exc_info:
            OspfAuthProfileCreateModel(
                name="test",
                folder="Test Folder",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestOspfAuthProfileUpdateModel:
    """Test OSPF Authentication Profile update model."""

    def test_valid_update_model(self):
        """Test valid update model."""
        model = OspfAuthProfileUpdateModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="updated-ospf",
            folder="Test Folder",
            password="updated-secret",
        )
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "updated-ospf"
        assert model.password == "updated-secret"

    def test_invalid_uuid(self):
        """Test update model with invalid UUID."""
        with pytest.raises(ValidationError):
            OspfAuthProfileUpdateModel(
                id="not-a-uuid",
                name="test",
                folder="Test Folder",
            )

    def test_mutual_exclusion_on_update(self):
        """Test that password/md5 mutual exclusion applies on update."""
        with pytest.raises(ValueError):
            OspfAuthProfileUpdateModel(
                id="123e4567-e89b-12d3-a456-426655440000",
                name="test",
                folder="Test Folder",
                password="secret",
                md5=[OspfAuthProfileMd5Key(name=1, key="key1")],
            )


class TestOspfAuthProfileResponseModel:
    """Test OSPF Authentication Profile response model."""

    def test_valid_response_model(self):
        """Test valid response model."""
        model = OspfAuthProfileResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="response-ospf",
            folder="Test Folder",
            password="my-password",
        )
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "response-ospf"
        assert model.password == "my-password"

    def test_missing_id_raises_error(self):
        """Test that missing id field raises ValidationError."""
        with pytest.raises(ValidationError):
            OspfAuthProfileResponseModel(
                name="test",
                folder="Test Folder",
            )


class TestExtraFieldsOspfAuthProfile:
    """Tests for extra field handling on OSPF Authentication Profile models."""

    def test_base_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on OspfAuthProfileBaseModel."""
        with pytest.raises(ValidationError) as exc_info:
            OspfAuthProfileBaseModel(
                name="test",
                folder="Test Folder",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_update_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on OspfAuthProfileUpdateModel."""
        with pytest.raises(ValidationError) as exc_info:
            OspfAuthProfileUpdateModel(
                id="123e4567-e89b-12d3-a456-426655440000",
                name="test",
                folder="Test Folder",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_response_model_extra_fields_ignored(self):
        """Test that extra fields are silently ignored on OspfAuthProfileResponseModel."""
        model = OspfAuthProfileResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test",
            folder="Test Folder",
            unknown_field="should_be_ignored",
        )
        assert not hasattr(model, "unknown_field")
