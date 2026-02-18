"""Test models for Route Prefix Lists."""

from uuid import UUID

from pydantic import ValidationError
import pytest

from scm.models.network import (
    RoutePrefixListBaseModel,
    RoutePrefixListCreateModel,
    RoutePrefixListIpv4,
    RoutePrefixListIpv4Entry,
    RoutePrefixListPrefix,
    RoutePrefixListPrefixEntry,
    RoutePrefixListResponseModel,
    RoutePrefixListUpdateModel,
)


class TestRoutePrefixListPrefixEntry:
    """Test route prefix list prefix entry nested model."""

    def test_valid_prefix_entry(self):
        """Test valid prefix entry configuration."""
        entry = RoutePrefixListPrefixEntry(
            network="10.0.0.0/8",
            greater_than_or_equal=16,
            less_than_or_equal=24,
        )
        assert entry.network == "10.0.0.0/8"
        assert entry.greater_than_or_equal == 16
        assert entry.less_than_or_equal == 24

    def test_prefix_entry_optional_fields(self):
        """Test prefix entry with no fields set."""
        entry = RoutePrefixListPrefixEntry()
        assert entry.network is None
        assert entry.greater_than_or_equal is None
        assert entry.less_than_or_equal is None

    def test_prefix_entry_ge_range(self):
        """Test greater_than_or_equal boundary values."""
        # Valid min
        entry = RoutePrefixListPrefixEntry(greater_than_or_equal=0)
        assert entry.greater_than_or_equal == 0

        # Valid max
        entry = RoutePrefixListPrefixEntry(greater_than_or_equal=32)
        assert entry.greater_than_or_equal == 32

        # Out of range
        with pytest.raises(ValidationError):
            RoutePrefixListPrefixEntry(greater_than_or_equal=-1)

        with pytest.raises(ValidationError):
            RoutePrefixListPrefixEntry(greater_than_or_equal=33)

    def test_prefix_entry_le_range(self):
        """Test less_than_or_equal boundary values."""
        entry = RoutePrefixListPrefixEntry(less_than_or_equal=0)
        assert entry.less_than_or_equal == 0

        entry = RoutePrefixListPrefixEntry(less_than_or_equal=32)
        assert entry.less_than_or_equal == 32

        with pytest.raises(ValidationError):
            RoutePrefixListPrefixEntry(less_than_or_equal=-1)

        with pytest.raises(ValidationError):
            RoutePrefixListPrefixEntry(less_than_or_equal=33)

    def test_prefix_entry_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RoutePrefixListPrefixEntry(network="10.0.0.0/8", unknown="fail")
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestRoutePrefixListPrefix:
    """Test route prefix list prefix model (oneOf: network or entry)."""

    def test_valid_prefix_with_network_any(self):
        """Test valid prefix with network='any'."""
        prefix = RoutePrefixListPrefix(network="any")
        assert prefix.network == "any"
        assert prefix.entry is None

    def test_valid_prefix_with_entry(self):
        """Test valid prefix with entry configuration."""
        prefix = RoutePrefixListPrefix(
            entry=RoutePrefixListPrefixEntry(
                network="10.0.0.0/8",
                greater_than_or_equal=16,
            )
        )
        assert prefix.network is None
        assert prefix.entry.network == "10.0.0.0/8"

    def test_network_and_entry_mutually_exclusive(self):
        """Test that network and entry are mutually exclusive."""
        with pytest.raises(ValueError) as exc_info:
            RoutePrefixListPrefix(
                network="any",
                entry=RoutePrefixListPrefixEntry(network="10.0.0.0/8"),
            )
        assert "'network' and 'entry' are mutually exclusive" in str(exc_info.value)

    def test_network_pattern_validation(self):
        """Test that network field only accepts 'any'."""
        with pytest.raises(ValidationError):
            RoutePrefixListPrefix(network="all")

        with pytest.raises(ValidationError):
            RoutePrefixListPrefix(network="10.0.0.0/8")

    def test_prefix_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RoutePrefixListPrefix(network="any", unknown="fail")
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestRoutePrefixListIpv4Entry:
    """Test route prefix list IPv4 entry nested model."""

    def test_valid_ipv4_entry(self):
        """Test valid IPv4 entry configuration."""
        entry = RoutePrefixListIpv4Entry(
            name=10,
            action="permit",
            prefix=RoutePrefixListPrefix(network="any"),
        )
        assert entry.name == 10
        assert entry.action == "permit"
        assert entry.prefix.network == "any"

    def test_ipv4_entry_optional_fields(self):
        """Test IPv4 entry with no fields set."""
        entry = RoutePrefixListIpv4Entry()
        assert entry.name is None
        assert entry.action is None
        assert entry.prefix is None

    def test_ipv4_entry_name_range(self):
        """Test entry name (sequence number) boundary values."""
        entry = RoutePrefixListIpv4Entry(name=1)
        assert entry.name == 1

        entry = RoutePrefixListIpv4Entry(name=65535)
        assert entry.name == 65535

        with pytest.raises(ValidationError):
            RoutePrefixListIpv4Entry(name=0)

        with pytest.raises(ValidationError):
            RoutePrefixListIpv4Entry(name=65536)

    def test_ipv4_entry_action_valid_values(self):
        """Test entry action field with valid values."""
        for action in ["deny", "permit"]:
            entry = RoutePrefixListIpv4Entry(action=action)
            assert entry.action == action

    def test_ipv4_entry_action_invalid_value(self):
        """Test entry action field with invalid value."""
        with pytest.raises(ValidationError):
            RoutePrefixListIpv4Entry(action="allow")

    def test_ipv4_entry_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RoutePrefixListIpv4Entry(name=1, unknown="fail")
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestRoutePrefixListIpv4:
    """Test route prefix list IPv4 container model."""

    def test_valid_ipv4_container(self):
        """Test valid IPv4 container with entries."""
        ipv4 = RoutePrefixListIpv4(
            ipv4_entry=[
                RoutePrefixListIpv4Entry(name=10, action="permit"),
                RoutePrefixListIpv4Entry(name=20, action="deny"),
            ]
        )
        assert len(ipv4.ipv4_entry) == 2

    def test_ipv4_container_optional(self):
        """Test IPv4 container with no entries."""
        ipv4 = RoutePrefixListIpv4()
        assert ipv4.ipv4_entry is None


