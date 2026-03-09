# PBF Rule

The `PbfRule` class manages Policy-Based Forwarding (PBF) rule objects in Palo Alto Networks' Strata Cloud Manager. It extends from `BaseObject` and offers methods to create, retrieve, update, list, fetch, and delete PBF rules. These rules allow you to override the routing table and forward traffic based on source zones/interfaces, source and destination addresses, applications, services, and users, directing matching traffic through specific egress interfaces or nexthops.

## Class Overview

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Access the PBF Rule service directly through the client
pbf_rules = client.pbf_rule
```

| Method     | Description                                                | Parameters                                                                                                                       | Return Type                    |
|------------|------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|--------------------------------|
| `create()` | Creates a new PBF rule                                     | `data: Dict[str, Any]`                                                                                                           | `PbfRuleResponseModel`         |
| `get()`    | Retrieves a PBF rule by its unique ID                      | `object_id: str`                                                                                                                 | `PbfRuleResponseModel`         |
| `update()` | Updates an existing PBF rule                               | `rule: PbfRuleUpdateModel`                                                                                                       | `PbfRuleResponseModel`         |
| `list()`   | Lists PBF rules with optional filtering                    | `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`, `exact_match: bool = False`, plus additional filters | `List[PbfRuleResponseModel]`   |
| `fetch()`  | Fetches a single PBF rule by name within a container       | `name: str`, `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`                                          | `PbfRuleResponseModel`         |
| `delete()` | Deletes a PBF rule by its ID                               | `object_id: str`                                                                                                                 | `None`                         |

### PBF Rule Model Attributes

| Attribute                 | Type                            | Required | Default | Description                                                       |
|---------------------------|--------------------------------|----------|---------|-------------------------------------------------------------------|
| `name`                    | str                            | Yes      | None    | PBF rule name                                                     |
| `id`                      | UUID                           | Yes*     | None    | Unique identifier (*response/update only)                         |
| `description`             | str                            | No       | None    | Description of the PBF rule                                       |
| `tag`                     | List[str]                      | No       | None    | Tags associated with the PBF rule                                 |
| `schedule`                | str                            | No       | None    | Schedule for the PBF rule                                         |
| `disabled`                | bool                           | No       | None    | Whether the PBF rule is disabled                                  |
| `from_`                   | PbfRuleFrom                    | No       | None    | Source zone or interface. API field name: `from`                   |
| `source`                  | List[str]                      | No       | None    | Source addresses                                                  |
| `source_user`             | List[str]                      | No       | None    | Source users                                                      |
| `destination`             | List[str]                      | No       | None    | Destination addresses                                             |
| `destination_application` | Dict[str, Any]                 | No       | None    | Destination application configuration                             |
| `service`                 | List[str]                      | No       | None    | Services                                                          |
| `application`             | List[str]                      | No       | None    | Applications                                                      |
| `action`                  | PbfRuleAction                  | No       | None    | Action configuration (forward, discard, or no_pbf)                |
| `enforce_symmetric_return`| PbfRuleEnforceSymmetricReturn  | No       | None    | Enforce symmetric return configuration                            |
| `folder`                  | str                            | No**     | None    | Folder location. Max 64 chars                                     |
| `snippet`                 | str                            | No**     | None    | Snippet location. Max 64 chars                                    |
| `device`                  | str                            | No**     | None    | Device location. Max 64 chars                                     |

\* Only required for update and response models
\** Exactly one container (folder/snippet/device) must be provided for create operations

!!! note
    The `from_` attribute uses a Python alias because `from` is a reserved word in Python. In the model, the field is defined as `from_` with `alias="from"`. When providing data as a dictionary to `create()`, use the API field name `"from"`. When accessing the attribute on a model instance, use `rule.from_`.

### Exceptions

| Exception                    | HTTP Code | Description                                                                   |
|------------------------------|-----------|-------------------------------------------------------------------------------|
| `InvalidObjectError`         | 400       | Thrown when provided data or parameters are invalid                           |
| `MissingQueryParameterError` | 400       | Thrown when required query parameters (e.g., `name` or `folder`) are missing  |
| `NameNotUniqueError`         | 409       | Rule name already exists                                                      |
| `ObjectNotPresentError`      | 404       | Rule not found                                                                |
| `ReferenceNotZeroError`      | 409       | Rule still referenced by other objects                                        |
| `AuthenticationError`        | 401       | Authentication failed                                                         |
| `ServerError`                | 500       | Internal server error                                                         |

## Methods

### List PBF Rules

```python
# List all PBF rules in a folder
rules = client.pbf_rule.list(
   folder="Texas"
)

# Process results
for rule in rules:
   print(f"Name: {rule.name}, Disabled: {rule.disabled}")
```

#### Filtering Responses

The `list()` method supports additional parameters to refine your query results even further. Alongside basic filters,
you can leverage the `exact_match`, `exclude_folders`, `exclude_snippets`, and `exclude_devices` parameters to control
which objects are included or excluded after the initial API response is fetched.

**Parameters:**

- `exact_match (bool)`: When `True`, only objects defined exactly in the specified container (`folder`, `snippet`, or `device`) are returned. Inherited or propagated objects are filtered out.
- `exclude_folders (List[str])`: Provide a list of folder names that you do not want included in the results.
- `exclude_snippets (List[str])`: Provide a list of snippet values to exclude from the results.
- `exclude_devices (List[str])`: Provide a list of device values to exclude from the results.

**Examples:**

```python
# Only return rules defined exactly in 'Texas'
exact_rules = client.pbf_rule.list(
   folder='Texas',
   exact_match=True
)

for rule in exact_rules:
   print(f"Exact match: {rule.name} in {rule.folder}")

