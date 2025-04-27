#!/usr/bin/env python3
"""
Example script for managing bandwidth allocations in Strata Cloud Manager.

This script demonstrates how to use the SCM SDK to create, list, update,
and delete bandwidth allocations.
"""

import os
import sys
import logging
import argparse

from dotenv import load_dotenv

from scm.client import ScmClient
from scm.models.deployment import (
    BandwidthAllocationCreateModel,
    BandwidthAllocationUpdateModel,
    BandwidthAllocationResponseModel,
)


def setup_logging(level: str = "INFO") -> None:
    """Set up logging for the script."""
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {level}")

    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )


def setup_client() -> ScmClient:
    """Set up the SCM client using environment variables."""
    # Load environment variables from .env file
    load_dotenv()

    # Get credentials from environment
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    tsg_id = os.getenv("TSG_ID")

    if not all([client_id, client_secret, tsg_id]):
        raise EnvironmentError(
            "Missing one or more required environment variables: CLIENT_ID, CLIENT_SECRET, TSG_ID"
        )

    # Initialize the client
    return ScmClient(
        client_id=client_id,
        client_secret=client_secret,
        tsg_id=tsg_id,
        log_level="INFO",
    )


def create_bandwidth_allocation(client: ScmClient, args: argparse.Namespace) -> None:
    """Create a new bandwidth allocation."""
    # Prepare QoS settings if enabled
    qos = None
    if args.qos_enabled:
        qos = {
            "enabled": True,
            "customized": args.qos_customized,
            "profile": args.qos_profile,
        }
        if args.qos_guaranteed_ratio is not None:
            qos["guaranteed_ratio"] = args.qos_guaranteed_ratio

    # Prepare the data
    allocation_data = {
        "name": args.name,
        "allocated_bandwidth": args.bandwidth,
        "spn_name_list": args.spn_list.split(","),
    }

    if qos:
        allocation_data["qos"] = qos

    # Use Pydantic model to validate the data
    create_model = BandwidthAllocationCreateModel(**allocation_data)

    # Convert to dict for API call
    payload = create_model.model_dump(exclude_unset=True)

    try:
        # Create the bandwidth allocation
        result = client.bandwidth_allocation.create(payload)
        print(f"Successfully created bandwidth allocation '{result.name}'")
        print_allocation_details(result)
    except Exception as e:
        logging.error(f"Failed to create bandwidth allocation: {e}")
        sys.exit(1)


def list_bandwidth_allocations(client: ScmClient, args: argparse.Namespace) -> None:
    """List bandwidth allocations with optional filtering."""
    filters = {}

    # Apply filters if provided
    if args.filter_name:
        filters["name"] = args.filter_name
    if args.filter_bandwidth:
        filters["allocated_bandwidth"] = args.filter_bandwidth
    if args.filter_spn:
        filters["spn_name_list"] = args.filter_spn
    if args.filter_qos_enabled is not None:
        filters["qos_enabled"] = args.filter_qos_enabled

    try:
        # List allocations with filters
        allocations = client.bandwidth_allocation.list(**filters)

        # Display results
        print(f"Found {len(allocations)} bandwidth allocation(s)")
        for i, allocation in enumerate(allocations, 1):
            print(f"\n--- Allocation {i} ---")
            print_allocation_details(allocation)
    except Exception as e:
        logging.error(f"Failed to list bandwidth allocations: {e}")
        sys.exit(1)


def update_bandwidth_allocation(client: ScmClient, args: argparse.Namespace) -> None:
    """Update an existing bandwidth allocation."""
    # Get current allocation
    try:
        current = client.bandwidth_allocation.get(args.name)
        if not current:
            logging.error(f"Bandwidth allocation '{args.name}' not found")
            sys.exit(1)
    except Exception as e:
        logging.error(f"Failed to get current bandwidth allocation: {e}")
        sys.exit(1)

    # Prepare update data
    update_data = {
        "name": args.name,
        "allocated_bandwidth": args.bandwidth
        if args.bandwidth is not None
        else current.allocated_bandwidth,
        "spn_name_list": args.spn_list.split(",") if args.spn_list else current.spn_name_list,
    }

    # Update QoS if specified
    if args.qos_enabled is not None:
        qos = {"enabled": args.qos_enabled}

        if args.qos_enabled:
            # Only include these if QoS is enabled
            if args.qos_customized is not None:
                qos["customized"] = args.qos_customized
            elif current.qos and current.qos.customized is not None:
                qos["customized"] = current.qos.customized

            if args.qos_profile is not None:
                qos["profile"] = args.qos_profile
            elif current.qos and current.qos.profile is not None:
                qos["profile"] = current.qos.profile

            if args.qos_guaranteed_ratio is not None:
                qos["guaranteed_ratio"] = args.qos_guaranteed_ratio
            elif current.qos and current.qos.guaranteed_ratio is not None:
                qos["guaranteed_ratio"] = current.qos.guaranteed_ratio

        update_data["qos"] = qos
    elif current.qos:
        # Keep current QoS settings if not specified
        update_data["qos"] = {
            "enabled": current.qos.enabled,
            "customized": current.qos.customized,
            "profile": current.qos.profile,
            "guaranteed_ratio": current.qos.guaranteed_ratio,
        }

    # Use Pydantic model to validate the data
    update_model = BandwidthAllocationUpdateModel(**update_data)

    # Convert to dict for API call
    payload = update_model.model_dump(exclude_unset=True)

    try:
        # Update the bandwidth allocation
        result = client.bandwidth_allocation.update(payload)
        print(f"Successfully updated bandwidth allocation '{result.name}'")
        print_allocation_details(result)
    except Exception as e:
        logging.error(f"Failed to update bandwidth allocation: {e}")
        sys.exit(1)


