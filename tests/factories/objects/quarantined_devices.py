# tests/factories/objects/quarantined_devices.py

# Standard library imports
from typing import Any, Dict

# External libraries
import factory  # type: ignore

# Local SDK imports
from scm.models.objects import (
    QuarantinedDevicesCreateModel,
    QuarantinedDevicesListParamsModel,
    QuarantinedDevicesResponseModel,
)
from scm.models.objects.quarantined_devices import QuarantinedDevicesBaseModel


# ----------------------------------------------------------------------------
# QuarantinedDevicesBaseFactory
# ----------------------------------------------------------------------------
class QuarantinedDevicesBaseFactory(factory.Factory):
    """Base factory for QuarantinedDevices model objects."""

    class Meta:
        """Factory configuration."""

        model = QuarantinedDevicesBaseModel

    host_id = factory.Sequence(lambda n: f"host-{n}")
    serial_number = factory.Sequence(lambda n: f"serial-{n}")

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override _create to force evaluation of Sequence attributes."""
        for key, value in list(kwargs.items()):
            if isinstance(value, factory.declarations.Sequence):
                kwargs[key] = value.evaluate(0, kwargs)
        return super()._create(model_class, *args, **kwargs)


# ----------------------------------------------------------------------------
# QuarantinedDevicesCreateFactory
# ----------------------------------------------------------------------------
class QuarantinedDevicesCreateFactory(QuarantinedDevicesBaseFactory):
    """Factory for creating QuarantinedDevicesCreateModel instances."""

    class Meta:
        """Factory configuration."""

        model = QuarantinedDevicesCreateModel


# ----------------------------------------------------------------------------
# QuarantinedDevicesResponseFactory
# ----------------------------------------------------------------------------
class QuarantinedDevicesResponseFactory(QuarantinedDevicesBaseFactory):
    """Factory for creating QuarantinedDevicesResponseModel instances."""

    class Meta:
        """Factory configuration."""

        model = QuarantinedDevicesResponseModel


# ----------------------------------------------------------------------------
# QuarantinedDevicesListParamsFactory
# ----------------------------------------------------------------------------
class QuarantinedDevicesListParamsFactory(factory.Factory):
    """Factory for creating QuarantinedDevicesListParamsModel instances."""

    class Meta:
        """Factory configuration."""

        model = QuarantinedDevicesListParamsModel

    host_id = None
    serial_number = None

    @classmethod
    def with_host_id(
        cls, host_id: str = "test-host-id", **kwargs
    ) -> QuarantinedDevicesListParamsModel:
        """Create a list params model with host_id filter."""
        return cls(host_id=host_id, **kwargs)

    @classmethod
    def with_serial_number(
        cls, serial_number: str = "test-serial", **kwargs
    ) -> QuarantinedDevicesListParamsModel:
        """Create a list params model with serial_number filter."""
        return cls(serial_number=serial_number, **kwargs)

    @classmethod
    def with_all_filters(
        cls, host_id: str = "test-host-id", serial_number: str = "test-serial", **kwargs
    ) -> QuarantinedDevicesListParamsModel:
        """Create a list params model with all filters."""
        return cls(host_id=host_id, serial_number=serial_number, **kwargs)


# ----------------------------------------------------------------------------
# QuarantinedDevicesCreateApiFactory
# ----------------------------------------------------------------------------
class QuarantinedDevicesCreateApiFactory:
    """Factory for creating dictionary data for QuarantinedDevicesCreateModel API requests."""

    @classmethod
    def build(cls, **kwargs) -> Dict[str, Any]:
        """Build a dictionary for a QuarantinedDevicesCreateModel API request."""
        host_id = kwargs.get("host_id", f"host-{0}")
        data = {
            "host_id": host_id,
        }

        # Add optional serial_number if provided
        if "serial_number" in kwargs:
            data["serial_number"] = kwargs["serial_number"]

        return data

    @classmethod
    def build_minimal(cls) -> Dict[str, Any]:
        """Build a dictionary with minimal required fields."""
        return {"host_id": f"host-{0}"}

    @classmethod
    def build_complete(cls) -> Dict[str, Any]:
        """Build a dictionary with all fields."""
        return {
            "host_id": f"host-{0}",
            "serial_number": f"serial-{0}",
        }
