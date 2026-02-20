"""Test models for BGP Redistribution Profiles."""

from uuid import UUID

from pydantic import ValidationError
import pytest

from scm.models.network import (
    BgpRedistributionIpv4,
    BgpRedistributionProfileBaseModel,
    BgpRedistributionProfileCreateModel,
    BgpRedistributionProfileResponseModel,
    BgpRedistributionProfileUpdateModel,
    BgpRedistributionProtocol,
    BgpRedistributionUnicast,
)


class TestBgpRedistributionProtocol:
    """Test BGP redistribution protocol nested model."""

    def test_valid_protocol(self):
        """Test valid protocol with all fields."""
        proto = BgpRedistributionProtocol(enable=True, metric=100, route_map="my-rm")
        assert proto.enable is True
        assert proto.metric == 100
        assert proto.route_map == "my-rm"

    def test_protocol_optional_fields(self):
        """Test protocol with no fields set."""
        proto = BgpRedistributionProtocol()
        assert proto.enable is None
        assert proto.metric is None
        assert proto.route_map is None

    def test_metric_min_valid(self):
        """Test metric at minimum valid boundary (1)."""
        proto = BgpRedistributionProtocol(metric=1)
        assert proto.metric == 1

    def test_metric_max_valid(self):
        """Test metric at maximum valid boundary (65535)."""
        proto = BgpRedistributionProtocol(metric=65535)
        assert proto.metric == 65535

    def test_metric_below_min_invalid(self):
        """Test metric below minimum boundary (0) raises ValidationError."""
        with pytest.raises(ValidationError):
            BgpRedistributionProtocol(metric=0)

    def test_metric_above_max_invalid(self):
        """Test metric above maximum boundary (65536) raises ValidationError."""
        with pytest.raises(ValidationError):
            BgpRedistributionProtocol(metric=65536)

    def test_protocol_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            BgpRedistributionProtocol(enable=True, unknown="fail")
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestBgpRedistributionUnicast:
    """Test BGP redistribution unicast model (NOT mutually exclusive protocols)."""

    def test_valid_with_all_protocols(self):
        """Test valid unicast with all three protocols coexisting."""
        unicast = BgpRedistributionUnicast(
            static=BgpRedistributionProtocol(enable=True, metric=100),
            ospf=BgpRedistributionProtocol(enable=True, metric=200),
            connected=BgpRedistributionProtocol(enable=False, metric=300),
        )
        assert unicast.static.enable is True
        assert unicast.static.metric == 100
        assert unicast.ospf.enable is True
        assert unicast.ospf.metric == 200
        assert unicast.connected.enable is False
        assert unicast.connected.metric == 300

    def test_valid_with_single_protocol(self):
        """Test valid unicast with only one protocol."""
        unicast = BgpRedistributionUnicast(static=BgpRedistributionProtocol(enable=True))
        assert unicast.static.enable is True
        assert unicast.ospf is None
        assert unicast.connected is None

    def test_optional_fields(self):
        """Test unicast with no fields set."""
        unicast = BgpRedistributionUnicast()
        assert unicast.static is None
        assert unicast.ospf is None
        assert unicast.connected is None

    def test_unicast_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            BgpRedistributionUnicast(unknown="fail")
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestBgpRedistributionIpv4:
    """Test BGP redistribution IPv4 container model."""

    def test_valid_with_unicast(self):
        """Test valid IPv4 with unicast."""
        ipv4 = BgpRedistributionIpv4(
            unicast=BgpRedistributionUnicast(static=BgpRedistributionProtocol(enable=True))
        )
        assert ipv4.unicast.static.enable is True

    def test_optional_fields(self):
        """Test IPv4 with no fields set."""
        ipv4 = BgpRedistributionIpv4()
        assert ipv4.unicast is None

    def test_ipv4_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            BgpRedistributionIpv4(unknown="fail")
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestBgpRedistributionProfileBaseModel:
    """Test BGP Redistribution Profile base model validation."""

    def test_valid_minimal_fields(self):
        """Test valid model with only required fields."""
        model = BgpRedistributionProfileBaseModel(name="test-rp", folder="Test Folder")
        assert model.name == "test-rp"
        assert model.folder == "Test Folder"
        assert model.ipv4 is None

    def test_valid_all_fields(self):
        """Test valid model with all fields populated."""
        model = BgpRedistributionProfileBaseModel(
            name="test-rp",
            folder="Test Folder",
            ipv4=BgpRedistributionIpv4(
                unicast=BgpRedistributionUnicast(
                    static=BgpRedistributionProtocol(enable=True, metric=100),
                    ospf=BgpRedistributionProtocol(enable=True, metric=200),
                    connected=BgpRedistributionProtocol(enable=False),
                )
            ),
        )
        assert model.name == "test-rp"
        assert model.ipv4.unicast.static.enable is True
        assert model.ipv4.unicast.static.metric == 100
        assert model.ipv4.unicast.ospf.metric == 200
        assert model.ipv4.unicast.connected.enable is False

    def test_missing_name_raises_error(self):
        """Test that missing name field raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            BgpRedistributionProfileBaseModel(folder="Test Folder")
        assert "name" in str(exc_info.value)

    def test_container_folder(self):
        """Test model with folder container."""
        model = BgpRedistributionProfileBaseModel(name="test", folder="MyFolder")
        assert model.folder == "MyFolder"
        assert model.snippet is None
        assert model.device is None

    def test_container_snippet(self):
        """Test model with snippet container."""
        model = BgpRedistributionProfileBaseModel(name="test", snippet="MySnippet")
        assert model.snippet == "MySnippet"
        assert model.folder is None

    def test_container_device(self):
        """Test model with device container."""
        model = BgpRedistributionProfileBaseModel(name="test", device="MyDevice")
        assert model.device == "MyDevice"
        assert model.folder is None

    def test_container_max_length(self):
        """Test container field max_length validation."""
        model = BgpRedistributionProfileBaseModel(name="test", folder="A" * 64)
        assert len(model.folder) == 64

        with pytest.raises(ValidationError):
            BgpRedistributionProfileBaseModel(name="test", folder="A" * 65)

    def test_container_pattern_validation(self):
        """Test container field pattern validation."""
        model = BgpRedistributionProfileBaseModel(name="test", folder="My-Folder_1.0")
        assert model.folder == "My-Folder_1.0"

        with pytest.raises(ValidationError):
            BgpRedistributionProfileBaseModel(name="test", folder="Folder@#$")


class TestBgpRedistributionProfileCreateModel:
    """Test BGP Redistribution Profile create model."""

    def test_valid_create_with_folder(self):
        """Test valid create model with folder container."""
        model = BgpRedistributionProfileCreateModel(
            name="test-rp",
            folder="Test Folder",
        )
        assert model.name == "test-rp"
        assert model.folder == "Test Folder"

    def test_valid_create_with_snippet(self):
        """Test valid create model with snippet container."""
        model = BgpRedistributionProfileCreateModel(
            name="test-rp",
            snippet="MySnippet",
        )
        assert model.snippet == "MySnippet"

    def test_valid_create_with_device(self):
        """Test valid create model with device container."""
        model = BgpRedistributionProfileCreateModel(
            name="test-rp",
            device="MyDevice",
        )
        assert model.device == "MyDevice"

    def test_create_no_container_raises_error(self):
        """Test that create without any container raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            BgpRedistributionProfileCreateModel(name="test-rp")
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_create_multiple_containers_raises_error(self):
        """Test that create with multiple containers raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            BgpRedistributionProfileCreateModel(
                name="test-rp",
                folder="Test Folder",
                snippet="MySnippet",
            )
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_create_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on BgpRedistributionProfileCreateModel."""
        with pytest.raises(ValidationError) as exc_info:
            BgpRedistributionProfileCreateModel(
                name="test",
                folder="Test Folder",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestBgpRedistributionProfileUpdateModel:
    """Test BGP Redistribution Profile update model."""

    def test_valid_update_model(self):
        """Test valid update model."""
        model = BgpRedistributionProfileUpdateModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="updated-rp",
            folder="Test Folder",
        )
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "updated-rp"

    def test_invalid_uuid(self):
        """Test update model with invalid UUID."""
        with pytest.raises(ValidationError):
            BgpRedistributionProfileUpdateModel(
                id="not-a-uuid",
                name="test",
                folder="Test Folder",
            )


