# tests/scm/models/identity/test_certificate_models.py

"""Tests for certificate identity models."""

# External libraries
from pydantic import ValidationError
import pytest

# Local SDK imports
from scm.models.identity.certificates import (
    CertificateDigest,
    CertificateExportModel,
    CertificateFormat,
    CertificateGenerateModel,
    CertificateImportModel,
    CertificateResponseModel,
)
from tests.factories.identity.certificate import (
    CertificateExportModelFactory,
    CertificateGenerateModelFactory,
    CertificateImportModelFactory,
)

# -------------------- Test Classes for Pydantic Models --------------------


class TestCertificateDigest:
    """Tests for the CertificateDigest enumeration."""

    def test_digest_sha1(self):
        """Test SHA1 digest enum value."""
        assert CertificateDigest.sha1 == "sha1"

    def test_digest_sha256(self):
        """Test SHA256 digest enum value."""
        assert CertificateDigest.sha256 == "sha256"

    def test_digest_sha384(self):
        """Test SHA384 digest enum value."""
        assert CertificateDigest.sha384 == "sha384"

    def test_digest_sha512(self):
        """Test SHA512 digest enum value."""
        assert CertificateDigest.sha512 == "sha512"

    def test_digest_md5(self):
        """Test MD5 digest enum value."""
        assert CertificateDigest.md5 == "md5"

    def test_digest_invalid(self):
        """Test that invalid digest raises ValueError."""
        with pytest.raises(ValueError):
            CertificateDigest("invalid-digest")


class TestCertificateFormat:
    """Tests for the CertificateFormat enumeration."""

    def test_format_pem(self):
        """Test PEM format enum value."""
        assert CertificateFormat.pem == "pem"

    def test_format_pkcs12(self):
        """Test PKCS12 format enum value."""
        assert CertificateFormat.pkcs12 == "pkcs12"

    def test_format_der(self):
        """Test DER format enum value."""
        assert CertificateFormat.der == "der"

    def test_format_invalid(self):
        """Test that invalid format raises ValueError."""
        with pytest.raises(ValueError):
            CertificateFormat("invalid-format")


