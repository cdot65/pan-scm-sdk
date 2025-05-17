"""Test factories for Log Forwarding Profile objects.

This module provides factory classes for creating test instances of Log Forwarding Profile models
used in the Palo Alto Networks Strata Cloud Manager SDK.
"""

from typing import Any, Dict, Union
from uuid import uuid4

import factory  # type: ignore
from faker import Faker

from scm.models.objects.log_forwarding_profile import (
    LogForwardingProfileBaseModel,
    LogForwardingProfileCreateModel,
    LogForwardingProfileResponseModel,
    LogForwardingProfileUpdateModel,
    MatchListItem,
)

fake = Faker()


class MatchListItemFactory(factory.Factory):
    """Factory for creating MatchListItem instances."""

    class Meta:
        model = MatchListItem

    name = factory.Sequence(lambda n: f"match_list_item_{n}")
    action_desc = factory.LazyAttribute(lambda _: fake.sentence())
    log_type = "traffic"
    filter = "addr.src in 10.0.0.0/8"
    send_http = ["http-server-1"]
    send_syslog = ["syslog-server-1"]
    send_to_panorama = True
    quarantine = False


# Base factory for all log forwarding profile models
class LogForwardingProfileBaseFactory(factory.Factory):
    """Base factory for Log Forwarding Profile with common fields."""

    class Meta:
        model = LogForwardingProfileBaseModel
        abstract = True

    name = factory.Sequence(lambda n: f"log_forwarding_profile_{n}")
    description = factory.LazyAttribute(lambda _: fake.sentence())
    match_list = factory.LazyFunction(
        lambda: [MatchListItemFactory(), MatchListItemFactory(log_type="threat")]
    )
    enhanced_application_logging = False

    # Container fields default to None
    folder = None
    snippet = None
    device = None


class LogForwardingProfileCreateApiFactory(LogForwardingProfileBaseFactory):
    """Factory for creating LogForwardingProfileCreateModel instances."""

    class Meta:
        model = LogForwardingProfileCreateModel

    # Default to folder container
    folder = "My Folder"

    @classmethod
    def with_match_list(cls, match_list=None, **kwargs):
        """Create a LogForwardingProfileCreateModel with specific match list."""
        if match_list is None:
            match_list = [
                MatchListItemFactory(log_type="traffic"),
                MatchListItemFactory(log_type="threat"),
            ]
        return cls(
            match_list=match_list,
            **kwargs,
        )

    @classmethod
    def with_empty_match_list(cls, **kwargs):
        """Create a LogForwardingProfileCreateModel with empty match list."""
        return cls(
            match_list=[],
            **kwargs,
        )

    @classmethod
    def with_enhanced_logging(cls, enabled=True, **kwargs):
        """Create a LogForwardingProfileCreateModel with enhanced application logging."""
        return cls(
            enhanced_application_logging=enabled,
            **kwargs,
        )

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Create a LogForwardingProfileCreateModel with snippet container."""
        return cls(
            folder=None,
            snippet=snippet,
            device=None,
            **kwargs,
        )

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """Create a LogForwardingProfileCreateModel with device container."""
        return cls(
            folder=None,
            snippet=None,
            device=device,
            **kwargs,
        )

    @classmethod
    def with_folder(cls, folder="TestFolder", **kwargs):
        """Create a LogForwardingProfileCreateModel with folder container."""
        return cls(
            folder=folder,
            snippet=None,
            device=None,
            **kwargs,
        )


class LogForwardingProfileUpdateApiFactory(LogForwardingProfileBaseFactory):
    """Factory for creating LogForwardingProfileUpdateModel instances."""

    class Meta:
        model = LogForwardingProfileUpdateModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    folder = "My Folder"

    @classmethod
    def with_match_list(cls, match_list=None, **kwargs):
        """Create a LogForwardingProfileUpdateModel with specific match list."""
        if match_list is None:
            match_list = [
                MatchListItemFactory(log_type="traffic"),
                MatchListItemFactory(log_type="threat"),
            ]
        return cls(
            match_list=match_list,
            **kwargs,
        )

    @classmethod
    def with_empty_match_list(cls, **kwargs):
        """Create a LogForwardingProfileUpdateModel with empty match list."""
        return cls(
            match_list=[],
            **kwargs,
        )

    @classmethod
    def with_enhanced_logging(cls, enabled=True, **kwargs):
        """Create a LogForwardingProfileUpdateModel with enhanced application logging."""
        return cls(
            enhanced_application_logging=enabled,
            **kwargs,
        )

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Create a LogForwardingProfileUpdateModel with snippet container."""
        return cls(
            folder=None,
            snippet=snippet,
            device=None,
            **kwargs,
        )

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """Create a LogForwardingProfileUpdateModel with device container."""
        return cls(
            folder=None,
            snippet=None,
            device=device,
            **kwargs,
        )

    @classmethod
    def with_folder(cls, folder="UpdatedFolder", **kwargs):
        """Create a LogForwardingProfileUpdateModel with folder container."""
        return cls(
            folder=folder,
            snippet=None,
            device=None,
            **kwargs,
        )

    @classmethod
    def without_id(cls, **kwargs):
        """Create a LogForwardingProfileUpdateModel without ID."""
        return cls(
            id=None,
            **kwargs,
        )


