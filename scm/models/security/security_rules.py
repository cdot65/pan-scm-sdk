# scm/models/security/security_rules.py

from typing import List, Optional
from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
    ConfigDict,
    constr,
    conlist,
)
from enum import Enum
import uuid


def string_validator(v):
    if not isinstance(v, str):
        raise ValueError("Must be a string")
    return v


StringList = conlist(item_type=string_validator, min_length=1)


# Moved Enums from security_rule_move.py
class RuleMoveDestination(str, Enum):
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


class Action(str, Enum):
    """
    Enum representing various network actions.
    """

    allow = "allow"
    deny = "deny"
    drop = "drop"
    reset_client = "reset-client"
    reset_server = "reset-server"
    reset_both = "reset-both"


class ProfileSetting(BaseModel):
    """
    Model for security profile settings.
    """

    group: Optional[List[str]] = Field(
        default_factory=lambda: ["best-practice"],
        description="The security profile group",
    )

    @field_validator("group")
    def validate_unique_items(cls, v):
        if v is not None and len(v) != len(set(v)):
            raise ValueError("List items in 'group' must be unique")
        return v


class SecurityRuleBaseModel(BaseModel):
    """
    Base model for Security Rules containing fields common to both requests and responses.
    """

    name: constr(pattern=r"^[a-zA-Z0-9_ \.-]+$") = Field(
        ...,
        description="The name of the security rule",
    )
    disabled: bool = Field(False, description="Is the security rule disabled?")
    description: Optional[str] = Field(
        None, description="The description of the security rule"
    )
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
    negate_destination: bool = Field(
        False, description="Negate the destination addresses(es)?"
    )
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
    action: Optional[Action] = Field(
        default="allow",
        description="The action to be taken when the rule is matched",
    )
    profile_setting: Optional[ProfileSetting] = None
    log_setting: Optional[str] = None
    schedule: Optional[str] = None
    log_start: Optional[bool] = None
    log_end: Optional[bool] = None

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

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
        if isinstance(v, str):
            v = [v]
        elif not isinstance(v, list):
            raise ValueError("Value must be a list of strings")
        if not all(isinstance(item, str) for item in v):
            raise ValueError("All items must be strings")
        return v

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
    )
    def ensure_unique_items(cls, v):
        if len(v) != len(set(v)):
            raise ValueError("List items must be unique")
        return v


