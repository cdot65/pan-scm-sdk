# tests/scm/models/security/test_url_access_profile_models.py

"""Tests for URL access profile security models."""

# External libraries
from pydantic import ValidationError
import pytest

# Local SDK imports
from scm.models.security.url_access_profiles import (
    CredentialEnforcement,
    CredentialEnforcementMode,
    URLAccessProfileCreateModel,
    URLAccessProfileResponseModel,
    URLAccessProfileUpdateModel,
)
from tests.factories.security.url_access_profile import (
    URLAccessProfileCreateModelFactory,
    URLAccessProfileUpdateModelFactory,
)

# -------------------- Test Classes for Pydantic Models --------------------


class TestCredentialEnforcementMode:
    """Tests for CredentialEnforcementMode validation."""

    def test_mode_valid_disabled(self):
        """Test validation with disabled mode."""
        data = {"disabled": {}}
        model = CredentialEnforcementMode(**data)
        assert model.disabled == {}

    def test_mode_valid_domain_credentials(self):
        """Test validation with domain credentials mode."""
        data = {"domain_credentials": {}}
        model = CredentialEnforcementMode(**data)
        assert model.domain_credentials == {}

    def test_mode_valid_ip_user(self):
        """Test validation with IP user mode."""
        data = {"ip_user": {}}
        model = CredentialEnforcementMode(**data)
        assert model.ip_user == {}

    def test_mode_valid_group_mapping(self):
        """Test validation with group mapping mode."""
        data = {"group_mapping": "test-group"}
        model = CredentialEnforcementMode(**data)
        assert model.group_mapping == "test-group"


class TestCredentialEnforcement:
    """Tests for CredentialEnforcement validation."""

    def test_credential_enforcement_valid(self):
        """Test validation with valid data."""
        data = {
            "alert": ["category1"],
            "allow": ["category2"],
            "block": ["category3"],
            "continue": ["category4"],
            "log_severity": "high",
            "mode": {"disabled": {}},
        }
        model = CredentialEnforcement(**data)
        assert model.alert == ["category1"]
        assert model.allow == ["category2"]
        assert model.block == ["category3"]
        assert model.continue_ == ["category4"]
        assert model.log_severity == "high"
        assert model.mode is not None

    def test_credential_enforcement_continue_alias(self):
        """Test that continue_ can be set using 'continue' alias."""
        data = {
            "continue": ["test-category"],
        }
        model = CredentialEnforcement(**data)
        assert model.continue_ == ["test-category"]

    def test_credential_enforcement_continue_serialization(self):
        """Test that continue_ serializes with 'continue' key."""
        data = {
            "continue": ["test-category"],
        }
        model = CredentialEnforcement(**data)
        dumped = model.model_dump(by_alias=True)
        assert "continue" in dumped
        assert dumped["continue"] == ["test-category"]

    def test_credential_enforcement_default_log_severity(self):
        """Test default log_severity."""
        model = CredentialEnforcement()
        assert model.log_severity == "medium"


