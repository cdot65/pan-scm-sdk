# tests/scm/config/identity/test_certificate.py

"""Tests for certificate identity configuration.

Certificates use a non-standard pattern: generate, import, export, list, get, delete.
There are no standard create or update operations.
"""

from unittest.mock import MagicMock
import pytest
from requests.exceptions import HTTPError

from scm.config.identity import Certificate
from scm.exceptions import InvalidObjectError, MissingQueryParameterError
from scm.models.identity.certificates import CertificateResponseModel
from tests.factories.identity.certificate import (
    CertificateResponseFactory,
)
from tests.utils import raise_mock_http_error


@pytest.mark.usefixtures("load_env")
class TestCertificateBase:
    """Base class for Certificate tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_scm):
        """Setup method that runs before each test."""
        self.mock_scm = mock_scm
        self.mock_scm.get = MagicMock()
        self.mock_scm.post = MagicMock()
        self.mock_scm.put = MagicMock()
        self.mock_scm.delete = MagicMock()
        self.client = Certificate(self.mock_scm, max_limit=5000)


class TestCertificateMaxLimit(TestCertificateBase):
    """Tests for Certificate max_limit functionality."""

    def test_default_max_limit(self):
        """Test that default max_limit is set correctly."""
        client = Certificate(self.mock_scm)
        assert client.max_limit == Certificate.DEFAULT_MAX_LIMIT
        assert client.max_limit == 2500

    def test_custom_max_limit(self):
        """Test setting a custom max_limit."""
        client = Certificate(self.mock_scm, max_limit=1000)
        assert client.max_limit == 1000

    def test_max_limit_setter(self):
        """Test the max_limit property setter."""
        client = Certificate(self.mock_scm)
        client.max_limit = 3000
        assert client.max_limit == 3000

    def test_invalid_max_limit_type(self):
        """Test that invalid max_limit type raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            Certificate(self.mock_scm, max_limit="invalid")
        assert "{'error': 'Invalid max_limit type'} - HTTP error: 400 - API error: E003" in str(
            exc_info.value
        )

    def test_max_limit_too_low(self):
        """Test that max_limit below 1 raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            Certificate(self.mock_scm, max_limit=0)
        assert "{'error': 'Invalid max_limit value'} - HTTP error: 400 - API error: E003" in str(
            exc_info.value
        )

    def test_max_limit_too_high(self):
        """Test that max_limit above ABSOLUTE_MAX_LIMIT raises error."""
        with pytest.raises(InvalidObjectError) as exc_info:
            Certificate(self.mock_scm, max_limit=6000)
        assert "max_limit exceeds maximum allowed value" in str(exc_info.value)


class TestCertificateList(TestCertificateBase):
    """Tests for listing Certificate objects."""

    def test_list_valid(self):
        """Test listing all objects successfully."""
        mock_response = {
            "data": [
                CertificateResponseFactory(name="cert1", folder="Texas").model_dump(),
                CertificateResponseFactory(name="cert2", folder="Texas").model_dump(),
            ],
            "offset": 0,
            "total": 2,
            "limit": 200,
        }
        self.mock_scm.get.return_value = mock_response
        existing_objects = self.client.list(folder="Texas")
        self.mock_scm.get.assert_called_once_with(
            "/config/identity/v1/certificates",
            params={"limit": 5000, "folder": "Texas", "offset": 0},
        )
        assert len(existing_objects) == 2
        assert isinstance(existing_objects[0], CertificateResponseModel)

    def test_list_folder_empty_error(self):
        """Test that an empty folder raises appropriate error."""
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=400,
            error_code="E003",
            message='"folder" is not allowed to be empty',
            error_type="Missing Query Parameter",
        )
        with pytest.raises(MissingQueryParameterError):
            self.client.list(folder="")

    def test_list_folder_nonexistent_error(self):
        """Test error handling when folder does not exist."""
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=404,
            error_code="API_I00013",
            message="Listing failed",
            error_type="Operation Impossible",
        )
        with pytest.raises(HTTPError):
            self.client.list(folder="NonexistentFolder")

    def test_list_container_missing_error(self):
        """Test that InvalidObjectError is raised when no container is provided."""
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=400,
            error_code="E003",
            message="Exactly one of 'folder', 'snippet', or 'device' must be provided.",
            error_type="Invalid Object",
        )
        with pytest.raises(InvalidObjectError):
            self.client.list()

    def test_list_container_multiple_error(self):
        """Test that InvalidObjectError is raised with multiple containers."""
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=400,
            error_code="E003",
            message="Multiple container types provided",
            error_type="Invalid Object",
        )
        with pytest.raises(InvalidObjectError):
            self.client.list(folder="folder1", snippet="snippet1")

    def test_list_response_invalid_format(self):
        """Test that InvalidObjectError is raised when response is not a dictionary."""
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Texas")
        assert exc_info.value.error_code == "E003"

    def test_list_response_invalid_data_field_missing(self):
        """Test that InvalidObjectError is raised when data field is missing."""
        self.mock_scm.get.return_value = {"wrong_field": "value"}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Texas")
        assert exc_info.value.error_code == "E003"

    def test_list_response_invalid_data_field_type(self):
        """Test that InvalidObjectError is raised when data field is not a list."""
        self.mock_scm.get.return_value = {"data": "not a list"}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.list(folder="Texas")
        assert exc_info.value.error_code == "E003"

    def test_list_http_error_no_content(self):
        """Test handling of HTTPError without content."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500
        self.mock_scm.get.side_effect = HTTPError(response=mock_response)
        with pytest.raises(HTTPError):
            self.client.list(folder="Texas")

    def test_list_exact_match(self):
        """Test that exact_match filters objects correctly."""
        mock_response = {
            "data": [
                CertificateResponseFactory(name="c_texas", folder="Texas").model_dump(),
                CertificateResponseFactory(name="c_all", folder="All").model_dump(),
            ]
        }
        self.mock_scm.get.return_value = mock_response
        filtered = self.client.list(folder="Texas", exact_match=True)
        assert len(filtered) == 1
        assert filtered[0].folder == "Texas"

    def test_list_exclude_folders(self):
        """Test that exclude_folders removes objects from specified folders."""
        mock_response = {
            "data": [
                CertificateResponseFactory(name="c1", folder="Texas").model_dump(),
                CertificateResponseFactory(name="c2", folder="All").model_dump(),
            ]
        }
        self.mock_scm.get.return_value = mock_response
        filtered = self.client.list(folder="Texas", exclude_folders=["All"])
        assert len(filtered) == 1

    def test_list_exclude_snippets(self):
        """Test that exclude_snippets removes objects from specified snippets."""
        mock_response = {
            "data": [
                CertificateResponseFactory(name="c1", folder="Texas").model_dump(),
                CertificateResponseFactory.with_snippet(name="c2", snippet="default").model_dump(),
            ]
        }
        self.mock_scm.get.return_value = mock_response
        filtered = self.client.list(folder="Texas", exclude_snippets=["default"])
        assert len(filtered) == 1
        assert filtered[0].name == "c1"

    def test_list_exclude_devices(self):
        """Test that exclude_devices removes objects from specified devices."""
        mock_response = {
            "data": [
                CertificateResponseFactory(name="c1", folder="Texas").model_dump(),
                CertificateResponseFactory.with_device(name="c2", device="DeviceA").model_dump(),
            ]
        }
        self.mock_scm.get.return_value = mock_response
        filtered = self.client.list(folder="Texas", exclude_devices=["DeviceA"])
        assert len(filtered) == 1
        assert filtered[0].name == "c1"

    def test_list_pagination_multiple_pages(self):
        """Test that pagination aggregates data from multiple pages."""
        client = Certificate(self.mock_scm, max_limit=2500)
        first_page = [
            CertificateResponseFactory(name=f"c1-{i}", folder="Texas").model_dump()
            for i in range(2500)
        ]
        second_page = [
            CertificateResponseFactory(name=f"c2-{i}", folder="Texas").model_dump()
            for i in range(2500)
        ]
        self.mock_scm.get.side_effect = [{"data": first_page}, {"data": second_page}, {"data": []}]
        results = client.list(folder="Texas")
        assert len(results) == 5000


