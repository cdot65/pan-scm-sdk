# scm/config/security/security_rule.py

from typing import List, Dict, Any, Optional
from scm.config import BaseObject
from scm.models.security import (
    SecurityRuleRequestModel,
    SecurityRuleResponseModel,
    SecurityRuleMoveModel,
    Rulebase,
)
from scm.exceptions import ValidationError


class SecurityRule(BaseObject):
    """
    Manages Security Rules in Palo Alto Networks' Strata Cloud Manager.
    """

    ENDPOINT = "/config/security/v1/security-rules"

    def __init__(self, api_client):
        super().__init__(api_client)

    def create(
        self,
        data: Dict[str, Any],
        rulebase: str = "pre",
    ) -> SecurityRuleResponseModel:
        """
        Create a new security rule.

        Args:
            data: Dictionary containing the security rule configuration
            rulebase: Which rulebase to use ('pre' or 'post'), defaults to 'pre'

        Example:
            >>> security_rule.create({
            ...     "name": "Allow_HTTPS_With_Profile",
            ...     "description": "Allow HTTPS traffic with security profiles",
            ...     "folder": "Texas",
            ...     "from": ["lan"],
            ...     "to": ["wan"],
            ...     "action": "allow",
            ...     "profile_setting": {"group": ["best-practice"]},
            ...     "log_end": True
            ... }, rulebase="post")
        """
        # Validate rulebase using the enum
        if not isinstance(rulebase, Rulebase):
            try:
                rulebase = Rulebase(rulebase.lower())
            except ValueError:
                raise ValueError("rulebase must be either 'pre' or 'post'")

        # Validate the request data
        profile = SecurityRuleRequestModel(**data)
        payload = profile.model_dump(
            exclude_none=True,
            by_alias=True,
        )

        # Make API call with rulebase as position query parameter
        response = self.api_client.post(
            self.ENDPOINT,
            params={"position": rulebase.value},
            json=payload,
        )
        return SecurityRuleResponseModel(**response)

    def get(
        self,
        object_id: str,
        rulebase: str = "pre",
    ) -> SecurityRuleResponseModel:
        """
        Get a security rule by ID.

        Args:
            object_id: The UUID of the security rule
            rulebase: Which rulebase to use ('pre' or 'post'), defaults to 'pre'
        """
        if not isinstance(rulebase, Rulebase):
            try:
                rulebase = Rulebase(rulebase.lower())
            except ValueError:
                raise ValueError("rulebase must be either 'pre' or 'post'")

        endpoint = f"{self.ENDPOINT}/{object_id}"
        response = self.api_client.get(
            endpoint,
            params={"position": rulebase.value},
        )
        return SecurityRuleResponseModel(**response)

    def update(
        self,
        data: Dict[str, Any],
        rulebase: str = "pre",
    ) -> SecurityRuleResponseModel:
        """
        Update an existing security rule.

        Args:
            object_id: The UUID of the security rule to update
            data: Dictionary containing the updated configuration
            rulebase: Which rulebase to use ('pre' or 'post'), defaults to 'pre'
        """
        if not isinstance(rulebase, Rulebase):
            try:
                rulebase = Rulebase(rulebase.lower())
            except ValueError:
                raise ValueError("rulebase must be either 'pre' or 'post'")

        profile = SecurityRuleRequestModel(**data)
        payload = profile.model_dump(
            exclude_unset=True,
            by_alias=True,
        )

        endpoint = f"{self.ENDPOINT}/{data['id']}"
        response = self.api_client.put(
            endpoint,
            params={"position": rulebase.value},
            json=payload,
        )
        return SecurityRuleResponseModel(**response)

    def delete(
        self,
        object_id: str,
        rulebase: str = "pre",
    ) -> None:
        """
        Delete a security rule.

        Args:
            object_id: The UUID of the security rule to delete
            rulebase: Which rulebase to use ('pre' or 'post'), defaults to 'pre'
        """
        if not isinstance(rulebase, Rulebase):
            try:
                rulebase = Rulebase(rulebase.lower())
            except ValueError:
                raise ValueError("rulebase must be either 'pre' or 'post'")

        endpoint = f"{self.ENDPOINT}/{object_id}"
        self.api_client.delete(
            endpoint,
            params={"position": rulebase.value},
        )

    def move(
        self,
        rule_id: str,
        data: Dict[str, Any],
    ) -> None:
        """
        Move a security rule to a new position within the rulebase.

        Args:
            rule_id (str): The UUID of the rule to move
            data (Dict[str, Any]): Dictionary containing move parameters:
                - destination: Where to move the rule ('top', 'bottom', 'before', 'after')
                - rulebase: Which rulebase to use ('pre', 'post')
                - destination_rule: UUID of reference rule (required for 'before'/'after')

        Example:
            >>> security_rule.move("123e4567-e89b-12d3-a456-426655440000", {
            ...     "destination": "before",
            ...     "rulebase": "pre",
            ...     "destination_rule": "987fcdeb-51d3-a456-426655440000"
            ... })
        """
        # Create move configuration with the provided rule_id and data
        move_config = SecurityRuleMoveModel(
            source_rule=rule_id,
            **data,
        )

        # Convert to dict for API request, excluding None values
        payload = move_config.model_dump(exclude_none=True)

        # Make the API call
        endpoint = f"{self.ENDPOINT}/{rule_id}:move"
        self.api_client.post(
            endpoint,
            json=payload,
        )

    def list(
        self,
        folder: Optional[str] = None,
        snippet: Optional[str] = None,
        device: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        name: Optional[str] = None,
        rulebase: str = "pre",
        **filters,
    ) -> List[SecurityRuleResponseModel]:
        """
        List security rules with the given filters.

        Args:
            folder: Folder in which the resource is defined
            snippet: Snippet in which the resource is defined
            device: Device in which the resource is defined
            offset: The offset into the list of results returned
            limit: The maximum number of results per page
            name: The name of the configuration resource
            rulebase: Which rulebase to use ('pre' or 'post'), defaults to 'pre'
            **filters: Additional filters to apply
        """
        if not isinstance(rulebase, Rulebase):
            try:
                rulebase = Rulebase(rulebase.lower())
            except ValueError:
                raise ValueError("rulebase must be either 'pre' or 'post'")

        params = {"position": rulebase.value}
        error_messages = []

        # Validate offset and limit
        if offset is not None:
            if not isinstance(offset, int) or offset < 0:
                error_messages.append("Offset must be a non-negative integer")
        if limit is not None:
            if not isinstance(limit, int) or limit <= 0:
                error_messages.append("Limit must be a positive integer")

        if error_messages:
            raise ValueError(". ".join(error_messages))

        # Include container type parameter
        container_params = {
            "folder": folder,
            "snippet": snippet,
            "device": device,
        }
        provided_containers = {
            k: v for k, v in container_params.items() if v is not None
        }

        if len(provided_containers) != 1:
            raise ValidationError(
                "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            )

        params.update(provided_containers)

        # Handle pagination parameters
        if offset is not None:
            params["offset"] = offset
        if limit is not None:
            params["limit"] = limit

        # Handle filters
        if name is not None:
            params["name"] = name

        # Include any additional filters provided
        params.update(
            {
                k: v
                for k, v in filters.items()
                if v is not None
                and k not in container_params
                and k not in ["offset", "limit", "name"]
            }
        )

        response = self.api_client.get(
            self.ENDPOINT,
            params=params,
        )
        profiles = [
            SecurityRuleResponseModel(**item) for item in response.get("data", [])
        ]
        return profiles

    def fetch(
        self,
        name: str,
        folder: Optional[str] = None,
        snippet: Optional[str] = None,
        device: Optional[str] = None,
        **filters,
    ) -> Dict[str, Any]:
        """
        Fetches a single Security Rule object by name.

        Args:
            name (str): The name of the Security Rule to fetch.
            folder (str, optional): The folder in which the resource is defined.
            snippet (str, optional): The snippet in which the resource is defined.
            device (str, optional): The device in which the resource is defined.
            **filters: Additional filters to apply to the request.

        Returns:
            SecurityRuleResponseModel: The fetched security rule object.

        Raises:
            ValidationError: If invalid parameters are provided.
            NotFoundError: If the security rule object is not found.
        """
        if not name:
            raise ValidationError("Parameter 'name' must be provided for fetch method.")

        params = {}

        # Include container type parameter
        container_params = {
            "folder": folder,
            "snippet": snippet,
            "device": device,
        }
        provided_containers = {
            k: v for k, v in container_params.items() if v is not None
        }

        if len(provided_containers) != 1:
            raise ValidationError(
                "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            )

        params.update(provided_containers)
        params["name"] = name  # Set the 'name' parameter

        # Include any additional filters provided
        params.update(
            {
                k: v
                for k, v in filters.items()
                if k
                not in [
                    "types",
                    "values",
                    "names",
                    "tags",
                    "folder",
                    "snippet",
                    "device",
                    "name",
                ]
            }
        )

        response = self.api_client.get(
            self.ENDPOINT,
            params=params,
        )

        # Since response is a single object when 'name' is provided
        # We can directly create the SecurityRuleResponseModel
        rule = SecurityRuleResponseModel(**response)
        return rule.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )
