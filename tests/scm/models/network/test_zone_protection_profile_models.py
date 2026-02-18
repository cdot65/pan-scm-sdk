"""Test models for Zone Protection Profiles."""

from uuid import UUID

from pydantic import ValidationError
import pytest

from scm.models.network import (
    FloodProtection,
    FloodRed,
    FloodSynCookies,
    IcmpFlood,
    Icmpv6Flood,
    L2SecGroupTagProtection,
    NonIpProtocol,
    NonIpProtocolEntry,
    OtherIpFlood,
    ScanAction,
    ScanActionBlockIp,
    ScanEntry,
    ScanWhiteListEntry,
    SctpInitFlood,
    SgtEntry,
    TcpSynFlood,
    UdpFlood,
    ZoneProtectionProfileCreateModel,
    ZoneProtectionProfileResponseModel,
    ZoneProtectionProfileUpdateModel,
)


class TestFloodProtectionModels:
    """Test flood protection nested models."""

    def test_flood_red_valid(self):
        """Test valid FloodRed configuration."""
        red = FloodRed(alarm_rate=100, activate_rate=200, maximal_rate=500)
        assert red.alarm_rate == 100
        assert red.activate_rate == 200
        assert red.maximal_rate == 500

    def test_flood_red_boundary_values(self):
        """Test FloodRed boundary values."""
        # Minimum values
        red = FloodRed(alarm_rate=0, activate_rate=0, maximal_rate=0)
        assert red.alarm_rate == 0

        # Maximum values
        red = FloodRed(alarm_rate=2000000, activate_rate=2000000, maximal_rate=2000000)
        assert red.maximal_rate == 2000000

    def test_flood_red_out_of_range(self):
        """Test FloodRed with out-of-range values."""
        with pytest.raises(ValidationError):
            FloodRed(alarm_rate=-1, activate_rate=0, maximal_rate=0)

        with pytest.raises(ValidationError):
            FloodRed(alarm_rate=0, activate_rate=2000001, maximal_rate=0)

    def test_flood_syn_cookies_valid(self):
        """Test valid FloodSynCookies configuration."""
        sc = FloodSynCookies(alarm_rate=100, activate_rate=200, maximal_rate=500)
        assert sc.alarm_rate == 100
        assert sc.activate_rate == 200
        assert sc.maximal_rate == 500

    def test_tcp_syn_flood_with_red(self):
        """Test TcpSynFlood with RED configuration."""
        tcp_syn = TcpSynFlood(
            enable=True,
            red=FloodRed(alarm_rate=100, activate_rate=200, maximal_rate=500),
        )
        assert tcp_syn.enable is True
        assert tcp_syn.red.alarm_rate == 100
        assert tcp_syn.syn_cookies is None

    def test_tcp_syn_flood_with_syn_cookies(self):
        """Test TcpSynFlood with SYN cookies configuration."""
        tcp_syn = TcpSynFlood(
            enable=True,
            syn_cookies=FloodSynCookies(alarm_rate=100, activate_rate=200, maximal_rate=500),
        )
        assert tcp_syn.enable is True
        assert tcp_syn.syn_cookies.alarm_rate == 100
        assert tcp_syn.red is None

    def test_tcp_syn_flood_mutual_exclusivity(self):
        """Test that red and syn_cookies are mutually exclusive."""
        with pytest.raises(ValueError) as exc_info:
            TcpSynFlood(
                enable=True,
                red=FloodRed(alarm_rate=100, activate_rate=200, maximal_rate=500),
                syn_cookies=FloodSynCookies(alarm_rate=100, activate_rate=200, maximal_rate=500),
            )
        assert "mutually exclusive" in str(exc_info.value)

    def test_udp_flood_valid(self):
        """Test valid UdpFlood configuration."""
        udp = UdpFlood(
            enable=True,
            red=FloodRed(alarm_rate=1000, activate_rate=2000, maximal_rate=5000),
        )
        assert udp.enable is True
        assert udp.red.alarm_rate == 1000

    def test_sctp_init_flood_valid(self):
        """Test valid SctpInitFlood configuration."""
        sctp = SctpInitFlood(
            enable=True,
            red=FloodRed(alarm_rate=500, activate_rate=1000, maximal_rate=2000),
        )
        assert sctp.enable is True
        assert sctp.red.activate_rate == 1000

    def test_icmp_flood_valid(self):
        """Test valid IcmpFlood configuration."""
        icmp = IcmpFlood(
            enable=True,
            red=FloodRed(alarm_rate=200, activate_rate=400, maximal_rate=800),
        )
        assert icmp.enable is True
        assert icmp.red.maximal_rate == 800

    def test_icmpv6_flood_valid(self):
        """Test valid Icmpv6Flood configuration."""
        icmpv6 = Icmpv6Flood(
            enable=True,
            red=FloodRed(alarm_rate=300, activate_rate=600, maximal_rate=1200),
        )
        assert icmpv6.enable is True
        assert icmpv6.red.alarm_rate == 300

    def test_other_ip_flood_valid(self):
        """Test valid OtherIpFlood configuration."""
        other = OtherIpFlood(
            enable=True,
            red=FloodRed(alarm_rate=400, activate_rate=800, maximal_rate=1600),
        )
        assert other.enable is True
        assert other.red.activate_rate == 800

    def test_flood_protection_complete(self):
        """Test complete FloodProtection configuration."""
        flood = FloodProtection(
            tcp_syn=TcpSynFlood(
                enable=True,
                red=FloodRed(alarm_rate=100, activate_rate=200, maximal_rate=500),
            ),
            udp=UdpFlood(enable=True),
            icmp=IcmpFlood(enable=False),
        )
        assert flood.tcp_syn.enable is True
        assert flood.tcp_syn.red.alarm_rate == 100
        assert flood.udp.enable is True
        assert flood.icmp.enable is False
        assert flood.sctp_init is None
        assert flood.icmpv6 is None
        assert flood.other_ip is None


