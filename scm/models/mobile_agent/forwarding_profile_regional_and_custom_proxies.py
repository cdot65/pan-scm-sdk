"""Forwarding Profile Regional and Custom Proxy models for Strata Cloud Manager SDK.

Contains Pydantic models for representing GlobalProtect forwarding profile
regional and custom proxies and related data.
"""

# scm/models/mobile_agent/forwarding_profile_regional_and_custom_proxies.py

# Standard library imports
from enum import Enum
from typing import List, Optional
from uuid import UUID

# External libraries
from pydantic import BaseModel, ConfigDict, Field


class RegionalProxyType(str, Enum):
    """Available types for GlobalProtect regional and custom proxies."""

    GP_AND_PAC = "gp-and-pac"
    ZTNA_AGENT = "ztna-agent"


class RegionalProxyConnectivityName(str, Enum):
    """Available connectivity preference names for regional and custom proxies."""

    TUNNEL = "tunnel"
    PROXY = "proxy"
    ADNS = "adns"
    MASQUE = "masque"


class RegionalProxyFallbackOption(str, Enum):
    """Available fallback options for regional and custom proxies."""

    FAIL_OPEN = "fail-open"
    FAIL_SAFE = "fail-safe"


class RegionalProxyLocationPreference(str, Enum):
    """Available location preferences for regional and custom proxies."""

    BEST_AVAILABLE = "best-available-pa-location"
    SPECIFIC = "specific-pa-location"


class RegionalProxyServer(BaseModel):
    """A proxy server definition for a regional and custom proxy.

    Attributes:
        fqdn (Optional[str]): The fully qualified domain name of the proxy.
        port (Optional[int]): The port of the proxy (1-65535).
        location (Optional[str]): The location of the proxy.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    fqdn: Optional[str] = Field(
        None,
        description="The fully qualified domain name of the proxy",
        max_length=255,
        pattern=r"^([\*a-zA-Z0-9._-])+$",
    )
    port: Optional[int] = Field(
        None,
        description="The port of the proxy",
        ge=1,
        le=65535,
    )
    location: Optional[str] = Field(
        None,
        description="The location of the proxy",
    )


class RegionalProxyConnectivityPreference(BaseModel):
    """A connectivity preference entry for a regional and custom proxy.

    Attributes:
        name (RegionalProxyConnectivityName): The connectivity preference name.
        enabled (Optional[bool]): Whether the connectivity preference is enabled.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    name: RegionalProxyConnectivityName = Field(
        ...,
        description="The connectivity preference name",
    )
    enabled: Optional[bool] = Field(
        None,
        description="Whether the connectivity preference is enabled",
    )


class RegionalProxyPrismaAccessLocation(BaseModel):
    """A Prisma Access location entry for a regional and custom proxy.

    Attributes:
        name (str): The region name (one of 'americas', 'europe', 'apac').
        locations (Optional[List[str]]): List of locations in that region.

    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )

    name: str = Field(
        ...,
        description="The region name (one of 'americas', 'europe', 'apac')",
        pattern=r"^[a-zA-Z]+$",
    )
    locations: Optional[List[str]] = Field(
        None,
        description="List of locations in that region",
    )


class ForwardingProfileRegionalAndCustomProxyBaseModel(BaseModel):
    """Base model for GlobalProtect Forwarding Profile Regional and Custom Proxies.

    Contains fields common to all CRUD operations.

    Attributes:
        name (str): The name of the regional and custom proxy.
        type (RegionalProxyType): The proxy type.
        description (Optional[str]): An optional description.
        proxy_1 (Optional[RegionalProxyServer]): The primary proxy server.
        proxy_2 (Optional[RegionalProxyServer]): The secondary proxy server.
        connectivity_preference (Optional[List[RegionalProxyConnectivityPreference]]):
            Connectivity preference entries.
        fallback_option (Optional[RegionalProxyFallbackOption]): The fallback option.
        location_preference (Optional[RegionalProxyLocationPreference]): The location
            preference.
        prisma_access_locations (Optional[List[RegionalProxyPrismaAccessLocation]]):
            Prisma Access locations (Americas, Europe, and Asia-Pacific).

    """

    # Pydantic model configuration
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    # Required fields
    name: str = Field(
        ...,
        description="The name of the regional and custom proxy",
        max_length=64,
        pattern=r"^[0-9a-zA-Z._-]+$",
    )

    # Optional fields
    type: RegionalProxyType = Field(
        default=RegionalProxyType.GP_AND_PAC,
        description="The proxy type",
    )
    description: Optional[str] = Field(
        None,
        description="An optional description of the regional and custom proxy",
        max_length=1023,
    )
    proxy_1: Optional[RegionalProxyServer] = Field(
        None,
        description="The primary proxy server",
    )
    proxy_2: Optional[RegionalProxyServer] = Field(
        None,
        description="The secondary proxy server",
    )
    connectivity_preference: Optional[List[RegionalProxyConnectivityPreference]] = Field(
        None,
        description="Connectivity preference entries",
    )
    fallback_option: Optional[RegionalProxyFallbackOption] = Field(
        None,
        description="The fallback option",
    )
    location_preference: Optional[RegionalProxyLocationPreference] = Field(
        None,
        description="The location preference",
    )
    prisma_access_locations: Optional[List[RegionalProxyPrismaAccessLocation]] = Field(
        None,
        description="Prisma Access locations (Americas, Europe, and Asia-Pacific)",
    )


class ForwardingProfileRegionalAndCustomProxyCreateModel(
    ForwardingProfileRegionalAndCustomProxyBaseModel
):
    """Represents the creation of a new GlobalProtect Regional and Custom Proxy."""


class ForwardingProfileRegionalAndCustomProxyUpdateModel(
    ForwardingProfileRegionalAndCustomProxyBaseModel
):
    """Represents the update of an existing GlobalProtect Regional and Custom Proxy.

    Attributes:
        id (UUID): The UUID of the regional and custom proxy.

    """

    id: UUID = Field(
        ...,
        description="The UUID of the regional and custom proxy",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class ForwardingProfileRegionalAndCustomProxyResponseModel(
    ForwardingProfileRegionalAndCustomProxyBaseModel
):
    """Represents a GlobalProtect Regional and Custom Proxy returned by the API.

    Attributes:
        id (UUID): The UUID of the regional and custom proxy.

    """

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    id: UUID = Field(
        ...,
        description="The UUID of the regional and custom proxy",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
