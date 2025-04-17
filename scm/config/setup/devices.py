"""SCM Config Setup Devices Service.

Handles interactions with the /devices endpoint.
"""

from typing import List, Optional

from ...base_object import BaseObject
from ...models.config.setup import DeviceGetResponseModel


class Devices(BaseObject):
    """SCM Devices Service Class."""

    ENDPOINT = "/devices"

    def get(self, id: str) -> DeviceGetResponseModel:
        """Retrieve a specific device by its ID.

        Args:
            id (str): The unique identifier for the device.

        Returns:
            DeviceGetResponseModel: The device details.

        Raises:
            ObjectNotPresentError: If the device with the specified ID is not found.
        """
        # TODO: Implement API call: GET /devices/{id}
        # TODO: Handle list response format [ {...} ]
        pass

    def list(self, **kwargs) -> List[DeviceGetResponseModel]:
        """Retrieve a list of devices.

        Args:
            **kwargs: Optional keyword arguments for filtering and pagination.
                Supported keys include 'limit', 'offset', etc. (Check API docs)

        Returns:
            List[DeviceGetResponseModel]: A list of devices.
        """
        # TODO: Implement API call: GET /devices
        # TODO: Handle pagination logic
        pass
