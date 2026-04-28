"""Shared logger factory for the project."""

import logging

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
_debug_modules = (
    "__main__", "map_app", "navigator",
    "map_screen", "file_picker_screen", "business_logic",
)
for _name in _debug_modules:
    logging.getLogger(_name).setLevel(logging.DEBUG)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger."""
    return logging.getLogger(name)
