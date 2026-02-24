"""App Override Rules security models for Strata Cloud Manager SDK.

Contains Pydantic models for representing app override rule objects and related data.
"""

# scm/models/security/app_override_rules.py

from enum import Enum
from typing import Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# Enums
class AppOverrideRuleMoveDestination(str, Enum):
    """Enum representing valid destination values for rule movement."""

    TOP = "top"
    BOTTOM = "bottom"
    BEFORE = "before"
    AFTER = "after"


class AppOverrideRuleRulebase(str, Enum):
    """Enum representing valid rulebase values."""

    PRE = "pre"
    POST = "post"


class AppOverrideRuleProtocol(str, Enum):
    """Enum representing valid protocol values for app override rules."""

    tcp = "tcp"
    udp = "udp"


class AppOverrideRuleBaseModel(BaseModel):
    """Base model for App Override Rules containing fields common to all operations."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    name: str = Field(
        ...,
        description="The name of the app override rule",
        pattern=r"^[a-zA-Z0-9._-]+$",
        max_length=63,
    )
    application: str = Field(
        ...,
        description="The application to override",
    )
    destination: List[str] = Field(
        default_factory=lambda: ["any"],
        description="The destination address(es)",
    )
    from_: List[str] = Field(
        default_factory=lambda: ["any"],
        description="The source security zone(s)",
        alias="from",
    )
    to_: List[str] = Field(
        default_factory=lambda: ["any"],
        description="The destination security zone(s)",
        alias="to",
    )
    port: str = Field(
        ...,
        description="The port(s) for the rule",
    )
    protocol: AppOverrideRuleProtocol = Field(
        ...,
        description="The protocol for the rule",
    )
    source: List[str] = Field(
        default_factory=lambda: ["any"],
        description="The source address(es)",
    )
    description: Optional[str] = Field(
        None,
        description="The description of the app override rule",
        max_length=1024,
    )
    disabled: Optional[bool] = Field(
        False,
        description="Is the app override rule disabled?",
    )
    group_tag: Optional[str] = Field(
        None,
        description="The group tag for the rule",
    )
    negate_destination: Optional[bool] = Field(
        False,
        description="Negate the destination address(es)?",
    )
    negate_source: Optional[bool] = Field(
        False,
        description="Negate the source address(es)?",
    )
    tag: Optional[List[str]] = Field(
        None,
        description="The tags associated with the app override rule",
    )

    folder: Optional[str] = Field(
        None,
        description="Folder",
        max_length=64,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
    )
    snippet: Optional[str] = Field(
        None,
        description="Snippet",
        max_length=64,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
    )
    device: Optional[str] = Field(
        None,
        description="Device",
        max_length=64,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
    )

    # Common validators
    @field_validator(
        "from_",
        "to_",
        "source",
        "destination",
        "tag",
        mode="before",
    )
    @classmethod
    def ensure_list_of_strings(cls, v):
        """Ensure value is a list of strings, converting from string if needed.

        Args:
            v (Any): The value to validate.

        Returns:
            list[str]: A list of strings.

        Raises:
            ValueError: If the value is not a string or list of strings.

        """
        if v is None:
            return v
        if isinstance(v, str):
            v = [v]
        elif not isinstance(v, list):
            raise ValueError("Value must be a list of strings")
        if not all(isinstance(item, str) for item in v):
            raise ValueError("All items must be strings")
        return v

    @field_validator(
        "from_",
        "to_",
        "source",
        "destination",
        "tag",
    )
    @classmethod
    def ensure_unique_items(cls, v):
        """Ensure all items in the list are unique.

        Args:
            v (list): The list to validate.

        Returns:
            list: The validated list.

        Raises:
            ValueError: If duplicate items are found.

        """
        if v is None:
            return v
        if len(v) != len(set(v)):
            raise ValueError("List items must be unique")
        return v


class AppOverrideRuleCreateModel(AppOverrideRuleBaseModel):
    """Model for creating new App Override Rules."""

    rulebase: Optional[AppOverrideRuleRulebase] = Field(
        None,
        description="Which rulebase to use (pre or post)",
    )

    @model_validator(mode="after")
    def validate_container_type(self) -> "AppOverrideRuleCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            AppOverrideRuleCreateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = ["folder", "snippet", "device"]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class AppOverrideRuleUpdateModel(AppOverrideRuleBaseModel):
    """Model for updating existing App Override Rules with all fields optional."""

    rulebase: Optional[AppOverrideRuleRulebase] = None

    id: UUID = Field(
        ...,
        description="The UUID of the app override rule",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class AppOverrideRuleResponseModel(AppOverrideRuleBaseModel):
    """Model for App Override Rule responses, including the id field."""

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    id: UUID = Field(
        ...,
        description="The UUID of the app override rule",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )

    # Override required fields as optional for response (API may omit for system/default rules)
    application: Optional[str] = Field(
        None,
        description="The application to override",
    )
    port: Optional[str] = Field(
        None,
        description="The port(s) for the rule",
    )
    protocol: Optional[AppOverrideRuleProtocol] = Field(
        None,
        description="The protocol for the rule",
    )

    rulebase: Optional[AppOverrideRuleRulebase] = Field(
        None,
        description="Which rulebase the rule belongs to (pre or post)",
    )

    # Override the device field to accept None, a string, or an empty dict
    device: Optional[Union[str, Dict]] = Field(
        None,
        description="Device (optional: can be None, a string, or an empty dictionary)",
    )

    @field_validator("device")
    @classmethod
    def validate_device(cls, v):
        """Validate that the device field is None, a string, or an empty dictionary.

        Args:
            v: The value of the device field to be validated.

        Raises:
            ValueError: If the device is a dictionary but not empty.

        Returns:
            The validated value of the device field.

        """
        if isinstance(v, dict) and v != {}:
            raise ValueError("If device is a dictionary, it must be empty")
        return v


class AppOverrideRuleMoveModel(BaseModel):
    """Model for app override rule move operations."""

    destination: AppOverrideRuleMoveDestination = Field(
        ...,
        description="Where to move the rule (top, bottom, before, after)",
    )
    rulebase: AppOverrideRuleRulebase = Field(
        ...,
        description="Which rulebase to use (pre or post)",
    )
    destination_rule: Optional[UUID] = Field(
        None,
        description="UUID of the reference rule for before/after moves",
    )

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    @model_validator(mode="after")
    def validate_move_configuration(self) -> "AppOverrideRuleMoveModel":
        """Validate move configuration for App Override Rule reordering.

        Ensures that destination_rule is provided only when destination is BEFORE or AFTER.

        Returns:
            AppOverrideRuleMoveModel: The validated model instance.

        Raises:
            ValueError: If destination_rule is missing or present in an invalid context.

        """
        if self.destination in (
            AppOverrideRuleMoveDestination.BEFORE,
            AppOverrideRuleMoveDestination.AFTER,
        ):
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
