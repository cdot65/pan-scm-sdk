"""Decryption Rules security models for Strata Cloud Manager SDK.

Contains Pydantic models for representing decryption rule objects and related data.
"""

# scm/models/security/decryption_rules.py

from enum import Enum
from typing import Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from scm.models.objects.tag import TagName


# Enums
class DecryptionRuleMoveDestination(str, Enum):
    """Enum representing valid destination values for rule movement."""

    TOP = "top"
    BOTTOM = "bottom"
    BEFORE = "before"
    AFTER = "after"


class DecryptionRuleRulebase(str, Enum):
    """Enum representing valid rulebase values."""

    PRE = "pre"
    POST = "post"


class DecryptionRuleAction(str, Enum):
    """Enum representing valid decryption rule actions."""

    decrypt = "decrypt"
    no_decrypt = "no-decrypt"


# Component Models
class DecryptionRuleType(BaseModel):
    """Model for decryption rule type settings.

    Supports oneOf: ssl_forward_proxy (empty dict) or ssl_inbound_inspection (string).
    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    ssl_forward_proxy: Optional[Dict] = Field(
        None,
        description="SSL Forward Proxy decryption type",
    )
    ssl_inbound_inspection: Optional[str] = Field(
        None,
        description="SSL Inbound Inspection certificate name",
    )

    @model_validator(mode="after")
    def validate_type_exclusivity(self) -> "DecryptionRuleType":
        """Ensure exactly one of ssl_forward_proxy or ssl_inbound_inspection is set.

        Returns:
            DecryptionRuleType: The validated model instance.

        Raises:
            ValueError: If neither or both fields are set.

        """
        has_forward = self.ssl_forward_proxy is not None
        has_inbound = self.ssl_inbound_inspection is not None
        if has_forward and has_inbound:
            raise ValueError(
                "Only one of 'ssl_forward_proxy' or 'ssl_inbound_inspection' can be provided."
            )
        if not has_forward and not has_inbound:
            raise ValueError(
                "Exactly one of 'ssl_forward_proxy' or 'ssl_inbound_inspection' must be provided."
            )
        return self


class DecryptionRuleBaseModel(BaseModel):
    """Base model for Decryption Rules containing fields common to all operations."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    name: str = Field(
        ..., description="The name of the decryption rule", pattern=r"^[a-zA-Z0-9_ \.-]+$"
    )
    action: Optional[DecryptionRuleAction] = Field(
        None,
        description="The action to be taken when the rule is matched",
    )
    description: Optional[str] = Field(None, description="The description of the decryption rule")
    tag: List[TagName] = Field(
        default_factory=list, description="The tags associated with the decryption rule"
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
    source: List[str] = Field(
        default_factory=lambda: ["any"],
        description="The source address(es)",
    )
    destination: List[str] = Field(
        default_factory=lambda: ["any"],
        description="The destination address(es)",
    )
    source_user: List[str] = Field(
        default_factory=lambda: ["any"],
        description="List of source users and/or groups",
    )
    category: List[str] = Field(
        default_factory=lambda: ["any"],
        description="The URL categories being accessed",
    )
    service: List[str] = Field(
        default_factory=lambda: ["any"],
        description="The service(s) being accessed",
    )
    source_hip: List[str] = Field(
        default_factory=lambda: ["any"],
        description="The source Host Integrity Profile(s)",
    )
    destination_hip: List[str] = Field(
        default_factory=lambda: ["any"],
        description="The destination Host Integrity Profile(s)",
    )
    negate_source: bool = Field(False, description="Negate the source address(es)?")
    negate_destination: bool = Field(False, description="Negate the destination address(es)?")
    disabled: bool = Field(False, description="Is the decryption rule disabled?")
    profile: Optional[str] = Field(
        None, description="The decryption profile associated with the rule"
    )
    type: Optional[DecryptionRuleType] = Field(None, description="The type of decryption")
    log_setting: Optional[str] = Field(None, description="The log settings of the decryption rule")
    log_fail: Optional[bool] = Field(None, description="Log failed decryption events?")
    log_success: Optional[bool] = Field(None, description="Log successful decryption events?")

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
        if len(v) != len(set(v)):
            raise ValueError("List items must be unique")
        return v


class DecryptionRuleCreateModel(DecryptionRuleBaseModel):
    """Model for creating new Decryption Rules."""

    rulebase: Optional[DecryptionRuleRulebase] = Field(
        None,
        description="Which rulebase to use (pre or post)",
    )

    @model_validator(mode="after")
    def validate_container_type(self) -> "DecryptionRuleCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            DecryptionRuleCreateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = ["folder", "snippet", "device"]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class DecryptionRuleUpdateModel(DecryptionRuleBaseModel):
    """Model for updating existing Decryption Rules with all fields optional."""

    rulebase: Optional[DecryptionRuleRulebase] = None

    id: UUID = Field(
        ...,
        description="The UUID of the decryption rule",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class DecryptionRuleResponseModel(DecryptionRuleBaseModel):
    """Model for Decryption Rule responses, including the id field."""

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    id: UUID = Field(
        ...,
        description="The UUID of the decryption rule",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )

    rulebase: Optional[DecryptionRuleRulebase] = Field(
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


class DecryptionRuleMoveModel(BaseModel):
    """Model for decryption rule move operations."""

    destination: DecryptionRuleMoveDestination = Field(
        ...,
        description="Where to move the rule (top, bottom, before, after)",
    )
    rulebase: DecryptionRuleRulebase = Field(
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
    def validate_move_configuration(self) -> "DecryptionRuleMoveModel":
        """Validate move configuration for Decryption Rule reordering.

        Ensures that destination_rule is provided only when destination is BEFORE or AFTER.

        Returns:
            DecryptionRuleMoveModel: The validated model instance.

        Raises:
            ValueError: If destination_rule is missing or present in an invalid context.

        """
        if self.destination in (
            DecryptionRuleMoveDestination.BEFORE,
            DecryptionRuleMoveDestination.AFTER,
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
