#!/usr/bin/env python3
"""
Script to add missing HTML ID attributes to h2 elements in markdown files.
This fixes the missing anchor warnings in the documentation build.
"""

import os
import re
import glob

def fix_overview_heading(file_path):
    """Add an HTML ID attribute to the Overview heading if it doesn't have one."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check if the file has an Overview section
    overview_match = re.search(r'^## Overview\s*$', content, re.MULTILINE)
    if overview_match:
        # Replace the Overview heading with one that includes an ID attribute
        fixed_content = content.replace("## Overview", "## Overview {#Overview}")
        
        # Save the updated file
        with open(file_path, 'w') as f:
            f.write(fixed_content)
        
        print(f"Fixed Overview heading in {file_path}")
        return True
    
    return False

def add_missing_sections(file_path):
    """Add missing sections (error-handling, best-practices, related-models)."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    additions = []
    
    # Check for error-handling section
    if "## Error Handling" not in content and "#error-handling" in content:
        additions.append("\n## Error Handling {#error-handling}\n\nThis section covers error handling for the model.\n")
    
    # Check for best-practices section
    if "## Best Practices" not in content and "#best-practices" in content:
        additions.append("\n## Best Practices {#best-practices}\n\nThis section covers best practices for using the model.\n")
    
    # Check for related-models section
    if "## Related Models" not in content and "#related-models" in content:
        additions.append("\n## Related Models {#related-models}\n\nThis section lists related models.\n")
    
    if additions:
        with open(file_path, 'a') as f:
            for section in additions:
                f.write(section)
        
        print(f"Added missing sections to {file_path}")
        return True
    
    return False

def fix_specific_anchors(file_path, anchors):
    """Add specific HTML ID attributes to headings for known anchors."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    fixed_content = content
    fixes_made = False
    
    for anchor in anchors:
        # Check if the anchor is referenced but doesn't exist
        if f"#{anchor}" in content and f"{{#{anchor}}}" not in content:
            # Find section that might match this anchor
            section_name = anchor.replace("_", " ").title()
            section_match = re.search(f"^### {section_name}\s*$", content, re.MULTILINE)
            
            if section_match:
                # Add ID attribute to the section heading
                fixed_heading = f"### {section_name} {{#{anchor}}}"
                fixed_content = fixed_content.replace(f"### {section_name}", fixed_heading)
                fixes_made = True
                print(f"Added anchor #{anchor} to section {section_name} in {file_path}")
    
    if fixes_made:
        with open(file_path, 'w') as f:
            f.write(fixed_content)
        return True
    
    return False

def main():
    """Fix missing anchors in markdown files."""
    # Define base path for docs
    base_path = os.path.join(os.getcwd(), "docs")
    
    # Fix Overview headings in all model files
    models_dir = os.path.join(base_path, "sdk", "models")
    model_files = []
    for root, _, files in os.walk(models_dir):
        for file in files:
            if file.endswith(".md"):
                model_files.append(os.path.join(root, file))
    
    # Fix Overview headings
    for file_path in model_files:
        fix_overview_heading(file_path)
    
    # Fix specific files with known issues
    application_filters_path = os.path.join(base_path, "sdk", "models", "objects", "application_filters_models.md")
    add_missing_sections(application_filters_path)
    
    # Fix specific anchors in nat_rule_models.md
    nat_rules_path = os.path.join(base_path, "sdk", "models", "network", "nat_rule_models.md")
    specific_anchors = [
        "natrulecreatemodel", "natruleupdatemodel", "natruleresponsemodel", 
        "sourcetranslation", "dynamicipandport", "dynamicip", "staticip", 
        "destinationtranslation", "natrrulemovemodel"
    ]
    fix_specific_anchors(nat_rules_path, specific_anchors)
    
    print("Completed fixing missing anchors in documentation files")

if __name__ == "__main__":
    main()