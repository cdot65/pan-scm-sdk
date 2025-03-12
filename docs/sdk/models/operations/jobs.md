# Jobs Models

## Table of Contents

1. [Overview](#overview)
2. [Model Attributes](#model-attributes)
   1. [JobDetails Model](#jobdetails-model)
   2. [JobStatusData Model](#jobstatusdata-model)
   3. [JobListItem Model](#joblistitem-model)
   4. [JobStatusResponse Model](#jobstatusresponse-model)
   5. [JobListResponse Model](#joblistresponse-model)
3. [Model Validators](#model-validators)
   1. [Timestamp Validation](#timestamp-validation)
   2. [Datetime Serialization](#datetime-serialization)
4. [Usage Examples](#usage-examples)
   1. [Working with Job Details](#working-with-job-details)
   2. [Processing Job Status Data](#processing-job-status-data)
   3. [Working with Job Lists](#working-with-job-lists)
   4. [Using Jobs with Unified Client](#using-jobs-with-unified-client)
   5. [Monitoring Long-Running Jobs](#monitoring-long-running-jobs)
5. [Best Practices](#best-practices)
6. [Related Models](#related-models)

## Overview

The Jobs models provide a structured way to track and monitor job status and details in Palo Alto Networks' Strata Cloud Manager. These models support both individual job status queries and paginated job list responses. The models handle validation and serialization of job data when interacting with the SCM API.

## Model Attributes

### JobDetails Model

| Attribute   | Type      | Required | Default | Description                    |
|-------------|-----------|----------|---------|--------------------------------|
| info        | List[str] | No       | []      | List of informational messages |
| errors      | List[str] | No       | []      | List of error messages         |
| warnings    | List[str] | No       | []      | List of warning messages       |
| description | str       | No       | None    | Description of the job         |

### JobStatusData Model

| Attribute   | Type     | Required | Default | Description                   |
|-------------|----------|----------|---------|-------------------------------|
| id          | str      | Yes      | None    | Unique identifier for the job |
| cfg_id      | str      | No       | ""      | Configuration ID              |
| details     | str      | Yes      | None    | Job details in JSON format    |
| dev_serial  | str      | No       | ""      | Device serial number          |
| dev_uuid    | str      | No       | ""      | Device UUID                   |
| device_name | str      | No       | ""      | Name of the device            |
| device_type | str      | No       | ""      | Type of device                |
| end_ts      | datetime | No       | None    | Job end timestamp             |
| insert_ts   | datetime | Yes      | None    | Job creation timestamp        |
| job_result  | str      | Yes      | None    | Result of the job             |
| job_status  | str      | Yes      | None    | Current status of the job     |
| job_type    | str      | Yes      | None    | Type of job                   |
| last_update | datetime | Yes      | None    | Last update timestamp         |
| owner       | str      | Yes      | None    | Job owner                     |
| parent_id   | str      | No       | "0"     | Parent job ID                 |
| percent     | str      | Yes      | None    | Job completion percentage     |
| result_i    | str      | Yes      | None    | Numeric result code           |
| result_str  | str      | Yes      | None    | String result description     |
| session_id  | str      | No       | ""      | Session ID                    |
| start_ts    | datetime | Yes      | None    | Job start timestamp           |
| status_i    | str      | Yes      | None    | Numeric status code           |
| status_str  | str      | Yes      | None    | String status description     |
| summary     | str      | No       | ""      | Job summary                   |
| type_i      | str      | Yes      | None    | Numeric job type code         |
| type_str    | str      | Yes      | None    | String job type description   |
| uname       | str      | Yes      | None    | Username                      |

### JobListItem Model

| Attribute   | Type | Required | Default | Description                   |
|-------------|------|----------|---------|-------------------------------|
| id          | str  | Yes      | None    | Unique identifier for the job |
| device_name | str  | No       | ""      | Name of the device            |
| end_ts      | str  | No       | None    | Job end timestamp             |
| job_result  | str  | Yes      | None    | Result of the job             |
| job_status  | str  | Yes      | None    | Current status of the job     |
| job_type    | str  | Yes      | None    | Type of job                   |
| parent_id   | str  | Yes      | None    | Parent job ID                 |
| percent     | str  | No       | ""      | Job completion percentage     |
| result_str  | str  | Yes      | None    | String result description     |
| start_ts    | str  | Yes      | None    | Job start timestamp           |
| status_str  | str  | Yes      | None    | String status description     |
| summary     | str  | No       | ""      | Job summary                   |
| type_str    | str  | Yes      | None    | String job type description   |
| uname       | str  | Yes      | None    | Username                      |
| description | str  | No       | ""      | Job description               |

### JobStatusResponse Model

| Attribute | Type                | Required | Default | Description                 |
|-----------|---------------------|----------|---------|-----------------------------|
| data      | List[JobStatusData] | Yes      | None    | List of job status objects  |

### JobListResponse Model

| Attribute | Type               | Required | Default | Description                     |
|-----------|--------------------|---------|---------|---------------------------------|
| data      | List[JobListItem]  | Yes      | None    | List of job list items          |
| total     | int                | Yes      | None    | Total number of jobs available  |
| limit     | int                | Yes      | None    | Max number of jobs per page     |
| offset    | int                | Yes      | None    | Current offset in result set    |

## Model Validators

### Timestamp Validation

The JobListItem model validates timestamp fields to handle empty strings:

<div class="termy">

<!-- termynal -->
```python
from scm.models.operations import JobListItem

# Empty string timestamps are converted to None
job = JobListItem(
   id="123",
   job_result="SUCCESS",
   job_status="COMPLETED",
   job_type="CONFIG",
   parent_id="0",
   result_str="Success",
   start_ts="2023-01-01T00:00:00",
   end_ts="",  # Will be converted to None
   status_str="Completed",
   type_str="Configuration",
   uname="admin"
)
print(job.end_ts)  # None
```

</div>

### Datetime Serialization

The JobStatusData model automatically serializes datetime fields to ISO format strings:

<div class="termy">

<!-- termynal -->
```python
from datetime import datetime
from scm.models.operations import JobStatusData

job = JobStatusData(
   id="123",
   details="{}",
   insert_ts=datetime.now(),
   job_result="SUCCESS",
   job_status="COMPLETED",
   job_type="CONFIG",
   last_update=datetime.now(),
   owner="admin",
   percent="100",
   result_i="1",
   result_str="Success",
   start_ts=datetime.now(),
   status_i="2",
   status_str="Completed",
   type_i="3",
   type_str="Configuration",
   uname="admin"
)

data = job.model_dump()
print(data["start_ts"])  # "2023-12-20T10:15:30.123456"
```

</div>

## Usage Examples

### Working with Job Details

<div class="termy">

<!-- termynal -->
```python
from scm.models.operations import JobDetails

# Create job details with messages
details = JobDetails(
   info=["Starting configuration push", "Configuration applied"],
   warnings=["Device connection slow"],
   errors=[],
   description="Configuration update job"
)

# Access job details
print(details.info)  # ["Starting configuration push", "Configuration applied"]
print(details.warnings)  # ["Device connection slow"]
print(details.description)  # "Configuration update job"
```

</div>

### Processing Job Status Data

<div class="termy">

<!-- termynal -->
```python
from scm.models.operations import JobStatusResponse, JobStatusData
from datetime import datetime

# Create job status data
job_data = JobStatusData(
   id="123",
   details="{}",
   insert_ts=datetime.now(),
   job_result="SUCCESS",
   job_status="COMPLETED",
   job_type="CONFIG",
   last_update=datetime.now(),
   owner="admin",
   percent="100",
   result_i="1",
   result_str="Success",
   start_ts=datetime.now(),
   status_i="2",
   status_str="Completed",
   type_i="3",
   type_str="Configuration",
   uname="admin"
)

# Create response with job data
response = JobStatusResponse(data=[job_data])

# Access job status information
for job in response.data:
   print(f"Job {job.id}: {job.status_str} ({job.percent}%)")
```

</div>

### Working with Job Lists

<div class="termy">

<!-- termynal -->
```python
from scm.models.operations import JobListResponse, JobListItem

# Create job list items
jobs = [
   JobListItem(
      id="123",
      job_result="SUCCESS",
      job_status="COMPLETED",
      job_type="CONFIG",
      parent_id="0",
      result_str="Success",
      start_ts="2023-01-01T00:00:00",
      status_str="Completed",
      type_str="Configuration",
      uname="admin"
   ),
   JobListItem(
      id="124",
      job_result="IN_PROGRESS",
      job_status="RUNNING",
      job_type="COMMIT",
      parent_id="0",
      result_str="In Progress",
      start_ts="2023-01-01T00:15:00",
      status_str="Running",
      type_str="Commit",
      uname="admin"
   )
]

# Create paginated response
response = JobListResponse(
   data=jobs,
   total=100,
   limit=10,
   offset=0
)

# Process job list
for job in response.data:
   print(f"Job {job.id}: {job.type_str} - {job.status_str}")

# Access pagination info
print(f"Showing {len(response.data)} of {response.total} jobs")
```

</div>

### Using Jobs with Unified Client

<div class="termy">

<!-- termynal -->
```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Get status of a specific job
job_id = "123e4567-e89b-12d3-a456-426655440000"
job_status = client.operations.get_job_status(job_id)

# Display job information
print(f"Job ID: {job_status.data[0].id}")
print(f"Status: {job_status.data[0].status_str}")
print(f"Result: {job_status.data[0].result_str}")
print(f"Progress: {job_status.data[0].percent}%")

# List recent jobs with pagination
recent_jobs = client.operations.list_jobs(limit=10, offset=0)
print(f"Found {recent_jobs.total} total jobs")

# Display list of jobs
for job in recent_jobs.data:
   print(f"Job {job.id}: {job.type_str} - {job.status_str}")

# Filter jobs by parent ID
parent_jobs = client.operations.list_jobs(
   limit=5,
   parent_id="0"  # Only top-level jobs
)

print(f"Found {parent_jobs.total} top-level jobs")
```

</div>

### Monitoring Long-Running Jobs

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

# Make a configuration change
commit_result = client.operations.commit(
   folders=["Security Policies"],
   description="Updated security rules",
   admin=["admin@example.com"]
)

# Get the job ID
job_id = commit_result.job_id
print(f"Monitoring job {job_id}")

# Poll for job completion
max_attempts = 12
attempt = 0
completed = False

while not completed and attempt < max_attempts:
   # Wait between checks
   time.sleep(5)
   attempt += 1

   # Get current job status
   status = client.operations.get_job_status(job_id)
   job = status.data[0]

   # Print progress
   print(f"Status: {job.status_str} ({job.percent}%)")

   # Check if job is completed or failed
   if job.job_status in ["FIN", "FAIL"]:
      completed = True
      if job.job_status == "FIN":
         print(f"Job completed successfully: {job.summary}")
      else:
         print(f"Job failed: {job.summary}")

# Handle timeout
if not completed:
   print("Job monitoring timed out. Check status later.")
```

</div>

## Best Practices

1. **Job Monitoring**
   - Implement timeouts when polling for job completion
   - Use exponential backoff for job status checks
   - Check both job_status and result_str for accurate status
   - Handle job failures gracefully with appropriate error messages

2. **Filtering and Pagination**
   - Use appropriate limit/offset values for listing jobs
   - Filter jobs by parent_id to group related operations
   - Consider job age when listing (recent jobs are usually more relevant)
   - Use pagination to navigate large result sets efficiently

3. **Error Handling**
   - Parse job details for specific error messages
   - Log job failures with sufficient context for troubleshooting
   - Implement retry logic for transient failures
   - Provide meaningful feedback to users about job progress

4. **Performance**
   - Batch job status checks when monitoring multiple jobs
   - Use appropriate polling intervals (5-10 seconds)
   - Avoid excessive job status checks
   - Consider using job notifications when available

## Related Models

- [CandidatePushModel](candidate_push.md) - Used for initiating commit operations
- [CandidatePushResponseModel](candidate_push.md#response-model-attributes) - Response from commit operations
