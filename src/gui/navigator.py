"""Screen navigator — controls transitions between app screens."""
import flet as ft

from file_picker_screen import FilePickerScreen
from map_screen import MapScreen
from utils.logger import get_logger

logger = get_logger(__name__)


class Navigator:
    """Owns both screens and switches between them on the Flet page."""

    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.file_picker_screen = FilePickerScreen(page, on_file_selected=self._go_to_map)
        self.map_screen = MapScreen(page, on_back=self.go_to_file_picker)

    def go_to_file_picker(self) -> None:
        self.page.controls.clear()
        self.page.add(self.file_picker_screen.build())

    def _go_to_map(self, file_path: str) -> None:
        logger.info("Switching to map view for: %s", file_path)
        self.page.controls.clear()
        self.page.add(self.map_screen.build())
        self.map_screen.load(file_path)
