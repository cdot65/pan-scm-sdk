# tests/factories/objects/region.py

from uuid import uuid4

import factory  # type: ignore
from faker import Faker

from scm.models.objects.regions import (
    GeoLocation,
    RegionBaseModel,
    RegionCreateModel,
    RegionResponseModel,
    RegionUpdateModel,
)

fake = Faker()


# Base factory for all region models
class RegionBaseFactory(factory.Factory):
    """Base factory for Region with common fields."""

    class Meta:
        model = RegionBaseModel
        abstract = True

    name = factory.Sequence(lambda n: f"region_{n}")
    description = fake.sentence()
    tag = ["test-tag", "region-tag"]
    geo_location = factory.LazyFunction(
        lambda: GeoLocation(
            latitude=float(fake.latitude()),
            longitude=float(fake.longitude()),
        )
    )
    address = factory.LazyFunction(
        lambda: [fake.ipv4() for _ in range(fake.random_int(min=1, max=3))]
    )

    # Container fields default to None
    folder = None
    snippet = None
    device = None


class RegionCreateApiFactory(RegionBaseFactory):
    """Factory for creating RegionCreateModel instances."""

    class Meta:
        model = RegionCreateModel

    # Default to folder container
    folder = "Global"

    @classmethod
    def build_valid(cls, **kwargs):
        """Create a valid RegionCreateModel instance."""
        return cls(
            folder="Global",
            snippet=None,
            device=None,
            **kwargs,
        )

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Create a RegionCreateModel instance with snippet container."""
        return cls(
            folder=None,
            snippet=snippet,
            device=None,
            **kwargs,
        )

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """Create a RegionCreateModel instance with device container."""
        return cls(
            folder=None,
            snippet=None,
            device=device,
            **kwargs,
        )

    @classmethod
    def build_with_invalid_name(cls, **kwargs):
        """Create a RegionCreateModel instance with an invalid name."""
        return cls(
            name="invalid@name",  # Contains invalid character
            folder="Global",
            **kwargs,
        )

    @classmethod
    def build_with_invalid_geo_location(cls, **kwargs):
        """Create a RegionCreateModel instance with invalid geo_location."""
        return cls(
            geo_location=GeoLocation(latitude=100, longitude=-122.4194),  # Invalid latitude
            folder="Global",
            **kwargs,
        )

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Create a RegionCreateModel instance with multiple containers."""
        # Note: This will fail validation but is needed for testing
        return cls(
            folder="Global",
            snippet="TestSnippet",
            device=None,
            **kwargs,
        )

    @classmethod
    def build_without_container(cls, **kwargs):
        """Create a RegionCreateModel instance without any container."""
        # Note: This will fail validation but is needed for testing
        return cls(
            folder=None,
            snippet=None,
            device=None,
            **kwargs,
        )


class RegionUpdateApiFactory(RegionBaseFactory):
    """Factory for creating RegionUpdateModel instances."""

    class Meta:
        model = RegionUpdateModel

    id = factory.LazyFunction(lambda: str(uuid4()))

    @classmethod
    def build_valid(cls, **kwargs):
        """Create a valid RegionUpdateModel instance."""
        return cls(
            folder="Global",
            snippet=None,
            device=None,
            **kwargs,
        )

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Create a RegionUpdateModel instance with snippet container."""
        return cls(
            folder=None,
            snippet=snippet,
            device=None,
            **kwargs,
        )

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """Create a RegionUpdateModel instance with device container."""
        return cls(
            folder=None,
            snippet=None,
            device=device,
            **kwargs,
        )

    @classmethod
    def build_without_id(cls, **kwargs):
        """Create a RegionUpdateModel instance without an ID."""
        return cls(id=None, **kwargs)

    @classmethod
    def build_with_invalid_id(cls, **kwargs):
        """Create a RegionUpdateModel instance with an invalid UUID format."""
        return cls(id="not-a-uuid", **kwargs)

    @classmethod
    def build_minimal_update(cls, **kwargs):
        """Create a minimal RegionUpdateModel with only required fields."""
        return cls(
            id=kwargs.get("id", str(uuid4())),
            name=kwargs.get("name", f"region_{fake.random_int(min=1000, max=9999)}"),
            geo_location=None,
            address=None,
            tag=None,
            folder="Global",
            **kwargs,
        )


class RegionResponseFactory(RegionBaseFactory):
    """Factory for creating RegionResponseModel instances."""

    class Meta:
        model = RegionResponseModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    folder = "Global"

    @classmethod
    def build_valid(cls, **kwargs):
        """Create a valid RegionResponseModel instance."""
        return cls(
            folder="Global",
            snippet=None,
            device=None,
            **kwargs,
        )

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Create a RegionResponseModel instance with snippet container."""
        return cls(
            folder=None,
            snippet=snippet,
            device=None,
            **kwargs,
        )

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """Create a RegionResponseModel instance with device container."""
        return cls(
            folder=None,
            snippet=None,
            device=device,
            **kwargs,
        )

    @classmethod
    def from_request(cls, request_model, **kwargs):
        """
        Create a response model based on a request model.

        This is useful for simulating the API's response to a create request.

        Args:
            request_model: The create request model to base the response on
            **kwargs: Additional attributes to override in the response

        Returns:
            RegionResponseModel instance
        """
        if hasattr(request_model, "model_dump"):
            data = request_model.model_dump(exclude_none=False)
        else:
            data = dict(request_model)

        # Set default ID if not provided
        if "id" not in kwargs and "id" not in data:
            data["id"] = str(uuid4())

        # Override with any provided kwargs
        data.update(kwargs)

        return cls(**data)


