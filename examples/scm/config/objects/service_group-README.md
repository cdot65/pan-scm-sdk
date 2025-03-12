# Service Group Example Notes

## Important Considerations

When working with service groups in Strata Cloud Manager, it's important to understand that:

1. **Service group members must reference existing service objects or other service groups** - You cannot use generic names like "HTTP" or "HTTPS" directly. These must be actual service object names that exist in your SCM environment.

2. **Tags must reference existing tag objects** - Similar to service members, tags must reference actual tag objects that exist in your SCM environment. You cannot use arbitrary tag strings like "Web" or "Hierarchical".

3. **Creating service groups requires preparation** - Before creating service groups, you should:
   - First create service objects that you'll reference in the members list
   - Create tag objects that you'll use in the tag list
   - Reference existing service objects and tags already in your environment
   - Use the Service API and Tag API to fetch existing objects and use their names

4. **Error handling** - The API will return a "not a valid reference" error when you try to use names that don't exist as actual objects in your environment, for either services or tags.

## Best Practices

1. **Query existing objects first** - Before creating service groups, query both the service objects and tag objects in your environment to get valid references.

2. **Create necessary objects** - Create any needed service objects and tag objects before creating service groups that reference them.

3. **Use proper error handling** - Implement proper error handling to catch "invalid reference" errors and provide useful feedback.

4. **Documentation** - Document clearly which services and tags need to exist in your environment for service groups to work properly.

## Example Workflow

The recommended workflow for creating service groups is:

1. Initialize service and tag managers to work with these objects:
   ```python
   from scm.config.objects import Service, Tag
   service_manager = Service(client)
   tag_manager = Tag(client)
   ```

2. List existing services and tags to find valid references:
   ```python
   existing_services = service_manager.list(folder="YOUR_FOLDER")
   service_names = [service.name for service in existing_services]

   existing_tags = tag_manager.list(folder="YOUR_FOLDER")
   tag_names = [tag.name for tag in existing_tags]
   ```

3. Create service group with valid service and tag references:
   ```python
   from scm.config.objects import ServiceGroup
   service_group_manager = ServiceGroup(client)

   # Use real service and tag names from your environment
   group_config = {
       "name": "my-service-group",
       "description": "Group of web services",
       "folder": "YOUR_FOLDER",
       "members": service_names[:2],  # Use first two services
       "tag": tag_names[:1]  # Use first tag
   }

   new_group = service_group_manager.create(group_config)
   ```

By following these guidelines, you'll avoid the common pitfalls:
1. Using predefined service names that don't exist as objects in your SCM environment
2. Using arbitrary tag strings that don't reference existing tag objects

## Creating Service Objects First

If you need to create service objects before creating service groups, here's an example:

```python
from scm.config.objects import Service

service_manager = Service(client)

# Create a TCP service
service_config = {
    "name": "custom-http",
    "folder": "YOUR_FOLDER",
    "protocol": {
        "tcp": {
            "port": "8080"
        }
    }
}

service = service_manager.create(service_config)
```

## Creating Tag Objects First

If you need to create tag objects before creating service groups, here's an example:

```python
from scm.config.objects import Tag

tag_manager = Tag(client)

# Create a tag
tag_config = {
    "name": "Automation",
    "folder": "YOUR_FOLDER",
    "color": "Blue"
}

tag = tag_manager.create(tag_config)
```

## Hierarchical Relationships and Deletion Order

When working with hierarchical service groups (groups that reference other groups), it's important to understand the implications for deletion operations:

1. **Reference constraints** - You cannot delete a service group that is referenced by another service group. Attempting to do so will result in a "Reference Not Zero" error.

2. **Deletion order** - When deleting service groups that have hierarchical relationships, you must delete them in the correct order:
   - First delete the groups that reference other groups (parent groups)
   - Then delete the groups that are referenced (child groups)

3. **Error handling** - The example script demonstrates how to handle these dependencies:
   - Detect hierarchical relationships between groups
   - Sort groups for deletion in the proper order
   - Handle errors if deletion fails due to unforeseen dependencies

### Example of Hierarchical Deletion

```python
# First, identify any hierarchical relationships between groups
hierarchical_relationships = {}

# Analyze each group to find which groups reference others
for group_id in group_ids:
    group = service_groups.get(group_id)

    # Check if this group references other groups in our list
    for member in group.members:
        for other_id in group_ids:
            other_group = service_groups.get(other_id)
            if member == other_group.name:
                # This group references another group
                if group_id not in hierarchical_relationships:
                    hierarchical_relationships[group_id] = []
                hierarchical_relationships[group_id].append(other_id)

# Sort group_ids so that groups referencing other groups are deleted first
sorted_ids = []
remaining_ids = group_ids.copy()

# First add all groups that reference other groups
for group_id in hierarchical_relationships.keys():
    if group_id in remaining_ids:
        sorted_ids.append(group_id)
        remaining_ids.remove(group_id)

# Then add all remaining groups
sorted_ids.extend(remaining_ids)

# Delete groups in the sorted order
for group_id in sorted_ids:
    service_groups.delete(group_id)
```