class TestCertificateGenerate(TestCertificateBase):
    """Tests for generating Certificate objects."""

    def test_generate_valid(self):
        """Test generating a certificate with valid data."""
        test_data = {
            "certificate_name": "test-cert",
            "common_name": "test.local",
            "signed_by": "ca",
            "algorithm": {"rsa_number_of_bits": 2048},
            "digest": "sha256",
            "folder": "Shared",
        }
        mock_response = CertificateResponseFactory().model_dump()
        self.mock_scm.post.return_value = mock_response
        result = self.client.generate(test_data)
        self.mock_scm.post.assert_called_once()
        assert isinstance(result, CertificateResponseModel)

    def test_generate_http_error_no_content(self):
        """Test generation with HTTPError without content."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500
        self.mock_scm.post.side_effect = HTTPError(response=mock_response)
        with pytest.raises(HTTPError):
            self.client.generate(
                {
                    "certificate_name": "test",
                    "common_name": "test.local",
                    "signed_by": "ca",
                    "algorithm": {"rsa_number_of_bits": 2048},
                    "digest": "sha256",
                    "folder": "Shared",
                }
            )

    def test_generate_http_error_with_response(self):
        """Test that HTTPError with response content triggers proper error handling."""
        self.mock_scm.post.side_effect = raise_mock_http_error(
            status_code=400,
            error_code="API_I00013",
            message="Generate failed",
            error_type="Malformed Command",
        )
        with pytest.raises(HTTPError) as exc_info:
            self.client.generate(
                {
                    "certificate_name": "test",
                    "common_name": "test.local",
                    "signed_by": "ca",
                    "algorithm": {"rsa_number_of_bits": 2048},
                    "digest": "sha256",
                    "folder": "Shared",
                }
            )
        assert exc_info.value.response.json()["_errors"][0]["message"] == "Generate failed"

    def test_generate_generic_exception_handling(self):
        """Test handling of a generic exception during generate."""
        self.mock_scm.post.side_effect = Exception("Generic error")
        with pytest.raises(Exception) as exc_info:
            self.client.generate(
                {
                    "certificate_name": "test",
                    "common_name": "test.local",
                    "signed_by": "ca",
                    "algorithm": {"rsa_number_of_bits": 2048},
                    "digest": "sha256",
                    "folder": "Shared",
                }
            )
        assert str(exc_info.value) == "Generic error"

    def test_generate_with_optional_fields(self):
        """Test generating a certificate with optional fields."""
        test_data = {
            "certificate_name": "test-cert",
            "common_name": "test.local",
            "signed_by": "ca",
            "algorithm": {"rsa_number_of_bits": 2048},
            "digest": "sha256",
            "folder": "Shared",
            "day_till_expiration": 365,
            "is_certificate_authority": True,
            "email": "admin@example.com",
        }
        mock_response = CertificateResponseFactory().model_dump()
        self.mock_scm.post.return_value = mock_response
        result = self.client.generate(test_data)
        self.mock_scm.post.assert_called_once()
        assert isinstance(result, CertificateResponseModel)


class TestCertificateImport(TestCertificateBase):
    """Tests for importing Certificate objects."""

    def test_import_valid(self):
        """Test importing a certificate with valid data."""
        test_data = {
            "name": "imported-cert",
            "certificate_file": "base64data",
            "format": "pem",
            "folder": "Shared",
        }
        mock_response = CertificateResponseFactory().model_dump()
        self.mock_scm.post.return_value = mock_response
        result = self.client.import_cert(test_data)
        self.mock_scm.post.assert_called_once()
        assert isinstance(result, CertificateResponseModel)

    def test_import_http_error_no_content(self):
        """Test import with HTTPError without content."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500
        self.mock_scm.post.side_effect = HTTPError(response=mock_response)
        with pytest.raises(HTTPError):
            self.client.import_cert(
                {
                    "name": "test",
                    "certificate_file": "base64data",
                    "format": "pem",
                    "folder": "Shared",
                }
            )

    def test_import_http_error_with_response(self):
        """Test that HTTPError with response content triggers proper error handling."""
        self.mock_scm.post.side_effect = raise_mock_http_error(
            status_code=400,
            error_code="API_I00013",
            message="Import failed",
            error_type="Malformed Command",
        )
        with pytest.raises(HTTPError) as exc_info:
            self.client.import_cert(
                {
                    "name": "test",
                    "certificate_file": "base64data",
                    "format": "pem",
                    "folder": "Shared",
                }
            )
        assert exc_info.value.response.json()["_errors"][0]["message"] == "Import failed"

    def test_import_generic_exception_handling(self):
        """Test handling of a generic exception during import."""
        self.mock_scm.post.side_effect = Exception("Generic error")
        with pytest.raises(Exception) as exc_info:
            self.client.import_cert(
                {
                    "name": "test",
                    "certificate_file": "base64data",
                    "format": "pem",
                    "folder": "Shared",
                }
            )
        assert str(exc_info.value) == "Generic error"

    def test_import_with_key_file(self):
        """Test importing a certificate with key file and passphrase."""
        test_data = {
            "name": "imported-cert",
            "certificate_file": "base64data",
            "format": "pkcs12",
            "key_file": "base64keydata",
            "passphrase": "secret",
            "folder": "Shared",
        }
        mock_response = CertificateResponseFactory().model_dump()
        self.mock_scm.post.return_value = mock_response
        result = self.client.import_cert(test_data)
        self.mock_scm.post.assert_called_once()
        assert isinstance(result, CertificateResponseModel)

    def test_import_endpoint(self):
        """Test that import uses the correct endpoint."""
        test_data = {
            "name": "imported-cert",
            "certificate_file": "base64data",
            "format": "pem",
            "folder": "Shared",
        }
        mock_response = CertificateResponseFactory().model_dump()
        self.mock_scm.post.return_value = mock_response
        self.client.import_cert(test_data)
        call_args = self.mock_scm.post.call_args
        assert call_args[0][0] == "/config/identity/v1/certificates:import"


