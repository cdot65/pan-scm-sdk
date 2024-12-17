# scm/models/objects/__init__.py

from .address import (
    AddressCreateModel,
    AddressUpdateModel,
    AddressResponseModel,
)
from .address_group import (
    AddressGroupResponseModel,
    AddressGroupCreateModel,
    AddressGroupUpdateModel,
)
from .application import (
    ApplicationCreateModel,
    ApplicationResponseModel,
    ApplicationUpdateModel,
)
from .application_filters import (
    ApplicationFiltersCreateModel,
    ApplicationFiltersResponseModel,
    ApplicationFiltersUpdateModel,
)
from .application_group import (
    ApplicationGroupCreateModel,
    ApplicationGroupResponseModel,
    ApplicationGroupUpdateModel,
)
from .external_dynamic_lists import (
    ExternalDynamicListsCreateModel,
    ExternalDynamicListsResponseModel,
    ExternalDynamicListsUpdateModel,
)
from .hip_object import (
    HIPObjectCreateModel,
    HIPObjectResponseModel,
    HIPObjectUpdateModel,
)
from .service import (
    ServiceCreateModel,
    ServiceResponseModel,
    ServiceUpdateModel,
)
from .service_group import (
    ServiceGroupResponseModel,
    ServiceGroupCreateModel,
    ServiceGroupUpdateModel,
)
from .tag import (
    TagCreateModel,
    TagResponseModel,
    TagUpdateModel,
)

"""
# these are pydantic implementations created by not currently implemented in the API
# these will all return a 403 status code until implemented
from .auto_tag_actions import (
    AutoTagActionCreateModel,
    AutoTagActionResponseModel,
    AutoTagActionUpdateModel,
)
"""
