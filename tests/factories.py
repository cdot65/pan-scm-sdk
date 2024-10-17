# tests/factories.py

import factory

from scm.models.objects import (
    ApplicationRequestModel,
    ServiceRequestModel,
    ApplicationGroupRequestModel,
)
from scm.models.objects.address import AddressRequestModel
from scm.models.objects.address_group import AddressGroupRequestModel, DynamicFilter


class AddressFactory(factory.Factory):
    class Meta:
        model = AddressRequestModel

    name = factory.Faker("word")
    id = factory.Faker("uuid4")
    description = "PyTest AddressRequestModel"
    ip_netmask = "192.168.1.1/32"
    folder = "Prisma Access"


class DynamicFilterFactory(factory.Factory):
    class Meta:
        model = DynamicFilter

    filter = "'test', 'abc123', 'prod', 'web'"


class AddressGroupDynamicFactory(factory.Factory):
    class Meta:
        model = AddressGroupRequestModel

    name = "ValidDynamicAddressGroup"
    description = "This is just a pytest that will fail"
    dynamic = factory.SubFactory(DynamicFilterFactory)
    folder = "MainFolder"
    tag = ["tag1", "tag2"]


class AddressGroupStaticFactory(factory.Factory):
    class Meta:
        model = AddressGroupRequestModel

    name = "ValidStaticAddressGroup"
    description = "Static AddressRequestModel Group Test"
    static = [
        "address-object1",
        "address-object2",
        "address-object3",
        "address-object4",
    ]
    folder = "MainFolder"
    tag = ["tag1", "tag2"]


class ApplicationFactory(factory.Factory):
    class Meta:
        model = ApplicationRequestModel

    name = "ValidApplication"
    description = "Application from pan-scm-sdk Test"
    category = "collaboration"
    subcategory = "file-sharing"
    technology = "client-server"
    risk = 1
    ports = ["tcp/80,443", "udp/3478"]
    folder = "Prisma Access"
    evasive = False
    pervasive = False
    excessive_bandwidth_use = False
    used_by_malware = False
    transfers_files = False
    has_known_vulnerabilities = True
    tunnels_other_apps = False
    prone_to_misuse = False
    no_certifications = False


class ApplicationGroupFactory(factory.Factory):
    class Meta:
        model = ApplicationGroupRequestModel

    name = "ValidStaticApplicationGroup"
    members = [
        "office365-consumer-access",
        "office365-enterprise-access",
    ]
    folder = "Prisma Access"


class ServiceFactory(factory.Factory):
    class Meta:
        model = ServiceRequestModel

    name = factory.Faker("word")
    description = "PyTest ServiceRequestModel test"
    tag = ["Automation"]
    folder = "Prisma Access"
    protocol = {"tcp": {"port": "80,443"}}
