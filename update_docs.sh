#!/bin/bash

# Script to update singular vs plural helper method names in markdown files

# Array of search and replace pairs
declare -a replacements=(
    "client\.internal_dns_servers" "client\.internal_dns_server"
    "client\.network_locations" "client\.network_location"
    "client\.remote_networks" "client\.remote_network"
    "client\.bandwidth_allocations" "client\.bandwidth_allocation"
    "client\.auth_settings" "client\.auth_setting"
    "client\.agent_versions" "client\.agent_version"
    "client\.quarantined_devices" "client\.quarantined_device"
    "client\.external_dynamic_lists" "client\.external_dynamic_list"
    "client\.application_filters" "client\.application_filter"
)

# Directory to search in
docs_dir="/home/cdot/development/cdot65/pan-scm-sdk"

# Loop through each search/replace pair
for ((i=0; i<${#replacements[@]}; i+=2)); do
    search="${replacements[$i]}"
    replace="${replacements[$i+1]}"
    
    echo "Replacing '$search' with '$replace' in markdown files..."
    
    # Find all markdown files containing the search pattern and replace the text
    grep -l "$search" --include="*.md" -r "$docs_dir" | while read -r file; do
        echo "Updating file: $file"
        # Use sed for the replacement
        sed -i "s/$search/$replace/g" "$file"
    done
done

echo "Done! All replacements complete."