# tests/conftest.py

import pytest
from tests.factories import DeviceInfoFactory

@pytest.fixture
def sample_device():
    return DeviceInfoFactory()