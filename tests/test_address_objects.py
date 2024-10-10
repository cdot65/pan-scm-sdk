# tests/test_address_model.py

import pytest
from pydantic import ValidationError
from scm.models.address import Address


def test_address_valid_ip_netmask():
    address_data = {
        "id": "123e4567-e89b-12d3-a456-426655440000",
        "name": "Test Address",
        "ip_netmask": "192.168.1.1/24",
        "folder": "My Folder",
    }
    address = Address(**address_data)
    assert address.ip_netmask == "192.168.1.1/24"
    assert address.folder == "My Folder"


def test_address_invalid_multiple_address_types():
    address_data = {
        "id": "123e4567-e89b-12d3-a456-426655440001",
        "name": "Invalid Address",
        "ip_netmask": "192.168.1.1/24",
        "fqdn": "example.com",
        "folder": "My Folder",
    }
    with pytest.raises(ValidationError) as exc_info:
        Address(**address_data)
    assert (
        "Exactly one of 'ip_netmask', 'ip_range', 'ip_wildcard', or 'fqdn' must be provided."
        in str(exc_info.value)
    )


def test_address_missing_address_type():
    address_data = {
        "id": "123e4567-e89b-12d3-a456-426655440002",
        "name": "No Address Type",
        "folder": "My Folder",
    }
    with pytest.raises(ValidationError) as exc_info:
        Address(**address_data)
    assert (
        "Exactly one of 'ip_netmask', 'ip_range', 'ip_wildcard', or 'fqdn' must be provided."
        in str(exc_info.value)
    )


def test_address_valid_container():
    address_data = {
        "id": "123e4567-e89b-12d3-a456-426655440003",
        "name": "Valid Container",
        "ip_range": "10.0.0.1-10.0.0.4",
        "device": "Device1",
    }
    address = Address(**address_data)
    assert address.ip_range == "10.0.0.1-10.0.0.4"
    assert address.device == "Device1"


def test_address_invalid_multiple_containers():
    address_data = {
        "id": "123e4567-e89b-12d3-a456-426655440004",
        "name": "Invalid Container",
        "ip_wildcard": "10.20.1.0/0.0.248.255",
        "folder": "Folder1",
        "snippet": "Snippet1",
    }
    with pytest.raises(ValidationError) as exc_info:
        Address(**address_data)
    assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
        exc_info.value
    )
