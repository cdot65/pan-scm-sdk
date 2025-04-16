# Snippet Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Snippet Model Attributes](#snippet-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating Snippets](#creating-snippets)
    - [Retrieving Snippets](#retrieving-snippets)
    - [Updating Snippets](#updating-snippets)
    - [Listing Snippets](#listing-snippets)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Deleting Snippets](#deleting-snippets)
7. [Folder Associations](#folder-associations)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Full Script Examples](#full-script-examples)
11. [Related Models](#related-models)

## Overview

The `Snippet` class provides functionality to manage snippet objects in Palo Alto Networks' Strata Cloud Manager. This
class inherits from `BaseObject` and provides methods for creating, retrieving, updating, and deleting snippet objects,
which are used to store reusable configuration elements.

## Core Methods

| Method                  | Description                           | Parameters                           | Return Type                      |
|-------------------------|---------------------------------------|--------------------------------------|----------------------------------|
| `create()`              | Creates a new snippet                 | `name: str`, etc.                    | `SnippetResponseModel`           |
| `get()`                 | Retrieves a snippet by ID             | `object_id: Union[str, UUID]`        | `SnippetResponseModel`           |
| `update()`              | Updates an existing snippet           | `snippet_id: Union[str, UUID]`, etc. | `SnippetResponseModel`           |
| `delete()`              | Deletes a snippet                     | `object_id: Union[str, UUID]`        | `None`                           |
| `list()`                | Lists snippets with filtering         | `name: str`, etc.                    | `List[SnippetResponseModel]`     |
| `fetch()`               | Gets a snippet by its name            | `name: str`                          | `Optional[SnippetResponseModel]` |
| `associate_folder()`    | Associates a snippet with a folder    | `snippet_id`, `folder_id`            | `SnippetResponseModel`           |
| `disassociate_folder()` | Disassociates a snippet from a folder | `snippet_id`, `folder_id`            | `SnippetResponseModel`           |

## Snippet Model Attributes

| Attribute       | Type                | Required | Description                                     |
|-----------------|---------------------|----------|-------------------------------------------------|
| `name`          | str                 | Yes      | Name of the snippet                             |
| `id`            | UUID                | Yes*     | Unique identifier (*response only)              |
| `description`   | Optional[str]       | No       | Optional description of the snippet             |
| `labels`        | Optional[List[str]] | No       | Optional list of labels to apply to the snippet |
| `enable_prefix` | bool                | No       | Whether to enable prefix for this snippet       |

## Exceptions

| Exception               | HTTP Code | Description                                      |
|-------------------------|-----------|--------------------------------------------------|
| `InvalidObjectError`    | 400       | Invalid snippet data or format                   |
| `ObjectNotPresentError` | 404       | Requested snippet not found                      |
| `APIError`              | Various   | General API communication error                  |
| `NotImplementedError`   | 501       | Feature not yet implemented (folder associations)|
| `AuthenticationError`   | 401       | Authentication failed                            |
| `ServerError`           | 500       | Internal server error                            |

## Basic Configuration

The Snippet service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# Access the Snippet service directly through the client
snippets = client.snippet
```

### Traditional Service Instantiation (Legacy)

```python
from scm.client import Scm
from scm.config.setup import Snippet

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# Initialize Snippet object explicitly
snippets = Snippet(client)
```

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Creating Snippets

```python
# Create a basic snippet
snippet = client.snippet.create(
    name="Security Policy Snippet",
    description="Common security policy configurations"
)
print(f"Created snippet: {snippet.name} (ID: {snippet.id})")

# Create a snippet with all optional parameters
detailed_snippet = client.snippet.create(
    name="Network Config Snippet",
    description="Network configuration template",
    labels=["network", "template"],
    enable_prefix=True
)
print(f"Created detailed snippet: {detailed_snippet.name}")
```

### Retrieving Snippets

```python
# Get a snippet by ID
snippet_id = "12345678-1234-1234-1234-123456789012"
snippet = client.snippet.get(object_id=snippet_id)
print(f"Retrieved snippet: {snippet.name}")

# Fetch a snippet by name
snippet_by_name = client.snippet.fetch(name="Security Policy Snippet")
if snippet_by_name:
    print(f"Found snippet with ID: {snippet_by_name.id}")
else:
    print("Snippet not found")
```

### Updating Snippets

```python
# Update a snippet
updated_snippet = client.snippet.update(
    snippet_id="12345678-1234-1234-1234-123456789012",
    name="Updated Security Policy",
    description="Updated security policy configurations",
    labels=["security", "updated"]
)
print(f"Updated snippet: {updated_snippet.name}")

# Update only specific fields
partial_update = client.snippet.update(
    snippet_id="12345678-1234-1234-1234-123456789012",
    description="New description only"
)
print(f"Partially updated snippet: {partial_update.name}")
```

### Listing Snippets

```python
# List all snippets
all_snippets = client.snippet.list()
print(f"Found {len(all_snippets)} snippets")

# List snippets with pagination
paginated_snippets = client.snippet.list(offset=10, limit=5)
print(f"Page of snippets: {len(paginated_snippets)}")
```

### Filtering Responses

```python
# Filter by name
filtered_snippets = client.snippet.list(name="Security")
print(f"Found {len(filtered_snippets)} snippets with 'Security' in the name")

# Exact match filter
exact_snippets = client.snippet.list(name="Network Config Snippet", exact_match=True)
print(f"Found {len(exact_snippets)} snippets with exact name match")

# Filter by type
type_snippets = client.snippet.list(type="predefined")
print(f"Found {len(type_snippets)} predefined snippets")
```

### Controlling Pagination with max_limit

```python
# Create a snippet client with custom max_limit
snippet_service = Snippet(client, max_limit=100)

# List snippets with pagination controls
snippets = snippet_service.list(limit=20, offset=40)
print(f"Retrieved {len(snippets)} snippets starting from offset 40")

# Be aware of the absolute maximum limit
print(f"Default max limit: {Snippet.DEFAULT_MAX_LIMIT}")
print(f"Absolute max limit: {Snippet.ABSOLUTE_MAX_LIMIT}")
```

### Deleting Snippets

```python
# Delete a snippet
client.snippet.delete(object_id="12345678-1234-1234-1234-123456789012")
print("Snippet deleted successfully")

try:
    # Verify deletion
    client.snippet.get(object_id="12345678-1234-1234-1234-123456789012")
except ObjectNotPresentError:
    print("Snippet was successfully deleted")
```

## Folder Associations

The API supports associating snippets with folders, although this functionality is currently in development:

```python
try:
    # Associate a snippet with a folder
    snippet_id = "12345678-1234-1234-1234-123456789012"
    folder_id = "87654321-4321-4321-4321-210987654321"
    
    updated_snippet = client.snippet.associate_folder(
        snippet_id=snippet_id,
        folder_id=folder_id
    )
    print(f"Associated snippet {snippet_id} with folder {folder_id}")
    
    # Disassociate a snippet from a folder
    result = client.snippet.disassociate_folder(
        snippet_id=snippet_id,
        folder_id=folder_id
    )
    print(f"Disassociated snippet from folder")
except NotImplementedError as e:
    print(f"Folder association not yet implemented: {e}")
```

## Error Handling

```python
try:
    # Try to retrieve a non-existent snippet
    snippet = client.snippet.get(object_id="nonexistent-id")
except ObjectNotPresentError:
    print("Snippet not found")
except APIError as e:
    print(f"API error occurred: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Best Practices

1. **Naming Conventions**
   - Use descriptive names for snippets
   - Establish consistent naming patterns

2. **Organization**
   - Use labels to categorize snippets by purpose or application
   - Group related snippets in folders

3. **Error Handling**
   - Always implement proper error handling
   - Catch specific exceptions for different error scenarios

4. **Validation**
   - Validate input data before sending to API
   - Check for naming conflicts before creating snippets

5. **Performance**
   - Use pagination for large result sets
   - Apply appropriate filters to limit results

## Full Script Examples

### Complete Snippet Management Example

```python
from scm.client import ScmClient
from scm.exceptions import ObjectNotPresentError, APIError

def manage_snippets():
    """Complete example of managing snippets in Strata Cloud Manager."""
    
    # Initialize the client
    client = ScmClient(
        client_id="your_client_id",
        client_secret="your_client_secret"
    )
    
    try:
        # Create a new snippet
        snippet = client.snippet.create(
            name="Security Policy Snippet",
            description="Common security policy configurations",
            labels=["security", "policy", "example"],
            enable_prefix=True
        )
        print(f"Created snippet: {snippet.name} (ID: {snippet.id})")
        
        # Get the snippet by ID
        retrieved_snippet = client.snippet.get(object_id=snippet.id)
        print(f"Retrieved snippet: {retrieved_snippet.name}")
        
        # Update the snippet
        updated_snippet = client.snippet.update(
            snippet_id=snippet.id,
            description="Updated security policy configurations",
            labels=["security", "policy", "updated"]
        )
        print(f"Updated snippet description: {updated_snippet.description}")
        
        # List all snippets with "Security" in the name
        filtered_snippets = client.snippet.list(name="Security")
        print(f"Found {len(filtered_snippets)} snippets matching 'Security'")
        
        # Delete the snippet
        client.snippet.delete(object_id=snippet.id)
        print("Snippet deleted successfully")
        
        # Verify deletion
        try:
            client.snippet.get(object_id=snippet.id)
            print("ERROR: Snippet was not deleted!")
        except ObjectNotPresentError:
            print("Verified: Snippet was successfully deleted")
    
    except ObjectNotPresentError as e:
        print(f"Snippet not found: {e}")
    except APIError as e:
        print(f"API error occurred: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    manage_snippets()
```

## Related Models

For detailed information about the models used with snippets, see [Snippet Models](../../models/setup/snippet_models.md).
