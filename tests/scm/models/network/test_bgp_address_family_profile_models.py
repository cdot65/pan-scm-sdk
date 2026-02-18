"""Test models for BGP Address Family Profiles."""

from uuid import UUID

from pydantic import ValidationError
import pytest

from scm.models.network import (
    BgpAddressFamily,
    BgpAddressFamilyAddPath,
    BgpAddressFamilyAllowasIn,
    BgpAddressFamilyMaximumPrefix,
    BgpAddressFamilyMaximumPrefixAction,
    BgpAddressFamilyMaximumPrefixRestart,
    BgpAddressFamilyNextHop,
    BgpAddressFamilyOrf,
    BgpAddressFamilyProfileBaseModel,
    BgpAddressFamilyProfileCreateModel,
    BgpAddressFamilyProfileIpv4UnicastMulticast,
    BgpAddressFamilyProfileResponseModel,
    BgpAddressFamilyProfileUpdateModel,
    BgpAddressFamilyRemovePrivateAS,
    BgpAddressFamilySendCommunity,
)


class TestBgpAddressFamilyAddPath:
    """Test BGP address family add-path nested model."""

    def test_valid_add_path(self):
        """Test valid add-path configuration."""
        ap = BgpAddressFamilyAddPath(tx_all_paths=True, tx_bestpath_per_AS=False)
        assert ap.tx_all_paths is True
        assert ap.tx_bestpath_per_AS is False

    def test_add_path_optional_fields(self):
        """Test add-path with no fields set."""
        ap = BgpAddressFamilyAddPath()
        assert ap.tx_all_paths is None
        assert ap.tx_bestpath_per_AS is None

    def test_add_path_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            BgpAddressFamilyAddPath(tx_all_paths=True, unknown="fail")
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestBgpAddressFamilyAllowasIn:
    """Test BGP address family allowas-in nested model (oneOf: origin or occurrence)."""

    def test_valid_with_origin(self):
        """Test valid allowas-in with origin."""
        allow = BgpAddressFamilyAllowasIn(origin={})
        assert allow.origin == {}
        assert allow.occurrence is None

    def test_valid_with_occurrence(self):
        """Test valid allowas-in with occurrence."""
        allow = BgpAddressFamilyAllowasIn(occurrence=5)
        assert allow.occurrence == 5
        assert allow.origin is None

    def test_origin_and_occurrence_mutually_exclusive(self):
        """Test that origin and occurrence are mutually exclusive."""
        with pytest.raises(ValueError) as exc_info:
            BgpAddressFamilyAllowasIn(origin={}, occurrence=5)
        assert "'origin' and 'occurrence' are mutually exclusive" in str(exc_info.value)

    def test_occurrence_range(self):
        """Test occurrence boundary values."""
        # Valid min
        allow = BgpAddressFamilyAllowasIn(occurrence=1)
        assert allow.occurrence == 1

        # Valid max
        allow = BgpAddressFamilyAllowasIn(occurrence=10)
        assert allow.occurrence == 10

        # Out of range
        with pytest.raises(ValidationError):
            BgpAddressFamilyAllowasIn(occurrence=0)

        with pytest.raises(ValidationError):
            BgpAddressFamilyAllowasIn(occurrence=11)


class TestBgpAddressFamilyMaximumPrefixRestart:
    """Test maximum prefix restart nested model."""

    def test_valid_restart(self):
        """Test valid restart configuration."""
        restart = BgpAddressFamilyMaximumPrefixRestart(interval=300)
        assert restart.interval == 300

    def test_restart_interval_range(self):
        """Test restart interval boundary values."""
        restart = BgpAddressFamilyMaximumPrefixRestart(interval=1)
        assert restart.interval == 1

        restart = BgpAddressFamilyMaximumPrefixRestart(interval=65535)
        assert restart.interval == 65535

        with pytest.raises(ValidationError):
            BgpAddressFamilyMaximumPrefixRestart(interval=0)

        with pytest.raises(ValidationError):
            BgpAddressFamilyMaximumPrefixRestart(interval=65536)


class TestBgpAddressFamilyMaximumPrefixAction:
    """Test maximum prefix action model (oneOf: warning_only or restart)."""

    def test_valid_warning_only(self):
        """Test valid warning_only action."""
        action = BgpAddressFamilyMaximumPrefixAction(warning_only={})
        assert action.warning_only == {}
        assert action.restart is None

    def test_valid_restart(self):
        """Test valid restart action."""
        action = BgpAddressFamilyMaximumPrefixAction(
            restart=BgpAddressFamilyMaximumPrefixRestart(interval=300)
        )
        assert action.restart.interval == 300
        assert action.warning_only is None

    def test_warning_only_and_restart_mutually_exclusive(self):
        """Test that warning_only and restart are mutually exclusive."""
        with pytest.raises(ValueError) as exc_info:
            BgpAddressFamilyMaximumPrefixAction(
                warning_only={},
                restart=BgpAddressFamilyMaximumPrefixRestart(interval=300),
            )
        assert "'warning_only' and 'restart' are mutually exclusive" in str(exc_info.value)


