# tests/factories/objects/application.py

"""Factory definitions for application objects."""

from uuid import uuid4

import factory  # type: ignore
from faker import Faker

from scm.models.objects.application import (
    ApplicationBaseModel,
    ApplicationCreateModel,
    ApplicationResponseModel,
    ApplicationUpdateModel,
)

fake = Faker()


# Base factory for all application models
class ApplicationBaseFactory(factory.Factory):
    """Base factory for Application with common fields."""

    class Meta:
        model = ApplicationBaseModel
        abstract = True

    name = factory.Sequence(lambda n: f"application_{n}")
    description = fake.sentence()
    category = "general-internet"
    subcategory = "file-sharing"
    technology = "client-server"
    risk = 1
    ports = ["tcp/80,443", "udp/3478"]

    # Boolean attributes with explicit defaults
    evasive = False
    pervasive = False
    excessive_bandwidth_use = False
    used_by_malware = False
    transfers_files = False
    has_known_vulnerabilities = False
    tunnels_other_apps = False
    prone_to_misuse = False
    no_certifications = False

    # Container fields default to None
    folder = None
    snippet = None


class ApplicationCreateApiFactory(ApplicationBaseFactory):
    """Factory for creating ApplicationCreateModel instances."""

    class Meta:
        model = ApplicationCreateModel

    # Default to folder container
    folder = "Prisma Access"

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, **kwargs)

    @classmethod
    def with_high_risk(cls, risk=5, **kwargs):
        """Create an instance with high risk level."""
        return cls(risk=risk, **kwargs)

    @classmethod
    def with_all_boolean_flags(cls, value=True, **kwargs):
        """Create an instance with all boolean flags set to specified value."""
        return cls(
            evasive=value,
            pervasive=value,
            excessive_bandwidth_use=value,
            used_by_malware=value,
            transfers_files=value,
            has_known_vulnerabilities=value,
            tunnels_other_apps=value,
            prone_to_misuse=value,
            no_certifications=value,
            **kwargs,
        )


class ApplicationUpdateApiFactory(ApplicationBaseFactory):
    """Factory for creating ApplicationUpdateModel instances."""

    class Meta:
        model = ApplicationUpdateModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    # All fields are optional for partial updates
    name = None
    description = None
    category = None
    subcategory = None
    technology = None
    risk = None
    ports = None

    # Boolean attributes set to None for partial updates
    evasive = None
    pervasive = None
    excessive_bandwidth_use = None
    used_by_malware = None
    transfers_files = None
    has_known_vulnerabilities = None
    tunnels_other_apps = None
    prone_to_misuse = None
    no_certifications = None

    @classmethod
    def with_risk_update(cls, risk=3, **kwargs):
        """Create an instance updating only the risk level."""
        return cls(risk=risk, **kwargs)

    @classmethod
    def with_boolean_updates(cls, value=True, **kwargs):
        """Create an instance updating all boolean flags."""
        return cls(
            evasive=value,
            pervasive=value,
            excessive_bandwidth_use=value,
            used_by_malware=value,
            transfers_files=value,
            has_known_vulnerabilities=value,
            tunnels_other_apps=value,
            prone_to_misuse=value,
            no_certifications=value,
            **kwargs,
        )

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, **kwargs)


class ApplicationResponseFactory(ApplicationBaseFactory):
    """Factory for creating ApplicationResponseModel instances."""

    class Meta:
        model = ApplicationResponseModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    description = factory.Faker("paragraph", nb_sentences=5)
    folder = "Prisma Access"
    tag = ["response-tag"]

    @classmethod
    def with_long_description(cls, length=4000, **kwargs):
        """Create an instance with a description near the maximum length."""
        return cls(description="A" * length, **kwargs)

    @classmethod
    def with_unknown_app(cls, **kwargs):
        """Create an instance for unknown-tcp application type."""
        return cls(
            name="unknown-tcp",
            subcategory=None,
            technology=None,
            risk=1,
            **kwargs,
        )

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, **kwargs)

    @classmethod
    def from_request(cls, request_model, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid4())
        data.update(kwargs)
        return cls(**data)


