# tests/test_models.py

import pytest

from scm.client import Scm
from scm.config.objects import AddressGroups, Addresses
from scm.models import (
    Address,
    AddressGroup,
)
from scm.models.address_group import DynamicFilter
from pydantic import ValidationError

from tests.factories import (
    AddressFactory,
    AddressGroupDynamicFactory,
    AddressGroupStaticFactory,
)


# -------------------------------------------------------------------------- #
# Testing the existence of the 'name' attribute
# -------------------------------------------------------------------------- #
def test_address_name_exists():
    with pytest.raises(ValidationError) as exc_info:
        Address(
            ip_netmask="192.168.1.1/32",
            folder="MainFolder",
        )
    assert (
        "1 validation error for Address\nname\n  Field required [type=missing,"
        in str(exc_info.value)
    )


def test_address_group_name_exists():
    with pytest.raises(ValidationError) as exc_info:
        AddressGroup(
            description="this is just a pytest that will fail",
            folder="MainFolder",
        )
    assert (
        "1 validation error for AddressGroup\nname\n  Field required [type=missing,"
        in str(exc_info.value)
    )


# -------------------------------------------------------------------------- #
# Testing the length of the 'name' attribute
# -------------------------------------------------------------------------- #
def test_address_name_max_length():
    with pytest.raises(ValidationError) as exc_info:
        Address(
            name="A" * 64,  # Exceeds max_length=63
            ip_netmask="192.168.1.1/32",
            folder="MainFolder",
        )
    assert "String should have at most 63 characters" in str(exc_info.value)


def test_address_group_name_max_length():
    with pytest.raises(ValidationError) as exc_info:
        AddressGroup(
            name="A" * 64,  # Exceeds max_length=63
            description="This is just a pytest that will fail",
            dynamic={"filter": "'this-is-a-tag"},
            folder="MainFolder",
        )
    assert "String should have at most 63 characters" in str(exc_info.value)


# -------------------------------------------------------------------------- #
# Testing the valid creations
# -------------------------------------------------------------------------- #
def test_address_valid_creation():
    address = Address(
        name="ValidAddress",
        fqdn="valid.example.com",
        folder="MainFolder",
        tag=["tag1", "tag2"],
    )
    assert address.name == "ValidAddress"
    assert address.fqdn == "valid.example.com"
    assert address.folder == "MainFolder"
    assert address.tag == ["tag1", "tag2"]
    assert address.ip_netmask is None
    assert address.ip_range is None
    assert address.ip_wildcard is None


def test_address_group_static_valid_creation():
    # Create an AddressGroup instance using the factory
    address = AddressGroupStaticFactory()
    assert address.name == "ValidStaticAddressGroup"
    assert address.description == "Static Address Group Test"
    assert address.static == [
        "address-object1",
        "address-object2",
        "address-object3",
        "address-object4",
    ]
    assert address.folder == "MainFolder"
    assert address.tag == ["tag1", "tag2"]
    assert address.dynamic is None


def test_address_group_dynamic_valid_creation():
    # Create an AddressGroup instance using the factory
    address_group = AddressGroupDynamicFactory()

    # Assertions
    assert address_group.name == "ValidDynamicAddressGroup"
    assert address_group.dynamic.filter == "'test', 'abc123', 'prod', 'web'"
    assert address_group.folder == "MainFolder"
    assert address_group.tag == ["tag1", "tag2"]

    # Compare the dynamic attribute's dictionary representation
    assert address_group.dynamic.model_dump() == {
        "filter": "'test', 'abc123', 'prod', 'web'"
    }

    # Compare with a DynamicFilter instance
    expected_dynamic = DynamicFilter(filter="'test', 'abc123', 'prod', 'web'")
    assert address_group.dynamic == expected_dynamic

    # Assert the folder
    assert address_group.folder == "MainFolder"

    # Assert the tags
    assert address_group.tag == ["tag1", "tag2"]


# -------------------------------------------------------------------------- #
# Testing the invalid creations
# -------------------------------------------------------------------------- #
def test_address_creation_with_factory():
    address = AddressFactory()
    assert address.name is not None
    assert address.ip_netmask == "192.168.1.1/32"


def test_address_group_creation_with_factory():
    address_group = AddressGroupDynamicFactory()
    assert address_group.name is not None
    assert address_group.description == "This is just a pytest that will fail"


