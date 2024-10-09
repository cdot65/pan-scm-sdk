# tests/test_panos_versions.py

from device_certificate_report.utilities.filters import is_version_affected


def test_is_version_affected():
    affected, min_version = is_version_affected("9.1.10")
    assert affected
    assert min_version == "9.1.11-h5"


def test_is_version_not_affected():
    affected, min_version = is_version_affected("10.2.12-h6")
    assert not affected
    assert min_version == ""


def test_is_version_affected_with_globalprotect():
    affected, min_version = is_version_affected("10.2.2-h3", is_global_protect=True)
    assert affected
    assert min_version == "10.2.2-h5"


def test_is_version_not_affected_with_globalprotect():
    affected, min_version = is_version_affected("11.2.0", is_global_protect=True)
    assert not affected
    assert min_version == ""
