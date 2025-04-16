# Operations Data Models

## Table of Contents

1. [Overview](#overview)
2. [Model Types](#model-types)
3. [Common Model Patterns](#common-model-patterns)
4. [Usage Examples](#usage-examples)
5. [Models by Category](#models-by-category)
   1. [Jobs](#jobs)
   2. [Candidate Push](#candidate-push)
6. [Best Practices](#best-practices)
7. [Related Documentation](#related-documentation)

## Overview {#Overview}
<span id="overview"></span>

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

## Best Practices

1. **Job Management**
   - Use appropriate job monitoring patterns for long-running operations
   - Implement timeout handling for job completion
   - Set up proper error handling for job failures
   - Include job metadata such as descriptions for easier tracking

2. **Commit Operations**
   - Be specific about which folders to commit to minimize impact
   - Include meaningful descriptions with commits
   - Verify changes before committing to production
   - Consider scheduling commits during maintenance windows

3. **Error Handling**
   - Check job status codes for proper error detection
   - Parse error messages to provide meaningful feedback
   - Implement retry logic for transient failures
   - Log detailed job information for troubleshooting

4. **Performance Considerations**
   - Use pagination for listing large numbers of jobs
   - Limit the scope of commits to improve performance
   - Monitor job completion times for performance bottlenecks
   - Consider batching changes for fewer commit operations

## Related Documentation

- [Authentication](../../auth.md) - Authentication for API operations
- [Client Interface](../../client.md) - Using the client for operations
- [Configuration Objects](../../config/base_object.md) - Managing configuration objects
