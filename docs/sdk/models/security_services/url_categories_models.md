# URL Categories Models

## Overview

The URL Categories models provide a structured way to manage URL categories in Palo Alto Networks' Strata Cloud Manager.
These models support both URL List and Category Match types, which can be defined in folders, snippets, or devices. The
models handle validation of inputs and outputs when interacting with the SCM API.

## Attributes

| Attribute   | Type                      | Required | Default  | Description                                    |
|-------------|---------------------------|----------|----------|------------------------------------------------|
| name        | str                       | Yes      | None     | Name of the URL category                       |
| list        | List[str]                 | Yes      | None     | Lists of URL categories                        |
| description | str                       | No       | None     | Description of the URL category                |
| type        | URLCategoriesListTypeEnum | No       | URL List | Type of URL category (URL List/Category Match) |
| folder      | str                       | No*      | None     | Folder where category is defined               |
| snippet     | str                       | No*      | None     | Snippet where category is defined              |
| device      | str                       | No*      | None     | Device where category is defined               |
| id          | UUID                      | Yes**    | None     | UUID of the URL category (response only)       |

\* Exactly one container type (folder/snippet/device) must be provided
\** Only required for response model

## Exceptions

The URL Categories models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When multiple container types (folder/snippet/device) are specified
    - When no container type is specified for create operations
    - When container name pattern validation fails

## Model Validators

### Container Type Validation

For create operations, exactly one container type must be specified:

<div class="termy">

<!-- termynal -->

```python
from scm.models.security import URLCategoriesCreateModel

# This will raise a validation error
try:
    category = URLCategoriesCreateModel(
        name="blocked-sites",
        list=["example.com", "test.com"],
        folder="Shared",
        device="fw01"  # Can't specify both folder and device
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."
```

</div>

## Usage Examples

### Creating a URL List Category

<div class="termy">

<!-- termynal -->

```python
from scm.config.security import URLCategories

# Using dictionary
url_list_dict = {
    "name": "blocked-sites",
    "description": "Blocked websites",
    "list": ["example.com", "test.com"],
    "type": "URL List",
    "folder": "Shared",
}

url_categories = URLCategories(api_client)
response = url_categories.create(url_list_dict)

# Using model directly
from scm.models.security import URLCategoriesCreateModel

url_list = URLCategoriesCreateModel(
    name="blocked-sites",
    description="Blocked websites",
    list=["example.com", "test.com"],
    type="URL List",
    folder="Shared"
)

payload = url_list.model_dump(exclude_unset=True)
response = url_categories.create(payload)
```

</div>

### Creating a Category Match Category

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
category_match_dict = {
    "name": "social-media",
    "description": "Social media categories",
    "list": ["social-networking", "personal-sites-and-blogs"],
    "type": "Category Match",
    "folder": "Shared"
}

response = url_categories.create(category_match_dict)

# Using model directly
from scm.models.security import URLCategoriesCreateModel, URLCategoriesListTypeEnum

category_match = URLCategoriesCreateModel(
    name="social-media",
    description="Social media categories",
    list=["social-networking", "personal-sites-and-blogs"],
    type=URLCategoriesListTypeEnum.category_match,
    folder="Shared"
)

payload = category_match.model_dump(exclude_unset=True)
response = url_categories.create(payload)
```

</div>

### Updating a URL Category

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
update_dict = {
    "id": "123e4567-e89b-12d3-a456-426655440000",
    "name": "blocked-sites-updated",
    "description": "Updated blocked websites",
    "list": ["example.com", "test.com", "blocked.com"],
}

response = url_categories.update(update_dict)

# Using model directly
from scm.models.security import URLCategoriesUpdateModel

update = URLCategoriesUpdateModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="blocked-sites-updated",
    description="Updated blocked websites",
    list=["example.com", "test.com", "blocked.com"]
)

payload = update.model_dump(exclude_unset=True)
response = url_categories.update(payload)
```

</div>