class TestCertificateGenerateModel:
    """Tests for CertificateGenerateModel validation."""

    def test_generate_model_valid(self):
        """Test validation with valid data."""
        data = CertificateGenerateModelFactory.build_valid()
        model = CertificateGenerateModel(**data)
        assert model.certificate_name == "test-cert"
        assert model.common_name == "test.local"
        assert model.signed_by == "ca"
        assert model.digest == CertificateDigest.sha256

    def test_generate_model_algorithm_rsa(self):
        """Test validation with RSA algorithm configuration."""
        data = CertificateGenerateModelFactory.build_valid(algorithm={"rsa_number_of_bits": 4096})
        model = CertificateGenerateModel(**data)
        assert model.algorithm == {"rsa_number_of_bits": 4096}

    def test_generate_model_algorithm_ecdsa(self):
        """Test validation with ECDSA algorithm configuration."""
        data = CertificateGenerateModelFactory.build_valid(algorithm={"ecdsa_number_of_bits": 256})
        model = CertificateGenerateModel(**data)
        assert model.algorithm == {"ecdsa_number_of_bits": 256}

    def test_generate_model_missing_required_certificate_name(self):
        """Test validation when certificate_name is missing."""
        data = CertificateGenerateModelFactory.build_valid()
        del data["certificate_name"]
        with pytest.raises(ValidationError) as exc_info:
            CertificateGenerateModel(**data)
        assert "certificate_name" in str(exc_info.value)

    def test_generate_model_missing_required_common_name(self):
        """Test validation when common_name is missing."""
        data = CertificateGenerateModelFactory.build_valid()
        del data["common_name"]
        with pytest.raises(ValidationError) as exc_info:
            CertificateGenerateModel(**data)
        assert "common_name" in str(exc_info.value)

    def test_generate_model_missing_required_signed_by(self):
        """Test validation when signed_by is missing."""
        data = CertificateGenerateModelFactory.build_valid()
        del data["signed_by"]
        with pytest.raises(ValidationError) as exc_info:
            CertificateGenerateModel(**data)
        assert "signed_by" in str(exc_info.value)

    def test_generate_model_missing_required_algorithm(self):
        """Test validation when algorithm is missing."""
        data = CertificateGenerateModelFactory.build_valid()
        del data["algorithm"]
        with pytest.raises(ValidationError) as exc_info:
            CertificateGenerateModel(**data)
        assert "algorithm" in str(exc_info.value)

    def test_generate_model_missing_required_digest(self):
        """Test validation when digest is missing."""
        data = CertificateGenerateModelFactory.build_valid()
        del data["digest"]
        with pytest.raises(ValidationError) as exc_info:
            CertificateGenerateModel(**data)
        assert "digest" in str(exc_info.value)

    def test_generate_model_with_optional_fields(self):
        """Test validation with optional fields."""
        data = CertificateGenerateModelFactory.build_valid(
            day_till_expiration=365,
            is_certificate_authority=True,
            email="admin@example.com",
            hostname=["host1.example.com"],
            ip=["10.0.0.1"],
            country_code="US",
            state="California",
            locality="San Francisco",
            department=["IT"],
            ocsp_responder_url="http://ocsp.example.com",
        )
        model = CertificateGenerateModel(**data)
        assert model.day_till_expiration == 365
        assert model.is_certificate_authority is True
        assert model.email == "admin@example.com"
        assert model.hostname == ["host1.example.com"]

    def test_generate_model_no_container(self):
        """Test validation when no container is provided."""
        data = CertificateGenerateModelFactory.build_valid()
        data["folder"] = None
        with pytest.raises(ValueError) as exc_info:
            CertificateGenerateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_generate_model_multiple_containers(self):
        """Test validation when multiple containers are provided."""
        data = CertificateGenerateModelFactory.build_valid()
        data["snippet"] = "TestSnippet"
        with pytest.raises(ValueError) as exc_info:
            CertificateGenerateModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_generate_model_rejects_extra_fields(self):
        """Test that extra fields are rejected."""
        data = CertificateGenerateModelFactory.build_valid()
        data["unknown_field"] = "value"
        with pytest.raises(ValidationError) as exc_info:
            CertificateGenerateModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestCertificateImportModel:
    """Tests for CertificateImportModel validation."""

    def test_import_model_valid(self):
        """Test validation with valid data."""
        data = CertificateImportModelFactory.build_valid()
        model = CertificateImportModel(**data)
        assert model.name == "imported-cert"
        assert model.certificate_file == "base64data"
        assert model.format == CertificateFormat.pem

    def test_import_model_missing_required_name(self):
        """Test validation when name is missing."""
        data = CertificateImportModelFactory.build_valid()
        del data["name"]
        with pytest.raises(ValidationError) as exc_info:
            CertificateImportModel(**data)
        assert "name" in str(exc_info.value)

    def test_import_model_missing_required_certificate_file(self):
        """Test validation when certificate_file is missing."""
        data = CertificateImportModelFactory.build_valid()
        del data["certificate_file"]
        with pytest.raises(ValidationError) as exc_info:
            CertificateImportModel(**data)
        assert "certificate_file" in str(exc_info.value)

    def test_import_model_with_key_file(self):
        """Test validation with optional key_file."""
        data = CertificateImportModelFactory.build_valid(
            key_file="base64keydata",
            passphrase="mypassphrase",
        )
        model = CertificateImportModel(**data)
        assert model.key_file == "base64keydata"
        assert model.passphrase == "mypassphrase"

    def test_import_model_pkcs12_format(self):
        """Test validation with PKCS12 format."""
        data = CertificateImportModelFactory.build_valid(format="pkcs12")
        model = CertificateImportModel(**data)
        assert model.format == CertificateFormat.pkcs12

    def test_import_model_no_container(self):
        """Test validation when no container is provided."""
        data = CertificateImportModelFactory.build_valid()
        data["folder"] = None
        with pytest.raises(ValueError) as exc_info:
            CertificateImportModel(**data)
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided." in str(
            exc_info.value
        )

    def test_import_model_rejects_extra_fields(self):
        """Test that extra fields are rejected."""
        data = CertificateImportModelFactory.build_valid()
        data["unknown_field"] = "value"
        with pytest.raises(ValidationError) as exc_info:
            CertificateImportModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestCertificateExportModel:
    """Tests for CertificateExportModel validation."""

    def test_export_model_valid(self):
        """Test validation with valid data."""
        data = CertificateExportModelFactory.build_valid()
        model = CertificateExportModel(**data)
        assert model.format == CertificateFormat.pem

    def test_export_model_with_passphrase(self):
        """Test validation with passphrase."""
        data = CertificateExportModelFactory.build_valid(passphrase="secretpass")
        model = CertificateExportModel(**data)
        assert model.passphrase == "secretpass"

    def test_export_model_pkcs12_format(self):
        """Test validation with PKCS12 format."""
        data = CertificateExportModelFactory.build_valid(format="pkcs12")
        model = CertificateExportModel(**data)
        assert model.format == CertificateFormat.pkcs12

    def test_export_model_missing_required_format(self):
        """Test validation when format is missing."""
        with pytest.raises(ValidationError) as exc_info:
            CertificateExportModel()
        assert "format" in str(exc_info.value)

    def test_export_model_rejects_extra_fields(self):
        """Test that extra fields are rejected."""
        data = CertificateExportModelFactory.build_valid()
        data["unknown_field"] = "value"
        with pytest.raises(ValidationError) as exc_info:
            CertificateExportModel(**data)
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestCertificateResponseModel:
    """Tests for CertificateResponseModel validation."""

    def test_response_model_valid(self):
        """Test validation with valid response data."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestCert",
            "folder": "Texas",
        }
        model = CertificateResponseModel(**data)
        assert str(model.id) == data["id"]
        assert model.name == data["name"]
        assert model.folder == data["folder"]

    def test_response_model_with_all_fields(self):
        """Test validation with all optional fields."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestCert",
            "algorithm": "RSA",
            "ca": True,
            "common_name": "test.local",
            "common_name_int": "test.local",
            "expiry_epoch": "1735689600",
            "issuer": "CN=root-ca",
            "issuer_hash": "abc123",
            "not_valid_after": "Dec 31 2025",
            "not_valid_before": "Jan 01 2024",
            "public_key": "MIIBIjAN...",
            "subject": "CN=test.local",
            "subject_hash": "def456",
            "subject_int": "CN=test.local",
            "folder": "Texas",
        }
        model = CertificateResponseModel(**data)
        assert model.algorithm == "RSA"
        assert model.ca is True
        assert model.common_name == "test.local"

    def test_response_model_invalid_uuid(self):
        """Test validation with invalid UUID format."""
        data = {
            "id": "invalid-uuid",
            "name": "TestCert",
            "folder": "Texas",
        }
        with pytest.raises(ValidationError) as exc_info:
            CertificateResponseModel(**data)
        assert "Input should be a valid UUID" in str(exc_info.value)

    def test_response_model_ignores_extra_fields(self):
        """Test that extra fields are silently ignored in ResponseModel."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
            "name": "TestCert",
            "folder": "Texas",
            "unknown_field": "should_be_ignored",
        }
        model = CertificateResponseModel(**data)
        assert not hasattr(model, "unknown_field")

    def test_response_model_minimal(self):
        """Test validation with minimal required data (only id)."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426655440000",
        }
        model = CertificateResponseModel(**data)
        assert str(model.id) == data["id"]
        assert model.name is None
        assert model.folder is None


# -------------------- End of Test Classes --------------------
