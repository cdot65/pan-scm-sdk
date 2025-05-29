"""Security Rules security models for Strata Cloud Manager SDK.

Contains Pydantic models for representing security rule objects and related data.
"""

# scm/models/security/security_rules.py

from enum import Enum
from typing import Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# Enums
class SecurityRuleMoveDestination(str, Enum):
    """Enum representing valid destination values for rule movement."""

    TOP = "top"
    BOTTOM = "bottom"
    BEFORE = "before"
    AFTER = "after"


class SecurityRuleRulebase(str, Enum):
    """Enum representing valid rulebase values."""

    PRE = "pre"
    POST = "post"


class SecurityRuleAction(str, Enum):
    """Enum representing various network actions."""

    allow = "allow"
    deny = "deny"
    drop = "drop"
    reset_client = "reset-client"
    reset_server = "reset-server"
    reset_both = "reset-both"


# Component Models
class SecurityRuleProfileSetting(BaseModel):
    """Model for security profile settings."""

    group: Optional[List[str]] = Field(
        default_factory=lambda: ["best-practice"],
        description="The security profile group",
    )

    @field_validator("group")
    def validate_unique_items(cls, v):
        """Ensure all items in the group list are unique.

        Args:
            v (list): The list to validate.

        Returns:
            list: The validated list.

        Raises:
            ValueError: If duplicate items are found.

        """
        if v is not None and len(v) != len(set(v)):
            raise ValueError("List items in 'group' must be unique")
        return v


class SecurityRuleBaseModel(BaseModel):
    """Base model for Security Rules containing fields common to all operations."""

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    name: str = Field(
        ..., description="The name of the security rule", pattern=r"^[a-zA-Z0-9_ \.-]+$"
    )
    disabled: bool = Field(False, description="Is the security rule disabled?")
    description: Optional[str] = Field(None, description="The description of the security rule")
    tag: List[str] = Field(
        default_factory=list, description="The tags associated with the security rule"
    )
    from_: List[str] = Field(
        default_factory=lambda: ["any"],
        description="The source security zone(s)",
        alias="from",
    )
    source: List[str] = Field(
        default_factory=lambda: ["any"],
        description="The source addresses(es)",
    )
    negate_source: bool = Field(False, description="Negate the source address(es)?")
    source_user: List[str] = Field(
        default_factory=lambda: ["any"],
        description="List of source users and/or groups",
    )
    source_hip: List[str] = Field(
        default_factory=lambda: ["any"],
        description="The source Host Integrity Profile(s)",
    )
    to_: List[str] = Field(
        default_factory=lambda: ["any"],
        description="The destination security zone(s)",
        alias="to",
    )
    destination: List[str] = Field(
        default_factory=lambda: ["any"],
        description="The destination address(es)",
    )
    negate_destination: bool = Field(False, description="Negate the destination addresses(es)?")
    destination_hip: List[str] = Field(
        default_factory=lambda: ["any"],
        description="The destination Host Integrity Profile(s)",
    )
    application: List[str] = Field(
        default_factory=lambda: ["any"],
        description="The application(s) being accessed",
    )
    service: List[str] = Field(
        default_factory=lambda: ["any"],
        description="The service(s) being accessed",
    )
    category: List[str] = Field(
        default_factory=lambda: ["any"],
        description="The URL categories being accessed",
    )
    action: SecurityRuleAction = Field(
        default=SecurityRuleAction.allow,
        description="The action to be taken when the rule is matched",
    )
    profile_setting: Optional[SecurityRuleProfileSetting] = None
    log_setting: Optional[str] = None
    schedule: Optional[str] = None
    log_start: Optional[bool] = None
    log_end: Optional[bool] = None

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
        "source",
        "source_user",
        "source_hip",
        "to_",
        "destination",
        "destination_hip",
        "application",
        "service",
        "category",
        "tag",
        mode="before",
    )
    def ensure_list_of_strings(cls, v):
        """Ensure value is a list of strings, converting from string if needed.

        Args:
            v (Any): The value to validate.

        Returns:
            list[str]: A list of strings.

        Raises:
            ValueError: If the value is not a string or list of strings.

        """
        if isinstance(v, str):
            v = [v]
        elif not isinstance(v, list):
            raise ValueError("Value must be a list of strings")
        if not all(isinstance(item, str) for item in v):
            raise ValueError("All items must be strings")
        return v

    @field_validator(
        "source",
        "source_user",
        "source_hip",
        "destination",
        "destination_hip",
        "application",
        "service",
        "category",
        "tag",
    )
    def ensure_unique_items(cls, v):
        """Ensure all items in the list are unique.

        Args:
            v (list): The list to validate.

        Returns:
            list: The validated list.

        Raises:
            ValueError: If duplicate items are found.

        """
        if len(v) != len(set(v)):
            raise ValueError("List items must be unique")
        return v


class SecurityRuleCreateModel(SecurityRuleBaseModel):
    """Model for creating new Security Rules."""

    rulebase: Optional[SecurityRuleRulebase] = Field(
        None,
        description="Which rulebase to use (pre or post)",
    )

    @model_validator(mode="after")
    def validate_container_type(self) -> "SecurityRuleCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            SecurityRuleCreateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = ["folder", "snippet", "device"]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class SecurityRuleUpdateModel(SecurityRuleBaseModel):
    """Model for updating existing Security Rules with all fields optional."""

    rulebase: Optional[SecurityRuleRulebase] = None

    id: Optional[UUID] = Field(
        ...,
        description="The UUID of the security rule",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class SecurityRuleResponseModel(SecurityRuleBaseModel):
    """Model for Security Rule responses, including the id field."""

    id: UUID = Field(
        ...,
        description="The UUID of the security rule",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )

    # Override the device field to accept None, a string, or an empty dict
    device: Optional[Union[str, Dict]] = Field(
        None,
        description="Device (optional: can be None, a string, or an empty dictionary)",
    )

    @field_validator("device")
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


class SecurityRuleMoveModel(BaseModel):
    """Model for security rule move operations."""

    destination: SecurityRuleMoveDestination = Field(
        ...,
        description="Where to move the rule (top, bottom, before, after)",
    )
    rulebase: SecurityRuleRulebase = Field(
        ...,
        description="Which rulebase to use (pre or post)",
    )
    destination_rule: Optional[UUID] = Field(
        None,
        description="UUID of the reference rule for before/after moves",
    )

    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    @model_validator(mode="after")
    def validate_move_configuration(self) -> "SecurityRuleMoveModel":
        """Validate move configuration for Security Rule reordering.

        Ensures that destination_rule is provided only when destination is BEFORE or AFTER.

        Returns:
            SecurityRuleMoveModel: The validated model instance.

        Raises:
            ValueError: If destination_rule is missing or present in an invalid context.

        """
        if self.destination in (
            SecurityRuleMoveDestination.BEFORE,
            SecurityRuleMoveDestination.AFTER,
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