class TestBgpAddressFamilyMaximumPrefix:
    """Test maximum prefix nested model."""

    def test_valid_maximum_prefix(self):
        """Test valid maximum prefix configuration."""
        mp = BgpAddressFamilyMaximumPrefix(
            num_prefixes=1000,
            threshold=80,
            action=BgpAddressFamilyMaximumPrefixAction(warning_only={}),
        )
        assert mp.num_prefixes == 1000
        assert mp.threshold == 80
        assert mp.action.warning_only == {}

    def test_num_prefixes_range(self):
        """Test num_prefixes boundary values."""
        mp = BgpAddressFamilyMaximumPrefix(num_prefixes=1)
        assert mp.num_prefixes == 1

        mp = BgpAddressFamilyMaximumPrefix(num_prefixes=4294967295)
        assert mp.num_prefixes == 4294967295

        with pytest.raises(ValidationError):
            BgpAddressFamilyMaximumPrefix(num_prefixes=0)

    def test_threshold_range(self):
        """Test threshold boundary values."""
        mp = BgpAddressFamilyMaximumPrefix(threshold=1)
        assert mp.threshold == 1

        mp = BgpAddressFamilyMaximumPrefix(threshold=100)
        assert mp.threshold == 100

        with pytest.raises(ValidationError):
            BgpAddressFamilyMaximumPrefix(threshold=0)

        with pytest.raises(ValidationError):
            BgpAddressFamilyMaximumPrefix(threshold=101)


class TestBgpAddressFamilyNextHop:
    """Test next-hop model (oneOf: self or self_force)."""

    def test_valid_self(self):
        """Test valid next-hop self."""
        nh = BgpAddressFamilyNextHop(**{"self": {}})
        assert nh.self_ == {}
        assert nh.self_force is None

    def test_valid_self_force(self):
        """Test valid next-hop self_force."""
        nh = BgpAddressFamilyNextHop(self_force={})
        assert nh.self_force == {}
        assert nh.self_ is None

    def test_self_and_self_force_mutually_exclusive(self):
        """Test that self and self_force are mutually exclusive."""
        with pytest.raises(ValueError) as exc_info:
            BgpAddressFamilyNextHop(**{"self": {}, "self_force": {}})
        assert "'self' and 'self_force' are mutually exclusive" in str(exc_info.value)


class TestBgpAddressFamilyRemovePrivateAS:
    """Test remove-private-AS model (oneOf: all or replace_AS)."""

    def test_valid_all(self):
        """Test valid remove-private-AS all."""
        rp = BgpAddressFamilyRemovePrivateAS(all={})
        assert rp.all == {}
        assert rp.replace_AS is None

    def test_valid_replace_AS(self):
        """Test valid remove-private-AS replace_AS."""
        rp = BgpAddressFamilyRemovePrivateAS(replace_AS={})
        assert rp.replace_AS == {}
        assert rp.all is None

    def test_all_and_replace_AS_mutually_exclusive(self):
        """Test that all and replace_AS are mutually exclusive."""
        with pytest.raises(ValueError) as exc_info:
            BgpAddressFamilyRemovePrivateAS(all={}, replace_AS={})
        assert "'all' and 'replace_AS' are mutually exclusive" in str(exc_info.value)


class TestBgpAddressFamilySendCommunity:
    """Test send-community model (oneOf: all, both, extended, large, standard)."""

    def test_valid_all(self):
        """Test valid send-community all."""
        sc = BgpAddressFamilySendCommunity(all={})
        assert sc.all == {}

    def test_valid_both(self):
        """Test valid send-community both."""
        sc = BgpAddressFamilySendCommunity(both={})
        assert sc.both == {}

    def test_valid_extended(self):
        """Test valid send-community extended."""
        sc = BgpAddressFamilySendCommunity(extended={})
        assert sc.extended == {}

    def test_valid_large(self):
        """Test valid send-community large."""
        sc = BgpAddressFamilySendCommunity(large={})
        assert sc.large == {}

    def test_valid_standard(self):
        """Test valid send-community standard."""
        sc = BgpAddressFamilySendCommunity(standard={})
        assert sc.standard == {}

    def test_multiple_send_community_types_fail(self):
        """Test that multiple send community types fail."""
        with pytest.raises(ValueError) as exc_info:
            BgpAddressFamilySendCommunity(all={}, both={})
        assert "At most one send community type can be set" in str(exc_info.value)

    def test_no_send_community_is_valid(self):
        """Test that no send community type is valid."""
        sc = BgpAddressFamilySendCommunity()
        assert sc.all is None
        assert sc.both is None


