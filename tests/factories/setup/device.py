# tests/factories/setup/device.py

import factory
from faker import Faker

from scm.models.setup.device import (
    DeviceLicenseModel,
    DeviceListResponseModel,
    DeviceResponseModel,
)

fake = Faker()


class DeviceLicenseModelFactory(factory.Factory):
    """Factory for DeviceLicenseModel."""

    class Meta:
        model = DeviceLicenseModel

    feature = factory.LazyFunction(lambda: fake.word())
    expires = factory.LazyFunction(lambda: fake.date())
    issued = factory.LazyFunction(lambda: fake.date())
    expired = factory.LazyFunction(lambda: fake.random_element(["yes", "no", None]))
    authcode = factory.LazyFunction(
        lambda: fake.lexify(text="????????", letters="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    )


class DeviceResponseModelFactory(factory.Factory):
    """Factory for DeviceResponseModel."""

    class Meta:
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
    gp_client_version = factory.LazyFunction(lambda: fake.numerify(text="#.#.#"))
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


class DeviceLicenseModelDictFactory(factory.Factory):
    """Factory for DeviceLicenseModel."""

    class Meta:
        model = dict

    feature = factory.LazyFunction(lambda: fake.word())
    expires = factory.LazyFunction(lambda: fake.date())
    issued = factory.LazyFunction(lambda: fake.date())
    expired = factory.LazyFunction(lambda: fake.random_element(["yes", "no", None]))
    authcode = factory.LazyFunction(
        lambda: fake.lexify(text="????????", letters="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    )


class DeviceResponseModelDictFactory(factory.Factory):
    """Factory for DeviceResponseModel."""

    class Meta:
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
    gp_client_version = factory.LazyFunction(lambda: fake.numerify(text="#.#.#"))
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
        model = DeviceListResponseModel

    data = factory.LazyFunction(lambda: DeviceResponseModelFactory.build_batch(3))
    limit = 200
    offset = 0
    total = 3


class DeviceListResponseModelDictFactory(factory.Factory):
    """Factory for DeviceListResponseModel."""

    class Meta:
        model = dict

    data = factory.LazyFunction(lambda: [DeviceResponseModelDictFactory.build() for _ in range(3)])
    limit = 200
    offset = 0
    total = 3
