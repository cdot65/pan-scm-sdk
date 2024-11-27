# Tag Models

## Overview

The Tag models provide a structured way to manage tags in Palo Alto Networks' Strata Cloud Manager.
These models support defining tags with names, colors, and comments that can be applied to various objects
in the system. Tags can be defined in folders, snippets, or devices. The models handle validation of inputs
and outputs when interacting with the SCM API.

## Attributes

| Attribute | Type | Required | Default | Description                                                                                |
|-----------|------|----------|---------|--------------------------------------------------------------------------------------------|
| name      | str  | Yes      | None    | Name of the tag. Max length: 63 chars. Must match pattern: ^[a-zA-Z0-9_ \.-\[\]\-\&\(\)]+$ |
| color     | str  | No       | None    | Color associated with the tag. Must be one of the predefined colors                        |
| comments  | str  | No       | None    | Comments about the tag. Max length: 1023 chars                                             |
| folder    | str  | No*      | None    | Folder where tag is defined. Max length: 64 chars                                          |
| snippet   | str  | No*      | None    | Snippet where tag is defined. Max length: 64 chars                                         |
| device    | str  | No*      | None    | Device where tag is defined. Max length: 64 chars                                          |
| id        | UUID | Yes**    | None    | UUID of the tag (response only)                                                            |

\* Exactly one container type (folder/snippet/device) must be provided
\** Only required for response model

## Exceptions

The Tag models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When multiple container types (folder/snippet/device) are specified
    - When no container type is specified for create operations
    - When an invalid color name is provided
    - When name pattern validation fails
    - When container field pattern validation fails
    - When field length limits are exceeded

## Model Validators

### Container Type Validation

For create operations, exactly one container type must be specified:

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
from scm.config.objects import Tag

# Error: multiple containers specified
try:
    tag_dict = {
        "name": "invalid-tag",
        "folder": "Texas",
        "device": "fw01"  # Can't specify both folder and device
    }
    tag = Tag(api_client)
    response = tag.create(tag_dict)
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."

# Using model directly
from scm.models.objects import TagCreateModel

try:
    tag = TagCreateModel(
        name="invalid-tag",
        folder="Texas",
        device="fw01"
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."
```

</div>

### Color Validation

Colors must be one of the predefined values:

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
try:
    tag_dict = {
        "name": "invalid-tag",
        "folder": "Texas",
        "color": "Invalid Color"  # Must be a valid color name
    }
    response = tag.create(tag_dict)
except ValueError as e:
    print(e)  # "Color must be one of: Azure Blue, Black, Blue, ..."

# Using model directly
try:
    tag = TagCreateModel(
        name="invalid-tag",
        folder="Texas",
        color="Invalid Color"
    )
except ValueError as e:
    print(e)  # "Color must be one of: Azure Blue, Black, Blue, ..."
```

</div>

## Usage Examples

### Creating a Basic Tag

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
tag_dict = {
    "name": "production",
    "color": "Red",
    "comments": "Production environment resources",
    "folder": "Texas"
}

tag = Tag(api_client)
response = tag.create(tag_dict)

# Using model directly
from scm.models.objects import TagCreateModel

tag = TagCreateModel(
    name="production",
    color="Red",
    comments="Production environment resources",
    folder="Texas"
)

payload = tag.model_dump(exclude_unset=True)
response = tag.create(payload)
```

</div>

### Updating a Tag

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
update_dict = {
    "id": "123e4567-e89b-12d3-a456-426655440000",
    "name": "prod-updated",
    "color": "Blue",
    "comments": "Updated production tag"
}

response = tag.update(update_dict)

# Using model directly
from scm.models.objects import TagUpdateModel

update_tag = TagUpdateModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="prod-updated",
    color="Blue",
    comments="Updated production tag"
)

payload = update_tag.model_dump(exclude_unset=True)
response = tag.update(payload)
```

</div>