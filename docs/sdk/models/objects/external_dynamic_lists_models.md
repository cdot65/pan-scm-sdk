# External Dynamic Lists Models

## Overview

The External Dynamic Lists models provide a structured way to manage external dynamic lists in Palo Alto Networks' Strata
Cloud Manager. These models support various types of dynamic lists including IP, domain, URL, IMSI, and IMEI lists, with
configurable update intervals and authentication options.

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

<div class="termy">

<!-- termynal -->
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

</div>

### Recurring Interval Validation

The models support various recurring update intervals:

<div class="termy">

<!-- termynal -->
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

</div>

## Usage Examples

### Creating an IP List

<div class="termy">

<!-- termynal -->
```python
from scm.config.objects import ExternalDynamicLists

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

edl = ExternalDynamicLists(api_client)
response = edl.create(ip_list)
```

</div>

### Creating a Domain List

<div class="termy">

<!-- termynal -->
```python
# Using model directly
from scm.models.objects import (
    ExternalDynamicListsCreateModel,
    DomainType,
    DomainModel,
    AuthModel,
    HourlyRecurringModel
)

domain_list = ExternalDynamicListsCreateModel(
    name="blocked-domains",
    folder="Shared",
    type=DomainType(
        domain=DomainModel(
            description="Blocked domains",
            url="http://example.com/domains.txt",
            auth=AuthModel(
                username="user1",
                password="pass123"
            ),
            recurring=HourlyRecurringModel(hourly={}),
            expand_domain=True
        )
    )
)

payload = domain_list.model_dump(exclude_unset=True)
response = edl.create(payload)
```

</div>

### Updating a List

<div class="termy">

<!-- termynal -->
```python
# Using dictionary
update_dict = {
    "id": "123e4567-e89b-12d3-a456-426655440000",
    "name": "blocked-ips-updated",
    "type": {
        "ip": {
            "description": "Updated blocked IPs",
            "url": "http://example.com/blocked-new.txt",
            "recurring": {"daily": {"at": "12"}}
        }
    }
}

response = edl.update(update_dict)
```

</div>

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

- [AuthModel](../../models/objects/external_dynamic_lists_models.md#Overview)
- [RecurringModels](../../models/objects/external_dynamic_lists_models.md#Overview)
- [TypeModels](../../models/objects/external_dynamic_lists_models.md#Overview)
