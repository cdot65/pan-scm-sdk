# scm/models/security/security_rule_move.py

from enum import Enum
from typing import Optional
from uuid import UUID
from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
    ConfigDict,
)


class Destination(str, Enum):
    """
    Enum representing valid destination values for rule movement.

    Attributes:
        TOP: Move rule to the top of the rulebase
        BOTTOM: Move rule to the bottom of the rulebase
        BEFORE: Move rule before a specified rule
        AFTER: Move rule after a specified rule
    """

    TOP = "top"
    BOTTOM = "bottom"
    BEFORE = "before"
    AFTER = "after"


class Rulebase(str, Enum):
    """
    Enum representing valid rulebase values.

    Attributes:
        PRE: Pre-rulebase
        POST: Post-rulebase
    """

    PRE = "pre"
    POST = "post"


class SecurityRuleMoveModel(BaseModel):
    """
    Model representing a rule-based move operation.

    This model defines the parameters required to move a security rule
    within a rulebase. It supports moving rules to specific positions
    (top/bottom) or relative to other rules (before/after).

    Attributes:
        source_rule (str): UUID of the security rule to be moved
        destination (Destination): Where to move the rule
        rulebase (Rulebase): Which rulebase to use (pre or post)
        destination_rule (Optional[str]): UUID of the reference rule
            Required only when destination is 'before' or 'after'

    Raises:
        ValueError: If destination_rule is missing when required or
                   if provided destination_rule is not a valid UUID
    """

    source_rule: str = Field(
        ...,
        description="UUID of the security rule to be moved",
    )
    destination: Destination = Field(
        ...,
        description="A destination of the rule. Valid destination values are "
        "top, bottom, before and after.",
    )
    rulebase: Rulebase = Field(
        ..., description="A base of a rule. Valid rulebase values are pre and post."
    )
    destination_rule: Optional[str] = Field(
        None,
        description="A destination_rule attribute is required only if the "
        "destination value is before or after. Valid destination_rule "
        "values are existing rule UUIDs within the same container.",
    )

    model_config = ConfigDict(validate_assignment=True, arbitrary_types_allowed=True)

    @field_validator("source_rule", "destination_rule")
    def validate_uuid_fields(cls, v: Optional[str]) -> Optional[str]:
        """Validates that UUID fields contain valid UUIDs when provided."""
        if v is not None:
            try:
                UUID(v)
            except ValueError:
                raise ValueError("Field must be a valid UUID")
        return v

    @model_validator(mode="after")
    def validate_destination_rule_requirement(self) -> "SecurityRuleMoveModel":
        """
        Validates that destination_rule is provided when required.

        The destination_rule field is required when destination is
        either 'before' or 'after', and must not be provided when
        destination is 'top' or 'bottom'.
        """
        dest = self.destination
        dest_rule = self.destination_rule

        if dest in (Destination.BEFORE, Destination.AFTER):
            if not dest_rule:
                raise ValueError(
                    "destination_rule is required when destination is "
                    f"'{dest.value}'"
                )
        elif dest_rule is not None:
            raise ValueError(
                "destination_rule should not be provided when destination "
                f"is '{dest.value}'"
            )

        return self