class TestBgpAddressFamilyOrf:
    """Test BGP address family ORF nested model."""

    def test_valid_orf_values(self):
        """Test valid ORF prefix list values."""
        for value in ["none", "both", "receive", "send"]:
            orf = BgpAddressFamilyOrf(orf_prefix_list=value)
            assert orf.orf_prefix_list == value

    def test_invalid_orf_value(self):
        """Test invalid ORF prefix list value."""
        with pytest.raises(ValidationError):
            BgpAddressFamilyOrf(orf_prefix_list="invalid")

    def test_orf_optional(self):
        """Test ORF with no fields set."""
        orf = BgpAddressFamilyOrf()
        assert orf.orf_prefix_list is None


class TestBgpAddressFamily:
    """Test core BGP address family configuration model."""

    def test_valid_minimal(self):
        """Test valid address family with minimal fields."""
        af = BgpAddressFamily(enable=True)
        assert af.enable is True
        assert af.soft_reconfig_with_stored_info is None

    def test_valid_all_fields(self):
        """Test valid address family with all fields populated."""
        af = BgpAddressFamily(
            enable=True,
            soft_reconfig_with_stored_info=True,
            add_path=BgpAddressFamilyAddPath(tx_all_paths=True),
            as_override=True,
            route_reflector_client=True,
            default_originate=True,
            default_originate_map="my-route-map",
            allowas_in=BgpAddressFamilyAllowasIn(occurrence=3),
            maximum_prefix=BgpAddressFamilyMaximumPrefix(num_prefixes=1000, threshold=80),
            next_hop=BgpAddressFamilyNextHop(**{"self": {}}),
            remove_private_AS=BgpAddressFamilyRemovePrivateAS(all={}),
            send_community=BgpAddressFamilySendCommunity(all={}),
            orf=BgpAddressFamilyOrf(orf_prefix_list="both"),
        )
        assert af.enable is True
        assert af.soft_reconfig_with_stored_info is True
        assert af.add_path.tx_all_paths is True
        assert af.as_override is True
        assert af.route_reflector_client is True
        assert af.default_originate is True
        assert af.default_originate_map == "my-route-map"
        assert af.allowas_in.occurrence == 3
        assert af.maximum_prefix.num_prefixes == 1000
        assert af.next_hop.self_ == {}
        assert af.remove_private_AS.all == {}
        assert af.send_community.all == {}
        assert af.orf.orf_prefix_list == "both"


class TestBgpAddressFamilyProfileIpv4Wrappers:
    """Test IPv4 unicast/multicast model."""

    def test_valid_unicast_multicast(self):
        """Test valid unicast/multicast container."""
        um = BgpAddressFamilyProfileIpv4UnicastMulticast(
            unicast=BgpAddressFamily(enable=True),
            multicast=BgpAddressFamily(enable=False),
        )
        assert um.unicast.enable is True
        assert um.multicast.enable is False

    def test_optional_fields(self):
        """Test optional fields on unicast/multicast model."""
        um = BgpAddressFamilyProfileIpv4UnicastMulticast()
        assert um.unicast is None
        assert um.multicast is None


