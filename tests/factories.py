# tests/factories.py

import factory
from device_certificate_report.models.device import DeviceInfo

class DeviceInfoFactory(factory.Factory):
    class Meta:
        model = DeviceInfo

    device_name = factory.Sequence(lambda n: f"device{n}")
    model = "PA-220"
    serial_number = factory.Sequence(lambda n: f"serial{n}")
    ipv4_address = factory.Sequence(lambda n: f"192.168.1.{n}")
    device_state = "Connected"
    device_certificate = "Valid"
    device_certificate_expiry_date = "2024-12-31"
    software_version = "10.0.0"
    globalprotect_client = "5.2.6"
    min_required_version = None
    notes = None