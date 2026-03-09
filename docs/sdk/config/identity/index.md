# Identity and Authentication Services

This section covers the identity and authentication services provided by the Palo Alto Networks Strata Cloud Manager SDK. Each service corresponds to a resource in the Strata Cloud Manager and provides methods for CRUD (Create, Read, Update, Delete) operations.

## Available Identity Services

### Authentication

- [Authentication Profile](authentication_profile.md) - Configure authentication profiles with methods such as LDAP, RADIUS, SAML, Kerberos, TACACS+, and local database

### Server Profiles

- [Kerberos Server Profile](kerberos_server_profile.md) - Configure Kerberos server profiles for Kerberos-based authentication
- [LDAP Server Profile](ldap_server_profile.md) - Configure LDAP server profiles for directory-based authentication
- [RADIUS Server Profile](radius_server_profile.md) - Configure RADIUS server profiles for centralized authentication
- [SAML Server Profile](saml_server_profile.md) - Configure SAML server profiles for single sign-on authentication
- [TACACS+ Server Profile](tacacs_server_profile.md) - Configure TACACS+ server profiles for terminal access controller authentication

## Common Features

All identity service objects provide standard operations:

- Create new identity configurations
- Read existing identity objects
- Update identity properties
- Delete identity objects
- List and filter identity objects with pagination support

The identity objects also enforce:

- Container validation (folder/device/snippet)
- Data validation with detailed error messages
- Consistent API patterns across all identity object types

## Usage Example

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Create an LDAP server profile
client.ldap_server_profile.create({
    "name": "corp-ldap",
    "server": [
        {
            "name": "ldap-primary",
            "address": "ldap.example.com",
            "port": 389
        }
    ],
    "base": "dc=example,dc=com",
    "ldap_type": "active-directory",
    "folder": "Texas"
})

# List authentication profiles
profiles = client.authentication_profile.list(folder="Texas")
for profile in profiles:
    print(f"Profile: {profile.name}")
```

Select a service from the list above to view detailed documentation, including methods, parameters, and examples.
