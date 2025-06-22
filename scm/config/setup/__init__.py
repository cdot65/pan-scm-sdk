"""scm.config.setup: Setup-related service classes."""

# from .devices import Devices
from .device import Device
from .folder import Folder
from .label import Label
from .snippet import Snippet
from .variable import Variable

__all__ = [
    "Device",
    "Folder",
    "Label",
    "Snippet",
    "Variable",
]
