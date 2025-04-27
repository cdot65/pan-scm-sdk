"""
Pytest suite for Device Pydantic models.
"""

import pytest
from pydantic import ValidationError

from scm.models.setup.device import DeviceLicenseModel, DeviceModel, DeviceListResponseModel
from tests.factories.setup.device import (
    DeviceLicenseDictFactory,
    DeviceModelDictFactory,
    DeviceListResponseModelDictFactory,
)


class TestDeviceLicenseModel:
    def test_valid_construction(self):
        data = DeviceLicenseDictFactory.build()
        model = DeviceLicenseModel.model_validate(data)
        assert model.feature == data["feature"]
        assert model.expires == data["expires"]
        assert model.issued == data["issued"]

    def test_missing_required_field(self):
        data = DeviceLicenseDictFactory.build()
        data.pop("feature")
        with pytest.raises(ValidationError):
            DeviceLicenseModel.model_validate(data)

    def test_optional_fields(self):
        data = DeviceLicenseDictFactory.build()
        data.pop("authcode", None)
        data.pop("expired", None)
        model = DeviceLicenseModel.model_validate(data)
        assert model.authcode is None or isinstance(model.authcode, str)
        assert model.expired is None or isinstance(model.expired, str)


class TestDeviceModel:
    def test_valid_construction(self):
        data = DeviceModelDictFactory.build()
        model = DeviceModel.model_validate(data)
        assert model.id == data["id"]
        assert isinstance(model.available_licensess, list)
        assert isinstance(model.installed_licenses, list)
        assert model.name == data["name"]

    def test_minimal_construction(self):
        # Only required field 'id'
        data = {"id": "123456789012345"}
        model = DeviceModel.model_validate(data)
        assert model.id == "123456789012345"
        # All other fields should be None or default
        for field in DeviceModel.model_fields:
            if field != "id":
                assert getattr(model, field) is None or isinstance(
                    getattr(model, field), (str, bool, int, list, type(None))
                )

    def test_missing_required_field(self):
        data = DeviceModelDictFactory.build()
        data.pop("id")
        with pytest.raises(ValidationError):
            DeviceModel.model_validate(data)

    def test_nested_license_validation(self):
        data = DeviceModelDictFactory.build()
        # Corrupt a nested license entry
        data["available_licensess"][0].pop("feature")
        with pytest.raises(ValidationError):
            DeviceModel.model_validate(data)


class TestDeviceListResponseModel:
    def test_valid_construction(self):
        data = DeviceListResponseModelDictFactory.build()
        model = DeviceListResponseModel.model_validate(data)
        assert isinstance(model.data, list)
        assert isinstance(model.limit, int)
        assert isinstance(model.offset, int)
        assert isinstance(model.total, int)

    def test_missing_required_field(self):
        data = DeviceListResponseModelDictFactory.build()
        data.pop("data")
        with pytest.raises(ValidationError):
            DeviceListResponseModel.model_validate(data)

    def test_empty_devices(self):
        data = DeviceListResponseModelDictFactory.build()
        data["data"] = []
        model = DeviceListResponseModel.model_validate(data)
        assert model.data == []
        assert isinstance(model.limit, int)
        assert isinstance(model.offset, int)
        assert isinstance(model.total, int)
