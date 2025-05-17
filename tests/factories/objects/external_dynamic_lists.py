"""Test factories for External Dynamic Lists objects."""

from typing import Any, Dict, Optional, Union
from uuid import uuid4

import factory  # type: ignore
from faker import Faker

from scm.models.objects.external_dynamic_lists import (
    ExternalDynamicListsBaseModel,
    ExternalDynamicListsCreateModel,
    ExternalDynamicListsResponseModel,
    ExternalDynamicListsUpdateModel,
)

fake = Faker()


# Base factory for all external dynamic lists models
class ExternalDynamicListsBaseFactory(factory.Factory):
    """Base factory for External Dynamic Lists with common fields."""

    class Meta:
        """Meta class that defines the model for ExternalDynamicListsBaseFactory."""

        model = ExternalDynamicListsBaseModel
        abstract = True

    name = factory.Sequence(lambda n: f"edl_{n}")
    folder: Optional[str] = None
    snippet: Optional[str] = None
    device: Optional[str] = None
    type: Optional[Dict[str, Any]] = None


class ExternalDynamicListsCreateApiFactory(ExternalDynamicListsBaseFactory):
    """Factory for creating ExternalDynamicListsCreateModel instances."""

    class Meta:
        """Meta class that defines the model for ExternalDynamicListsCreateModelFactory."""

        model = ExternalDynamicListsCreateModel

    # Default to folder and IP type
    folder = "My Folder"
    type = {
        "ip": {
            "url": "http://example.com/edl.txt",
            "recurring": {"daily": {"at": "03"}},
        }
    }

    @classmethod
    def with_ip_type(cls, url="http://example.com/ip-list.txt", **kwargs):
        """Create an instance with IP type configuration."""
        return cls(
            type={
                "ip": {
                    "url": url,
                    "recurring": {"daily": {"at": "03"}},
                }
            },
            **kwargs,
        )

    @classmethod
    def with_domain_type(cls, url="http://example.com/domain-list.txt", **kwargs):
        """Create an instance with domain type configuration."""
        return cls(
            type={
                "domain": {
                    "url": url,
                    "recurring": {"daily": {"at": "03"}},
                }
            },
            **kwargs,
        )

    @classmethod
    def with_url_type(cls, url="http://example.com/url-list.txt", **kwargs):
        """Create an instance with URL type configuration."""
        return cls(
            type={
                "url": {
                    "url": url,
                    "recurring": {"daily": {"at": "03"}},
                }
            },
            **kwargs,
        )

    @classmethod
    def with_imsi_type(cls, url="http://example.com/imsi-list.txt", **kwargs):
        """Create an instance with IMSI type configuration."""
        return cls(
            type={
                "imsi": {
                    "url": url,
                    "recurring": {"daily": {"at": "03"}},
                }
            },
            **kwargs,
        )

    @classmethod
    def with_imei_type(cls, url="http://example.com/imei-list.txt", **kwargs):
        """Create an instance with IMEI type configuration."""
        return cls(
            type={
                "imei": {
                    "url": url,
                    "recurring": {"daily": {"at": "03"}},
                }
            },
            **kwargs,
        )

    @classmethod
    def with_predefined_ip_type(cls, type_id="predefined-ip", **kwargs):
        """Create an instance with predefined IP type configuration."""
        return cls(
            type={
                "predefined": {
                    "type": "ip",
                    "id": type_id,
                }
            },
            **kwargs,
        )

    @classmethod
    def with_predefined_url_type(cls, type_id="predefined-url", **kwargs):
        """Create an instance with predefined URL type configuration."""
        return cls(
            type={
                "predefined": {
                    "type": "url",
                    "id": type_id,
                }
            },
            **kwargs,
        )

    @classmethod
    def with_five_minute_recurring(cls, **kwargs):
        """Create an instance with five-minute recurring schedule."""
        type_data = cls.with_ip_type().type
        type_key = next(iter(type_data.keys()))
        type_data[type_key]["recurring"] = {"five-minute": {}}
        return cls(type=type_data, **kwargs)

    @classmethod
    def with_hourly_recurring(cls, minute="30", **kwargs):
        """Create an instance with hourly recurring schedule."""
        type_data = cls.with_ip_type().type
        type_key = next(iter(type_data.keys()))
        type_data[type_key]["recurring"] = {"hourly": {"at": minute}}
        return cls(type=type_data, **kwargs)

    @classmethod
    def with_daily_recurring(cls, hour="12", **kwargs):
        """Create an instance with daily recurring schedule."""
        type_data = cls.with_ip_type().type
        type_key = next(iter(type_data.keys()))
        type_data[type_key]["recurring"] = {"daily": {"at": hour}}
        return cls(type=type_data, **kwargs)

    @classmethod
    def with_weekly_recurring(cls, day="monday", hour="12", **kwargs):
        """Create an instance with weekly recurring schedule."""
        type_data = cls.with_ip_type().type
        type_key = next(iter(type_data.keys()))
        type_data[type_key]["recurring"] = {"weekly": {"day": day, "at": hour}}
        return cls(type=type_data, **kwargs)

    @classmethod
    def with_monthly_recurring(cls, day="1", hour="12", **kwargs):
        """Create an instance with monthly recurring schedule."""
        type_data = cls.with_ip_type().type
        type_key = next(iter(type_data.keys()))
        type_data[type_key]["recurring"] = {"monthly": {"day": day, "at": hour}}
        return cls(type=type_data, **kwargs)

    @classmethod
    def with_certificate_profile(cls, cert_profile="default", **kwargs):
        """Create an instance with certificate profile."""
        type_data = cls.with_ip_type().type
        type_key = next(iter(type_data.keys()))
        type_data[type_key]["certificate_profile"] = cert_profile
        return cls(type=type_data, **kwargs)

    @classmethod
    def with_auth(cls, username="admin", password="password", **kwargs):
        """Create an instance with authentication."""
        type_data = cls.with_ip_type().type
        type_key = next(iter(type_data.keys()))
        type_data[type_key]["auth"] = {"username": username, "password": password}
        return cls(type=type_data, **kwargs)

    @classmethod
    def with_disabled_auth(cls, **kwargs):
        """Create an instance with disabled authentication."""
        type_data = cls.with_ip_type().type
        type_key = next(iter(type_data.keys()))
        type_data[type_key]["auth"] = {"disable": True}
        return cls(type=type_data, **kwargs)

    @classmethod
    def with_exception_list(cls, ips=None, **kwargs):
        """Create an instance with exception list."""
        if ips is None:
            ips = ["192.168.1.1", "10.0.0.1"]
        type_data = cls.with_ip_type().type
        type_key = next(iter(type_data.keys()))
        type_data[type_key]["exception_list"] = ips
        return cls(type=type_data, **kwargs)

    @classmethod
    def with_snippet(cls, snippet="MySnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device="MyDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def with_folder(cls, folder="MyFolder", **kwargs):
        """Create an instance with folder container."""
        return cls(folder=folder, snippet=None, device=None, **kwargs)

    @classmethod
    def with_invalid_name(cls, **kwargs):
        """Create an instance with an invalid name (exceeding max length)."""
        return cls(name="a" * 64, **kwargs)  # Name exceeds max length of 63

    @classmethod
    def with_invalid_recurring_format(cls, **kwargs):
        """Create an instance with an invalid recurring format."""
        return cls(
            type={
                "ip": {
                    "url": "http://example.com/edl.txt",
                    "recurring": {"daily": {"at": "25"}},  # Invalid hour (must be 00-23)
                }
            },
            **kwargs,
        )

    @classmethod
    def with_no_container(cls, **kwargs):
        """Create an instance without any container."""
        return cls(folder=None, snippet=None, device=None, **kwargs)

    @classmethod
    def with_multiple_containers(cls, **kwargs):
        """Create an instance with multiple containers."""
        return cls(folder="FolderA", snippet="SnippetA", **kwargs)

    @classmethod
    def with_predefined_snippet(cls, **kwargs):
        """Create an instance with snippet='predefined' and no type."""
        return cls(folder=None, snippet="predefined", type=None, **kwargs)


class ExternalDynamicListsUpdateApiFactory(ExternalDynamicListsBaseFactory):
    """Factory for creating ExternalDynamicListsUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for ExternalDynamicListsUpdateModelFactory."""

        model = ExternalDynamicListsUpdateModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    name = factory.Sequence(lambda n: f"edl_update_{n}")
    folder = "My Folder"
    type = {
        "ip": {
            "url": "http://example.com/updated-edl.txt",
            "recurring": {"daily": {"at": "05"}},
        }
    }

    @classmethod
    def with_ip_type(cls, url="http://example.com/ip-list-updated.txt", **kwargs):
        """Create an instance with IP type configuration."""
        return cls(
            type={
                "ip": {
                    "url": url,
                    "recurring": {"daily": {"at": "05"}},
                }
            },
            **kwargs,
        )

    @classmethod
    def with_domain_type(cls, url="http://example.com/domain-list-updated.txt", **kwargs):
        """Create an instance with domain type configuration."""
        return cls(
            type={
                "domain": {
                    "url": url,
                    "recurring": {"daily": {"at": "05"}},
                }
            },
            **kwargs,
        )

    @classmethod
    def with_url_type(cls, url="http://example.com/url-list-updated.txt", **kwargs):
        """Create an instance with URL type configuration."""
        return cls(
            type={
                "url": {
                    "url": url,
                    "recurring": {"daily": {"at": "05"}},
                }
            },
            **kwargs,
        )

    @classmethod
    def with_certificate_profile(cls, cert_profile="updated-cert", **kwargs):
        """Create an instance with certificate profile."""
        type_data = cls.with_ip_type().type
        type_key = next(iter(type_data.keys()))
        type_data[type_key]["certificate_profile"] = cert_profile
        return cls(type=type_data, **kwargs)

    @classmethod
    def with_auth(cls, username="updated-admin", password="updated-password", **kwargs):
        """Create an instance with authentication."""
        type_data = cls.with_ip_type().type
        type_key = next(iter(type_data.keys()))
        type_data[type_key]["auth"] = {"username": username, "password": password}
        return cls(type=type_data, **kwargs)

    @classmethod
    def with_disabled_auth(cls, **kwargs):
        """Create an instance with disabled authentication."""
        type_data = cls.with_ip_type().type
        type_key = next(iter(type_data.keys()))
        type_data[type_key]["auth"] = {"disable": True}
        return cls(type=type_data, **kwargs)

    @classmethod
    def with_exception_list(cls, ips=None, **kwargs):
        """Create an instance with exception list."""
        if ips is None:
            ips = ["192.168.1.100", "10.0.0.100"]
        type_data = cls.with_ip_type().type
        type_key = next(iter(type_data.keys()))
        type_data[type_key]["exception_list"] = ips
        return cls(type=type_data, **kwargs)

    @classmethod
    def with_daily_recurring(cls, hour="10", **kwargs):
        """Create an instance with daily recurring schedule."""
        type_data = cls.with_ip_type().type
        type_key = next(iter(type_data.keys()))
        type_data[type_key]["recurring"] = {"daily": {"at": hour}}
        return cls(type=type_data, **kwargs)

    @classmethod
    def with_weekly_recurring(cls, day="friday", hour="10", **kwargs):
        """Create an instance with weekly recurring schedule."""
        type_data = cls.with_ip_type().type
        type_key = next(iter(type_data.keys()))
        type_data[type_key]["recurring"] = {"weekly": {"day": day, "at": hour}}
        return cls(type=type_data, **kwargs)

    @classmethod
    def with_monthly_recurring(cls, day="15", hour="10", **kwargs):
        """Create an instance with monthly recurring schedule."""
        type_data = cls.with_ip_type().type
        type_key = next(iter(type_data.keys()))
        type_data[type_key]["recurring"] = {"monthly": {"day": day, "at": hour}}
        return cls(type=type_data, **kwargs)

    @classmethod
    def with_snippet(cls, snippet="UpdatedSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device="UpdatedDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def with_folder(cls, folder="UpdatedFolder", **kwargs):
        """Create an instance with folder container."""
        return cls(folder=folder, snippet=None, device=None, **kwargs)

    @classmethod
    def without_id(cls, **kwargs):
        """Create an instance without ID."""
        return cls(id=None, **kwargs)


class ExternalDynamicListsResponseFactory(ExternalDynamicListsBaseFactory):
    """Factory for creating ExternalDynamicListsResponseModel instances."""

    class Meta:
        """Meta class that defines the model for ExternalDynamicListsResponseModelFactory."""

        model = ExternalDynamicListsResponseModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    name = factory.Sequence(lambda n: f"edl_resp_{n}")
    folder = "My Folder"
    type = {
        "ip": {
            "url": "http://example.com/edl.txt",
            "recurring": {"daily": {"at": "03"}},
        }
    }

    @classmethod
    def with_ip_type(cls, url="http://example.com/ip-list.txt", **kwargs):
        """Create an instance with IP type configuration."""
        return cls(
            type={
                "ip": {
                    "url": url,
                    "recurring": {"daily": {"at": "03"}},
                }
            },
            **kwargs,
        )

    @classmethod
    def with_domain_type(cls, url="http://example.com/domain-list.txt", **kwargs):
        """Create an instance with domain type configuration."""
        return cls(
            type={
                "domain": {
                    "url": url,
                    "recurring": {"daily": {"at": "03"}},
                }
            },
            **kwargs,
        )

    @classmethod
    def with_url_type(cls, url="http://example.com/url-list.txt", **kwargs):
        """Create an instance with URL type configuration."""
        return cls(
            type={
                "url": {
                    "url": url,
                    "recurring": {"daily": {"at": "03"}},
                }
            },
            **kwargs,
        )

    @classmethod
    def with_predefined_snippet(cls, **kwargs):
        """Create an instance with predefined snippet."""
        return cls(id=None, snippet="predefined", type=None, **kwargs)

    @classmethod
    def with_non_predefined_snippet_no_id(cls, **kwargs):
        """Create an instance with non-predefined snippet and no ID."""
        return cls(id=None, snippet="My Snippet", **kwargs)

    @classmethod
    def with_non_predefined_snippet_no_type(cls, **kwargs):
        """Create an instance with non-predefined snippet and no type."""
        return cls(snippet="My Snippet", type=None, **kwargs)

    @classmethod
    def from_request(
        cls, request_model: Union[ExternalDynamicListsCreateModel, Dict[str, Any]], **kwargs
    ) -> ExternalDynamicListsResponseModel:
        """Create a response model based on a request model.

        This is useful for simulating the API's response to a create request.

        Args:
            request_model: The create request model or dictionary to base the response on
            **kwargs: Additional attributes to override in the response

        Returns:
            ExternalDynamicListsResponseModel instance

        """
        if isinstance(request_model, ExternalDynamicListsCreateModel):
            data = request_model.model_dump()
        else:
            data = request_model.copy()

        data["id"] = str(uuid4())
        data.update(kwargs)
        return ExternalDynamicListsResponseModel(**data)


# ----------------------------------------------------------------------------
# External Dynamic Lists model factories for Pydantic validation testing.
# ----------------------------------------------------------------------------


class ExternalDynamicListsCreateModelFactory(factory.DictFactory):
    """Factory for creating dictionary data for ExternalDynamicListsCreateModel validation testing."""

    name = "edl_test"
    folder = "My Folder"  # Default to folder as the container
    type = {
        "ip": {
            "url": "http://example.com/edl.txt",
            "recurring": {"daily": {"at": "03"}},
        }
    }

    @classmethod
    def build_ip_type(cls, url="http://example.com/ip-list.txt", **kwargs) -> dict:
        """Return a data dictionary with IP type."""
        data = {
            "type": {
                "ip": {
                    "url": url,
                    "recurring": {"daily": {"at": "03"}},
                }
            }
        }
        data.update(kwargs)
        return data

    @classmethod
    def build_domain_type(cls, url="http://example.com/domain-list.txt", **kwargs) -> dict:
        """Return a data dictionary with domain type."""
        data = {
            "type": {
                "domain": {
                    "url": url,
                    "recurring": {"daily": {"at": "03"}},
                }
            }
        }
        data.update(kwargs)
        return data

    @classmethod
    def build_url_type(cls, url="http://example.com/url-list.txt", **kwargs) -> dict:
        """Return a data dictionary with URL type."""
        data = {
            "type": {
                "url": {
                    "url": url,
                    "recurring": {"daily": {"at": "03"}},
                }
            }
        }
        data.update(kwargs)
        return data

    @classmethod
    def build_without_container(cls, **kwargs) -> dict:
        """Return a data dictionary without any container."""
        data = cls.build_valid()
        data.pop("folder", None)
        return data

    @classmethod
    def build_multiple_containers(cls, **kwargs) -> dict:
        """Return a data dictionary with multiple containers."""
        data = cls.build_valid()
        data["snippet"] = "SnippetA"
        return data

    @classmethod
    def build_predefined_snippet(cls, **kwargs) -> dict:
        """Return a data dictionary with predefined snippet and no type."""
        data = {
            "name": "edl_predefined_test",
            "snippet": "predefined",
        }
        data.update(kwargs)
        return data

    @classmethod
    def build_valid(cls, **kwargs) -> dict:
        """Return a data dictionary with all valid attributes."""
        data = {
            "name": "edl_valid_test",
            "folder": "My Folder",
            "type": {
                "ip": {
                    "url": "http://example.com/edl.txt",
                    "recurring": {"daily": {"at": "03"}},
                }
            },
        }
        data.update(kwargs)
        return data


class ExternalDynamicListsUpdateModelFactory(factory.DictFactory):
    """Factory for creating dictionary data for ExternalDynamicListsUpdateModel validation testing."""

    id = str(uuid4())
    name = "edl_update_test"
    folder = "My Folder"
    type = {
        "ip": {
            "url": "http://example.com/edl.txt",
            "recurring": {"daily": {"at": "03"}},
        }
    }

    @classmethod
    def build_without_id(cls, **kwargs) -> dict:
        """Return a data dictionary without ID."""
        data = cls.build_valid()
        data.pop("id", None)
        return data

    @classmethod
    def build_with_auth(cls, username="admin", password="password", **kwargs) -> dict:
        """Return a data dictionary with authentication."""
        data = cls.build_valid()
        type_key = next(iter(data["type"].keys()))
        data["type"][type_key]["auth"] = {"username": username, "password": password}
        return data

    @classmethod
    def build_without_container(cls, **kwargs) -> dict:
        """Return a data dictionary without any container."""
        data = cls.build_valid()
        data.pop("folder", None)
        return data

    @classmethod
    def build_multiple_containers(cls, **kwargs) -> dict:
        """Return a data dictionary with multiple containers."""
        data = cls.build_valid()
        data["snippet"] = "SnippetA"
        return data

    @classmethod
    def build_valid(cls, **kwargs) -> dict:
        """Return a data dictionary with all valid attributes."""
        data = {
            "id": str(uuid4()),
            "name": "edl_update_valid_test",
            "folder": "My Folder",
            "type": {
                "ip": {
                    "url": "http://example.com/updated-edl.txt",
                    "recurring": {"daily": {"at": "05"}},
                }
            },
        }
        data.update(kwargs)
        return data


class ExternalDynamicListsResponseModelFactory(factory.DictFactory):
    """Factory for creating dictionary data for ExternalDynamicListsResponseModel validation testing."""

    id = str(uuid4())
    name = "edl_test"
    folder = "My Folder"
    type = {
        "ip": {
            "url": "http://example.com/edl.txt",
            "recurring": {"daily": {"at": "03"}},
        }
    }

    @classmethod
    def build_predefined(cls, **kwargs) -> dict:
        """Return a data dictionary with predefined snippet."""
        data = {
            "name": "edl_predefined_test",
            "snippet": "predefined",
        }
        data.update(kwargs)
        return data

    @classmethod
    def build_without_id_non_predefined(cls, **kwargs) -> dict:
        """Return a data dictionary without ID for non-predefined snippet."""
        data = {
            "name": "edl_non_predefined_test",
            "snippet": "My Snippet",
            "type": {
                "ip": {
                    "url": "http://example.com/edl.txt",
                    "recurring": {"daily": {"at": "03"}},
                }
            },
        }
        data.update(kwargs)
        return data

    @classmethod
    def build_without_type_non_predefined(cls, **kwargs) -> dict:
        """Return a data dictionary without type for non-predefined snippet."""
        data = {
            "id": str(uuid4()),
            "name": "edl_non_predefined_test",
            "snippet": "My Snippet",
        }
        data.update(kwargs)
        return data

    @classmethod
    def build_from_request(cls, request_data: dict, **kwargs) -> dict:
        """Return a data dictionary based on request data.

        Args:
            request_data: Request data dictionary to base the response on
            **kwargs: Additional attributes to override

        Returns:
            Dictionary with response data

        """
        data = request_data.copy()
        data["id"] = str(uuid4())
        data.update(kwargs)
        return data

    @classmethod
    def build_valid(cls, **kwargs) -> dict:
        """Return a data dictionary with all valid attributes."""
        data = {
            "id": str(uuid4()),
            "name": "edl_resp_valid_test",
            "folder": "My Folder",
            "type": {
                "ip": {
                    "url": "http://example.com/edl.txt",
                    "recurring": {"daily": {"at": "03"}},
                }
            },
        }
        data.update(kwargs)
        return data
