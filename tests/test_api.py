# tests/test_api.py

from scm.client import Scm
from scm.config.objects import Addresses, AddressGroups
from scm.models import Address, AddressGroup


def test_list_addresses(load_env):
    client_id = load_env["client_id"]
    client_secret = load_env["client_secret"]
    tsg_id = load_env["tsg_id"]

    # Initialize the API client
    api_client = Scm(
        client_id=client_id,
        client_secret=client_secret,
        tsg_id=tsg_id,
    )

    # Create an instance of Addresses
    addresses_client = Addresses(api_client)

    # Call the list method
    addresses = addresses_client.list(folder="Prisma Access")

    # Assertions
    assert isinstance(addresses, list)
    assert isinstance(addresses[0], Address)


def test_list_address_groups(load_env):
    client_id = load_env["client_id"]
    client_secret = load_env["client_secret"]
    tsg_id = load_env["tsg_id"]

    # Initialize the API client
    api_client = Scm(
        client_id=client_id,
        client_secret=client_secret,
        tsg_id=tsg_id,
    )

    # Create an instance of Addresses
    address_groups_client = AddressGroups(api_client)

    # Call the list method
    address_groups = address_groups_client.list(folder="Prisma Access")

    # Assertions
    assert isinstance(address_groups, list)
    assert isinstance(address_groups[0], AddressGroup)
