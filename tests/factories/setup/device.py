# tests/factories/setup/device.py

"""Factory definitions for device objects."""

import factory
from faker import Faker

from scm.models.setup.device import (
    DeviceLicenseModel,
    DeviceListResponseModel,
    DeviceResponseModel,
)

fake = Faker()


class DeviceLicenseFactory(factory.Factory):
    """Factory for DeviceLicenseModel."""

    class Meta:
        """Meta class that defines the model for the factory."""

        model = DeviceLicenseModel

    feature = factory.Faker("word")
    expires = factory.Faker("date")
    issued = factory.Faker("date")
    expired = factory.Faker("random_element", elements=["yes", "no", None])
    authcode = factory.Faker("lexify", text="????????", letters="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")


class DeviceLicenseModelFactory(factory.Factory):
    """Factory for DeviceLicenseModel."""

    class Meta:
        """Meta class that defines the model for the factory."""

        model = DeviceLicenseModel

    feature = factory.LazyFunction(lambda: fake.word())
    expires = factory.LazyFunction(lambda: fake.date())
    issued = factory.LazyFunction(lambda: fake.date())
    expired = factory.LazyFunction(lambda: fake.random_element(["yes", "no", None]))
    authcode = factory.LazyFunction(
        lambda: fake.lexify(text="????????", letters="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    )


class DeviceLicenseDictFactory(factory.Factory):
    """Factory for DeviceLicenseModel as dict."""

    class Meta:
        """Meta class that defines the model for the factory."""

        model = dict

    feature = factory.Faker("word")
    expires = factory.Faker("date")
    issued = factory.Faker("date")
    expired = factory.Faker("random_element", elements=["yes", "no", None])
    authcode = factory.Faker("lexify", text="????????", letters="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")


class DeviceLicenseModelDictFactory(factory.Factory):
    """Factory for DeviceLicenseModel as dict."""

    class Meta:
        """Meta class that defines the model for DeviceLicenseModelDictFactory."""

        model = dict

    feature = factory.LazyFunction(lambda: fake.word())
    expires = factory.LazyFunction(lambda: fake.date())
    issued = factory.LazyFunction(lambda: fake.date())
    expired = factory.LazyFunction(lambda: fake.random_element(["yes", "no", None]))
    authcode = factory.LazyFunction(
        lambda: fake.lexify(text="????????", letters="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    )


class DeviceResponseFactory(factory.Factory):
    """Factory for DeviceResponseModel."""

    class Meta:
        """Meta class that defines the model for the factory."""

        model = DeviceResponseModel

    id = factory.Faker("uuid4")
    name = factory.Sequence(lambda n: f"test-device-{n}")
    display_name = factory.LazyAttribute(lambda o: o.name)
    hostname = factory.Faker("hostname")
    description = factory.Faker("sentence")
    serial_number = factory.Sequence(lambda n: f"SN{1000 + n}")
    folder = factory.Faker("word")
    type = "Prisma Access"
    family = "Cloud Service"
    model = "Prisma Access GW"
    is_connected = factory.Faker("boolean")
    connected_since = factory.Faker("iso8601")

    # Added fields from correct model
    device_only = factory.Faker("boolean")
    last_disconnect_time = factory.Faker("iso8601")
    last_device_update_time = factory.Faker("iso8601")
    last_das_update_time = factory.Faker("iso8601")
    deactivate_wait_hrs = factory.Faker("random_int", min=1, max=24)
    deactivated_by = factory.Faker("email")
    to_be_deactivated_at = factory.Faker("iso8601")
    app_version = factory.Faker("numerify", text="####-####")
    app_release_date = factory.LazyFunction(lambda: fake.date_time().strftime("%Y/%m/%d %H:%M:%S %Z"))
    av_release_date = factory.LazyFunction(lambda: fake.date_time().strftime("%Y/%m/%d %H:%M:%S %Z"))
    anti_virus_version = factory.Faker("numerify", text="####-####")
    threat_version = factory.Faker("numerify", text="####-####")
    threat_release_date = factory.LazyFunction(lambda: fake.date_time().strftime("%Y/%m/%d %H:%M:%S %Z"))
    wf_ver = factory.Faker("numerify", text="######-######")
    wf_release_date = factory.LazyFunction(lambda: fake.date_time().strftime("%Y/%m/%d %H:%M:%S %Z"))
    iot_version = factory.Faker("numerify", text="###-###")
    iot_release_date = factory.LazyFunction(lambda: fake.date_time().strftime("%Y/%m/%d %H:%M:%S %Z"))
    gp_client_verion = factory.Faker("numerify", text="#.#.#")
    gp_data_version = factory.Faker("numerify", text="#")
    log_db_version = factory.Faker("numerify", text="##.#.#")
    software_version = factory.Faker("numerify", text="##.#.#")
    uptime = factory.LazyFunction(lambda: f"{fake.random_int(1, 100)} days, {fake.time()}")
    mac_address = factory.Faker("mac_address")
    ip_address = factory.Faker("ipv4")
    ipV6_address = factory.Faker("ipv6")
    url_db_ver = factory.Faker("numerify", text="########.#####")
    url_db_type = None
    license_match = factory.Faker("boolean")
    available_licenses = factory.List([factory.SubFactory(DeviceLicenseFactory) for _ in range(2)])
    installed_licenses = factory.List([factory.SubFactory(DeviceLicenseFactory) for _ in range(3)])
    ha_state = factory.Faker("random_element", elements=["active", "passive", "unknown"])
    ha_peer_state = factory.Faker("random_element", elements=["active", "passive", "unknown"])
    ha_peer_serial = factory.LazyFunction(lambda: fake.unique.numerify(text="###########"))
    vm_state = None


class DeviceResponseModelFactory(factory.Factory):
    """Factory for DeviceResponseModel."""

    class Meta:
        """Meta class that defines the model for DeviceResponseModelFactory."""

        model = DeviceResponseModel

    id = factory.LazyFunction(lambda: fake.lexify(text="??????????", letters="0123456789ABCDEF"))
    name = factory.LazyFunction(lambda: fake.slug())
    display_name = factory.LazyFunction(lambda: fake.word())
    serial_number = factory.LazyFunction(
        lambda: fake.lexify(text="??????????", letters="0123456789ABCDEF")
    )
    family = factory.LazyFunction(lambda: fake.random_element(["vm", "firewall", "panorama"]))
    model = factory.LazyFunction(lambda: fake.random_element(["PA-VM", "PA-220", "Panorama"]))
    folder = factory.LazyFunction(lambda: fake.word())
    hostname = factory.LazyFunction(lambda: fake.hostname())
    type = factory.LazyFunction(lambda: fake.random_element(["on-prem", "container", "cloud"]))
    device_only = factory.LazyFunction(lambda: fake.boolean())
    is_connected = factory.LazyFunction(lambda: fake.boolean())
    connected_since = factory.LazyFunction(lambda: fake.iso8601())
    last_disconnect_time = factory.LazyFunction(lambda: fake.iso8601())
    last_device_update_time = factory.LazyFunction(lambda: fake.iso8601())
    last_das_update_time = factory.LazyFunction(lambda: fake.iso8601())
    deactivate_wait_hrs = factory.LazyFunction(lambda: fake.random_int(min=1, max=24))
    deactivated_by = factory.LazyFunction(lambda: fake.email())
    to_be_deactivated_at = factory.LazyFunction(lambda: fake.iso8601())
    description = factory.LazyFunction(lambda: fake.sentence())
    app_version = factory.LazyFunction(lambda: fake.numerify(text="####-####"))
    app_release_date = factory.LazyFunction(
        lambda: fake.date_time().strftime("%Y/%m/%d %H:%M:%S %Z")
    )
    av_release_date = factory.LazyFunction(
        lambda: fake.date_time().strftime("%Y/%m/%d %H:%M:%S %Z")
    )
    anti_virus_version = factory.LazyFunction(lambda: fake.numerify(text="####-####"))
    threat_version = factory.LazyFunction(lambda: fake.numerify(text="####-####"))
    threat_release_date = factory.LazyFunction(
        lambda: fake.date_time().strftime("%Y/%m/%d %H:%M:%S %Z")
    )
    wf_ver = factory.LazyFunction(lambda: fake.numerify(text="######-######"))
    wf_release_date = factory.LazyFunction(
        lambda: fake.date_time().strftime("%Y/%m/%d %H:%M:%S %Z")
    )
    iot_version = factory.LazyFunction(lambda: fake.numerify(text="###-###"))
    iot_release_date = factory.LazyFunction(
        lambda: fake.date_time().strftime("%Y/%m/%d %H:%M:%S %Z")
    )
    gp_client_verion = factory.LazyFunction(lambda: fake.numerify(text="#.#.#"))
    gp_data_version = factory.LazyFunction(lambda: fake.numerify(text="#"))
    log_db_version = factory.LazyFunction(lambda: fake.numerify(text="##.#.#"))
    software_version = factory.LazyFunction(lambda: fake.numerify(text="##.#.#"))
    uptime = factory.LazyFunction(lambda: f"{fake.random_int(1, 100)} days, {fake.time()}")
    mac_address = factory.LazyFunction(fake.mac_address)
    ip_address = factory.LazyFunction(fake.ipv4)
    ipV6_address = factory.LazyFunction(lambda: fake.random_element([fake.ipv6(), "unknown"]))
    url_db_ver = factory.LazyFunction(lambda: fake.numerify(text="########.#####"))
    url_db_type = None
    license_match = factory.LazyFunction(lambda: fake.boolean())
    available_licenses = factory.LazyFunction(lambda: DeviceLicenseModelFactory.build_batch(2))
    installed_licenses = factory.LazyFunction(lambda: DeviceLicenseModelFactory.build_batch(5))
    ha_state = factory.LazyFunction(lambda: fake.random_element(["active", "passive", "unknown"]))
    ha_peer_state = factory.LazyFunction(
        lambda: fake.random_element(["active", "passive", "unknown"])
    )
    ha_peer_serial = factory.LazyFunction(lambda: fake.unique.numerify(text="###########"))
    vm_state = None


class DeviceResponseDictFactory(factory.Factory):
    """Factory for DeviceResponseModel as dict with API aliases."""

    class Meta:
        """Meta class that defines the model for the factory."""

        model = dict

    id = factory.Faker("uuid4")
    name = factory.Sequence(lambda n: f"test-device-{n}")
    displayName = factory.LazyAttribute(lambda o: o.name)  # Use API alias
    hostname = factory.Faker("hostname")
    description = factory.Faker("sentence")
    serialNumber = factory.Sequence(lambda n: f"SN{1000 + n}")  # Use API alias
    folder = factory.Faker("word")
    type = "Prisma Access"
    family = "Cloud Service"
    model = "Prisma Access GW"
    isConnected = factory.Faker("boolean")  # Use API alias
    connectedSince = factory.Faker("iso8601")  # Use API alias

    # Added fields from correct model
    device_only = factory.Faker("boolean")
    last_disconnect_time = factory.Faker("iso8601")
    last_device_update_time = factory.Faker("iso8601")
    last_das_update_time = factory.Faker("iso8601")
    deactivate_wait_hrs = factory.Faker("random_int", min=1, max=24)
    deactivated_by = factory.Faker("email")
    to_be_deactivated_at = factory.Faker("iso8601")
    dev_cert_detail = None
    dev_cert_expiry_date = None
    app_version = factory.Faker("numerify", text="####-####")
    app_release_date = factory.LazyFunction(lambda: fake.date_time().strftime("%Y/%m/%d %H:%M:%S %Z"))
    av_release_date = factory.LazyFunction(lambda: fake.date_time().strftime("%Y/%m/%d %H:%M:%S %Z"))
    anti_virus_version = factory.Faker("numerify", text="####-####")
    threat_version = factory.Faker("numerify", text="####-####")
    threat_release_date = factory.LazyFunction(lambda: fake.date_time().strftime("%Y/%m/%d %H:%M:%S %Z"))
    wf_ver = factory.Faker("numerify", text="######-######")
    wf_release_date = factory.LazyFunction(lambda: fake.date_time().strftime("%Y/%m/%d %H:%M:%S %Z"))
    iot_version = factory.Faker("numerify", text="###-###")
    iot_release_date = factory.LazyFunction(lambda: fake.date_time().strftime("%Y/%m/%d %H:%M:%S %Z"))
    gp_client_verion = factory.Faker("numerify", text="#.#.#")
    gp_data_version = factory.Faker("numerify", text="#")
    log_db_version = factory.Faker("numerify", text="##.#.#")
    software_version = factory.Faker("numerify", text="##.#.#")
    uptime = factory.LazyFunction(lambda: f"{fake.random_int(1, 100)} days, {fake.time()}")
    mac_address = factory.Faker("mac_address")
    ip_address = factory.Faker("ipv4")
    ipV6_address = factory.Faker("ipv6")
    url_db_ver = factory.Faker("numerify", text="########.#####")
    url_db_type = None
    license_match = factory.Faker("boolean")
    availableLicenses = factory.List([factory.SubFactory(DeviceLicenseDictFactory) for _ in range(2)])  # Use API alias
    installedLicenses = factory.List([factory.SubFactory(DeviceLicenseDictFactory) for _ in range(3)])  # Use API alias
    ha_state = factory.Faker("random_element", elements=["active", "passive", "unknown"])
    ha_peer_state = factory.Faker("random_element", elements=["active", "passive", "unknown"])
    ha_peer_serial = factory.LazyFunction(lambda: fake.unique.numerify(text="###########"))
    vm_state = None


class DeviceResponseModelDictFactory(factory.Factory):
    """Factory for DeviceResponseModel as dict."""

    class Meta:
        """Meta class that defines the model for DeviceResponseModelDictFactory."""

        model = dict

    id = factory.LazyFunction(lambda: fake.lexify(text="??????????", letters="0123456789ABCDEF"))
    name = factory.LazyFunction(lambda: fake.slug())
    display_name = factory.LazyFunction(lambda: fake.word())
    serial_number = factory.LazyFunction(
        lambda: fake.lexify(text="??????????", letters="0123456789ABCDEF")
    )
    family = factory.LazyFunction(lambda: fake.random_element(["vm", "firewall", "panorama"]))
    model = factory.LazyFunction(lambda: fake.random_element(["PA-VM", "PA-220", "Panorama"]))
    folder = factory.LazyFunction(lambda: fake.word())
    hostname = factory.LazyFunction(lambda: fake.hostname())
    type = factory.LazyFunction(lambda: fake.random_element(["on-prem", "container", "cloud"]))
    device_only = factory.LazyFunction(lambda: fake.boolean())
    is_connected = factory.LazyFunction(lambda: fake.boolean())
    connected_since = factory.LazyFunction(lambda: fake.iso8601())
    last_disconnect_time = factory.LazyFunction(lambda: fake.iso8601())
    last_device_update_time = factory.LazyFunction(lambda: fake.iso8601())
    last_das_update_time = factory.LazyFunction(lambda: fake.iso8601())
    deactivate_wait_hrs = factory.LazyFunction(lambda: fake.random_int(min=1, max=24))
    deactivated_by = factory.LazyFunction(lambda: fake.email())
    to_be_deactivated_at = factory.LazyFunction(lambda: fake.iso8601())
    description = factory.LazyFunction(lambda: fake.sentence())
    app_version = factory.LazyFunction(lambda: fake.numerify(text="####-####"))
    app_release_date = factory.LazyFunction(
        lambda: fake.date_time().strftime("%Y/%m/%d %H:%M:%S %Z")
    )
    av_release_date = factory.LazyFunction(
        lambda: fake.date_time().strftime("%Y/%m/%d %H:%M:%S %Z")
    )
    anti_virus_version = factory.LazyFunction(lambda: fake.numerify(text="####-####"))
    threat_version = factory.LazyFunction(lambda: fake.numerify(text="####-####"))
    threat_release_date = factory.LazyFunction(
        lambda: fake.date_time().strftime("%Y/%m/%d %H:%M:%S %Z")
    )
    wf_ver = factory.LazyFunction(lambda: fake.numerify(text="######-######"))
    wf_release_date = factory.LazyFunction(
        lambda: fake.date_time().strftime("%Y/%m/%d %H:%M:%S %Z")
    )
    iot_version = factory.LazyFunction(lambda: fake.numerify(text="###-###"))
    iot_release_date = factory.LazyFunction(
        lambda: fake.date_time().strftime("%Y/%m/%d %H:%M:%S %Z")
    )
    gp_client_verion = factory.LazyFunction(lambda: fake.numerify(text="#.#.#"))
    gp_data_version = factory.LazyFunction(lambda: fake.numerify(text="#"))
    log_db_version = factory.LazyFunction(lambda: fake.numerify(text="##.#.#"))
    software_version = factory.LazyFunction(lambda: fake.numerify(text="##.#.#"))
    uptime = factory.LazyFunction(lambda: f"{fake.random_int(1, 100)} days, {fake.time()}")
    mac_address = factory.LazyFunction(fake.mac_address)
    ip_address = factory.LazyFunction(fake.ipv4)
    ipV6_address = factory.LazyFunction(lambda: fake.random_element([fake.ipv6(), "unknown"]))
    url_db_ver = factory.LazyFunction(lambda: fake.numerify(text="########.#####"))
    url_db_type = None
    license_match = factory.LazyFunction(lambda: fake.boolean())
    available_licenses = factory.LazyFunction(
        lambda: [DeviceLicenseModelDictFactory.build() for _ in range(2)]
    )
    installed_licenses = factory.LazyFunction(
        lambda: [DeviceLicenseModelDictFactory.build() for _ in range(5)]
    )
    ha_state = factory.LazyFunction(lambda: fake.random_element(["active", "passive", "unknown"]))
    ha_peer_state = factory.LazyFunction(
        lambda: fake.random_element(["active", "passive", "unknown"])
    )
    ha_peer_serial = factory.LazyFunction(lambda: fake.unique.numerify(text="###########"))
    vm_state = None


class DeviceListResponseModelFactory(factory.Factory):
    """Factory for DeviceListResponseModel."""

    class Meta:
        """Meta class that defines the model for the factory."""

        model = DeviceListResponseModel

    data = factory.LazyFunction(lambda: DeviceResponseModelFactory.build_batch(3))
    limit = 200
    offset = 0
    total = 3


class DeviceListResponseModelDictFactory(factory.Factory):
    """Factory for DeviceListResponseModel as dict."""

    class Meta:
        """Meta class that defines the model for DeviceListResponseModelDictFactory."""

        model = dict

    data = factory.List([factory.SubFactory(DeviceResponseDictFactory) for _ in range(3)])
    limit = 200
    offset = 0
    total = 3
