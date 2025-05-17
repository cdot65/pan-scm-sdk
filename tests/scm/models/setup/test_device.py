"""Pytest suite for Device Pydantic models."""

from pydantic import ValidationError
import pytest

from scm.models.setup.device import (
    DeviceLicenseModel,
    DeviceListResponseModel,
    DeviceResponseModel,
)
from tests.factories.setup.device import (
    DeviceLicenseDictFactory,
    DeviceListResponseModelDictFactory,
    DeviceResponseDictFactory,
)


class TestDeviceLicenseModel:
    """Tests for device license model validation."""

    def test_valid_construction(self):
        """Test valid construction of DeviceLicenseModel."""
        data = DeviceLicenseDictFactory.build()
        model = DeviceLicenseModel.model_validate(data)
        assert model.feature == data["feature"]
        assert model.expires == data["expires"]
        assert model.issued == data["issued"]

    def test_missing_required_field(self):
        """Test validation error when required field is missing."""
        data = DeviceLicenseDictFactory.build()
        data.pop("feature")
        with pytest.raises(ValidationError):
            DeviceLicenseModel.model_validate(data)

    def test_optional_fields(self):
        """Test that optional fields can be omitted."""
        data = DeviceLicenseDictFactory.build()
        data.pop("authcode", None)
        data.pop("expired", None)
        model = DeviceLicenseModel.model_validate(data)
        assert model.authcode is None or isinstance(model.authcode, str)
        assert model.expired is None or isinstance(model.expired, str)


class TestDeviceResponseModel:
    """Tests for device response model validation."""

    def test_valid_construction(self):
        """Test valid construction of DeviceResponseModel."""
        data = DeviceResponseDictFactory.build()
        model = DeviceResponseModel.model_validate(data)
        assert model.id == data["id"]
        assert isinstance(model.available_licenses, list)
        assert isinstance(model.installed_licenses, list)
        assert model.name == data["name"]

    def test_minimal_construction(self):
        """Test construction with only required fields."""
        # Only required field 'id'
        data = {"id": "123456789012345"}
        model = DeviceResponseModel.model_validate(data)
        assert model.id == "123456789012345"
        # All other fields should be None or default
        for field in DeviceResponseModel.model_fields:
            if field != "id":
                assert getattr(model, field) is None or isinstance(
                    getattr(model, field), (str, bool, int, list, type(None))
                )

    def test_missing_required_field(self):
        """Test validation error when required field is missing."""
        data = DeviceResponseDictFactory.build()
        data.pop("id")
        with pytest.raises(ValidationError):
            DeviceResponseModel.model_validate(data)

    def test_nested_license_validation(self):
        """Test validation of nested license objects."""
        data = DeviceResponseDictFactory.build()
        # Corrupt a nested license entry
        data["availableLicenses"][0].pop("feature")
        with pytest.raises(ValidationError):
            DeviceResponseModel.model_validate(data)


class TestDeviceListResponseModel:
    """Tests for device list response model validation."""

    def test_valid_construction(self):
        """Test valid construction of DeviceListResponseModel."""
        data = DeviceListResponseModelDictFactory.build()
        model = DeviceListResponseModel.model_validate(data)
        assert isinstance(model.data, list)
        assert isinstance(model.limit, int)
        assert isinstance(model.offset, int)
        assert isinstance(model.total, int)

    def test_missing_required_field(self):
        """Test validation error when required field is missing."""
        data = DeviceListResponseModelDictFactory.build()
        data.pop("data")
        with pytest.raises(ValidationError):
            DeviceListResponseModel.model_validate(data)

    def test_empty_devices(self):
        """Test that empty device list is valid."""
        data = DeviceListResponseModelDictFactory.build()
        data["data"] = []
        model = DeviceListResponseModel.model_validate(data)
        assert model.data == []
        assert isinstance(model.limit, int)
        assert isinstance(model.offset, int)
        assert isinstance(model.total, int)
