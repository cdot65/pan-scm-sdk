# Tag Models

## Overview {#Overview}

The Tag models provide a structured way to manage tags in Palo Alto Networks' Strata Cloud Manager.
These models support defining tags with names, colors, and comments that can be applied to various objects
in the system. Tags can be defined in folders, snippets, or devices. The models handle validation of inputs
and outputs when interacting with the SCM API.

### Models

The module provides the following Pydantic models:

- `TagBaseModel`: Base model with fields common to all tag operations
- `TagCreateModel`: Model for creating new tags
- `TagUpdateModel`: Model for updating existing tags
- `TagResponseModel`: Response model for tag operations
- `Colors`: Enum class defining all valid color values

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

## Attributes

| Attribute | Type | Required | Default | Description                                                                                |
|-----------|------|----------|---------|--------------------------------------------------------------------------------------------|
| name      | str  | Yes      | None    | Name of the tag. Max length: 127 chars. Must match pattern: ^[a-zA-Z0-9_ \.-\[\]\-\&\(\)]+$ |
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

## Colors Enum

The `Colors` enum defines all valid color values that can be assigned to tags:

| Color Name | Value |
|------------|-------|
| AZURE_BLUE | "Azure Blue" |
| BLACK | "Black" |
| BLUE | "Blue" |
| BLUE_GRAY | "Blue Gray" |
| BLUE_VIOLET | "Blue Violet" |
| BROWN | "Brown" |
| BURNT_SIENNA | "Burnt Sienna" |
| CERULEAN_BLUE | "Cerulean Blue" |
| CHESTNUT | "Chestnut" |
| COBALT_BLUE | "Cobalt Blue" |
| COPPER | "Copper" |
| CYAN | "Cyan" |
| FOREST_GREEN | "Forest Green" |
| GOLD | "Gold" |
| GRAY | "Gray" |
| GREEN | "Green" |
| LAVENDER | "Lavender" |
| LIGHT_GRAY | "Light Gray" |
| LIGHT_GREEN | "Light Green" |
| LIME | "Lime" |
| MAGENTA | "Magenta" |
| MAHOGANY | "Mahogany" |
| MAROON | "Maroon" |
| MEDIUM_BLUE | "Medium Blue" |
| MEDIUM_ROSE | "Medium Rose" |
| MEDIUM_VIOLET | "Medium Violet" |
| MIDNIGHT_BLUE | "Midnight Blue" |
| OLIVE | "Olive" |
| ORANGE | "Orange" |
| ORCHID | "Orchid" |
| PEACH | "Peach" |
| PURPLE | "Purple" |
| RED | "Red" |
| RED_VIOLET | "Red Violet" |
| RED_ORANGE | "Red-Orange" |
| SALMON | "Salmon" |
| THISTLE | "Thistle" |
| TURQUOISE_BLUE | "Turquoise Blue" |
| VIOLET_BLUE | "Violet Blue" |
| YELLOW | "Yellow" |
| YELLOW_ORANGE | "Yellow-Orange" |

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
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
tag_dict = {
    "name": "production",
    "color": "Red",
    "comments": "Production environment resources",
    "folder": "Texas"
}

response = client.tag.create(tag_dict)
print(f"Created tag: {response.name} (ID: {response.id})")
```

### Creating Tags with Different Colors

```python
# Create multiple tags with different colors
tags_to_create = [
    {
        "name": "development",
        "color": "Green",
        "comments": "Development environment resources",
        "folder": "Texas"
    },
    {
        "name": "staging",
        "color": "Yellow",
        "comments": "Staging environment resources",
        "folder": "Texas"
    },
    {
        "name": "testing",
        "color": "Blue",
        "comments": "Testing environment resources",
        "folder": "Texas"
    }
]

# Create each tag
for tag_data in tags_to_create:
    response = client.tag.create(tag_data)
    print(f"Created tag: {response.name} with color: {response.color}")
```

### Creating a Tag in a Snippet

```python
# Create a tag in a snippet instead of a folder
snippet_tag_data = {
    "name": "shared-tag",
    "color": "Orange",
    "comments": "Shared across multiple folders",
    "snippet": "Common"  # Using snippet instead of folder
}

response = client.tag.create(snippet_tag_data)
print(f"Created tag in snippet: {response.name}")
```

### Updating a Tag

```python
# Fetch existing tag
existing = client.tag.fetch(name="production", folder="Texas")

# Modify attributes using dot notation
existing.color = "Blue"
existing.comments = "Updated production tag"

# Pass modified object to update()
updated = client.tag.update(existing)
print(f"Updated tag: {updated.name} with color: {updated.color}")
```

### Retrieving Tags

```python
# Fetch tag by name and container
tag = client.tag.fetch(name="production", folder="Texas")
print(f"Retrieved tag: {tag.name}, Color: {tag.color}")

# Get tag by ID
tag_id = "123e4567-e89b-12d3-a456-426655440000"
tag_response = client.tag.get(tag_id)
print(f"Retrieved tag: {tag_response.name}")

# List tags with color filter
tag_list = client.tag.list(folder="Texas", colors=["Red"])
print(f"Found {len(tag_list)} red tags")

# List all tags in a folder
all_tags = client.tag.list(folder="Texas")
for t in all_tags:
    print(f"Tag: {t.name}, Color: {t.color}")
```

### Deleting Tags

```python
# Delete tag by ID
tag_id = "123e4567-e89b-12d3-a456-426655440000"
client.tag.delete(tag_id)
print(f"Deleted tag with ID: {tag_id}")
```