class TestRoutePrefixListBaseModel:
    """Test Route Prefix List base model validation."""

    def test_valid_minimal_fields(self):
        """Test valid model with only required fields."""
        model = RoutePrefixListBaseModel(name="test-prefix", folder="Test Folder")
        assert model.name == "test-prefix"
        assert model.folder == "Test Folder"
        assert model.description is None
        assert model.ipv4 is None

    def test_valid_all_fields(self):
        """Test valid model with all fields populated."""
        model = RoutePrefixListBaseModel(
            name="test-prefix",
            folder="Test Folder",
            description="My prefix list",
            ipv4=RoutePrefixListIpv4(
                ipv4_entry=[
                    RoutePrefixListIpv4Entry(
                        name=10,
                        action="permit",
                        prefix=RoutePrefixListPrefix(
                            entry=RoutePrefixListPrefixEntry(
                                network="10.0.0.0/8",
                                greater_than_or_equal=16,
                                less_than_or_equal=24,
                            )
                        ),
                    )
                ]
            ),
        )
        assert model.name == "test-prefix"
        assert model.description == "My prefix list"
        assert model.ipv4.ipv4_entry[0].action == "permit"

    def test_missing_name_raises_error(self):
        """Test that missing name field raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            RoutePrefixListBaseModel(folder="Test Folder")
        assert "name" in str(exc_info.value)

    def test_container_folder(self):
        """Test model with folder container."""
        model = RoutePrefixListBaseModel(name="test", folder="MyFolder")
        assert model.folder == "MyFolder"
        assert model.snippet is None
        assert model.device is None

    def test_container_snippet(self):
        """Test model with snippet container."""
        model = RoutePrefixListBaseModel(name="test", snippet="MySnippet")
        assert model.snippet == "MySnippet"
        assert model.folder is None

    def test_container_device(self):
        """Test model with device container."""
        model = RoutePrefixListBaseModel(name="test", device="MyDevice")
        assert model.device == "MyDevice"
        assert model.folder is None

    def test_container_max_length(self):
        """Test container field max_length validation."""
        model = RoutePrefixListBaseModel(name="test", folder="A" * 64)
        assert len(model.folder) == 64

        with pytest.raises(ValidationError):
            RoutePrefixListBaseModel(name="test", folder="A" * 65)

    def test_container_pattern_validation(self):
        """Test container field pattern validation."""
        model = RoutePrefixListBaseModel(name="test", folder="My-Folder_1.0")
        assert model.folder == "My-Folder_1.0"

        with pytest.raises(ValidationError):
            RoutePrefixListBaseModel(name="test", folder="Folder@#$")


class TestRoutePrefixListCreateModel:
    """Test Route Prefix List create model."""

    def test_valid_create_with_folder(self):
        """Test valid create model with folder container."""
        model = RoutePrefixListCreateModel(
            name="test-prefix",
            folder="Test Folder",
        )
        assert model.name == "test-prefix"
        assert model.folder == "Test Folder"

    def test_valid_create_with_snippet(self):
        """Test valid create model with snippet container."""
        model = RoutePrefixListCreateModel(
            name="test-prefix",
            snippet="MySnippet",
        )
        assert model.snippet == "MySnippet"

    def test_valid_create_with_device(self):
        """Test valid create model with device container."""
        model = RoutePrefixListCreateModel(
            name="test-prefix",
            device="MyDevice",
        )
        assert model.device == "MyDevice"

    def test_create_no_container_raises_error(self):
        """Test that create without any container raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            RoutePrefixListCreateModel(name="test-prefix")
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_create_multiple_containers_raises_error(self):
        """Test that create with multiple containers raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            RoutePrefixListCreateModel(
                name="test-prefix",
                folder="Test Folder",
                snippet="MySnippet",
            )
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_create_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on RoutePrefixListCreateModel."""
        with pytest.raises(ValidationError) as exc_info:
            RoutePrefixListCreateModel(
                name="test",
                folder="Test Folder",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestRoutePrefixListUpdateModel:
    """Test Route Prefix List update model."""

    def test_valid_update_model(self):
        """Test valid update model."""
        model = RoutePrefixListUpdateModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="updated-prefix",
            folder="Test Folder",
            description="Updated description",
        )
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "updated-prefix"

    def test_invalid_uuid(self):
        """Test update model with invalid UUID."""
        with pytest.raises(ValidationError):
            RoutePrefixListUpdateModel(
                id="not-a-uuid",
                name="test",
                folder="Test Folder",
            )


