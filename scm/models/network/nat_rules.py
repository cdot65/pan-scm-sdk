"""NAT Rules models for Strata Cloud Manager SDK.

Contains Pydantic models for representing NAT rule objects and related data.
"""

from enum import Enum
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


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


class DistributionMethod(str, Enum):
    """Distribution methods for dynamic destination translation."""

    ROUND_ROBIN = "round-robin"
    SOURCE_IP_HASH = "source-ip-hash"
    IP_MODULO = "ip-modulo"
    IP_HASH = "ip-hash"
    LEAST_SESSIONS = "least-sessions"


class DnsRewriteDirection(str, Enum):
    """DNS rewrite direction options."""

    REVERSE = "reverse"
    FORWARD = "forward"


class BiDirectional(str, Enum):
    """Bi-directional translation options."""

    YES = "yes"
    NO = "no"


class InterfaceAddress(BaseModel):
    """Interface address configuration."""

    interface: str = Field(..., description="Interface name")
    ip: Optional[str] = Field(None, description="IP address")
    floating_ip: Optional[str] = Field(None, description="Floating IP address")


class DynamicIpAndPortTranslatedAddress(BaseModel):
    """Dynamic IP and port translated address configuration."""

    translated_address: List[str] = Field(..., description="Translated source IP addresses")


class DynamicIpAndPortInterfaceAddress(BaseModel):
    """Dynamic IP and port interface address configuration."""

    interface: str = Field(..., description="Interface name")
    ip: Optional[str] = Field(None, description="Translated source IP address")
    floating_ip: Optional[str] = Field(None, description="Floating IP address")


class DynamicIp(BaseModel):
    """Dynamic IP translation configuration."""

    translated_address: List[str] = Field(..., description="Translated IP addresses")
    fallback_type: Optional[str] = Field(
        None,
        description="Type of fallback configuration (translated_address or interface_address)",
    )
    fallback_address: Optional[List[str]] = Field(
        None,
        description="Fallback IP addresses (when fallback_type is translated_address)",
    )
    fallback_interface: Optional[str] = Field(
        None,
        description="Fallback interface name (when fallback_type is interface_address)",
    )
    fallback_ip: Optional[str] = Field(
        None,
        description="Fallback IP address (when fallback_type is interface_address)",
    )


class StaticIp(BaseModel):
    """Static IP translation configuration."""

    translated_address: str = Field(..., description="Translated IP address")
    bi_directional: Optional[BiDirectional] = Field(
        None,
        description="Enable bi-directional translation",
    )

    @field_validator("bi_directional")
    def convert_boolean_to_enum(cls, v):
        """Convert boolean to BiDirectional enum if needed."""
        if v is None:
            return v

        if isinstance(v, bool):
            return BiDirectional.YES if v else BiDirectional.NO

        return v


class DynamicIpAndPort(BaseModel):
    """Dynamic IP and port translation configuration."""

    # This class uses discriminated union pattern
    # Either translated_address or interface_address should be provided
    type: Literal["dynamic_ip_and_port"] = "dynamic_ip_and_port"
    translated_address: Optional[List[str]] = Field(
        None, description="Translated source IP addresses"
    )
    interface_address: Optional[InterfaceAddress] = Field(
        None, description="Translated source interface"
    )

    @model_validator(mode="after")
    def validate_dynamic_ip_and_port(self) -> "DynamicIpAndPort":
        """Validate that either translated_address or interface_address is provided, but not both."""
        if bool(self.translated_address) == bool(self.interface_address):
            raise ValueError(
                "Either translated_address or interface_address must be provided, but not both"
            )
        return self


class SourceTranslation(BaseModel):
    """Source translation configuration."""

    model_config = ConfigDict(validate_assignment=True)

    # Using discriminated union pattern for different source translation types
    dynamic_ip_and_port: Optional[DynamicIpAndPort] = Field(
        None, description="Dynamic IP and port translation configuration"
    )
    dynamic_ip: Optional[DynamicIp] = Field(
        None, description="Dynamic IP translation configuration"
    )
    static_ip: Optional[StaticIp] = Field(None, description="Static IP translation configuration")

    @model_validator(mode="after")
    def validate_source_translation(self) -> "SourceTranslation":
        """Validate that exactly one source translation type is provided."""
        translation_types = [self.dynamic_ip_and_port, self.dynamic_ip, self.static_ip]
        provided_types = [t for t in translation_types if t is not None]

        if len(provided_types) != 1:
            raise ValueError(
                "Exactly one of dynamic_ip_and_port, dynamic_ip, or static_ip must be provided"
            )
        return self


class DnsRewrite(BaseModel):
    """DNS rewrite configuration."""

    direction: DnsRewriteDirection = Field(..., description="DNS rewrite direction")


class DestinationTranslation(BaseModel):
    """Destination translation configuration."""

    model_config = ConfigDict(validate_assignment=True)

    translated_address: Optional[str] = Field(None, description="Translated destination IP address")
    translated_port: Optional[int] = Field(
        None,
        description="Translated destination port",
        ge=1,
        le=65535,
    )
    dns_rewrite: Optional[DnsRewrite] = Field(None, description="DNS rewrite configuration")
    # The API doesn't accept 'distribution' directly in the destination_translation object
    # Distribution settings should be configured separately


class NatRuleBaseModel(BaseModel):
    """Base model for NAT Rules containing fields common to all operations."""

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    name: str = Field(
        ...,
        description="The name of the NAT rule",
        pattern=r"^[a-zA-Z0-9_ \.-]+$",
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
    to_interface: Optional[str] = Field(
        None,
        description="Destination interface of the original packet",
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
        "any",
        description="The TCP/UDP service",
    )
    source_translation: Optional[SourceTranslation] = Field(
        None,
        description="Source translation configuration",
    )
    destination_translation: Optional[DestinationTranslation] = Field(
        None,
        description="Destination translation configuration",
    )
    # Distribution configuration should be added at the top level for load balancing
    active_active_device_binding: Optional[str] = Field(
        None,
        description="Active/Active device binding",
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

    @field_validator(
        "from_",
        "to_",
        "source",
        "destination",
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
        "from_",
        "to_",
        "source",
        "destination",
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

    @field_validator("tag")
    def validate_tags(cls, v):
        """Validate tags."""
        for tag in v:
            if not tag or not isinstance(tag, str) or not tag.strip():
                raise ValueError("Tags must be non-empty strings")
            if not all(c.isalnum() or c in "-_" for c in tag):
                raise ValueError(
                    "Tags should only contain alphanumeric characters, hyphens, or underscores"
                )
        return v

    @model_validator(mode="after")
    def validate_nat64_dns_rewrite_compatibility(self) -> "NatRuleBaseModel":
        """Validate that DNS rewrite is not used with NAT64 type rules."""
        if (
            self.nat_type == NatType.nat64
            and self.destination_translation
            and self.destination_translation.dns_rewrite
        ):
            raise ValueError("DNS rewrite is not available with NAT64 rules")
        return self

    @model_validator(mode="after")
    def validate_bidirectional_nat_compatibility(self) -> "NatRuleBaseModel":
        """Validate that bi-directional static NAT is not used with destination translation."""
        if (
            self.source_translation
            and self.source_translation.static_ip
            and self.source_translation.static_ip.bi_directional == BiDirectional.YES
            and self.destination_translation
        ):
            raise ValueError(
                "Bi-directional static NAT cannot be used with destination translation in the same rule"
            )
        return self


class NatRuleCreateModel(NatRuleBaseModel):
    """Model for creating new NAT Rules."""

    @model_validator(mode="after")
    def validate_container_type(self) -> "NatRuleCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            NatRuleCreateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = ["folder", "snippet", "device"]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
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
        """Validate move configuration for NAT rule reordering.

        Ensures that destination_rule is provided only when destination is BEFORE or AFTER.

        Returns:
            NatRuleMoveModel: The validated model instance.

        Raises:
            ValueError: If destination_rule is missing or present in an invalid context.

        """
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
