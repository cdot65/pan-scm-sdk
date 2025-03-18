#!/usr/bin/env python3
"""
This script patches the mkdocstrings and mkdocs-autorefs compatibility issues
to suppress deprecation warnings during the build process.
"""

import os
import sys
import subprocess

# Set environment variable to ignore deprecation warnings
os.environ["PYTHONWARNINGS"] = "ignore::DeprecationWarning"

# The command to run must be the remaining arguments
command = sys.argv[1:]
if not command:
    print("No command provided")
    sys.exit(1)

# Run the original command (mkdocs build)
sys.exit(subprocess.run(command).returncode)