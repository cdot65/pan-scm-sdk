"""Authentication Profile models for Strata Cloud Manager SDK.

Contains Pydantic models for representing authentication profile objects and related data.
"""

# scm/models/identity/authentication_profiles.py

from typing import Dict, List, Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


# Nested Models for Method
class AuthProfileMethodSamlIdp(BaseModel):
    """SAML IDP method configuration.

    Attributes:
        attribute_name_usergroup (Optional[str]): Attribute name for user group.
        attribute_name_username (Optional[str]): Attribute name for username.
        certificate_profile (Optional[str]): Certificate profile name.
        enable_single_logout (Optional[bool]): Enable single logout.
        request_signing_certificate (Optional[str]): Request signing certificate.
        server_profile (Optional[str]): Server profile name.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    attribute_name_usergroup: Optional[str] = Field(
        None,
        description="Attribute name for user group",
    )
    attribute_name_username: Optional[str] = Field(
        None,
        description="Attribute name for username",
    )
    certificate_profile: Optional[str] = Field(
        None,
        description="Certificate profile name",
    )
    enable_single_logout: Optional[bool] = Field(
        None,
        description="Enable single logout",
    )
    request_signing_certificate: Optional[str] = Field(
        None,
        description="Request signing certificate",
    )
    server_profile: Optional[str] = Field(
        None,
        description="Server profile name",
    )


class AuthProfileMethodLdap(BaseModel):
    """LDAP method configuration.

    Attributes:
        login_attribute (Optional[str]): Login attribute.
        passwd_exp_days (Optional[int]): Password expiration days.
        server_profile (Optional[str]): Server profile name.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    login_attribute: Optional[str] = Field(
        None,
        description="Login attribute",
    )
    passwd_exp_days: Optional[int] = Field(
        None,
        description="Password expiration days",
    )
    server_profile: Optional[str] = Field(
        None,
        description="Server profile name",
    )


class AuthProfileMethodRadius(BaseModel):
    """RADIUS method configuration.

    Attributes:
        checkgroup (Optional[bool]): Check group membership.
        server_profile (Optional[str]): Server profile name.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    checkgroup: Optional[bool] = Field(
        None,
        description="Check group membership",
    )
    server_profile: Optional[str] = Field(
        None,
        description="Server profile name",
    )


class AuthProfileMethodTacplus(BaseModel):
    """TACACS+ method configuration.

    Attributes:
        checkgroup (Optional[bool]): Check group membership.
        server_profile (Optional[str]): Server profile name.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    checkgroup: Optional[bool] = Field(
        None,
        description="Check group membership",
    )
    server_profile: Optional[str] = Field(
        None,
        description="Server profile name",
    )


class AuthProfileMethodKerberos(BaseModel):
    """Kerberos method configuration.

    Attributes:
        realm (Optional[str]): Kerberos realm.
        server_profile (Optional[str]): Server profile name.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    realm: Optional[str] = Field(
        None,
        description="Kerberos realm",
    )
    server_profile: Optional[str] = Field(
        None,
        description="Server profile name",
    )


class AuthProfileMethod(BaseModel):
    """Authentication method configuration (oneOf pattern).

    Exactly one method type should be provided.

    Attributes:
        local_database (Optional[Dict]): Local database method.
        saml_idp (Optional[AuthProfileMethodSamlIdp]): SAML IDP method.
        ldap (Optional[AuthProfileMethodLdap]): LDAP method.
        radius (Optional[AuthProfileMethodRadius]): RADIUS method.
        tacplus (Optional[AuthProfileMethodTacplus]): TACACS+ method.
        kerberos (Optional[AuthProfileMethodKerberos]): Kerberos method.
        cloud (Optional[Dict]): Cloud method.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    local_database: Optional[Dict] = Field(
        None,
        description="Local database method",
    )
    saml_idp: Optional[AuthProfileMethodSamlIdp] = Field(
        None,
        description="SAML IDP method",
    )
    ldap: Optional[AuthProfileMethodLdap] = Field(
        None,
        description="LDAP method",
    )
    radius: Optional[AuthProfileMethodRadius] = Field(
        None,
        description="RADIUS method",
    )
    tacplus: Optional[AuthProfileMethodTacplus] = Field(
        None,
        description="TACACS+ method",
    )
    kerberos: Optional[AuthProfileMethodKerberos] = Field(
        None,
        description="Kerberos method",
    )
    cloud: Optional[Dict] = Field(
        None,
        description="Cloud method",
    )


class AuthProfileLockout(BaseModel):
    """Account lockout configuration.

    Attributes:
        failed_attempts (Optional[int]): Number of failed attempts before lockout.
        lockout_time (Optional[int]): Lockout duration in minutes.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    failed_attempts: Optional[int] = Field(
        None,
        description="Number of failed attempts before lockout",
    )
    lockout_time: Optional[int] = Field(
        None,
        description="Lockout duration in minutes",
    )


# Base Model
class AuthenticationProfileBaseModel(BaseModel):
    """Base model for Authentication Profile containing common fields across all operations."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    name: str = Field(
        ...,
        description="Profile name",
    )
    allow_list: Optional[List[str]] = Field(
        ["all"],
        description="Allow list",
    )
    lockout: Optional[AuthProfileLockout] = Field(
        None,
        description="Account lockout configuration",
    )
    method: Optional[AuthProfileMethod] = Field(
        None,
        description="Authentication method configuration",
    )
    multi_factor_auth: Optional[Dict] = Field(
        None,
        description="Multi-factor authentication configuration",
    )
    single_sign_on: Optional[Dict] = Field(
        None,
        description="Single sign-on configuration",
    )
    user_domain: Optional[str] = Field(
        None,
        description="User domain",
    )
    username_modifier: Optional[str] = Field(
        None,
        description="Username modifier",
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


class AuthenticationProfileCreateModel(AuthenticationProfileBaseModel):
    """Model for creating a new Authentication Profile.

    Inherits from base model and adds create-specific validation.
    """

    @model_validator(mode="after")
    def validate_container_type(self) -> "AuthenticationProfileCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            AuthenticationProfileCreateModel: The validated model instance.

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


class AuthenticationProfileUpdateModel(AuthenticationProfileBaseModel):
    """Model for updating an existing Authentication Profile.

    All fields are optional to allow partial updates.
    """

    id: UUID = Field(
        ...,
        description="Profile ID",
    )


class AuthenticationProfileResponseModel(AuthenticationProfileBaseModel):
    """Model for Authentication Profile API responses.

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
