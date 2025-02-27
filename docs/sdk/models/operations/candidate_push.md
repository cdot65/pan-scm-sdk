# Candidate Push Models

## Overview

The Candidate Push models provide a structured way to manage configuration commits in Palo Alto Networks' Strata Cloud
Manager.
These models handle the validation and processing of commit requests, including folder selection, admin authorization,
and
commit descriptions.

## Attributes

### Request Model Attributes

| Attribute   | Type      | Required | Default | Description                                     |
|-------------|-----------|----------|---------|-------------------------------------------------|
| folders     | List[str] | Yes      | None    | List of folders to commit changes from          |
| admin       | List[str] | Yes      | None    | List of admin email addresses for authorization |
| description | str       | Yes      | None    | Description of commit changes. Max length: 255  |

### Response Model Attributes

| Attribute | Type | Required | Default | Description                                       |
|-----------|------|----------|---------|---------------------------------------------------|
| success   | bool | Yes      | None    | Whether commit operation was successfully started |
| job_id    | str  | Yes      | None    | ID of the commit job                              |
| message   | str  | Yes      | None    | Detailed message about the commit operation       |

## Exceptions

The Candidate Push models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When folders list is empty or contains invalid strings
    - When admin list is empty or contains invalid email addresses
    - When description validation fails (empty or exceeds max length)

## Model Validators

### Folder Validation

The models enforce validation rules for the folders list:

<div class="termy">

<!-- termynal -->

```python
from scm.models.operations import CandidatePushRequestModel

# Error: empty folders list
try:
    request = CandidatePushRequestModel(
        folders=[],
        admin=["admin@example.com"],
        description="Test commit"
    )
except ValueError as e:
    print(e)  # "At least one folder must be specified"

# Error: invalid folder strings
try:
    request = CandidatePushRequestModel(
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
# Error: empty admin list
try:
    request = CandidatePushRequestModel(
        folders=["Production"],
        admin=[],
        description="Test commit"
    )
except ValueError as e:
    print(e)  # "At least one admin must be specified"

# Error: invalid email addresses
try:
    request = CandidatePushRequestModel(
        folders=["Production"],
        admin=["invalid-email", "also-invalid"],
        description="Test commit"
    )
except ValueError as e:
    print(e)  # "All admin entries must be valid email addresses"
```

</div>

> **Note**: use the string value of "all" if you intend to commit the changes for all admin users.

## Usage Examples

### Creating a Commit Request

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
from scm.config.operations import CandidatePush

commit_dict = {
    "folders": ["Texas", "Production"],
    "admin": ["admin@example.com", "all"],
    "description": "Updating security policies"
}

candidate_push = CandidatePush(api_client)
response = candidate_push.create(commit_dict)

# Using model directly
from scm.models.operations import CandidatePushRequestModel

commit_request = CandidatePushRequestModel(
    folders=["Texas", "Production"],
    admin=["admin@example.com"],
    description="Updating security policies"
)

payload = commit_request.model_dump(exclude_unset=True)
response = candidate_push.create(payload)
```

</div>

### Handling the Response

<div class="termy">

<!-- termynal -->

```python
from scm.models.operations import CandidatePushResponseModel

# Response will be automatically validated
response = CandidatePushResponseModel(
    success=True,
    job_id="1586",
    message="CommitAndPush job enqueued with jobid 1586"
)

# Access response attributes
if response.success:
    print(f"Commit job {response.job_id} started successfully")
    print(f"Message: {response.message}")
```

</div>