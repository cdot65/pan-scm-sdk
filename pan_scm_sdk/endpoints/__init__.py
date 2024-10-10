# pan_scm_sdk/endpoints/__init__.py

from .addresses import ADDRESSES_ENDPOINTS
from .address_groups import ADDRESS_GROUPS_ENDPOINTS
from .applications import APPLICATIONS_ENDPOINTS

# more on the way


API_ENDPOINTS = {
    **ADDRESSES_ENDPOINTS,
    **ADDRESS_GROUPS_ENDPOINTS,
    **APPLICATIONS_ENDPOINTS,
    # more on the way
}