class TestRoutePrefixListResponseModel:
    """Test Route Prefix List response model."""

    def test_valid_response_model(self):
        """Test valid response model."""
        model = RoutePrefixListResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="response-prefix",
            folder="Test Folder",
            description="A response prefix list",
        )
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "response-prefix"

    def test_missing_id_raises_error(self):
        """Test that missing id field raises ValidationError."""
        with pytest.raises(ValidationError):
            RoutePrefixListResponseModel(
                name="test",
                folder="Test Folder",
            )


class TestExtraFieldsRoutePrefixList:
    """Tests for extra field handling on Route Prefix List models."""

    def test_base_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on RoutePrefixListBaseModel."""
        with pytest.raises(ValidationError) as exc_info:
            RoutePrefixListBaseModel(
                name="test",
                folder="Test Folder",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_update_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on RoutePrefixListUpdateModel."""
        with pytest.raises(ValidationError) as exc_info:
            RoutePrefixListUpdateModel(
                id="123e4567-e89b-12d3-a456-426655440000",
                name="test",
                folder="Test Folder",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_response_model_extra_fields_ignored(self):
        """Test that extra fields are silently ignored on RoutePrefixListResponseModel."""
        model = RoutePrefixListResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test",
            folder="Test Folder",
            unknown_field="should_be_ignored",
        )
        assert not hasattr(model, "unknown_field")
