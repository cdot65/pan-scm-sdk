# QoS Rule

The `QosRule` class manages QoS policy rule objects in Palo Alto Networks' Strata Cloud Manager. It extends from `BaseObject` and offers methods to create, retrieve, update, list, fetch, delete, and move QoS policy rules. These rules define how traffic is classified and assigned to QoS classes, enabling traffic prioritization through DSCP/TOS markings and schedule-based application.

## Class Overview

```python
from scm.client import Scm

# Initialize client
client = Scm(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Access the QoS Rule service directly through the client
qos_rules = client.qos_rule
```

| Method     | Description                                                | Parameters                                                                                                                       | Return Type                    |
|------------|------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|--------------------------------|
| `create()` | Creates a new QoS rule                                     | `data: Dict[str, Any]`                                                                                                           | `QosRuleResponseModel`         |
| `get()`    | Retrieves a QoS rule by its unique ID                      | `object_id: str`                                                                                                                 | `QosRuleResponseModel`         |
| `update()` | Updates an existing QoS rule                               | `rule: QosRuleUpdateModel`                                                                                                       | `QosRuleResponseModel`         |
| `list()`   | Lists QoS rules with optional filtering                    | `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`, `exact_match: bool = False`, plus additional filters | `List[QosRuleResponseModel]`   |
| `fetch()`  | Fetches a single QoS rule by name within a container       | `name: str`, `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`                                          | `QosRuleResponseModel`         |
| `delete()` | Deletes a QoS rule by its ID                               | `object_id: str`                                                                                                                 | `None`                         |
| `move()`   | Moves a QoS rule to a new position within the rulebase     | `rule_id: UUID`, `data: Dict[str, Any]`                                                                                          | `None`                         |

### QoS Rule Model Attributes

| Attribute     | Type              | Required | Default | Description                                                       |
|---------------|-------------------|----------|---------|-------------------------------------------------------------------|
| `name`        | str               | Yes      | None    | Rule name                                                         |
| `id`          | UUID              | Yes*     | None    | Unique identifier (*response/update only)                         |
| `description` | str               | No       | None    | Description of the QoS rule                                       |
| `action`      | Dict[str, Any]    | No       | None    | QoS action configuration with 'class' field referencing a profile |
| `schedule`    | str               | No       | None    | Schedule for the QoS rule                                         |
| `dscp_tos`    | Dict[str, Any]    | No       | None    | DSCP/TOS codepoint settings                                       |
| `folder`      | str               | No**     | None    | Folder location. Max 64 chars                                     |
| `snippet`     | str               | No**     | None    | Snippet location. Max 64 chars                                    |
| `device`      | str               | No**     | None    | Device location. Max 64 chars                                     |

\* Only required for update and response models
\** Exactly one container (folder/snippet/device) must be provided for create operations

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

### List QoS Rules

```python
# List all QoS rules in a folder
rules = client.qos_rule.list(
   folder="Texas"
)

# Process results
for rule in rules:
   print(f"Name: {rule.name}, Description: {rule.description}")
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
exact_rules = client.qos_rule.list(
   folder='Texas',
   exact_match=True
)

for rule in exact_rules:
   print(f"Exact match: {rule.name} in {rule.folder}")

# Exclude all rules from the 'All' folder
no_all_rules = client.qos_rule.list(
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
from scm.client import Scm

# Initialize client
client = Scm(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Configure max_limit using the property setter
client.qos_rule.max_limit = 4000

# List all rules - auto-paginates through results
all_rules = client.qos_rule.list(folder='Texas')
```

### Fetch a QoS Rule

```python
# Fetch by name and folder
rule = client.qos_rule.fetch(
   name="voip-priority",
   folder="Texas"
)
print(f"Found rule: {rule.name}")

# Get by ID
rule_by_id = client.qos_rule.get(rule.id)
print(f"Retrieved rule: {rule_by_id.name}")
```

### Create a QoS Rule

```python
from scm.client import Scm

# Initialize client
client = Scm(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Create a QoS rule with action and DSCP settings
rule_data = {
   "name": "voip-priority",
   "description": "Prioritize VoIP traffic",
   "action": {
      "class": "class1"
   },
   "dscp_tos": {
      "codepoints": [
         {"name": "ef", "type": {"af": {"codepoint": "ef"}}}
      ]
   },
   "folder": "Texas"
}

new_rule = client.qos_rule.create(rule_data)
print(f"Created QoS rule with ID: {new_rule.id}")

# Create a scheduled QoS rule
scheduled_rule = {
   "name": "business-hours-qos",
   "description": "Business hours bandwidth management",
   "action": {
      "class": "class2"
   },
   "schedule": "business-hours",
   "folder": "Texas"
}

sched_rule = client.qos_rule.create(scheduled_rule)
print(f"Created scheduled QoS rule with ID: {sched_rule.id}")
```

### Update a QoS Rule

```python
# Fetch existing rule
existing_rule = client.qos_rule.fetch(
   name="voip-priority",
   folder="Texas"
)

# Modify the description and action
existing_rule.description = "Updated VoIP priority rule"
existing_rule.action = {
   "class": "class1"
}

# Perform update
updated_rule = client.qos_rule.update(existing_rule)
```

### Delete a QoS Rule

```python
# Delete by ID
rule_id = "123e4567-e89b-12d3-a456-426655440000"
client.qos_rule.delete(rule_id)
```

## Use Cases

#### Performing Commits

```python
# Prepare commit parameters
commit_params = {
   "folders": ["Texas"],
   "description": "Updated QoS rule configurations",
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
from scm.client import Scm
from scm.exceptions import (
   InvalidObjectError,
   MissingQueryParameterError,
   NameNotUniqueError,
   ObjectNotPresentError,
   ReferenceNotZeroError
)

# Initialize client
client = Scm(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

try:
   # Create QoS rule
   rule_config = {
      "name": "test-qos-rule",
      "description": "Test QoS rule",
      "action": {
         "class": "class1"
      },
      "folder": "Texas"
   }

   new_rule = client.qos_rule.create(rule_config)

   # Commit changes
   result = client.commit(
      folders=["Texas"],
      description="Added QoS rule",
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

- [QosRuleBaseModel](../../models/network/qos_rule_models.md#Overview)
- [QosRuleCreateModel](../../models/network/qos_rule_models.md#Overview)
- [QosRuleUpdateModel](../../models/network/qos_rule_models.md#Overview)
- [QosRuleResponseModel](../../models/network/qos_rule_models.md#Overview)
- [QosRuleMoveModel](../../models/network/qos_rule_models.md#Overview)
- [QosMoveDestination](../../models/network/qos_rule_models.md#Overview)
- [QosRulebase](../../models/network/qos_rule_models.md#Overview)