class TestScanProtectionModels:
    """Test scan protection nested models."""

    def test_scan_action_block_ip_valid(self):
        """Test valid ScanActionBlockIp configuration."""
        block_ip = ScanActionBlockIp(track_by="source", duration=300)
        assert block_ip.track_by == "source"
        assert block_ip.duration == 300

    def test_scan_action_block_ip_source_and_destination(self):
        """Test ScanActionBlockIp with source-and-destination tracking."""
        block_ip = ScanActionBlockIp(track_by="source-and-destination", duration=60)
        assert block_ip.track_by == "source-and-destination"

    def test_scan_action_block_ip_invalid_track_by(self):
        """Test ScanActionBlockIp with invalid track_by value."""
        with pytest.raises(ValidationError):
            ScanActionBlockIp(track_by="invalid", duration=300)

    def test_scan_action_block_ip_duration_range(self):
        """Test ScanActionBlockIp duration boundary values."""
        # Valid boundaries
        block_ip = ScanActionBlockIp(track_by="source", duration=1)
        assert block_ip.duration == 1

        block_ip = ScanActionBlockIp(track_by="source", duration=3600)
        assert block_ip.duration == 3600

        # Invalid values
        with pytest.raises(ValidationError):
            ScanActionBlockIp(track_by="source", duration=0)

        with pytest.raises(ValidationError):
            ScanActionBlockIp(track_by="source", duration=3601)

    def test_scan_action_allow(self):
        """Test ScanAction with allow action."""
        action = ScanAction(allow={})
        assert action.allow == {}
        assert action.alert is None
        assert action.block is None
        assert action.block_ip is None

    def test_scan_action_alert(self):
        """Test ScanAction with alert action."""
        action = ScanAction(alert={})
        assert action.alert == {}

    def test_scan_action_block(self):
        """Test ScanAction with block action."""
        action = ScanAction(block={})
        assert action.block == {}

    def test_scan_action_block_ip(self):
        """Test ScanAction with block_ip action."""
        action = ScanAction(block_ip=ScanActionBlockIp(track_by="source", duration=300))
        assert action.block_ip.track_by == "source"

    def test_scan_action_no_action_set(self):
        """Test ScanAction with no action set fails."""
        with pytest.raises(ValueError) as exc_info:
            ScanAction()
        assert "Exactly one action must be set" in str(exc_info.value)

    def test_scan_action_multiple_actions_set(self):
        """Test ScanAction with multiple actions set fails."""
        with pytest.raises(ValueError) as exc_info:
            ScanAction(allow={}, alert={})
        assert "Exactly one action must be set" in str(exc_info.value)

    def test_scan_entry_valid(self):
        """Test valid ScanEntry configuration."""
        entry = ScanEntry(
            name="8001",
            action=ScanAction(alert={}),
            interval=10,
            threshold=100,
        )
        assert entry.name == "8001"
        assert entry.interval == 10
        assert entry.threshold == 100

    def test_scan_entry_valid_names(self):
        """Test ScanEntry with all valid name values."""
        for name in ["8001", "8002", "8003", "8006"]:
            entry = ScanEntry(name=name)
            assert entry.name == name

    def test_scan_entry_invalid_name(self):
        """Test ScanEntry with invalid name."""
        with pytest.raises(ValidationError):
            ScanEntry(name="8004")

        with pytest.raises(ValidationError):
            ScanEntry(name="invalid")

    def test_scan_entry_interval_range(self):
        """Test ScanEntry interval boundary values."""
        entry = ScanEntry(name="8001", interval=2)
        assert entry.interval == 2

        entry = ScanEntry(name="8001", interval=65535)
        assert entry.interval == 65535

        with pytest.raises(ValidationError):
            ScanEntry(name="8001", interval=1)

        with pytest.raises(ValidationError):
            ScanEntry(name="8001", interval=65536)

    def test_scan_entry_threshold_range(self):
        """Test ScanEntry threshold boundary values."""
        entry = ScanEntry(name="8001", threshold=2)
        assert entry.threshold == 2

        entry = ScanEntry(name="8001", threshold=65535)
        assert entry.threshold == 65535

        with pytest.raises(ValidationError):
            ScanEntry(name="8001", threshold=1)

        with pytest.raises(ValidationError):
            ScanEntry(name="8001", threshold=65536)

    def test_scan_white_list_entry_valid(self):
        """Test valid ScanWhiteListEntry configuration."""
        entry = ScanWhiteListEntry(name="trusted-host", ipv4="192.168.1.1")
        assert entry.name == "trusted-host"
        assert entry.ipv4 == "192.168.1.1"
        assert entry.ipv6 is None

    def test_scan_white_list_entry_ipv6(self):
        """Test ScanWhiteListEntry with IPv6."""
        entry = ScanWhiteListEntry(name="trusted-host-v6", ipv6="2001:db8::1")
        assert entry.name == "trusted-host-v6"
        assert entry.ipv6 == "2001:db8::1"


