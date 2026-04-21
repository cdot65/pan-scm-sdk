"""Pytest suite for Device Pydantic models."""

from pydantic import ValidationError
import pytest

from scm.models.setup.device import (
    DeviceBaseModel,
    DeviceCreateModel,
    DeviceLicenseModel,
    DeviceListResponseModel,
    DeviceResponseModel,
    DeviceUpdateModel,
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

    def test_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        data = DeviceLicenseDictFactory.build()
        data["unknown_field"] = "should_fail"
        with pytest.raises(ValidationError) as exc_info:
            DeviceLicenseModel.model_validate(data)
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestDeviceBaseModel:
    """Tests for device base model validation."""

    def test_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        data = {"name": "test-device", "unknown_field": "should_fail"}
        with pytest.raises(ValidationError) as exc_info:
            DeviceBaseModel.model_validate(data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_create_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on CreateModel."""
        data = {"name": "test-device", "unknown_field": "should_fail"}
        with pytest.raises(ValidationError) as exc_info:
            DeviceCreateModel.model_validate(data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_update_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on UpdateModel."""
        data = {"id": "123456", "name": "test-device", "unknown_field": "should_fail"}
        with pytest.raises(ValidationError) as exc_info:
            DeviceUpdateModel.model_validate(data)
        assert "Extra inputs are not permitted" in str(exc_info.value)


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

    def test_extra_fields_allowed(self):
        """Test that extra fields are allowed on ResponseModel (API compatibility)."""
        data = {"id": "123456789012345", "future_api_field": "should_work"}
        model = DeviceResponseModel.model_validate(data)
        assert model.id == "123456789012345"
        # Extra field should be accessible via model_extra or __pydantic_extra__
        assert hasattr(model, "__pydantic_extra__")


class TestDeviceBaseModelLabelsAndSnippets:
    """Labels and snippets are writable metadata per the devices-put schema."""

    def test_labels_accepted_on_base(self):
        """DeviceBaseModel accepts a labels list."""
        model = DeviceBaseModel.model_validate({"name": "d", "labels": ["prod", "east"]})
        assert model.labels == ["prod", "east"]

    def test_snippets_accepted_on_base(self):
        """DeviceBaseModel accepts a snippets list."""
        model = DeviceBaseModel.model_validate({"name": "d", "snippets": ["s1", "s2"]})
        assert model.snippets == ["s1", "s2"]

    def test_labels_default_none(self):
        """Labels default to None when omitted."""
        model = DeviceBaseModel.model_validate({"name": "d"})
        assert model.labels is None
        assert model.snippets is None


class TestDeviceUpdateModel:
    """DeviceUpdateModel must match the devices-put OpenAPI schema exactly."""

    def test_minimal_valid_payload(self):
        """Id alone is a valid payload (all writable fields are optional)."""
        model = DeviceUpdateModel.model_validate({"id": "abc-123"})
        assert model.id == "abc-123"

    def test_all_writable_fields(self):
        """Accept all five writable fields plus id."""
        data = {
            "id": "abc-123",
            "display_name": "edge-1",
            "folder": "Prod",
            "description": "Edge firewall",
            "labels": ["prod", "east"],
            "snippets": ["baseline"],
        }
        model = DeviceUpdateModel.model_validate(data)
        assert model.labels == ["prod", "east"]
        assert model.snippets == ["baseline"]
        assert model.folder == "Prod"

    def test_id_required(self):
        """Omitting id is a validation error."""
        with pytest.raises(ValidationError):
            DeviceUpdateModel.model_validate({"folder": "Prod"})

    @pytest.mark.parametrize(
        "field",
        ["serial_number", "hostname", "family", "model", "is_connected", "name", "type"],
    )
    def test_non_writable_fields_rejected(self, field):
        """Fields not in devices-put must be rejected by the update model."""
        data = {"id": "abc-123", field: "whatever"}
        with pytest.raises(ValidationError) as exc_info:
            DeviceUpdateModel.model_validate(data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_payload_excludes_unset(self):
        """model_dump(exclude_unset=True) omits fields not provided."""
        model = DeviceUpdateModel.model_validate({"id": "abc", "labels": ["x"]})
        payload = model.model_dump(exclude_unset=True)
        assert payload == {"id": "abc", "labels": ["x"]}


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

    def test_extra_fields_allowed(self):
        """Test that extra fields are allowed on DeviceListResponseModel (API compatibility)."""
        data = DeviceListResponseModelDictFactory.build()
        data["unknown_field"] = "should_be_allowed"
        model = DeviceListResponseModel.model_validate(data)
        assert hasattr(model, "__pydantic_extra__")
