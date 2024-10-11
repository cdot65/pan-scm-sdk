# tests/factories.py

import factory
from scm.models.address_model import AddressModel
from scm.models.address_group import AddressGroupModel, DynamicFilter


class AddressFactory(factory.Factory):
    class Meta:
        model = AddressModel

    name = factory.Faker("word")
    id = factory.Faker("uuid4")
    description = "PyTest AddressModel"
    ip_netmask = "192.168.1.1/32"
    folder = "Prisma Access"


class DynamicFilterFactory(factory.Factory):
    class Meta:
        model = DynamicFilter

    filter = "'test', 'abc123', 'prod', 'web'"


class AddressGroupDynamicFactory(factory.Factory):
    class Meta:
        model = AddressGroupModel

    name = "ValidDynamicAddressGroup"
    description = "This is just a pytest that will fail"
    dynamic = factory.SubFactory(DynamicFilterFactory)
    folder = "MainFolder"
    tag = ["tag1", "tag2"]


class AddressGroupStaticFactory(factory.Factory):
    class Meta:
        model = AddressGroupModel

    name = "ValidStaticAddressGroup"
    description = "Static AddressModel Group Test"
    static = [
        "address-object1",
        "address-object2",
        "address-object3",
        "address-object4",
    ]
    folder = "MainFolder"
    tag = ["tag1", "tag2"]
