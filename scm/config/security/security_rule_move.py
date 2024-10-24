# scm/config/security/security_rule_move.py

from typing import Dict, Any
from scm.config import BaseObject
from scm.models.security import SecurityRuleMoveModel


class SecurityRuleMove(BaseObject):
    """
    Manages Security Rule movement operations in Palo Alto Networks' Strata Cloud Manager.

    This class provides methods to move security rules within their rulebase, supporting
    operations such as moving to top/bottom or before/after other rules.

    Attributes:
        ENDPOINT (str): The base API endpoint for Security Rule operations.

    Example:
        >>> rule_move = SecurityRuleMoveModel(api_client)
        >>> rule_move.move({
        ...     "source_rule": "123e4567-e89b-12d3-a456-426655440000",
        ...     "destination": "before",
        ...     "rulebase": "pre",
        ...     "destination_rule": "987fcdeb-51d3-a456-426655440000"
        ... })
    """

    ENDPOINT = "/config/security/v1/security-rules"

    def __init__(self, api_client):
        super().__init__(api_client)

    def move(self, data: Dict[str, Any]) -> None:
        """
        Move a security rule to a new position within the rulebase.

        Args:
            data (Dict[str, Any]): Dictionary containing move parameters:
                - source_rule: UUID of the rule to move
                - destination: Where to move the rule ('top', 'bottom', 'before', 'after')
                - rulebase: Which rulebase to use ('pre', 'post')
                - destination_rule: UUID of reference rule (required for 'before'/'after')

        Raises:
            ValidationError: If the move parameters are invalid.
            ValueError: If the provided data doesn't match the expected schema.

        Returns:
            None
        """
        # Validate the input data using the Pydantic model
        move_config = SecurityRuleMoveModel(**data)

        # Extract the source_rule for the URL and remove it from the payload
        source_rule = move_config.source_rule
        payload = move_config.model_dump(exclude={"source_rule"}, exclude_none=True)

        # Construct the endpoint URL
        endpoint = f"{self.ENDPOINT}/{source_rule}:move"

        # Make the API call
        self.api_client.post(endpoint, json=payload)
