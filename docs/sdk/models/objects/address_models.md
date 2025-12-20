# Address Models

## Overview {#Overview}

The Address models provide a structured way to manage network addresses in Palo Alto Networks' Strata Cloud Manager.
These models support IP addresses (with CIDR notation), IP ranges, IP wildcards, and FQDNs. The models handle validation
of inputs and outputs when interacting with the SCM API.

## Attributes

| Attribute   | Type      | Required | Default | Description                                                                        |
|-------------|-----------|----------|---------|------------------------------------------------------------------------------------|
| name        | str       | Yes      | None    | Name of the address. Max length: 63 chars. Pattern: `^[a-zA-Z0-9_ \.-]+$`          |
| description | str       | No       | None    | Description of the address. Max length: 1023 chars                                 |
| tag         | List[str] | No       | None    | List of tags. Each tag max length: 127 chars                                       |
| ip_netmask  | str       | No*      | None    | IP address with optional CIDR notation (e.g. "192.168.80.0/24")                    |
| ip_range    | str       | No*      | None    | IP address range (e.g. "10.0.0.1-10.0.0.4")                                        |
| ip_wildcard | str       | No*      | None    | IP wildcard mask (e.g. "10.20.1.0/0.0.248.255")                                    |
| fqdn        | str       | No*      | None    | FQDN. Min: 1, Max: 255 chars. Pattern: `^[a-zA-Z0-9_]([a-zA-Z0-9._-])*[a-zA-Z0-9]$`|
| folder      | str       | No**     | None    | Folder where address is defined. Max: 64 chars. Pattern: `^[a-zA-Z\d\-_. ]+$`      |
| snippet     | str       | No**     | None    | Snippet where address is defined. Max: 64 chars. Pattern: `^[a-zA-Z\d\-_. ]+$`     |
| device      | str       | No**     | None    | Device where address is defined. Max: 64 chars. Pattern: `^[a-zA-Z\d\-_. ]+$`      |
| id          | UUID      | Yes***   | None    | UUID of the address (response/update models)                                       |

\* Exactly one address type (ip_netmask/ip_range/ip_wildcard/fqdn) must be provided
\** Exactly one container type (folder/snippet/device) must be provided for create operations
\*** Required for response model; required for update model

!!! note
    All models use `extra="forbid"` in the model config, which means they will reject any fields not explicitly defined in the model.

## Exceptions

The Address models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
  - When no address type or multiple address types are provided
  - When multiple container types (folder/snippet/device) are specified for create operations
  - When no container type is specified for create operations
  - When tag values are not unique in a list
  - When tag input is neither a string nor a list
  - When FQDN pattern validation fails
  - When name pattern validation fails

## Model Validators

### Address Type Validation

The models enforce that exactly one address type must be specified:

```python
# This will raise a validation error
from scm.models.objects import AddressCreateModel

# Error: multiple address types provided
try:
    address = AddressCreateModel(
        name="invalid-address",
        ip_netmask="192.168.1.0/24",
        fqdn="example.com",
        folder="Texas"
    )
except ValueError as e:
    print(e)  # "Exactly one of 'ip_netmask', 'ip_range', 'ip_wildcard', or 'fqdn' must be provided."

# Error: no address type provided
try:
    address = AddressCreateModel(
        name="invalid-address",
        folder="Texas"
    )
except ValueError as e:
    print(e)  # "Value error, Exactly one of 'ip_netmask', 'ip_range', 'ip_wildcard', or 'fqdn' must be provided."
```

### Container Type Validation

For create operations, exactly one container type must be specified:

```python
# This will raise a validation error
try:
    address = AddressCreateModel(
        name="invalid-address",
        ip_netmask="192.168.1.0/24",
        folder="Texas",
        device="fw01"  # Can't specify both folder and device
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."
```

### Tag Validation

Tags must be unique and properly formatted:

```python
# This will raise a validation error for duplicate tags
try:
    address = AddressCreateModel(
        name="invalid-address",
        ip_netmask="192.168.1.0/24",
        folder="Texas",
        tag=["web", "web"]  # Duplicate tags not allowed
    )
except ValueError as e:
    print(e)  # "List items must be unique"

# This will convert a single string tag to a list
address = AddressCreateModel(
    name="valid-address",
    ip_netmask="192.168.1.0/24",
    folder="Texas",
    tag="web"  # Will be converted to ["web"]
)
```

## Usage Examples

### Creating an Address Object

```python
from scm.client import ScmClient
from scm.models.objects import AddressCreateModel

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
address_dict = {
    "name": "web-server",
    "description": "Primary web server",
    "ip_netmask": "192.168.1.100/32",
    "folder": "Texas",
    "tag": ["web", "production"]
}

response = client.address.create(address_dict)

# Using model directly
address_obj = AddressCreateModel(
    name="web-server",
    description="Primary web server",
    ip_netmask="192.168.1.100/32",
    folder="Texas",
    tag=["web", "production"]
)

payload = address_obj.model_dump(exclude_unset=True)
response = client.address.create(payload)
```

### Creating an FQDN Address

```python
# Using dictionary
fqdn_dict = {
    "name": "example-domain",
    "description": "Example domain address",
    "fqdn": "www.example.com",
    "folder": "Texas",
    "tag": ["web", "domain"]
}

response = client.address.create(fqdn_dict)

# Using model directly
from scm.models.objects import AddressCreateModel

fqdn_address = AddressCreateModel(
    name="example-domain",
    description="Example domain address",
    fqdn="www.example.com",
    folder="Texas",
    tag=["web", "domain"]
)

payload = fqdn_address.model_dump(exclude_unset=True)
response = client.address.create(payload)
```

### Updating an Address

```python
# Fetch existing address
existing = client.address.fetch(name="web-server", folder="Texas")

# Modify attributes using dot notation
existing.name = "web-server-updated"
existing.description = "Updated web server"
existing.ip_netmask = "192.168.1.101/32"
existing.tag = ["web", "production", "updated"]

# Pass the modified object to update()
response = client.address.update(existing)
```
