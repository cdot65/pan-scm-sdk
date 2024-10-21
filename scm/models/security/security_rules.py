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


# Enums
class Action(str, Enum):
    """
    Enum representing various network actions.

    class Action:

        allow:
            Represents an action that allows the network traffic.

        deny:
            Represents an action that denies the network traffic.

        drop:
            Represents an action that drops the network traffic without responding to the sender.

        reset_client:
            Represents an action that resets the client-side connection.

        reset_server:
            Represents an action that resets the server-side connection.

        reset_both:
            Represents an action that resets both client and server-side connections.
    """

    allow = "allow"
    deny = "deny"
    drop = "drop"
    reset_client = "reset-client"
    reset_server = "reset-server"
    reset_both = "reset-both"


# Model for profile_setting
class ProfileSetting(BaseModel):
    """
    class ProfileSetting(BaseModel):

        group: Optional[List[str]] = Field(
            default_factory=lambda: ["best-practice"],
            description="The security profile group",
        )
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


# Base model for Security Rule
class SecurityRuleBaseModel(BaseModel):
    name: constr(pattern=r"^[a-zA-Z0-9_ -]+$") = Field(
        ...,
        description="The name of the security rule",
    )
    disabled: bool = Field(
        False,
        description="Is the security rule disabled?",
    )
    description: Optional[str] = Field(
        None,
        description="The description of the security rule",
    )
    tag: List[str] = Field(
        default_factory=list,
        description="The tags associated with the security rule",
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
    negate_source: bool = Field(
        False,
        description="Negate the source address(es)?",
    )
    source_user: List[str] = Field(
        default_factory=lambda: ["any"],
        description=(
            "List of source users and/or groups. Reserved words include `any`, "
            "`pre-login`, `known-user`, and `unknown`."
        ),
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
        False,
        description="Negate the destination address(es)?",
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
    profile_setting: Optional[ProfileSetting] = Field(
        None,
        description="The security profile object",
    )
    log_setting: Optional[str] = Field(
        None,
        description="The external log forwarding profile",
    )
    schedule: Optional[str] = Field(
        None,
        description="Schedule in which this rule will be applied",
    )
    log_start: Optional[bool] = Field(
        None,
        description="Log at session start?",
    )
    log_end: Optional[bool] = Field(
        None,
        description="Log at session end?",
    )

    model_config = ConfigDict(populate_by_name=True)

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

    model_config = ConfigDict(validate_assignment=True, arbitrary_types_allowed=True)

    @model_validator(mode="after")
    def validate_container(self) -> "SecurityRuleRequestModel":
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
