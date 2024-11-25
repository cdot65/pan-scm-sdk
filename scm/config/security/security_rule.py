# scm/config/security/security_rule.py

# Standard library imports
import logging
from typing import List, Dict, Any, Optional
from uuid import UUID

# External libraries
from requests import Response
from requests.exceptions import HTTPError

# Local SDK imports
from scm.config import BaseObject
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
    ErrorHandler,
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
    """

    ENDPOINT = "/config/security/v1/security-rules"
    DEFAULT_LIMIT = 10000

    def __init__(
        self,
        api_client,
    ):
        super().__init__(api_client)
        self.logger = logging.getLogger(__name__)

    def create(
        self,
        data: Dict[str, Any],
        rulebase: str = "pre",
    ) -> SecurityRuleResponseModel:
        """
        Creates a new security rule object.

        Returns:
            SecurityRuleResponseModel

        Raises:
            Custom Error Handling class response
        """
        try:
            # Validate that the rulebase is of type `pre` or `post`
            if not isinstance(rulebase, SecurityRuleRulebase):
                try:
                    SecurityRuleRulebase(rulebase.lower())
                except ValueError:
                    raise InvalidObjectError("rulebase must be either 'pre' or 'post'")

            # Use the dictionary "data" to pass into Pydantic and return a modeled object
            profile = SecurityRuleCreateModel(**data)

            # Convert back to a Python dictionary, removing any unset fields and using aliases
            payload = profile.model_dump(
                exclude_unset=True,
                by_alias=True,
            )

            # Send the updated object to the remote API as JSON, expecting a dictionary object to be returned.
            response: Dict[str, Any] = self.api_client.post(
                self.ENDPOINT,
                json=payload,
            )

            # Return the SCM API response as a new Pydantic object
            return SecurityRuleResponseModel(**response)

        except HTTPError as e:
            # create an object of the type Response and store the contents of e.response within it
            response: Optional[Response] = e.response

            # if the response is not none, and there is data within response.content
            if response is not None and response.content:

                # Perform our custom exception handler by sending the response.json() object and http status code
                ErrorHandler.raise_for_error(
                    response.json(),
                    response.status_code,
                )
            else:
                self.logger.error("No response content available for error parsing.")
                raise

    def get(
        self,
        object_id: str,
        rulebase: str = "pre",
    ) -> SecurityRuleResponseModel:
        """
        Gets a security rule object by ID.

        Returns:
            SecurityRuleResponseModel

        Raises:
            Custom Error Handling class response
        """
        try:
            # Validate that the rulebase is of type `pre` or `post`
            if not isinstance(rulebase, SecurityRuleRulebase):
                try:
                    SecurityRuleRulebase(rulebase.lower())
                except ValueError:
                    raise InvalidObjectError("rulebase must be either 'pre' or 'post'")

            # Send the request to the remote API
            endpoint = f"{self.ENDPOINT}/{object_id}"
            response: Dict[str, Any] = self.api_client.get(endpoint)

            # Return the SCM API response as a new Pydantic object
            return SecurityRuleResponseModel(**response)

        except HTTPError as e:
            # create an object of the type Response and store the contents of e.response within it
            response: Optional[Response] = e.response

            # if the response is not none, and there is data within response.content
            if response is not None and response.content:

                # Perform our custom exception handler by sending the response.json() object and http status code
                ErrorHandler.raise_for_error(
                    response.json(),
                    response.status_code,
                )
            else:
                self.logger.error("No response content available for error parsing.")
                raise

    def update(
        self,
        data: Dict[str, Any],
        rulebase: str = "pre",
    ) -> SecurityRuleResponseModel:
        """
        Updates an existing security rule object.

        Returns:
            SecurityRuleResponseModel

        Raises:
            Custom Error Handling class response
        """
        try:
            # Validate that the rulebase is of type `pre` or `post`
            if not isinstance(rulebase, SecurityRuleRulebase):
                try:
                    rulebase = SecurityRuleRulebase(rulebase.lower())
                except ValueError:
                    raise InvalidObjectError("rulebase must be either 'pre' or 'post'")

            # Use the dictionary "data" to pass into Pydantic and return a modeled object
            profile = SecurityRuleUpdateModel(**data)

            # Convert back to a Python dictionary, removing any unset fields and using aliases
            payload = profile.model_dump(
                exclude_unset=True,
                by_alias=True,
            )

            # Send the updated object to the remote API as JSON
            endpoint = f"{self.ENDPOINT}/{data['id']}"
            response: Dict[str, Any] = self.api_client.put(
                endpoint,
                params={"position": rulebase.value},
                json=payload,
            )

            # Return the SCM API response as a new Pydantic object
            return SecurityRuleResponseModel(**response)

        except HTTPError as e:
            # create an object of the type Response and store the contents of e.response within it
            response: Optional[Response] = e.response

            # if the response is not none, and there is data within response.content
            if response is not None and response.content:

                # Perform our custom exception handler by sending the response.json() object and http status code
                ErrorHandler.raise_for_error(
                    response.json(),
                    response.status_code,
                )
            else:
                self.logger.error("No response content available for error parsing.")
                raise

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

        Raises:
            InvalidObjectError: If filter criteria are invalid
        """

        filter_criteria = rules

        # Filter by action
        if "action" in filters:
            if not isinstance(filters["action"], list):
                raise InvalidObjectError("'action' filter must be a list")
            actions = filters["action"]
            filter_criteria = [
                rule for rule in filter_criteria if rule.action in actions
            ]

        # Filter by category
        if "category" in filters:
            if not isinstance(filters["category"], list):
                raise InvalidObjectError("'category' filter must be a list")
            categories = filters["category"]
            filter_criteria = [
                rule
                for rule in filter_criteria
                if any(cat in rule.category for cat in categories)
            ]

        # Filter by service
        if "service" in filters:
            if not isinstance(filters["service"], list):
                raise InvalidObjectError("'service' filter must be a list")
            services = filters["service"]
            filter_criteria = [
                rule
                for rule in filter_criteria
                if any(svc in rule.service for svc in services)
            ]

        # Filter by application
        if "application" in filters:
            if not isinstance(filters["application"], list):
                raise InvalidObjectError("'application' filter must be a list")
            applications = filters["application"]
            filter_criteria = [
                rule
                for rule in filter_criteria
                if any(app in rule.application for app in applications)
            ]

        # Filter by destination
        if "destination" in filters:
            if not isinstance(filters["destination"], list):
                raise InvalidObjectError("'destination' filter must be a list")
            destinations = filters["destination"]
            filter_criteria = [
                rule
                for rule in filter_criteria
                if any(dest in rule.destination for dest in destinations)
            ]

        # Filter by to_
        if "to_" in filters:
            if not isinstance(filters["to_"], list):
                raise InvalidObjectError("'to_' filter must be a list")
            to_zones = filters["to_"]
            filter_criteria = [
                rule
                for rule in filter_criteria
                if any(zone in rule.to_ for zone in to_zones)
            ]

        # Filter by source
        if "source" in filters:
            if not isinstance(filters["source"], list):
                raise InvalidObjectError("'source' filter must be a list")
            sources = filters["source"]
            filter_criteria = [
                rule
                for rule in filter_criteria
                if any(src in rule.source for src in sources)
            ]

        # Filter by from_
        if "from_" in filters:
            if not isinstance(filters["from_"], list):
                raise InvalidObjectError("'from_' filter must be a list")
            from_zones = filters["from_"]
            filter_criteria = [
                rule
                for rule in filter_criteria
                if any(zone in rule.from_ for zone in from_zones)
            ]

        # Filter by tag
        if "tag" in filters:
            if not isinstance(filters["tag"], list):
                raise InvalidObjectError("'tag' filter must be a list")
            tags = filters["tag"]
            filter_criteria = [
                rule
                for rule in filter_criteria
                if rule.tag and any(tag in rule.tag for tag in tags)
            ]

        # Filter by disabled status
        if "disabled" in filters:
            if not isinstance(filters["disabled"], bool):
                raise InvalidObjectError("'disabled' filter must be a boolean")
            disabled = filters["disabled"]
            filter_criteria = [
                rule for rule in filter_criteria if rule.disabled == disabled
            ]

        # Filter by profile_setting group
        if "profile_setting" in filters:
            if not isinstance(filters["profile_setting"], list):
                raise InvalidObjectError("'profile_setting' filter must be a list")
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
                raise InvalidObjectError("'log_setting' filter must be a list")
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
        **filters,
    ) -> List[SecurityRuleResponseModel]:
        """
        Lists security rule objects with optional filtering.

        Args:
            folder: Optional folder name
            snippet: Optional snippet name
            device: Optional device name
            rulebase: Which rulebase to use ('pre' or 'post'), defaults to 'pre'
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

        Raises:
            MissingQueryParameterError: If provided container fields are empty
            InvalidObjectError: If the container parameters are invalid
            APIError: If response format is invalid
        """
        if folder == "":
            raise MissingQueryParameterError(
                message="Field 'folder' cannot be empty",
                error_code="E003",
                http_status_code=400,
                details=['"folder" is not allowed to be empty'],  # noqa
            )

        # Validate that the rulebase is of type `pre` or `post`
        if not isinstance(rulebase, SecurityRuleRulebase):
            try:
                rulebase = SecurityRuleRulebase(rulebase.lower())
            except ValueError:
                raise InvalidObjectError("rulebase must be either 'pre' or 'post'")

        params = {
            "limit": self.DEFAULT_LIMIT,
            "position": rulebase.value,
        }

        container_parameters = self._build_container_params(
            folder,
            snippet,
            device,
        )

        if len(container_parameters) != 1:
            raise InvalidObjectError(
                "Exactly one of 'folder', 'snippet', or 'device' must be provided.",
                error_code="E003",
                http_status_code=400,
            )

        params.update(container_parameters)

        try:
            response = self.api_client.get(
                self.ENDPOINT,
                params=params,
            )

            if not isinstance(response, dict):
                raise InvalidObjectError(
                    "Invalid response format: expected dictionary",
                    error_code="E003",
                    http_status_code=500,
                )

            if "data" not in response:
                raise InvalidObjectError(
                    "Invalid response format: missing 'data' field",
                    error_code="E003",
                    http_status_code=500,
                )

            if not isinstance(response["data"], list):
                raise InvalidObjectError(
                    "Invalid response format: 'data' field must be a list",
                    error_code="E003",
                    http_status_code=500,
                )

            rules = [SecurityRuleResponseModel(**item) for item in response["data"]]

            return self._apply_filters(
                rules,
                filters,
            )

        except HTTPError as e:
            # create an object of the type Response and store the contents of e.response within it
            response: Optional[Response] = e.response

            # if the response is not none, and there is data within response.content
            if response is not None and response.content:

                # Perform our custom exception handler by sending the response.json() object and http status code
                ErrorHandler.raise_for_error(
                    response.json(),
                    response.status_code,
                )
            else:
                self.logger.error("No response content available for error parsing.")
                raise

    def fetch(
        self,
        name: str,
        folder: Optional[str] = None,
        snippet: Optional[str] = None,
        device: Optional[str] = None,
        rulebase: str = "pre",
    ) -> Dict[str, Any]:
        """
        Fetches a single security rule by name.

        Args:
            name (str): The name of the security rule to fetch.
            folder (str, optional): The folder in which the resource is defined.
            snippet (str, optional): The snippet in which the resource is defined.
            device (str, optional): The device in which the resource is defined.
            rulebase: Which rulebase to use ('pre' or 'post'), defaults to 'pre'

        Returns:
            Dict: The fetched object.

        Raises:
            MissingQueryParameterError: If name or container fields are empty
            InvalidObjectError: If the parameters are invalid
            APIError: For other API-related errors
        """
        if not name:
            raise MissingQueryParameterError(
                message="Field 'name' cannot be empty",
                error_code="E003",
                http_status_code=400,
                details=['"name" is not allowed to be empty'],  # noqa
            )

        if folder == "":
            raise MissingQueryParameterError(
                message="Field 'folder' cannot be empty",
                error_code="E003",
                http_status_code=400,
                details=['"folder" is not allowed to be empty'],  # noqa
            )

        # Validate that the rulebase is of type `pre` or `post`
        if not isinstance(rulebase, SecurityRuleRulebase):
            try:
                rulebase = SecurityRuleRulebase(rulebase.lower())
            except ValueError:
                raise InvalidObjectError("rulebase must be either 'pre' or 'post'")

        params = {}

        container_parameters = self._build_container_params(
            folder,
            snippet,
            device,
        )

        if len(container_parameters) != 1:
            raise InvalidObjectError(
                "Exactly one of 'folder', 'snippet', or 'device' must be provided.",
                error_code="E003",
                http_status_code=400,
            )

        params.update(container_parameters)
        params["position"] = rulebase.value
        params["name"] = name

        try:
            response = self.api_client.get(
                self.ENDPOINT,
                params=params,
            )

            if not isinstance(response, dict):
                raise InvalidObjectError(
                    "Invalid response format: expected dictionary",
                    error_code="E003",
                    http_status_code=500,
                )

            if "id" in response:
                address = SecurityRuleResponseModel(**response)
                return address.model_dump(
                    exclude_unset=True,
                    exclude_none=True,
                )
            else:
                raise InvalidObjectError(
                    "Invalid response format: missing 'id' field",
                    error_code="E003",
                    http_status_code=500,
                )

        except HTTPError as e:
            # create an object of the type Response and store the contents of e.response within it
            response: Optional[Response] = e.response

            # if the response is not none, and there is data within response.content
            if response is not None and response.content:

                # Perform our custom exception handler by sending the response.json() object and http status code
                ErrorHandler.raise_for_error(
                    response.json(),
                    response.status_code,
                )
            else:
                self.logger.error("No response content available for error parsing.")
                raise

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

        Raises:
            ObjectNotPresentError: If the object doesn't exist
            ReferenceNotZeroError: If the object is still referenced by other objects
            MalformedCommandError: If the request is malformed
        """
        try:
            # Validate that the rulebase is of type `pre` or `post`
            if not isinstance(rulebase, SecurityRuleRulebase):
                try:
                    rulebase = SecurityRuleRulebase(rulebase.lower())
                except ValueError:
                    raise InvalidObjectError("rulebase must be either 'pre' or 'post'")

            endpoint = f"{self.ENDPOINT}/{object_id}"
            self.api_client.delete(
                endpoint,
                params={"position": rulebase.value},
            )

        except HTTPError as e:
            # create an object of the type Response and store the contents of e.response within it
            response: Optional[Response] = e.response

            # if the response is not none, and there is data within response.content
            if response is not None and response.content:

                # Perform our custom exception handler by sending the response.json() object and http status code
                ErrorHandler.raise_for_error(
                    response.json(),
                    response.status_code,
                )
            else:
                self.logger.error("No response content available for error parsing.")
                raise

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

        Raises:
            InvalidObjectError: If the move parameters are invalid
            ObjectNotPresentError: If the referenced rules don't exist
            MalformedCommandError: If the request is malformed
        """
        try:
            rule_id_str = str(rule_id)
            move_config = SecurityRuleMoveModel(**data)
            payload = move_config.model_dump(exclude_none=True)

            endpoint = f"{self.ENDPOINT}/{rule_id_str}:move"
            self.api_client.post(
                endpoint,
                json=payload,
            )

        except HTTPError as e:
            # create an object of the type Response and store the contents of e.response within it
            response: Optional[Response] = e.response

            # if the response is not none, and there is data within response.content
            if response is not None and response.content:

                # Perform our custom exception handler by sending the response.json() object and http status code
                ErrorHandler.raise_for_error(
                    response.json(),
                    response.status_code,
                )
            else:
                self.logger.error("No response content available for error parsing.")
                raise
