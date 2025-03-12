# Candidate Push Models

## Table of Contents

1. [Overview](#overview)
2. [Model Attributes](#model-attributes)
   1. [Request Model Attributes](#request-model-attributes)
   2. [Response Model Attributes](#response-model-attributes)
3. [Exceptions](#exceptions)
4. [Model Validators](#model-validators)
   1. [Folder Validation](#folder-validation)
   2. [Admin Validation](#admin-validation)
   3. [Description Validation](#description-validation)
5. [Usage Examples](#usage-examples)
   1. [Creating a Commit Request](#creating-a-commit-request)
   2. [Handling the Response](#handling-the-response)
   3. [Commit with Unified Client](#commit-with-unified-client)
6. [Best Practices](#best-practices)
7. [Related Models](#related-models)

## Overview

The Candidate Push models provide a structured way to manage configuration commits in Palo Alto Networks' Strata Cloud Manager. These models handle the validation and processing of commit requests, including folder selection, admin authorization, and commit descriptions.

## Model Attributes

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

<div class="termy">

<!-- termynal -->
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

</div>

### Admin Validation

The models validate admin email addresses:

<div class="termy">

<!-- termynal -->
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

</div>

### Description Validation

The models validate the commit description:

<div class="termy">

<!-- termynal -->
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

</div>

## Usage Examples

### Creating a Commit Request

<div class="termy">

<!-- termynal -->
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

</div>

### Handling the Response

<div class="termy">

<!-- termynal -->
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

</div>

### Commit with Unified Client

<div class="termy">

<!-- termynal -->
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

</div>

## Best Practices

1. **Commit Description**
   - Use descriptive, meaningful commit descriptions
   - Include ticket/issue numbers for traceability
   - Mention impacted services or functionality
   - Keep descriptions under 255 characters

2. **Folder Selection**
   - Only commit to folders that contain actual changes
   - Group related changes in the same commit
   - Consider impacts on other configurations
   - Use a testing folder before committing to production

3. **Admin Authorization**
   - Use specific admin accounts rather than "all" when possible
   - Follow the principle of least privilege
   - Document which admins are authorized for which folders
   - Regularly review and update admin privileges

4. **Job Monitoring**
   - Always check job status after initiating a commit
   - Implement a timeout for long-running commits
   - Add retry logic for transient failures
   - Log commit job details for audit purposes

## Related Models

- [Jobs Models](jobs.md) - Used for tracking commit job status
- [JobStatusResponse](jobs.md#jobstatusresponse-model) - Job status tracking model
