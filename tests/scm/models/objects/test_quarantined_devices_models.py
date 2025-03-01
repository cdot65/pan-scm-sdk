# tests/scm/models/objects/test_quarantined_devices_models.py

# Standard library imports
import pytest
from uuid import UUID

# Local SDK imports
from scm.models.objects.quarantined_devices import QuarantinedDevicesBaseModel
from scm.models.objects import (
    QuarantinedDevicesCreateModel,
    QuarantinedDevicesResponseModel,
    QuarantinedDevicesListParamsModel,
)


class TestQuarantinedDevicesBaseModel:
    """
    Tests for QuarantinedDevicesBaseModel.
    """

    def test_valid_model(self):
        """Test with valid required fields."""
        model = QuarantinedDevicesBaseModel(host_id="test-host-id")
        assert model.host_id == "test-host-id"
        assert model.serial_number is None

    def test_model_with_all_fields(self):
        """Test with all fields provided."""
        model = QuarantinedDevicesBaseModel(
            host_id="test-host-id",
            serial_number="test-serial-number",
        )
        assert model.host_id == "test-host-id"
        assert model.serial_number == "test-serial-number"

    def test_model_missing_required_fields(self):
        """Test that missing required fields raises validation error."""
        with pytest.raises(ValueError) as excinfo:
            QuarantinedDevicesBaseModel()
        assert "host_id" in str(excinfo.value), "Should error on missing host_id"


class TestQuarantinedDevicesCreateModel:
    """
    Tests for QuarantinedDevicesCreateModel.
    """

    def test_valid_model(self):
        """Test with valid required fields."""
        model = QuarantinedDevicesCreateModel(host_id="test-host-id")
        assert model.host_id == "test-host-id"
        assert model.serial_number is None

    def test_model_with_all_fields(self):
        """Test with all fields provided."""
        model = QuarantinedDevicesCreateModel(
            host_id="test-host-id",
            serial_number="test-serial-number",
        )
        assert model.host_id == "test-host-id"
        assert model.serial_number == "test-serial-number"

    def test_model_missing_required_fields(self):
        """Test that missing required fields raises validation error."""
        with pytest.raises(ValueError) as excinfo:
            QuarantinedDevicesCreateModel()
        assert "host_id" in str(excinfo.value), "Should error on missing host_id"


class TestQuarantinedDevicesResponseModel:
    """
    Tests for QuarantinedDevicesResponseModel.
    """

    def test_valid_model(self):
        """Test with valid required fields."""
        model = QuarantinedDevicesResponseModel(host_id="test-host-id")
        assert model.host_id == "test-host-id"
        assert model.serial_number is None

    def test_model_with_all_fields(self):
        """Test with all fields provided."""
        model = QuarantinedDevicesResponseModel(
            host_id="test-host-id",
            serial_number="test-serial-number",
        )
        assert model.host_id == "test-host-id"
        assert model.serial_number == "test-serial-number"

    def test_model_missing_required_fields(self):
        """Test that missing required fields raises validation error."""
        with pytest.raises(ValueError) as excinfo:
            QuarantinedDevicesResponseModel()
        assert "host_id" in str(excinfo.value), "Should error on missing host_id"


class TestQuarantinedDevicesListParamsModel:
    """
    Tests for QuarantinedDevicesListParamsModel.
    """

    def test_empty_model(self):
        """Test with no fields provided."""
        model = QuarantinedDevicesListParamsModel()
        assert model.host_id is None
        assert model.serial_number is None

    def test_model_with_host_id(self):
        """Test with only host_id provided."""
        model = QuarantinedDevicesListParamsModel(host_id="test-host-id")
        assert model.host_id == "test-host-id"
        assert model.serial_number is None

    def test_model_with_serial_number(self):
        """Test with only serial_number provided."""
        model = QuarantinedDevicesListParamsModel(serial_number="test-serial-number")
        assert model.host_id is None
        assert model.serial_number == "test-serial-number"

    def test_model_with_all_fields(self):
        """Test with all fields provided."""
        model = QuarantinedDevicesListParamsModel(
            host_id="test-host-id",
            serial_number="test-serial-number",
        )
        assert model.host_id == "test-host-id"
        assert model.serial_number == "test-serial-number"