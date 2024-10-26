# tests/factories.py
import uuid

import factory

from scm.models.objects import (
    ApplicationRequestModel,
    ServiceRequestModel,
    ApplicationGroupRequestModel,
)
from scm.models.objects.address import AddressRequestModel
from scm.models.objects.address_group import AddressGroupRequestModel, DynamicFilter
from scm.models.security.security_rules import (
    SecurityRuleRequestModel,
    ProfileSetting,
    Rulebase,
    SecurityRuleMoveModel,
    RuleMoveDestination,
    SecurityRuleResponseModel,
)


class AddressFactory(factory.Factory):
    class Meta:
        model = AddressRequestModel

    name = factory.Faker("word")
    id = factory.Faker("uuid4")
    description = "PyTest AddressRequestModel"
    ip_netmask = "192.168.1.1/32"
    folder = "Prisma Access"


class DynamicFilterFactory(factory.Factory):
    class Meta:
        model = DynamicFilter

    filter = "'test', 'abc123', 'prod', 'web'"


class AddressGroupDynamicFactory(factory.Factory):
    class Meta:
        model = AddressGroupRequestModel

    name = "ValidDynamicAddressGroup"
    description = "This is just a pytest that will fail"
    dynamic = factory.SubFactory(DynamicFilterFactory)
    folder = "MainFolder"
    tag = ["tag1", "tag2"]


class AddressGroupStaticFactory(factory.Factory):
    class Meta:
        model = AddressGroupRequestModel

    name = "ValidStaticAddressGroup"
    description = "Static AddressRequestModel Group Test"
    static = [
        "address-object1",
        "address-object2",
        "address-object3",
        "address-object4",
    ]
    folder = "MainFolder"
    tag = ["tag1", "tag2"]


class ApplicationFactory(factory.Factory):
    class Meta:
        model = ApplicationRequestModel

    name = "ValidApplication"
    description = "Application from pan-scm-sdk Test"
    category = "collaboration"
    subcategory = "file-sharing"
    technology = "client-server"
    risk = 1
    ports = ["tcp/80,443", "udp/3478"]
    folder = "Prisma Access"
    evasive = False
    pervasive = False
    excessive_bandwidth_use = False
    used_by_malware = False
    transfers_files = False
    has_known_vulnerabilities = True
    tunnels_other_apps = False
    prone_to_misuse = False
    no_certifications = False


class ApplicationGroupFactory(factory.Factory):
    class Meta:
        model = ApplicationGroupRequestModel

    name = "ValidStaticApplicationGroup"
    members = [
        "office365-consumer-access",
        "office365-enterprise-access",
    ]
    folder = "Prisma Access"


class ServiceFactory(factory.Factory):
    class Meta:
        model = ServiceRequestModel

    name = factory.Faker("word")
    description = "PyTest ServiceRequestModel test"
    tag = ["Automation"]
    folder = "Prisma Access"
    protocol = {"tcp": {"port": "80,443"}}


class BaseSecurityRuleFactory(factory.Factory):
    """Base factory for common security rule fields."""

    name = factory.Sequence(lambda n: f"security_rule_{n}")
    description = factory.Faker("sentence")
    action = "allow"

    # Lists with default values
    source = ["any"]
    destination = ["any"]
    application = ["any"]
    service = ["any"]
    source_user = ["any"]
    source_hip = ["any"]
    destination_hip = ["any"]
    category = ["any"]
    tag = factory.List([factory.Faker("word") for _ in range(2)])

    # Boolean fields
    disabled = False
    log_start = False
    log_end = True

    # Other fields
    log_setting = "Cortex Data Lake"
    profile_setting = factory.SubFactory("tests.factories.ProfileSettingFactory")


class SecurityRuleRequestFactory(BaseSecurityRuleFactory):
    """Factory for creating SecurityRuleRequestModel instances."""

    class Meta:
        model = SecurityRuleRequestModel

    folder = "Shared"  # Default container type

    @classmethod
    def with_snippet(cls, **kwargs) -> SecurityRuleRequestModel:
        """Create a security rule with snippet container."""
        return cls(folder=None, snippet="TestSnippet", **kwargs)

    @classmethod
    def with_device(cls, **kwargs) -> SecurityRuleRequestModel:
        """Create a security rule with device container."""
        return cls(folder=None, device="TestDevice", **kwargs)

    @classmethod
    def create_batch_with_names(
        cls, names: list[str], **kwargs
    ) -> list[SecurityRuleRequestModel]:
        """Create multiple security rules with specified names."""
        return [cls(name=name, **kwargs) for name in names]


class SecurityRuleResponseFactory(BaseSecurityRuleFactory):
    """Factory for creating SecurityRuleResponseModel instances."""

    class Meta:
        model = SecurityRuleResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    folder = factory.SelfAttribute("..folder")  # Inherits from request if provided

    @classmethod
    def from_request(
        cls,
        request_model: SecurityRuleRequestModel,
        **kwargs,
    ) -> SecurityRuleResponseModel:
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data.update(kwargs)
        return cls(**data)


class SecurityRuleMoveFactory(factory.Factory):
    """Factory for creating SecurityRuleMoveModel instances."""

    class Meta:
        model = SecurityRuleMoveModel

    source_rule = factory.LazyFunction(lambda: str(uuid.uuid4()))
    destination = RuleMoveDestination.TOP
    rulebase = Rulebase.PRE
    destination_rule = None

    @classmethod
    def before_rule(cls, **kwargs) -> SecurityRuleMoveModel:
        """Create a move configuration for placing before another rule."""
        return cls(
            destination=RuleMoveDestination.BEFORE,
            destination_rule=str(uuid.uuid4()),
            **kwargs,
        )

    @classmethod
    def after_rule(cls, **kwargs) -> SecurityRuleMoveModel:
        """Create a move configuration for placing after another rule."""
        return cls(
            destination=RuleMoveDestination.AFTER,
            destination_rule=str(uuid.uuid4()),
            **kwargs,
        )

    @classmethod
    def to_post_rulebase(cls, **kwargs) -> SecurityRuleMoveModel:
        """Create a move configuration for the post rulebase."""
        return cls(rulebase=Rulebase.POST, **kwargs)


class ProfileSettingFactory(factory.Factory):
    """Factory for creating ProfileSetting instances."""

    class Meta:
        model = ProfileSetting

    group = ["best-practice"]

    @classmethod
    def with_groups(cls, groups: list[str]) -> ProfileSetting:
        """Create a profile setting with specific groups."""
        return cls(group=groups)
