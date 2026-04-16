"""Tests for local config version models."""

import pytest
from pydantic import ValidationError

from scm.models.operations.local_config import LocalConfigVersionModel


class TestLocalConfigVersionModel:
    """Tests for LocalConfigVersionModel."""

    def test_valid_model(self):
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
        data = {
            "id": 1,
            "serial": "007951000123456",
        }
        with pytest.raises(ValidationError):
            LocalConfigVersionModel(**data)

    def test_timestamp_parsing(self):
        data = {
            "id": 1,
            "serial": "007951000123456",
            "local_version": "1.0.0",
            "timestamp": "2025-01-15T10:30:00Z",
            "xfmed_version": "1.0.0-transformed",
        }
        model = LocalConfigVersionModel(**data)
        assert model.timestamp is not None
