# scm/models/security/__init__.py

from .anti_spyware_profiles import (
    AntiSpywareProfileCreateModel,
    AntiSpywareProfileResponseModel,
    AntiSpywareProfileUpdateModel,
)
from .decryption_profiles import (
    DecryptionProfileCreateModel,
    DecryptionProfileResponseModel,
    DecryptionProfileUpdateModel,
)
from .dns_security_profiles import (
    DNSSecurityProfileCreateModel,
    DNSSecurityProfileResponseModel,
    DNSSecurityProfileUpdateModel,
)
from .security_rules import (
    SecurityRuleCreateModel,
    SecurityRuleResponseModel,
    SecurityRuleMoveModel,
    SecurityRuleUpdateModel,
    SecurityRuleRulebase,
)
from .url_categories import (
    URLCategoriesCreateModel,
    URLCategoriesUpdateModel,
    URLCategoriesResponseModel,
)
from .vulnerability_protection_profiles import (
    VulnerabilityProfileCreateModel,
    VulnerabilityProfileResponseModel,
    VulnerabilityProfileUpdateModel,
)
from .wildfire_antivirus_profiles import (
    WildfireAvProfileCreateModel,
    WildfireAvProfileResponseModel,
    WildfireAvProfileUpdateModel,
)
