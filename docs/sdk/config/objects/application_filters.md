# Application Filters

The `ApplicationFilters` service manages application filter definitions in Strata Cloud Manager, enabling you to organize and filter applications based on categories, risk levels, and security behaviors.

## Class Overview

The `ApplicationFilters` class provides CRUD operations for application filter objects. It is accessed through the `client.application_filter` attribute on an initialized `Scm` instance.

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the ApplicationFilters service
app_filters = client.application_filter
```

### Key Attributes

| Attribute                   | Type        | Required | Description                                |
|-----------------------------|-------------|----------|--------------------------------------------|
| `name`                      | `str`       | Yes      | Name of filter (max 31 chars)              |
| `id`                        | `UUID`      | Yes*     | Unique identifier (*response only)         |
| `category`                  | `List[str]` | No       | List of application categories             |
| `sub_category`              | `List[str]` | No       | List of application subcategories          |
| `technology`                | `List[str]` | No       | List of application technologies           |
| `risk`                      | `List[int]` | No       | List of risk levels (1-5)                  |
| `evasive`                   | `bool`      | No       | Filter evasive applications                |
| `used_by_malware`           | `bool`      | No       | Filter malware-associated apps             |
| `transfers_files`           | `bool`      | No       | Filter file-transferring apps              |
| `has_known_vulnerabilities` | `bool`      | No       | Filter apps with vulnerabilities           |
| `tunnels_other_apps`        | `bool`      | No       | Filter tunneling applications              |
| `prone_to_misuse`           | `bool`      | No       | Filter misuse-prone applications           |
| `pervasive`                 | `bool`      | No       | Filter pervasive applications              |
| `is_saas`                   | `bool`      | No       | Filter SaaS applications                   |
| `new_appid`                 | `bool`      | No       | Filter new applications                    |
| `excessive_bandwidth_use`   | `bool`      | No       | Filter apps using excessive bandwidth      |
| `saas_risk`                 | `List[str]` | No       | Filter by SaaS risk levels                 |
| `saas_certifications`       | `List[str]` | No       | Filter by SaaS certifications              |
| `exclude`                   | `List[str]` | No       | List of applications to exclude            |
| `tag`                       | `List[str]` | No       | Tags associated with the filter            |
| `folder`                    | `str`       | Yes**    | Folder location (**one container required) |
| `snippet`                   | `str`       | Yes**    | Snippet location (**one container required)|

\* Exactly one of `folder`, `snippet`, or `device` is required.

## Methods

### List Application Filters

Retrieves a list of application filter objects with optional filtering.

```python
filters = client.application_filter.list(
    folder="Texas",
    category=["business-systems"],
    risk=[4, 5]
)

for f in filters:
    print(f"Name: {f.name}, Categories: {f.category}, Risk: {f.risk}")
```

### Fetch an Application Filter

Retrieves a single application filter by name and container.

```python
filter_obj = client.application_filter.fetch(
    name="high-risk-apps",
    folder="Texas"
)
print(f"Found filter: {filter_obj.name}")
```

### Create an Application Filter

Creates a new application filter definition.

```python
new_filter = client.application_filter.create({
    "name": "high-risk-apps",
    "category": ["business-systems", "collaboration"],
    "risk": [4, 5],
    "folder": "Texas",
    "has_known_vulnerabilities": True,
    "used_by_malware": True
})
```

### Update an Application Filter

Updates an existing application filter.

```python
existing = client.application_filter.fetch(name="high-risk-apps", folder="Texas")
existing.risk = [3, 4, 5]
existing.prone_to_misuse = True

updated = client.application_filter.update(existing)
```

### Delete an Application Filter

Deletes an application filter by ID.

```python
client.application_filter.delete("123e4567-e89b-12d3-a456-426655440000")
```

## Use Cases

### Creating Security-Focused Filters

Define filters targeting applications with specific security characteristics.

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Filter for high-risk vulnerable applications
client.application_filter.create({
    "name": "vulnerable-high-risk",
    "risk": [4, 5],
    "folder": "Texas",
    "has_known_vulnerabilities": True,
    "used_by_malware": True
})

# Filter for SaaS applications
client.application_filter.create({
    "name": "saas-apps",
    "folder": "Texas",
    "is_saas": True,
    "saas_risk": ["high", "medium"],
    "saas_certifications": ["soc2", "iso27001"]
})
```

### Advanced List Filtering

Use exact match and exclusions to narrow results.

```python
# Only filters defined exactly in 'Texas'
exact_filters = client.application_filter.list(
    folder="Texas",
    exact_match=True
)

# Combine exact match with exclusions
combined = client.application_filter.list(
    folder="Texas",
    exact_match=True,
    exclude_folders=["All"],
    exclude_snippets=["default"]
)

for f in combined:
    print(f"Filter: {f.name} in {f.folder}")
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
    new_filter = client.application_filter.create({
        "name": "test-filter",
        "category": ["business-systems"],
        "risk": [4, 5],
        "folder": "Texas",
        "has_known_vulnerabilities": True
    })
except InvalidObjectError as e:
    print(f"Invalid filter data: {e.message}")
except NameNotUniqueError as e:
    print(f"Filter name already exists: {e.message}")
except ObjectNotPresentError as e:
    print(f"Filter not found: {e.message}")
except ReferenceNotZeroError as e:
    print(f"Filter still in use: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing parameter: {e.message}")
```

## Related Topics

- [Application Filters Models](../../models/objects/application_filters_models.md#Overview)
- [Application](application.md)
- [Application Group](application_group.md)
