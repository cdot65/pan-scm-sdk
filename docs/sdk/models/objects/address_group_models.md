# Address Group Models

This section covers the data models associated with the `AddressGroup` configuration object.

---

## AddressGroupRequestModel

Used when creating or updating an address group.

### Attributes

- `name` (str): **Required.** The name of the address group. Max length: 63 characters.
- `description` (Optional[str]): A description of the address group. Max length: 1023 characters.
- `tag` (Optional[List[str]]): Tags associated with the address group. Max length: 64 characters per tag.
- **Group Type Fields** (Exactly one must be provided):
    - `static` (Optional[List[str]]): List of address names for static groups. Min length: 1, Max length: 255.
    - `dynamic` (Optional[DynamicFilter]): Dynamic filter for dynamic groups.
- **Container Type Fields** (Exactly one must be provided):
    - `folder` (Optional[str]): The folder where the group is defined. Max length: 64 characters.
    - `snippet` (Optional[str]): The snippet where the group is defined. Max length: 64 characters.
    - `device` (Optional[str]): The device where the group is defined. Max length: 64 characters.

### DynamicFilter Model

- `filter` (str): **Required.** Tag-based filter defining group membership. Max length: 1024 characters.

### Example 1 (Static Group)

<div class="termy">

<!-- termynal -->

```python
from scm.models.objects import AddressGroupRequestModel

address_group_request = AddressGroupRequestModel(
    name="example-static-group",
    description="Test static address group",
    static=["server1", "server2", "server3"],
    folder="Prisma Access",
    tag=["production", "web-servers"]
)

print(address_group_request.model_dump_json(indent=2))
```

</div>

### Example 2 (Dynamic Group)

<div class="termy">

<!-- termynal -->

```python
from scm.models.objects import AddressGroupRequestModel, DynamicFilter

address_group_request = AddressGroupRequestModel(
    name="example-dynamic-group",
    description="Test dynamic address group",
    dynamic=DynamicFilter(filter="'aws-tag' and 'production'"),
    folder="Prisma Access",
    tag=["dynamic", "aws"]
)

print(address_group_request.model_dump_json(indent=2))
```

</div>

### Example 3 (Static Group with Snippet)

<div class="termy">

<!-- termynal -->

```python
address_group_request = AddressGroupRequestModel(
    name="snippet-static-group",
    description="Static group in a snippet",
    static=["app1", "app2"],
    snippet="MySnippet",
    tag=["snippet", "apps"]
)

print(address_group_request.model_dump_json(indent=2))
```

</div>

---

## AddressGroupResponseModel

Used when parsing address groups retrieved from the API.

### Attributes

- `id` (Optional[str]): The UUID of the address group.
- `name` (str): The name of the address group. Max length: 63 characters.
- `description` (Optional[str]): A description of the address group. Max length: 1023 characters.
- `tag` (Optional[List[str]]): Tags associated with the address group. Max length: 64 characters per tag.
- **Group Type Fields**:
    - `static` (Optional[List[str]]): List of address names for static groups. Min length: 1, Max length: 255.
    - `dynamic` (Optional[DynamicFilter]): Dynamic filter for dynamic groups.
- **Container Type Fields**:
    - `folder` (Optional[str]): The folder where the group is defined. Max length: 64 characters.
    - `snippet` (Optional[str]): The snippet where the group is defined. Max length: 64 characters.
    - `device` (Optional[str]): The device where the group is defined. Max length: 64 characters.

### Example 4 (Static Group Response)

<div class="termy">

<!-- termynal -->

```python
from scm.models.objects import AddressGroupResponseModel

address_group_response = AddressGroupResponseModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="example-static-group",
    description="Test static address group",
    static=["server1", "server2", "server3"],
    folder="Prisma Access",
    tag=["production", "web-servers"]
)

print(address_group_response.model_dump_json(indent=2))
```

</div>

### Example 5 (Dynamic Group Response)

<div class="termy">

<!-- termynal -->

```python
from scm.models.objects import AddressGroupResponseModel, DynamicFilter

address_group_response = AddressGroupResponseModel(
    id="123e4567-e89b-12d3-a456-426655440001",
    name="example-dynamic-group",
    description="Test dynamic address group",
    dynamic=DynamicFilter(filter="'aws-tag' and 'production'"),
    folder="Prisma Access",
    tag=["dynamic", "aws"]
)

print(address_group_response.model_dump_json(indent=2))
```

</div>

### Example 6 (Static Group Response with Device)

<div class="termy">

<!-- termynal -->

```python
address_group_response = AddressGroupResponseModel(
    id="123e4567-e89b-12d3-a456-426655440002",
    name="device-static-group",
    description="Static group on a device",
    static=["internal1", "internal2"],
    device="firewall-01",
    tag=["device", "internal"]
)

print(address_group_response.model_dump_json(indent=2))
```

</div>

---

## Full Pydantic Model Usage Example

Here's a complete example demonstrating how to use the AddressGroup Pydantic models:

<div class="termy">

<!-- termynal -->

```python
from scm.models.objects import AddressGroupRequestModel, AddressGroupResponseModel, DynamicFilter

# Create a static address group request
static_group_request = AddressGroupRequestModel(
    name="web-servers",
    description="Web server address group",
    static=["web1.example.com", "web2.example.com"],
    folder="Prisma Access",
    tag=["production", "web"]
)

print("Static Group Request:")
print(static_group_request.model_dump_json(indent=2))
print("\n")

# Create a dynamic address group request
dynamic_group_request = AddressGroupRequestModel(
    name="dynamic-db-servers",
    description="Dynamic database server address group",
    dynamic=DynamicFilter(filter="'database-server' and 'production'"),
    folder="Prisma Access",
    tag=["production", "database"]
)

print("Dynamic Group Request:")
print(dynamic_group_request.model_dump_json(indent=2))
print("\n")

# Simulate API response for static group
static_group_response = AddressGroupResponseModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    **static_group_request.model_dump()
)

print("Static Group Response:")
print(static_group_response.model_dump_json(indent=2))
print("\n")

# Simulate API response for dynamic group
dynamic_group_response = AddressGroupResponseModel(
    id="123e4567-e89b-12d3-a456-426655440001",
    **dynamic_group_request.model_dump()
)

print("Dynamic Group Response:")
print(dynamic_group_response.model_dump_json(indent=2))
```

</div>

This example shows how to create both static and dynamic address group requests, and how the response models would look
after the groups are created.
