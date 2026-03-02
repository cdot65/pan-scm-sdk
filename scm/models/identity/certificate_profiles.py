"""Certificate Profile models for Strata Cloud Manager SDK.

Contains Pydantic models for representing certificate profile objects and related data.
"""

# scm/models/identity/certificate_profiles.py

from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


class CaCertificate(BaseModel):
    """CA certificate configuration within a certificate profile.

    Attributes:
        name (str): CA certificate name.
        default_ocsp_url (Optional[str]): Default OCSP responder URL.
        ocsp_verify_cert (Optional[str]): Certificate for OCSP response verification.
        template_name (Optional[str]): Template name.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(
        ...,
        description="CA certificate name",
    )
    default_ocsp_url: Optional[str] = Field(
        None,
        description="Default OCSP responder URL",
    )
    ocsp_verify_cert: Optional[str] = Field(
        None,
        description="Certificate for OCSP response verification",
    )
    template_name: Optional[str] = Field(
        None,
        description="Template name",
    )


class UsernameFieldSubject(str, Enum):
    """Enumeration of username field subject options."""

    common_name = "common-name"


class UsernameFieldSubjectAlt(str, Enum):
    """Enumeration of username field subject alternative options."""

    email = "email"


class CertProfileUsernameField(BaseModel):
    """Username field configuration for certificate profiles.

    Attributes:
        subject (Optional[UsernameFieldSubject]): Subject field for username extraction.
        subject_alt (Optional[UsernameFieldSubjectAlt]): Subject alternative field for username extraction.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    subject: Optional[UsernameFieldSubject] = Field(
        None,
        description="Subject field for username extraction",
    )
    subject_alt: Optional[UsernameFieldSubjectAlt] = Field(
        None,
        description="Subject alternative field for username extraction",
    )


# Base Model
class CertificateProfileBaseModel(BaseModel):
    """Base model for Certificate Profile containing common fields across all operations.

    Attributes:
        name (str): Profile name.
        ca_certificates (Optional[List[CaCertificate]]): List of CA certificates.
        username_field (Optional[CertProfileUsernameField]): Username field configuration.
        domain (Optional[str]): User domain.
        use_crl (Optional[bool]): Enable CRL checking.
        use_ocsp (Optional[bool]): Enable OCSP checking.
        crl_receive_timeout (Optional[int]): CRL receive timeout in seconds.
        ocsp_receive_timeout (Optional[int]): OCSP receive timeout in seconds.
        cert_status_timeout (Optional[int]): Certificate status timeout in seconds.
        block_unknown_cert (Optional[bool]): Block certificates with unknown status.
        block_timeout_cert (Optional[bool]): Block certificates on timeout.
        block_unauthenticated_cert (Optional[bool]): Block unauthenticated certificates.
        block_expired_cert (Optional[bool]): Block expired certificates.
        folder (Optional[str]): Folder in which the resource is defined.
        snippet (Optional[str]): Snippet in which the resource is defined.
        device (Optional[str]): Device in which the resource is defined.

    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    name: str = Field(
        ...,
        description="Profile name",
        max_length=63,
    )
    ca_certificates: Optional[List[CaCertificate]] = Field(
        None,
        description="List of CA certificates",
    )
    username_field: Optional[CertProfileUsernameField] = Field(
        None,
        description="Username field configuration",
    )
    domain: Optional[str] = Field(
        None,
        description="User domain",
    )
    use_crl: Optional[bool] = Field(
        None,
        description="Enable CRL checking",
    )
    use_ocsp: Optional[bool] = Field(
        None,
        description="Enable OCSP checking",
    )
    crl_receive_timeout: Optional[int] = Field(
        None,
        description="CRL receive timeout in seconds",
        ge=1,
        le=60,
    )
    ocsp_receive_timeout: Optional[int] = Field(
        None,
        description="OCSP receive timeout in seconds",
        ge=1,
        le=60,
    )
    cert_status_timeout: Optional[int] = Field(
        None,
        description="Certificate status timeout in seconds",
        ge=1,
        le=60,
    )
    block_unknown_cert: Optional[bool] = Field(
        None,
        description="Block certificates with unknown status",
    )
    block_timeout_cert: Optional[bool] = Field(
        None,
        description="Block certificates on timeout",
    )
    block_unauthenticated_cert: Optional[bool] = Field(
        None,
        description="Block unauthenticated certificates",
    )
    block_expired_cert: Optional[bool] = Field(
        None,
        description="Block expired certificates",
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


class CertificateProfileCreateModel(CertificateProfileBaseModel):
    """Model for creating a new Certificate Profile.

    Inherits from base model and adds create-specific validation.
    """

    @model_validator(mode="after")
    def validate_container_type(self) -> "CertificateProfileCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            CertificateProfileCreateModel: The validated model instance.

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


class CertificateProfileUpdateModel(CertificateProfileBaseModel):
    """Model for updating an existing Certificate Profile.

    All fields are optional to allow partial updates.
    """

    id: UUID = Field(
        ...,
        description="Profile ID",
    )


class CertificateProfileResponseModel(CertificateProfileBaseModel):
    """Model for Certificate Profile API responses.

    Includes all base fields plus the id field.
    """

    model_config = ConfigDict(
        extra="ignore",
        validate_assignment=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    id: UUID = Field(
        ...,
        description="Profile ID",
    )
