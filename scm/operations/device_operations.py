"""DeviceOperations service for Operations API."""

import time
from typing import List, Union

from scm.exceptions import JobTimeoutError
from scm.models.operations.device_operations import (
    DeviceJobStatusModel,
    DeviceOperationsRequestModel,
    JobCreatedModel,
)
from scm.services import ServiceBase


class DeviceOperations(ServiceBase):
    """Service for dispatching device operation jobs and polling for results."""

    BASE_ENDPOINT = "/operations/v1"

    def _dispatch_job(
        self,
        endpoint: str,
        devices: List[str],
        sync: bool = False,
        poll_interval: int = 10,
        timeout: int = 300,
    ) -> Union[JobCreatedModel, DeviceJobStatusModel]:
        """Dispatch a device operation job.

        Args:
            endpoint: Job endpoint path (e.g., "jobs/route-table").
            devices: List of 1-5 device serial numbers.
            sync: If True, poll until job completes or times out.
            poll_interval: Seconds between polls when sync=True.
            timeout: Max seconds to wait when sync=True.

        Returns:
            JobCreatedModel if sync=False, DeviceJobStatusModel if sync=True.

        Raises:
            ValidationError: If devices list is invalid.
            JobTimeoutError: If sync=True and job doesn't complete within timeout.

        """
        request_model = DeviceOperationsRequestModel(devices=devices)
        response = self.api_client.post(
            f"{self.BASE_ENDPOINT}/{endpoint}",
            json=request_model.model_dump(),
        )
        job = JobCreatedModel(**response)

        if not sync:
            return job

        start_time = time.time()
        while True:
            status = self.get_job_status(job.job_id)
            if status.state in ("complete", "failed"):
                return status

            if time.time() - start_time > timeout:
                raise JobTimeoutError(
                    job_id=job.job_id,
                    last_state=status.state,
                    timeout=timeout,
                )

            time.sleep(poll_interval)

    def get_job_status(self, job_id: str) -> DeviceJobStatusModel:
        """Get the status of a device operations job.

        Args:
            job_id: The job ID returned from a dispatch method.

        Returns:
            DeviceJobStatusModel with current job state and results.

        """
        response = self.api_client.get(f"{self.BASE_ENDPOINT}/device/jobs/{job_id}")
        return DeviceJobStatusModel(**response)

    def route_table(
        self, devices: List[str], sync: bool = False,
        poll_interval: int = 10, timeout: int = 300,
    ) -> Union[JobCreatedModel, DeviceJobStatusModel]:
        """Retrieve route table from device(s)."""
        return self._dispatch_job("jobs/route-table", devices, sync, poll_interval, timeout)

    def fib_table(
        self, devices: List[str], sync: bool = False,
        poll_interval: int = 10, timeout: int = 300,
    ) -> Union[JobCreatedModel, DeviceJobStatusModel]:
        """Retrieve FIB table from device(s)."""
        return self._dispatch_job("jobs/fib-table", devices, sync, poll_interval, timeout)

    def dns_proxy(
        self, devices: List[str], sync: bool = False,
        poll_interval: int = 10, timeout: int = 300,
    ) -> Union[JobCreatedModel, DeviceJobStatusModel]:
        """Retrieve DNS proxy configuration from device(s)."""
        return self._dispatch_job("jobs/dns-proxy", devices, sync, poll_interval, timeout)

    def device_interfaces(
        self, devices: List[str], sync: bool = False,
        poll_interval: int = 10, timeout: int = 300,
    ) -> Union[JobCreatedModel, DeviceJobStatusModel]:
        """Retrieve network interfaces from device(s)."""
        return self._dispatch_job("jobs/device-interfaces", devices, sync, poll_interval, timeout)

    def device_rules(
        self, devices: List[str], sync: bool = False,
        poll_interval: int = 10, timeout: int = 300,
    ) -> Union[JobCreatedModel, DeviceJobStatusModel]:
        """Retrieve security rules from device(s)."""
        return self._dispatch_job("jobs/device-rules", devices, sync, poll_interval, timeout)

    def bgp_policy_export(
        self, devices: List[str], sync: bool = False,
        poll_interval: int = 10, timeout: int = 300,
    ) -> Union[JobCreatedModel, DeviceJobStatusModel]:
        """Retrieve BGP policy export from device(s)."""
        return self._dispatch_job("jobs/bgp-policy-export", devices, sync, poll_interval, timeout)

    def logging_service_status(
        self, devices: List[str], sync: bool = False,
        poll_interval: int = 10, timeout: int = 300,
    ) -> Union[JobCreatedModel, DeviceJobStatusModel]:
        """Retrieve logging service forwarding status from device(s)."""
        return self._dispatch_job(
            "jobs/logging-service-forwarding-status", devices, sync, poll_interval, timeout
        )
