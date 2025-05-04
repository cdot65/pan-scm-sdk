#!/usr/bin/env python3

# Python script to verify our renamed helper methods
# This script won't be executed, just to show how the API would be used

from scm.client import Scm

# Create a client
client = Scm(
    client_id="some_id",
    client_secret="some_secret",
    tsg_id="some_tsg_id",
)

# Access renamed helper methods (these should now be singular)
address = client.address
address_group = client.address_group
agent_version = client.agent_version  # renamed from agent_versions
application_filter = client.application_filter  # renamed from application_filters
auth_setting = client.auth_setting  # renamed from auth_settings
auto_tag_action = client.auto_tag_action  # renamed from auto_tag_actions
bandwidth_allocation = client.bandwidth_allocation  # renamed from bandwidth_allocations
bgp_route = client.bgp_route  # renamed from bgp_routing
external_dynamic_list = client.external_dynamic_list  # renamed from external_dynamic_lists
internal_dns_server = client.internal_dns_server  # renamed from internal_dns_servers
network_location = client.network_location  # renamed from network_locations
quarantined_device = client.quarantined_device  # renamed from quarantined_devices
remote_network = client.remote_network  # renamed from remote_networks
schedule = client.schedule  # unchanged, was already singular
service_connection = client.service_connection  # unchanged, was already singular