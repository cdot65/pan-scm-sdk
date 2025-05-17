# scm/utils/tag_colors.py


"""Utility functions for handling tag colors in the SCM SDK."""


def normalize_color_name(color_name: str) -> str:
    """Normalize the color name by converting it to lowercase.

    Replacing hyphens with spaces, and stripping whitespace.

    Args:
        color_name (str): The color name to normalize.

    Returns:
        str: The normalized color name.

    """
    return color_name.lower().replace("-", " ").strip()
