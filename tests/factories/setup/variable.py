from typing import Any, Dict, Union
import uuid

import factory
from faker import Faker

from scm.models.setup.variable import (
    VariableBaseModel,
    VariableCreateModel,
    VariableResponseModel,
    VariableUpdateModel,
)

fake = Faker()


# --- Base ModelFactory for All Variable Models ---
class VariableBaseModelFactory(factory.Factory):
    class Meta:
        model = VariableBaseModel
        abstract = True

    name = factory.Sequence(lambda n: f"variable_{n}")
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


# --- VariableCreateModel ModelFactory ---
class VariableCreateModelFactory(VariableBaseModelFactory):
    """Factory for creating VariableCreateModel instances."""

    class Meta:
        model = VariableCreateModel

    @classmethod
    def build_valid_model(cls, **kwargs) -> VariableCreateModel:
        """Return a valid VariableCreateModel instance."""
        return cls.build(**kwargs)

    @classmethod
    def build_minimal_model(cls, **kwargs) -> VariableCreateModel:
        """Return a minimal valid VariableCreateModel instance (only required fields)."""
        fields = dict(
            name=fake.unique.word(),
            type="ip-netmask",
            value="192.168.1.0/24",
            folder=fake.word(),
        )
        fields.update(kwargs)
        return cls.build(**fields)


# --- VariableUpdateModel ModelFactory ---
class VariableUpdateModelFactory(VariableBaseModelFactory):
    """Factory for creating VariableUpdateModel instances."""

    class Meta:
        model = VariableUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))

    @classmethod
    def build_valid_model(cls, **kwargs) -> VariableUpdateModel:
        """Return a valid VariableUpdateModel instance."""
        return cls.build(**kwargs)

    @classmethod
    def build_minimal_model(cls, **kwargs) -> VariableUpdateModel:
        """Return a minimal valid VariableUpdateModel instance (only required fields)."""
        fields = dict(
            id=str(uuid.uuid4()),
            name=fake.unique.word(),
            type="fqdn",
            value="example.com",
            folder=fake.word(),
        )
        fields.update(kwargs)
        return cls.build(**fields)


# --- VariableResponseModel ModelFactory ---
class VariableResponseModelFactory(VariableBaseModelFactory):
    """Factory for creating VariableResponseModel instances."""

    class Meta:
        model = VariableResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    overridden = factory.LazyFunction(lambda: fake.pybool())

    @classmethod
    def build_valid_model(cls, **kwargs) -> VariableResponseModel:
        """Return a valid VariableResponseModel instance."""
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
        request_model: Union[VariableCreateModel, VariableUpdateModel, Dict[str, Any]],
        **kwargs,
    ) -> VariableResponseModel:
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


# --- VariableCreateModel DictFactory ---
class VariableCreateModelDictFactory(factory.Factory):
    """Factory for creating data dicts for VariableCreateModel validation testing."""

    class Meta:
        model = dict

    name = factory.Sequence(lambda n: f"variable_{n}")
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


# --- VariableUpdateModel DictFactory ---
class VariableUpdateModelDictFactory(factory.Factory):
    """Factory for creating data dicts for VariableUpdateModel validation testing."""

    class Meta:
        model = dict

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"updated_variable_{n}")
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
