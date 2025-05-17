"""External Dynamic Lists models for Strata Cloud Manager SDK.

Contains Pydantic models for representing external dynamic list objects and related data.
"""

# scm/models/objects/external_dynamic_lists.py

from typing import List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class FiveMinuteRecurringModel(BaseModel):
    """Model for a recurring schedule that updates every five minutes."""

    five_minute: dict = Field(
        ...,
        description="Indicates update every five minutes",
    )


class HourlyRecurringModel(BaseModel):
    """Model for a recurring schedule that updates every hour."""

    hourly: dict = Field(
        ...,
        description="Indicates update every hour",
    )


class DailyRecurringModel(BaseModel):
    """Model for a recurring schedule that updates daily at a specified hour."""

    class DailyModel(BaseModel):
        """Model representing the daily time specification for recurring updates."""

        at: str = Field(
            default="00",
            description="Time specification hh (e.g. 20)",
            pattern="([01][0-9]|[2][0-3])",
            min_length=2,
            max_length=2,
        )

    daily: DailyModel = Field(
        ...,
        description="Recurring daily update configuration",
    )


class WeeklyRecurringModel(BaseModel):
    """Model for a recurring schedule that updates weekly on a specified day and hour."""

    class WeeklyModel(BaseModel):
        """Model representing the day and time specification for weekly recurring updates."""

        day_of_week: str = Field(
            ...,
            description="Day of the week",
            pattern="^(sunday|monday|tuesday|wednesday|thursday|friday|saturday)$",
        )
        at: str = Field(
            default="00",
            description="Time specification hh (e.g. 20)",
            pattern="([01][0-9]|[2][0-3])",
            min_length=2,
            max_length=2,
        )

    weekly: WeeklyModel = Field(
        ...,
        description="Recurring weekly update configuration",
    )


class MonthlyRecurringModel(BaseModel):
    """Model for a recurring schedule that updates monthly on a specified day and hour."""

    class MonthlyModel(BaseModel):
        """Model representing the day and time specification for monthly recurring updates."""

        day_of_month: int = Field(
            ...,
            description="Day of month",
            ge=1,
            le=31,
        )
        at: str = Field(
            default="00",
            description="Time specification hh (e.g. 20)",
            pattern="([01][0-9]|[2][0-3])",
            min_length=2,
            max_length=2,
        )

    monthly: MonthlyModel = Field(
        ...,
        description="Recurring monthly update configuration",
    )


RecurringUnion = Union[
    FiveMinuteRecurringModel,
    HourlyRecurringModel,
    DailyRecurringModel,
    WeeklyRecurringModel,
    MonthlyRecurringModel,
]


class AuthModel(BaseModel):
    """Model for authentication credentials used in dynamic list sources."""

    username: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Authentication username",
    )
    password: str = Field(
        ...,
        max_length=255,
        description="Authentication password",
    )


class PredefinedIpModel(BaseModel):
    """Model for a predefined IP list external dynamic list entry."""

    exception_list: Optional[List[str]] = Field(
        None,
        description="Exception list entries",
    )
    description: Optional[str] = Field(
        None,
        max_length=255,
        description="Description of the predefined IP list",
    )
    url: str = Field(
        ...,
        description="URL for the predefined IP list",
    )


class PredefinedUrlModel(BaseModel):
    """Model for a predefined URL list external dynamic list entry."""

    exception_list: Optional[List[str]] = Field(
        None,
        description="Exception list entries",
    )
    description: Optional[str] = Field(
        None,
        max_length=255,
        description="Description of the predefined URL list",
    )
    url: str = Field(
        ...,
        description="URL for the predefined URL list",
    )


class IpModel(BaseModel):
    """Model for an IP external dynamic list entry."""

    exception_list: Optional[List[str]] = Field(
        None,
        description="Exception list entries",
    )
    description: Optional[str] = Field(
        None,
        max_length=255,
        description="Description of the IP list",
    )
    url: str = Field(
        default="http://",  # noqa
        max_length=255,
        description="URL for the IP list",
    )
    certificate_profile: Optional[str] = Field(
        None,
        description="Profile for authenticating client certificates",
    )
    auth: Optional[AuthModel] = Field(
        None,
        description="Authentication credentials",
    )
    recurring: RecurringUnion = Field(
        ...,
        description="Recurring interval for updates",
    )


class DomainModel(BaseModel):
    """Model for a domain external dynamic list entry."""

    exception_list: Optional[List[str]] = Field(
        None,
        description="Exception list entries",
    )
    description: Optional[str] = Field(
        None,
        max_length=255,
        description="Description of the domain list",
    )
    url: str = Field(
        default="http://",  # noqa
        max_length=255,
        description="URL for the domain list",
    )
    certificate_profile: Optional[str] = Field(
        None,
        description="Profile for authenticating client certificates",
    )
    auth: Optional[AuthModel] = Field(
        None,
        description="Authentication credentials",
    )
    recurring: RecurringUnion = Field(
        ...,
        description="Recurring interval for updates",
    )
    expand_domain: Optional[bool] = Field(
        False,
        description="Enable/Disable expand domain",
    )


class UrlTypeModel(BaseModel):
    """Model for a URL external dynamic list entry."""

    exception_list: Optional[List[str]] = Field(
        None,
        description="Exception list entries",
    )
    description: Optional[str] = Field(
        None,
        max_length=255,
        description="Description of the URL list",
    )
    url: str = Field(
        default="http://",  # noqa
        max_length=255,
        description="URL for the URL list",
    )
    certificate_profile: Optional[str] = Field(
        None,
        description="Profile for authenticating client certificates",
    )
    auth: Optional[AuthModel] = Field(
        None,
        description="Authentication credentials",
    )
    recurring: RecurringUnion = Field(
        ...,
        description="Recurring interval for updates",
    )