class TestCertificateExport(TestCertificateBase):
    """Tests for exporting Certificate objects."""

    def test_export_valid(self):
        """Test exporting a certificate with valid data."""
        cert_id = "123e4567-e89b-12d3-a456-426655440000"
        test_data = {"format": "pem"}
        mock_response = {"certificate": "base64data"}
        self.mock_scm.post.return_value = mock_response
        result = self.client.export(cert_id, test_data)
        self.mock_scm.post.assert_called_once_with(
            f"/config/identity/v1/certificates/{cert_id}:export",
            json={"format": "pem"},
        )
        assert result == {"certificate": "base64data"}

    def test_export_http_error_no_content(self):
        """Test export with HTTPError without content."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500
        self.mock_scm.post.side_effect = HTTPError(response=mock_response)
        with pytest.raises(HTTPError):
            self.client.export("123e4567-e89b-12d3-a456-426655440000", {"format": "pem"})

    def test_export_http_error_with_response(self):
        """Test that HTTPError with response content triggers proper error handling."""
        self.mock_scm.post.side_effect = raise_mock_http_error(
            status_code=400,
            error_code="API_I00013",
            message="Export failed",
            error_type="Malformed Command",
        )
        with pytest.raises(HTTPError) as exc_info:
            self.client.export("123e4567-e89b-12d3-a456-426655440000", {"format": "pem"})
        assert exc_info.value.response.json()["_errors"][0]["message"] == "Export failed"

    def test_export_generic_exception_handling(self):
        """Test handling of a generic exception during export."""
        self.mock_scm.post.side_effect = Exception("Generic error")
        with pytest.raises(Exception) as exc_info:
            self.client.export("123e4567-e89b-12d3-a456-426655440000", {"format": "pem"})
        assert str(exc_info.value) == "Generic error"

    def test_export_with_passphrase(self):
        """Test exporting a certificate with passphrase."""
        cert_id = "123e4567-e89b-12d3-a456-426655440000"
        test_data = {"format": "pkcs12", "passphrase": "secret"}
        mock_response = {"certificate": "base64data"}
        self.mock_scm.post.return_value = mock_response
        result = self.client.export(cert_id, test_data)
        self.mock_scm.post.assert_called_once_with(
            f"/config/identity/v1/certificates/{cert_id}:export",
            json={"format": "pkcs12", "passphrase": "secret"},
        )
        assert result == {"certificate": "base64data"}


class TestCertificateGet(TestCertificateBase):
    """Tests for retrieving Certificate objects."""

    def test_get_valid_object(self):
        """Test retrieving a specific object."""
        mock_response = CertificateResponseFactory.build()
        self.mock_scm.get.return_value = mock_response.model_dump()
        retrieved_object = self.client.get(str(mock_response.id))
        self.mock_scm.get.assert_called_once_with(
            f"/config/identity/v1/certificates/{mock_response.id}"
        )
        assert isinstance(retrieved_object, CertificateResponseModel)

    def test_get_object_not_present_error(self):
        """Test error handling when object is not present."""
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )
        with pytest.raises(HTTPError):
            self.client.get("123e4567-e89b-12d3-a456-426655440000")

    def test_get_generic_exception_handling(self):
        """Test generic exception handling in get method."""
        self.mock_scm.get.side_effect = Exception("Generic error")
        with pytest.raises(Exception) as exc_info:
            self.client.get("123e4567-e89b-12d3-a456-426655440000")
        assert str(exc_info.value) == "Generic error"

    def test_get_http_error_no_response_content(self):
        """Test get method when HTTP error has no response content."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500
        self.mock_scm.get.side_effect = HTTPError(response=mock_response)
        with pytest.raises(HTTPError):
            self.client.get("123e4567-e89b-12d3-a456-426655440000")

    def test_get_server_error(self):
        """Test handling of server errors during get method."""
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )
        with pytest.raises(HTTPError):
            self.client.get("123e4567-e89b-12d3-a456-426655440000")


