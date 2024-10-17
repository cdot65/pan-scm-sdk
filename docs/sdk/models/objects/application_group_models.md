# Application Group Models

This section covers the data models associated with the `ApplicationGroup` configuration object.

---

## ApplicationGroupRequestModel

Used when creating or updating an application group object.

### Attributes

- `name` (str): **Required.** The name of the application group object.
- `members` (Optional[List[str]]): Members of Application objects associated with the application group object.
- `dynamic` (Optional[Dict[str, str]]): Dynamic filter for the application group.
- **Container Type Fields** (Exactly one must be provided):
    - `folder` (Optional[str]): The folder where the application group is defined.
    - `snippet` (Optional[str]): The snippet where the application group is defined.
    - `device` (Optional[str]): The device where the application group is defined.

### Example 1: Static Application Group

<div class="termy">

<!-- termynal -->

```python
from scm.models.objects import ApplicationGroupRequestModel

static_group = ApplicationGroupRequestModel(
    name="static-app-group",
    folder="Prisma Access",
    members=["app1", "app2", "app3"]
)

print(f"Static group name: {static_group.name}")
print(f"Static group members: {static_group.members}")
```

</div>

### Example 2: Dynamic Application Group

<div class="termy">

<!-- termynal -->

```python
from scm.models.objects import ApplicationGroupRequestModel

dynamic_group = ApplicationGroupRequestModel(
    name="dynamic-app-group",
    folder="Prisma Access",
    dynamic={"filter": "'aws.ec2.tag.AppType' eq 'web'"}
)

print(f"Dynamic group name: {dynamic_group.name}")
print(f"Dynamic group filter: {dynamic_group.dynamic['filter']}")
```

</div>

### Example 3: Application Group in a Snippet

<div class="termy">

<!-- termynal -->

```python
from scm.models.objects import ApplicationGroupRequestModel

snippet_group = ApplicationGroupRequestModel(
    name="snippet-app-group",
    snippet="My Snippet",
    members=["app4", "app5"]
)

print(f"Snippet group name: {snippet_group.name}")
print(f"Snippet group container: {snippet_group.snippet}")
```

</div>

---

## ApplicationGroupResponseModel

Used when parsing application group objects retrieved from the API.

### Attributes

- `id` (str): The UUID of the application group object.
- `name` (str): The name of the application group object.
- `members` (Optional[List[str]]): Members of Application objects associated with the application group object.
- `dynamic` (Optional[Dict[str, str]]): Dynamic filter for the application group.
- **Container Type Fields** (Exactly one will be provided):
    - `folder` (Optional[str]): The folder where the application group is defined.
    - `snippet` (Optional[str]): The snippet where the application group is defined.
    - `device` (Optional[str]): The device where the application group is defined.

### Example 4: Parsing API Response

<div class="termy">

<!-- termynal -->

```python
from scm.models.objects import ApplicationGroupResponseModel

api_response = {
    "id": "123e4567-e89b-12d3-a456-426655440000",
    "name": "api-app-group",
    "folder": "Prisma Access",
    "members": ["app1", "app2"]
}

group_response = ApplicationGroupResponseModel(**api_response)

print(f"Group ID: {group_response.id}")
print(f"Group name: {group_response.name}")
print(f"Group members: {group_response.members}")
```

</div>

### Example 5: Dynamic Group Response

<div class="termy">

<!-- termynal -->

```python
from scm.models.objects import ApplicationGroupResponseModel

dynamic_response = {
    "id": "123e4567-e89b-12d3-a456-426655440001",
    "name": "dynamic-api-group",
    "folder": "Prisma Access",
    "dynamic": {"filter": "'aws.ec2.tag.Environment' eq 'production'"}
}

dynamic_group_response = ApplicationGroupResponseModel(**dynamic_response)

print(f"Dynamic Group ID: {dynamic_group_response.id}")
print(f"Dynamic Group name: {dynamic_group_response.name}")
print(f"Dynamic Group filter: {dynamic_group_response.dynamic['filter']}")
```

</div>

### Example 6: Device-based Group Response

<div class="termy">

<!-- termynal -->

```python
from scm.models.objects import ApplicationGroupResponseModel

device_response = {
    "id": "123e4567-e89b-12d3-a456-426655440002",
    "name": "device-app-group",
    "device": "firewall-01",
    "members": ["app3", "app4", "app5"]
}

device_group_response = ApplicationGroupResponseModel(**device_response)

print(f"Device Group ID: {device_group_response.id}")
print(f"Device Group name: {device_group_response.name}")
print(f"Device: {device_group_response.device}")
print(f"Device Group members: {device_group_response.members}")
```

</div>

---

## Full Example: Creating and Using Application Group Models

Here's a comprehensive example that demonstrates creating and using both ApplicationGroupRequestModel and
ApplicationGroupResponseModel:

<div class="termy">

<!-- termynal -->

```python
from scm.models.objects import ApplicationGroupRequestModel, ApplicationGroupResponseModel

# Create a new ApplicationGroupRequestModel
new_group_request = ApplicationGroupRequestModel(
    name="example-app-group",
    folder="Prisma Access",
    members=["app1", "app2", "app3"]
)

print("Application Group Request:")
print(f"Name: {new_group_request.name}")
print(f"Folder: {new_group_request.folder}")
print(f"Members: {new_group_request.members}")

# Simulate API response
api_response = {
    "id": "123e4567-e89b-12d3-a456-426655440000",
    "name": new_group_request.name,
    "folder": new_group_request.folder,
    "members": new_group_request.members
}

# Create ApplicationGroupResponseModel from API response
new_group_response = ApplicationGroupResponseModel(**api_response)

print("\nApplication Group Response:")
print(f"ID: {new_group_response.id}")
print(f"Name: {new_group_response.name}")
print(f"Folder: {new_group_response.folder}")
print(f"Members: {new_group_response.members}")

# Create a dynamic group request
dynamic_group_request = ApplicationGroupRequestModel(
    name="dynamic-web-apps",
    folder="Prisma Access",
    dynamic={"filter": "'aws.ec2.tag.AppType' eq 'web'"}
)

print("\nDynamic Application Group Request:")
print(f"Name: {dynamic_group_request.name}")
print(f"Folder: {dynamic_group_request.folder}")
print(f"Dynamic Filter: {dynamic_group_request.dynamic['filter']}")

# Simulate API response for dynamic group
dynamic_api_response = {
    "id": "123e4567-e89b-12d3-a456-426655440001",
    "name": dynamic_group_request.name,
    "folder": dynamic_group_request.folder,
    "dynamic": dynamic_group_request.dynamic
}

# Create ApplicationGroupResponseModel for dynamic group
dynamic_group_response = ApplicationGroupResponseModel(**dynamic_api_response)

print("\nDynamic Application Group Response:")
print(f"ID: {dynamic_group_response.id}")
print(f"Name: {dynamic_group_response.name}")
print(f"Folder: {dynamic_group_response.folder}")
print(f"Dynamic Filter: {dynamic_group_response.dynamic['filter']}")
```

</div>

This example showcases the creation of both static and dynamic application groups using the request model, and then
demonstrates how to work with the response model after receiving data from the API.
