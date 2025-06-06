# Candidate Push Models

## Overview {#Overview}

The Candidate Push models provide a structured way to manage configuration commits in Palo Alto Networks' Strata Cloud Manager. These models handle the validation and processing of commit requests, including folder selection, admin authorization, and commit descriptions.

## Attributes

### Request Model Attributes

| Attribute                 | Type      | Required | Default | Description                                     |
|---------------------------|-----------|----------|---------|-------------------------------------------------|
| folders                   | List[str] | Yes      | None    | List of folders to commit changes from          |
| admin                     | List[str] | Yes      | None    | List of admin email addresses for authorization |
| description               | str       | Yes      | None    | Description of commit changes. Max length: 255  |
| device_groups             | List[str] | No       | []      | List of device groups to commit changes to      |
| devices                   | List[str] | No       | []      | List of devices to commit changes to            |
| include_uncommitted_changes | bool    | No       | False   | Whether to include uncommitted changes          |

### Response Model Attributes

| Attribute | Type | Required | Default | Description                                       |
|-----------|------|----------|---------|---------------------------------------------------|
| success   | bool | Yes      | None    | Whether commit operation was successfully started |
| job_id    | str  | Yes      | None    | ID of the commit job                              |
| id        | str  | Yes      | None    | ID of the commit job (alias for job_id)           |
| message   | str  | Yes      | None    | Detailed message about the commit operation       |

## Exceptions

The Candidate Push models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
  - When folders list is empty or contains invalid strings
  - When admin list is empty or contains invalid email addresses
  - When description validation fails (empty or exceeds max length)
  - When device_groups or devices contain invalid entries

## Model Validators

### Folder Validation

The models enforce validation rules for the folders list:

```python
from scm.models.operations import CandidatePushModel

# Initialize with valid folder data
commit_request = CandidatePushModel(
   folders=["Texas", "Production"],
   admin=["admin@example.com"],
   description="Configuration update"
)

# Error: empty folders list
try:
   invalid_request = CandidatePushModel(
      folders=[],
      admin=["admin@example.com"],
      description="Test commit"
   )
except ValueError as e:
   print(e)  # "At least one folder must be specified"

# Error: invalid folder strings
try:
   invalid_request = CandidatePushModel(
      folders=["", "  "],
      admin=["admin@example.com"],
      description="Test commit"
   )
except ValueError as e:
   print(e)  # "All folders must be non-empty strings"
```

### Admin Validation

The models validate admin email addresses:

```python
from scm.models.operations import CandidatePushModel

# Initialize with valid admin data
commit_request = CandidatePushModel(
   folders=["Texas"],
   admin=["admin@example.com"],
   description="Configuration update"
)

# Special value "all" is allowed for all admins
all_admins_request = CandidatePushModel(
   folders=["Texas"],
   admin=["all"],
   description="Configuration update"
)

# Error: empty admin list
try:
   invalid_request = CandidatePushModel(
      folders=["Production"],
      admin=[],
      description="Test commit"
   )
except ValueError as e:
   print(e)  # "At least one admin must be specified"

# Error: invalid email addresses
try:
   invalid_request = CandidatePushModel(
      folders=["Production"],
      admin=["invalid-email", "also-invalid"],
      description="Test commit"
   )
except ValueError as e:
   print(e)  # "All admin entries must be valid email addresses"
```

### Description Validation

The models validate the commit description:

```python
from scm.models.operations import CandidatePushModel

# Initialize with valid description
commit_request = CandidatePushModel(
   folders=["Texas"],
   admin=["admin@example.com"],
   description="Configuration update"
)

# Error: empty description
try:
   invalid_request = CandidatePushModel(
      folders=["Production"],
      admin=["admin@example.com"],
      description=""
   )
except ValueError as e:
   print(e)  # "Description cannot be empty"

# Error: description too long
try:
   invalid_request = CandidatePushModel(
      folders=["Production"],
      admin=["admin@example.com"],
      description="A" * 300  # Over 255 characters
   )
except ValueError as e:
   print(e)  # "Description cannot exceed 255 characters"
```

## Usage Examples

### Creating a Commit Request

```python
from scm.client import ScmClient
from scm.models.operations import CandidatePushModel

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Create a commit request using a dictionary
commit_dict = {
   "folders": ["Texas", "Production"],
   "admin": ["admin@example.com"],
   "description": "Updating security policies",
   "include_uncommitted_changes": True
}

response = client.operations.commit(commit_dict)

# Using model directly
commit_request = CandidatePushModel(
   folders=["Texas", "Production"],
   admin=["admin@example.com"],
   description="Updating security policies",
   include_uncommitted_changes=True
)

payload = commit_request.model_dump(exclude_unset=True)
response = client.operations.commit(payload)

print(f"Commit job started with ID: {response.job_id}")
```

### Handling the Response

```python
from scm.client import ScmClient
from scm.models.operations import CandidatePushResponseModel

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Create a commit request
commit_dict = {
   "folders": ["Texas"],
   "admin": ["admin@example.com"],
   "description": "Updating security policies"
}

response = client.operations.commit(commit_dict)

# Process the response
if response.success:
   print(f"Commit job {response.job_id} started successfully")
   print(f"Message: {response.message}")

   # Track the job status
   job_status = client.operations.get_job_status(response.job_id)
   print(f"Job status: {job_status.data[0].status_str}")
else:
   print(f"Commit failed: {response.message}")
```

### Commit with Unified Client

```python
from scm.client import ScmClient
import time

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Perform configuration updates
security_rule = client.security_rule.create({
   "name": "allow-web-traffic",
   "source": ["any"],
   "destination": ["any"],
   "application": ["web-browsing"],
   "service": ["application-default"],
   "action": "allow",
   "folder": "Security Policies"
})

# Commit the changes
commit_result = client.operations.commit(
   folders=["Security Policies"],
   description="Added web traffic rule",
   admin=["admin@example.com"]
)

# Monitor the job asynchronously
job_id = commit_result.job_id
print(f"Commit job initiated with ID: {job_id}")

# Poll for job completion
status = "PENDING"
while status not in ["FIN", "FAIL"]:
   time.sleep(5)
   job_result = client.operations.get_job_status(job_id)
   status = job_result.data[0].job_status
   print(f"Current status: {job_result.data[0].status_str}")

if status == "FIN":
   print("Commit completed successfully")
else:
   print(f"Commit failed: {job_result.data[0].summary}")
```
