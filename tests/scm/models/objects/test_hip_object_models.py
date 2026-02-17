# tests/scm/models/objects/test_hip_object_models.py

"""Tests for HIP object models."""

from pydantic import ValidationError
import pytest

from scm.models.objects.hip_object import (
    CustomChecksModel,
    HIPObjectCreateModel,
    HIPObjectResponseModel,
    HIPObjectUpdateModel,
    PlistKeyModel,
    PlistModel,
    ProcessListItemModel,
    RegistryKeyModel,
    RegistryValueModel,
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

    def test_valid_create_with_custom_checks(self):
        """Test valid creation with custom checks."""
        data = HIPObjectCreateModelFactory.build_valid_custom_checks()
        model = HIPObjectCreateModel(**data)
        assert model.name == data["name"]
        assert model.custom_checks is not None
        assert model.custom_checks.criteria.registry_key is not None

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

    def test_hip_object_response_model_extra_fields_ignored(self):
        """Test that extra fields are silently ignored in HIPObjectResponseModel."""
        data = HIPObjectResponseModelFactory.build_valid()
        data["unknown_field"] = "should be ignored"
        model = HIPObjectResponseModel(**data)
        assert not hasattr(model, "unknown_field")


class TestProcessListItemModel:
    """Tests for ProcessListItemModel validation."""

    def test_valid_process_list_item(self):
        """Test valid process list item creation."""
        model = ProcessListItemModel(name="notepad.exe", running=True)
        assert model.name == "notepad.exe"
        assert model.running is True

    def test_process_list_item_default_running(self):
        """Test that running defaults to True."""
        model = ProcessListItemModel(name="process.exe")
        assert model.running is True

    def test_process_list_item_running_false(self):
        """Test process list item with running=False."""
        model = ProcessListItemModel(name="process.exe", running=False)
        assert model.running is False

    def test_process_list_item_name_required(self):
        """Test that name is required."""
        with pytest.raises(ValidationError) as exc_info:
            ProcessListItemModel()
        assert "name" in str(exc_info.value)

    def test_process_list_item_name_max_length(self):
        """Test name max length constraint."""
        with pytest.raises(ValidationError) as exc_info:
            ProcessListItemModel(name="x" * 1024)
        assert "String should have at most 1023 characters" in str(exc_info.value)


class TestRegistryValueModel:
    """Tests for RegistryValueModel validation."""

    def test_valid_registry_value(self):
        """Test valid registry value creation."""
        model = RegistryValueModel(name="Version", value_data="1.0.0")
        assert model.name == "Version"
        assert model.value_data == "1.0.0"
        assert model.negate is False

    def test_registry_value_negate_default(self):
        """Test that negate defaults to False."""
        model = RegistryValueModel(name="TestValue")
        assert model.negate is False

    def test_registry_value_name_required(self):
        """Test that name is required."""
        with pytest.raises(ValidationError) as exc_info:
            RegistryValueModel()
        assert "name" in str(exc_info.value)

    def test_registry_value_max_lengths(self):
        """Test max length constraints."""
        with pytest.raises(ValidationError) as exc_info:
            RegistryValueModel(name="x" * 1024)
        assert "String should have at most 1023 characters" in str(exc_info.value)


class TestRegistryKeyModel:
    """Tests for RegistryKeyModel validation."""

    def test_valid_registry_key(self):
        """Test valid registry key creation."""
        model = RegistryKeyModel(name="HKEY_LOCAL_MACHINE\\SOFTWARE\\TestApp")
        assert model.name == "HKEY_LOCAL_MACHINE\\SOFTWARE\\TestApp"
        assert model.negate is False

    def test_registry_key_with_values(self):
        """Test registry key with registry values."""
        model = RegistryKeyModel(
            name="HKEY_LOCAL_MACHINE\\SOFTWARE\\TestApp",
            registry_value=[
                RegistryValueModel(name="Version", value_data="1.0.0"),
                RegistryValueModel(name="InstallPath", value_data="C:\\Program Files"),
            ],
        )
        assert len(model.registry_value) == 2
        assert model.registry_value[0].name == "Version"

    def test_registry_key_name_required(self):
        """Test that name is required."""
        with pytest.raises(ValidationError) as exc_info:
            RegistryKeyModel()
        assert "name" in str(exc_info.value)


class TestPlistKeyModel:
    """Tests for PlistKeyModel validation."""

    def test_valid_plist_key(self):
        """Test valid plist key creation."""
        model = PlistKeyModel(name="CFBundleVersion", value="1.0")
        assert model.name == "CFBundleVersion"
        assert model.value == "1.0"
        assert model.negate is False

    def test_plist_key_negate_default(self):
        """Test that negate defaults to False."""
        model = PlistKeyModel(name="TestKey")
        assert model.negate is False

    def test_plist_key_name_required(self):
        """Test that name is required."""
        with pytest.raises(ValidationError) as exc_info:
            PlistKeyModel()
        assert "name" in str(exc_info.value)


class TestPlistModel:
    """Tests for PlistModel validation."""

    def test_valid_plist(self):
        """Test valid plist creation."""
        model = PlistModel(name="com.apple.finder")
        assert model.name == "com.apple.finder"
        assert model.negate is False

    def test_plist_with_keys(self):
        """Test plist with keys."""
        model = PlistModel(
            name="com.apple.finder",
            key=[
                PlistKeyModel(name="ShowHardDrivesOnDesktop", value="true"),
            ],
        )
        assert len(model.key) == 1
        assert model.key[0].name == "ShowHardDrivesOnDesktop"

    def test_plist_name_required(self):
        """Test that name is required."""
        with pytest.raises(ValidationError) as exc_info:
            PlistModel()
        assert "name" in str(exc_info.value)


class TestCustomChecksModel:
    """Tests for CustomChecksModel validation."""

    def test_valid_custom_checks_with_process_list(self):
        """Test valid custom checks with process list."""
        model = CustomChecksModel(
            criteria={
                "process_list": [
                    {"name": "notepad.exe", "running": True},
                ]
            }
        )
        assert len(model.criteria.process_list) == 1

    def test_valid_custom_checks_with_registry_keys(self):
        """Test valid custom checks with registry keys."""
        model = CustomChecksModel(
            criteria={
                "registry_key": [
                    {
                        "name": "HKEY_LOCAL_MACHINE\\SOFTWARE\\TestApp",
                        "registry_value": [{"name": "Version", "value_data": "1.0.0"}],
                    }
                ]
            }
        )
        assert len(model.criteria.registry_key) == 1
        assert model.criteria.registry_key[0].name == "HKEY_LOCAL_MACHINE\\SOFTWARE\\TestApp"

    def test_valid_custom_checks_with_plist(self):
        """Test valid custom checks with plist."""
        model = CustomChecksModel(
            criteria={
                "plist": [
                    {
                        "name": "com.apple.finder",
                        "key": [{"name": "ShowHardDrivesOnDesktop", "value": "true"}],
                    }
                ]
            }
        )
        assert len(model.criteria.plist) == 1

    def test_custom_checks_criteria_required(self):
        """Test that criteria is required."""
        with pytest.raises(ValidationError) as exc_info:
            CustomChecksModel()
        assert "criteria" in str(exc_info.value)

    def test_custom_checks_empty_criteria(self):
        """Test custom checks with empty criteria."""
        model = CustomChecksModel(criteria={})
        assert model.criteria.process_list is None
        assert model.criteria.registry_key is None
        assert model.criteria.plist is None


class TestHIPObjectWithCustomChecks:
    """Tests for HIP Object models with custom checks."""

    def test_response_model_with_custom_checks(self):
        """Test response model with custom checks."""
        data = HIPObjectResponseModelFactory.build_valid_custom_checks()
        model = HIPObjectResponseModel(**data)
        assert model.custom_checks is not None
        assert model.custom_checks.criteria.registry_key is not None