class TestNonIpProtocolModels:
    """Test non-IP protocol models."""

    def test_non_ip_protocol_entry_valid(self):
        """Test valid NonIpProtocolEntry configuration."""
        entry = NonIpProtocolEntry(name="ARP", ether_type="0x0806", enable=True)
        assert entry.name == "ARP"
        assert entry.ether_type == "0x0806"
        assert entry.enable is True

    def test_non_ip_protocol_valid(self):
        """Test valid NonIpProtocol configuration."""
        protocol = NonIpProtocol(
            list_type="exclude",
            protocol=[
                NonIpProtocolEntry(name="ARP", ether_type="0x0806", enable=True),
            ],
        )
        assert protocol.list_type == "exclude"
        assert len(protocol.protocol) == 1

    def test_non_ip_protocol_invalid_list_type(self):
        """Test NonIpProtocol with invalid list_type."""
        with pytest.raises(ValidationError):
            NonIpProtocol(list_type="invalid")

    def test_non_ip_protocol_include_type(self):
        """Test NonIpProtocol with include list type."""
        protocol = NonIpProtocol(list_type="include")
        assert protocol.list_type == "include"


class TestSgtModels:
    """Test Security Group Tag models."""

    def test_sgt_entry_valid(self):
        """Test valid SgtEntry configuration."""
        entry = SgtEntry(name="test-sgt", tag="0x0001", enable=True)
        assert entry.name == "test-sgt"
        assert entry.tag == "0x0001"
        assert entry.enable is True

    def test_l2_sec_group_tag_protection_valid(self):
        """Test valid L2SecGroupTagProtection configuration."""
        protection = L2SecGroupTagProtection(
            tags=[
                SgtEntry(name="sgt1", tag="0x0001", enable=True),
                SgtEntry(name="sgt2", tag="0x0002", enable=False),
            ]
        )
        assert len(protection.tags) == 2
        assert protection.tags[0].name == "sgt1"
        assert protection.tags[1].enable is False

    def test_l2_sec_group_tag_protection_empty(self):
        """Test L2SecGroupTagProtection with no tags."""
        protection = L2SecGroupTagProtection()
        assert protection.tags is None


