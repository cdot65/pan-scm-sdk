"""Test models for Route Access Lists."""

from uuid import UUID

from pydantic import ValidationError
import pytest

from scm.models.network import (
    RouteAccessListBaseModel,
    RouteAccessListCreateModel,
    RouteAccessListDestinationAddress,
    RouteAccessListIpv4,
    RouteAccessListIpv4Entry,
    RouteAccessListResponseModel,
    RouteAccessListSourceAddress,
    RouteAccessListType,
    RouteAccessListUpdateModel,
)


class TestRouteAccessListSourceAddress:
    """Test route access list source address nested model."""

    def test_valid_source_address(self):
        """Test valid source address configuration."""
        addr = RouteAccessListSourceAddress(address="192.168.1.0", wildcard="0.0.0.255")
        assert addr.address == "192.168.1.0"
        assert addr.wildcard == "0.0.0.255"

    def test_source_address_optional_fields(self):
        """Test source address with no fields set."""
        addr = RouteAccessListSourceAddress()
        assert addr.address is None
        assert addr.wildcard is None

    def test_source_address_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RouteAccessListSourceAddress(address="10.0.0.0", unknown="fail")
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestRouteAccessListDestinationAddress:
    """Test route access list destination address nested model."""

    def test_valid_destination_address(self):
        """Test valid destination address configuration."""
        addr = RouteAccessListDestinationAddress(address="10.0.0.0", wildcard="0.0.255.255")
        assert addr.address == "10.0.0.0"
        assert addr.wildcard == "0.0.255.255"

    def test_destination_address_optional_fields(self):
        """Test destination address with no fields set."""
        addr = RouteAccessListDestinationAddress()
        assert addr.address is None
        assert addr.wildcard is None

    def test_destination_address_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RouteAccessListDestinationAddress(address="10.0.0.0", unknown="fail")
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestRouteAccessListIpv4Entry:
    """Test route access list IPv4 entry nested model."""

    def test_valid_entry(self):
        """Test valid IPv4 entry configuration."""
        entry = RouteAccessListIpv4Entry(
            name=10,
            action="permit",
            source_address=RouteAccessListSourceAddress(
                address="192.168.1.0", wildcard="0.0.0.255"
            ),
            destination_address=RouteAccessListDestinationAddress(
                address="10.0.0.0", wildcard="0.0.255.255"
            ),
        )
        assert entry.name == 10
        assert entry.action == "permit"
        assert entry.source_address.address == "192.168.1.0"
        assert entry.destination_address.address == "10.0.0.0"

    def test_entry_optional_fields(self):
        """Test IPv4 entry with no fields set."""
        entry = RouteAccessListIpv4Entry()
        assert entry.name is None
        assert entry.action is None
        assert entry.source_address is None
        assert entry.destination_address is None

    def test_entry_name_range(self):
        """Test entry name (sequence number) boundary values."""
        # Valid min
        entry = RouteAccessListIpv4Entry(name=1)
        assert entry.name == 1

        # Valid max
        entry = RouteAccessListIpv4Entry(name=65535)
        assert entry.name == 65535

        # Out of range
        with pytest.raises(ValidationError):
            RouteAccessListIpv4Entry(name=0)

        with pytest.raises(ValidationError):
            RouteAccessListIpv4Entry(name=65536)

    def test_entry_action_valid_values(self):
        """Test entry action field with valid values."""
        for action in ["deny", "permit"]:
            entry = RouteAccessListIpv4Entry(action=action)
            assert entry.action == action

    def test_entry_action_invalid_value(self):
        """Test entry action field with invalid value."""
        with pytest.raises(ValidationError):
            RouteAccessListIpv4Entry(action="allow")

    def test_entry_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RouteAccessListIpv4Entry(name=1, unknown="fail")
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestRouteAccessListIpv4:
    """Test route access list IPv4 container model."""

    def test_valid_ipv4_container(self):
        """Test valid IPv4 container with entries."""
        ipv4 = RouteAccessListIpv4(
            ipv4_entry=[
                RouteAccessListIpv4Entry(name=10, action="permit"),
                RouteAccessListIpv4Entry(name=20, action="deny"),
            ]
        )
        assert len(ipv4.ipv4_entry) == 2
        assert ipv4.ipv4_entry[0].name == 10
        assert ipv4.ipv4_entry[1].action == "deny"

    def test_ipv4_container_optional(self):
        """Test IPv4 container with no entries."""
        ipv4 = RouteAccessListIpv4()
        assert ipv4.ipv4_entry is None


class TestRouteAccessListType:
    """Test route access list type container model."""

    def test_valid_type_container(self):
        """Test valid type container with IPv4."""
        acl_type = RouteAccessListType(
            ipv4=RouteAccessListIpv4(
                ipv4_entry=[RouteAccessListIpv4Entry(name=10, action="permit")]
            )
        )
        assert acl_type.ipv4 is not None
        assert len(acl_type.ipv4.ipv4_entry) == 1

    def test_type_container_optional(self):
        """Test type container with no fields."""
        acl_type = RouteAccessListType()
        assert acl_type.ipv4 is None


