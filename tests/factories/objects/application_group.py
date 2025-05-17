# tests/factories/objects/application_group.py

"""Factory definitions for application group objects."""

from uuid import uuid4

import factory  # type: ignore
from faker import Faker

from scm.models.objects.application_group import (
    ApplicationGroupBaseModel,
    ApplicationGroupCreateModel,
    ApplicationGroupResponseModel,
    ApplicationGroupUpdateModel,
)

fake = Faker()


class ApplicationGroupBaseFactory(factory.Factory):
    """Base factory for ApplicationGroup with common fields."""

    class Meta:
        """Meta class that defines the model for ApplicationGroupBaseFactory."""

        """Meta class that defines the model for ApplicationGroupBaseFactory."""
        model = ApplicationGroupBaseModel
        abstract = True

    name = factory.Sequence(lambda n: f"application_group_{n}")
    members = [
        "office365-consumer-access",
        "office365-enterprise-access",
    ]
    folder = "Texas"
    snippet = None
    device = None


class ApplicationGroupCreateApiFactory(ApplicationGroupBaseFactory):
    """Factory for creating ApplicationGroupCreateModel instances."""

    class Meta:
        """Meta class that defines the model for ApplicationGroupBaseFactory."""

        """Meta class that defines the model for ApplicationGroupCreateModelFactory."""
        model = ApplicationGroupCreateModel

    @classmethod
    def with_folder(cls, folder="Texas", **kwargs):
        """Create an instance with folder container."""
        return cls(folder=folder, snippet=None, device=None, **kwargs)

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def with_members(cls, members: list[str], **kwargs):
        """Create an instance with specific members."""
        return cls(members=members, **kwargs)

    @classmethod
    def with_single_member(cls, member="single-app", **kwargs):
        """Create an instance with a single member."""
        return cls(members=[member], **kwargs)


class ApplicationGroupUpdateApiFactory(ApplicationGroupBaseFactory):
    """Factory for creating ApplicationGroupUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for ApplicationGroupBaseFactory."""

        """Meta class that defines the model for ApplicationGroupUpdateModelFactory."""
        model = ApplicationGroupUpdateModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    name = factory.Sequence(lambda n: f"application_group_updated_{n}")

    @classmethod
    def with_folder(cls, folder="Texas", **kwargs):
        """Create an instance with folder container."""
        return cls(folder=folder, snippet=None, device=None, **kwargs)

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def with_members(cls, members: list[str], **kwargs):
        """Create an instance with specific members."""
        return cls(members=members, **kwargs)

    @classmethod
    def minimal_update(cls, id=None, **kwargs):
        """Create an instance with minimal required fields for update."""
        if id is None:
            id = str(uuid4())
        return cls(
            id=id,
            name="MinimalUpdate",
            members=["min-app"],
            **kwargs,
        )


class ApplicationGroupResponseFactory(ApplicationGroupBaseFactory):
    """Factory for creating ApplicationGroupResponseModel instances."""

    class Meta:
        """Meta class that defines the model for ApplicationGroupBaseFactory."""

        """Meta class that defines the model for ApplicationGroupResponseModelFactory."""
        model = ApplicationGroupResponseModel

    id = factory.LazyFunction(lambda: str(uuid4()))

    @classmethod
    def with_folder(cls, folder="Texas", **kwargs):
        """Create an instance with folder container."""
        return cls(folder=folder, snippet=None, device=None, **kwargs)

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device="TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def with_members(cls, members: list[str], **kwargs):
        """Create an instance with specific members."""
        return cls(members=members, **kwargs)

    @classmethod
    def from_request(cls, request_model: ApplicationGroupCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid4())
        data.update(kwargs)
        return cls(**data)


# -------------------- Model Validation Factories --------------------


class ApplicationGroupCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for ApplicationGroupCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"application_group_{n}")
    members = [
        "office365-consumer-access",
        "office365-enterprise-access",
    ]
    folder = "Texas"
    snippet = None
    device = None

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestApplicationGroup",
            members=["app1", "app2"],
            folder="Texas",
        )

    @classmethod
    def build_with_invalid_name(cls):
        """Return a data dict with invalid name pattern."""
        return cls(
            name="@invalid-name#",
            members=["app1"],
            folder="Texas",
        )

    @classmethod
    def build_with_empty_members(cls):
        """Return a data dict with empty members list."""
        return cls(
            name="TestGroup",
            members=[],
            folder="Texas",
        )

    @classmethod
    def build_with_invalid_folder(cls):
        """Return a data dict with invalid folder pattern."""
        return cls(
            name="TestGroup",
            members=["app1"],
            folder="Invalid@Folder#",
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="TestGroup",
            members=["app1"],
            folder="Texas",
            snippet="TestSnippet",
        )

    @classmethod
    def build_with_no_container(cls):
        """Return a data dict without any container."""
        return cls(
            name="TestGroup",
            members=["app1"],
            folder=None,
            snippet=None,
            device=None,
        )


class ApplicationGroupUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for ApplicationGroupUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"application_group_updated_{n}")
    members = [
        "office365-consumer-access",
        "office365-enterprise-access",
    ]
    folder = None
    snippet = None
    device = None

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating an application group."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedGroup",
            members=["updated-app1", "updated-app2"],
            folder="UpdatedFolder",
        )

    @classmethod
    def build_with_invalid_fields(cls):
        """Return a data dict with multiple invalid fields."""
        return cls(
            id="not-a-valid-uuid",
            name="@invalid-name#",
            members=[],
        )

    @classmethod
    def build_minimal_update(cls):
        """Return a data dict with minimal fields required for update."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="MinimalUpdate",
        )
