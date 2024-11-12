# scm/config/security/security_rule.py

from typing import List, Dict, Any, Optional
from scm.config import BaseObject
from scm.models.security import (
    SecurityRuleCreateModel,
    SecurityRuleUpdateModel,
    SecurityRuleResponseModel,
    SecurityRuleMoveModel,
    Rulebase,
)
from scm.exceptions import (
    ValidationError,
    EmptyFieldError,
    ErrorHandler,
    BadResponseError,
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
            # Validate rulebase using the enum
            if not isinstance(rulebase, Rulebase):
                try:
                    rulebase = Rulebase(rulebase.lower())
                except ValueError:
                    raise ValueError("rulebase must be either 'pre' or 'post'")

            # Use the dictionary "data" to pass into Pydantic and return a modeled object
            profile = SecurityRuleCreateModel(**data)

            # Convert back to a Python dictionary, but removing any excluded object
            # Note: by_alias=True is crucial for correct handling of from_/to_ fields
            payload = profile.model_dump(
                exclude_unset=True,
                by_alias=True,
            )

            # Send the updated object to the remote API as JSON
            response = self.api_client.post(
                self.ENDPOINT,
                params={"position": rulebase.value},
                json=payload,
            )

            # Return the SCM API response as a new Pydantic object
            return SecurityRuleResponseModel(**response)

        # Forward exceptions to our custom ErrorHandler object
        except Exception as e:
            if hasattr(e, "response") and e.response is not None:  # noqa
                ErrorHandler.raise_for_error(e.response.json())
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
            # Validate rulebase using the enum
            if not isinstance(rulebase, Rulebase):
                try:
                    rulebase = Rulebase(rulebase.lower())
                except ValueError:
                    raise ValueError("rulebase must be either 'pre' or 'post'")

            # Send the request to the remote API
            endpoint = f"{self.ENDPOINT}/{object_id}"
            response = self.api_client.get(
                endpoint,
                params={"position": rulebase.value},
            )

            # Return the SCM API response as a new Pydantic object
            return SecurityRuleResponseModel(**response)

        # Forward exceptions to our custom ErrorHandler object
        except Exception as e:
            if hasattr(e, "response") and e.response is not None:  # noqa
                ErrorHandler.raise_for_error(e.response.json())
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
            # Validate rulebase using the enum
            if not isinstance(rulebase, Rulebase):
                try:
                    rulebase = Rulebase(rulebase.lower())
                except ValueError:
                    raise ValueError("rulebase must be either 'pre' or 'post'")

            # Use the dictionary "data" to pass into Pydantic and return a modeled object
            profile = SecurityRuleUpdateModel(**data)

            # Convert back to a Python dictionary, but removing any excluded object
            # Note: by_alias=True is crucial for correct handling of from_/to_ fields
            payload = profile.model_dump(
                exclude_unset=True,
                by_alias=True,
            )

            # Send the updated object to the remote API as JSON
            endpoint = f"{self.ENDPOINT}/{data['id']}"
            response = self.api_client.put(
                endpoint,
                params={"position": rulebase.value},
                json=payload,
            )

            # Return the SCM API response as a new Pydantic object
            return SecurityRuleResponseModel(**response)

        # Forward exceptions to our custom ErrorHandler object
        except Exception as e:
            if hasattr(e, "response") and e.response is not None:  # noqa
                ErrorHandler.raise_for_error(e.response.json())
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
        """
        # Build a list of what criteria we are looking to filter our response from
        filter_criteria = rules

        # Filter by action
        if "action" in filters:
            if not isinstance(filters["action"], list):
                raise ValidationError("'action' filter must be a list")
            actions = filters["action"]
            filter_criteria = [
                rule for rule in filter_criteria if rule.action in actions
            ]

        # Filter by category
        if "category" in filters:
            if not isinstance(filters["category"], list):
                raise ValidationError("'category' filter must be a list")
            categories = filters["category"]
            filter_criteria = [
                rule
                for rule in filter_criteria
                if any(cat in rule.category for cat in categories)
            ]

        # Filter by service
        if "service" in filters:
            if not isinstance(filters["service"], list):
                raise ValidationError("'service' filter must be a list")
            services = filters["service"]
            filter_criteria = [
                rule
                for rule in filter_criteria
                if any(svc in rule.service for svc in services)
            ]

        # Filter by application
        if "application" in filters:
            if not isinstance(filters["application"], list):
                raise ValidationError("'application' filter must be a list")
            applications = filters["application"]
            filter_criteria = [
                rule
                for rule in filter_criteria
                if any(app in rule.application for app in applications)
            ]

        # Filter by destination
        if "destination" in filters:
            if not isinstance(filters["destination"], list):
                raise ValidationError("'destination' filter must be a list")
            destinations = filters["destination"]
            filter_criteria = [
                rule
                for rule in filter_criteria
                if any(dest in rule.destination for dest in destinations)
            ]

        # Filter by to_
        if "to_" in filters:
            if not isinstance(filters["to_"], list):
                raise ValidationError("'to_' filter must be a list")
            to_zones = filters["to_"]
            filter_criteria = [
                rule
                for rule in filter_criteria
                if any(zone in rule.to_ for zone in to_zones)
            ]

        # Filter by source
        if "source" in filters:
            if not isinstance(filters["source"], list):
                raise ValidationError("'source' filter must be a list")
            sources = filters["source"]
            filter_criteria = [
                rule
                for rule in filter_criteria
                if any(src in rule.source for src in sources)
            ]

        # Filter by from_
        if "from_" in filters:
            if not isinstance(filters["from_"], list):
                raise ValidationError("'from_' filter must be a list")
            from_zones = filters["from_"]
            filter_criteria = [
                rule
                for rule in filter_criteria
                if any(zone in rule.from_ for zone in from_zones)
            ]

        # Filter by tag
        if "tag" in filters:
            if not isinstance(filters["tag"], list):
                raise ValidationError("'tag' filter must be a list")
            tags = filters["tag"]
            filter_criteria = [
                rule
                for rule in filter_criteria
                if rule.tag and any(tag in rule.tag for tag in tags)
            ]

        # Filter by disabled status
        if "disabled" in filters:
            if not isinstance(filters["disabled"], bool):
                raise ValidationError("'disabled' filter must be a boolean")
            disabled = filters["disabled"]
            filter_criteria = [
                rule for rule in filter_criteria if rule.disabled == disabled
            ]

        # Filter by profile_setting group
        if "profile_setting" in filters:
            if not isinstance(filters["profile_setting"], list):
                raise ValidationError("'profile_setting' filter must be a list")
            groups = filters["profile_setting"]
            filter_criteria = [
                rule
                for rule in filter_criteria
                if rule.profile_setting
                and rule.profile_setting.group
                and any(group in rule.profile_setting.group for group in groups)
            ]

        return filter_criteria

    @staticmethod
    def _build_container_params(
        folder: Optional[str],
        snippet: Optional[str],
        device: Optional[str],
    ) -> dict:
        """Builds container parameters dictionary."""
        # Only return a key of "folder", "snippet", or "device" if their value is not None
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
            EmptyFieldError: If provided container fields are empty
            FolderNotFoundError: If the specified folder doesn't exist
            ValidationError: If the container parameters are invalid
            BadResponseError: If response format is invalid
        """
        # If the folder object is empty, raise exception
        if folder == "":
            raise EmptyFieldError(
                message="Field 'folder' cannot be empty",
                error_code="API_I00035",
                details=['"folder" is not allowed to be empty'],  # noqa
            )

        # Validate rulebase using the enum
        if not isinstance(rulebase, Rulebase):
            try:
                rulebase = Rulebase(rulebase.lower())
            except ValueError:
                raise ValueError("rulebase must be either 'pre' or 'post'")

        # Set the parameters, starting with a high limit for more than the default 200
        params = {
            "limit": self.DEFAULT_LIMIT,
            "position": rulebase.value,
        }

        # Build the configuration container object (folder, snippet, or device)
        container_parameters = self._build_container_params(
            folder,
            snippet,
            device,
        )

        # Ensure that we have only a single instance of "folder", "device", or "snippet"
        if len(container_parameters) != 1:
            raise ValidationError(
                "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            )

        # Add the resulting container object to our parameters
        params.update(container_parameters)

        # Perform our request
        try:
            response = self.api_client.get(
                self.ENDPOINT,
                params=params,
            )

            # return errors if invalid structure
            if not isinstance(response, dict):
                raise BadResponseError("Invalid response format: expected dictionary")

            if "data" not in response:
                raise BadResponseError("Invalid response format: missing 'data' field")

            if not isinstance(response["data"], list):
                raise BadResponseError(
                    "Invalid response format: 'data' field must be a list"
                )

            # Return a list object of the entries as Pydantic modeled objects
            rules = [SecurityRuleResponseModel(**item) for item in response["data"]]

            # Apply client-side filtering
            return self._apply_filters(rules, filters)

        # Forward exceptions to our custom ErrorHandler object
        except Exception as e:
            if hasattr(e, "response") and e.response is not None:  # noqa
                ErrorHandler.raise_for_error(e.response.json())
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
            EmptyFieldError: If name or container fields are empty
            FolderNotFoundError: If the specified folder doesn't exist
            ObjectNotPresentError: If the object is not found
            ValidationError: If the parameters are invalid
            BadResponseError: For other API-related errors
        """
        if not name:
            raise EmptyFieldError(
                message="Field 'name' cannot be empty",
                error_code="API_I00035",
                details=['"name" is not allowed to be empty'],  # noqa
            )

        if folder == "":
            raise EmptyFieldError(
                message="Field 'folder' cannot be empty",
                error_code="API_I00035",
                details=['"folder" is not allowed to be empty'],  # noqa
            )

        # Validate rulebase using the enum
        if not isinstance(rulebase, Rulebase):
            try:
                rulebase = Rulebase(rulebase.lower())
            except ValueError:
                raise ValueError("rulebase must be either 'pre' or 'post'")

        # Build the configuration container object (folder, snippet, or device)
        container_parameters = self._build_container_params(
            folder,
            snippet,
            device,
        )

        # Ensure that we have only a single instance of "folder", "device", or "snippet"
        if len(container_parameters) != 1:
            raise ValidationError(
                "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            )

        # Start with container parameters and add position
        params = {
            **container_parameters,
            "position": rulebase.value,
            "name": name,
        }

        # Add name parameter

        try:
            response = self.api_client.get(
                self.ENDPOINT,
                params=params,
            )

            # return errors if invalid structure
            if not isinstance(response, dict):
                raise BadResponseError("Invalid response format: expected dictionary")

            # If the response has a key of "_errors", pass to our custom error handler
            if "_errors" in response:
                ErrorHandler.raise_for_error(response)

            # If the response has a key of "id"
            elif "id" in response:
                # Create a new object by passing the response through our Pydantic model
                rule = SecurityRuleResponseModel(**response)

                # Return an instance of the object as a Python dictionary
                return rule.model_dump(
                    exclude_unset=True,
                    exclude_none=True,
                )

            else:
                raise BadResponseError("Invalid response format: missing 'id' field")

        # Forward exceptions to our custom ErrorHandler object
        except Exception as e:
            if hasattr(e, "response") and e.response is not None:  # noqa
                ErrorHandler.raise_for_error(e.response.json())
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
            MalformedRequestError: If the request is malformed
        """
        try:
            # Validate rulebase using the enum
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

        # Forward exceptions to our custom ErrorHandler object
        except Exception as e:
            if hasattr(e, "response") and e.response is not None:  # noqa
                ErrorHandler.raise_for_error(e.response.json())
            raise

    def move(
        self,
        rule_id: str,
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
            ValidationError: If the move parameters are invalid
            ObjectNotPresentError: If the referenced rules don't exist
            MalformedRequestError: If the request is malformed
        """
        try:
            rule_id_str = str(rule_id)
            # Create move configuration with the provided rule_id and data
            move_config = SecurityRuleMoveModel(
                source_rule=rule_id,
                **data,
            )

            # Convert to dict for API request, excluding None values
            payload = move_config.model_dump(exclude_none=True)
            payload["source_rule"] = rule_id_str

            # Make the API call
            endpoint = f"{self.ENDPOINT}/{rule_id_str}:move"
            self.api_client.post(
                endpoint,
                json=payload,
            )

        # Forward exceptions to our custom ErrorHandler object
        except Exception as e:
            if hasattr(e, "response") and e.response is not None:  # noqa
                ErrorHandler.raise_for_error(e.response.json())
            raise
