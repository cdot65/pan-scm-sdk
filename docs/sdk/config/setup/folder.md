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
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
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

| Exception                | HTTP Code | Description                                   |
|--------------------------|-----------|-----------------------------------------------|
| `InvalidObjectError`     | 400       | Invalid folder data or format                |
| `ObjectNotPresentError`  | 404       | Requested folder not found                   |
| `NameNotUniqueError`     | 409       | Folder name already exists in parent context |
| `APIError`               | Various   | General API communication error              |
| `AuthenticationError`    | 401       | Authentication failed                        |
| `ServerError`            | 500       | Internal server error                        |

## Basic Configuration

The Folder service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# Access the Folder service directly through the client
folders = client.folder
```

### Traditional Service Instantiation (Legacy)

```python
from scm.client import Scm
from scm.config.setup import Folder

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# Initialize Folder object explicitly
folders = Folder(client)
```

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

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

### Controlling Pagination with max_limit

```python
# Create a folder client with custom max_limit
folder_service = Folder(client, max_limit=100)

# List folders with pagination controls
folders = folder_service.list(limit=20, offset=40)
print(f"Retrieved {len(folders)} folders starting from offset 40")

# Be aware of the absolute maximum limit
print(f"Default max limit: {Folder.DEFAULT_MAX_LIMIT}")
print(f"Absolute max limit: {Folder.ABSOLUTE_MAX_LIMIT}")
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

    # Start building from the root
    return build_branch(root)

# Example usage:
folder_tree = build_folder_tree(client)
print(f"Folder tree: {folder_tree}")
```

### Deleting Folders

```python
# Delete a folder
folder_id = "12345678-1234-1234-1234-123456789012"
client.folder.delete(folder_id=folder_id)
print(f"Deleted folder with ID {folder_id}")

# Verify the folder has been deleted
try:
    client.folder.get(folder_id=folder_id)
    print("ERROR: Folder still exists!")
except ObjectNotPresentError:
    print("Folder successfully deleted")
```

## Error Handling

```python
from scm.exceptions import ObjectNotPresentError, NameNotUniqueError, APIError

try:
    # Try to create a folder with a duplicate name
    duplicate_folder = client.folder.create(
        name="Development",  # Assuming this folder already exists
        parent="Projects",
        description="Duplicate folder"
    )
except NameNotUniqueError:
    print("A folder with this name already exists in the specified parent")
except ObjectNotPresentError:
    print("Parent folder not found")
except APIError as e:
    print(f"API error occurred: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Best Practices

1. **Naming Conventions**
   - Use descriptive names for folders
   - Establish consistent hierarchical structure
   - Avoid excessively long names or special characters

2. **Organization**
   - Design your folder hierarchy carefully before implementation
   - Use descriptive labels to categorize folders
   - Keep hierarchy depth reasonable (avoid deep nesting)

3. **Error Handling**
   - Always implement proper error handling
   - Check for naming conflicts before creation
   - Verify parent folders exist

4. **Performance**
   - Use pagination for large folder structures
   - Cache folder structure for repetitive operations
   - Limit folder hierarchy depth for better performance

5. **Security**
   - Implement proper access controls
   - Follow principle of least privilege

## Full Script Examples

### Creating a Folder Hierarchy

```python
from scm.client import ScmClient
from scm.exceptions import APIError, NameNotUniqueError, ObjectNotPresentError

def create_folder_hierarchy():
    try:
        # Initialize client
        client = ScmClient(
            client_id="your_client_id",
            client_secret="your_client_secret"
        )

        # Create root folder
        try:
            root = client.folder.create(
                name="Organization",
                parent="",  # Empty for root folder
                description="Organization Root Folder",
                labels=["root", "organization"]
            )
            print(f"Created root folder: {root.name} (ID: {root.id})")
        except NameNotUniqueError:
            # If the folder already exists, fetch it
            root = client.folder.fetch(name="Organization")
            print(f"Using existing root folder: {root.name} (ID: {root.id})")

        # Create department folders
        departments = ["Engineering", "Marketing", "Operations", "Finance"]
        for dept in departments:
            try:
                dept_folder = client.folder.create(
                    name=dept,
                    parent="Organization",
                    description=f"{dept} Department",
                    labels=["department", dept.lower()]
                )
                print(f"Created department folder: {dept_folder.name}")

                # Create project folders for Engineering
                if dept == "Engineering":
                    projects = ["Cloud", "Security", "Mobile", "Web"]
                    for project in projects:
                        try:
                            project_folder = client.folder.create(
                                name=project,
                                parent="Engineering",
                                description=f"{project} Projects",
                                labels=["project", "engineering", project.lower()]
                            )
                            print(f"Created project folder: {project_folder.name}")
                        except NameNotUniqueError:
                            print(f"Project folder {project} already exists, skipping")
            except NameNotUniqueError:
                print(f"Department folder {dept} already exists, skipping")

        # List all folders
        all_folders = client.folder.list()
        print(f"Total folders created: {len(all_folders)}")

    except APIError as e:
        print(f"API error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    create_folder_hierarchy()
```

## Related Models

For detailed information about the models used with folders, see [Folder Models](../../models/setup/folder_models.md).
