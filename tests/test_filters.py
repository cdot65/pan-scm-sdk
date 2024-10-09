# tests/test_filters.py

from device_certificate_report.utilities.filters import (
    filter_devices_by_model,
    split_devices_by_version,
)
from tests.factories import DeviceInfoFactory

def test_filter_devices_by_model():
    device1 = DeviceInfoFactory(model="PA-220")
    device2 = DeviceInfoFactory(device_name="device2", model="PA-460")
    device3 = DeviceInfoFactory(device_name="device3", model="UnknownModel")

    devices = [device1, device2, device3]
    affected, unaffected = filter_devices_by_model(devices)
    assert len(affected) == 1
    assert len(unaffected) == 2
    assert affected[0].device_name == device1.device_name
    assert unaffected[0].device_name == device2.device_name
    assert unaffected[1].notes == "Model not recognized; considered unaffected."

def test_split_devices_by_version():
    device1 = DeviceInfoFactory(software_version="9.1.10")
    device2 = DeviceInfoFactory(device_name="device2", software_version="10.2.12-h12")
    device3 = DeviceInfoFactory(device_name="device3", software_version="11.2.0")

    devices = [device1, device2, device3]
    no_upgrade_required, upgrade_required = split_devices_by_version(devices)
    assert len(no_upgrade_required) == 2
    assert len(upgrade_required) == 1
    assert upgrade_required[0].device_name == device1.device_name
    assert upgrade_required[0].min_required_version == "9.1.11-h5"