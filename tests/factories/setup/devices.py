"""Factories for generating test data for SCM Devices models."""

import factory
from scm.models.config.setup.devices import (
    AvailableLicenseModel,
    DeviceGetResponseModel,
    InstalledLicenseModel,
)


class InstalledLicenseFactory(factory.Factory):
    """Factory for InstalledLicenseModel."""
    class Meta:
        model = InstalledLicenseModel

    # TODO: Define factory fields based on InstalledLicenseModel
    # example_field = factory.Faker("word")


class AvailableLicenseFactory(factory.Factory):
    """Factory for AvailableLicenseModel."""
    class Meta:
        model = AvailableLicenseModel

    # TODO: Define factory fields based on AvailableLicenseModel
    # example_field = factory.Faker("word")


class DevicesFactory(factory.Factory):
    """Factory for DeviceGetResponseModel."""
    class Meta:
        model = DeviceGetResponseModel

    id = factory.Faker("uuid4")
    name = factory.Sequence(lambda n: f"test-device-{n}")
    display_name = factory.LazyAttribute(lambda o: o.name)
    hostname = factory.Faker("hostname")
    description = factory.Faker("sentence")
    serial_number = factory.Sequence(lambda n: f"SN{1000+n}")
    folder = factory.Faker("word")
    type = "Prisma Access"
    family = "Cloud Service"
    model = "Prisma Access GW"
    is_connected = factory.Faker("boolean")
    connected_since = factory.Faker("iso8601")

    # TODO: Add factory logic for nested license models using SubFactory or LazyAttribute
    # installed_licenses = factory.List([factory.SubFactory(InstalledLicenseFactory) for _ in range(2)])
    # available_licenses = factory.List([factory.SubFactory(AvailableLicenseFactory) for _ in range(3)])

