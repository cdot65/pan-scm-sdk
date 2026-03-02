# tests/factories/identity/__init__.py

"""Factory definitions for identity objects."""

from tests.factories.identity.authentication_profile import (
    AuthenticationProfileCreateApiFactory,
    AuthenticationProfileCreateModelFactory,
    AuthenticationProfileResponseFactory,
    AuthenticationProfileUpdateApiFactory,
    AuthenticationProfileUpdateModelFactory,
)
from tests.factories.identity.certificate import (
    CertificateExportModelFactory,
    CertificateGenerateModelFactory,
    CertificateImportModelFactory,
    CertificateResponseFactory,
)
from tests.factories.identity.certificate_profile import (
    CertificateProfileCreateApiFactory,
    CertificateProfileCreateModelFactory,
    CertificateProfileResponseFactory,
    CertificateProfileUpdateApiFactory,
    CertificateProfileUpdateModelFactory,
)
from tests.factories.identity.kerberos_server_profile import (
    KerberosServerProfileCreateApiFactory,
    KerberosServerProfileCreateModelFactory,
    KerberosServerProfileResponseFactory,
    KerberosServerProfileUpdateApiFactory,
    KerberosServerProfileUpdateModelFactory,
)
from tests.factories.identity.ldap_server_profile import (
    LdapServerProfileCreateApiFactory,
    LdapServerProfileCreateModelFactory,
    LdapServerProfileResponseFactory,
    LdapServerProfileUpdateApiFactory,
    LdapServerProfileUpdateModelFactory,
)
from tests.factories.identity.radius_server_profile import (
    RadiusServerProfileCreateApiFactory,
    RadiusServerProfileCreateModelFactory,
    RadiusServerProfileResponseFactory,
    RadiusServerProfileUpdateApiFactory,
    RadiusServerProfileUpdateModelFactory,
)
from tests.factories.identity.saml_server_profile import (
    SamlServerProfileCreateApiFactory,
    SamlServerProfileCreateModelFactory,
    SamlServerProfileResponseFactory,
    SamlServerProfileUpdateApiFactory,
    SamlServerProfileUpdateModelFactory,
)
from tests.factories.identity.tacacs_server_profile import (
    TacacsServerProfileCreateApiFactory,
    TacacsServerProfileCreateModelFactory,
    TacacsServerProfileResponseFactory,
    TacacsServerProfileUpdateApiFactory,
    TacacsServerProfileUpdateModelFactory,
)
from tests.factories.identity.tls_service_profile import (
    TlsServiceProfileCreateApiFactory,
    TlsServiceProfileCreateModelFactory,
    TlsServiceProfileResponseFactory,
    TlsServiceProfileUpdateApiFactory,
    TlsServiceProfileUpdateModelFactory,
)

__all__ = [
    "AuthenticationProfileCreateApiFactory",
    "AuthenticationProfileCreateModelFactory",
    "AuthenticationProfileResponseFactory",
    "AuthenticationProfileUpdateApiFactory",
    "AuthenticationProfileUpdateModelFactory",
    "CertificateExportModelFactory",
    "CertificateGenerateModelFactory",
    "CertificateImportModelFactory",
    "CertificateProfileCreateApiFactory",
    "CertificateProfileCreateModelFactory",
    "CertificateProfileResponseFactory",
    "CertificateProfileUpdateApiFactory",
    "CertificateProfileUpdateModelFactory",
    "CertificateResponseFactory",
    "KerberosServerProfileCreateApiFactory",
    "KerberosServerProfileCreateModelFactory",
    "KerberosServerProfileResponseFactory",
    "KerberosServerProfileUpdateApiFactory",
    "KerberosServerProfileUpdateModelFactory",
    "LdapServerProfileCreateApiFactory",
    "LdapServerProfileCreateModelFactory",
    "LdapServerProfileResponseFactory",
    "LdapServerProfileUpdateApiFactory",
    "LdapServerProfileUpdateModelFactory",
    "RadiusServerProfileCreateApiFactory",
    "RadiusServerProfileCreateModelFactory",
    "RadiusServerProfileResponseFactory",
    "RadiusServerProfileUpdateApiFactory",
    "RadiusServerProfileUpdateModelFactory",
    "SamlServerProfileCreateApiFactory",
    "SamlServerProfileCreateModelFactory",
    "SamlServerProfileResponseFactory",
    "SamlServerProfileUpdateApiFactory",
    "SamlServerProfileUpdateModelFactory",
    "TacacsServerProfileCreateApiFactory",
    "TacacsServerProfileCreateModelFactory",
    "TacacsServerProfileResponseFactory",
    "TacacsServerProfileUpdateApiFactory",
    "TacacsServerProfileUpdateModelFactory",
    "TlsServiceProfileCreateApiFactory",
    "TlsServiceProfileCreateModelFactory",
    "TlsServiceProfileResponseFactory",
    "TlsServiceProfileUpdateApiFactory",
    "TlsServiceProfileUpdateModelFactory",
]
