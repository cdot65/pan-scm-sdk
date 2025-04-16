# Tag Models

## Overview {#Overview}

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

\* Exactly one container type (folder/snippet/device) must be provided for create operations
\** Only required for response model

## Exceptions

The Tag models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When multiple container types (folder/snippet/device) are specified for create operations
    - When no container type is specified for create operations
    - When an invalid color name is provided
    - When name pattern validation fails
    - When container field pattern validation fails
    - When field length limits are exceeded

## Model Validators

### Container Type Validation

For create operations, exactly one container type must be specified:

```python
# This will raise a validation error
from scm.models.objects import TagCreateModel

# Error: multiple containers specified
try:
    tag = TagCreateModel(
        name="invalid-tag",
        folder="Texas",
        device="fw01"  # Can't specify both folder and device
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."
```

### Color Validation

Colors must be one of the predefined values:

```python
# This will raise a validation error
try:
    tag = TagCreateModel(
        name="invalid-tag",
        folder="Texas",
        color="Invalid Color"  # Must be a valid color name
    )
except ValueError as e:
    print(e)  # "Color must be one of: Azure Blue, Black, Blue, ..."
```

### Name Validation

Tag names must match the required pattern:

```python
# This will raise a validation error
try:
    tag = TagCreateModel(
        name="invalid@tag!",  # Contains invalid characters
        folder="Texas",
        color="Red"
    )
except ValueError as e:
    print(e)  # "String should match pattern '^[a-zA-Z0-9_ \\.-\\[\\]\\-\\&\\(\\)]+$'"
```

## Usage Examples

### Creating a Basic Tag

```python
# Using dictionary
from scm.config.objects import Tag

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

tag_model = TagCreateModel(
    name="production",
    color="Red",
    comments="Production environment resources",
    folder="Texas"
)

payload = tag_model.model_dump(exclude_unset=True)
response = tag.create(payload)
```

### Creating Tags with Different Colors

```python
# Create multiple tags with different colors
tag_models = [
    TagCreateModel(
        name="development",
        color="Green",
        comments="Development environment resources",
        folder="Texas"
    ),
    TagCreateModel(
        name="staging",
        color="Yellow",
        comments="Staging environment resources",
        folder="Texas"
    ),
    TagCreateModel(
        name="testing",
        color="Blue",
        comments="Testing environment resources",
        folder="Texas"
    )
]

# Create each tag
for tag_model in tag_models:
    payload = tag_model.model_dump(exclude_unset=True)
    response = tag.create(payload)
    print(f"Created tag: {response.name} with color: {response.color}")
```

### Creating a Tag in a Snippet

```python
# Create a tag in a snippet instead of a folder
snippet_tag = TagCreateModel(
    name="shared-tag",
    color="Orange",
    comments="Shared across multiple folders",
    snippet="Common"  # Using snippet instead of folder
)

payload = snippet_tag.model_dump(exclude_unset=True)
response = tag.create(payload)
print(f"Created tag in snippet: {response.name}")
```

### Updating a Tag

```python
# Using dictionary
from scm.config.objects import Tag

update_dict = {
    "id": "123e4567-e89b-12d3-a456-426655440000",
    "name": "prod-updated",
    "color": "Blue",
    "comments": "Updated production tag"
}

tag = Tag(api_client)
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

### Retrieving Tags

```python
# Get tag by ID
tag_id = "123e4567-e89b-12d3-a456-426655440000"
tag_response = tag.get(tag_id)
print(f"Retrieved tag: {tag_response.name}")

# List tags with filters
tag_list = tag.list(folder="Texas", color="Red")
print(f"Found {len(tag_list)} red tags")

# Filter tags by name pattern
filtered_tags = tag.list(folder="Texas", name="prod")
for t in filtered_tags:
    print(f"Tag: {t.name}, Color: {t.color}")
```

### Deleting Tags

```python
# Delete tag by ID
tag_id = "123e4567-e89b-12d3-a456-426655440000"
tag.delete(tag_id)
print(f"Deleted tag with ID: {tag_id}")
```
