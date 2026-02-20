"""PBF Rule models for Strata Cloud Manager SDK.

Contains Pydantic models for representing Policy-Based Forwarding rule objects and related data.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


# --- Sub-Models ---


class PbfRuleForwardMonitor(BaseModel):
    """Monitor configuration for forward action."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    profile: Optional[str] = Field(
        None,
        description="Monitoring profile",
    )
    disable_if_unreachable: Optional[bool] = Field(
        None,
        description="Disable this rule if nexthop/monitor IP is unreachable",
    )
    ip_address: Optional[str] = Field(
        None,
        description="Monitor IP address",
    )


class PbfRuleForwardNexthop(BaseModel):
    """Nexthop configuration for forward action.

    Uses Dict to handle oneOf: ip_address or fqdn.
    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    ip_address: Optional[str] = Field(
        None,
        description="Next hop IP address",
    )
    fqdn: Optional[str] = Field(
        None,
        description="Next hop FQDN",
    )


class PbfRuleForward(BaseModel):
    """Forward action configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    egress_interface: Optional[str] = Field(
        None,
        description="Egress interface",
    )
    nexthop: Optional[PbfRuleForwardNexthop] = Field(
        None,
        description="Next hop configuration",
    )
    monitor: Optional[PbfRuleForwardMonitor] = Field(
        None,
        description="Monitor configuration",
    )


class PbfRuleAction(BaseModel):
    """Action configuration for PBF rules.

    Supports oneOf: forward, discard, or no_pbf.
    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    forward: Optional[PbfRuleForward] = Field(
        None,
        description="Forward action configuration",
    )
    discard: Optional[Dict[str, Any]] = Field(
        None,
        description="Discard action (empty object)",
    )
    no_pbf: Optional[Dict[str, Any]] = Field(
        None,
        description="No PBF action (empty object)",
    )


class PbfRuleFrom(BaseModel):
    """Source zone/interface configuration.

    Supports oneOf: zone (list of zone names) or interface (list of interface names).
    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    zone: Optional[List[str]] = Field(
        None,
        description="Source zones",
    )
    interface: Optional[List[str]] = Field(
        None,
        description="Source interfaces",
    )


class PbfRuleNexthopAddress(BaseModel):
    """Nexthop address entry for enforce symmetric return."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(
        ...,
        description="Next hop IP address",
    )


class PbfRuleEnforceSymmetricReturn(BaseModel):
    """Enforce symmetric return configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    enabled: Optional[bool] = Field(
        None,
        description="Enforce symmetric return",
    )
    nexthop_address_list: Optional[List[PbfRuleNexthopAddress]] = Field(
        None,
        description="Next hop IP addresses for symmetric return",
    )


# --- Main Models ---


class PbfRuleBaseModel(BaseModel):
    """Base model for PBF Rules."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    name: str = Field(
        ...,
        description="PBF rule name",
    )
    description: Optional[str] = Field(
        None,
        description="Description of the PBF rule",
    )
    tag: Optional[List[str]] = Field(
        None,
        description="Tags associated with the PBF rule",
    )
    schedule: Optional[str] = Field(
        None,
        description="Schedule for the PBF rule",
    )
    disabled: Optional[bool] = Field(
        None,
        description="Is the PBF rule disabled",
    )
    from_: Optional[PbfRuleFrom] = Field(
        None,
        description="Source zone or interface",
        alias="from",
    )
    source: Optional[List[str]] = Field(
        None,
        description="Source addresses",
    )
    source_user: Optional[List[str]] = Field(
        None,
        description="Source users",
    )
    destination: Optional[List[str]] = Field(
        None,
        description="Destination addresses",
    )
    destination_application: Optional[Dict[str, Any]] = Field(
        None,
        description="Destination application configuration",
    )
    service: Optional[List[str]] = Field(
        None,
        description="Services",
    )
    application: Optional[List[str]] = Field(
        None,
        description="Applications",
    )
    action: Optional[PbfRuleAction] = Field(
        None,
        description="Action configuration (forward, discard, or no_pbf)",
    )
    enforce_symmetric_return: Optional[PbfRuleEnforceSymmetricReturn] = Field(
        None,
        description="Enforce symmetric return configuration",
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


class PbfRuleCreateModel(PbfRuleBaseModel):
    """Model for creating new PBF Rules."""

    @model_validator(mode="after")
    def validate_container_type(self) -> "PbfRuleCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            PbfRuleCreateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = ["folder", "snippet", "device"]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class PbfRuleUpdateModel(PbfRuleBaseModel):
    """Model for updating PBF Rules."""

    id: UUID = Field(
        ...,
        description="The UUID of the PBF rule",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class PbfRuleResponseModel(PbfRuleBaseModel):
    """Model for PBF Rule responses."""

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    id: UUID = Field(
        ...,
        description="The UUID of the PBF rule",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
