from enum import Enum
from typing import List, Optional, Union
from uuid import UUID
from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
    ConfigDict,
    constr,
)


class NatType(str, Enum):
    """NAT types supported by the system."""

    ipv4 = "ipv4"
    nat64 = "nat64"
    nptv6 = "nptv6"


class NatMoveDestination(str, Enum):
    """Valid destination values for rule movement."""

    TOP = "top"
    BOTTOM = "bottom"
    BEFORE = "before"
    AFTER = "after"


class NatRulebase(str, Enum):
    """Valid rulebase values."""

    PRE = "pre"
    POST = "post"


class InterfaceAddress(BaseModel):
    """Interface address configuration."""

    interface: str = Field(..., description="Interface name")
    ip: Optional[str] = Field(None, description="IP address")
    floating_ip: Optional[str] = Field(None, description="Floating IP address")


class SourceTranslation(BaseModel):
    """Source translation configuration."""

    model_config = ConfigDict(validate_assignment=True)

    translated_address: Optional[List[str]] = Field(
        None, description="Translated addresses"
    )
    bi_directional: Optional[bool] = Field(
        None, description="Enable bi-directional translation"
    )
    interface: Optional[InterfaceAddress] = None
    fallback: Optional[dict] = None


class NatRuleBaseModel(BaseModel):
    """Base model for NAT Rules containing fields common to all operations."""

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    name: constr(pattern=r"^[a-zA-Z0-9_ \.-]+$") = Field(
        ...,
        description="The name of the NAT rule",
    )
    description: Optional[str] = Field(
        None,
        description="The description of the NAT rule",
    )
    tag: List[str] = Field(
        default_factory=list,
        description="The tags associated with the NAT rule",
    )
    disabled: bool = Field(
        False,
        description="Is the NAT rule disabled?",
    )
    nat_type: NatType = Field(
        default=NatType.ipv4,
        description="The type of NAT operation",
    )
    from_: List[str] = Field(
        default_factory=lambda: ["any"],
        description="Source zone(s)",
        alias="from",
    )
    to_: List[str] = Field(
        default_factory=lambda: ["any"],
        description="Destination zone(s)",
        alias="to",
    )
    source: List[str] = Field(
        default_factory=lambda: ["any"],
        description="Source address(es)",
    )
    destination: List[str] = Field(
        default_factory=lambda: ["any"],
        description="Destination address(es)",
    )
    service: Optional[str] = Field(
        None,
        description="The TCP/UDP service",
    )
    source_translation: Optional[SourceTranslation] = None

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

    @field_validator(
        "from_",
        "to_",
        "source",
        "destination",
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
        "to_",
        "source",
        "destination",
        "tag",
    )
    def ensure_unique_items(cls, v):
        if len(v) != len(set(v)):
            raise ValueError("List items must be unique")
        return v


class NatRuleCreateModel(NatRuleBaseModel):
    """Model for creating new NAT Rules."""

    @model_validator(mode="after")
    def validate_container(self) -> "NatRuleCreateModel":
        container_fields = ["folder", "snippet", "device"]
        provided = [
            field for field in container_fields if getattr(self, field) is not None
        ]
        if len(provided) != 1:
            raise ValueError(
                "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            )
        return self


class NatRuleUpdateModel(NatRuleBaseModel):
    """Model for updating existing NAT Rules."""

    id: UUID = Field(
        ...,
        description="The UUID of the NAT rule",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class NatRuleResponseModel(NatRuleBaseModel):
    """Model for NAT Rule responses."""

    id: UUID = Field(
        ...,
        description="The UUID of the NAT rule",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class NatRuleMoveModel(BaseModel):
    """Model for NAT rule move operations."""

    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    destination: NatMoveDestination = Field(
        ...,
        description="Where to move the rule (top, bottom, before, after)",
    )
    rulebase: NatRulebase = Field(
        ...,
        description="Which rulebase to use (pre or post)",
    )
    destination_rule: Optional[UUID] = Field(
        None,
        description="UUID of the reference rule for before/after moves",
    )

    @model_validator(mode="after")
    def validate_move_configuration(self) -> "NatRuleMoveModel":
        if self.destination in (NatMoveDestination.BEFORE, NatMoveDestination.AFTER):
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
