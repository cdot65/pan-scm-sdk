"""Tests for local config version models."""

from pydantic import ValidationError
import pytest

from scm.models.operations.local_config import LocalConfigVersionModel


class TestLocalConfigVersionModel:
    """Tests for LocalConfigVersionModel."""

    def test_valid_model(self):
        """Test that a valid model with all required fields is accepted."""
        data = {
            "id": 1,
            "serial": "007951000123456",
            "local_version": "1.0.0",
            "timestamp": "2025-01-15T10:30:00Z",
            "xfmed_version": "1.0.0-transformed",
        }
        model = LocalConfigVersionModel(**data)
        assert model.id == 1
        assert model.serial == "007951000123456"
        assert model.local_version == "1.0.0"
        assert model.xfmed_version == "1.0.0-transformed"

    def test_optional_md5(self):
        """Test that optional md5 field is accepted when provided."""
        data = {
            "id": 2,
            "serial": "007951000123456",
            "local_version": "1.0.0",
            "timestamp": "2025-01-15T10:30:00Z",
            "xfmed_version": "1.0.0-transformed",
            "md5": "abc123def456",
        }
        model = LocalConfigVersionModel(**data)
        assert model.md5 == "abc123def456"

    def test_md5_defaults_none(self):
        """Test that md5 defaults to None when not provided."""
        data = {
            "id": 1,
            "serial": "007951000123456",
            "local_version": "1.0.0",
            "timestamp": "2025-01-15T10:30:00Z",
            "xfmed_version": "1.0.0-transformed",
        }
        model = LocalConfigVersionModel(**data)
        assert model.md5 is None

    def test_missing_required_field(self):
        """Test that missing required fields raise ValidationError."""
        data = {
            "id": 1,
            "serial": "007951000123456",
        }
        with pytest.raises(ValidationError):
            LocalConfigVersionModel(**data)

    def test_timestamp_parsing(self):
        """Test that timestamp string is stored correctly."""
        data = {
            "id": 1,
            "serial": "007951000123456",
            "local_version": "1.0.0",
            "timestamp": "2025-01-15T10:30:00Z",
            "xfmed_version": "1.0.0-transformed",
        }
        model = LocalConfigVersionModel(**data)
        assert model.timestamp is not None
