"""Certificate models for Strata Cloud Manager SDK.

Contains Pydantic models for representing certificate objects and related data.
Certificates use a non-standard pattern: generate (POST), import, export, list, get, delete.
There are no standard create or update operations.
"""

# scm/models/identity/certificates.py

from enum import Enum
from typing import Dict, List, Optional, Union
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


class CertificateDigest(str, Enum):
    """Enumeration of supported certificate digest algorithms."""

    sha1 = "sha1"
    sha256 = "sha256"
    sha384 = "sha384"
    sha512 = "sha512"
    md5 = "md5"


class CertificateFormat(str, Enum):
    """Enumeration of supported certificate formats."""

    pem = "pem"
    pkcs12 = "pkcs12"
    der = "der"


# Response model for GET
class CertificateResponseModel(BaseModel):
    """Model for Certificate API responses.

    Attributes:
        id (UUID): Certificate UUID.
        name (Optional[str]): Certificate name.
        algorithm (Optional[str]): Algorithm used.
        ca (Optional[bool]): Whether this is a CA certificate.
        common_name (Optional[str]): Common name.
        common_name_int (Optional[str]): Internal common name.
        expiry_epoch (Optional[str]): Expiry epoch timestamp.
        issuer (Optional[str]): Certificate issuer.
        issuer_hash (Optional[str]): Issuer hash.
        not_valid_after (Optional[str]): Certificate expiry date.
        not_valid_before (Optional[str]): Certificate start date.
        public_key (Optional[str]): Public key.
        subject (Optional[str]): Certificate subject.
        subject_hash (Optional[str]): Subject hash.
        subject_int (Optional[str]): Internal subject.
        folder (Optional[str]): Folder in which the resource is defined.
        snippet (Optional[str]): Snippet in which the resource is defined.
        device (Optional[str]): Device in which the resource is defined.

    """

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    id: UUID = Field(
        ...,
        description="Certificate UUID",
    )
    name: Optional[str] = Field(
        None,
        description="Certificate name",
    )
    algorithm: Optional[str] = Field(
        None,
        description="Algorithm used",
    )
    ca: Optional[bool] = Field(
        None,
        description="Whether this is a CA certificate",
    )
    common_name: Optional[str] = Field(
        None,
        description="Common name",
    )
    common_name_int: Optional[str] = Field(
        None,
        description="Internal common name",
    )
    expiry_epoch: Optional[str] = Field(
        None,
        description="Expiry epoch timestamp",
    )
    issuer: Optional[str] = Field(
        None,
        description="Certificate issuer",
    )
    issuer_hash: Optional[str] = Field(
        None,
        description="Issuer hash",
    )
    not_valid_after: Optional[str] = Field(
        None,
        description="Certificate expiry date",
    )
    not_valid_before: Optional[str] = Field(
        None,
        description="Certificate start date",
    )
    public_key: Optional[Union[str, Dict]] = Field(
        None,
        description="Public key (string or empty dict from API)",
    )
    subject: Optional[str] = Field(
        None,
        description="Certificate subject",
    )
    subject_hash: Optional[str] = Field(
        None,
        description="Subject hash",
    )
    subject_int: Optional[str] = Field(
        None,
        description="Internal subject",
    )
    folder: Optional[str] = Field(
        None,
        description="Folder in which the resource is defined",
        max_length=64,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
    )
    snippet: Optional[str] = Field(
        None,
        description="Snippet in which the resource is defined",
        max_length=64,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
    )
    device: Optional[str] = Field(
        None,
        description="Device in which the resource is defined",
        max_length=64,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
    )


