"""Live API tests for Objects models.

These tests validate that Pydantic models correctly parse real API responses.
They are excluded from CI and only run locally with valid credentials.

Run with: pytest -m api tests/scm/api/test_objects_api.py -v
"""

import pytest

from scm.models.objects import (
    AddressResponseModel,
    AddressGroupResponseModel,
    ApplicationResponseModel,
    ApplicationFiltersResponseModel,
    ApplicationGroupResponseModel,
    DynamicUserGroupResponseModel,
    ExternalDynamicListsResponseModel,
    HIPObjectResponseModel,
    HIPProfileResponseModel,
    HTTPServerProfileResponseModel,
    LogForwardingProfileResponseModel,
    RegionResponseModel,
    ScheduleResponseModel,
    ServiceResponseModel,
    ServiceGroupResponseModel,
    SyslogServerProfileResponseModel,
    TagResponseModel,
)


@pytest.mark.api
class TestAddressAPI:
    """Live API tests for Address objects."""

    def test_list_addresses(self, live_client, folder):
        """Verify Address list responses parse correctly."""
        addresses = live_client.address.list(folder=folder, limit=10)
        assert isinstance(addresses, list)
        for addr in addresses:
            assert isinstance(addr, AddressResponseModel)
            assert addr.id is not None
            assert addr.name is not None

    def test_address_has_valid_type(self, live_client, folder):
        """Verify Address objects have valid address type."""
        addresses = live_client.address.list(folder=folder, limit=5)
        for addr in addresses:
            # Each address should have exactly one type set
            types = [addr.ip_netmask, addr.ip_range, addr.ip_wildcard, addr.fqdn]
            assert any(t is not None for t in types), f"Address {addr.name} has no type set"


@pytest.mark.api
class TestAddressGroupAPI:
    """Live API tests for AddressGroup objects."""

    def test_list_address_groups(self, live_client, folder):
        """Verify AddressGroup list responses parse correctly."""
        groups = live_client.address_group.list(folder=folder, limit=10)
        assert isinstance(groups, list)
        for group in groups:
            assert isinstance(group, AddressGroupResponseModel)
            assert group.id is not None
            assert group.name is not None


@pytest.mark.api
class TestApplicationAPI:
    """Live API tests for Application objects."""

    def test_list_applications(self, live_client, folder):
        """Verify Application list responses parse correctly."""
        apps = live_client.application.list(folder=folder, limit=10)
        assert isinstance(apps, list)
        for app in apps:
            assert isinstance(app, ApplicationResponseModel)
            # Predefined objects from snippets may not have IDs
            if app.snippet != "predefined-snippet":
                assert app.id is not None
            assert app.name is not None


@pytest.mark.api
class TestApplicationFiltersAPI:
    """Live API tests for ApplicationFilters objects."""

    def test_list_application_filters(self, live_client, folder):
        """Verify ApplicationFilters list responses parse correctly."""
        filters = live_client.application_filter.list(folder=folder, limit=10)
        assert isinstance(filters, list)
        for f in filters:
            assert isinstance(f, ApplicationFiltersResponseModel)
            # Predefined objects from snippets may not have IDs
            if f.snippet != "predefined-snippet":
                assert f.id is not None
            assert f.name is not None


@pytest.mark.api
class TestApplicationGroupAPI:
    """Live API tests for ApplicationGroup objects."""

    def test_list_application_groups(self, live_client, folder):
        """Verify ApplicationGroup list responses parse correctly."""
        groups = live_client.application_group.list(folder=folder, limit=10)
        assert isinstance(groups, list)
        for group in groups:
            assert isinstance(group, ApplicationGroupResponseModel)
            assert group.id is not None
            assert group.name is not None


@pytest.mark.api
class TestDynamicUserGroupAPI:
    """Live API tests for DynamicUserGroup objects."""

    def test_list_dynamic_user_groups(self, live_client, folder):
        """Verify DynamicUserGroup list responses parse correctly."""
        groups = live_client.dynamic_user_group.list(folder=folder, limit=10)
        assert isinstance(groups, list)
        for group in groups:
            assert isinstance(group, DynamicUserGroupResponseModel)
            assert group.id is not None
            assert group.name is not None


@pytest.mark.api
class TestExternalDynamicListsAPI:
    """Live API tests for ExternalDynamicLists objects."""

    def test_list_external_dynamic_lists(self, live_client, folder):
        """Verify ExternalDynamicLists list responses parse correctly."""
        edls = live_client.external_dynamic_list.list(folder=folder, limit=10)
        assert isinstance(edls, list)
        for edl in edls:
            assert isinstance(edl, ExternalDynamicListsResponseModel)
            # Predefined objects from snippets may not have IDs
            if edl.snippet not in ("predefined-snippet", "predefined"):
                assert edl.id is not None
            assert edl.name is not None


