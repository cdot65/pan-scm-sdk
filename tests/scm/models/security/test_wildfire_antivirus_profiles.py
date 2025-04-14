# tests/scm/models/security/test_wildfire_antivirus_profiles.py

from uuid import UUID

from pydantic import ValidationError

# External libraries
import pytest

# Local SDK imports
from scm.models.security.wildfire_antivirus_profiles import (
    WildfireAvAnalysis,
    WildfireAvDirection,
    WildfireAvProfileCreateModel,
    WildfireAvProfileResponseModel,
    WildfireAvProfileUpdateModel,
)
from tests.factories import (
    WildfireAvProfileCreateApiFactory,
    WildfireAvProfileCreateModelFactory,
    WildfireAvProfileResponseFactory,
    WildfireAvProfileUpdateApiFactory,
    WildfireAvProfileUpdateModelFactory,
    WildfireAvRuleBaseFactory,
)

# -------------------- Test Classes for Pydantic Models --------------------


class TestWildfireAvProfileCreateModel:
    """Tests for WildfireAvProfileCreateModel validation."""

    def test_wildfire_av_profile_create_model_valid(self):
        """Test validation with valid data."""
        data = WildfireAvProfileCreateModelFactory.build_valid()
        model = WildfireAvProfileCreateModel(**data)
        assert model.name == "TestWildfireProfile"
        assert model.folder == "Texas"
        assert len(model.rules) == 1
        assert model.rules[0].direction == WildfireAvDirection.both
        assert model.rules[0].analysis == WildfireAvAnalysis.public_cloud

    def test_wildfire_av_profile_create_model_invalid_name(self):
        """Test validation when an invalid name is provided."""
        data = WildfireAvProfileCreateModelFactory.build_with_invalid_name()
        with pytest.raises(ValidationError) as exc_info:
            WildfireAvProfileCreateModel(**data)
        assert "name\n  String should match pattern" in str(exc_info.value)

    def test_wildfire_av_profile_create_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = WildfireAvProfileCreateModelFactory.build_with_multiple_containers()
        with pytest.raises(ValueError) as exc_info:
            WildfireAvProfileCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    # def test_wildfire_av_profile_create_model_no_container(self):
    #     """Test validation when no container is provided."""
    #     data = WildfireAvProfileCreateModelFactory.build_with_no_container()
    #     with pytest.raises(ValueError) as exc_info:
    #         WildfireAvProfileCreateModel(**data)
    #     assert (
    #         "Exactly one of 'folder', 'snippet', or 'device' must be provided."
    #         in str(exc_info.value)
    #     )

    def test_wildfire_av_profile_create_model_invalid_rule(self):
        """Test validation with invalid rule data."""
        data = WildfireAvProfileCreateModelFactory.build_with_invalid_rule()
        with pytest.raises(ValidationError) as exc_info:
            WildfireAvProfileCreateModel(**data)
        assert "direction\n  Input should be" in str(exc_info.value)

    def test_wildfire_av_profile_create_model_with_snippet(self):
        """Test creation with snippet container."""
        model = WildfireAvProfileCreateApiFactory.with_snippet()
        assert model.snippet == "TestSnippet"
        assert model.folder is None
        assert model.device is None

    def test_wildfire_av_profile_create_model_with_device(self):
        """Test creation with device container."""
        model = WildfireAvProfileCreateApiFactory.with_device()
        assert model.device == "TestDevice"
        assert model.folder is None
        assert model.snippet is None

    def test_wildfire_av_profile_create_model_packet_capture(self):
        """Test creation with packet capture enabled."""
        model = WildfireAvProfileCreateApiFactory.with_packet_capture(enabled=True)
        assert model.packet_capture is True

    def test_wildfire_av_profile_create_model_default_lists(self):
        """Test default values for list fields in rules."""
        rule = WildfireAvRuleBaseFactory()
        assert rule.application == ["any"]
        assert rule.file_type == ["any"]


class TestWildfireAvProfileUpdateModel:
    """Tests for WildfireAvProfileUpdateModel validation."""

    def test_wildfire_av_profile_update_model_valid(self):
        """Test validation with valid update data."""
        data = WildfireAvProfileUpdateModelFactory.build_valid()
        model = WildfireAvProfileUpdateModel(**data)
        assert model.name == "UpdatedWildfireProfile"
        assert len(model.rules) == 1
        assert model.rules[0].direction == WildfireAvDirection.download

    def test_wildfire_av_profile_update_model_invalid_fields(self):
        """Test validation with multiple invalid fields."""
        data = WildfireAvProfileUpdateModelFactory.build_with_invalid_fields()
        with pytest.raises(ValidationError) as exc_info:
            WildfireAvProfileUpdateModel(**data)
        error_msg = str(exc_info.value)
        assert "4 validation errors for WildfireAvProfileUpdateModel" in error_msg

    def test_wildfire_av_profile_update_model_minimal_update(self):
        """Test validation with minimal valid update fields."""
        data = WildfireAvProfileUpdateModelFactory.build_minimal_update()
        model = WildfireAvProfileUpdateModel(**data)
        assert model.description == "Updated description"

    def test_wildfire_av_profile_update_model_packet_capture(self):
        """Test update with packet capture modification."""
        model = WildfireAvProfileUpdateApiFactory.with_packet_capture(enabled=True)
        assert model.packet_capture is True


class TestWildfireAvProfileResponseModel:
    """Tests for WildfireAvProfileResponseModel validation."""

    def test_wildfire_av_profile_response_model_valid(self):
        """Test validation with valid response data."""
        data = WildfireAvProfileResponseFactory().model_dump()
        model = WildfireAvProfileResponseModel(**data)
        assert isinstance(model.id, UUID)
        assert model.name.startswith("wildfire_profile_")
        assert model.folder == "Texas"
        assert len(model.rules) > 0

    def test_wildfire_av_profile_response_model_from_request(self):
        """Test creation of response model from request data."""
        request_data = WildfireAvProfileCreateModelFactory.build_valid()
        request_model = WildfireAvProfileCreateModel(**request_data)
        response_data = WildfireAvProfileResponseFactory.from_request(request_model)
        model = WildfireAvProfileResponseModel(**response_data.model_dump())
        assert isinstance(model.id, UUID)
        assert model.name == request_model.name
        assert model.folder == request_model.folder
        assert len(model.rules) == len(request_model.rules)

    def test_wildfire_av_profile_response_model_with_snippet(self):
        """Test response model with snippet container."""
        data = WildfireAvProfileResponseFactory.with_snippet()
        model = WildfireAvProfileResponseModel(**data.model_dump())
        assert model.snippet == "TestSnippet"
        assert model.folder is None
        assert model.device is None

    def test_wildfire_av_profile_response_model_with_device(self):
        """Test response model with device container."""
        data = WildfireAvProfileResponseFactory.with_device()
        model = WildfireAvProfileResponseModel(**data.model_dump())
        assert model.device == "TestDevice"
        assert model.folder is None
        assert model.snippet is None


# -------------------- End of Test Classes --------------------
