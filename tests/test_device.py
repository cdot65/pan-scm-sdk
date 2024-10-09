# tests/test_device.py

from tests.factories import DeviceInfoFactory

def test_device_info_creation():
    device = DeviceInfoFactory()

    assert device.device_name == "device5"
    assert device.model == "PA-220"
    assert device.serial_number == "serial5"
    assert device.ipv4_address == "192.168.1.5"
    assert device.device_state == "Connected"
    assert device.device_certificate == "Valid"
    assert device.device_certificate_expiry_date == "2024-12-31"
    assert device.software_version == "10.0.0"
    assert device.globalprotect_client == "5.2.6"