class TestURLAccessProfileCreateModel:
    """Tests for URLAccessProfileCreateModel validation."""

    def test_profile_create_model_valid(self):
        """Test validation with valid data."""
        data = URLAccessProfileCreateModelFactory.build_valid()
        model = URLAccessProfileCreateModel(**data)
        assert model.name == data["name"]
        assert model.folder == data["folder"]

    def test_profile_create_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = URLAccessProfileCreateModelFactory.build_with_multiple_containers()
        with pytest.raises(ValueError) as exc_info:
            URLAccessProfileCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_profile_create_model_no_container(self):
        """Test validation when no container is provided."""
        data = URLAccessProfileCreateModelFactory.build_with_no_container()
        with pytest.raises(ValueError) as exc_info:
            URLAccessProfileCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_profile_create_model_with_snippet(self):
        """Test creation with snippet container."""
        data = URLAccessProfileCreateModelFactory.build_with_snippet()
        model = URLAccessProfileCreateModel(**data)
        assert model.snippet == "TestSnippet"
        assert model.folder is None
        assert model.device is None

    def test_profile_create_model_with_device(self):
        """Test creation with device container."""
        data = URLAccessProfileCreateModelFactory.build_with_device()
        model = URLAccessProfileCreateModel(**data)
        assert model.device == "TestDevice"
        assert model.folder is None
        assert model.snippet is None

    def test_profile_create_model_continue_alias(self):
        """Test that continue_ can be set via 'continue' alias and accessed via continue_."""
        data = {
            "name": "TestProfile",
            "folder": "Texas",
            "continue": ["url-category-1", "url-category-2"],
        }
        model = URLAccessProfileCreateModel(**data)
        assert model.continue_ == ["url-category-1", "url-category-2"]

    def test_profile_create_model_continue_serialization(self):
        """Test that continue_ serializes with 'continue' key when by_alias=True."""
        data = {
            "name": "TestProfile",
            "folder": "Texas",
            "continue": ["url-category-1"],
        }
        model = URLAccessProfileCreateModel(**data)
        dumped = model.model_dump(by_alias=True)
        assert "continue" in dumped
        assert dumped["continue"] == ["url-category-1"]

    def test_profile_create_model_with_all_url_categories(self):
        """Test creation with all URL category action fields."""
        data = {
            "name": "TestProfile",
            "folder": "Texas",
            "alert": ["social-networking"],
            "allow": ["business-and-economy"],
            "block": ["adult"],
            "continue": ["streaming-media"],
        }
        model = URLAccessProfileCreateModel(**data)
        assert model.alert == ["social-networking"]
        assert model.allow == ["business-and-economy"]
        assert model.block == ["adult"]
        assert model.continue_ == ["streaming-media"]

    def test_profile_create_model_with_logging_options(self):
        """Test creation with logging-related options."""
        data = {
            "name": "TestProfile",
            "folder": "Texas",
            "log_container_page_only": True,
            "log_http_hdr_referer": True,
            "log_http_hdr_user_agent": True,
            "log_http_hdr_xff": True,
            "safe_search_enforcement": True,
        }
        model = URLAccessProfileCreateModel(**data)
        assert model.log_container_page_only is True
        assert model.log_http_hdr_referer is True
        assert model.log_http_hdr_user_agent is True
        assert model.log_http_hdr_xff is True
        assert model.safe_search_enforcement is True


class TestURLAccessProfileUpdateModel:
    """Tests for URLAccessProfileUpdateModel validation."""

    def test_profile_update_model_valid(self):
        """Test validation with valid update data."""
        data = URLAccessProfileUpdateModelFactory.build_valid()
        model = URLAccessProfileUpdateModel(**data)
        assert model.name == data["name"]
        assert model.description == data["description"]

    def test_profile_update_model_partial_update(self):
        """Test validation with partial update data."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "UpdatedProfile",
            "description": "Updated description",
        }
        model = URLAccessProfileUpdateModel(**data)
        assert model.name == data["name"]
        assert model.description == data["description"]

    def test_profile_update_model_with_continue(self):
        """Test update with continue_ field using alias."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "UpdatedProfile",
            "continue": ["new-category"],
        }
        model = URLAccessProfileUpdateModel(**data)
        assert model.continue_ == ["new-category"]


