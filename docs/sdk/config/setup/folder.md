# Folder Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Folder Model Attributes](#folder-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating Folder Objects](#creating-folder-objects)
    - [Retrieving Folders](#retrieving-folders)
    - [Updating Folders](#updating-folders)
    - [Listing Folders](#listing-folders)
    - [Filtering Responses](#filtering-responses)
    - [Working with Folder Hierarchies](#working-with-folder-hierarchies)
    - [Deleting Folders](#deleting-folders)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)
9. [Full Script Examples](#full-script-examples)
10. [Related Models](#related-models)

## Overview

The `Folder` class provides functionality to manage folder objects in Palo Alto Networks' Strata Cloud Manager. This
class inherits from `BaseObject` and provides methods for creating, retrieving, updating, and deleting folder objects,
which are used to organize resources in a hierarchical structure.

## Core Methods

| Method     | Description                  | Parameters                          | Return Type                     |
|------------|------------------------------|-------------------------------------|---------------------------------|
| `create()` | Creates a new folder         | `name: str`, `parent: str`, etc.    | `FolderResponseModel`           |
| `get()`    | Retrieves a folder by ID     | `folder_id: Union[str, UUID]`       | `FolderResponseModel`           |
| `update()` | Updates an existing folder   | `folder_id: Union[str, UUID]`, etc. | `FolderResponseModel`           |
| `delete()` | Deletes a folder             | `folder_id: Union[str, UUID]`       | `None`                          |
| `list()`   | Lists folders with filtering | `name: str`, `parent: str`, etc.    | `List[FolderResponseModel]`     |
| `fetch()`  | Gets a folder by its name    | `name: str`                         | `Optional[FolderResponseModel]` |

## Folder Model Attributes

| Attribute     | Type                | Required | Description                                                           |
|---------------|---------------------|----------|-----------------------------------------------------------------------|
| `name`        | str                 | Yes      | Name of the folder                                                    |
| `parent`      | str                 | Yes      | Name of the parent folder (not the ID). Empty string for root folders |
| `id`          | UUID                | Yes*     | Unique identifier (*response only)                                    |
| `description` | Optional[str]       | No       | Optional description of the folder                                    |
| `labels`      | Optional[List[str]] | No       | Optional list of labels to apply to the folder                        |
| `snippets`    | Optional[List[str]] | No       | Optional list of snippet IDs associated with the folder               |

## Exceptions

The Folder class can raise the following exceptions:

- `APIError`: Base class for all API-related errors
- `InvalidObjectError`: Raised when an invalid object or parameter is provided
- `ObjectNotPresentError`: Raised when a requested folder does not exist
- `NameNotUniqueError`: Raised when attempting to create a folder with a name that already exists

## Basic Configuration

```python
from scm.client import Scm
from scm.config.setup import Folder

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret"
)
```

## Usage Examples

### Creating Folder Objects

```python
# Create a root-level folder
root_folder = client.folder.create(
    name="Projects",
    parent="",  # Empty string for root-level folders
    description="All company projects"
)
print(f"Created root folder: {root_folder.name} (ID: {root_folder.id})")

# Create a child folder
child_folder = client.folder.create(
    name="Development",
    parent="Projects",  # Use the NAME of the parent folder, not its ID
    description="Development projects",
    labels=["development", "internal"]
)
print(f"Created child folder: {child_folder.name} under {child_folder.parent}")
```

### Retrieving Folders

```python
# Get a folder by ID
folder_id = "12345678-1234-1234-1234-123456789012"
folder = client.folder.get(folder_id=folder_id)
print(f"Retrieved folder: {folder.name}")

# Get a folder by name
folder_name = "Development"
folder = client.folder.fetch(name=folder_name)
if folder:
    print(f"Found folder: {folder.name} (ID: {folder.id})")
    print(f"Parent folder: {folder.parent}")
else:
    print(f"No folder found with name '{folder_name}'")
```

### Updating Folders

```python
# Update a folder
folder_id = "12345678-1234-1234-1234-123456789012"
updated_folder = client.folder.update(
    folder_id=folder_id,
    name="Development-Updated",  # New name
    description="Updated development projects folder",  # New description
    labels=["development", "internal", "updated"]  # Updated labels
)
print(f"Updated folder: {updated_folder.name}")
print(f"New description: {updated_folder.description}")
```

### Listing Folders

```python
# List all folders (up to max_limit)
all_folders = client.folder.list()
print(f"Found {len(all_folders)} folders")
for folder in all_folders:
    print(f"- {folder.name}: {folder.id}, parent: {folder.parent}")

# List folders with filtering by parent
parent_name = "Projects"
child_folders = client.folder.list(parent=parent_name)
print(f"Found {len(child_folders)} child folders under '{parent_name}'")
for folder in child_folders:
    print(f"- {folder.name}: {folder.id}")
```

### Filtering Responses

```python
# Filter folders by name (partial matching)
name_filter = "Dev"
matching_folders = client.folder.list(name=name_filter)
print(f"Found {len(matching_folders)} folders with '{name_filter}' in the name")

# Filter folders with exact name matching
exact_folders = client.folder.list(name="Development", exact_match=True)
print(f"Found {len(exact_folders)} folders with the exact name 'Development'")
```

### Working with Folder Hierarchies

```python
def build_folder_tree(client, root_name=""):
    """
    Build a hierarchical representation of the folder structure
    
    Args:
        client: The SCM client
        root_name: Name of the root folder (empty string for the absolute root)
        
    Returns:
        dict: A nested dictionary representing the folder tree
    """
    # Get all folders
    all_folders = client.folder.list()

    # Find the root folder or use the specified root
    if root_name:
        root_folders = [f for f in all_folders if f.name == root_name]
        if not root_folders:
            return {}
        root = root_folders[0]
    else:
        # Find folders with empty parent (top-level folders)
        root_folders = [f for f in all_folders if not f.parent]
        if not root_folders:
            return {}
        root = root_folders[0]

    # Build the tree recursively
    def build_branch(folder):
        children = [f for f in all_folders if f.parent == folder.name]
        branch = {
            "id": str(folder.id),
            "name": folder.name,
            "description": folder.description,
        }

        if children:
            branch["children"] = [build_branch(child) for child in children]

        return branch

    return build_branch(root)


# Example usage:
folder_tree = build_folder_tree(client)
import json

print(json.dumps(folder_tree, indent=2))
```

### Deleting Folders

```python
# Delete a folder by ID
folder_id = "12345678-1234-1234-1234-123456789012"
client.folder.delete(folder_id=folder_id)
print(f"Folder with ID {folder_id} has been deleted")
```

## Error Handling

```python
from scm.exceptions import APIError, ObjectNotPresentError, NameNotUniqueError

try:
    # Attempt to create a folder
    folder = client.folder.create(
        name="Development",
        parent="NonExistentParent"
    )
except NameNotUniqueError as e:
    print(f"A folder with this name already exists: {e}")
except ObjectNotPresentError as e:
    print(f"The parent folder does not exist: {e}")
except APIError as e:
    print(f"API Error: {e}")
```

## Best Practices

1. **Folder Naming and Organization**
    - Use consistent naming conventions for folders
    - Maintain a logical hierarchy for your resources
    - Avoid creating deeply nested folder structures (more than 5-6 levels)
    - Document your folder organization strategy

2. **Parent References**
    - Always use folder names (not UUIDs) for parent references
    - Verify parent folders exist before creating child folders
    - Be cautious when renaming parent folders as it affects child folder references

3. **Error Handling**
    - Implement comprehensive error handling for all operations
    - Handle specific exceptions before generic ones
    - Verify folder existence before performing operations on it

## Full Script Examples

### Creating a Complete Folder Hierarchy

```python
from scm.client import Scm
from scm.exceptions import APIError, NameNotUniqueError

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret"
)


def create_folder_hierarchy():
    try:
        # Create root folder
        try:
            root = client.folder.create(
                name="Organization",
                parent="",
                description="Organization root folder"
            )
            print(f"Created root folder: {root.name} (ID: {root.id})")
        except NameNotUniqueError:
            # Folder already exists, fetch it instead
            root = client.folder.fetch(name="Organization")
            print(f"Root folder already exists: {root.name} (ID: {root.id})")

        # Create department folders
        departments = ["Engineering", "Marketing", "Operations", "Sales"]

        for dept in departments:
            try:
                dept_folder = client.folder.create(
                    name=dept,
                    parent="Organization",
                    description=f"{dept} department folder",
                    labels=["department", dept.lower()]
                )
                print(f"Created department folder: {dept_folder.name} (ID: {dept_folder.id})")

                # Create sub-folders for Engineering department
                if dept == "Engineering":
                    teams = ["Frontend", "Backend", "DevOps", "QA"]
                    for team in teams:
                        try:
                            team_folder = client.folder.create(
                                name=team,
                                parent="Engineering",
                                description=f"{team} team folder",
                                labels=["team", team.lower(), "engineering"]
                            )
                            print(f"Created team folder: {team_folder.name} (ID: {team_folder.id})")
                        except NameNotUniqueError:
                            print(f"Team folder '{team}' already exists")

            except NameNotUniqueError:
                print(f"Department folder '{dept}' already exists")

        print("\nFolder hierarchy creation complete!")

    except APIError as e:
        print(f"Error creating folder hierarchy: {e}")


# Execute the function
create_folder_hierarchy()
```

## Related Models

- [FolderCreateModel](../models/setup/folder_models.md): Model for creating folder objects
- [FolderUpdateModel](../models/setup/folder_models.md): Model for updating folder objects
- [FolderResponseModel](../models/setup/folder_models.md): Model for folder responses from the API
