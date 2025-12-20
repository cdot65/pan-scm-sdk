# tests/scm/models/objects/test_hip_object_models.py

"""Tests for HIP object models."""

import pytest
from pydantic import ValidationError

from scm.models.objects.hip_object import (
    HIPObjectCreateModel,
    HIPObjectResponseModel,
    HIPObjectUpdateModel,
)
from tests.factories.objects.hip_object import (
    HIPObjectCreateModelFactory,
    HIPObjectResponseModelFactory,
    HIPObjectUpdateModelFactory,
)


class TestHIPObjectCreateModel:
    """Tests for HIPObjectCreateModel validation."""

    def test_valid_create_with_host_info(self):
        """Test valid creation with host info."""
        data = HIPObjectCreateModelFactory.build_valid_host_info()
        model = HIPObjectCreateModel(**data)
        assert model.name == data["name"]
        assert model.folder == data["folder"]
        assert model.host_info is not None

    def test_valid_create_with_network_info(self):
        """Test valid creation with network info."""
        data = HIPObjectCreateModelFactory.build_valid_network_info()
        model = HIPObjectCreateModel(**data)
        assert model.name == data["name"]
        assert model.network_info is not None

    def test_valid_create_with_disk_encryption(self):
        """Test valid creation with disk encryption."""
        data = HIPObjectCreateModelFactory.build_valid_disk_encryption()
        model = HIPObjectCreateModel(**data)
        assert model.name == data["name"]
        assert model.disk_encryption is not None

    def test_valid_create_with_mobile_device(self):
        """Test valid creation with mobile device."""
        data = HIPObjectCreateModelFactory.build_valid_mobile_device()
        model = HIPObjectCreateModel(**data)
        assert model.name == data["name"]
        assert model.mobile_device is not None

    def test_valid_create_with_certificate(self):
        """Test valid creation with certificate."""
        data = HIPObjectCreateModelFactory.build_valid_certificate()
        model = HIPObjectCreateModel(**data)
        assert model.name == data["name"]
        assert model.certificate is not None

    def test_no_container_provided(self):
        """Test validation error when no container is provided."""
        data = HIPObjectCreateModelFactory.build_with_no_containers()
        with pytest.raises(ValueError) as exc_info:
            HIPObjectCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_multiple_containers_provided(self):
        """Test validation error when multiple containers are provided."""
        data = HIPObjectCreateModelFactory.build_with_multiple_containers()
        with pytest.raises(ValueError) as exc_info:
            HIPObjectCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )


class TestHIPObjectUpdateModel:
    """Tests for HIPObjectUpdateModel validation."""

    def test_valid_update(self):
        """Test valid update model creation."""
        data = HIPObjectUpdateModelFactory.build_valid()
        model = HIPObjectUpdateModel(**data)
        assert model.name == data["name"]
        assert model.folder == data["folder"]
        assert str(model.id) == data["id"]

    def test_update_without_id(self):
        """Test update model can be created without id."""
        data = HIPObjectUpdateModelFactory.build_without_id()
        model = HIPObjectUpdateModel(**data)
        assert model.id is None
        assert model.name == data["name"]


class TestHIPObjectResponseModel:
    """Tests for HIPObjectResponseModel validation."""

    def test_valid_response(self):
        """Test valid response model creation."""
        data = HIPObjectResponseModelFactory.build_valid()
        model = HIPObjectResponseModel(**data)
        assert model.name == data["name"]
        assert str(model.id) == data["id"]
        assert model.folder == data["folder"]

    def test_response_requires_id(self):
        """Test that response model requires id."""
        data = {
            "name": "test-hip",
            "folder": "Shared",
        }
        with pytest.raises(ValidationError) as exc_info:
            HIPObjectResponseModel(**data)
        assert "id" in str(exc_info.value)
        assert "Field required" in str(exc_info.value)


class TestExtraFieldsForbidden:
    """Test that extra fields are rejected by all models."""

    def test_hip_object_create_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected in HIPObjectCreateModel."""
        data = HIPObjectCreateModelFactory.build_valid_host_info()
        data["unknown_field"] = "should fail"
        with pytest.raises(ValidationError) as exc_info:
            HIPObjectCreateModel(**data)
        assert "extra" in str(exc_info.value).lower()

    def test_hip_object_update_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected in HIPObjectUpdateModel."""
        data = HIPObjectUpdateModelFactory.build_valid()
        data["unknown_field"] = "should fail"
        with pytest.raises(ValidationError) as exc_info:
            HIPObjectUpdateModel(**data)
        assert "extra" in str(exc_info.value).lower()

    def test_hip_object_response_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected in HIPObjectResponseModel."""
        data = HIPObjectResponseModelFactory.build_valid()
        data["unknown_field"] = "should fail"
        with pytest.raises(ValidationError) as exc_info:
            HIPObjectResponseModel(**data)
        assert "extra" in str(exc_info.value).lower()