# ----------------------------------------------------------------------------
# Region model factories for Pydantic validation testing.
# ----------------------------------------------------------------------------


class RegionCreateModelFactory:
    """Factory for creating data dicts for RegionCreateModel validation testing."""

    model = dict
    name = "test-region"  # Use a concrete string instead of factory.Sequence
    description = fake.sentence()
    tag = ["test-tag", "region-tag"]
    geo_location = {"latitude": 37.7749, "longitude": -122.4194}
    address = ["192.168.1.0/24", "10.0.0.0/8"]
    folder = "Global"

    @classmethod
    def build_without_container(cls, **kwargs):
        """Return a data dict without any container field."""
        data = {
            "name": "test-region",  # Use a concrete string instead of cls.name
            "description": kwargs.get("description", cls.description),
            "tag": kwargs.get("tag", cls.tag),
            "geo_location": kwargs.get("geo_location", cls.geo_location),
            "address": kwargs.get("address", cls.address),
            "folder": None,
            "snippet": None,
            "device": None,
        }
        return {**data, **kwargs}

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Return a data dict with multiple container fields."""
        data = {
            "name": "test-region",  # Use a concrete string instead of cls.name
            "description": kwargs.get("description", cls.description),
            "tag": kwargs.get("tag", cls.tag),
            "geo_location": kwargs.get("geo_location", cls.geo_location),
            "address": kwargs.get("address", cls.address),
            "folder": "Global",
            "snippet": "TestSnippet",
            "device": None,
        }
        return {**data, **kwargs}

    @classmethod
    def build_with_invalid_name(cls, **kwargs):
        """Return a data dict with an invalid name."""
        data = {
            "name": "invalid@name",  # Contains invalid character
            "description": kwargs.get("description", cls.description),
            "tag": kwargs.get("tag", cls.tag),
            "geo_location": kwargs.get("geo_location", cls.geo_location),
            "address": kwargs.get("address", cls.address),
            "folder": kwargs.get("folder", cls.folder),
            "snippet": None,
            "device": None,
        }
        return {**data, **kwargs}

    @classmethod
    def build_with_invalid_geo_location(cls, **kwargs):
        """Return a data dict with invalid geo_location."""
        data = {
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "tag": kwargs.get("tag", cls.tag),
            "geo_location": {"latitude": 100, "longitude": -122.4194},  # Invalid latitude
            "address": kwargs.get("address", cls.address),
            "folder": kwargs.get("folder", cls.folder),
            "snippet": None,
            "device": None,
        }
        return {**data, **kwargs}

    @classmethod
    def build_valid(cls, **kwargs):
        """Return a data dict with all the expected attributes."""
        data = {
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "tag": kwargs.get("tag", cls.tag),
            "geo_location": kwargs.get("geo_location", cls.geo_location),
            "address": kwargs.get("address", cls.address),
            "folder": kwargs.get("folder", cls.folder),
            "snippet": None,
            "device": None,
        }
        return {**data, **kwargs}


class RegionUpdateModelFactory:
    """Factory for creating data dicts for RegionUpdateModel validation testing."""

    model = dict
    id = "123e4567-e89b-12d3-a456-426655440000"
    name = "test-region"  # Use a concrete string instead of factory.Sequence
    description = fake.sentence()
    tag = ["test-tag", "region-tag"]
    geo_location = {"latitude": 37.7749, "longitude": -122.4194}
    address = ["192.168.1.0/24", "10.0.0.0/8"]
    folder = "Global"

    @classmethod
    def build_without_id(cls, **kwargs):
        """Return a data dict without an ID field."""
        data = {
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "tag": kwargs.get("tag", cls.tag),
            "geo_location": kwargs.get("geo_location", cls.geo_location),
            "address": kwargs.get("address", cls.address),
            "folder": kwargs.get("folder", cls.folder),
            "snippet": None,
            "device": None,
        }
        return {**data, **kwargs}

    @classmethod
    def build_with_invalid_id(cls, **kwargs):
        """Return a data dict with an invalid ID format."""
        data = {
            "id": "not-a-uuid",
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "tag": kwargs.get("tag", cls.tag),
            "geo_location": kwargs.get("geo_location", cls.geo_location),
            "address": kwargs.get("address", cls.address),
            "folder": kwargs.get("folder", cls.folder),
            "snippet": None,
            "device": None,
        }
        return {**data, **kwargs}

    @classmethod
    def build_minimal_update(cls, **kwargs):
        """Return a data dict with only the required fields."""
        data = {
            "id": kwargs.get("id", cls.id),
            "name": kwargs.get("name", cls.name),
            "folder": kwargs.get("folder", cls.folder),
        }
        return {**data, **kwargs}

    @classmethod
    def build_valid(cls, **kwargs):
        """Return a data dict with all the expected attributes."""
        data = {
            "id": kwargs.get("id", cls.id),
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "tag": kwargs.get("tag", cls.tag),
            "geo_location": kwargs.get("geo_location", cls.geo_location),
            "address": kwargs.get("address", cls.address),
            "folder": kwargs.get("folder", cls.folder),
            "snippet": None,
            "device": None,
        }
        return {**data, **kwargs}


class RegionResponseModelFactory:
    """Factory for creating data dicts for RegionResponseModel validation testing."""

    model = dict
    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"region_{n}")
    description = fake.sentence()
    tag = ["test-tag", "region-tag"]
    geo_location = {"latitude": 37.7749, "longitude": -122.4194}
    address = ["192.168.1.0/24", "10.0.0.0/8"]
    folder = "Global"

    @classmethod
    def build_without_id(cls, **kwargs):
        """Return a data dict without an ID field."""
        data = {
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "tag": kwargs.get("tag", cls.tag),
            "geo_location": kwargs.get("geo_location", cls.geo_location),
            "address": kwargs.get("address", cls.address),
            "folder": kwargs.get("folder", cls.folder),
            "snippet": None,
            "device": None,
        }
        return {**data, **kwargs}

    @classmethod
    def build_from_request(cls, request_data, **kwargs):
        """
        Return a data dictionary based on request data.

        Args:
            request_data: Request data dictionary to base the response on
            **kwargs: Additional attributes to override

        Returns:
            Dictionary with response data
        """
        if hasattr(request_data, "model_dump"):
            data = request_data.model_dump(exclude_none=False)
        else:
            data = dict(request_data)

        # Set default ID if not provided
        if "id" not in kwargs and "id" not in data:
            data["id"] = cls.id

        # Override with any provided kwargs
        data.update(kwargs)

        return data

    @classmethod
    def build_valid(cls, **kwargs):
        """Return a data dict with all the expected attributes."""
        data = {
            "id": kwargs.get("id", cls.id),
            "name": kwargs.get("name", cls.name),
            "description": kwargs.get("description", cls.description),
            "tag": kwargs.get("tag", cls.tag),
            "geo_location": kwargs.get("geo_location", cls.geo_location),
            "address": kwargs.get("address", cls.address),
            "folder": kwargs.get("folder", cls.folder),
            "snippet": None,
            "device": None,
        }
        return {**data, **kwargs}
