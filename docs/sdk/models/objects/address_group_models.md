# Address Group Models

## Overview {#Overview}

The Address Group models provide a structured way to manage address groups in Palo Alto Networks' Strata Cloud Manager.
These models support both static and dynamic address groups, which can be defined in folders, snippets, or devices. The
models handle validation of inputs and outputs when interacting with the SCM API.

## Attributes

| Attribute   | Type          | Required | Default | Description                                                                              |
|-------------|---------------|----------|---------|------------------------------------------------------------------------------------------|
| name        | str           | Yes      | None    | Name of the address group. Max length: 63 chars. Must match pattern: ^[a-zA-Z0-9_ \.-]+$ |
| description | str           | No       | None    | Description of the address group. Max length: 1023 chars                                 |
| tag         | List[str]     | No       | None    | List of tags. Each tag max length: 64 chars                                              |
| dynamic     | DynamicFilter | No*      | None    | Dynamic filter for group membership                                                      |
| static      | List[str]     | No*      | None    | List of static addresses. Min: 1, Max: 255                                               |
| folder      | str           | No**     | None    | Folder where group is defined. Max length: 64 chars                                      |
| snippet     | str           | No**     | None    | Snippet where group is defined. Max length: 64 chars                                     |
| device      | str           | No**     | None    | Device where group is defined. Max length: 64 chars                                      |
| id          | UUID          | Yes***   | None    | UUID of the address group (response only)                                                |

\* Either dynamic or static must be provided, but not both
\** Exactly one container type (folder/snippet/device) must be provided
\*** Only required for response model

## Exceptions

The Address Group models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When neither or both static and dynamic fields are provided
    - When multiple container types (folder/snippet/device) are specified
    - When no container type is specified for create operations
    - When tag values are not unique in a list
    - When tag input is neither a string nor a list

## Model Validators

### Address Group Type Validation

The models enforce that exactly one group type (static or dynamic) must be specified:

<div class="termy">

<!-- termynal -->

```python
# This will raise a validation error
from scm.models.objects import AddressGroupCreateModel

# Error: both static and dynamic provided
try:
    group = AddressGroupCreateModel(
        name="invalid-group",
        static=["addr1"],
        dynamic={"filter": "'tag1'"},
        folder="Texas"
    )
except ValueError as e:
    print(e)  # "Exactly one of 'static' or 'dynamic' must be provided."

# Error: neither static nor dynamic provided
try:
    group = AddressGroupCreateModel(
        name="invalid-group",
        folder="Texas"
    )
except ValueError as e:
    print(e)  # "Exactly one of 'static' or 'dynamic' must be provided."
```

</div>

### Container Type Validation

For create operations, exactly one container type must be specified:

<div class="termy">

<!-- termynal -->

```python
# This will raise a validation error
try:
    group = AddressGroupCreateModel(
        name="invalid-group",
        static=["addr1"],
        folder="Texas",
        device="fw01"  # Can't specify both folder and device
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."
```

</div>

### Tag Validation

Tags must be unique and properly formatted:

<div class="termy">

<!-- termynal -->

```python
# This will raise a validation error for duplicate tags
try:
    group = AddressGroupCreateModel(
        name="invalid-group",
        static=["addr1"],
        folder="Texas",
        tag=["web", "web"]  # Duplicate tags not allowed
    )
except ValueError as e:
    print(e)  # "List items must be unique"

# This will convert a single string tag to a list
group = AddressGroupCreateModel(
    name="valid-group",
    static=["addr1"],
    folder="Texas",
    tag="web"  # Will be converted to ["web"]
)
```

</div>

## Usage Examples

### Creating a Static Address Group

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
from scm.config.objects import AddressGroup

static_group_dict = {
    "name": "web-servers",
    "description": "Web server group",
    "static": ["web1", "web2", "web3"],
    "folder": "Texas",
    "tag": ["web", "production"]
}

address_group = AddressGroup(api_client)
response = address_group.create(static_group_dict)

# Using model directly
from scm.models.objects import AddressGroupCreateModel

static_group = AddressGroupCreateModel(
    name="web-servers",
    description="Web server group",
    static=["web1", "web2", "web3"],
    folder="Texas",
    tag=["web", "production"]
)

payload = static_group.model_dump(exclude_unset=True)
response = address_group.create(payload)
```

</div>

### Creating a Dynamic Address Group

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
dynamic_group_dict = {
    "name": "aws-instances",
    "description": "AWS EC2 instances",
    "dynamic": {
        "filter": "'aws-tag' and 'production'"
    },
    "folder": "Cloud",
    "tag": ["aws", "dynamic"]
}

response = address_group.create(dynamic_group_dict)

# Using model directly
from scm.models.objects import AddressGroupCreateModel, DynamicFilter

dynamic_group = AddressGroupCreateModel(
    name="aws-instances",
    description="AWS EC2 instances",
    dynamic=DynamicFilter(filter="'aws-tag' and 'production'"),
    folder="Cloud",
    tag=["aws", "dynamic"]
)

payload = dynamic_group.model_dump(exclude_unset=True)
response = address_group.create(payload)
```

</div>

### Updating an Address Group

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
update_dict = {
    "id": "123e4567-e89b-12d3-a456-426655440000",
    "name": "web-servers-updated",
    "description": "Updated web server group",
    "static": ["web1", "web2", "web3", "web4"],
    "tag": ["web", "production", "updated"]
}

response = address_group.update(update_dict)

# Using model directly
from scm.models.objects import AddressGroupUpdateModel

update_group = AddressGroupUpdateModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="web-servers-updated",
    description="Updated web server group",
    static=["web1", "web2", "web3", "web4"],
    tag=["web", "production", "updated"]
)

payload = update_group.model_dump(exclude_unset=True)
response = address_group.update(payload)
```

</div>
