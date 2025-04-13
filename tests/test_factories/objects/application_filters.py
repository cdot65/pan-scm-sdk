# tests/test_factories/objects/application_filters.py

from uuid import uuid4

import factory  # type: ignore
from faker import Faker

from scm.models.objects.application_filters import (
    ApplicationFiltersBaseModel,
    ApplicationFiltersCreateModel,
    ApplicationFiltersResponseModel,
    ApplicationFiltersUpdateModel,
)

fake = Faker()


# Base factory for all application filters models
class ApplicationFiltersBaseFactory(factory.Factory):
    """Base factory for ApplicationFilters with common fields."""

    class Meta:
        model = ApplicationFiltersBaseModel
        abstract = True

    name = factory.Sequence(lambda n: f"application_filters_{n}")

    # Optional category fields
    category = None
    sub_category = None
    technology = None
    risk = None
    saas_certifications = None
    saas_risk = None

    # Boolean attributes with explicit defaults
    evasive = False
    used_by_malware = False
    transfers_files = False
    has_known_vulnerabilities = False
    tunnels_other_apps = False
    prone_to_misuse = False
    pervasive = False
    is_saas = False
    new_appid = False

    # Field that was missing in original (found in OpenAPI spec)
    excessive_bandwidth_use = False
    exclude = None

    # Container fields default to None
    folder = None
    snippet = None
    tag = ["test-tag", "environment-prod"]


class ApplicationFiltersCreateApiFactory(ApplicationFiltersBaseFactory):
    """Factory for creating ApplicationFiltersCreateModel instances."""

    class Meta:
        model = ApplicationFiltersCreateModel

    @classmethod
    def with_folder(cls, folder="Texas", **kwargs):
        """Create an instance with folder container."""
        return cls(folder=folder, snippet=None, **kwargs)

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, **kwargs)

    @classmethod
    def with_categories(cls, categories=None, **kwargs):
        """Create an instance with specific categories."""
        if categories is None:
            categories = ["business-systems", "collaboration"]
        return cls(category=categories, **kwargs)

    @classmethod
    def with_subcategories(cls, subcategories=None, **kwargs):
        """Create an instance with specific subcategories."""
        if subcategories is None:
            subcategories = ["email", "file-sharing"]
        return cls(sub_category=subcategories, **kwargs)

    @classmethod
    def with_technologies(cls, technologies=None, **kwargs):
        """Create an instance with specific technologies."""
        if technologies is None:
            technologies = ["client-server", "peer-to-peer"]
        return cls(technology=technologies, **kwargs)

    @classmethod
    def with_risks(cls, risks=None, **kwargs):
        """Create an instance with specific risk levels."""
        if risks is None:
            risks = [1, 3, 5]
        return cls(risk=risks, **kwargs)

    @classmethod
    def with_all_boolean_flags(cls, value=True, **kwargs):
        """Create an instance with all boolean flags set to specified value."""
        return cls(
            evasive=value,
            used_by_malware=value,
            transfers_files=value,
            has_known_vulnerabilities=value,
            tunnels_other_apps=value,
            prone_to_misuse=value,
            pervasive=value,
            is_saas=value,
            new_appid=value,
            # Remove excessive_bandwidth_use as it doesn't exist in the model
            folder="Texas",  # Default container to make the model valid
            **kwargs,
        )