class TestURLAccessProfileResponseModel:
    """Tests for URLAccessProfileResponseModel validation."""

    def test_profile_response_model_valid(self):
        """Test validation with valid response data."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestProfile",
            "folder": "Texas",
            "alert": ["social-networking"],
            "block": ["adult"],
        }
        model = URLAccessProfileResponseModel(**data)
        assert str(model.id) == data["id"]
        assert model.name == data["name"]
        assert model.folder == data["folder"]
        assert model.alert == ["social-networking"]
        assert model.block == ["adult"]

    def test_profile_response_model_invalid_uuid(self):
        """Test validation with invalid UUID format."""
        data = {
            "id": "invalid-uuid",
            "name": "TestProfile",
            "folder": "Texas",
        }
        with pytest.raises(ValidationError) as exc_info:
            URLAccessProfileResponseModel(**data)
        assert "Input should be a valid UUID" in str(exc_info.value)

    def test_profile_response_model_with_continue_alias(self):
        """Test that continue_ can be read via the 'continue' alias in response."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestProfile",
            "folder": "Texas",
            "continue": ["streaming-media"],
        }
        model = URLAccessProfileResponseModel(**data)
        assert model.continue_ == ["streaming-media"]
        dumped = model.model_dump(by_alias=True)
        assert "continue" in dumped
        assert dumped["continue"] == ["streaming-media"]


class TestExtraFieldsForbidden:
    """Tests for extra='forbid' validation on all models."""

    def test_profile_create_model_rejects_extra_fields(self):
        """Test that extra fields are rejected in CreateModel."""
        data = URLAccessProfileCreateModelFactory.build_valid()
        data["unknown_field"] = "should_fail"
        with pytest.raises(ValidationError) as exc_info:
            URLAccessProfileCreateModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_profile_update_model_rejects_extra_fields(self):
        """Test that extra fields are rejected in UpdateModel."""
        data = URLAccessProfileUpdateModelFactory.build_valid()
        data["unknown_field"] = "should_fail"
        with pytest.raises(ValidationError) as exc_info:
            URLAccessProfileUpdateModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_profile_response_model_ignores_extra_fields(self):
        """Test that extra fields are silently ignored in ResponseModel."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestProfile",
            "folder": "Texas",
            "unknown_field": "should_be_ignored",
        }
        model = URLAccessProfileResponseModel(**data)
        assert not hasattr(model, "unknown_field")

    def test_credential_enforcement_rejects_extra_fields(self):
        """Test that extra fields are rejected in CredentialEnforcement."""
        data = {
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            CredentialEnforcement(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_credential_enforcement_mode_rejects_extra_fields(self):
        """Test that extra fields are rejected in CredentialEnforcementMode."""
        data = {
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            CredentialEnforcementMode(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestBoundaryValues:
    """Tests for boundary values on string fields."""

    def test_description_max_length(self):
        """Test that description respects max_length of 255."""
        long_desc = "a" * 256
        data = {
            "name": "TestProfile",
            "folder": "Texas",
            "description": long_desc,
        }
        with pytest.raises(ValidationError):
            URLAccessProfileCreateModel(**data)

    def test_description_valid_at_max_length(self):
        """Test that description at exactly 255 characters is valid."""
        desc_255 = "a" * 255
        model = URLAccessProfileCreateModel(
            name="TestProfile",
            folder="Texas",
            description=desc_255,
        )
        assert model.description == desc_255

    def test_folder_max_length(self):
        """Test that folder respects max_length of 64."""
        long_folder = "a" * 65
        with pytest.raises(ValidationError):
            URLAccessProfileCreateModel(
                name="TestProfile",
                folder=long_folder,
            )

    def test_folder_invalid_pattern(self):
        """Test that folder rejects invalid characters."""
        with pytest.raises(ValidationError):
            URLAccessProfileCreateModel(
                name="TestProfile",
                folder="invalid@folder!",
            )

    def test_snippet_invalid_pattern(self):
        """Test that snippet rejects invalid characters."""
        with pytest.raises(ValidationError):
            URLAccessProfileCreateModel(
                name="TestProfile",
                snippet="invalid@snippet!",
            )

    def test_device_invalid_pattern(self):
        """Test that device rejects invalid characters on CreateModel."""
        with pytest.raises(ValidationError):
            URLAccessProfileCreateModel(
                name="TestProfile",
                device="invalid@device!",
            )


# -------------------- End of Test Classes --------------------