class TestZoneProtectionProfileModels:
    """Test Zone Protection Profile Pydantic models."""

    def test_base_model_validation(self):
        """Test validation of ZoneProtectionProfileBaseModel through the Create model."""
        valid_data = {
            "name": "test-profile",
            "folder": "Test Folder",
            "description": "A test zone protection profile",
            "spoofed_ip_discard": True,
            "strict_ip_check": False,
        }
        model = ZoneProtectionProfileCreateModel(**valid_data)
        assert model.name == "test-profile"
        assert model.folder == "Test Folder"
        assert model.description == "A test zone protection profile"
        assert model.spoofed_ip_discard is True
        assert model.strict_ip_check is False

    def test_name_max_length(self):
        """Test name field max_length validation."""
        # Valid name at max length (31 chars)
        valid_data = {
            "name": "A" * 31,
            "folder": "Test Folder",
        }
        model = ZoneProtectionProfileCreateModel(**valid_data)
        assert len(model.name) == 31

        # Invalid name over max length
        invalid_data = {
            "name": "A" * 32,
            "folder": "Test Folder",
        }
        with pytest.raises(ValidationError) as exc_info:
            ZoneProtectionProfileCreateModel(**invalid_data)
        assert "should have at most 31 characters" in str(exc_info.value).lower()

    def test_description_max_length(self):
        """Test description field max_length validation."""
        # Valid description at max length
        valid_data = {
            "name": "test",
            "folder": "Test Folder",
            "description": "A" * 255,
        }
        model = ZoneProtectionProfileCreateModel(**valid_data)
        assert len(model.description) == 255

        # Invalid description over max length
        invalid_data = {
            "name": "test",
            "folder": "Test Folder",
            "description": "A" * 256,
        }
        with pytest.raises(ValidationError) as exc_info:
            ZoneProtectionProfileCreateModel(**invalid_data)
        assert "should have at most 255 characters" in str(exc_info.value).lower()

    def test_create_model_container_validation(self):
        """Test validation of container fields in ZoneProtectionProfileCreateModel."""
        # Test with folder container
        model = ZoneProtectionProfileCreateModel(name="test", folder="Test Folder")
        assert model.folder == "Test Folder"
        assert model.snippet is None
        assert model.device is None

        # Test with snippet container
        model = ZoneProtectionProfileCreateModel(name="test", snippet="Test Snippet")
        assert model.snippet == "Test Snippet"
        assert model.folder is None

        # Test with device container
        model = ZoneProtectionProfileCreateModel(name="test", device="Test Device")
        assert model.device == "Test Device"
        assert model.folder is None

        # Test with no container
        with pytest.raises(ValueError) as exc_info:
            ZoneProtectionProfileCreateModel(name="test")
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

        # Test with multiple containers
        with pytest.raises(ValueError) as exc_info:
            ZoneProtectionProfileCreateModel(
                name="test", folder="Test Folder", snippet="Test Snippet"
            )
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_string_enum_fields_valid(self):
        """Test valid string enum field values."""
        # reject_non_syn_tcp
        for value in ["global", "yes", "no"]:
            model = ZoneProtectionProfileCreateModel(
                name="test", folder="Folder", reject_non_syn_tcp=value
            )
            assert model.reject_non_syn_tcp == value

        # asymmetric_path
        for value in ["global", "drop", "bypass"]:
            model = ZoneProtectionProfileCreateModel(
                name="test", folder="Folder", asymmetric_path=value
            )
            assert model.asymmetric_path == value

        # mptcp_option_strip
        for value in ["no", "yes", "global"]:
            model = ZoneProtectionProfileCreateModel(
                name="test", folder="Folder", mptcp_option_strip=value
            )
            assert model.mptcp_option_strip == value

    def test_string_enum_fields_invalid(self):
        """Test invalid string enum field values."""
        with pytest.raises(ValidationError):
            ZoneProtectionProfileCreateModel(
                name="test", folder="Folder", reject_non_syn_tcp="invalid"
            )

        with pytest.raises(ValidationError):
            ZoneProtectionProfileCreateModel(
                name="test", folder="Folder", asymmetric_path="invalid"
            )

        with pytest.raises(ValidationError):
            ZoneProtectionProfileCreateModel(
                name="test", folder="Folder", mptcp_option_strip="invalid"
            )

    def test_update_model(self):
        """Test validation of ZoneProtectionProfileUpdateModel."""
        valid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "updated-profile",
            "folder": "Test Folder",
            "spoofed_ip_discard": True,
        }
        model = ZoneProtectionProfileUpdateModel(**valid_data)
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "updated-profile"
        assert model.spoofed_ip_discard is True

        # Test invalid UUID
        invalid_data = valid_data.copy()
        invalid_data["id"] = "not-a-uuid"
        with pytest.raises(ValidationError):
            ZoneProtectionProfileUpdateModel(**invalid_data)

    def test_response_model(self):
        """Test validation of ZoneProtectionProfileResponseModel."""
        valid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "response-profile",
            "folder": "Test Folder",
            "description": "A response profile",
        }
        model = ZoneProtectionProfileResponseModel(**valid_data)
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "response-profile"

        # Test missing required ID
        invalid_data = valid_data.copy()
        del invalid_data["id"]
        with pytest.raises(ValidationError):
            ZoneProtectionProfileResponseModel(**invalid_data)

    def test_model_with_flood_protection(self):
        """Test model with flood protection configuration."""
        model = ZoneProtectionProfileCreateModel(
            name="flood-test",
            folder="Test Folder",
            flood=FloodProtection(
                tcp_syn=TcpSynFlood(
                    enable=True,
                    red=FloodRed(alarm_rate=100, activate_rate=200, maximal_rate=500),
                ),
                udp=UdpFlood(enable=True),
            ),
        )
        assert model.flood.tcp_syn.enable is True
        assert model.flood.tcp_syn.red.alarm_rate == 100
        assert model.flood.udp.enable is True

    def test_model_with_scan_entries(self):
        """Test model with scan protection entries."""
        model = ZoneProtectionProfileCreateModel(
            name="scan-test",
            folder="Test Folder",
            scan=[
                ScanEntry(
                    name="8001",
                    action=ScanAction(alert={}),
                    interval=10,
                    threshold=100,
                ),
                ScanEntry(
                    name="8002",
                    action=ScanAction(block_ip=ScanActionBlockIp(track_by="source", duration=300)),
                ),
            ],
        )
        assert len(model.scan) == 2
        assert model.scan[0].name == "8001"
        assert model.scan[1].action.block_ip.duration == 300

    def test_model_with_ipv6_dict(self):
        """Test model with IPv6 as Dict."""
        model = ZoneProtectionProfileCreateModel(
            name="ipv6-test",
            folder="Test Folder",
            ipv6={
                "routing_header_0": True,
                "routing_header_1": False,
                "routing_header_3": True,
            },
        )
        assert model.ipv6["routing_header_0"] is True
        assert model.ipv6["routing_header_1"] is False

    def test_model_with_non_ip_protocol(self):
        """Test model with non-IP protocol configuration."""
        model = ZoneProtectionProfileCreateModel(
            name="nonip-test",
            folder="Test Folder",
            non_ip_protocol=NonIpProtocol(
                list_type="exclude",
                protocol=[
                    NonIpProtocolEntry(name="ARP", ether_type="0x0806", enable=True),
                ],
            ),
        )
        assert model.non_ip_protocol.list_type == "exclude"
        assert len(model.non_ip_protocol.protocol) == 1

    def test_model_with_l2_sgt(self):
        """Test model with L2 Security Group Tag protection."""
        model = ZoneProtectionProfileCreateModel(
            name="sgt-test",
            folder="Test Folder",
            l2_sec_group_tag_protection=L2SecGroupTagProtection(
                tags=[
                    SgtEntry(name="sgt1", tag="0x0001", enable=True),
                ]
            ),
        )
        assert len(model.l2_sec_group_tag_protection.tags) == 1
        assert model.l2_sec_group_tag_protection.tags[0].name == "sgt1"

    def test_model_all_boolean_discard_fields(self):
        """Test model with all boolean discard fields."""
        model = ZoneProtectionProfileCreateModel(
            name="discard-test",
            folder="Test Folder",
            spoofed_ip_discard=True,
            strict_ip_check=True,
            fragmented_traffic_discard=True,
            strict_source_routing_discard=True,
            loose_source_routing_discard=True,
            timestamp_discard=True,
            record_route_discard=True,
            security_discard=True,
            stream_id_discard=True,
            unknown_option_discard=True,
            malformed_option_discard=True,
            mismatched_overlapping_tcp_segment_discard=True,
            tcp_handshake_discard=True,
            tcp_syn_with_data_discard=True,
            tcp_synack_with_data_discard=True,
            tcp_timestamp_strip=True,
            tcp_fast_open_and_data_strip=True,
            icmp_ping_zero_id_discard=True,
            icmp_frag_discard=True,
            icmp_large_packet_discard=True,
            discard_icmp_embedded_error=True,
            suppress_icmp_timeexceeded=True,
            suppress_icmp_needfrag=True,
        )
        assert model.spoofed_ip_discard is True
        assert model.strict_ip_check is True
        assert model.fragmented_traffic_discard is True
        assert model.strict_source_routing_discard is True
        assert model.loose_source_routing_discard is True
        assert model.timestamp_discard is True
        assert model.record_route_discard is True
        assert model.security_discard is True
        assert model.stream_id_discard is True
        assert model.unknown_option_discard is True
        assert model.malformed_option_discard is True
        assert model.mismatched_overlapping_tcp_segment_discard is True
        assert model.tcp_handshake_discard is True
        assert model.tcp_syn_with_data_discard is True
        assert model.tcp_synack_with_data_discard is True
        assert model.tcp_timestamp_strip is True
        assert model.tcp_fast_open_and_data_strip is True
        assert model.icmp_ping_zero_id_discard is True
        assert model.icmp_frag_discard is True
        assert model.icmp_large_packet_discard is True
        assert model.discard_icmp_embedded_error is True
        assert model.suppress_icmp_timeexceeded is True
        assert model.suppress_icmp_needfrag is True


