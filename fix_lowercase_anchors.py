#!/usr/bin/env python3
"""
Script to add lowercase HTML ID attributes to h2 elements in markdown files.
This fixes the additional missing anchor warnings in the documentation build.
"""

import os
import re
import glob

def add_lowercase_anchor(file_path):
    """Add a lowercase HTML ID attribute to the Overview heading."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check if the file has an Overview section with uppercase ID
    overview_match = re.search(r'^## Overview {#Overview}', content, re.MULTILINE)
    if overview_match:
        # Add the lowercase anchor
        fixed_content = content.replace(
            "## Overview {#Overview}", 
            "## Overview {#Overview}\n<span id=\"overview\"></span>"
        )
        
        # Save the updated file
        with open(file_path, 'w') as f:
            f.write(fixed_content)
        
        print(f"Added lowercase 'overview' anchor to {file_path}")
        return True
    
    return False

def main():
    """Fix missing lowercase anchors in markdown files."""
    # Define base path for docs
    base_path = os.path.join(os.getcwd(), "docs")
    
    # Files with missing lowercase anchors
    problem_files = [
        os.path.join(base_path, "sdk", "models", "mobile_agent", "index.md"),
        os.path.join(base_path, "sdk", "models", "mobile_agent", "agent_versions_models.md"),
        os.path.join(base_path, "sdk", "models", "network", "index.md"),
        os.path.join(base_path, "sdk", "models", "objects", "index.md"),
        os.path.join(base_path, "sdk", "models", "objects", "application_filters_models.md"),
        os.path.join(base_path, "sdk", "models", "operations", "index.md"),
        os.path.join(base_path, "sdk", "models", "security_services", "index.md"),
    ]
    
    # Fix each file
    for file_path in problem_files:
        add_lowercase_anchor(file_path)
    
    print("Completed fixing missing lowercase anchors in documentation files")

if __name__ == "__main__":
    main()