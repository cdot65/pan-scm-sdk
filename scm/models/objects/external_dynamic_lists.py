# scm/models/objects/external_dynamic_lists.py

from typing import Optional, List, Union
from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    model_validator,
)


class FiveMinuteRecurringModel(BaseModel):
    five_minute: dict = Field(
        ...,
        description="Indicates update every five minutes",
    )


class HourlyRecurringModel(BaseModel):
    hourly: dict = Field(
        ...,
        description="Indicates update every hour",
    )


class DailyRecurringModel(BaseModel):
    class DailyModel(BaseModel):
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
    class WeeklyModel(BaseModel):
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
    class MonthlyModel(BaseModel):
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
    predefined_ip: PredefinedIpModel = Field(
        ...,
        description="Predefined IP configuration",
    )


class PredefinedUrlType(BaseModel):
    predefined_url: PredefinedUrlModel = Field(
        ...,
        description="Predefined URL configuration",
    )


class IpType(BaseModel):
    ip: IpModel = Field(
        ...,
        description="IP external dynamic list configuration",
    )


class DomainType(BaseModel):
    domain: DomainModel = Field(
        ...,
        description="Domain external dynamic list configuration",
    )


class UrlType(BaseModel):
    url: UrlTypeModel = Field(
        ...,
        description="URL external dynamic list configuration",
    )


class ImsiType(BaseModel):
    imsi: ImsiModel = Field(
        ...,
        description="IMSI external dynamic list configuration",
    )


class ImeiType(BaseModel):
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
    @model_validator(mode="after")
    def validate_container_type(self) -> "ExternalDynamicListsCreateModel":
        container_fields = [
            "folder",
            "snippet",
            "device",
        ]
        provided = [
            field for field in container_fields if getattr(self, field) is not None
        ]
        if len(provided) != 1:
            raise ValueError(
                "Exactly one of 'folder', 'snippet', or 'device' must be provided."
            )
        return self


class ExternalDynamicListsUpdateModel(ExternalDynamicListsBaseModel):
    id: Optional[UUID] = Field(
        None,
        description="The UUID of the external dynamic list",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class ExternalDynamicListsResponseModel(ExternalDynamicListsBaseModel):
    id: Optional[UUID] = Field(
        None,
        description="The UUID of the external dynamic list",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )

    @model_validator(mode="after")
    def validate_predefined_snippet(self) -> "ExternalDynamicListsResponseModel":
        if self.snippet != "predefined":
            if self.id is None:
                raise ValueError("id is required if snippet is not 'predefined'")
            if self.type is None:
                raise ValueError("type is required if snippet is not 'predefined'")
        return self
