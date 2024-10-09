# tests/test_data_collection.py

import pytest
from unittest.mock import MagicMock
from device_certificate_report.components.data_collection import (
    process_csv_file,
    collect_data_from_panorama,
    collect_data_from_firewall,
)
from panos.panorama import Panorama
from panos.firewall import Firewall
import xml.etree.ElementTree as ET

from tests.factories import DeviceInfoFactory

def test_process_csv_file(tmp_path):
    # Create sample devices using factories
    device1 = DeviceInfoFactory()
    device2 = DeviceInfoFactory(
        device_name="device2",
        model="PA-3020",
        software_version="9.1.0",
        globalprotect_client=None,
    )

    # Create CSV content from devices
    csv_content = f"""Device Name,IP Address Serial Number,IP Address IPv4,Status Device State,Status Device Certificate,Status Device Certificate Expiry Date,GlobalProtect Client,Model,Software Version
"{device1.device_name}","{device1.serial_number}","{device1.ipv4_address}","{device1.device_state}","{device1.device_certificate}","{device1.device_certificate_expiry_date}","{device1.globalprotect_client or '0.0.0'}","{device1.model}","{device1.software_version}"
"{device2.device_name}","{device2.serial_number}","{device2.ipv4_address}","{device2.device_state}","{device2.device_certificate}","{device2.device_certificate_expiry_date}","{device2.globalprotect_client or '0.0.0'}","{device2.model}","{device2.software_version}"
"""
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(csv_content)

    devices = process_csv_file(str(csv_file))

    assert len(devices) == 2
    assert devices[0].device_name == device1.device_name
    assert devices[0].model == device1.model
    assert devices[0].software_version == device1.software_version
    assert devices[1].device_name == device2.device_name
    assert devices[1].globalprotect_client is None  # Should be None because it's "0.0.0"

def test_collect_data_from_panorama(monkeypatch):
    # Mock Panorama instance
    panorama = Panorama("hostname", "username", "password")

    # Create sample devices using factories
    device1 = DeviceInfoFactory()
    device2 = DeviceInfoFactory(
        device_name="device2",
        model="PA-3020",
        serial_number="serial2",
        ipv4_address="192.168.1.2",
        device_state="Disconnected",
        device_certificate="Invalid",
        device_certificate_expiry_date="2023-11-30",
        software_version="9.1.0",
        globalprotect_client=None,
    )

    # Create XML response using devices
    mock_response = ET.fromstring(f"""
    <response status="success">
        <result>
            <devices>
                <entry>
                    <hostname>{device1.device_name}</hostname>
                    <model>{device1.model}</model>
                    <serial>{device1.serial_number}</serial>
                    <ip-address>{device1.ipv4_address}</ip-address>
                    <connected>{"yes" if device1.device_state == "Connected" else "no"}</connected>
                    <device-cert-present>{device1.device_certificate}</device-cert-present>
                    <device-cert-expiry-date>{device1.device_certificate_expiry_date}</device-cert-expiry-date>
                    <sw-version>{device1.software_version}</sw-version>
                    <global-protect-client-package-version>{device1.globalprotect_client or "0.0.0"}</global-protect-client-package-version>
                </entry>
                <entry>
                    <hostname>{device2.device_name}</hostname>
                    <model>{device2.model}</model>
                    <serial>{device2.serial_number}</serial>
                    <ip-address>{device2.ipv4_address}</ip-address>
                    <connected>{"yes" if device2.device_state == "Connected" else "no"}</connected>
                    <device-cert-present>{device2.device_certificate}</device-cert-present>
                    <device-cert-expiry-date>{device2.device_certificate_expiry_date}</device-cert-expiry-date>
                    <sw-version>{device2.software_version}</sw-version>
                    <global-protect-client-package-version>{device2.globalprotect_client or "0.0.0"}</global-protect-client-package-version>
                </entry>
            </devices>
        </result>
    </response>
    """)

    def mock_op(cmd, cmd_xml=False):
        return mock_response

    monkeypatch.setattr(panorama, "op", mock_op)

    devices = collect_data_from_panorama(panorama)

    assert len(devices) == 2
    assert devices[0].device_name == device1.device_name
    assert devices[0].device_state == device1.device_state
    assert devices[1].device_name == device2.device_name
    assert devices[1].device_state == device2.device_state

def test_collect_data_from_firewall(monkeypatch):
    # Mock Firewall instance
    firewall = Firewall("hostname", "username", "password")

    # Create a sample device using factory
    device = DeviceInfoFactory()

    # Mock responses from firewall.op()
    mock_system_info_response = ET.fromstring(f"""
    <response status="success">
        <result>
            <system>
                <hostname>{device.device_name}</hostname>
                <model>{device.model}</model>
                <serial>{device.serial_number}</serial>
                <ip-address>{device.ipv4_address}</ip-address>
                <sw-version>{device.software_version}</sw-version>
                <global-protect-client-package-version>{device.globalprotect_client or "0.0.0"}</global-protect-client-package-version>
                <device-certificate-status>{device.device_certificate}</device-certificate-status>
            </system>
        </result>
    </response>
    """)

    mock_device_cert_response = ET.fromstring(f"""
    <response status="success">
        <result>
            <device-certificate>
                <validity>{device.device_certificate}</validity>
                <not_valid_after>{device.device_certificate_expiry_date}</not_valid_after>
            </device-certificate>
        </result>
    </response>
    """)

    def mock_op(cmd, cmd_xml=False):
        if "system" in cmd:
            return mock_system_info_response
        elif "device-certificate" in cmd:
            return mock_device_cert_response

    monkeypatch.setattr(firewall, "op", mock_op)

    collected_device = collect_data_from_firewall(firewall)

    assert collected_device.device_name == device.device_name
    assert collected_device.model == device.model
    assert collected_device.device_certificate == device.device_certificate
    assert collected_device.device_certificate_expiry_date == device.device_certificate_expiry_date