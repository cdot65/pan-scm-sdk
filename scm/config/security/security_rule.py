# scm/config/security/security_rule.py

# Standard library imports
import logging
from typing import List, Dict, Any, Optional
from uuid import UUID

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
)
from scm.models.security import (
    SecurityRuleCreateModel,
    SecurityRuleUpdateModel,
    SecurityRuleResponseModel,
    SecurityRuleMoveModel,
    SecurityRuleRulebase,
)


class SecurityRule(BaseObject):
    """
    Manages Security Rule objects in Palo Alto Networks' Strata Cloud Manager.
    Args:
        api_client: The API client instance
        max_limit (Optional[int]): Maximum number of objects to return in a single API request.
            Defaults to 5000. Must be between 1 and 10000.
    """

    ENDPOINT = "/config/security/v1/security-rules"
    DEFAULT_MAX_LIMIT = 2500
    ABSOLUTE_MAX_LIMIT = 5000  # Maximum allowed by the API

    def __init__(
        self,
        api_client,
        max_limit: Optional[int] = None,
    ):
        super().__init__(api_client)
        self.logger = logging.getLogger(__name__)

        # Validate and set max_limit
        self._max_limit = self._validate_max_limit(max_limit)

    @property
    def max_limit(self) -> int:
        """Get the current maximum limit for API requests."""
        return self._max_limit

    @max_limit.setter
    def max_limit(self, value: int) -> None:
        """Set a new maximum limit for API requests."""
        self._max_limit = self._validate_max_limit(value)

    def _validate_max_limit(self, limit: Optional[int]) -> int:
        """
        Validates the max_limit parameter.

        Args:
            limit: The limit to validate

        Returns:
            int: The validated limit

        Raises:
            InvalidObjectError: If the limit is invalid
        """
        if limit is None:
            return self.DEFAULT_MAX_LIMIT

        try:
            limit_int = int(limit)
        except (TypeError, ValueError):
            raise InvalidObjectError(
                message="max_limit must be an integer",
                error_code="E003",
                http_status_code=400,
                details={"error": "Invalid max_limit type"},
            )

        if limit_int < 1:
            raise InvalidObjectError(
                message="max_limit must be greater than 0",
                error_code="E003",
                http_status_code=400,
                details={"error": "Invalid max_limit value"},
            )

        if limit_int > self.ABSOLUTE_MAX_LIMIT:
            raise InvalidObjectError(
                message=f"max_limit cannot exceed {self.ABSOLUTE_MAX_LIMIT}",
                error_code="E003",
                http_status_code=400,
                details={"error": "max_limit exceeds maximum allowed value"},
            )

        return limit_int

    def create(
        self,
        data: Dict[str, Any],
        rulebase: str = "pre",
    ) -> SecurityRuleResponseModel:
        """
        Creates a new security rule object.

        Returns:
            SecurityRuleResponseModel
        """
        # Validate that the rulebase is of type `pre` or `post`
        if not isinstance(rulebase, SecurityRuleRulebase):
            try:
                rulebase = SecurityRuleRulebase(rulebase.lower())
            except ValueError:
                raise InvalidObjectError(
                    message="rulebase must be either 'pre' or 'post'",
                    error_code="E003",
                    http_status_code=400,
                    details={"error": "Invalid rulebase value"},
                )

        # Use the dictionary "data" to pass into Pydantic and return a modeled object
        profile = SecurityRuleCreateModel(**data)

        # Create params dict to pass rulebase
        params = {"position": rulebase.value}

        # Convert back to a Python dictionary, removing any unset fields and using aliases
        payload = profile.model_dump(
            exclude_unset=True,
            by_alias=True,
        )

        # Send the updated object to the remote API as JSON, expecting a dictionary object to be returned.
        response: Dict[str, Any] = self.api_client.post(
            self.ENDPOINT,
            params=params,
            json=payload,
        )

        # Return the SCM API response as a new Pydantic object
        return SecurityRuleResponseModel(**response)

    def get(
        self,
        object_id: str,
        rulebase: str = "pre",
    ) -> SecurityRuleResponseModel:
        """
        Gets a security rule object by ID.

        Returns:
            SecurityRuleResponseModel
        """
        # Validate that the rulebase is of type `pre` or `post`
        if not isinstance(rulebase, SecurityRuleRulebase):
            try:
                SecurityRuleRulebase(rulebase.lower())
            except ValueError:
                raise InvalidObjectError(
                    message="rulebase must be either 'pre' or 'post'",
                    error_code="E003",
                    http_status_code=400,
                    details={"error": "Invalid rulebase value"},
                )

        # Send the request to the remote API
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.get(endpoint)

        # Return the SCM API response as a new Pydantic object
        return SecurityRuleResponseModel(**response)

    def update(
        self,
        rule: SecurityRuleUpdateModel,
        rulebase: str = "pre",
    ) -> SecurityRuleResponseModel:
        """
        Updates an existing security rule object.

        Args:
            rule: SecurityRuleUpdateModel instance containing the update data
            rulebase: Which rulebase to use ('pre' or 'post'), defaults to 'pre'

        Returns:
            SecurityRuleResponseModel
        """
        # Validate that the rulebase is of type `pre` or `post`
        if not isinstance(rulebase, SecurityRuleRulebase):
            try:
                rulebase = SecurityRuleRulebase(rulebase.lower())
            except ValueError:
                raise InvalidObjectError(
                    message="rulebase must be either 'pre' or 'post'",
                    error_code="E003",
                    http_status_code=400,
                    details={"error": "Invalid rulebase value"},
                )

        # Convert to dict for API request, excluding unset fields and using aliases
        payload = rule.model_dump(
            exclude_unset=True,
            by_alias=True,
        )

        # Extract ID and remove from payload since it's in the URL
        object_id = str(rule.id)
        payload.pop("id", None)

        # Send the updated object to the remote API as JSON
        endpoint = f"{self.ENDPOINT}/{object_id}"
        response: Dict[str, Any] = self.api_client.put(
            endpoint,
            params={"position": rulebase.value},
            json=payload,
        )

        # Return the SCM API response as a new Pydantic model
        return SecurityRuleResponseModel(**response)

    @staticmethod
    def _apply_filters(
        rules: List[SecurityRuleResponseModel],
        filters: Dict[str, Any],
    ) -> List[SecurityRuleResponseModel]:
        """
        Apply client-side filtering to the list of security rules.

        Args:
            rules: List of SecurityRuleResponseModel objects
            filters: Dictionary of filter criteria

        Returns:
            List[SecurityRuleResponseModel]: Filtered list of security rules
        """
        filter_criteria = rules

        # Filter by action
        if "action" in filters:
            if not isinstance(filters["action"], list):
                raise InvalidObjectError(
                    message="'action' filter must be a list",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Object"},
                )
            actions = filters["action"]
            filter_criteria = [
                rule for rule in filter_criteria if rule.action in actions
            ]

        # Filter by category
        if "category" in filters:
            if not isinstance(filters["category"], list):
                raise InvalidObjectError(
                    message="'category' filter must be a list",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Object"},
                )
            categories = filters["category"]
            filter_criteria = [
                rule
                for rule in filter_criteria
                if any(cat in rule.category for cat in categories)
            ]

        # Filter by service
        if "service" in filters:
            if not isinstance(filters["service"], list):
                raise InvalidObjectError(
                    message="'service' filter must be a list",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Object"},
                )
            services = filters["service"]
            filter_criteria = [
                rule
                for rule in filter_criteria
                if any(svc in rule.service for svc in services)
            ]

        # Filter by application
        if "application" in filters:
            if not isinstance(filters["application"], list):
                raise InvalidObjectError(
                    message="'application' filter must be a list",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Object"},
                )
            applications = filters["application"]
            filter_criteria = [
                rule
                for rule in filter_criteria
                if any(app in rule.application for app in applications)
            ]

        # Filter by destination
        if "destination" in filters:
            if not isinstance(filters["destination"], list):
                raise InvalidObjectError(
                    message="'destination' filter must be a list",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Object"},
                )
            destinations = filters["destination"]
            filter_criteria = [
                rule
                for rule in filter_criteria
                if any(dest in rule.destination for dest in destinations)
            ]

        # Filter by to_
        if "to_" in filters:
            if not isinstance(filters["to_"], list):
                raise InvalidObjectError(
                    message="'to_' filter must be a list",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Object"},
                )
            to_zones = filters["to_"]
            filter_criteria = [
                rule
                for rule in filter_criteria
                if any(zone in rule.to_ for zone in to_zones)
            ]

        # Filter by source
        if "source" in filters:
            if not isinstance(filters["source"], list):
                raise InvalidObjectError(
                    message="'source' filter must be a list",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Object"},
                )
            sources = filters["source"]
            filter_criteria = [
                rule
                for rule in filter_criteria
                if any(src in rule.source for src in sources)
            ]

        # Filter by from_
        if "from_" in filters:
            if not isinstance(filters["from_"], list):
                raise InvalidObjectError(
                    message="'from_' filter must be a list",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Object"},
                )
            from_zones = filters["from_"]
            filter_criteria = [
                rule
                for rule in filter_criteria
                if any(zone in rule.from_ for zone in from_zones)
            ]

        # Filter by tag
        if "tag" in filters:
            if not isinstance(filters["tag"], list):
                raise InvalidObjectError(
                    message="'tag' filter must be a list",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Object"},
                )
            tags = filters["tag"]
            filter_criteria = [
                rule
                for rule in filter_criteria
                if rule.tag and any(tag in rule.tag for tag in tags)
            ]

        # Filter by disabled status
        if "disabled" in filters:
            if not isinstance(filters["disabled"], bool):
                raise InvalidObjectError(
                    message="'disabled' filter must be a boolean",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Object"},
                )
            disabled = filters["disabled"]
            filter_criteria = [
                rule for rule in filter_criteria if rule.disabled == disabled
            ]

        # Filter by profile_setting group
        if "profile_setting" in filters:
            if not isinstance(filters["profile_setting"], list):
                raise InvalidObjectError(
                    message="'profile_setting' filter must be a list",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Object"},
                )
            groups = filters["profile_setting"]
            filter_criteria = [
                rule
                for rule in filter_criteria
                if rule.profile_setting
                and rule.profile_setting.group
                and any(group in rule.profile_setting.group for group in groups)
            ]

        # Filter by log_setting
        if "log_setting" in filters:
            if not isinstance(filters["log_setting"], list):
                raise InvalidObjectError(
                    message="'log_setting' filter must be a list",
                    error_code="E003",
                    http_status_code=400,
                    details={"errorType": "Invalid Object"},
                )
            log_settings = filters["log_setting"]
            filter_criteria = [
                rule for rule in filter_criteria if rule.log_setting in log_settings
            ]

        return filter_criteria

    @staticmethod
    def _build_container_params(
        folder: Optional[str],
        snippet: Optional[str],
        device: Optional[str],
    ) -> dict:
        """Builds container parameters dictionary."""
        return {
            k: v
            for k, v in {"folder": folder, "snippet": snippet, "device": device}.items()
            if v is not None
        }

    def list(
        self,
        folder: Optional[str] = None,
        snippet: Optional[str] = None,
        device: Optional[str] = None,
        rulebase: str = "pre",
        exact_match: bool = False,
        exclude_folders: Optional[List[str]] = None,
        exclude_snippets: Optional[List[str]] = None,
        exclude_devices: Optional[List[str]] = None,
        **filters,
    ) -> List[SecurityRuleResponseModel]:
        """
        Lists security rule objects with optional filtering.

        Args:
            folder: Optional folder name
            snippet: Optional snippet name
            device: Optional device name
            rulebase: Which rulebase to use ('pre' or 'post'), defaults to 'pre'
            exact_match (bool): If True, only return objects whose container
                                exactly matches the provided container parameter.
            exclude_folders (List[str], optional): List of folder names to exclude from results.
            exclude_snippets (List[str], optional): List of snippet values to exclude from results.
            exclude_devices (List[str], optional): List of device values to exclude from results.
            **filters: Additional filters including:
                - action: List[str] - Filter by actions
                - category: List[str] - Filter by categories
                - service: List[str] - Filter by services
                - application: List[str] - Filter by applications
                - destination: List[str] - Filter by destinations
                - to_: List[str] - Filter by to zones
                - source: List[str] - Filter by sources
                - from_: List[str] - Filter by from zones
                - tag: List[str] - Filter by tags
                - disabled: bool - Filter by disabled status
                - profile_setting: List[str] - Filter by profile setting groups

        Returns:
            List[SecurityRuleResponseModel]: A list of security rule objects
        """

        # Validate that the rulebase is of type `pre` or `post`
        if not isinstance(rulebase, SecurityRuleRulebase):
            try:
                rulebase = SecurityRuleRulebase(rulebase.lower())
            except ValueError:
                raise InvalidObjectError(
                    message="rulebase must be either 'pre' or 'post'",
                    error_code="E003",
                    http_status_code=400,
                    details={"error": "Invalid rulebase value"},
                )

        if folder == "":
            raise MissingQueryParameterError(
                message="Field 'folder' cannot be empty",
                error_code="E003",
                http_status_code=400,
                details={
                    "field": "folder",
                    "error": '"folder" is not allowed to be empty',
                },
            )

        container_parameters = self._build_container_params(
            folder,
            snippet,
            device,
        )

        if len(container_parameters) != 1:
            raise InvalidObjectError(
                message="Exactly one of 'folder', 'snippet', or 'device' must be provided.",
                error_code="E003",
                http_status_code=400,
                details={"error": "Invalid container parameters"},
            )

        # Pagination logic
        limit = self._max_limit
        offset = 0
        all_objects = []

        while True:
            params = container_parameters.copy()
            params["position"] = rulebase.value
            params["limit"] = limit
            params["offset"] = offset

            response = self.api_client.get(
                self.ENDPOINT,
                params=params,
            )

            if not isinstance(response, dict):
                raise InvalidObjectError(
                    message="Invalid response format: expected dictionary",
                    error_code="E003",
                    http_status_code=500,
                    details={"error": "Response is not a dictionary"},
                )

            if "data" not in response:
                raise InvalidObjectError(
                    message="Invalid response format: missing 'data' field",
                    error_code="E003",
                    http_status_code=500,
                    details={
                        "field": "data",
                        "error": '"data" field missing in the response',
                    },
                )

            if not isinstance(response["data"], list):
                raise InvalidObjectError(
                    message="Invalid response format: 'data' field must be a list",
                    error_code="E003",
                    http_status_code=500,
                    details={
                        "field": "data",
                        "error": '"data" field must be a list',
                    },
                )

            data = response["data"]
            object_instances = [SecurityRuleResponseModel(**item) for item in data]
            all_objects.extend(object_instances)

            # If we got fewer than 'limit' objects, we've reached the end
            if len(data) < limit:
                break

            offset += limit

        # Apply existing filters first
        filtered_objects = self._apply_filters(
            all_objects,
            filters,
        )

        # Determine which container key and value we are filtering on
        container_key, container_value = next(iter(container_parameters.items()))

        # If exact_match is True, filter out filtered_objects that don't match exactly
        if exact_match:
            filtered_objects = [
                each
                for each in filtered_objects
                if getattr(each, container_key) == container_value
            ]

        # Exclude folders if provided
        if exclude_folders and isinstance(exclude_folders, list):
            filtered_objects = [
                each for each in filtered_objects if each.folder not in exclude_folders
            ]

        # Exclude snippets if provided
        if exclude_snippets and isinstance(exclude_snippets, list):
            filtered_objects = [
                each
                for each in filtered_objects
                if each.snippet not in exclude_snippets
            ]

        # Exclude devices if provided
        if exclude_devices and isinstance(exclude_devices, list):
            filtered_objects = [
                each for each in filtered_objects if each.device not in exclude_devices
            ]

        return filtered_objects

    def fetch(
        self,
        name: str,
        folder: Optional[str] = None,
        snippet: Optional[str] = None,
        device: Optional[str] = None,
        rulebase: str = "pre",
    ) -> SecurityRuleResponseModel:
        """
        Fetches a single security rule by name.

        Args:
            name (str): The name of the security rule to fetch.
            folder (str, optional): The folder in which the resource is defined.
            snippet (str, optional): The snippet in which the resource is defined.
            device (str, optional): The device in which the resource is defined.
            rulebase: Which rulebase to use ('pre' or 'post'), defaults to 'pre'

        Returns:
            SecurityRuleResponseModel: The fetched security rule object as a Pydantic model.
        """
        if not name:
            raise MissingQueryParameterError(
                message="Field 'name' cannot be empty",
                error_code="E003",
                http_status_code=400,
                details={
                    "field": "name",
                    "error": '"name" is not allowed to be empty',
                },
            )

        if folder == "":
            raise MissingQueryParameterError(
                message="Field 'folder' cannot be empty",
                error_code="E003",
                http_status_code=400,
                details={
                    "field": "folder",
                    "error": '"folder" is not allowed to be empty',
                },
            )

        # Validate that the rulebase is of type `pre` or `post`
        if not isinstance(rulebase, SecurityRuleRulebase):
            try:
                rulebase = SecurityRuleRulebase(rulebase.lower())
            except ValueError:
                raise InvalidObjectError(
                    message="rulebase must be either 'pre' or 'post'",
                    error_code="E003",
                    http_status_code=400,
                    details={"error": "Invalid rulebase value"},
                )

        params = {}

        container_parameters = self._build_container_params(
            folder,
            snippet,
            device,
        )

        if len(container_parameters) != 1:
            raise InvalidObjectError(
                message="Exactly one of 'folder', 'snippet', or 'device' must be provided.",
                error_code="E003",
                http_status_code=400,
                details={
                    "error": "Exactly one of 'folder', 'snippet', or 'device' must be provided."
                },
            )

        params.update(container_parameters)
        params["position"] = rulebase.value
        params["name"] = name

        response = self.api_client.get(
            self.ENDPOINT,
            params=params,
        )

        if not isinstance(response, dict):
            raise InvalidObjectError(
                message="Invalid response format: expected dictionary",
                error_code="E003",
                http_status_code=500,
                details={"error": "Response is not a dictionary"},
            )

        if "id" in response:
            return SecurityRuleResponseModel(**response)
        else:
            raise InvalidObjectError(
                message="Invalid response format: missing 'id' field",
                error_code="E003",
                http_status_code=500,
                details={"error": "Response missing 'id' field"},
            )

    def delete(
        self,
        object_id: str,
        rulebase: str = "pre",
    ) -> None:
        """
        Deletes a security rule object.

        Args:
            object_id (str): The ID of the object to delete.
            rulebase: Which rulebase to use ('pre' or 'post'), defaults to 'pre'
        """
        # Validate that the rulebase is of type `pre` or `post`
        if not isinstance(rulebase, SecurityRuleRulebase):
            try:
                rulebase = SecurityRuleRulebase(rulebase.lower())
            except ValueError:
                raise InvalidObjectError(
                    message="rulebase must be either 'pre' or 'post'",
                    error_code="E003",
                    http_status_code=400,
                    details={"error": "Invalid rulebase value"},
                )

        endpoint = f"{self.ENDPOINT}/{object_id}"
        self.api_client.delete(
            endpoint,
            params={"position": rulebase.value},
        )

    def move(
        self,
        rule_id: UUID,
        data: Dict[str, Any],
    ) -> None:
        """
        Move a security rule to a new position within the rulebase.

        Args:
            rule_id (UUID): The UUID of the rule to move
            data (Dict[str, Any]): Dictionary containing move parameters:
                - destination: Where to move the rule ('top', 'bottom', 'before', 'after')
                - rulebase: Which rulebase to use ('pre', 'post')
                - destination_rule: UUID of reference rule (required for 'before'/'after')
        """
        rule_id_str = str(rule_id)
        move_config = SecurityRuleMoveModel(**data)
        payload = move_config.model_dump(exclude_none=True)

        endpoint = f"{self.ENDPOINT}/{rule_id_str}:move"
        self.api_client.post(
            endpoint,
            json=payload,
        )