class ImsiModel(BaseModel):
    """Model for an IMSI external dynamic list entry."""

    exception_list: Optional[List[str]] = Field(
        None,
        description="Exception list entries",
    )
    description: Optional[str] = Field(
        None,
        max_length=255,
        description="Description of the IMSI list",
    )
    url: str = Field(
        default="http://",  # noqa
        max_length=255,
        description="URL for the IMSI list",
    )
    certificate_profile: Optional[str] = Field(
        None,
        description="Profile for authenticating client certificates",
    )
    auth: Optional[AuthModel] = Field(
        None,
        description="Authentication credentials",
    )
    recurring: RecurringUnion = Field(
        ...,
        description="Recurring interval for updates",
    )


class ImeiModel(BaseModel):
    """Model for an IMEI external dynamic list entry."""

    exception_list: Optional[List[str]] = Field(
        None,
        description="Exception list entries",
    )
    description: Optional[str] = Field(
        None,
        max_length=255,
        description="Description of the IMEI list",
    )
    url: str = Field(
        default="http://",  # noqa
        max_length=255,
        description="URL for the IMEI list",
    )
    certificate_profile: Optional[str] = Field(
        None,
        description="Profile for authenticating client certificates",
    )
    auth: Optional[AuthModel] = Field(
        None,
        description="Authentication credentials",
    )
    recurring: RecurringUnion = Field(
        ...,
        description="Recurring interval for updates",
    )


class PredefinedIpType(BaseModel):
    """Type wrapper for predefined IP external dynamic list model."""

    predefined_ip: PredefinedIpModel = Field(
        ...,
        description="Predefined IP configuration",
    )


class PredefinedUrlType(BaseModel):
    """Type wrapper for predefined URL external dynamic list model."""

    predefined_url: PredefinedUrlModel = Field(
        ...,
        description="Predefined URL configuration",
    )


class IpType(BaseModel):
    """Type wrapper for IP external dynamic list model."""

    ip: IpModel = Field(
        ...,
        description="IP external dynamic list configuration",
    )


class DomainType(BaseModel):
    """Type wrapper for domain external dynamic list model."""

    domain: DomainModel = Field(
        ...,
        description="Domain external dynamic list configuration",
    )


class UrlType(BaseModel):
    """Type wrapper for URL external dynamic list model."""

    url: UrlTypeModel = Field(
        ...,
        description="URL external dynamic list configuration",
    )


class ImsiType(BaseModel):
    """Type wrapper for IMSI external dynamic list model."""

    imsi: ImsiModel = Field(
        ...,
        description="IMSI external dynamic list configuration",
    )


class ImeiType(BaseModel):
    """Type wrapper for IMEI external dynamic list model."""

    imei: ImeiModel = Field(
        ...,
        description="IMEI external dynamic list configuration",
    )


TypeUnion = Union[
    PredefinedIpType,
    PredefinedUrlType,
    IpType,
    DomainType,
    UrlType,
    ImsiType,
    ImeiType,
]


class ExternalDynamicListsBaseModel(BaseModel):
    """Base model for external dynamic lists, containing common fields and configuration."""

    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    name: str = Field(
        ...,
        max_length=63,
        description="The name of the external dynamic list",
        pattern=r"^[ a-zA-Z\d.\-_]+$",
    )
    type: Optional[TypeUnion] = Field(
        None,
        description="The type definition of the external dynamic list",
    )

    folder: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z\d\-_\. ]+$",
        max_length=64,
        description="The folder in which the resource is defined",
        examples=["My Folder"],
    )
    snippet: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z\d\-_\. ]+$",
        max_length=64,
        description="The snippet in which the resource is defined",
        examples=["My Snippet"],
    )
    device: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z\d\-_\. ]+$",
        max_length=64,
        description="The device in which the resource is defined",
        examples=["My Device"],
    )


class ExternalDynamicListsCreateModel(ExternalDynamicListsBaseModel):
    """Model for creating an external dynamic list resource."""

    @model_validator(mode="after")
    def validate_container_type(self) -> "ExternalDynamicListsCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            ExternalDynamicListsCreateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = [
            "folder",
            "snippet",
            "device",
        ]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class ExternalDynamicListsUpdateModel(ExternalDynamicListsBaseModel):
    """Model for updating an external dynamic list resource."""

    id: Optional[UUID] = Field(
        None,
        description="The UUID of the external dynamic list",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class ExternalDynamicListsResponseModel(ExternalDynamicListsBaseModel):
    """Model for responses representing an external dynamic list resource."""

    id: Optional[UUID] = Field(
        None,
        description="The UUID of the external dynamic list",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )

    @model_validator(mode="after")
    def validate_predefined_snippet(self) -> "ExternalDynamicListsResponseModel":
        """Validate that required fields are set if snippet is not 'predefined'.

        Returns:
            ExternalDynamicListsResponseModel: The validated model instance.

        Raises:
            ValueError: If id or type is missing when snippet is not 'predefined'.

        """
        if self.snippet != "predefined":
            if self.id is None:
                raise ValueError("id is required if snippet is not 'predefined'")
            if self.type is None:
                raise ValueError("type is required if snippet is not 'predefined'")
        return self
