# tests/factories/security/url_categories.py
from uuid import uuid4

import factory  # type: ignore
from faker import Faker

from scm.models.security.url_categories import (
    URLCategoriesCreateModel,
    URLCategoriesListTypeEnum,
    URLCategoriesResponseModel,
    URLCategoriesUpdateModel,
)

fake = Faker()


# Base factory with common fields
class URLCategoriesBaseFactory(factory.Factory):
    """Base factory for URL Categories with common fields."""

    name = factory.Sequence(lambda n: f"url_categories_{n}")
    description = factory.Faker("sentence")
    # Ensure list is always provided with default values
    list = factory.List([factory.Faker("domain_name") for _ in range(3)])
    type = URLCategoriesListTypeEnum.url_list

    # Container fields default to None
    folder = None
    snippet = None
    device = None


class URLCategoriesCreateModelFactory(URLCategoriesBaseFactory):
    """Factory for creating URLCategoriesCreateModel instances."""

    class Meta:
        model = URLCategoriesCreateModel

    # Default to folder container
    folder = "Shared"

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        # Ensure list field is included with default value if not provided
        if "list" not in kwargs:
            kwargs["list"] = [fake.domain_name() for _ in range(3)]
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """Create an instance with device container."""
        # Ensure list field is included with default value if not provided
        if "list" not in kwargs:
            kwargs["list"] = [fake.domain_name() for _ in range(3)]
        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def build_with_multiple_containers(cls):
        """Create data with multiple containers for validation testing."""
        return {
            "name": fake.word(),
            "description": fake.sentence(),
            "list": [fake.domain_name() for _ in range(3)],
            "folder": "Shared",
            "snippet": "TestSnippet",
            "device": None,
        }


class URLCategoriesUpdateModelFactory(URLCategoriesBaseFactory):
    """Factory for creating URLCategoriesUpdateModel instances."""

    class Meta:
        model = URLCategoriesUpdateModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    folder = "Shared"

    @classmethod
    def with_updated_list(cls, **kwargs):
        """Create an instance with an updated list."""
        updated_list = [fake.domain_name() for _ in range(3)]
        return cls(list=updated_list, **kwargs)

    @classmethod
    def with_category_match(cls, **kwargs):
        """Create an instance with category match type."""
        return cls(
            type=URLCategoriesListTypeEnum.category_match,
            list=["hacking", "low-risk"],
            **kwargs,
        )

    @classmethod
    def with_invalid_type(cls, **kwargs):
        """Create an instance with an invalid type."""
        return cls(
            type="invalid-type",
            **kwargs,
        )


class URLCategoriesResponseModelFactory(URLCategoriesBaseFactory):
    """Factory for creating URLCategoriesResponseModel instances."""

    class Meta:
        model = URLCategoriesResponseModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    folder = "Shared"

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Create a response instance with snippet container."""
        if "list" not in kwargs:
            kwargs["list"] = [fake.domain_name() for _ in range(3)]
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """Create a response instance with device container."""
        if "list" not in kwargs:
            kwargs["list"] = [fake.domain_name() for _ in range(3)]
        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def with_custom_urls(cls, urls=None, **kwargs):
        """Create a response instance with custom URL list."""
        if urls is None:
            urls = [
                "http.kali.org/kali/dists/kali-rolling/InRelease",
                "http.kali.org/kali/dists/kali-rolling/main/binary-amd64/Packages.xz",
                "http.kali.org/kali/pool/main/g/glusterfs/",
            ]
        return cls(list=urls, **kwargs)

    @classmethod
    def from_request(cls, request_model, **kwargs):
        """Create a response model based on a request model."""
        # Start with the base fields from the request
        data = {
            "name": request_model.name,
            "description": request_model.description,
            "list": request_model.list,
            "type": request_model.type,
        }

        # Add the container from the request
        if request_model.folder:
            data["folder"] = request_model.folder
        if request_model.snippet:
            data["snippet"] = request_model.snippet
        if request_model.device:
            data["device"] = request_model.device

        # Override with any additional kwargs
        data.update(kwargs)

        return cls(**data)


# End of file
