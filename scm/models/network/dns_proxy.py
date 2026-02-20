"""DNS Proxy models for Strata Cloud Manager SDK.

Contains Pydantic models for representing DNS proxy objects and related data.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


# --- Sub-Models ---


class DnsProxyDefaultServer(BaseModel):
    """Default DNS server configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    inheritance: Optional[Dict[str, Any]] = Field(
        None,
        description="Inheritance settings with 'source' (dynamic interface)",
    )
    primary: str = Field(
        ...,
        description="Primary DNS Name server IP address",
    )
    secondary: Optional[str] = Field(
        None,
        description="Secondary DNS Name server IP address",
    )


class DnsProxyDomainServer(BaseModel):
    """DNS proxy rule (domain server) entry."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(
        ...,
        description="Proxy rule name",
    )
    cacheable: Optional[bool] = Field(
        None,
        description="Enable caching for this DNS proxy rule",
    )
    domain_name: Optional[List[str]] = Field(
        None,
        description="Domain names that will be matched",
        alias="domain-name",
    )
    primary: str = Field(
        ...,
        description="Primary DNS server IP address",
    )
    secondary: Optional[str] = Field(
        None,
        description="Secondary DNS server IP address",
    )


class DnsProxyStaticEntry(BaseModel):
    """Static domain name mapping entry."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    name: str = Field(
        ...,
        description="Static entry name",
        max_length=31,
    )
    domain: str = Field(
        ...,
        description="Fully qualified domain name",
        max_length=255,
    )
    address: List[str] = Field(
        ...,
        description="Resolved IP addresses",
    )


class DnsProxyTcpQueries(BaseModel):
    """TCP queries configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    enabled: bool = Field(
        ...,
        description="Turn on forwarding of TCP DNS queries",
    )
    max_pending_requests: Optional[int] = Field(
        None,
        description="Upper limit on number of concurrent TCP DNS requests",
        ge=64,
        le=256,
        alias="max-pending-requests",
    )


class DnsProxyUdpRetries(BaseModel):
    """UDP query retry configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    interval: Optional[int] = Field(
        None,
        description="Time in seconds for another request to be sent",
        ge=1,
        le=30,
    )
    attempts: Optional[int] = Field(
        None,
        description="Maximum number of retries before trying next name server",
        ge=1,
        le=30,
    )


class DnsProxyUdpQueries(BaseModel):
    """UDP queries configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    retries: Optional[DnsProxyUdpRetries] = Field(
        None,
        description="Retry configuration for UDP queries",
    )


class DnsProxyCacheMaxTtl(BaseModel):
    """Cache max TTL configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    enabled: bool = Field(
        ...,
        description="Enable max TTL for this DNS object",
    )
    time_to_live: Optional[int] = Field(
        None,
        description="Time in seconds after which entry is cleared",
        ge=60,
        le=86400,
        alias="time-to-live",
    )


class DnsProxyCache(BaseModel):
    """DNS cache configuration."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

    enabled: bool = Field(
        ...,
        description="Turn on caching for this DNS object",
    )
    cache_edns: Optional[bool] = Field(
        None,
        description="Cache EDNS UDP response",
        alias="cache-edns",
    )
    max_ttl: Optional[DnsProxyCacheMaxTtl] = Field(
        None,
        description="Maximum TTL configuration",
        alias="max-ttl",
    )


# --- Main Models ---


class DnsProxyBaseModel(BaseModel):
    """Base model for DNS Proxy configurations."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    name: str = Field(
        ...,
        description="DNS proxy name",
        max_length=31,
    )
    enabled: Optional[bool] = Field(
        None,
        description="Enable DNS proxy",
    )
    default: Optional[DnsProxyDefaultServer] = Field(
        None,
        description="Default DNS server configuration",
    )
    interface: Optional[List[str]] = Field(
        None,
        description="Interfaces on which to enable DNS proxy service",
    )
    domain_servers: Optional[List[DnsProxyDomainServer]] = Field(
        None,
        description="DNS proxy rules (domain servers)",
        alias="domain-servers",
    )
    static_entries: Optional[List[DnsProxyStaticEntry]] = Field(
        None,
        description="Static domain name mappings",
        alias="static-entries",
    )
    tcp_queries: Optional[DnsProxyTcpQueries] = Field(
        None,
        description="TCP queries configuration",
        alias="tcp-queries",
    )
    udp_queries: Optional[DnsProxyUdpQueries] = Field(
        None,
        description="UDP queries configuration",
        alias="udp-queries",
    )
    cache: Optional[DnsProxyCache] = Field(
        None,
        description="DNS cache configuration",
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


class DnsProxyCreateModel(DnsProxyBaseModel):
    """Model for creating new DNS Proxy configurations."""

    @model_validator(mode="after")
    def validate_container_type(self) -> "DnsProxyCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            DnsProxyCreateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = ["folder", "snippet", "device"]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class DnsProxyUpdateModel(DnsProxyBaseModel):
    """Model for updating DNS Proxy configurations."""

    id: UUID = Field(
        ...,
        description="The UUID of the resource",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class DnsProxyResponseModel(DnsProxyBaseModel):
    """Model for DNS Proxy responses."""

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    id: UUID = Field(
        ...,
        description="The UUID of the resource",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
