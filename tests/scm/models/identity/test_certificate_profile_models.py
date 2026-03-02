# tests/scm/models/identity/test_certificate_profile_models.py

"""Tests for certificate profile identity models."""

# External libraries
from pydantic import ValidationError
import pytest

# Local SDK imports
from scm.models.identity.certificate_profiles import (
    CaCertificate,
    CertificateProfileCreateModel,
    CertificateProfileResponseModel,
    CertificateProfileUpdateModel,
    CertProfileUsernameField,
    UsernameFieldSubject,
    UsernameFieldSubjectAlt,
)
from tests.factories.identity.certificate_profile import (
    CertificateProfileCreateModelFactory,
    CertificateProfileUpdateModelFactory,
)

# -------------------- Test Classes for Pydantic Models --------------------


class TestCaCertificate:
    """Tests for CaCertificate component model."""

    def test_ca_certificate_valid(self):
        """Test valid CA certificate configuration."""
        model = CaCertificate(name="root-ca")
        assert model.name == "root-ca"

    def test_ca_certificate_with_optional_fields(self):
        """Test CA certificate with all optional fields."""
        model = CaCertificate(
            name="root-ca",
            default_ocsp_url="http://ocsp.example.com",
            ocsp_verify_cert="verify-cert",
            template_name="template1",
        )
        assert model.default_ocsp_url == "http://ocsp.example.com"
        assert model.ocsp_verify_cert == "verify-cert"
        assert model.template_name == "template1"

    def test_ca_certificate_rejects_extra_fields(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            CaCertificate(name="root-ca", unknown_field="value")
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestCertProfileUsernameField:
    """Tests for CertProfileUsernameField component model."""

    def test_username_field_subject(self):
        """Test username field with subject configuration."""
        model = CertProfileUsernameField(subject=UsernameFieldSubject.common_name)
        assert model.subject == UsernameFieldSubject.common_name

    def test_username_field_subject_alt(self):
        """Test username field with subject alternative configuration."""
        model = CertProfileUsernameField(subject_alt=UsernameFieldSubjectAlt.email)
        assert model.subject_alt == UsernameFieldSubjectAlt.email

    def test_username_field_empty(self):
        """Test that username field can be empty."""
        model = CertProfileUsernameField()
        assert model.subject is None
        assert model.subject_alt is None

    def test_username_field_rejects_extra_fields(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            CertProfileUsernameField(unknown="value")
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestCertificateProfileCreateModel:
    """Tests for CertificateProfileCreateModel validation."""

    def test_create_model_valid(self):
        """Test validation with valid data."""
        data = CertificateProfileCreateModelFactory.build_valid()
        model = CertificateProfileCreateModel(**data)
        assert model.name == data["name"]
        assert model.folder == data["folder"]

    def test_create_model_with_ca_certificates(self):
        """Test validation with CA certificates."""
        data = CertificateProfileCreateModelFactory.build_valid(
            ca_certificates=[
                {"name": "root-ca", "default_ocsp_url": "http://ocsp.example.com"},
            ]
        )
        model = CertificateProfileCreateModel(**data)
        assert model.ca_certificates is not None
        assert len(model.ca_certificates) == 1
        assert isinstance(model.ca_certificates[0], CaCertificate)
        assert model.ca_certificates[0].name == "root-ca"

    def test_create_model_with_username_field(self):
        """Test validation with username field."""
        data = CertificateProfileCreateModelFactory.build_valid(
            username_field={"subject": "common-name"}
        )
        model = CertificateProfileCreateModel(**data)
        assert model.username_field is not None
        assert isinstance(model.username_field, CertProfileUsernameField)

    def test_create_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = CertificateProfileCreateModelFactory.build_with_multiple_containers()
        with pytest.raises(ValueError) as exc_info:
            CertificateProfileCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_create_model_no_container(self):
        """Test validation when no container is provided."""
        data = CertificateProfileCreateModelFactory.build_with_no_container()
        with pytest.raises(ValueError) as exc_info:
            CertificateProfileCreateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_create_model_crl_receive_timeout_valid(self):
        """Test CRL receive timeout with valid value."""
        data = CertificateProfileCreateModelFactory.build_valid(crl_receive_timeout=30)
        model = CertificateProfileCreateModel(**data)
        assert model.crl_receive_timeout == 30

    def test_create_model_crl_receive_timeout_too_low(self):
        """Test CRL receive timeout below minimum."""
        data = CertificateProfileCreateModelFactory.build_valid(crl_receive_timeout=0)
        with pytest.raises(ValidationError) as exc_info:
            CertificateProfileCreateModel(**data)
        assert "greater than or equal to 1" in str(exc_info.value)

    def test_create_model_crl_receive_timeout_too_high(self):
        """Test CRL receive timeout above maximum."""
        data = CertificateProfileCreateModelFactory.build_valid(crl_receive_timeout=61)
        with pytest.raises(ValidationError) as exc_info:
            CertificateProfileCreateModel(**data)
        assert "less than or equal to 60" in str(exc_info.value)

    def test_create_model_ocsp_receive_timeout_valid(self):
        """Test OCSP receive timeout with valid value."""
        data = CertificateProfileCreateModelFactory.build_valid(ocsp_receive_timeout=15)
        model = CertificateProfileCreateModel(**data)
        assert model.ocsp_receive_timeout == 15

    def test_create_model_ocsp_receive_timeout_too_low(self):
        """Test OCSP receive timeout below minimum."""
        data = CertificateProfileCreateModelFactory.build_valid(ocsp_receive_timeout=0)
        with pytest.raises(ValidationError) as exc_info:
            CertificateProfileCreateModel(**data)
        assert "greater than or equal to 1" in str(exc_info.value)

    def test_create_model_ocsp_receive_timeout_too_high(self):
        """Test OCSP receive timeout above maximum."""
        data = CertificateProfileCreateModelFactory.build_valid(ocsp_receive_timeout=61)
        with pytest.raises(ValidationError) as exc_info:
            CertificateProfileCreateModel(**data)
        assert "less than or equal to 60" in str(exc_info.value)

    def test_create_model_cert_status_timeout_valid(self):
        """Test cert status timeout with valid value."""
        data = CertificateProfileCreateModelFactory.build_valid(cert_status_timeout=5)
        model = CertificateProfileCreateModel(**data)
        assert model.cert_status_timeout == 5

    def test_create_model_cert_status_timeout_too_low(self):
        """Test cert status timeout below minimum."""
        data = CertificateProfileCreateModelFactory.build_valid(cert_status_timeout=0)
        with pytest.raises(ValidationError) as exc_info:
            CertificateProfileCreateModel(**data)
        assert "greater than or equal to 1" in str(exc_info.value)

    def test_create_model_cert_status_timeout_too_high(self):
        """Test cert status timeout above maximum."""
        data = CertificateProfileCreateModelFactory.build_valid(cert_status_timeout=61)
        with pytest.raises(ValidationError) as exc_info:
            CertificateProfileCreateModel(**data)
        assert "less than or equal to 60" in str(exc_info.value)

    def test_create_model_name_too_long(self):
        """Test validation with name exceeding max length."""
        data = CertificateProfileCreateModelFactory.build_valid(name="a" * 64)
        with pytest.raises(ValidationError) as exc_info:
            CertificateProfileCreateModel(**data)
        assert "String should have at most 63 characters" in str(exc_info.value)


class TestCertificateProfileUpdateModel:
    """Tests for CertificateProfileUpdateModel validation."""

    def test_update_model_valid(self):
        """Test validation with valid update data."""
        data = CertificateProfileUpdateModelFactory.build_valid()
        model = CertificateProfileUpdateModel(**data)
        assert model.name == data["name"]
        assert str(model.id) == data["id"]

    def test_update_model_invalid_uuid(self):
        """Test validation with invalid UUID format."""
        data = CertificateProfileUpdateModelFactory.build_valid(id="invalid-uuid")
        with pytest.raises(ValidationError) as exc_info:
            CertificateProfileUpdateModel(**data)
        assert "Input should be a valid UUID" in str(exc_info.value)


class TestCertificateProfileResponseModel:
    """Tests for CertificateProfileResponseModel validation."""

    def test_response_model_valid(self):
        """Test validation with valid response data."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestProfile",
            "folder": "Texas",
        }
        model = CertificateProfileResponseModel(**data)
        assert str(model.id) == data["id"]
        assert model.name == data["name"]
        assert model.folder == data["folder"]

    def test_response_model_invalid_uuid(self):
        """Test validation with invalid UUID format."""
        data = {
            "id": "invalid-uuid",
            "name": "TestProfile",
            "folder": "Texas",
        }
        with pytest.raises(ValidationError) as exc_info:
            CertificateProfileResponseModel(**data)
        assert "Input should be a valid UUID" in str(exc_info.value)

    def test_response_model_ignores_extra_fields(self):
        """Test that extra fields are silently ignored in ResponseModel."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestProfile",
            "folder": "Texas",
            "unknown_field": "should_be_ignored",
        }
        model = CertificateProfileResponseModel(**data)
        assert not hasattr(model, "unknown_field")


# -------------------- End of Test Classes --------------------
