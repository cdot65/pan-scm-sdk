# External Dynamic Lists Models

## Overview {#Overview}

The External Dynamic Lists models provide a structured way to manage external dynamic lists in Palo Alto Networks' Strata
Cloud Manager. These models support various types of dynamic lists including IP, domain, URL, IMSI, and IMEI lists, with
configurable update intervals and authentication options.

### Models

| Model                               | Purpose                                          |
|-------------------------------------|--------------------------------------------------|
| `ExternalDynamicListsBaseModel`     | Base model with common fields for all operations |
| `ExternalDynamicListsCreateModel`   | Model for creating new external dynamic lists    |
| `ExternalDynamicListsUpdateModel`   | Model for updating existing lists                |
| `ExternalDynamicListsResponseModel` | Model for API responses                          |

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

## Attributes

| Attribute           | Type           | Required | Default   | Description                                                                       |
|---------------------|----------------|----------|-----------|-----------------------------------------------------------------------------------|
| name                | str            | Yes      | None      | Name of the list. Max length: 63 chars. Must match pattern: ^[ a-zA-Z\d.\-_]+$    |
| type                | TypeUnion      | Yes*     | None      | Type of dynamic list (predefined_ip, predefined_url, ip, domain, url, imsi, imei) |
| folder              | str            | No**     | None      | Folder where list is defined. Max length: 64 chars                                |
| snippet             | str            | No**     | None      | Snippet where list is defined. Max length: 64 chars                               |
| device              | str            | No**     | None      | Device where list is defined. Max length: 64 chars                                |
| id                  | UUID           | Yes***   | None      | UUID of the list (response only)                                                  |
| description         | str            | No       | None      | Description of the list. Max length: 255 chars                                    |
| url                 | str            | Yes      | "http://" | URL for fetching list content                                                     |
| exception_list      | List[str]      | No       | None      | List of exceptions                                                                |
| certificate_profile | str            | No       | None      | Client certificate profile name                                                   |
| auth                | AuthModel      | No       | None      | Username/password authentication                                                  |
| recurring           | RecurringUnion | Yes      | None      | Update interval configuration                                                     |
| expand_domain       | bool           | No       | False     | Enable domain expansion (domain type only)                                        |

\* Required for non-predefined lists
\** Exactly one container type (folder/snippet/device) must be provided for create operations
\*** Required for response model when snippet is not "predefined"

## Exceptions

The External Dynamic Lists models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When no container type or multiple container types are specified for create operations
    - When ID is missing for non-predefined response models
    - When type is missing for non-predefined response models
    - When invalid recurring interval configuration is provided
    - When invalid URL format is provided
    - When name pattern validation fails

## Model Validators

### Container Type Validation

For create operations, exactly one container type must be specified:

```python
from scm.models.objects import ExternalDynamicListsCreateModel

# This will raise a validation error
try:
    edl = ExternalDynamicListsCreateModel(
        name="blocked-ips",
        folder="Shared",
        device="fw01",  # Can't specify both folder and device
        type={"ip": {
            "url": "http://example.com/blocked.txt",
            "recurring": {"hourly": {}}
        }}
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."
```

### Recurring Interval Validation

The models support various recurring update intervals:

```python
# Five minute interval
edl = ExternalDynamicListsCreateModel(
    name="blocked-ips",
    folder="Shared",
    type={"ip": {
        "url": "http://example.com/blocked.txt",
        "recurring": {"five_minute": {}}
    }}
)

# Daily at specific hour
edl = ExternalDynamicListsCreateModel(
    name="blocked-ips",
    folder="Shared",
    type={"ip": {
        "url": "http://example.com/blocked.txt",
        "recurring": {"daily": {"at": "23"}}
    }}
)

# Weekly on specific day and time
edl = ExternalDynamicListsCreateModel(
    name="blocked-ips",
    folder="Shared",
    type={"ip": {
        "url": "http://example.com/blocked.txt",
        "recurring": {"weekly": {"day_of_week": "monday", "at": "12"}}
    }}
)
```

## Usage Examples

### Creating an IP List

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
ip_list = {
    "name": "blocked-ips",
    "folder": "Shared",
    "type": {
        "ip": {
            "description": "Blocked IP addresses",
            "url": "http://example.com/blocked.txt",
            "auth": {
                "username": "user1",
                "password": "pass123"
            },
            "recurring": {"hourly": {}}
        }
    }
}

response = client.external_dynamic_list.create(ip_list)
```

### Creating a Domain List

```python
# Using dictionary
domain_list = {
    "name": "blocked-domains",
    "folder": "Shared",
    "type": {
        "domain": {
            "description": "Blocked domains",
            "url": "http://example.com/domains.txt",
            "auth": {
                "username": "user1",
                "password": "pass123"
            },
            "recurring": {"hourly": {}},
            "expand_domain": True
        }
    }
}

response = client.external_dynamic_list.create(domain_list)
```

### Updating a List

```python
# Fetch existing EDL
existing = client.external_dynamic_list.fetch(name="blocked-ips", folder="Shared")

# Modify attributes using dot notation
existing.type.ip.description = "Updated blocked IPs"
existing.type.ip.url = "http://example.com/blocked-new.txt"
existing.type.ip.recurring = {"daily": {"at": "12"}}

# Pass modified object to update()
updated = client.external_dynamic_list.update(existing)
```

## Best Practices

1. **List Management**
    - Use descriptive names for lists
    - Document list purposes in descriptions
    - Configure appropriate update intervals
    - Monitor list update status
    - Review exception lists regularly

2. **Security**
    - Use HTTPS URLs when possible
    - Implement proper authentication
    - Use client certificates when available
    - Regularly rotate credentials
    - Monitor list content changes

3. **Performance**
    - Choose appropriate update intervals
    - Monitor bandwidth usage
    - Use exception lists efficiently
    - Consider list size impacts
    - Monitor update job status

## Related Models

- AuthModel
- RecurringModels
- TypeModels

These related models are defined within the same file and described in the Attributes section above.