class TestBgpAddressFamilyProfileBaseModel:
    """Test BGP Address Family Profile base model validation."""

    def test_valid_minimal_fields(self):
        """Test valid model with only required fields."""
        model = BgpAddressFamilyProfileBaseModel(name="test-af", folder="Test Folder")
        assert model.name == "test-af"
        assert model.folder == "Test Folder"
        assert model.ipv4 is None

    def test_valid_all_fields(self):
        """Test valid model with all fields populated."""
        model = BgpAddressFamilyProfileBaseModel(
            name="test-af",
            folder="Test Folder",
            ipv4=BgpAddressFamilyProfileIpv4UnicastMulticast(
                unicast=BgpAddressFamily(
                    enable=True,
                    soft_reconfig_with_stored_info=True,
                    allowas_in=BgpAddressFamilyAllowasIn(occurrence=3),
                ),
                multicast=BgpAddressFamily(enable=False),
            ),
        )
        assert model.name == "test-af"
        assert model.ipv4.unicast.enable is True
        assert model.ipv4.unicast.allowas_in.occurrence == 3
        assert model.ipv4.multicast.enable is False

    def test_missing_name_raises_error(self):
        """Test that missing name field raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            BgpAddressFamilyProfileBaseModel(folder="Test Folder")
        assert "name" in str(exc_info.value)

    def test_container_folder(self):
        """Test model with folder container."""
        model = BgpAddressFamilyProfileBaseModel(name="test", folder="MyFolder")
        assert model.folder == "MyFolder"
        assert model.snippet is None
        assert model.device is None

    def test_container_snippet(self):
        """Test model with snippet container."""
        model = BgpAddressFamilyProfileBaseModel(name="test", snippet="MySnippet")
        assert model.snippet == "MySnippet"
        assert model.folder is None

    def test_container_device(self):
        """Test model with device container."""
        model = BgpAddressFamilyProfileBaseModel(name="test", device="MyDevice")
        assert model.device == "MyDevice"
        assert model.folder is None

    def test_container_max_length(self):
        """Test container field max_length validation."""
        model = BgpAddressFamilyProfileBaseModel(name="test", folder="A" * 64)
        assert len(model.folder) == 64

        with pytest.raises(ValidationError):
            BgpAddressFamilyProfileBaseModel(name="test", folder="A" * 65)

    def test_container_pattern_validation(self):
        """Test container field pattern validation."""
        model = BgpAddressFamilyProfileBaseModel(name="test", folder="My-Folder_1.0")
        assert model.folder == "My-Folder_1.0"

        with pytest.raises(ValidationError):
            BgpAddressFamilyProfileBaseModel(name="test", folder="Folder@#$")


class TestBgpAddressFamilyProfileCreateModel:
    """Test BGP Address Family Profile create model."""

    def test_valid_create_with_folder(self):
        """Test valid create model with folder container."""
        model = BgpAddressFamilyProfileCreateModel(
            name="test-af",
            folder="Test Folder",
        )
        assert model.name == "test-af"
        assert model.folder == "Test Folder"

    def test_valid_create_with_snippet(self):
        """Test valid create model with snippet container."""
        model = BgpAddressFamilyProfileCreateModel(
            name="test-af",
            snippet="MySnippet",
        )
        assert model.snippet == "MySnippet"

    def test_valid_create_with_device(self):
        """Test valid create model with device container."""
        model = BgpAddressFamilyProfileCreateModel(
            name="test-af",
            device="MyDevice",
        )
        assert model.device == "MyDevice"

    def test_create_no_container_raises_error(self):
        """Test that create without any container raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            BgpAddressFamilyProfileCreateModel(name="test-af")
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_create_multiple_containers_raises_error(self):
        """Test that create with multiple containers raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            BgpAddressFamilyProfileCreateModel(
                name="test-af",
                folder="Test Folder",
                snippet="MySnippet",
            )
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_create_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on BgpAddressFamilyProfileCreateModel."""
        with pytest.raises(ValidationError) as exc_info:
            BgpAddressFamilyProfileCreateModel(
                name="test",
                folder="Test Folder",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestBgpAddressFamilyProfileUpdateModel:
    """Test BGP Address Family Profile update model."""

    def test_valid_update_model(self):
        """Test valid update model."""
        model = BgpAddressFamilyProfileUpdateModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="updated-af",
            folder="Test Folder",
        )
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "updated-af"

    def test_invalid_uuid(self):
        """Test update model with invalid UUID."""
        with pytest.raises(ValidationError):
            BgpAddressFamilyProfileUpdateModel(
                id="not-a-uuid",
                name="test",
                folder="Test Folder",
            )


class TestBgpAddressFamilyProfileResponseModel:
    """Test BGP Address Family Profile response model."""

    def test_valid_response_model(self):
        """Test valid response model."""
        model = BgpAddressFamilyProfileResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="response-af",
            folder="Test Folder",
        )
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "response-af"

    def test_missing_id_raises_error(self):
        """Test that missing id field raises ValidationError."""
        with pytest.raises(ValidationError):
            BgpAddressFamilyProfileResponseModel(
                name="test",
                folder="Test Folder",
            )


class TestExtraFieldsBgpAddressFamilyProfile:
    """Tests for extra field handling on BGP Address Family Profile models."""

    def test_base_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on BgpAddressFamilyProfileBaseModel."""
        with pytest.raises(ValidationError) as exc_info:
            BgpAddressFamilyProfileBaseModel(
                name="test",
                folder="Test Folder",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_update_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on BgpAddressFamilyProfileUpdateModel."""
        with pytest.raises(ValidationError) as exc_info:
            BgpAddressFamilyProfileUpdateModel(
                id="123e4567-e89b-12d3-a456-426655440000",
                name="test",
                folder="Test Folder",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_response_model_extra_fields_ignored(self):
        """Test that extra fields are silently ignored on BgpAddressFamilyProfileResponseModel."""
        model = BgpAddressFamilyProfileResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test",
            folder="Test Folder",
            unknown_field="should_be_ignored",
        )
        assert not hasattr(model, "unknown_field")