class TestExtraFieldsForbidden:
    """Tests for extra='forbid' validation on all Zone Protection Profile models."""

    def test_create_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on ZoneProtectionProfileCreateModel."""
        data = {
            "name": "test-profile",
            "folder": "Test Folder",
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            ZoneProtectionProfileCreateModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_update_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on ZoneProtectionProfileUpdateModel."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-profile",
            "folder": "Test Folder",
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            ZoneProtectionProfileUpdateModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_response_model_extra_fields_ignored(self):
        """Test that extra fields are silently ignored on ZoneProtectionProfileResponseModel."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-profile",
            "folder": "Test Folder",
            "unknown_field": "should_be_ignored",
        }
        model = ZoneProtectionProfileResponseModel(**data)
        assert not hasattr(model, "unknown_field")

    def test_flood_red_extra_fields_forbidden(self):
        """Test that extra fields are rejected on FloodRed."""
        with pytest.raises(ValidationError) as exc_info:
            FloodRed(alarm_rate=100, unknown_field="should_fail")
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_tcp_syn_flood_extra_fields_forbidden(self):
        """Test that extra fields are rejected on TcpSynFlood."""
        with pytest.raises(ValidationError) as exc_info:
            TcpSynFlood(enable=True, unknown_field="should_fail")
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_scan_entry_extra_fields_forbidden(self):
        """Test that extra fields are rejected on ScanEntry."""
        with pytest.raises(ValidationError) as exc_info:
            ScanEntry(name="8001", unknown_field="should_fail")
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_non_ip_protocol_entry_extra_fields_forbidden(self):
        """Test that extra fields are rejected on NonIpProtocolEntry."""
        with pytest.raises(ValidationError) as exc_info:
            NonIpProtocolEntry(name="ARP", ether_type="0x0806", unknown_field="should_fail")
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_sgt_entry_extra_fields_forbidden(self):
        """Test that extra fields are rejected on SgtEntry."""
        with pytest.raises(ValidationError) as exc_info:
            SgtEntry(name="test", tag="0x0001", unknown_field="should_fail")
        assert "Extra inputs are not permitted" in str(exc_info.value)