class TestRouteAccessListBaseModel:
    """Test Route Access List base model validation."""

    def test_valid_minimal_fields(self):
        """Test valid model with only required fields."""
        model = RouteAccessListBaseModel(name="test-acl", folder="Test Folder")
        assert model.name == "test-acl"
        assert model.folder == "Test Folder"
        assert model.description is None
        assert model.type is None

    def test_valid_all_fields(self):
        """Test valid model with all fields populated."""
        model = RouteAccessListBaseModel(
            name="test-acl",
            folder="Test Folder",
            description="My access list",
            type=RouteAccessListType(
                ipv4=RouteAccessListIpv4(
                    ipv4_entry=[
                        RouteAccessListIpv4Entry(
                            name=10,
                            action="permit",
                            source_address=RouteAccessListSourceAddress(
                                address="10.0.0.0", wildcard="0.0.255.255"
                            ),
                        )
                    ]
                )
            ),
        )
        assert model.name == "test-acl"
        assert model.description == "My access list"
        assert model.type.ipv4.ipv4_entry[0].action == "permit"

    def test_missing_name_raises_error(self):
        """Test that missing name field raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            RouteAccessListBaseModel(folder="Test Folder")
        assert "name" in str(exc_info.value)

    def test_container_folder(self):
        """Test model with folder container."""
        model = RouteAccessListBaseModel(name="test", folder="MyFolder")
        assert model.folder == "MyFolder"
        assert model.snippet is None
        assert model.device is None

    def test_container_snippet(self):
        """Test model with snippet container."""
        model = RouteAccessListBaseModel(name="test", snippet="MySnippet")
        assert model.snippet == "MySnippet"
        assert model.folder is None

    def test_container_device(self):
        """Test model with device container."""
        model = RouteAccessListBaseModel(name="test", device="MyDevice")
        assert model.device == "MyDevice"
        assert model.folder is None

    def test_container_max_length(self):
        """Test container field max_length validation."""
        model = RouteAccessListBaseModel(name="test", folder="A" * 64)
        assert len(model.folder) == 64

        with pytest.raises(ValidationError):
            RouteAccessListBaseModel(name="test", folder="A" * 65)

    def test_container_pattern_validation(self):
        """Test container field pattern validation."""
        model = RouteAccessListBaseModel(name="test", folder="My-Folder_1.0")
        assert model.folder == "My-Folder_1.0"

        with pytest.raises(ValidationError):
            RouteAccessListBaseModel(name="test", folder="Folder@#$")


class TestRouteAccessListCreateModel:
    """Test Route Access List create model."""

    def test_valid_create_with_folder(self):
        """Test valid create model with folder container."""
        model = RouteAccessListCreateModel(
            name="test-acl",
            folder="Test Folder",
        )
        assert model.name == "test-acl"
        assert model.folder == "Test Folder"

    def test_valid_create_with_snippet(self):
        """Test valid create model with snippet container."""
        model = RouteAccessListCreateModel(
            name="test-acl",
            snippet="MySnippet",
        )
        assert model.snippet == "MySnippet"

    def test_valid_create_with_device(self):
        """Test valid create model with device container."""
        model = RouteAccessListCreateModel(
            name="test-acl",
            device="MyDevice",
        )
        assert model.device == "MyDevice"

    def test_create_no_container_raises_error(self):
        """Test that create without any container raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            RouteAccessListCreateModel(name="test-acl")
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_create_multiple_containers_raises_error(self):
        """Test that create with multiple containers raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            RouteAccessListCreateModel(
                name="test-acl",
                folder="Test Folder",
                snippet="MySnippet",
            )
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_create_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on RouteAccessListCreateModel."""
        with pytest.raises(ValidationError) as exc_info:
            RouteAccessListCreateModel(
                name="test",
                folder="Test Folder",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestRouteAccessListUpdateModel:
    """Test Route Access List update model."""

    def test_valid_update_model(self):
        """Test valid update model."""
        model = RouteAccessListUpdateModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="updated-acl",
            folder="Test Folder",
            description="Updated description",
        )
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "updated-acl"
        assert model.description == "Updated description"

    def test_invalid_uuid(self):
        """Test update model with invalid UUID."""
        with pytest.raises(ValidationError):
            RouteAccessListUpdateModel(
                id="not-a-uuid",
                name="test",
                folder="Test Folder",
            )


class TestRouteAccessListResponseModel:
    """Test Route Access List response model."""

    def test_valid_response_model(self):
        """Test valid response model."""
        model = RouteAccessListResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="response-acl",
            folder="Test Folder",
            description="A response ACL",
        )
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "response-acl"

    def test_missing_id_raises_error(self):
        """Test that missing id field raises ValidationError."""
        with pytest.raises(ValidationError):
            RouteAccessListResponseModel(
                name="test",
                folder="Test Folder",
            )


class TestExtraFieldsRouteAccessList:
    """Tests for extra field handling on Route Access List models."""

    def test_base_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on RouteAccessListBaseModel."""
        with pytest.raises(ValidationError) as exc_info:
            RouteAccessListBaseModel(
                name="test",
                folder="Test Folder",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_update_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on RouteAccessListUpdateModel."""
        with pytest.raises(ValidationError) as exc_info:
            RouteAccessListUpdateModel(
                id="123e4567-e89b-12d3-a456-426655440000",
                name="test",
                folder="Test Folder",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_response_model_extra_fields_ignored(self):
        """Test that extra fields are silently ignored on RouteAccessListResponseModel."""
        model = RouteAccessListResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test",
            folder="Test Folder",
            unknown_field="should_be_ignored",
        )
        assert not hasattr(model, "unknown_field")
