# tests/test_factories/__init__.py
from tests.test_factories.objects.address import (
    AddressCreateApiFactory,
    AddressCreateModelFactory,
    AddressResponseFactory,
    AddressUpdateApiFactory,
    AddressUpdateModelFactory,
)
from tests.test_factories.objects.address_group import (
    AddressGroupBaseFactory,
    AddressGroupCreateApiFactory,
    AddressGroupCreateModelFactory,
    AddressGroupResponseFactory,
    AddressGroupUpdateApiFactory,
    AddressGroupUpdateModelFactory,
)
from tests.test_factories.objects.application_filters import (
    ApplicationFiltersBaseFactory,
    ApplicationFiltersCreateApiFactory,
    ApplicationFiltersCreateModelFactory,
    ApplicationFiltersResponseFactory,
    ApplicationFiltersResponseModelFactory,
    ApplicationFiltersUpdateApiFactory,
    ApplicationFiltersUpdateModelFactory,
)
from tests.test_factories.objects.application_group import (
    ApplicationGroupBaseFactory,
    ApplicationGroupCreateApiFactory,
    ApplicationGroupCreateModelFactory,
    ApplicationGroupResponseFactory,
    ApplicationGroupUpdateApiFactory,
    ApplicationGroupUpdateModelFactory,
)
from tests.test_factories.objects.dynamic_user_group import (
    DynamicUserGroupBaseFactory,
    DynamicUserGroupCreateApiFactory,
    DynamicUserGroupCreateModelFactory,
    DynamicUserGroupResponseFactory,
    DynamicUserGroupUpdateApiFactory,
    DynamicUserGroupUpdateModelFactory,
)
from tests.test_factories.objects.external_dynamic_lists import (
    ExternalDynamicListsBaseFactory,
    ExternalDynamicListsCreateApiFactory,
    ExternalDynamicListsCreateModelFactory,
    ExternalDynamicListsResponseFactory,
    ExternalDynamicListsResponseModelFactory,
    ExternalDynamicListsUpdateApiFactory,
    ExternalDynamicListsUpdateModelFactory,
)
from tests.test_factories.objects.hip_object import (
    HIPObjectBaseFactory,
    HIPObjectCreateApiFactory,
    HIPObjectCreateModelFactory,
    HIPObjectResponseFactory,
    HIPObjectResponseModelFactory,
    HIPObjectUpdateApiFactory,
    HIPObjectUpdateModelFactory,
)
from tests.test_factories.objects.syslog_server_profiles import (
    EscapingModelFactory,
    FormatModelFactory,
    SyslogServerModelFactory,
    SyslogServerProfileCreateModelFactory,
    SyslogServerProfileResponseModelFactory,
    SyslogServerProfileUpdateModelFactory,
)
from tests.test_factories.security.url_categories import (
    URLCategoriesCreateModelFactory,
    URLCategoriesResponseModelFactory,
    URLCategoriesUpdateModelFactory,
)

__all__ = [
    # Security - URL Categories
    "URLCategoriesCreateModelFactory",
    "URLCategoriesUpdateModelFactory",
    "URLCategoriesResponseModelFactory",
    # Syslog Server Profiles
    "EscapingModelFactory",
    "FormatModelFactory",
    "SyslogServerModelFactory",
    "SyslogServerProfileCreateModelFactory",
    "SyslogServerProfileUpdateModelFactory",
    "SyslogServerProfileResponseModelFactory",
    # Address
    "AddressCreateApiFactory",
    "AddressUpdateApiFactory",
    "AddressResponseFactory",
    "AddressCreateModelFactory",
    "AddressUpdateModelFactory",
    # Address Group
    "AddressGroupBaseFactory",
    "AddressGroupCreateApiFactory",
    "AddressGroupUpdateApiFactory",
    "AddressGroupResponseFactory",
    "AddressGroupCreateModelFactory",
    "AddressGroupUpdateModelFactory",
    # Application Filters
    "ApplicationFiltersBaseFactory",
    "ApplicationFiltersCreateApiFactory",
    "ApplicationFiltersUpdateApiFactory",
    "ApplicationFiltersResponseFactory",
    "ApplicationFiltersCreateModelFactory",
    "ApplicationFiltersUpdateModelFactory",
    "ApplicationFiltersResponseModelFactory",
    # Application Group
    "ApplicationGroupBaseFactory",
    "ApplicationGroupCreateApiFactory",
    "ApplicationGroupUpdateApiFactory",
    "ApplicationGroupResponseFactory",
    "ApplicationGroupCreateModelFactory",
    "ApplicationGroupUpdateModelFactory",
    # Dynamic User Group
    "DynamicUserGroupBaseFactory",
    "DynamicUserGroupCreateApiFactory",
    "DynamicUserGroupUpdateApiFactory",
    "DynamicUserGroupResponseFactory",
    "DynamicUserGroupCreateModelFactory",
    "DynamicUserGroupUpdateModelFactory",
    # External Dynamic Lists
    "ExternalDynamicListsBaseFactory",
    "ExternalDynamicListsCreateApiFactory",
    "ExternalDynamicListsUpdateApiFactory",
    "ExternalDynamicListsResponseFactory",
    "ExternalDynamicListsCreateModelFactory",
    "ExternalDynamicListsUpdateModelFactory",
    "ExternalDynamicListsResponseModelFactory",
    # HIP Objects
    "HIPObjectBaseFactory",
    "HIPObjectCreateApiFactory",
    "HIPObjectUpdateApiFactory",
    "HIPObjectResponseFactory",
    "HIPObjectCreateModelFactory",
    "HIPObjectUpdateModelFactory",
    "HIPObjectResponseModelFactory",
]