class ApplicationFiltersUpdateApiFactory(ApplicationFiltersBaseFactory):
    """Factory for creating ApplicationFiltersUpdateModel instances."""

    class Meta:
        model = ApplicationFiltersUpdateModel

    id = factory.LazyFunction(lambda: str(uuid4()))

    @classmethod
    def with_snippet(cls, snippet="TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, **kwargs)

    @classmethod
    def with_folder(cls, folder="Texas", **kwargs):
        """Create an instance with folder container."""
        return cls(folder=folder, snippet=None, **kwargs)

    @classmethod
    def with_categories(cls, categories=None, **kwargs):
        """Create an instance with specific categories."""
        if categories is None:
            categories = ["business-systems", "collaboration"]
        return cls(category=categories, **kwargs)

    @classmethod
    def with_boolean_updates(cls, value=True, **kwargs):
        """Create an instance updating all boolean flags."""
        return cls(
            evasive=value,
            used_by_malware=value,
            transfers_files=value,
            has_known_vulnerabilities=value,
            tunnels_other_apps=value,
            prone_to_misuse=value,
            pervasive=value,
            is_saas=value,
            new_appid=value,
            excessive_bandwidth_use=value,
            **kwargs,
        )


class ApplicationFiltersResponseFactory(ApplicationFiltersBaseFactory):
    """Factory for creating ApplicationFiltersResponseModel instances."""

    class Meta:
        model = ApplicationFiltersResponseModel

    id = factory.LazyFunction(lambda: str(uuid4()))
    folder = "Texas"
    tag = ["response-tag"]

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
# Application Filters model factories for Pydantic validation testing.
# ----------------------------------------------------------------------------


class ApplicationFiltersCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for ApplicationFiltersCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"application_filters_{n}")
    category = ["business-systems", "collaboration"]
    sub_category = ["email", "file-sharing"]
    technology = ["client-server", "browser-based"]
    risk = [1, 3, 5]
    saas_certifications = ["soc1", "soc2"]
    saas_risk = ["high", "medium"]
    folder = "Texas"
    snippet = None
    tag = ["test-tag", "environment-prod"]
    exclude = ["app1", "app2"]

    # Boolean attributes
    evasive = False
    used_by_malware = False
    transfers_files = False
    has_known_vulnerabilities = False
    tunnels_other_apps = False
    prone_to_misuse = False
    pervasive = False
    is_saas = False
    new_appid = False
    excessive_bandwidth_use = False

    @classmethod
    def build_with_invalid_name(cls, **kwargs):
        """Return a data dict with invalid name pattern."""
        return cls(name="@invalid-name#", **kwargs)

    @classmethod
    def build_with_no_containers(cls, **kwargs):
        """Return a data dict without any containers."""
        return cls(folder=None, snippet=None, **kwargs)

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Return a data dict with multiple containers."""
        return cls(folder="Texas", snippet="TestSnippet", **kwargs)

    @classmethod
    def build_valid(cls, **kwargs):
        """Return a data dict with all the expected attributes."""
        return cls(**kwargs)


class ApplicationFiltersUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for ApplicationFiltersUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"application_filters_updated_{n}")
    category = ["business-systems", "collaboration"]
    sub_category = ["email", "file-sharing"]
    technology = ["client-server", "browser-based"]
    risk = [1, 3, 5]
    saas_certifications = ["soc1", "soc2"]
    saas_risk = ["high", "medium"]
    folder = "Development"
    snippet = None
    tag = ["test-tag", "environment-prod"]
    exclude = ["app3", "app4"]

    # Boolean attributes
    evasive = True
    used_by_malware = False
    transfers_files = True
    has_known_vulnerabilities = False
    tunnels_other_apps = False
    prone_to_misuse = False
    pervasive = False
    is_saas = True
    new_appid = False
    excessive_bandwidth_use = True

    @classmethod
    def build_with_invalid_fields(cls, **kwargs):
        """Return a data dict with multiple invalid fields."""
        return cls(
            id="invalid-uuid",
            name="@invalid-name",
            folder="Invalid@Folder",
            **kwargs,
        )

    @classmethod
    def build_with_no_containers(cls, **kwargs):
        """Return a data dict without any containers."""
        return cls(folder=None, snippet=None, **kwargs)

    @classmethod
    def build_with_multiple_containers(cls, **kwargs):
        """Return a data dict with multiple containers."""
        return cls(folder="Texas", snippet="TestSnippet", **kwargs)

    @classmethod
    def build_minimal_update(cls, **kwargs):
        """Return a data dict with minimal valid update fields."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="MinimalUpdate",
            **kwargs,
        )

    @classmethod
    def build_valid(cls, **kwargs):
        """Return a data dict with all the expected attributes."""
        data = cls(**kwargs)
        return data


class ApplicationFiltersResponseModelFactory(factory.DictFactory):
    """Factory for creating data dicts for ApplicationFiltersResponseModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"application_filters_{n}")
    category = ["business-systems", "collaboration"]
    sub_category = ["email", "file-sharing"]
    technology = ["client-server", "browser-based"]
    risk = [1, 3, 5]
    saas_certifications = ["soc1", "soc2"]
    saas_risk = ["high", "medium"]
    folder = "Texas"
    snippet = None
    tag = ["test-tag", "environment-prod"]
    exclude = ["app1", "app2"]

    # Boolean attributes
    evasive = False
    used_by_malware = False
    transfers_files = False
    has_known_vulnerabilities = False
    tunnels_other_apps = False
    prone_to_misuse = False
    pervasive = False
    is_saas = False
    new_appid = False
    excessive_bandwidth_use = False

    @classmethod
    def build_valid(cls, **kwargs):
        """Return a data dict with all the expected attributes."""
        data = cls(**kwargs)
        return data