# Exclude all rules from the 'All' folder
no_all_rules = client.pbf_rule.list(
   folder='Texas',
   exclude_folders=['All']
)

for rule in no_all_rules:
   assert rule.folder != 'All'
   print(f"Filtered out 'All': {rule.name}")
```

#### Controlling Pagination with max_limit

The SDK supports pagination through the `max_limit` parameter, which defines how many objects are retrieved per API call. By default, `max_limit` is set to 2500. The API itself imposes a maximum allowed value of 5000. If you set `max_limit` higher than 5000, it will be capped to the API's maximum. The `list()` method will continue to iterate through all objects until all results have been retrieved. Adjusting `max_limit` can help manage retrieval performance and memory usage when working with large datasets.

**Example:**

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Configure max_limit using the property setter
client.pbf_rule.max_limit = 4000

# List all rules - auto-paginates through results
all_rules = client.pbf_rule.list(folder='Texas')
```

### Fetch a PBF Rule

```python
# Fetch by name and folder
rule = client.pbf_rule.fetch(
   name="redirect-to-wan2",
   folder="Texas"
)
print(f"Found rule: {rule.name}")

# Get by ID
rule_by_id = client.pbf_rule.get(rule.id)
print(f"Retrieved rule: {rule_by_id.name}")

# Access the 'from' field using the Python attribute name 'from_'
if rule.from_:
   print(f"Source zones: {rule.from_.zone}")
```

### Create a PBF Rule

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Create a PBF rule with forward action
rule_data = {
   "name": "redirect-to-wan2",
   "description": "Forward specific traffic through WAN2 interface",
   "from": {
      "zone": ["trust"]
   },
   "source": ["10.0.0.0/24"],
   "destination": ["any"],
   "application": ["web-browsing", "ssl"],
   "service": ["application-default"],
   "action": {
      "forward": {
         "egress_interface": "ethernet1/2",
         "nexthop": {
            "ip_address": "203.0.113.1"
         },
         "monitor": {
            "profile": "default",
            "ip_address": "203.0.113.1",
            "disable_if_unreachable": True
         }
      }
   },
   "folder": "Texas"
}

new_rule = client.pbf_rule.create(rule_data)
print(f"Created PBF rule with ID: {new_rule.id}")

# Create a PBF rule with discard action
discard_rule = {
   "name": "block-p2p-traffic",
   "description": "Discard peer-to-peer traffic",
   "from": {
      "zone": ["trust"]
   },
   "source": ["any"],
   "destination": ["any"],
   "application": ["bittorrent"],
   "action": {
      "discard": {}
   },
   "folder": "Texas"
}

discard = client.pbf_rule.create(discard_rule)
print(f"Created discard PBF rule with ID: {discard.id}")
```

### Update a PBF Rule

```python
# Fetch existing rule
existing_rule = client.pbf_rule.fetch(
   name="redirect-to-wan2",
   folder="Texas"
)

# Modify the description and disable the rule
existing_rule.description = "Updated WAN2 redirect rule"
existing_rule.disabled = True

# Perform update
updated_rule = client.pbf_rule.update(existing_rule)
```

### Delete a PBF Rule

```python
# Delete by ID
rule_id = "123e4567-e89b-12d3-a456-426655440000"
client.pbf_rule.delete(rule_id)
```

## Use Cases

#### Performing Commits

```python
# Prepare commit parameters
commit_params = {
   "folders": ["Texas"],
   "description": "Updated PBF rule configurations",
   "sync": True,
   "timeout": 300  # 5 minute timeout
}

# Commit the changes directly on the client
result = client.commit(**commit_params)

print(f"Commit job ID: {result.job_id}")
```

#### Monitoring Jobs

```python
# Get status of specific job directly from the client
job_status = client.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

# List recent jobs directly from the client
recent_jobs = client.list_jobs(limit=10)
for job in recent_jobs.data:
   print(f"Job {job.id}: {job.type_str} - {job.status_str}")
```

## Error Handling

```python
from scm.client import ScmClient
from scm.exceptions import (
   InvalidObjectError,
   MissingQueryParameterError,
   NameNotUniqueError,
   ObjectNotPresentError,
   ReferenceNotZeroError
)

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

try:
   # Create PBF rule
   rule_config = {
      "name": "test-pbf-rule",
      "description": "Test PBF rule",
      "from": {
         "zone": ["trust"]
      },
      "source": ["any"],
      "destination": ["any"],
      "action": {
         "forward": {
            "egress_interface": "ethernet1/2",
            "nexthop": {
               "ip_address": "10.0.0.1"
            }
         }
      },
      "folder": "Texas"
   }

   new_rule = client.pbf_rule.create(rule_config)

   # Commit changes
   result = client.commit(
      folders=["Texas"],
      description="Added PBF rule",
      sync=True
   )

   # Check job status
   status = client.get_job_status(result.job_id)

except InvalidObjectError as e:
   print(f"Invalid rule data: {e.message}")
except NameNotUniqueError as e:
   print(f"Rule name already exists: {e.message}")
except ObjectNotPresentError as e:
   print(f"Rule not found: {e.message}")
except ReferenceNotZeroError as e:
   print(f"Rule still in use: {e.message}")
except MissingQueryParameterError as e:
   print(f"Missing parameter: {e.message}")
```

## Related Topics

- [PbfRuleBaseModel](../../models/network/pbf_rule_models.md#Overview)
- [PbfRuleCreateModel](../../models/network/pbf_rule_models.md#Overview)
- [PbfRuleUpdateModel](../../models/network/pbf_rule_models.md#Overview)
- [PbfRuleResponseModel](../../models/network/pbf_rule_models.md#Overview)
