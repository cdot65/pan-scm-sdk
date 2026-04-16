"""Incidents service for the Unified Incident Framework API."""

from typing import Any, Dict, List, Optional

from scm.models.incidents.incidents import (
    IncidentDetailModel,
    IncidentSearchResponseModel,
)
from scm.services import ServiceBase


class Incidents(ServiceBase):
    """Service for searching and retrieving incident details."""

    BASE_ENDPOINT = "/incidents/v1"

    def _get_headers(self) -> Dict[str, str]:
        headers = {"X-PANW-Region": self.api_client.default_region}
        if self.api_client.oauth_client:
            tsg_id = self.api_client.oauth_client.auth_request.tsg_id
            if tsg_id:
                headers["prisma-tenant"] = tsg_id
        return headers

    def search(
        self,
        *,
        status: Optional[List[str]] = None,
        severity: Optional[List[str]] = None,
        product: Optional[List[str]] = None,
        filter_rules: Optional[List[Dict[str, Any]]] = None,
        page_size: int = 50,
        page_number: int = 1,
        order_by: Optional[List[Dict[str, str]]] = None,
    ) -> IncidentSearchResponseModel:
        """Search incidents with filtering and pagination.

        Args:
            status: Filter by incident status (e.g., ["Raised", "Cleared"]).
            severity: Filter by severity (e.g., ["Critical", "High"]).
            product: Filter by product (e.g., ["NGFW", "Prisma Access"]).
            filter_rules: Raw filter rules for full control. Overrides convenience kwargs.
            page_size: Number of results per page (default 50).
            page_number: Page number (default 1).
            order_by: Ordering specification.

        Returns:
            IncidentSearchResponseModel with header metadata and incident list.

        """
        if filter_rules is not None:
            rules = filter_rules
        else:
            rules = []
            if status:
                rules.append({"property": "status", "operator": "in", "values": status})
            if severity:
                rules.append({"property": "severity", "operator": "in", "values": severity})
            if product:
                rules.append({"property": "product", "operator": "in", "values": product})

        payload: Dict[str, Any] = {
            "pagination": {
                "page_size": page_size,
                "page_number": page_number,
            },
        }

        if order_by:
            payload["pagination"]["order_by"] = order_by

        if rules:
            payload["filter"] = {"rules": rules}

        response = self.api_client.post(
            f"{self.BASE_ENDPOINT}/search",
            json=payload,
            headers=self._get_headers(),
        )
        return IncidentSearchResponseModel(**response)

    def get_details(self, incident_id: str) -> IncidentDetailModel:
        """Get detailed information about a specific incident.

        Args:
            incident_id: The unique identifier of the incident.

        Returns:
            IncidentDetailModel with full incident details including alerts.

        """
        response = self.api_client.get(
            f"{self.BASE_ENDPOINT}/details/{incident_id}",
            headers=self._get_headers(),
        )
        return IncidentDetailModel(**response)
