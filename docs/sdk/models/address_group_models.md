# Address Group Models

This section covers the data models associated with the `AddressGroup` configuration object.

---

## AddressGroupRequestModel

Used when creating or updating an address group.

### Attributes

- `name` (str): **Required.** The name of the address group.
- `description` (Optional[str]): A description of the address group.
- `tag` (Optional[List[str]]): Tags associated with the address group.
- **Group Type Fields** (Exactly one must be provided):
    - `static` (Optional[List[str]]): List of address names for static groups.
    - `dynamic` (Optional[DynamicFilter]): Dynamic filter for dynamic groups.
- **Container Type Fields** (Exactly one must be provided):
    - `folder` (Optional[str]): The folder where the group is defined.
    - `snippet` (Optional[str]): The snippet where the group is defined.
    - `device` (Optional[str]): The device where the group is defined.

### DynamicFilter Model

- `filter` (str): **Required.** Tag-based filter defining group membership.

### Example (Static Group)

```python
address_group_request = AddressGroupRequestModel(
    name="example-group",
    description="Test address group",
    static=["test-address"],
    folder="Prisma Access",
)
```

### Example (Dynamic Group)

```python
address_group_request = AddressGroupRequestModel(
    name="dynamic-group",
    description="Dynamic address group",
    dynamic=DynamicFilter(filter="'tag1' or 'tag2'"),
    folder="Prisma Access",
)
```

---

## AddressGroupResponseModel

Used when parsing address groups retrieved from the API.

### Attributes

- `id` (str): The UUID of the address group.
- `name` (str): The name of the address group.
- `description` (Optional[str]): A description of the address group.
- `tag` (Optional[List[str]]): Tags associated with the address group.
- **Group Type Fields**:
    - `static` (Optional[List[str]]): List of address names for static groups.
    - `dynamic` (Optional[DynamicFilter]): Dynamic filter for dynamic groups.
- **Container Type Fields**:
    - `folder` (Optional[str]): The folder where the group is defined.
    - `snippet` (Optional[str]): The snippet where the group is defined.
    - `device` (Optional[str]): The device where the group is defined.

### Example

```python
address_group_response = AddressGroupResponseModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="example-group",
    static=["test-address"],
    description="Test address group",
    folder="Prisma Access",
)
```
