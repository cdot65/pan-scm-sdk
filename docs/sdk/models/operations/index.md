# Operations Data Models

Pydantic models for validating and serializing operations-related data in the Strata Cloud Manager SDK.

## Overview

The Strata Cloud Manager SDK uses Pydantic models for data validation and serialization of operations-related data. These models ensure that the data being sent to and received from the Strata Cloud Manager API adheres to the expected structure and constraints. This section documents the models for operational tasks such as job management and configuration commits.

## Model Types

For operations functionality, there are corresponding model types:

- **Request Models**: Used when sending operational commands to the API
- **Response Models**: Used when parsing operation results retrieved from the API
- **Data Models**: Used to represent specific operational data structures

## Common Model Patterns

Operations models share common patterns:

- UUID validation for identifiers
- Timestamp handling and validation
- Status and result code validation
- Pagination and filtering configuration
- Job monitoring and control
- Error handling and message parsing

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

# Create a commit request using a model
commit_request = CandidatePushModel(
   description="Updated security policies",
   folders=["Security Policies"],
   device_groups=[],
   devices=[],
   include_uncommitted_changes=True,
   admins=[]
)

# Convert the model to a dictionary for the API call
commit_dict = commit_request.model_dump(exclude_unset=True)
result = client.operations.commit(commit_dict)
```

### Checking Job Status

```python
# Check job status
job_id = result.id
job_status = client.operations.get_job_status(job_id)

# List recent jobs
job_list = client.operations.list_jobs(limit=10)
for job in job_list.data:
   print(f"Job {job.id}: {job.type_str} - {job.status_str}")
```

## Models by Category

### Jobs

- [Jobs Models](jobs.md) - Job status and monitoring models

### Candidate Push

- [Candidate Push Models](candidate_push.md) - Configuration commit models

### Local Config

- [Local Config Models](local_config_models.md) - Device configuration version models

### Device Operations

- [Device Operations Models](device_operations_models.md) - Device job dispatch and status models