class TestBgpRedistributionProfileResponseModel:
    """Test BGP Redistribution Profile response model."""

    def test_valid_response_model(self):
        """Test valid response model."""
        model = BgpRedistributionProfileResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="response-rp",
            folder="Test Folder",
        )
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "response-rp"

    def test_missing_id_raises_error(self):
        """Test that missing id field raises ValidationError."""
        with pytest.raises(ValidationError):
            BgpRedistributionProfileResponseModel(
                name="test",
                folder="Test Folder",
            )


class TestExtraFieldsBgpRedistributionProfile:
    """Tests for extra field handling on BGP Redistribution Profile models."""

    def test_base_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on BgpRedistributionProfileBaseModel."""
        with pytest.raises(ValidationError) as exc_info:
            BgpRedistributionProfileBaseModel(
                name="test",
                folder="Test Folder",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_update_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on BgpRedistributionProfileUpdateModel."""
        with pytest.raises(ValidationError) as exc_info:
            BgpRedistributionProfileUpdateModel(
                id="123e4567-e89b-12d3-a456-426655440000",
                name="test",
                folder="Test Folder",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_response_model_extra_fields_ignored(self):
        """Test that extra fields are silently ignored on BgpRedistributionProfileResponseModel."""
        model = BgpRedistributionProfileResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test",
            folder="Test Folder",
            unknown_field="should_be_ignored",
        )
        assert not hasattr(model, "unknown_field")