# ----------------------------------------------------------------------------
# Application model factories for Pydantic validation testing.
# ----------------------------------------------------------------------------


class ApplicationCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for ApplicationCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"application_{n}")
    description = fake.sentence()
    category = "general-internet"
    subcategory = "file-sharing"
    technology = "client-server"
    risk = 1
    ports = ["tcp/80,443", "udp/3478"]
    folder = "Prisma Access"
    snippet = None
    tag = ["test-tag", "environment-prod"]

    @classmethod
    def build_with_invalid_ports(cls, **kwargs):
        """Return a data dict with invalid port format."""
        return cls(ports=["invalid-port-format"], **kwargs)

    @classmethod
    def build_with_invalid_folder(cls, **kwargs):
        """Return a data dict with invalid folder pattern."""
        return cls(folder="Invalid@Folder#Pattern", **kwargs)

    @classmethod
    def build_with_no_containers(cls, **kwargs):
        """Return a data dict without any containers."""
        return cls(folder=None, snippet=None, **kwargs)

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Return a data dict with multiple containers."""
        return cls(folder="Prisma Access", snippet="TestSnippet", **kwargs)

    @classmethod
    def build_valid(cls, **kwargs):
        """Return a data dict with all the expected attributes."""
        return cls(**kwargs)


class ApplicationUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for ApplicationUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"updated_application_{n}")
    description = fake.sentence()
    category = "business-systems"
    subcategory = "management"
    technology = "client-server"
    risk = 2
    ports = ["tcp/8080"]
    folder = "Development"
    snippet = None
    tag = ["test-tag", "environment-prod"]

    # Boolean attributes
    evasive = True
    pervasive = False
    excessive_bandwidth_use = False
    used_by_malware = False
    transfers_files = True
    has_known_vulnerabilities = False
    tunnels_other_apps = False
    prone_to_misuse = False
    no_certifications = False

    @classmethod
    def build_with_invalid_ports(cls, **kwargs):
        """Return a data dict with invalid port format."""
        return cls(ports=["invalid-port-format"], **kwargs)

    @classmethod
    def build_with_invalid_folder(cls, **kwargs):
        """Return a data dict with invalid folder pattern."""
        return cls(folder="Invalid@Folder#Pattern", **kwargs)

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Return a data dict with multiple containers."""
        return cls(folder="Prisma Access", snippet="TestSnippet", **kwargs)

    @classmethod
    def build_with_no_containers(cls, **kwargs):
        """Return a data dict without any containers."""
        return cls(folder=None, snippet=None, **kwargs)

    @classmethod
    def build_valid(cls, **kwargs):
        """Return a data dict with all the expected attributes."""
        data = cls(**kwargs)
        return data


class ApplicationResponseModelFactory(factory.DictFactory):
    """Factory for creating data dicts for ApplicationResponseModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"application_{n}")
    description = fake.sentence()
    category = "general-internet"
    subcategory = "file-sharing"
    technology = "client-server"
    risk = 1
    ports = ["tcp/80,443", "udp/3478"]
    folder = "Prisma Access"
    snippet = None
    tag = ["test-tag", "environment-prod"]

    # Boolean attributes
    evasive = False
    pervasive = False
    excessive_bandwidth_use = False
    used_by_malware = False
    transfers_files = False
    has_known_vulnerabilities = False
    tunnels_other_apps = False
    prone_to_misuse = False
    no_certifications = False

    @classmethod
    def build_with_long_description(cls, **kwargs):
        """Return a data dict with a long description."""
        return cls(description="A" * 4000, **kwargs)

    @classmethod
    def build_with_unknown_app(cls, **kwargs):
        """Return a data dict for unknown-tcp application."""
        return cls(
            name="unknown-tcp",
            subcategory=None,
            technology=None,
            risk=1,
            **kwargs,
        )

    @classmethod
    def build_valid(cls, **kwargs):
        """Return a data dict with all the expected attributes."""
        data = cls(**kwargs)
        return data
