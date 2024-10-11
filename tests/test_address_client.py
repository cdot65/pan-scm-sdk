# tests/test_address_client.py

from unittest.mock import MagicMock
from scm.client import Scm
from scm.config.objects.addresses import AddressClient


def test_list_addresses():
    api_client = Scm(
        client_id="dummy_client_id",
        client_secret="dummy_client_secret",
        tsg_id="dummy_tsg_id",
    )
    api_client.get = MagicMock(
        return_value={
            "data": [
                {
                    "id": "1",
                    "name": "Address1",
                    "ip_netmask": "192.168.1.0/24",
                    "folder": "Folder1",
                },
                {
                    "id": "2",
                    "name": "Address2",
                    "fqdn": "example.com",
                    "folder": "Folder1",
                },
            ]
        }
    )

    address_client = AddressClient(api_client)
    addresses = address_client.list_addresses()
    assert len(addresses) == 2
    assert addresses[0].name == "Address1"
    assert addresses[1].fqdn == "example.com"


def test_get_address():
    api_client = Scm(
        client_id="dummy_client_id",
        client_secret="dummy_client_secret",
        tsg_id="dummy_tsg_id",
    )
    api_client.get = MagicMock(
        return_value={
            "id": "1",
            "name": "Address1",
            "ip_netmask": "192.168.1.0/24",
            "folder": "Folder1",
        }
    )

    address_client = AddressClient(api_client)
    address = address_client.get_address("1")
    assert address.id == "1"
    assert address.ip_netmask == "192.168.1.0/24"


# Additional tests for create, update, delete