# Request model
class SecurityRuleRequestModel(SecurityRuleBaseModel):
    """
    SecurityRuleRequestModel defines a model for creating and validating security rule requests. Inherits properties from SecurityRuleBaseModel.

    Attributes:
    folder: Optional[str]
        Folder in which the resource is defined. Must be a string with a maximum length of 64 characters and match the specified pattern.
    snippet: Optional[str]
        Snippet in which the resource is defined. Must be a string with a maximum length of 64 characters and match the specified pattern.
    device: Optional[str]
        Device in which the resource is defined. Must be a string with a maximum length of 64 characters and match the specified pattern.

    config:
        ConfigDict with validate_assignment set to True and arbitrary_types_allowed set to True.

    Methods:
    validate_container:
        Validates that exactly one of the optional fields (folder, snippet, or device) is provided. Raises a ValueError if this condition is not met.
    """

    # Container fields
    folder: Optional[str] = Field(
        None,
        description="Folder in which the resource is defined",
        max_length=64,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
    )
    snippet: Optional[str] = Field(
        None,
        description="Snippet in which the resource is defined",
        max_length=64,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
    )
    device: Optional[str] = Field(
        None,
        description="Device in which the resource is defined",
        max_length=64,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
    )
    rulebase: Optional[Rulebase] = Field(
        None,
        description="Which rulebase to use (pre or post)",
    )

    @model_validator(mode="after")
    def validate_container(self) -> "SecurityRuleRequestModel":
        """Validates that exactly one container field is provided."""
        container_fields = ["folder", "snippet", "device"]
        provided_containers = [
            field for field in container_fields if getattr(self, field) is not None
        ]
        if len(provided_containers) != 1:
            raise ValueError(
                "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            )
        return self


# Response model
class SecurityRuleResponseModel(SecurityRuleBaseModel):
    """
    SecurityRuleResponseModel

    A class representing the response model for a security rule. Inherits from SecurityRuleBaseModel.

    Attributes:
        id (str): The UUID of the security rule.
        folder (Optional[str]): Folder in which the resource is defined.
        snippet (Optional[str]): Snippet in which the resource is defined.
        device (Optional[str]): Device in which the resource is defined.

    Methods:
        validate_id(cls, v): Validates that the 'id' is in UUID format.
    """

    id: str = Field(
        ...,
        description="The UUID of the security rule",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
    folder: Optional[str] = Field(
        None,
        description="Folder in which the resource is defined",
    )
    snippet: Optional[str] = Field(
        None,
        description="Snippet in which the resource is defined",
    )
    device: Optional[str] = Field(
        None,
        description="Device in which the resource is defined",
    )

    @field_validator("id")
    def validate_id(cls, v):
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError("Invalid UUID format for 'id'")
        return v


# Response model for list of security rules
class SecurityRulesResponse(BaseModel):
    """

    class SecurityRulesResponse(BaseModel):

    data: List[SecurityRuleResponseModel]
    offset: int
    total: int
    limit: int


    SecurityRulesResponse represents the response for a security rules query.

    Attributes:
    data : List[SecurityRuleResponseModel]
        A list containing the security rule response models.
    offset : int
        The offset for the response.
    total : int
        The total number of security rules available.
    limit : int
        The limit on the number of security rules returned in the response.
    """

    data: List[SecurityRuleResponseModel]
    offset: int
    total: int
    limit: int


class SecurityRuleMoveModel(BaseModel):
    """
    Model for security rule move operations.

    This model defines and validates the fields required for moving a security rule
    within a rulebase. It handles the move operation independently from other security
    rule operations.

    Attributes:
        source_rule (str): UUID of the security rule to be moved
        destination (RuleMoveDestination): Where to move the rule (top, bottom, before, after)
        rulebase (Rulebase): Which rulebase to use (pre or post)
        destination_rule (Optional[str]): UUID of the reference rule, required for
            'before' and 'after' operations

    Example:
        >>> move_config = SecurityRuleMoveModel(
        ...     source_rule="123e4567-e89b-12d3-a456-426655440000",
        ...     destination=RuleMoveDestination.BEFORE,
        ...     rulebase=Rulebase.PRE,
        ...     destination_rule="987fcdeb-51d3-a456-426655440000"
        ... )
    """

    source_rule: str = Field(
        ...,
        description="UUID of the security rule to be moved",
    )
    destination: RuleMoveDestination = Field(
        ...,
        description="Where to move the rule (top, bottom, before, after)",
    )
    rulebase: Rulebase = Field(
        ...,
        description="Which rulebase to use (pre or post)",
    )
    destination_rule: Optional[str] = Field(
        None,
        description="UUID of the reference rule for before/after moves",
    )

    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    @field_validator("source_rule", "destination_rule")
    def validate_uuid_fields(cls, v: Optional[str]) -> Optional[str]:
        """Validate UUID format for rule identifiers."""
        if v is not None:
            try:
                uuid.UUID(v)
            except ValueError:
                raise ValueError("Field must be a valid UUID")
        return v

    @model_validator(mode="after")
    def validate_move_configuration(self) -> "SecurityRuleMoveModel":
        """
        Validates the combination of move operation fields.

        Ensures that destination_rule is provided when required (for before/after moves)
        and not provided when it shouldn't be (for top/bottom moves).
        """
        if self.destination in (RuleMoveDestination.BEFORE, RuleMoveDestination.AFTER):
            if not self.destination_rule:
                raise ValueError(
                    f"destination_rule is required when destination is '{self.destination.value}'"
                )
        elif self.destination_rule is not None:
            raise ValueError(
                f"destination_rule should not be provided when destination is '{self.destination.value}'"
            )
        return self
