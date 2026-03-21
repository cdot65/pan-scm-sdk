# External Dynamic Lists

The `ExternalDynamicLists` service manages External Dynamic Lists (EDLs) in Strata Cloud Manager, supporting IP, Domain, URL, IMSI, and IMEI list types with configurable update intervals.

## Class Overview

The `ExternalDynamicLists` class provides CRUD operations for EDL objects. It is accessed through the `client.external_dynamic_list` attribute on an initialized `Scm` instance.

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the ExternalDynamicLists service
edls = client.external_dynamic_list
```

### Key Attributes

| Attribute        | Type             | Required | Description                                |
|------------------|------------------|----------|--------------------------------------------|
| `name`           | `str`            | Yes      | Name of EDL (max 63 chars)                 |
| `id`             | `UUID`           | Yes*     | Unique identifier (*response only)         |
| `type`           | `TypeUnion`      | Yes      | EDL type configuration                     |
| `url`            | `str`            | Yes      | Source URL for EDL content                  |
| `description`    | `str`            | No       | Description (max 255 chars)                |
| `exception_list` | `List[str]`      | No       | List of exceptions                         |
| `auth`           | `AuthModel`      | No       | Authentication credentials                 |
| `recurring`      | `RecurringUnion`  | Yes      | Update schedule configuration              |
| `folder`         | `str`            | Yes**    | Folder location (**one container required) |
| `snippet`        | `str`            | Yes**    | Snippet location (**one container required)|
| `device`         | `str`            | Yes**    | Device location (**one container required) |

\* Exactly one of `folder`, `snippet`, or `device` is required.

## Methods

### List External Dynamic Lists

Retrieves a list of EDL objects with optional filtering.

```python
edls = client.external_dynamic_list.list(
    folder="Texas",
    types=["ip", "domain"]
)

for edl in edls:
    print(f"Name: {edl.name}")
```

### Fetch an External Dynamic List

Retrieves a single EDL by name and container.

```python
edl = client.external_dynamic_list.fetch(
    name="malicious-ips",
    folder="Texas"
)
print(f"Found EDL: {edl.name}")
```

### Create an External Dynamic List

Creates a new EDL object.

```python
ip_edl = client.external_dynamic_list.create({
    "name": "malicious-ips",
    "folder": "Texas",
    "type": {
        "ip": {
            "url": "https://threatfeeds.example.com/ips.txt",
            "description": "Known malicious IPs",
            "recurring": {"daily": {"at": "03"}},
            "auth": {
                "username": "user123",
                "password": "pass123"
            }
        }
    }
})
```

### Update an External Dynamic List

Updates an existing EDL object.

```python
existing = client.external_dynamic_list.fetch(
    name="malicious-ips",
    folder="Texas"
)
existing.type.ip.recurring = {"five_minute": {}}

updated = client.external_dynamic_list.update(existing)
```

### Delete an External Dynamic List

Deletes an EDL by ID.

```python
client.external_dynamic_list.delete("123e4567-e89b-12d3-a456-426655440000")
```

## Use Cases

### Creating Different EDL Types

Set up IP and domain-based EDLs for threat intelligence feeds.

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# IP-based EDL with daily updates
client.external_dynamic_list.create({
    "name": "malicious-ips",
    "folder": "Texas",
    "type": {
        "ip": {
            "url": "https://threatfeeds.example.com/ips.txt",
            "description": "Known malicious IPs",
            "recurring": {"daily": {"at": "03"}}
        }
    }
})

# Domain-based EDL with hourly updates
client.external_dynamic_list.create({
    "name": "blocked-domains",
    "folder": "Texas",
    "type": {
        "domain": {
            "url": "https://threatfeeds.example.com/domains.txt",
            "description": "Blocked domains list",
            "recurring": {"hourly": {}},
            "expand_domain": True
        }
    }
})
```

### Filtering EDLs

Use advanced filtering to find specific EDLs.

```python
# Exact match with exclusions
filtered = client.external_dynamic_list.list(
    folder="Texas",
    exact_match=True,
    exclude_folders=["All"],
    exclude_snippets=["default"]
)

for edl in filtered:
    print(f"EDL: {edl.name} in {edl.folder}")
```

## Error Handling

```python
from scm.client import Scm
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
    NameNotUniqueError,
    ObjectNotPresentError,
    ReferenceNotZeroError
)

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

try:
    new_edl = client.external_dynamic_list.create({
        "name": "test-edl",
        "folder": "Texas",
        "type": {
            "ip": {
                "url": "https://example.com/ips.txt",
                "description": "Test IP list",
                "recurring": {"daily": {"at": "03"}}
            }
        }
    })
except InvalidObjectError as e:
    print(f"Invalid EDL data: {e.message}")
except NameNotUniqueError as e:
    print(f"EDL name already exists: {e.message}")
except ObjectNotPresentError as e:
    print(f"EDL not found: {e.message}")
except ReferenceNotZeroError as e:
    print(f"EDL still in use: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing parameter: {e.message}")
```

## Related Topics

- [External Dynamic Lists Models](../../models/objects/external_dynamic_lists_models.md#Overview)
