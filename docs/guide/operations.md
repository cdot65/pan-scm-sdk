# Operations Management

The Strata Cloud Manager SDK provides capabilities for managing operations beyond just configuration objects, including candidate configurations, commits, and job monitoring.

## Candidate Configurations

In Palo Alto Networks environments, configuration changes are made to a candidate configuration before being committed to the running configuration. The SDK provides methods for managing these candidate configurations.

### Pushing Candidate Configurations

After making changes to your configuration, you need to commit those changes to make them active:

```python
# Create some objects
client.address.create({"name": "web-server-1", "folder": "Texas", "ip_netmask": "192.168.1.100/32"})
client.address.create({"name": "web-server-2", "folder": "Texas", "ip_netmask": "192.168.1.101/32"})

# Commit the changes
result = client.commit(
    folders=["Texas"],
    description="Adding server addresses",
    sync=True,
    timeout=300,
)

# Get the job ID from the response
job_id = result.job_id
```

### Getting Commit Status

After initiating a commit, you can check its status:

```python
# Check the status of the commit job
job_status = client.get_job_status(job_id)
print(f"Job status: {job_status.data[0].status_str}")

# Wait for the job to complete using the built-in method
final_status = client.wait_for_job(job_id, timeout=600, poll_interval=10)

if final_status.data[0].status_str == "FIN":
    print("Commit completed successfully")
else:
    print(f"Commit status: {final_status.data[0].result_str}")
```

## Job Monitoring

Many operations in the Strata Cloud Manager are asynchronous and return a job ID. The SDK provides methods for monitoring these jobs.

### Checking Job Status

```python
# Check the status of a job
job_status = client.get_job_status(job_id)
print(f"Job status: {job_status.data[0].status_str}")
```

### Listing Jobs

```python
# List recent jobs
jobs = client.list_jobs(limit=10)

# Get child jobs of a specific job
child_jobs = client.list_jobs(parent_id="parent-job-id")
```

### Waiting for Jobs to Complete

The SDK provides a built-in `wait_for_job` method:

```python
# Wait for a job to complete (raises TimeoutError if it exceeds timeout)
final_status = client.wait_for_job(
    job_id,
    timeout=600,
    poll_interval=10,
)

if final_status.data[0].status_str == "FIN":
    print("Job completed successfully")
else:
    print(f"Job result: {final_status.data[0].result_str}")
```

## Error Handling

Operations can sometimes fail due to various reasons. The SDK provides structured error handling:

```python
from scm.exceptions import APIError

try:
    # Commit changes synchronously
    result = client.commit(
        folders=["Texas"],
        description="Adding server addresses",
        sync=True,
        timeout=300,
    )
    print(f"Commit job ID: {result.job_id}")

except TimeoutError as e:
    print(f"Commit timed out: {e}")

except APIError as e:
    print(f"API Error: {e}")
    # Handle API errors (e.g., invalid parameters, insufficient permissions)

except Exception as e:
    print(f"General Error: {e}")
    # Handle other errors
```

## Next Steps

- Check out [Advanced Topics](advanced-topics.md) for pagination, filtering, and error handling
- Explore the [API Reference](../sdk/index.md) for detailed information on all available methods
