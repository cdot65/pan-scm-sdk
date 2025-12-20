# URL Categories Models

## Table of Contents

1. [Overview](#overview)
2. [Model Attributes](#model-attributes)
3. [Enum Types](#enum-types)
4. [Exceptions](#exceptions)
5. [Model Validators](#model-validators)
6. [Usage Examples](#usage-examples)

## Overview {#Overview}

The URL Categories models provide a structured way to manage URL categories in Palo Alto Networks' Strata Cloud Manager.
These models support both URL List and Category Match types, which can be defined in folders, snippets, or devices. The
models handle validation of inputs and outputs when interacting with the SCM API.

### Models

The module provides the following Pydantic models:

- `URLCategoriesBaseModel`: Base model with fields common to all URL category operations
- `URLCategoriesCreateModel`: Model for creating new URL categories
- `URLCategoriesUpdateModel`: Model for updating existing URL categories
- `URLCategoriesResponseModel`: Response model for URL category operations

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

## Model Attributes

### URLCategoriesBaseModel

| Attribute   | Type                      | Required | Default  | Description                                    |
|-------------|---------------------------|----------|----------|------------------------------------------------|
| name        | str                       | Yes      | None     | Name of the URL category                       |
| list        | List[str]                 | No       | []       | Lists of URLs or predefined categories         |
| description | str                       | No       | None     | Description of the URL category                |
| type        | URLCategoriesListTypeEnum | No       | URL List | Type of URL category (URL List/Category Match) |
| folder      | str                       | No**     | None     | Folder location. Max 64 chars                  |
| snippet     | str                       | No**     | None     | Snippet location. Max 64 chars                 |
| device      | str                       | No**     | None     | Device location. Max 64 chars                  |

\** Exactly one container (folder/snippet/device) must be provided for create operations

### URLCategoriesCreateModel

Inherits all fields from `URLCategoriesBaseModel` and enforces that **exactly one** of `folder`, `snippet`, or `device` is provided during creation.

### URLCategoriesUpdateModel

Extends `URLCategoriesBaseModel` by adding:

| Attribute | Type | Required | Default | Description                             |
|-----------|------|----------|---------|-----------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the category   |

### URLCategoriesResponseModel

Extends `URLCategoriesBaseModel` by adding:

| Attribute | Type | Required | Default | Description                             |
|-----------|------|----------|---------|-----------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the category   |

## Enum Types

### URLCategoriesListTypeEnum

Defines the allowed types of URL categories:

| Value            | Description                              |
|------------------|------------------------------------------|
| `URL List`       | List of specific URLs or domains         |
| `Category Match` | Match against predefined PAN-DB categories |

## Exceptions

The URL Categories models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When multiple container types (folder/snippet/device) are specified for create operations
    - When no container type is specified for create operations
    - When invalid type values are provided
    - When container field pattern validation fails
    - When field length limits are exceeded

## Model Validators

### Container Type Validation

For create operations, exactly one container type must be specified:

```python
from scm.models.security import URLCategoriesCreateModel

# Error: multiple containers specified
try:
    category = URLCategoriesCreateModel(
        name="blocked-sites",
        list=["example.com"],
        folder="Texas",
        device="fw01"  # Can't specify both folder and device
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."

# Error: no container specified
try:
    category = URLCategoriesCreateModel(
        name="blocked-sites",
        list=["example.com"]
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."
```

## Usage Examples

### Creating a URL List Category

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
url_list_config = {
    "name": "blocked-sites",
    "description": "Blocked websites",
    "list": ["example.com", "test.com"],
    "type": "URL List",
    "folder": "Texas"
}

response = client.url_categories.create(url_list_config)
print(f"Created category: {response.name}")
```

### Creating a Category Match Category

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
category_match_config = {
    "name": "social-media",
    "description": "Social media categories",
    "list": ["social-networking", "personal-sites-and-blogs"],
    "type": "Category Match",
    "folder": "Texas"
}

response = client.url_categories.create(category_match_config)
print(f"Created category match: {response.name}")
```

### Updating a URL Category

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Fetch existing category
existing = client.url_categories.fetch(name="blocked-sites", folder="Texas")

# Modify attributes using dot notation
existing.description = "Updated blocked websites list"
existing.list.extend(["newsite.com", "anothersite.com"])

# Pass modified object to update()
updated = client.url_categories.update(existing)
print(f"Updated category: {updated.name}")
```

## Best Practices

### URL List Configuration
- For URL List type, include fully qualified domain names (without http:// or https:// prefixes)
- Use wildcards (*) to match subdomains (e.g., *.example.com)
- Keep lists organized and maintainable by limiting the number of entries

### Category Match Configuration
- Use predefined PAN-DB categories for Category Match type
- Combine related categories to simplify policy management
- Verify that category names exactly match PAN-DB category names

### Container Management
- Always specify exactly one container type (folder, snippet, or device)
- Use consistent naming conventions for URL categories
- Organize categories logically by function or security policy
