# tests/test_version.py

import pytest
from device_certificate_report.components.version import parse_version, Version

def test_parse_version():
    version_str = "10.2.3-h4"
    version = parse_version(version_str)
    assert version.major == 10
    assert version.feature == 2
    assert version.maintenance == 3
    assert version.hotfix == 4

def test_parse_version_no_hotfix():
    version_str = "9.1.13"
    version = parse_version(version_str)
    assert version.major == 9
    assert version.feature == 1
    assert version.maintenance == 13
    assert version.hotfix == 0

def test_version_comparison():
    v1 = Version(10, 1, 6, 8)
    v2 = Version(10, 1, 7, 1)
    assert v1 < v2

def test_invalid_version():
    with pytest.raises(ValueError):
        parse_version("invalid-version")