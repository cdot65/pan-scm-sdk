"""QoS Rule models for Strata Cloud Manager SDK.

Contains Pydantic models for representing QoS policy rule objects and related data.
"""

from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class QosMoveDestination(str, Enum):
    """Valid destination values for QoS rule movement."""

    TOP = "top"
    BOTTOM = "bottom"
    BEFORE = "before"
    AFTER = "after"


class QosRulebase(str, Enum):
    """Valid rulebase values for QoS rules."""

    PRE = "pre"
    POST = "post"


# --- Main Models ---


class QosRuleBaseModel(BaseModel):
    """Base model for QoS Rules."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    name: str = Field(
        ...,
        description="QoS rule name",
    )
    description: Optional[str] = Field(
        None,
        description="Description of the QoS rule",
    )
    action: Optional[Dict[str, Any]] = Field(
        None,
        description="QoS action configuration with 'class' field referencing a QoS profile class",
    )
    schedule: Optional[str] = Field(
        None,
        description="Schedule for the QoS rule",
    )
    dscp_tos: Optional[Dict[str, Any]] = Field(
        None,
        description="DSCP/TOS codepoint settings",
    )

    # Container fields
    folder: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The folder in which the resource is defined",
    )
    snippet: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The snippet in which the resource is defined",
    )
    device: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The device in which the resource is defined",
    )


class QosRuleCreateModel(QosRuleBaseModel):
    """Model for creating new QoS Rules.

    Note: While this model exists for completeness, the QoS Rule service
    does not expose a create() method per the v0.10.0 specification.
    """

    @model_validator(mode="after")
    def validate_container_type(self) -> "QosRuleCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            QosRuleCreateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = ["folder", "snippet", "device"]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class QosRuleUpdateModel(QosRuleBaseModel):
    """Model for updating QoS Rules."""

    id: UUID = Field(
        ...,
        description="The UUID of the QoS rule",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class QosRuleResponseModel(QosRuleBaseModel):
    """Model for QoS Rule responses."""

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    id: UUID = Field(
        ...,
        description="The UUID of the QoS rule",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class QosRuleMoveModel(BaseModel):
    """Model for QoS rule move operations.

    Follows the same pattern as NatRuleMoveModel and SecurityRuleMoveModel.
    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    destination: QosMoveDestination = Field(
        ...,
        description="Where to move the rule (top, bottom, before, after)",
    )
    rulebase: QosRulebase = Field(
        ...,
        description="Which rulebase to use (pre or post)",
    )
    destination_rule: Optional[UUID] = Field(
        None,
        description="UUID of the reference rule for before/after moves",
    )

    @model_validator(mode="after")
    def validate_move_configuration(self) -> "QosRuleMoveModel":
        """Validate move configuration for QoS rule reordering.

        Ensures that destination_rule is provided only when destination is BEFORE or AFTER.

        Returns:
            QosRuleMoveModel: The validated model instance.

        Raises:
            ValueError: If destination_rule is missing or present in an invalid context.

        """
        if self.destination in (QosMoveDestination.BEFORE, QosMoveDestination.AFTER):
            if not self.destination_rule:
                raise ValueError(
                    f"destination_rule is required when destination is '{self.destination.value}'"
                )
        else:
            if self.destination_rule is not None:
                raise ValueError(
                    f"destination_rule should not be provided when destination is '{self.destination.value}'"
                )
        return self