@pytest.mark.api
class TestHIPObjectAPI:
    """Live API tests for HIPObject objects."""

    def test_list_hip_objects(self, live_client, folder):
        """Verify HIPObject list responses parse correctly."""
        hip_objects = live_client.hip_object.list(folder=folder, limit=10)
        assert isinstance(hip_objects, list)
        for obj in hip_objects:
            assert isinstance(obj, HIPObjectResponseModel)
            assert obj.id is not None
            assert obj.name is not None

    def test_hip_object_custom_checks_parsing(self, live_client, folder):
        """Verify HIPObject custom_checks field parses correctly if present."""
        hip_objects = live_client.hip_object.list(folder=folder, limit=10)
        for obj in hip_objects:
            # custom_checks is optional, but if present should be valid
            if obj.custom_checks is not None:
                assert obj.custom_checks.criteria is not None


@pytest.mark.api
class TestHIPProfileAPI:
    """Live API tests for HIPProfile objects."""

    def test_list_hip_profiles(self, live_client, folder):
        """Verify HIPProfile list responses parse correctly."""
        profiles = live_client.hip_profile.list(folder=folder)
        assert isinstance(profiles, list)
        for profile in profiles:
            assert isinstance(profile, HIPProfileResponseModel)
            assert profile.id is not None
            assert profile.name is not None


@pytest.mark.api
class TestHTTPServerProfileAPI:
    """Live API tests for HTTPServerProfile objects."""

    def test_list_http_server_profiles(self, live_client, folder):
        """Verify HTTPServerProfile list responses parse correctly."""
        profiles = live_client.http_server_profile.list(folder=folder, limit=10)
        assert isinstance(profiles, list)
        for profile in profiles:
            assert isinstance(profile, HTTPServerProfileResponseModel)
            assert profile.id is not None
            assert profile.name is not None


@pytest.mark.api
class TestLogForwardingProfileAPI:
    """Live API tests for LogForwardingProfile objects."""

    def test_list_log_forwarding_profiles(self, live_client, folder):
        """Verify LogForwardingProfile list responses parse correctly."""
        profiles = live_client.log_forwarding_profile.list(folder=folder, limit=10)
        assert isinstance(profiles, list)
        for profile in profiles:
            assert isinstance(profile, LogForwardingProfileResponseModel)
            # Predefined objects from snippets may not have IDs
            if profile.snippet != "predefined-snippet":
                assert profile.id is not None
            assert profile.name is not None


@pytest.mark.api
class TestRegionAPI:
    """Live API tests for Region objects."""

    def test_list_regions(self, live_client, folder):
        """Verify Region list responses parse correctly."""
        regions = live_client.region.list(folder=folder, limit=10)
        assert isinstance(regions, list)
        for region in regions:
            assert isinstance(region, RegionResponseModel)
            # Predefined objects from snippets may not have IDs
            if region.snippet != "predefined-snippet":
                assert region.id is not None
            assert region.name is not None


@pytest.mark.api
class TestScheduleAPI:
    """Live API tests for Schedule objects."""

    def test_list_schedules(self, live_client, folder):
        """Verify Schedule list responses parse correctly."""
        schedules = live_client.schedule.list(folder=folder, limit=10)
        assert isinstance(schedules, list)
        for schedule in schedules:
            assert isinstance(schedule, ScheduleResponseModel)
            assert schedule.id is not None
            assert schedule.name is not None


@pytest.mark.api
class TestServiceAPI:
    """Live API tests for Service objects."""

    def test_list_services(self, live_client, folder):
        """Verify Service list responses parse correctly."""
        services = live_client.service.list(folder=folder, limit=10)
        assert isinstance(services, list)
        for service in services:
            assert isinstance(service, ServiceResponseModel)
            # Predefined objects from snippets may not have IDs
            if service.snippet != "predefined-snippet":
                assert service.id is not None
            assert service.name is not None


@pytest.mark.api
class TestServiceGroupAPI:
    """Live API tests for ServiceGroup objects."""

    def test_list_service_groups(self, live_client, folder):
        """Verify ServiceGroup list responses parse correctly."""
        groups = live_client.service_group.list(folder=folder, limit=10)
        assert isinstance(groups, list)
        for group in groups:
            assert isinstance(group, ServiceGroupResponseModel)
            assert group.id is not None
            assert group.name is not None


@pytest.mark.api
class TestSyslogServerProfileAPI:
    """Live API tests for SyslogServerProfile objects."""

    def test_list_syslog_server_profiles(self, live_client, folder):
        """Verify SyslogServerProfile list responses parse correctly."""
        profiles = live_client.syslog_server_profile.list(folder=folder, limit=10)
        assert isinstance(profiles, list)
        for profile in profiles:
            assert isinstance(profile, SyslogServerProfileResponseModel)
            assert profile.id is not None
            assert profile.name is not None


@pytest.mark.api
class TestTagAPI:
    """Live API tests for Tag objects."""

    def test_list_tags(self, live_client, folder):
        """Verify Tag list responses parse correctly."""
        tags = live_client.tag.list(folder=folder, limit=10)
        assert isinstance(tags, list)
        for tag in tags:
            assert isinstance(tag, TagResponseModel)
            assert tag.id is not None
            assert tag.name is not None

    def test_tag_colors_are_valid(self, live_client, folder):
        """Verify Tag color values are properly parsed."""
        tags = live_client.tag.list(folder=folder, limit=10)
        for tag in tags:
            if tag.color is not None:
                # Color should be a valid string from the Colors enum
                assert isinstance(tag.color, str)
