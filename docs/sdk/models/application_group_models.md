# application Group Models

This section covers the data models associated with the `applicationGroup` configuration object.

---

## ApplicationGroupRequestModel

Used when creating or updating an application object.

### Attributes

- `name` (str): **Required.** The name of the application object.
- `members` (List[str]): Members of Application objects associated with the application object.
- **Container Type Fields** (Exactly one must be provided):
    - `folder` (Optional[str]): The folder where the application group is defined.
    - `snippet` (Optional[str]): The snippet where the application group is defined.
    - `device` (Optional[str]): The device where the application group is defined.

### Example

```python
application_group_request = ApplicationGroupRequestModel(
    name="test-application",
    folder="Prisma Access",
    members=["test1", "test2"]
)
```

---

## ApplicationGroupResponseModel

Used when parsing application objects retrieved from the API.

### Attributes

- `id` (str): The UUID of the application object.
- `name` (str): **Required.** The name of the application object.
- `members` (List[str]): Members of Application objects associated with the application object.
- **Container Type Fields** (Exactly one must be provided):
    - `folder` (Optional[str]): The folder where the application group is defined.
    - `snippet` (Optional[str]): The snippet where the application group is defined.
    - `device` (Optional[str]): The device where the application group is defined.

### Example

```python
application_response = ApplicationGroupResponseModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="test-application",
    folder="Prisma Access",
    members=["test1", "test2"]
)
```