# Generate model (POST /certificates)
class CertificateGenerateModel(BaseModel):
    """Model for generating a new certificate via POST.

    Attributes:
        certificate_name (str): Certificate name.
        common_name (str): Common name for the certificate.
        signed_by (str): Signing CA name.
        algorithm (dict): RSA or ECDSA configuration.
        digest (CertificateDigest): Hash algorithm.
        day_till_expiration (Optional[int]): Days until certificate expiry.
        is_certificate_authority (Optional[bool]): Whether this is a CA certificate.
        is_block_privateKey (Optional[bool]): Block private key export.
        email (Optional[str]): Email address.
        hostname (Optional[List[str]]): Hostnames for the certificate.
        ip (Optional[List[str]]): IP addresses for the certificate.
        country_code (Optional[str]): Country code.
        state (Optional[str]): State or province.
        locality (Optional[str]): Locality or city.
        department (Optional[List[str]]): Department names.
        ocsp_responder_url (Optional[str]): OCSP responder URL.
        folder (Optional[str]): Folder in which the resource is defined.
        snippet (Optional[str]): Snippet in which the resource is defined.
        device (Optional[str]): Device in which the resource is defined.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    certificate_name: str = Field(
        ...,
        description="Certificate name",
    )
    common_name: str = Field(
        ...,
        description="Common name for the certificate",
    )
    signed_by: str = Field(
        ...,
        description="Signing CA name",
        max_length=64,
    )
    algorithm: dict = Field(
        ...,
        description="RSA or ECDSA configuration, e.g. {'rsa_number_of_bits': 2048}",
    )
    digest: CertificateDigest = Field(
        ...,
        description="Hash algorithm",
    )
    day_till_expiration: Optional[int] = Field(
        None,
        description="Days until certificate expiry",
    )
    is_certificate_authority: Optional[bool] = Field(
        None,
        description="Whether this is a CA certificate",
    )
    is_block_privateKey: Optional[bool] = Field(  # noqa: N815
        None,
        description="Block private key export",
    )
    email: Optional[str] = Field(
        None,
        description="Email address",
    )
    hostname: Optional[List[str]] = Field(
        None,
        description="Hostnames for the certificate",
    )
    ip: Optional[List[str]] = Field(
        None,
        description="IP addresses for the certificate",
    )
    country_code: Optional[str] = Field(
        None,
        description="Country code",
    )
    state: Optional[str] = Field(
        None,
        description="State or province",
        max_length=32,
    )
    locality: Optional[str] = Field(
        None,
        description="Locality or city",
        max_length=64,
    )
    department: Optional[List[str]] = Field(
        None,
        description="Department names",
    )
    ocsp_responder_url: Optional[str] = Field(
        None,
        description="OCSP responder URL",
        max_length=64,
    )
    folder: Optional[str] = Field(
        None,
        description="Folder in which the resource is defined",
        max_length=64,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
    )
    snippet: Optional[str] = Field(
        None,
        description="Snippet in which the resource is defined",
    )
    device: Optional[str] = Field(
        None,
        description="Device in which the resource is defined",
    )

    @model_validator(mode="after")
    def validate_container_type(self) -> "CertificateGenerateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            CertificateGenerateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = [
            "folder",
            "snippet",
            "device",
        ]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


# Import model (POST /certificates:import)
class CertificateImportModel(BaseModel):
    """Model for importing a certificate via POST to :import endpoint.

    Attributes:
        name (str): Certificate name.
        certificate_file (str): Base64 encoded certificate file.
        format (CertificateFormat): Certificate format.
        key_file (Optional[str]): Base64 encoded private key file.
        passphrase (Optional[str]): Private key passphrase.
        folder (Optional[str]): Folder in which the resource is defined.
        snippet (Optional[str]): Snippet in which the resource is defined.
        device (Optional[str]): Device in which the resource is defined.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    name: str = Field(
        ...,
        description="Certificate name",
    )
    certificate_file: str = Field(
        ...,
        description="Base64 encoded certificate file",
    )
    format: CertificateFormat = Field(
        CertificateFormat.pem,
        description="Certificate format",
    )
    key_file: Optional[str] = Field(
        None,
        description="Base64 encoded private key file",
    )
    passphrase: Optional[str] = Field(
        None,
        description="Private key passphrase",
    )
    folder: Optional[str] = Field(
        None,
        description="Folder in which the resource is defined",
        max_length=64,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
    )
    snippet: Optional[str] = Field(
        None,
        description="Snippet in which the resource is defined",
    )
    device: Optional[str] = Field(
        None,
        description="Device in which the resource is defined",
    )

    @model_validator(mode="after")
    def validate_container_type(self) -> "CertificateImportModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            CertificateImportModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = [
            "folder",
            "snippet",
            "device",
        ]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


# Export model (POST /certificates/{id}:export)
class CertificateExportModel(BaseModel):
    """Model for exporting a certificate via POST to {id}:export endpoint.

    Attributes:
        format (CertificateFormat): Certificate export format.
        passphrase (Optional[str]): Passphrase for encrypted export.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    format: CertificateFormat = Field(
        ...,
        description="Certificate export format",
    )
    passphrase: Optional[str] = Field(
        None,
        description="Passphrase for encrypted export",
    )