# -------------------------------------------------------------------------- #
# Testing the custom validators
# -------------------------------------------------------------------------- #
def test_address_single_address_type():
    with pytest.raises(ValueError) as exc_info:
        Address(
            name="TestAddress",
            ip_netmask="192.168.1.1/32",
            fqdn="example.com",  # Both ip_netmask and fqdn provided
            folder="MainFolder",
        )
    assert (
        "Exactly one of 'ip_netmask', 'ip_range', 'ip_wildcard', or 'fqdn' must be provided."
        in str(exc_info.value)
    )


# -------------------------------------------------------------------------- #
# Mock Tests
# -------------------------------------------------------------------------- #
def test_create_addresses(load_env, mocker):
    # Initialize the API client
    api_client = Scm(
        client_id=load_env["client_id"],
        client_secret=load_env["client_secret"],
        tsg_id=load_env["tsg_id"],
    )

    # Create an instance of AddressGroups
    address_client = Addresses(api_client)

    # Create a test AddressGroup instance using Factory Boy
    test_address = AddressFactory()

    # Mock the API client's post method
    mock_response = test_address.model_dump()
    mock_response["id"] = "123e4567-e89b-12d3-a456-426655440000"  # Mocked ID
    mocked_post = mocker.patch.object(
        api_client,
        "post",
        return_value=mock_response,
    )

    # Call the create method
    created_group = address_client.create(test_address.model_dump(exclude_unset=True))

    # Assertions
    mocked_post.assert_called_once_with(
        "/config/objects/v1/addresses",
        json=test_address.model_dump(exclude_unset=True),
    )
    assert created_group.id == "123e4567-e89b-12d3-a456-426655440000"
    assert created_group.name == test_address.name
    assert created_group.description == test_address.description
    assert created_group.ip_netmask == test_address.ip_netmask
    assert created_group.folder == test_address.folder


def test_create_address_group_with_dynamic_filter(load_env, mocker):
    # Initialize the API client
    api_client = Scm(
        client_id=load_env["client_id"],
        client_secret=load_env["client_secret"],
        tsg_id=load_env["tsg_id"],
    )

    # Create an instance of AddressGroups
    address_groups_client = AddressGroups(api_client)

    # Create a test AddressGroup instance using Factory Boy
    test_address_group = AddressGroupDynamicFactory()

    # Mock the API client's post method
    mock_response = test_address_group.model_dump()
    mock_response["id"] = "123e4567-e89b-12d3-a456-426655440000"  # Mocked ID
    mocked_post = mocker.patch.object(
        api_client,
        "post",
        return_value=mock_response,
    )

    # Call the create method
    created_group = address_groups_client.create(
        test_address_group.model_dump(exclude_unset=True)
    )

    # Assertions
    mocked_post.assert_called_once_with(
        "/config/objects/v1/address-groups",
        json=test_address_group.model_dump(exclude_unset=True),
    )
    assert created_group.id == "123e4567-e89b-12d3-a456-426655440000"
    assert created_group.name == test_address_group.name
    assert created_group.dynamic.filter == test_address_group.dynamic.filter
    assert created_group.folder == test_address_group.folder


def test_create_address_group_with_static_entries(load_env, mocker):
    # Initialize the API client
    api_client = Scm(
        client_id=load_env["client_id"],
        client_secret=load_env["client_secret"],
        tsg_id=load_env["tsg_id"],
    )

    # Create an instance of AddressGroups
    address_groups_client = AddressGroups(api_client)

    # Create a test AddressGroup instance using Factory Boy
    test_address_group = AddressGroupStaticFactory()

    # Mock the API client's post method
    mock_response = test_address_group.model_dump()
    mock_response["id"] = "123e4567-e89b-12d3-a456-426655440000"  # Mocked ID
    mocked_post = mocker.patch.object(
        api_client,
        "post",
        return_value=mock_response,
    )

    # Call the create method
    created_group = address_groups_client.create(
        test_address_group.model_dump(exclude_unset=True)
    )

    # Assertions
    mocked_post.assert_called_once_with(
        "/config/objects/v1/address-groups",
        json=test_address_group.model_dump(exclude_unset=True),
    )
    assert created_group.id == "123e4567-e89b-12d3-a456-426655440000"
    assert created_group.name == test_address_group.name
    assert created_group.folder == test_address_group.folder
