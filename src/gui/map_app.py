"""Flet application entry point for the GPS Track Viewer."""
import os
import sys

import flet as ft

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.constants import IS_DOCKER
from navigator import Navigator


def main(page: ft.Page) -> None:
    """Flet entry point — called once per connected client."""
    page.title = "GPS Track Viewer"
    page.window.width = 1000
    page.window.height = 750
    page.padding = 0

    navigator = Navigator(page)
    navigator.go_to_file_picker()


if __name__ == "__main__":
    if IS_DOCKER:
        # host="0.0.0.0" makes the server reachable from outside the container.
        ft.run(main, view=ft.AppView.FLET_APP_WEB, host="0.0.0.0", port=8080)
    else:
        ft.run(main)
