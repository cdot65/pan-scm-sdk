# Authentication Profile Models

Models for authentication profile objects in Strata Cloud Manager, defining how users authenticate using various methods.

## Overview

The Authentication Profile models support the following key attributes:

- Profile name and container assignment
- Authentication method selection (LDAP, RADIUS, SAML, Kerberos, TACACS+, local database, cloud)
- Allow list configuration
- Account lockout settings
- Multi-factor authentication and single sign-on options
- User domain and username modifier

## Base Models

### AuthenticationProfileBaseModel

The base model contains fields common to all CRUD operations.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | `str` | Yes | Profile name |
| `allow_list` | `List[str]` | No | Allow list (defaults to `["all"]`) |
| `lockout` | `AuthProfileLockout` | No | Account lockout configuration |
| `method` | `AuthProfileMethod` | No | Authentication method configuration |
| `multi_factor_auth` | `Dict` | No | Multi-factor authentication configuration |
| `single_sign_on` | `Dict` | No | Single sign-on configuration |
| `user_domain` | `str` | No | User domain |
| `username_modifier` | `str` | No | Username modifier |
| `folder` | `str` | No* | Folder in which the resource is defined |
| `snippet` | `str` | No* | Snippet in which the resource is defined |
| `device` | `str` | No* | Device in which the resource is defined |

\* Exactly one of `folder`, `snippet`, or `device` is required.

### AuthenticationProfileCreateModel

Inherits from `AuthenticationProfileBaseModel` and adds container validation ensuring exactly one of `folder`, `snippet`, or `device` is provided.

### AuthenticationProfileUpdateModel

Inherits from `AuthenticationProfileBaseModel` with an additional required field:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes | The unique identifier of the profile |

### AuthenticationProfileResponseModel

Inherits from `AuthenticationProfileBaseModel` with an additional field:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes | The unique identifier of the profile |

!!! note
    The response model uses `extra="ignore"` to handle any additional fields returned by the API.

## Component Models

### AuthProfileMethod

Authentication method configuration. Exactly one method type should be provided.

| Field | Type | Description |
| --- | --- | --- |
| `local_database` | `Dict` | Local database method |
| `saml_idp` | `AuthProfileMethodSamlIdp` | SAML IDP method |
| `ldap` | `AuthProfileMethodLdap` | LDAP method |
| `radius` | `AuthProfileMethodRadius` | RADIUS method |
| `tacplus` | `AuthProfileMethodTacplus` | TACACS+ method |
| `kerberos` | `AuthProfileMethodKerberos` | Kerberos method |
| `cloud` | `Dict` | Cloud method |

### AuthProfileMethodSamlIdp

| Field | Type | Description |
| --- | --- | --- |
| `attribute_name_usergroup` | `str` | Attribute name for user group |
| `attribute_name_username` | `str` | Attribute name for username |
| `certificate_profile` | `str` | Certificate profile name |
| `enable_single_logout` | `bool` | Enable single logout |
| `request_signing_certificate` | `str` | Request signing certificate |
| `server_profile` | `str` | Server profile name |

### AuthProfileMethodLdap

| Field | Type | Description |
| --- | --- | --- |
| `login_attribute` | `str` | Login attribute |
| `passwd_exp_days` | `int` | Password expiration days |
| `server_profile` | `str` | Server profile name |

### AuthProfileMethodRadius

| Field | Type | Description |
| --- | --- | --- |
| `checkgroup` | `bool` | Check group membership |
| `server_profile` | `str` | Server profile name |

### AuthProfileMethodTacplus

| Field | Type | Description |
| --- | --- | --- |
| `checkgroup` | `bool` | Check group membership |
| `server_profile` | `str` | Server profile name |

### AuthProfileMethodKerberos

| Field | Type | Description |
| --- | --- | --- |
| `realm` | `str` | Kerberos realm |
| `server_profile` | `str` | Server profile name |

### AuthProfileLockout

| Field | Type | Description |
| --- | --- | --- |
| `failed_attempts` | `int` | Number of failed attempts before lockout |
| `lockout_time` | `int` | Lockout duration in minutes |

## Usage Examples

### Creating an Authentication Profile

```python
from scm.models.identity.authentication_profiles import (
    AuthenticationProfileCreateModel,
    AuthProfileMethod,
    AuthProfileMethodLdap,
    AuthProfileLockout,
)

# Create model instance with LDAP method
profile = AuthenticationProfileCreateModel(
    name="corp-auth",
    folder="Texas",
    method=AuthProfileMethod(
        ldap=AuthProfileMethodLdap(
            server_profile="corp-ldap",
            login_attribute="sAMAccountName",
            passwd_exp_days=90
        )
    ),
    lockout=AuthProfileLockout(
        failed_attempts=5,
        lockout_time=30
    ),
    allow_list=["all"],
    user_domain="example.com"
)

# Use with SDK
payload = profile.model_dump(exclude_unset=True)
result = client.authentication_profile.create(payload)
```

### Parsing an Authentication Profile Response

```python
from scm.models.identity.authentication_profiles import (
    AuthenticationProfileResponseModel,
)

# Parse API response
response = AuthenticationProfileResponseModel(**api_response)
print(f"Name: {response.name}")
print(f"Domain: {response.user_domain}")
if response.method and response.method.ldap:
    print(f"LDAP Profile: {response.method.ldap.server_profile}")
```

## Related Topics

- [Authentication Profile Service](../../config/identity/authentication_profile.md)
- [LDAP Server Profile Models](ldap_server_profile_models.md)
- [RADIUS Server Profile Models](radius_server_profile_models.md)
- [SAML Server Profile Models](saml_server_profile_models.md)
