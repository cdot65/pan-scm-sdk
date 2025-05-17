# tests/scm/models/objects/test_quarantined_devices_models.py

# Standard library imports
import pytest

from scm.models.objects import (
    QuarantinedDevicesCreateModel,
    QuarantinedDevicesResponseModel,
)

# Local SDK imports
from scm.models.objects.quarantined_devices import QuarantinedDevicesBaseModel
from tests.factories.objects.quarantined_devices import (
    QuarantinedDevicesBaseFactory,
    QuarantinedDevicesCreateFactory,
    QuarantinedDevicesListParamsFactory,
    QuarantinedDevicesResponseFactory,
)


class TestQuarantinedDevicesBaseModel:
    """Tests for QuarantinedDevicesBaseModel.
    """

    def test_valid_model(self):
        """Test with valid required fields."""
        model = QuarantinedDevicesBaseFactory.build(serial_number=None)
        assert model.host_id is not None
        assert model.serial_number is None

    def test_model_with_all_fields(self):
        """Test with all fields provided."""
        model = QuarantinedDevicesBaseFactory.build()
        assert model.host_id is not None
        assert model.serial_number is not None

    def test_model_missing_required_fields(self):
        """Test that missing required fields raises validation error."""
        with pytest.raises(ValueError) as excinfo:
            QuarantinedDevicesBaseModel()
        assert "host_id" in str(excinfo.value), "Should error on missing host_id"


class TestQuarantinedDevicesCreateModel:
    """Tests for QuarantinedDevicesCreateModel.
    """

    def test_valid_model(self):
        """Test with valid required fields."""
        model = QuarantinedDevicesCreateFactory.build(serial_number=None)
        assert model.host_id is not None
        assert model.serial_number is None

    def test_model_with_all_fields(self):
        """Test with all fields provided."""
        model = QuarantinedDevicesCreateFactory.build()
        assert model.host_id is not None
        assert model.serial_number is not None

    def test_model_missing_required_fields(self):
        """Test that missing required fields raises validation error."""
        with pytest.raises(ValueError) as excinfo:
            QuarantinedDevicesCreateModel()
        assert "host_id" in str(excinfo.value), "Should error on missing host_id"


class TestQuarantinedDevicesResponseModel:
    """Tests for QuarantinedDevicesResponseModel.
    """

    def test_valid_model(self):
        """Test with valid required fields."""
        model = QuarantinedDevicesResponseFactory.build(serial_number=None)
        assert model.host_id is not None
        assert model.serial_number is None

    def test_model_with_all_fields(self):
        """Test with all fields provided."""
        model = QuarantinedDevicesResponseFactory.build()
        assert model.host_id is not None
        assert model.serial_number is not None

    def test_model_missing_required_fields(self):
        """Test that missing required fields raises validation error."""
        with pytest.raises(ValueError) as excinfo:
            QuarantinedDevicesResponseModel()
        assert "host_id" in str(excinfo.value), "Should error on missing host_id"


class TestQuarantinedDevicesListParamsModel:
    """Tests for QuarantinedDevicesListParamsModel.
    """

    def test_empty_model(self):
        """Test with no fields provided."""
        model = QuarantinedDevicesListParamsFactory.build()
        assert model.host_id is None
        assert model.serial_number is None

    def test_model_with_host_id(self):
        """Test with only host_id provided."""
        model = QuarantinedDevicesListParamsFactory.with_host_id("test-host")
        assert model.host_id == "test-host"
        assert model.serial_number is None

    def test_model_with_serial_number(self):
        """Test with only serial_number provided."""
        model = QuarantinedDevicesListParamsFactory.with_serial_number("test-serial")
        assert model.host_id is None
        assert model.serial_number == "test-serial"

    def test_model_with_all_fields(self):
        """Test with all fields provided."""
        model = QuarantinedDevicesListParamsFactory.with_all_filters(
            host_id="test-host", serial_number="test-serial"
        )
        assert model.host_id == "test-host"
        assert model.serial_number == "test-serial"
