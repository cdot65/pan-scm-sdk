"""Authentication Rules security models for Strata Cloud Manager SDK.

Contains Pydantic models for representing authentication rule objects and related data.
"""

# scm/models/security/authentication_rules.py

from enum import Enum
from typing import Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# Enums
class AuthenticationRuleMoveDestination(str, Enum):
    """Enum representing valid destination values for rule movement."""

    TOP = "top"
    BOTTOM = "bottom"
    BEFORE = "before"
    AFTER = "after"


class AuthenticationRuleRulebase(str, Enum):
    """Enum representing valid rulebase values."""

    PRE = "pre"
    POST = "post"


class AuthenticationRuleBaseModel(BaseModel):
    """Base model for Authentication Rules containing fields common to all operations."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    name: str = Field(
        ..., description="The name of the authentication rule", pattern=r"^[a-zA-Z0-9_ \.-]+$"
    )
    disabled: bool = Field(False, description="Is the authentication rule disabled?")
    description: Optional[str] = Field(
        None, description="The description of the authentication rule"
    )
    tag: List[str] = Field(
        default_factory=list, description="The tags associated with the authentication rule"
    )
    from_: List[str] = Field(
        default_factory=lambda: ["any"],
        description="The source security zone(s)",
        alias="from",
    )
    source: List[str] = Field(
        default_factory=lambda: ["any"],
        description="The source address(es)",
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
    negate_destination: bool = Field(False, description="Negate the destination address(es)?")
    destination_hip: List[str] = Field(
        default_factory=lambda: ["any"],
        description="The destination Host Integrity Profile(s)",
    )
    service: List[str] = Field(
        default_factory=lambda: ["any"],
        description="The service(s) being accessed",
    )
    category: List[str] = Field(
        default_factory=lambda: ["any"],
        description="The URL categories being accessed",
    )
    authentication_enforcement: Optional[str] = Field(
        None, description="The authentication profile name"
    )
    hip_profiles: Optional[List[str]] = Field(
        None, description="The source Host Integrity Profile(s)"
    )
    group_tag: Optional[str] = Field(None, description="The group tag")
    timeout: Optional[int] = Field(
        None, ge=1, le=1440, description="Auth session timeout in minutes"
    )
    log_setting: Optional[str] = Field(None, description="The log forwarding profile name")
    log_authentication_timeout: bool = Field(False, description="Log authentication timeouts?")

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
        "service",
        "category",
        "tag",
        "hip_profiles",
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
        "source",
        "source_user",
        "source_hip",
        "destination",
        "destination_hip",
        "service",
        "category",
        "tag",
        "hip_profiles",
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
        if v is not None and len(v) != len(set(v)):
            raise ValueError("List items must be unique")
        return v


class AuthenticationRuleCreateModel(AuthenticationRuleBaseModel):
    """Model for creating new Authentication Rules."""

    rulebase: Optional[AuthenticationRuleRulebase] = Field(
        None,
        description="Which rulebase to use (pre or post)",
    )

    @model_validator(mode="after")
    def validate_container_type(self) -> "AuthenticationRuleCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            AuthenticationRuleCreateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = ["folder", "snippet", "device"]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class AuthenticationRuleUpdateModel(AuthenticationRuleBaseModel):
    """Model for updating existing Authentication Rules with all fields optional."""

    rulebase: Optional[AuthenticationRuleRulebase] = None

    id: UUID = Field(
        ...,
        description="The UUID of the authentication rule",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class AuthenticationRuleResponseModel(AuthenticationRuleBaseModel):
    """Model for Authentication Rule responses, including the id field."""

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    id: UUID = Field(
        ...,
        description="The UUID of the authentication rule",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )

    rulebase: Optional[AuthenticationRuleRulebase] = Field(
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


class AuthenticationRuleMoveModel(BaseModel):
    """Model for authentication rule move operations."""

    destination: AuthenticationRuleMoveDestination = Field(
        ...,
        description="Where to move the rule (top, bottom, before, after)",
    )
    rulebase: AuthenticationRuleRulebase = Field(
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
    def validate_move_configuration(self) -> "AuthenticationRuleMoveModel":
        """Validate move configuration for Authentication Rule reordering.

        Ensures that destination_rule is provided only when destination is BEFORE or AFTER.

        Returns:
            AuthenticationRuleMoveModel: The validated model instance.

        Raises:
            ValueError: If destination_rule is missing or present in an invalid context.

        """
        if self.destination in (
            AuthenticationRuleMoveDestination.BEFORE,
            AuthenticationRuleMoveDestination.AFTER,
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
