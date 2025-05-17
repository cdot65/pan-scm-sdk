"""Factory definitions for label objects."""

from typing import Any, Dict, Union
import uuid

import factory
from faker import Faker

from scm.models.setup.label import (
    LabelBaseModel,
    LabelCreateModel,
    LabelResponseModel,
    LabelUpdateModel,
)

fake = Faker()


# --- Base ModelFactory for All Label Models ---
class LabelBaseModelFactory(factory.Factory):
    """Base factory for creating label model instances."""

    class Meta:
        """Meta class that defines the model for the factory."""

        model = LabelBaseModel
        abstract = True

    name = factory.Sequence(lambda n: f"label_{n}")
    type = factory.LazyFunction(
        lambda: fake.random_element(
            [
                "ip-netmask",
                "fqdn",
                "port",
                "percent",
                "count",
                "zone",
                "ip-range",
                "ip-wildcard",
                "device-priority",
                "device-id",
                "egress-max",
                "as-number",
                "link-tag",
                "group-id",
                "rate",
                "router-id",
                "qos-profile",
                "timer",
            ]
        )
    )
    value = factory.LazyFunction(lambda: fake.word())
    description = factory.LazyFunction(lambda: fake.sentence())
    folder = factory.LazyFunction(lambda: fake.word())
    snippet = None
    device = None


# --- LabelCreateModel ModelFactory ---
class LabelCreateModelFactory(LabelBaseModelFactory):
    """Factory for creating LabelCreateModel instances."""

    class Meta:
        """Meta class that defines the model for the factory."""

        model = LabelCreateModel

    @classmethod
    def build_valid_model(cls, **kwargs) -> LabelCreateModel:
        """Return a valid LabelCreateModel instance."""
        return cls.build(**kwargs)

    @classmethod
    def build_minimal_model(cls, **kwargs) -> LabelCreateModel:
        """Return a minimal valid LabelCreateModel instance (only required fields)."""
        fields = dict(
            name=fake.unique.word(),
            type="ip-netmask",
            value="192.168.1.0/24",
            folder=fake.word(),
        )
        fields.update(kwargs)
        return cls.build(**fields)


# --- LabelUpdateModel ModelFactory ---
class LabelUpdateModelFactory(LabelBaseModelFactory):
    """Factory for creating LabelUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for the factory."""

        model = LabelUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))

    @classmethod
    def build_valid_model(cls, **kwargs) -> LabelUpdateModel:
        """Return a valid LabelUpdateModel instance."""
        return cls.build(**kwargs)

    @classmethod
    def build_minimal_model(cls, **kwargs) -> LabelUpdateModel:
        """Return a minimal valid LabelUpdateModel instance (only required fields)."""
        fields = dict(
            id=str(uuid.uuid4()),
            name=fake.unique.word(),
            type="fqdn",
            value="example.com",
            folder=fake.word(),
        )
        fields.update(kwargs)
        return cls.build(**fields)


# --- LabelResponseModel ModelFactory ---
class LabelResponseModelFactory(LabelBaseModelFactory):
    """Factory for creating LabelResponseModel instances."""

    class Meta:
        """Meta class that defines the model for the factory."""

        model = LabelResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    overridden = factory.LazyFunction(lambda: fake.pybool())

    @classmethod
    def build_valid_model(cls, **kwargs) -> LabelResponseModel:
        """Return a valid LabelResponseModel instance."""
        model = cls.build(**kwargs)
        # Add extra attributes that might be in API responses but aren't defined in the model
        if "labels" in kwargs:
            model.__dict__["labels"] = kwargs["labels"]
        if "parent" in kwargs:
            model.__dict__["parent"] = kwargs["parent"]
        if "snippets" in kwargs:
            model.__dict__["snippets"] = kwargs["snippets"]
        if "model" in kwargs:
            model.__dict__["model"] = kwargs["model"]
        if "serial_number" in kwargs:
            model.__dict__["serial_number"] = kwargs["serial_number"]
        if "device_only" in kwargs:
            model.__dict__["device_only"] = kwargs["device_only"]
        return model

    @classmethod
    def from_request_model(
        cls,
        request_model: Union[LabelCreateModel, LabelUpdateModel, Dict[str, Any]],
        **kwargs,
    ) -> LabelResponseModel:
        """Create a response model based on a request model."""
        if isinstance(request_model, dict):
            data = request_model.copy()
        else:
            data = (
                request_model.model_dump()
                if hasattr(request_model, "model_dump")
                else dict(request_model)
            )
        if "id" not in data:
            data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls.build(**data)


# --- LabelCreateModel DictFactory ---
class LabelCreateModelDictFactory(factory.Factory):
    """Factory for creating data dicts for LabelCreateModel validation testing."""

    class Meta:
        """Meta class that defines the model for LabelCreateModelDictFactory."""

        model = dict

    name = factory.Sequence(lambda n: f"label_{n}")
    type = factory.LazyFunction(
        lambda: fake.random_element(
            [
                "ip-netmask",
                "fqdn",
                "port",
                "percent",
                "count",
                "zone",
                "ip-range",
                "ip-wildcard",
                "device-priority",
                "device-id",
                "egress-max",
                "as-number",
                "link-tag",
                "group-id",
                "rate",
                "router-id",
                "qos-profile",
                "timer",
            ]
        )
    )
    value = factory.LazyFunction(lambda: fake.word())
    description = factory.LazyFunction(lambda: fake.sentence())
    folder = factory.LazyFunction(lambda: fake.word())

    @classmethod
    def build_valid_dict(cls, **kwargs) -> Dict[str, Any]:
        """Return a data dict with all the expected attributes."""
        return cls.build(**kwargs)

    @classmethod
    def build_minimal_dict(cls, **kwargs) -> Dict[str, Any]:
        """Return a minimal valid data dict (only required fields)."""
        fields = dict(
            name=fake.unique.word(),
            type="ip-netmask",
            value="192.168.1.0/24",
            folder=fake.word(),
        )
        fields.update(kwargs)
        return cls.build(**fields)


# --- LabelUpdateModel DictFactory ---
class LabelUpdateModelDictFactory(factory.Factory):
    """Factory for creating data dicts for LabelUpdateModel validation testing."""

    class Meta:
        """Meta class that defines the model for LabelUpdateModelDictFactory."""

        model = dict

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"updated_label_{n}")
    type = factory.LazyFunction(
        lambda: fake.random_element(
            [
                "ip-netmask",
                "fqdn",
                "port",
                "percent",
                "count",
                "zone",
                "ip-range",
                "ip-wildcard",
                "device-priority",
                "device-id",
                "egress-max",
                "as-number",
                "link-tag",
                "group-id",
                "rate",
                "router-id",
                "qos-profile",
                "timer",
            ]
        )
    )
    value = factory.LazyFunction(lambda: fake.word())
    description = factory.LazyFunction(lambda: fake.sentence())
    folder = factory.LazyFunction(lambda: fake.word())

    @classmethod
    def build_valid_dict(cls, **kwargs) -> Dict[str, Any]:
        """Return a data dict with all the expected attributes."""
        return cls.build(**kwargs)

    @classmethod
    def build_minimal_dict(cls, **kwargs) -> Dict[str, Any]:
        """Return a minimal valid data dict (only required fields)."""
        fields = dict(
            id=str(uuid.uuid4()),
            name=fake.unique.word(),
            type="fqdn",
            value="example.com",
            folder=fake.word(),
        )
        fields.update(kwargs)
        return cls.build(**fields)