class TestCertificateDelete(TestCertificateBase):
    """Tests for deleting Certificate objects."""

    def test_delete_success(self):
        """Test successful deletion of an object."""
        object_id = "123e4567-e89b-12d3-a456-426655440000"
        self.mock_scm.delete.return_value = None
        self.client.delete(object_id)
        self.mock_scm.delete.assert_called_once_with(
            f"/config/identity/v1/certificates/{object_id}"
        )

    def test_delete_referenced_object(self):
        """Test deleting an object that is referenced."""
        self.mock_scm.delete.side_effect = raise_mock_http_error(
            status_code=409,
            error_code="E009",
            message="Reference not zero",
            error_type="Reference Not Zero",
        )
        with pytest.raises(HTTPError):
            self.client.delete("123e4567-e89b-12d3-a456-426655440000")

    def test_delete_object_not_present_error(self):
        """Test error handling when the object to delete is not present."""
        self.mock_scm.delete.side_effect = raise_mock_http_error(
            status_code=404,
            error_code="API_I00013",
            message="Object not found",
            error_type="Object Not Present",
        )
        with pytest.raises(HTTPError):
            self.client.delete("123e4567-e89b-12d3-a456-426655440000")

    def test_delete_http_error_no_response_content(self):
        """Test delete method when HTTP error has no response content."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500
        self.mock_scm.delete.side_effect = HTTPError(response=mock_response)
        with pytest.raises(HTTPError):
            self.client.delete("123e4567-e89b-12d3-a456-426655440000")

    def test_delete_generic_exception_handling(self):
        """Test handling of a generic exception during delete."""
        self.mock_scm.delete.side_effect = Exception("Generic error")
        with pytest.raises(Exception) as exc_info:
            self.client.delete("abcdefg")
        assert str(exc_info.value) == "Generic error"

    def test_delete_server_error(self):
        """Test handling of server errors during delete."""
        self.mock_scm.delete.side_effect = raise_mock_http_error(
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )
        with pytest.raises(HTTPError):
            self.client.delete("123e4567-e89b-12d3-a456-426655440000")


class TestCertificateFetch(TestCertificateBase):
    """Tests for fetching Certificate objects by name."""

    def test_fetch_valid_object(self):
        """Test retrieving an object by its name using the fetch method."""
        mock_response_model = CertificateResponseFactory.build()
        self.mock_scm.get.return_value = mock_response_model.model_dump()
        fetched_object = self.client.fetch(
            name=mock_response_model.name, folder=mock_response_model.folder
        )
        self.mock_scm.get.assert_called_once_with(
            "/config/identity/v1/certificates",
            params={"folder": mock_response_model.folder, "name": mock_response_model.name},
        )
        assert isinstance(fetched_object, CertificateResponseModel)

    def test_fetch_empty_name_error(self):
        """Test fetching with an empty name parameter."""
        with pytest.raises(MissingQueryParameterError):
            self.client.fetch(name="", folder="Texas")

    def test_fetch_empty_container_error(self):
        """Test fetching with an empty folder parameter."""
        with pytest.raises(MissingQueryParameterError):
            self.client.fetch(name="test", folder="")

    def test_fetch_no_container_provided_error(self):
        """Test that InvalidObjectError is raised when no container is provided."""
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test-cert")
        assert exc_info.value.error_code == "E003"

    def test_fetch_multiple_containers_provided_error(self):
        """Test that InvalidObjectError is raised with multiple containers."""
        with pytest.raises(InvalidObjectError):
            self.client.fetch(name="test", folder="Texas", snippet="TestSnippet")

    def test_fetch_missing_id_field_error(self):
        """Test that InvalidObjectError is raised when response is missing id field."""
        self.mock_scm.get.return_value = {"name": "test", "folder": "Texas"}
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test", folder="Texas")
        assert exc_info.value.error_code == "E003"
        assert exc_info.value.http_status_code == 500

    def test_fetch_invalid_response_type_error(self):
        """Test that InvalidObjectError is raised when response is not a dictionary."""
        self.mock_scm.get.return_value = ["not", "a", "dictionary"]
        with pytest.raises(InvalidObjectError) as exc_info:
            self.client.fetch(name="test123", folder="Texas")
        assert exc_info.value.error_code == "E003"

    def test_fetch_http_error_no_response_content(self):
        """Test that HTTPError without response content re-raises the exception."""
        mock_response = MagicMock()
        mock_response.content = None
        mock_response.status_code = 500
        self.mock_scm.get.side_effect = HTTPError(response=mock_response)
        with pytest.raises(HTTPError):
            self.client.fetch(name="test", folder="Texas")

    def test_fetch_server_error(self):
        """Test handling of server errors during fetch."""
        self.mock_scm.get.side_effect = raise_mock_http_error(
            status_code=500,
            error_code="E003",
            message="An internal error occurred",
            error_type="Internal Error",
        )
        with pytest.raises(HTTPError):
            self.client.fetch(name="test", folder="Texas")

    def test_fetch_generic_exception_handling(self):
        """Test generic exception handling during fetch."""
        self.mock_scm.get.side_effect = Exception("Generic error")
        with pytest.raises(Exception) as exc_info:
            self.client.fetch(name="test", folder="Texas")
        assert str(exc_info.value) == "Generic error"