def delete_bandwidth_allocation(client: ScmClient, args: argparse.Namespace) -> None:
    """Delete a bandwidth allocation."""
    try:
        # Get current allocation to verify it exists
        current = client.bandwidth_allocation.get(args.name)
        if not current:
            logging.error(f"Bandwidth allocation '{args.name}' not found")
            sys.exit(1)

        # Convert spn_name_list to comma-separated string
        spn_list = ",".join(current.spn_name_list)

        # Delete the allocation
        client.bandwidth_allocation.delete(args.name, spn_list)
        print(f"Successfully deleted bandwidth allocation '{args.name}'")
    except Exception as e:
        logging.error(f"Failed to delete bandwidth allocation: {e}")
        sys.exit(1)


def print_allocation_details(allocation: BandwidthAllocationResponseModel) -> None:
    """Print details of a bandwidth allocation."""
    print(f"Name: {allocation.name}")
    print(f"Allocated Bandwidth: {allocation.allocated_bandwidth} Mbps")
    print(f"SPN List: {', '.join(allocation.spn_name_list)}")

    if allocation.qos:
        print("QoS Settings:")
        print(f"  Enabled: {allocation.qos.enabled}")
        if allocation.qos.enabled:
            print(f"  Customized: {allocation.qos.customized}")
            print(f"  Profile: {allocation.qos.profile}")
            print(f"  Guaranteed Ratio: {allocation.qos.guaranteed_ratio}")
    else:
        print("QoS: Disabled")


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Manage SCM bandwidth allocations")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new bandwidth allocation")
    create_parser.add_argument("--name", required=True, help="Name of the allocation")
    create_parser.add_argument(
        "--bandwidth", type=float, required=True, help="Allocated bandwidth in Mbps"
    )
    create_parser.add_argument("--spn-list", required=True, help="Comma-separated list of SPNs")
    create_parser.add_argument("--qos-enabled", action="store_true", help="Enable QoS")
    create_parser.add_argument("--qos-customized", action="store_true", help="Use customized QoS")
    create_parser.add_argument("--qos-profile", help="QoS profile name")
    create_parser.add_argument(
        "--qos-guaranteed-ratio", type=float, help="QoS guaranteed ratio (0.0-1.0)"
    )

    # List command
    list_parser = subparsers.add_parser("list", help="List bandwidth allocations")
    list_parser.add_argument("--filter-name", help="Filter by name")
    list_parser.add_argument("--filter-bandwidth", type=float, help="Filter by allocated bandwidth")
    list_parser.add_argument("--filter-spn", help="Filter by SPN name")
    list_parser.add_argument("--filter-qos-enabled", type=bool, help="Filter by QoS enabled status")

    # Update command
    update_parser = subparsers.add_parser("update", help="Update a bandwidth allocation")
    update_parser.add_argument("--name", required=True, help="Name of the allocation to update")
    update_parser.add_argument("--bandwidth", type=float, help="New allocated bandwidth in Mbps")
    update_parser.add_argument("--spn-list", help="New comma-separated list of SPNs")
    update_parser.add_argument("--qos-enabled", type=bool, help="Enable/disable QoS")
    update_parser.add_argument("--qos-customized", type=bool, help="Use customized QoS")
    update_parser.add_argument("--qos-profile", help="QoS profile name")
    update_parser.add_argument(
        "--qos-guaranteed-ratio", type=float, help="QoS guaranteed ratio (0.0-1.0)"
    )

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a bandwidth allocation")
    delete_parser.add_argument("--name", required=True, help="Name of the allocation to delete")

    # Parse arguments
    args = parser.parse_args()

    # Set up logging
    setup_logging("INFO")

    # Set up client
    try:
        client = setup_client()
    except Exception as e:
        logging.error(f"Failed to set up client: {e}")
        sys.exit(1)

    # Execute command
    if args.command == "create":
        create_bandwidth_allocation(client, args)
    elif args.command == "list":
        list_bandwidth_allocations(client, args)
    elif args.command == "update":
        update_bandwidth_allocation(client, args)
    elif args.command == "delete":
        delete_bandwidth_allocation(client, args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
