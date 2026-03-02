# tests/factories/identity/certificate.py

"""Factory definitions for certificate objects.

Certificates use a non-standard pattern: generate, import, export, list, get, delete.
There are no standard Create/Update models.
"""

from uuid import uuid4

import factory  # type: ignore
from faker import Faker

from scm.models.identity.certificates import (
    CertificateResponseModel,
)

fake = Faker()


# ----------------------------------------------------------------------------
# API Response Factory
# ----------------------------------------------------------------------------
class CertificateResponseFactory(factory.Factory):
    """Factory for creating CertificateResponseModel instances."""

    class Meta:
        """Meta class that defines the model for CertificateResponseFactory."""

        model = CertificateResponseModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    name = factory.Sequence(lambda n: f"certificate_{n}")
    folder = "Texas"
    snippet = None
    device = None

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Factory method for creating with snippet."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """Factory method for creating with device."""
        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def from_request(cls, request_data, **kwargs):
        """Create response factory from request data dict."""
        data = {}
        if isinstance(request_data, dict):
            data = request_data.copy()
        else:
            data = request_data.model_dump()
        data.pop("id", None)
        return cls(**data, **kwargs)


# ----------------------------------------------------------------------------
# Model dict factories for Pydantic validation testing
# ----------------------------------------------------------------------------
class CertificateGenerateModelFactory(factory.Factory):
    """Factory for creating data dicts for CertificateGenerateModel validation testing."""

    class Meta:
        """Meta class that defines the model for CertificateGenerateModelFactory."""

        model = dict

    certificate_name = factory.Sequence(lambda n: f"cert_{n}")
    common_name = factory.Sequence(lambda n: f"cert{n}.local")
    signed_by = "root-ca"
    algorithm = factory.LazyFunction(lambda: {"rsa_number_of_bits": 2048})
    digest = "sha256"
    folder = "Shared"
    snippet = None
    device = None

    @classmethod
    def build_valid(cls, **kwargs):
        """Build valid certificate generate data."""
        defaults = {
            "certificate_name": "test-cert",
            "common_name": "test.local",
            "signed_by": "ca",
            "algorithm": {"rsa_number_of_bits": 2048},
            "digest": "sha256",
            "folder": "Shared",
            "snippet": None,
            "device": None,
        }
        defaults.update(kwargs)
        return cls(**defaults)


class CertificateImportModelFactory(factory.Factory):
    """Factory for creating data dicts for CertificateImportModel validation testing."""

    class Meta:
        """Meta class that defines the model for CertificateImportModelFactory."""

        model = dict

    name = factory.Sequence(lambda n: f"imported_cert_{n}")
    certificate_file = "base64encodeddata"
    format = "pem"
    folder = "Shared"
    snippet = None
    device = None

    @classmethod
    def build_valid(cls, **kwargs):
        """Build valid certificate import data."""
        defaults = {
            "name": "imported-cert",
            "certificate_file": "base64data",
            "format": "pem",
            "folder": "Shared",
            "snippet": None,
            "device": None,
        }
        defaults.update(kwargs)
        return cls(**defaults)


class CertificateExportModelFactory(factory.Factory):
    """Factory for creating data dicts for CertificateExportModel validation testing."""

    class Meta:
        """Meta class that defines the model for CertificateExportModelFactory."""

        model = dict

    format = "pem"

    @classmethod
    def build_valid(cls, **kwargs):
        """Build valid certificate export data."""
        defaults = {"format": "pem"}
        defaults.update(kwargs)
        return cls(**defaults)
