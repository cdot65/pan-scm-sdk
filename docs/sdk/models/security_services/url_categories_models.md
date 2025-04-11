# URL Categories Models

## Overview

The URL Categories models provide a structured way to manage URL categories in Palo Alto Networks' Strata Cloud Manager.
These models support both URL List and Category Match types, which can be defined in folders, snippets, or devices. The
models handle validation of inputs and outputs when interacting with the SCM API.

## Models Overview

The module provides the following Pydantic models:

- `URLCategoriesListTypeEnum`: Enumeration of URL category types (URL List or Category Match)
- `URLCategoriesBaseModel`: Base model with fields common to all URL category operations
- `URLCategoriesCreateModel`: Model for creating new URL categories
- `URLCategoriesUpdateModel`: Model for updating existing URL categories
- `URLCategoriesResponseModel`: Response model for URL category operations

## URLCategoriesListTypeEnum

The `URLCategoriesListTypeEnum` defines the allowed types of URL categories:

```python
class URLCategoriesListTypeEnum(str, Enum):
    """Enumeration of allowed types within a list."""
    url_list = "URL List"
    category_match = "Category Match"
```

## URLCategoriesBaseModel

The `URLCategoriesBaseModel` contains fields common to all URL category CRUD operations.

| Attribute   | Type                      | Required | Default  | Description                                    |
|-------------|---------------------------|----------|----------|------------------------------------------------|
| name        | str                       | Yes      | -        | Name of the URL category                       |
| list        | List[str]                 | Yes      | []       | Lists of URLs or predefined categories         |
| description | Optional[str]             | No       | None     | Description of the URL category                |
| type        | URLCategoriesListTypeEnum | No       | URL List | Type of URL category (URL List/Category Match) |
| folder      | Optional[str]             | No*      | None     | Folder where category is defined               |
| snippet     | Optional[str]             | No*      | None     | Snippet where category is defined              |
| device      | Optional[str]             | No*      | None     | Device where category is defined               |

\* Exactly one container type (folder/snippet/device) must be provided for create operations

## URLCategoriesCreateModel

The `URLCategoriesCreateModel` extends the base model and includes validation to ensure that exactly one container type is provided.

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| *All attributes from URLCategoriesBaseModel* |  |  |  |  |

### Container Type Validation

When creating a URL category, exactly one of the following container types must be provided:
- `folder`: The folder in which the resource is defined
- `snippet`: The snippet in which the resource is defined
- `device`: The device in which the resource is defined

This validation is enforced by the `validate_container` model validator:

```python
@model_validator(mode="after")
def validate_container(self) -> "URLCategoriesCreateModel":
    container_fields = [
        "folder",
        "snippet",
        "device",
    ]
    provided_containers = [
        field for field in container_fields if getattr(self, field) is not None
    ]
    if len(provided_containers) != 1:
        raise ValueError(
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
        )
    return self
```

## URLCategoriesUpdateModel

The `URLCategoriesUpdateModel` extends the base model and adds the ID field required for updating existing URL categories.

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| id | Optional[UUID] | Yes | - | The UUID of the URL category |
| *All attributes from URLCategoriesBaseModel* |  |  |  |  |

## URLCategoriesResponseModel

The `URLCategoriesResponseModel` extends the base model and includes the ID field returned in API responses.

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| id | UUID | Yes | - | The UUID of the URL category |
| *All attributes from URLCategoriesBaseModel* |  |  |  |  |

## Usage Examples

### Creating a URL List Category

```python
from scm.models.security import URLCategoriesCreateModel, URLCategoriesListTypeEnum

# Create a URL list category
url_list = URLCategoriesCreateModel(
    name="blocked-sites",
    description="Blocked websites",
    list=["example.com", "test.com"],
    type=URLCategoriesListTypeEnum.url_list,
    folder="Shared"
)

# Or using string for type
url_list_alt = URLCategoriesCreateModel(
    name="blocked-sites",
    description="Blocked websites",
    list=["example.com", "test.com"],
    type="URL List",
    folder="Shared"
)
```

### Creating a Category Match Category

```python
from scm.models.security import URLCategoriesCreateModel, URLCategoriesListTypeEnum

# Create a category match category
category_match = URLCategoriesCreateModel(
    name="social-media",
    description="Social media categories",
    list=["social-networking", "personal-sites-and-blogs"],
    type=URLCategoriesListTypeEnum.category_match,
    folder="Shared"
)

# Or using string for type
category_match_alt = URLCategoriesCreateModel(
    name="social-media",
    description="Social media categories",
    list=["social-networking", "personal-sites-and-blogs"],
    type="Category Match",
    folder="Shared"
)
```

### Updating a URL Category

```python
from uuid import UUID
from scm.models.security import URLCategoriesUpdateModel

# Update an existing URL category
update = URLCategoriesUpdateModel(
    id=UUID("123e4567-e89b-12d3-a456-426655440000"),
    name="blocked-sites-updated",
    description="Updated blocked websites",
    list=["example.com", "test.com", "blocked.com"]
)
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
