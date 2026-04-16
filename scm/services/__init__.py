"""scm.services: Base class for non-CRUD service implementations."""

from typing import Any, Dict


class ServiceBase:
    """Thin base class for non-CRUD services.

    Provides api_client access and optional header injection.
    Subclasses override _get_headers() to inject custom headers.
    """

    def __init__(self, api_client: Any):
        self.api_client = api_client

    def _get_headers(self) -> Dict[str, str]:
        return {}
