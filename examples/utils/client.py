#!/usr/bin/env python3
"""
Standardized client initialization utilities for Strata Cloud Manager SDK examples.

This module provides consistent authentication and client initialization
for SDK examples, with support for .env files and environment variables.

Features:
- Consistent SCM client initialization
- Environment variable loading from .env files
- Credential validation and sanitization
- User-friendly error messages for authentication issues

Usage:
    from examples.utils.client import ClientInitializer
    from examples.utils.logging import SDKLogger
    from scm.client import Scm

    # Initialize the logger
    logger = SDKLogger("example_name")

    # Initialize the client
    client_init = ClientInitializer(logger)
    client = client_init.initialize_client(Scm)

    # Use the client for API operations
    # ...
"""

import os
from pathlib import Path
from typing import Any, Type, Optional

try:
    from dotenv import load_dotenv

    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


class ClientInitializer:
    """Standardized client initialization for SCM example scripts."""

    def __init__(self, logger):
        """
        Initialize the client initializer.

        Args:
            logger: The SDKLogger instance for logging
        """
        self.logger = logger

    def load_environment_variables(self) -> bool:
        """
        Load environment variables from .env files.

        Attempts to load from:
        1. Current directory .env file
        2. Script's parent directory .env file

        Returns:
            bool: True if a .env file was loaded, False otherwise
        """
        if not DOTENV_AVAILABLE:
            self.logger.warning("python-dotenv not installed. Cannot load .env files.")
            self.logger.info("Install python-dotenv for .env support: pip install python-dotenv")
            return False

        # First try to load from current directory
        env_path = Path(".") / ".env"
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
            self.logger.success(f"Loaded environment variables from {env_path.absolute()}")
            return True
        else:
            # If not found, try the script's directory (one up from utils)
            script_dir = Path(__file__).parent.parent.absolute()
            env_path = script_dir / ".env"
            if env_path.exists():
                load_dotenv(dotenv_path=env_path)
                self.logger.success(f"Loaded environment variables from {env_path}")
                return True

        self.logger.warning("No .env file found in current directory or script directory")
        self.logger.info("Searched locations:")
        self.logger.info(f"  - {Path('.').absolute()}/.env")
        self.logger.info(f"  - {script_dir}/.env")
        self.logger.info("Using environment credentials instead")
        return False

    def validate_credentials(self) -> tuple:
        """
        Validate required SCM credentials from environment variables.

        Checks for the following environment variables:
        - SCM_CLIENT_ID
        - SCM_CLIENT_SECRET
        - SCM_TSG_ID
        - SCM_LOG_LEVEL (optional)

        Returns:
            tuple: (client_id, client_secret, tsg_id, log_level, missing_credentials)
                where missing_credentials is a list of missing credential names
        """
        # Get credentials from environment variables with fallbacks
        client_id = os.environ.get("SCM_CLIENT_ID", None)
        client_secret = os.environ.get("SCM_CLIENT_SECRET", None)
        tsg_id = os.environ.get("SCM_TSG_ID", None)
        log_level = os.environ.get("SCM_LOG_LEVEL", "DEBUG")

        # Validate required credentials
        missing = []
        if not client_id:
            missing.append("SCM_CLIENT_ID")
        if not client_secret:
            missing.append("SCM_CLIENT_SECRET")
        if not tsg_id:
            missing.append("SCM_TSG_ID")

        return client_id, client_secret, tsg_id, log_level, missing

    def initialize_client(self, client_class: Type[Any]) -> Optional[Any]:
        """
        Initialize the SCM client using credentials from environment variables or .env file.

        This method:
        1. Loads credentials from .env file (if available)
        2. Validates required credentials (client_id, client_secret, tsg_id)
        3. Initializes the SCM client with appropriate credentials

        Args:
            client_class: The client class to instantiate (Scm)

        Returns:
            An authenticated client instance ready for API calls, or None if credentials are missing
        """
        self.logger.section("AUTHENTICATION & INITIALIZATION")
        self.logger.operation_start("Loading credentials and initializing client")

        # Load environment variables from .env file
        self.load_environment_variables()

        # Validate credentials
        client_id, client_secret, tsg_id, log_level, missing = self.validate_credentials()

        # Check if any required credentials are missing
        if missing:
            self.logger.error(f"Missing required credentials: {', '.join(missing)}")
            self.logger.info("Please provide credentials in .env file or environment variables")
            self.logger.info("Example .env file format:")
            self.logger.info("  SCM_CLIENT_ID=your_client_id")
            self.logger.info("  SCM_CLIENT_SECRET=your_client_secret")
            self.logger.info("  SCM_TSG_ID=your_tsg_id")
            self.logger.info("  SCM_LOG_LEVEL=DEBUG")
            return None
        else:
            self.logger.success("All required credentials found")

        self.logger.operation_start("Creating SCM client")

        # Create the client with the appropriate class
        try:
            client = client_class(
                client_id=client_id,
                client_secret=client_secret,
                tsg_id=tsg_id,
                log_level=log_level,
            )

            # Mask the TSG ID for security in logs
            masked_tsg = (
                f"{tsg_id[:4]}{'*' * (len(tsg_id) - 8)}{tsg_id[-4:]}"
                if len(tsg_id or "") >= 8
                else "****"
            )

            self.logger.operation_complete(
                "SCM client initialization",
                f"TSG ID: {masked_tsg}",
            )
            return client

        except Exception as e:
            self.logger.error("Failed to initialize SCM client", e)
            self.logger.info("Please check your credentials and network connectivity")
            return None
