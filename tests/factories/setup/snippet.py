"""Factory definitions for snippet objects."""

from typing import Any, Dict, Union
import uuid

import factory
from faker import Faker

from scm.models.setup.snippet import (
    FolderReference,
    SnippetBaseModel,
    SnippetCreateModel,
    SnippetResponseModel,
    SnippetUpdateModel,
)

fake = Faker()


# --- Folder Reference ModelFactory ---
class FolderReferenceModelFactory(factory.Factory):
    class Meta:
        model = FolderReference

    id = factory.LazyFunction(lambda: uuid.uuid4())
    name = factory.Sequence(lambda n: f"folder_{n}")


# --- Base ModelFactory for All Snippet Models ---
class SnippetBaseModelFactory(factory.Factory):
    class Meta:
        model = SnippetBaseModel
        abstract = True

    name = factory.Sequence(lambda n: f"snippet_{n}")
    description = factory.LazyFunction(lambda: fake.sentence())
    labels = factory.LazyFunction(lambda: [fake.word() for _ in range(2)])
    enable_prefix = factory.LazyFunction(lambda: fake.pybool())


# --- SnippetCreateModel ModelFactory ---
class SnippetCreateModelFactory(SnippetBaseModelFactory):
    """Factory for creating SnippetCreateModel instances."""

    class Meta:
        model = SnippetCreateModel

    @classmethod
    def build_valid_model(cls, **kwargs) -> SnippetCreateModel:
        """Return a valid SnippetCreateModel instance."""
        return cls.build(**kwargs)

    @classmethod
    def build_minimal_model(cls, **kwargs) -> SnippetCreateModel:
        """Return a minimal valid SnippetCreateModel instance (only required fields)."""
        fields = dict(name=fake.unique.word())
        fields.update(kwargs)
        return cls.build(**fields)

    @classmethod
    def build_without_name_model(cls, **kwargs) -> SnippetCreateModel:
        """Return a SnippetCreateModel instance missing the 'name' field."""
        fields = dict(description=fake.sentence(), labels=[fake.word()])
        fields.update(kwargs)
        fields.pop("name", None)
        return cls.build(**fields)


# --- SnippetUpdateModel ModelFactory ---
class SnippetUpdateModelFactory(SnippetBaseModelFactory):
    """Factory for creating SnippetUpdateModel instances."""

    class Meta:
        model = SnippetUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))

    @classmethod
    def build_valid_model(cls, **kwargs) -> SnippetUpdateModel:
        """Return a valid SnippetUpdateModel instance."""
        return cls.build(**kwargs)

    @classmethod
    def build_minimal_model(cls, **kwargs) -> SnippetUpdateModel:
        """Return a minimal valid SnippetUpdateModel instance (only required fields)."""
        fields = dict(id=str(uuid.uuid4()), name=fake.unique.word())
        fields.update(kwargs)
        return cls.build(**fields)

    @classmethod
    def build_without_id_model(cls, **kwargs) -> SnippetUpdateModel:
        fields = dict(name=fake.unique.word())
        fields.update(kwargs)
        fields.pop("id", None)
        return cls.build(**fields)


# --- SnippetResponseModel ModelFactory ---
class SnippetResponseModelFactory(SnippetBaseModelFactory):
    """Factory for creating SnippetResponseModel instances."""

    class Meta:
        model = SnippetResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    type = factory.LazyFunction(lambda: fake.random_element(["predefined", "custom", "readonly"]))
    display_name = factory.LazyFunction(lambda: fake.word())
    last_update = factory.LazyFunction(lambda: fake.iso8601())
    created_in = factory.LazyFunction(lambda: fake.iso8601())
    folders = factory.LazyFunction(lambda: [])
    shared_in = factory.LazyFunction(lambda: fake.word())

    @classmethod
    def build_valid_model(cls, **kwargs) -> SnippetResponseModel:
        """Return a valid SnippetResponseModel instance."""
        return cls.build(**kwargs)

    @classmethod
    def from_request_model(
        cls,
        request_model: Union[SnippetCreateModel, SnippetUpdateModel, Dict[str, Any]],
        **kwargs,
    ) -> SnippetResponseModel:
        """Create a response model based on a request model."""
        if isinstance(request_model, dict):
            data = request_model.copy()
        else:
            data = (
                request_model.model_dump()
                if hasattr(request_model, "model_dump")
                else dict(request_model)
            )
        data.update(kwargs)
        return cls.build(**data)


# --- SnippetCreateModel DictFactory ---
class SnippetCreateModelDictFactory(factory.Factory):
    """Factory for creating data dicts for SnippetCreateModel validation testing."""

    class Meta:
        model = dict

    name = factory.Sequence(lambda n: f"snippet_{n}")
    description = factory.LazyFunction(lambda: fake.sentence())
    labels = factory.LazyFunction(lambda: [fake.word() for _ in range(2)])
    enable_prefix = factory.LazyFunction(lambda: fake.pybool())

    @classmethod
    def build_valid_dict(cls, **kwargs) -> Dict[str, Any]:
        """Return a data dict with all the expected attributes."""
        return cls.build(**kwargs)

    @classmethod
    def build_minimal_dict(cls, **kwargs) -> Dict[str, Any]:
        """Return a minimal valid data dict (only required fields)."""
        fields = dict(name=fake.unique.word())
        fields.update(kwargs)
        return cls.build(**fields)

    @classmethod
    def build_without_name_dict(cls, **kwargs) -> Dict[str, Any]:
        """Return a data dict missing the 'name' field."""
        fields = dict(description=fake.sentence(), labels=[fake.word()])
        fields.update(kwargs)
        fields.pop("name", None)
        return cls.build(**fields)


# --- SnippetUpdateModel DictFactory ---
class SnippetUpdateModelDictFactory(factory.Factory):
    """Factory for creating data dicts for SnippetUpdateModel validation testing."""

    class Meta:
        model = dict

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"updated_snippet_{n}")
    description = factory.LazyFunction(lambda: fake.sentence())
    labels = factory.LazyFunction(lambda: [fake.word() for _ in range(2)])
    enable_prefix = factory.LazyFunction(lambda: fake.pybool())

    @classmethod
    def build_valid_dict(cls, **kwargs) -> Dict[str, Any]:
        """Return a data dict with all the expected attributes."""
        return cls.build(**kwargs)

    @classmethod
    def build_minimal_dict(cls, **kwargs) -> Dict[str, Any]:
        """Return a minimal valid data dict (only required fields)."""
        fields = dict(id=str(uuid.uuid4()), name=fake.unique.word())
        fields.update(kwargs)
        return cls.build(**fields)

    @classmethod
    def build_without_id_dict(cls, **kwargs) -> Dict[str, Any]:
        """Return a data dict missing the 'id' field."""
        fields = dict(name=fake.unique.word())
        fields.update(kwargs)
        fields.pop("id", None)
        return cls.build(**fields)
