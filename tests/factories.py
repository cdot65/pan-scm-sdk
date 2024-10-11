# tests/factories.py

import factory
from scm.models.address import Address
from scm.models.address_group import AddressGroup, DynamicFilter


class AddressFactory(factory.Factory):
    class Meta:
        model = Address

    name = factory.Faker("word")
    id = factory.Faker("uuid4")
    description = "PyTest Address"
    ip_netmask = "192.168.1.1/32"
    folder = "Prisma Access"


class DynamicFilterFactory(factory.Factory):
    class Meta:
        model = DynamicFilter

    filter = "'test', 'abc123', 'prod', 'web'"


class AddressGroupDynamicFactory(factory.Factory):
    class Meta:
        model = AddressGroup

    name = "ValidDynamicAddressGroup"
    description = "This is just a pytest that will fail"
    dynamic = factory.SubFactory(DynamicFilterFactory)
    folder = "MainFolder"
    tag = ["tag1", "tag2"]


class AddressGroupStaticFactory(factory.Factory):
    class Meta:
        model = AddressGroup

    name = "ValidStaticAddressGroup"
    description = "Static Address Group Test"
    static = [
        "address-object1",
        "address-object2",
        "address-object3",
        "address-object4",
    ]
    folder = "MainFolder"
    tag = ["tag1", "tag2"]
