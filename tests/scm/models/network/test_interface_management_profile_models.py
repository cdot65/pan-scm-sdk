"""Test models for Interface Management Profiles."""

from uuid import UUID

from pydantic import ValidationError
import pytest

from scm.models.network import (
    InterfaceManagementProfileCreateModel,
    InterfaceManagementProfileResponseModel,
    InterfaceManagementProfileUpdateModel,
)


class TestInterfaceManagementProfileModels:
    """Test Interface Management Profile Pydantic models."""

    def test_base_model_validation(self):
        """Test validation of InterfaceManagementProfileBaseModel through the Create model."""
        # Test valid model
        valid_data = {
            "name": "test-profile",
            "folder": "Test Folder",
            "http": True,
            "https": True,
            "ssh": True,
            "ping": True,
            "telnet": False,
            "http_ocsp": False,
            "response_pages": True,
            "userid_service": False,
            "userid_syslog_listener_ssl": False,
            "userid_syslog_listener_udp": False,
            "permitted_ip": ["10.0.0.0/8"],
        }
        model = InterfaceManagementProfileCreateModel(**valid_data)
        assert model.name == "test-profile"
        assert model.folder == "Test Folder"
        assert model.http is True
        assert model.https is True
        assert model.ssh is True
        assert model.ping is True
        assert model.telnet is False
        assert model.http_ocsp is False
        assert model.response_pages is True
        assert model.userid_service is False
        assert model.userid_syslog_listener_ssl is False
        assert model.userid_syslog_listener_udp is False
        assert model.permitted_ip == ["10.0.0.0/8"]

        # Test with whitespace in name
        valid_with_whitespace = {
            "name": "Management Profile 1",
            "folder": "Test Folder",
        }
        model = InterfaceManagementProfileCreateModel(**valid_with_whitespace)
        assert model.name == "Management Profile 1"

        # Test with multiple words and special characters
        valid_with_special_chars = {
            "name": "External-Mgmt_Profile.1",
            "folder": "Test Folder",
        }
        model = InterfaceManagementProfileCreateModel(**valid_with_special_chars)
        assert model.name == "External-Mgmt_Profile.1"

        # Test invalid name with invalid characters
        invalid_name = {
            "name": "Profile!@#",
            "folder": "Test Folder",
        }
        with pytest.raises(ValidationError) as exc_info:
            InterfaceManagementProfileCreateModel(**invalid_name)
        assert "String should match pattern" in str(exc_info.value)

        # Test invalid name (too long)
        invalid_name = {
            "name": "A" * 64,  # Max length is 63
            "folder": "Test Folder",
        }
        with pytest.raises(ValidationError) as exc_info:
            InterfaceManagementProfileCreateModel(**invalid_name)
        assert "should have at most 63 characters" in str(exc_info.value).lower()

    def test_create_model_with_aliases(self):
        """Test that alias (kebab-case) field names work for creation."""
        valid_data = {
            "name": "test-profile",
            "folder": "Test Folder",
            "http-ocsp": True,
            "response-pages": True,
            "userid-service": False,
            "userid-syslog-listener-ssl": True,
            "userid-syslog-listener-udp": False,
            "permitted-ip": ["10.0.0.0/8", "172.16.0.0/12"],
        }
        model = InterfaceManagementProfileCreateModel(**valid_data)
        assert model.http_ocsp is True
        assert model.response_pages is True
        assert model.userid_service is False
        assert model.userid_syslog_listener_ssl is True
        assert model.userid_syslog_listener_udp is False
        assert model.permitted_ip == ["10.0.0.0/8", "172.16.0.0/12"]

    def test_create_model_model_dump_by_alias(self):
        """Test that model_dump with by_alias produces kebab-case keys."""
        valid_data = {
            "name": "test-profile",
            "folder": "Test Folder",
            "http_ocsp": True,
            "response_pages": True,
            "userid_service": False,
            "permitted_ip": ["10.0.0.0/8"],
        }
        model = InterfaceManagementProfileCreateModel(**valid_data)
        dumped = model.model_dump(exclude_unset=True, by_alias=True)
        assert "http-ocsp" in dumped
        assert "response-pages" in dumped
        assert "userid-service" in dumped
        assert "permitted-ip" in dumped
        assert dumped["http-ocsp"] is True
        assert dumped["response-pages"] is True
        assert dumped["userid-service"] is False
        assert dumped["permitted-ip"] == ["10.0.0.0/8"]

    def test_create_model_container_validation(self):
        """Test validation of container fields in InterfaceManagementProfileCreateModel."""
        valid_data = {
            "name": "test-profile",
            "folder": "Test Folder",
        }
        model = InterfaceManagementProfileCreateModel(**valid_data)
        assert model.folder == "Test Folder"
        assert model.snippet is None
        assert model.device is None

        # Test with snippet container
        valid_with_snippet = {
            "name": "test-profile",
            "snippet": "Test Snippet",
        }
        model = InterfaceManagementProfileCreateModel(**valid_with_snippet)
        assert model.snippet == "Test Snippet"
        assert model.folder is None
        assert model.device is None

        # Test with device container
        valid_with_device = {
            "name": "test-profile",
            "device": "Test Device",
        }
        model = InterfaceManagementProfileCreateModel(**valid_with_device)
        assert model.device == "Test Device"
        assert model.folder is None
        assert model.snippet is None

        # Test with no container
        invalid_no_container = {
            "name": "test-profile",
        }
        with pytest.raises(ValueError) as exc_info:
            InterfaceManagementProfileCreateModel(**invalid_no_container)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

        # Test with multiple containers
        invalid_multiple_containers = {
            "name": "test-profile",
            "folder": "Test Folder",
            "snippet": "Test Snippet",
        }
        with pytest.raises(ValueError) as exc_info:
            InterfaceManagementProfileCreateModel(**invalid_multiple_containers)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_update_model(self):
        """Test validation of InterfaceManagementProfileUpdateModel."""
        # Test valid update model
        valid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "updated-profile",
            "folder": "Test Folder",
            "http": True,
            "ssh": False,
            "ping": True,
        }
        model = InterfaceManagementProfileUpdateModel(**valid_data)
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "updated-profile"
        assert model.folder == "Test Folder"
        assert model.http is True
        assert model.ssh is False
        assert model.ping is True

        # Test with whitespace in name on update
        valid_with_whitespace = valid_data.copy()
        valid_with_whitespace["name"] = "Management Profile 1"
        model = InterfaceManagementProfileUpdateModel(**valid_with_whitespace)
        assert model.name == "Management Profile 1"

        # Test invalid UUID
        invalid_id = valid_data.copy()
        invalid_id["id"] = "not-a-uuid"
        with pytest.raises(ValidationError):
            InterfaceManagementProfileUpdateModel(**invalid_id)

    def test_response_model(self):
        """Test validation of InterfaceManagementProfileResponseModel."""
        # Test valid response model
        valid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "response-profile",
            "folder": "Test Folder",
            "http": True,
            "https": True,
            "ssh": False,
            "ping": True,
        }
        model = InterfaceManagementProfileResponseModel(**valid_data)
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "response-profile"
        assert model.folder == "Test Folder"
        assert model.http is True
        assert model.https is True
        assert model.ssh is False
        assert model.ping is True

        # Test with whitespace in name in response
        valid_with_whitespace = valid_data.copy()
        valid_with_whitespace["name"] = "Management Profile 1"
        model = InterfaceManagementProfileResponseModel(**valid_with_whitespace)
        assert model.name == "Management Profile 1"

        # Test missing required ID
        invalid_data = valid_data.copy()
        del invalid_data["id"]
        with pytest.raises(ValidationError):
            InterfaceManagementProfileResponseModel(**invalid_data)

    def test_response_model_with_aliases(self):
        """Test that response model works with alias (kebab-case) field names."""
        valid_data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "response-profile",
            "folder": "Test Folder",
            "http-ocsp": True,
            "response-pages": False,
            "userid-service": True,
            "userid-syslog-listener-ssl": False,
            "userid-syslog-listener-udp": True,
            "permitted-ip": ["192.168.1.0/24"],
        }
        model = InterfaceManagementProfileResponseModel(**valid_data)
        assert model.http_ocsp is True
        assert model.response_pages is False
        assert model.userid_service is True
        assert model.userid_syslog_listener_ssl is False
        assert model.userid_syslog_listener_udp is True
        assert model.permitted_ip == ["192.168.1.0/24"]

    def test_minimal_model(self):
        """Test model with only required fields."""
        valid_data = {
            "name": "minimal-profile",
            "folder": "Test Folder",
        }
        model = InterfaceManagementProfileCreateModel(**valid_data)
        assert model.name == "minimal-profile"
        assert model.folder == "Test Folder"
        assert model.http is None
        assert model.https is None
        assert model.telnet is None
        assert model.ssh is None
        assert model.ping is None
        assert model.http_ocsp is None
        assert model.response_pages is None
        assert model.userid_service is None
        assert model.userid_syslog_listener_ssl is None
        assert model.userid_syslog_listener_udp is None
        assert model.permitted_ip is None


class TestExtraFieldsForbidden:
    """Tests for extra='forbid' validation on all Interface Management Profile models."""

    def test_create_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on InterfaceManagementProfileCreateModel."""
        data = {
            "name": "test-profile",
            "folder": "Test Folder",
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            InterfaceManagementProfileCreateModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_update_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on InterfaceManagementProfileUpdateModel."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-profile",
            "folder": "Test Folder",
            "unknown_field": "should_fail",
        }
        with pytest.raises(ValidationError) as exc_info:
            InterfaceManagementProfileUpdateModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_response_model_extra_fields_ignored(self):
        """Test that extra fields are silently ignored on InterfaceManagementProfileResponseModel."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "test-profile",
            "folder": "Test Folder",
            "unknown_field": "should_be_ignored",
        }
        model = InterfaceManagementProfileResponseModel(**data)
        assert not hasattr(model, "unknown_field")
