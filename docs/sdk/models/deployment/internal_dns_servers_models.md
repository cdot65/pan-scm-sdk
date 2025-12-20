# Internal DNS Servers Models

## Overview {#Overview}

The Internal DNS Servers models provide a structured way to manage DNS server configurations in Palo Alto Networks' Strata Cloud Manager. These models handle validation of inputs and outputs when interacting with the SCM API for internal DNS server resources.

### Models

The module provides the following Pydantic models:

- `InternalDnsServersBaseModel`: Base model with fields common to all internal DNS server operations
- `InternalDnsServersCreateModel`: Model for creating new internal DNS servers
- `InternalDnsServersUpdateModel`: Model for updating existing internal DNS servers
- `InternalDnsServersResponseModel`: Response model for internal DNS server operations

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

## Attributes

| Attribute     | Type           | Required | Default | Description                                                                       |
|---------------|----------------|----------|---------|-----------------------------------------------------------------------------------|
| name          | str            | Yes      | None    | Name of the DNS server. Max length: 63 chars. Must match pattern: ^[0-9a-zA-Z._\- ]+$ |
| domain_name   | List[str]      | Yes      | None    | List of DNS domain names. Cannot be empty.                                        |
| primary       | IPvAnyAddress  | Yes      | None    | IP address of the primary DNS server                                              |
| secondary     | IPvAnyAddress  | No       | None    | IP address of the secondary DNS server                                            |
| id            | UUID           | Yes*     | None    | UUID of the DNS server (required for update and response models)                  |

\* Only required for update and response models

## Exceptions

The Internal DNS Servers models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When domain_name is empty
    - When domain_name is neither a string nor a list
    - When at least one field is not specified for updates
    - When name pattern validation fails
    - When IP address validation fails

## Model Validators

### Domain Name Validation

The models enforce that domain_name must be provided and cannot be empty:

```python
# This will raise a validation error
from scm.models.deployment import InternalDnsServersCreateModel

# Error: empty domain_name
try:
    dns_server = InternalDnsServersCreateModel(
        name="invalid-dns-server",
        domain_name=[],
        primary="192.168.1.10"
    )
except ValueError as e:
    print(e)  # "domain_name must not be empty"

# This will convert a single string to a list
dns_server = InternalDnsServersCreateModel(
    name="valid-dns-server",
    domain_name="example.com",  # Will be converted to ["example.com"]
    primary="192.168.1.10"
)
print(dns_server.domain_name)  # ["example.com"]
```

### Update Model Validation

For update operations, the model validates that at least one field other than id is provided:

```python
# This will raise a validation error
from scm.models.deployment import InternalDnsServersUpdateModel

# Error: no fields to update
try:
    dns_server = InternalDnsServersUpdateModel(
        id="123e4567-e89b-12d3-a456-426655440000"
        # No other fields provided
    )
except ValueError as e:
    print(e)  # "At least one field must be specified for update"
```

## Usage Examples

### Creating an Internal DNS Server

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
dns_dict = {
    "name": "main-dns-server",
    "domain_name": ["example.com", "internal.example.com"],
    "primary": "192.168.1.10",
    "secondary": "192.168.1.11"
}

response = client.internal_dns_server.create(dns_dict)
print(f"Created DNS server: {response.name} with ID: {response.id}")
```

### Updating an Internal DNS Server

```python
# Fetch existing DNS server
existing = client.internal_dns_server.fetch(name="main-dns-server")

# Modify attributes using dot notation
existing.domain_name = ["example.com", "updated.example.com"]
existing.secondary = "192.168.1.12"

# Pass modified object to update()
updated = client.internal_dns_server.update(existing)
print(f"Updated DNS server: {updated.name}")
```

### Working with Response Model

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Get an existing DNS server
dns_server = client.internal_dns_server.fetch(name="main-dns-server")

# Access response model attributes
print(f"DNS Server ID: {dns_server.id}")
print(f"DNS Server Name: {dns_server.name}")
print(f"Domain Names: {dns_server.domain_name}")
print(f"Primary DNS: {dns_server.primary}")
print(f"Secondary DNS: {dns_server.secondary}")

# Modify the response model using dot notation
dns_server.domain_name = dns_server.domain_name + ["new-domain.example.com"]

# Update the DNS server
updated = client.internal_dns_server.update(dns_server)
```

### Model Serialization

```python
from scm.models.deployment import InternalDnsServersCreateModel

# Create a model instance
dns_model = InternalDnsServersCreateModel(
    name="main-dns-server",
    domain_name=["example.com", "internal.example.com"],
    primary="192.168.1.10",
    secondary="192.168.1.11"
)

# Convert to dictionary (default)
model_dict = dns_model.model_dump()
print(model_dict)

# Convert to dictionary, excluding unset fields
model_dict_exclude_unset = dns_model.model_dump(exclude_unset=True)
print(model_dict_exclude_unset)

# Convert to dictionary, using field aliases if defined
model_dict_by_alias = dns_model.model_dump(by_alias=True)
print(model_dict_by_alias)

# Convert to JSON string
model_json = dns_model.model_dump_json()
print(model_json)

# IP addresses are serialized as strings for JSON compatibility
print(f"Primary DNS type: {type(dns_model.primary)}")  # IPvAnyAddress
print(f"Serialized primary DNS: {model_dict['primary']}")  # String
```

## Implementation Details

### InternalDnsServersBaseModel

This is the base model that contains common fields and validation logic used by all other Internal DNS Servers models.

#### Validators

- `serialize_ip_address`: Converts IPvAnyAddress objects to strings for JSON serialization
- `validate_domain_name`: Ensures domain_name is a list (converts single string to list)
- `validate_domain_name_not_empty`: Ensures domain_name is not empty

### InternalDnsServersCreateModel

Model used for creating new Internal DNS Servers.

#### Validators

- `validate_create_model`: Performs additional validation for creation operations

### InternalDnsServersUpdateModel

Model used for updating existing Internal DNS Servers. All fields except `id` are optional to support partial updates.

#### Validators

- `validate_update_model`: Validates update requirements:
  - At least one field other than id must be specified for update
  - Ensures domain_name is not empty if provided

### InternalDnsServersResponseModel

Model used for representing API responses for Internal DNS Servers operations.

#### Validators

- `validate_response_model`: Ensures response data consistency
