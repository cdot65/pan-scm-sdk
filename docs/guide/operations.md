# Operations Management

The Strata Cloud Manager SDK provides capabilities for managing operations beyond just configuration objects, including candidate configurations, commits, and job monitoring.

## Candidate Configurations

In Palo Alto Networks environments, configuration changes are made to a candidate configuration before being committed to the running configuration. The SDK provides methods for managing these candidate configurations.

### Pushing Candidate Configurations

After making changes to your configuration, you need to push those changes to make them active:

```python
from scm.models.operations.candidate_push import CandidatePushRequestModel

# Create some objects
client.address.create({"name": "server1", "folder": "Shared", "ip_netmask": "192.168.1.100/32"})
client.address.create({"name": "server2", "folder": "Shared", "ip_netmask": "192.168.1.101/32"})

# Commit the changes
response = client.candidate_push({
    "description": "Adding server addresses",
    "admin_name": "admin"
})

# Get the job ID from the response
job_id = response["id"]
```

### Getting Commit Status

After initiating a commit, you can check its status:

```python
# Check the status of the commit job
job_status = client.jobs.status(job_id)
print(f"Job status: {job_status['status']}")

# Wait for the job to complete
import time
while job_status["status"] not in ["COMPLETED", "FAILED"]:
    time.sleep(5)
    job_status = client.jobs.status(job_id)
    print(f"Job status: {job_status['status']}")

if job_status["status"] == "COMPLETED":
    print("Commit completed successfully")
else:
    print(f"Commit failed: {job_status.get('message', 'Unknown error')}")
```

## Job Monitoring

Many operations in the Strata Cloud Manager are asynchronous and return a job ID. The SDK provides methods for monitoring these jobs.

### Checking Job Status

```python
# Check the status of a job
job_status = client.jobs.status(job_id)
print(f"Job status: {job_status['status']}")
```

### Waiting for Jobs to Complete

Here's a helper function to wait for a job to complete:

```python
def wait_for_job_completion(client, job_id, interval=5, timeout=600):
    import time
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        job_status = client.jobs.status(job_id)
        if job_status["status"] in ["COMPLETED", "FAILED"]:
            return job_status
        
        print(f"Job status: {job_status['status']}")
        time.sleep(interval)
    
    raise TimeoutError(f"Job did not complete within {timeout} seconds")

# Usage
job_result = wait_for_job_completion(client, job_id)
if job_result["status"] == "COMPLETED":
    print("Job completed successfully")
else:
    print(f"Job failed: {job_result.get('message', 'Unknown error')}")
```

## Error Handling

Operations can sometimes fail due to various reasons. The SDK provides structured error handling:

```python
from scm.exceptions import ScmError, ApiError, BadResponseError

try:
    # Attempt to push a candidate configuration
    response = client.candidate_push({
        "description": "Adding server addresses",
        "admin_name": "admin"
    })
    job_id = response["id"]
    
    # Wait for job completion
    job_result = wait_for_job_completion(client, job_id)
    if job_result["status"] != "COMPLETED":
        raise Exception(f"Job failed: {job_result.get('message', 'Unknown error')}")
        
except ApiError as e:
    print(f"API Error: {e}")
    # Handle API errors (e.g., invalid parameters, insufficient permissions)
    
except BadResponseError as e:
    print(f"Response Error: {e}")
    # Handle unexpected response format
    
except ScmError as e:
    print(f"SDK Error: {e}")
    # Handle general SDK errors
    
except Exception as e:
    print(f"General Error: {e}")
    # Handle other errors
```

## Next Steps

- Check out [Advanced Topics](advanced-topics.md) for pagination, filtering, and error handling
- Explore the [API Reference](../sdk/index.md) for detailed information on all available methods