# Identity Models

## Overview

The Strata Cloud Manager SDK uses Pydantic models for data validation and serialization of identity and authentication configurations. These models ensure that the data being sent to and received from the Strata Cloud Manager API adheres to the expected structure and constraints. This section documents the models for identity service resources.

## Model Types

For each identity resource, there are corresponding model types:

- **Create Models**: Used when creating new identity resources (`{Object}CreateModel`)
- **Update Models**: Used when updating existing identity resources (`{Object}UpdateModel`)
- **Response Models**: Used when parsing identity data retrieved from the API (`{Object}ResponseModel`)
- **Base Models**: Common shared attributes for related identity models (`{Object}BaseModel`)

## Common Model Patterns

Identity models share common patterns:

- Container validation (exactly one of folder/snippet/device)
- UUID validation for identifiers
- Server list configurations with host, port, and optional credentials
- Protocol and method selection patterns

## Models by Category

### Authentication

- [Authentication Profile Models](authentication_profile_models.md) - Authentication profile configurations with method selection

### Server Profiles

- [Kerberos Server Profile Models](kerberos_server_profile_models.md) - Kerberos KDC server configurations
- [LDAP Server Profile Models](ldap_server_profile_models.md) - LDAP directory server configurations
- [RADIUS Server Profile Models](radius_server_profile_models.md) - RADIUS AAA server configurations
- [SAML Server Profile Models](saml_server_profile_models.md) - SAML Identity Provider configurations
- [TACACS+ Server Profile Models](tacacs_server_profile_models.md) - TACACS+ server configurations

## Usage Examples

```python
from scm.client import ScmClient
from scm.models.identity import (
    LdapServerProfileCreateModel,
    RadiusServerProfileCreateModel,
)

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Create using a model instance
ldap_profile = LdapServerProfileCreateModel(
    name="corp-ldap",
    folder="Texas",
    base="dc=example,dc=com",
    ldap_type="active-directory",
    ssl=True
)

result = client.ldap_server_profile.create(
    ldap_profile.model_dump(exclude_unset=True)
)
```

## Best Practices

1. **Model Validation**
    - Always validate identity configuration data with models before sending to the API
    - Handle validation errors appropriately
    - Use `model_dump(exclude_unset=True)` to avoid sending default values

2. **Server Configuration**
    - Define multiple servers for high availability
    - Use SSL/TLS where available for encrypted communication
    - Store secrets securely and avoid hardcoding credentials

3. **Error Handling**
    - Catch and handle `ValueError` exceptions from model validation
    - Validate that referenced server profiles exist before creating authentication profiles

## Related Documentation

- [Identity Services](../../config/identity/index.md) - Working with identity service configurations
- [Authentication Profile](../../config/identity/authentication_profile.md) - Authentication profile operations
