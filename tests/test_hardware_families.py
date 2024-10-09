# tests/test_hardware_families.py

from device_certificate_report.utilities.filters import (
    is_affected_model,
    is_unaffected_model,
)


def test_is_affected_model():
    assert is_affected_model("PA-220")
    assert is_affected_model("PA-3020")
    assert not is_affected_model("PA-460")


def test_is_unaffected_model():
    assert is_unaffected_model("PA-460")
    assert is_unaffected_model("PA-1410")
    assert not is_unaffected_model("PA-220")
