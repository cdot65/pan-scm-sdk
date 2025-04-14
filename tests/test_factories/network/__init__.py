"""Network factories for testing."""

from tests.test_factories.network.nat_rules import (
    InterfaceAddressFactory,
    NatRuleCreateApiFactory,
    NatRuleCreateModelFactory,
    NatRuleMoveApiFactory,
    NatRuleMoveModelFactory,
    NatRuleResponseFactory,
    NatRuleUpdateApiFactory,
    NatRuleUpdateModelFactory,
    SourceTranslationFactory,
)

# Explicitly export these factories
__all__ = [
    "InterfaceAddressFactory",
    "NatRuleCreateApiFactory",
    "NatRuleCreateModelFactory",
    "NatRuleMoveApiFactory",
    "NatRuleMoveModelFactory",
    "NatRuleResponseFactory",
    "NatRuleUpdateApiFactory",
    "NatRuleUpdateModelFactory",
    "SourceTranslationFactory",
]
