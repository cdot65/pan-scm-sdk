# tests/test_pdf_generation.py

from device_certificate_report.utilities.pdf_generation import generate_report
from tests.factories import DeviceInfoFactory
import os

def test_generate_report(tmp_path):
    device1 = DeviceInfoFactory()
    device2 = DeviceInfoFactory(
        device_name="device2",
        model="PA-460",
        software_version="10.1.0",
    )

    unaffected_devices = [device2]
    no_upgrade_required = []
    upgrade_required = [device1]
    devices_with_globalprotect = []
    devices_with_certificates = []

    output_file = tmp_path / "report.pdf"
    generate_report(
        unaffected_devices=unaffected_devices,
        no_upgrade_required=no_upgrade_required,
        upgrade_required=upgrade_required,
        devices_with_globalprotect=devices_with_globalprotect,
        devices_with_certificates=devices_with_certificates,
        output_file=str(output_file),
    )

    assert os.path.exists(output_file)
    assert os.path.getsize(output_file) > 0