class LogForwardingProfileResponseFactory(LogForwardingProfileBaseFactory):
    """Factory for creating LogForwardingProfileResponseModel instances."""

    class Meta:
        model = LogForwardingProfileResponseModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    folder = "My Folder"

    @classmethod
    def build(cls, **kwargs):
        """Create a basic LogForwardingProfileResponseModel instance.

        Args:
            **kwargs: Additional keyword arguments to override default values

        Returns:
            LogForwardingProfileResponseModel: A configured log forwarding profile response model

        """
        return cls(**kwargs)

    @classmethod
    def with_match_list(cls, match_list=None, **kwargs):
        """Create a LogForwardingProfileResponseModel with specific match list."""
        if match_list is None:
            match_list = [
                MatchListItemFactory(log_type="traffic"),
                MatchListItemFactory(log_type="threat"),
            ]
        return cls(
            match_list=match_list,
            **kwargs,
        )

    @classmethod
    def with_empty_match_list(cls, **kwargs):
        """Create a LogForwardingProfileResponseModel with empty match list."""
        return cls(
            match_list=[],
            **kwargs,
        )

    @classmethod
    def with_enhanced_logging(cls, enabled=True, **kwargs):
        """Create a LogForwardingProfileResponseModel with enhanced application logging."""
        return cls(
            enhanced_application_logging=enabled,
            **kwargs,
        )

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Create a LogForwardingProfileResponseModel with snippet container."""
        return cls(
            folder=None,
            snippet=snippet,
            device=None,
            **kwargs,
        )

    @classmethod
    def with_predefined_snippet(cls, **kwargs):
        """Create a LogForwardingProfileResponseModel with predefined snippet."""
        return cls(
            id=None,
            folder=None,
            snippet="predefined-snippet",
            device=None,
            **kwargs,
        )

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """Create a LogForwardingProfileResponseModel with device container."""
        return cls(
            folder=None,
            snippet=None,
            device=device,
            **kwargs,
        )

    @classmethod
    def with_folder(cls, folder="ResponseFolder", **kwargs):
        """Create a LogForwardingProfileResponseModel with folder container."""
        return cls(
            folder=folder,
            snippet=None,
            device=None,
            **kwargs,
        )

    @classmethod
    def from_request(
        cls,
        request_model: Union[LogForwardingProfileCreateModel, Dict[str, Any]],
        **kwargs,
    ) -> LogForwardingProfileResponseModel:
        """Create a response model based on a request model.

        This is useful for simulating the API's response to a create request.

        Args:
            request_model: The create request model or dictionary to base the response on
            **kwargs: Additional attributes to override in the response

        Returns:
            LogForwardingProfileResponseModel instance

        """
        if isinstance(request_model, dict):
            data = request_model.copy()
        else:
            data = request_model.model_dump()

        # Add or override the id field if not in kwargs
        if "id" not in kwargs:
            data["id"] = str(uuid4())

        # Override with any additional kwargs
        data.update(kwargs)

        return cls(**data)


# ----------------------------------------------------------------------------
# Log Forwarding Profile model factories for Pydantic validation testing.
# ----------------------------------------------------------------------------


class LogForwardingProfileCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for LogForwardingProfileCreateModel validation testing."""

    name = "test_log_forwarding_profile"
    description = "Test log forwarding profile description"
    folder = "My Folder"
    match_list = [
        {
            "name": "traffic-match",
            "action_desc": "Match traffic logs",
            "log_type": "traffic",
            "filter": "addr.src in 10.0.0.0/8",
            "send_http": ["http-server-1"],
        },
        {
            "name": "threat-match",
            "action_desc": "Match threat logs",
            "log_type": "threat",
            "filter": "addr.dst in 192.168.0.0/16",
            "send_syslog": ["syslog-server-1"],
        },
    ]
    enhanced_application_logging = False

    @classmethod
    def build_with_no_containers(cls, **kwargs):
        """Return a data dict without any containers."""
        data = {
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "match_list": kwargs.get("match_list", cls.match_list),
            "enhanced_application_logging": kwargs.get(
                "enhanced_application_logging", cls.enhanced_application_logging
            ),
        }
        return data

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Return a data dict with multiple containers."""
        data = {
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "match_list": kwargs.get("match_list", cls.match_list),
            "enhanced_application_logging": kwargs.get(
                "enhanced_application_logging", cls.enhanced_application_logging
            ),
            "folder": "My Folder",
            "snippet": "My Snippet",
        }
        return data

    @classmethod
    def build_with_invalid_match_list(cls, **kwargs):
        """Return a data dict with invalid match list item."""
        data = {
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "match_list": [
                {
                    "name": "invalid-match",
                    "log_type": "invalid-type",  # Invalid log type
                    "filter": "addr.src in 10.0.0.0/8",
                }
            ],
            "folder": kwargs.get("folder", cls.folder),
        }
        return data

    @classmethod
    def build_valid(cls, **kwargs):
        """Return a valid data dict for validation."""
        data = {
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "match_list": kwargs.get("match_list", cls.match_list),
            "enhanced_application_logging": kwargs.get(
                "enhanced_application_logging", cls.enhanced_application_logging
            ),
            "folder": kwargs.get("folder", cls.folder),
        }
        return data


class LogForwardingProfileUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for LogForwardingProfileUpdateModel validation testing."""

    id = str(uuid4())
    name = "update_log_forwarding_profile"
    description = "Updated log forwarding profile description"
    folder = "My Folder"
    match_list = [
        {
            "name": "updated-traffic-match",
            "action_desc": "Updated match traffic logs",
            "log_type": "traffic",
            "filter": "addr.src in 172.16.0.0/12",
            "send_http": ["updated-http-server"],
        }
    ]
    enhanced_application_logging = True

    @classmethod
    def build_without_id(cls, **kwargs):
        """Return a data dict without ID."""
        data = {
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "match_list": kwargs.get("match_list", cls.match_list),
            "enhanced_application_logging": kwargs.get(
                "enhanced_application_logging", cls.enhanced_application_logging
            ),
            "folder": kwargs.get("folder", cls.folder),
        }
        return data

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Return a data dict with multiple containers."""
        data = {
            "id": kwargs.get("id", cls.id),
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "match_list": kwargs.get("match_list", cls.match_list),
            "enhanced_application_logging": kwargs.get(
                "enhanced_application_logging", cls.enhanced_application_logging
            ),
            "folder": "My Folder",
            "snippet": "My Snippet",
        }
        return data

    @classmethod
    def build_valid(cls, **kwargs):
        """Return a valid data dict for update."""
        data = {
            "id": kwargs.get("id", cls.id),
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "match_list": kwargs.get("match_list", cls.match_list),
            "enhanced_application_logging": kwargs.get(
                "enhanced_application_logging", cls.enhanced_application_logging
            ),
            "folder": kwargs.get("folder", cls.folder),
        }
        return data


class LogForwardingProfileResponseModelFactory(factory.DictFactory):
    """Factory for creating data dicts for LogForwardingProfileResponseModel validation testing."""

    id = str(uuid4())
    name = "response_log_forwarding_profile"
    description = "Response log forwarding profile description"
    folder = "My Folder"
    match_list = [
        {
            "name": "response-traffic-match",
            "action_desc": "Response match traffic logs",
            "log_type": "traffic",
            "filter": "addr.src in 10.0.0.0/8",
            "send_http": ["http-server-response"],
        }
    ]
    enhanced_application_logging = False

    @classmethod
    def build_valid(cls, **kwargs):
        """Return a valid data dict for response."""
        data = {
            "id": kwargs.get("id", cls.id),
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "match_list": kwargs.get("match_list", cls.match_list),
            "enhanced_application_logging": kwargs.get(
                "enhanced_application_logging", cls.enhanced_application_logging
            ),
            "folder": kwargs.get("folder", cls.folder),
        }
        return data

    @classmethod
    def build_predefined_snippet(cls, **kwargs):
        """Return a data dict with predefined snippet."""
        data = {
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "match_list": kwargs.get("match_list", cls.match_list),
            "enhanced_application_logging": kwargs.get(
                "enhanced_application_logging", cls.enhanced_application_logging
            ),
            "snippet": "predefined-snippet",
        }
        return data

    @classmethod
    def build_without_id(cls, **kwargs):
        """Return a data dict without ID for validation testing."""
        data = {
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "match_list": kwargs.get("match_list", cls.match_list),
            "enhanced_application_logging": kwargs.get(
                "enhanced_application_logging", cls.enhanced_application_logging
            ),
            "folder": kwargs.get("folder", cls.folder),
        }
        return data

    @classmethod
    def build_from_request(cls, request_data: Dict[str, Any], **kwargs):
        """Return a data dictionary based on request data.

        Args:
            request_data: Request data dictionary to base the response on
            **kwargs: Additional attributes to override

        Returns:
            Dictionary with response data

        """
        data = request_data.copy()

        # Add ID if not present
        if "id" not in data or "id" not in kwargs:
            data["id"] = cls.id

        # Override with any additional kwargs
        data.update(kwargs)

        return data
