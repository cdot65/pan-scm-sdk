"""Factory definitions for network Zone Protection Profile objects."""

import uuid

import factory

from scm.models.network.zone_protection_profile import (
    ZoneProtectionProfileCreateModel,
    ZoneProtectionProfileResponseModel,
    ZoneProtectionProfileUpdateModel,
)


# SDK tests against SCM API
class ZoneProtectionProfileCreateApiFactory(factory.Factory):
    """Factory for creating ZoneProtectionProfileCreateModel instances."""

    class Meta:
        """Meta class that defines the model for ZoneProtectionProfileCreateApiFactory."""

        model = ZoneProtectionProfileCreateModel

    name = factory.Sequence(lambda n: f"zone_protection_{n}")
    folder = "Shared"
    description = None
    flood = None
    scan = None
    scan_white_list = None
    spoofed_ip_discard = None
    strict_ip_check = None
    fragmented_traffic_discard = None
    strict_source_routing_discard = None
    loose_source_routing_discard = None
    timestamp_discard = None
    record_route_discard = None
    security_discard = None
    stream_id_discard = None
    unknown_option_discard = None
    malformed_option_discard = None
    mismatched_overlapping_tcp_segment_discard = None
    tcp_handshake_discard = None
    tcp_syn_with_data_discard = None
    tcp_synack_with_data_discard = None
    reject_non_syn_tcp = None
    asymmetric_path = None
    mptcp_option_strip = None
    tcp_timestamp_strip = None
    tcp_fast_open_and_data_strip = None
    icmp_ping_zero_id_discard = None
    icmp_frag_discard = None
    icmp_large_packet_discard = None
    discard_icmp_embedded_error = None
    suppress_icmp_timeexceeded = None
    suppress_icmp_needfrag = None
    ipv6 = None
    non_ip_protocol = None
    l2_sec_group_tag_protection = None

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)


class ZoneProtectionProfileUpdateApiFactory(factory.Factory):
    """Factory for creating ZoneProtectionProfileUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for ZoneProtectionProfileUpdateApiFactory."""

        model = ZoneProtectionProfileUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"zone_protection_{n}")
    description = None
    flood = None
    scan = None
    scan_white_list = None
    spoofed_ip_discard = None
    strict_ip_check = None
    fragmented_traffic_discard = None
    strict_source_routing_discard = None
    loose_source_routing_discard = None
    timestamp_discard = None
    record_route_discard = None
    security_discard = None
    stream_id_discard = None
    unknown_option_discard = None
    malformed_option_discard = None
    mismatched_overlapping_tcp_segment_discard = None
    tcp_handshake_discard = None
    tcp_syn_with_data_discard = None
    tcp_synack_with_data_discard = None
    reject_non_syn_tcp = None
    asymmetric_path = None
    mptcp_option_strip = None
    tcp_timestamp_strip = None
    tcp_fast_open_and_data_strip = None
    icmp_ping_zero_id_discard = None
    icmp_frag_discard = None
    icmp_large_packet_discard = None
    discard_icmp_embedded_error = None
    suppress_icmp_timeexceeded = None
    suppress_icmp_needfrag = None
    ipv6 = None
    non_ip_protocol = None
    l2_sec_group_tag_protection = None


class ZoneProtectionProfileResponseFactory(factory.Factory):
    """Factory for creating ZoneProtectionProfileResponseModel instances."""

    class Meta:
        """Meta class that defines the model for ZoneProtectionProfileResponseFactory."""

        model = ZoneProtectionProfileResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"zone_protection_{n}")
    folder = "Shared"
    description = None
    flood = None
    scan = None
    scan_white_list = None
    spoofed_ip_discard = None
    strict_ip_check = None
    fragmented_traffic_discard = None
    strict_source_routing_discard = None
    loose_source_routing_discard = None
    timestamp_discard = None
    record_route_discard = None
    security_discard = None
    stream_id_discard = None
    unknown_option_discard = None
    malformed_option_discard = None
    mismatched_overlapping_tcp_segment_discard = None
    tcp_handshake_discard = None
    tcp_syn_with_data_discard = None
    tcp_synack_with_data_discard = None
    reject_non_syn_tcp = None
    asymmetric_path = None
    mptcp_option_strip = None
    tcp_timestamp_strip = None
    tcp_fast_open_and_data_strip = None
    icmp_ping_zero_id_discard = None
    icmp_frag_discard = None
    icmp_large_packet_discard = None
    discard_icmp_embedded_error = None
    suppress_icmp_timeexceeded = None
    suppress_icmp_needfrag = None
    ipv6 = None
    non_ip_protocol = None
    l2_sec_group_tag_protection = None

    @classmethod
    def from_request(cls, request_model: ZoneProtectionProfileCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class ZoneProtectionProfileCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for ZoneProtectionProfileCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"zone_protection_{n}")
    folder = "Shared"

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestZoneProtection",
            folder="Shared",
            description="Test zone protection profile",
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="TestZoneProtection",
            folder="Shared",
            snippet="TestSnippet",
        )

    @classmethod
    def build_with_no_container(cls):
        """Return a data dict without any container."""
        return cls(
            name="TestZoneProtection",
            folder=None,
            snippet=None,
            device=None,
        )


class ZoneProtectionProfileUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for ZoneProtectionProfileUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"zone_protection_{n}")

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating a zone protection profile."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedZoneProtection",
            description="Updated zone protection profile",
        )
