"""File picker landing screen."""

from typing import Callable, cast

import flet as ft

from utils.logger import get_logger

logger = get_logger(__name__)


class FilePickerScreen:
    """Landing screen that lets the user choose a .bin log file."""

    def __init__(self, page: ft.Page, on_file_selected: Callable[[str], None]) -> None:
        self.page = page
        self.on_file_selected = on_file_selected
        self.file_picker = ft.FilePicker()

    def build(self) -> ft.Control:
        """Return the full-screen file-picker landing view."""
        return ft.Container(
            content=ft.Column(
                controls=cast(
                    list[ft.Control],
                    [
                        ft.Icon(ft.Icons.FLIGHT, size=64, color=ft.Colors.BLUE_GREY_400),
                        ft.Text(
                            "GPS Track Viewer",
                            size=28,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            "בחר קובץ MAVLink להצגת המסלול",
                            size=14,
                            color=ft.Colors.BLUE_GREY_600,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Button(
                            "בחר קובץ .bin",
                            icon=ft.Icons.FOLDER_OPEN,
                            on_click=self._on_pick_click,
                        ),
                    ],
                ),
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
            ),
            expand=True,
            alignment=ft.Alignment.CENTER,
        )

    async def _on_pick_click(self, _: ft.Event[ft.Button]) -> None:
        try:
            files = await self.file_picker.pick_files(
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["bin"],
            )
        except Exception:
            logger.exception("File picker failed unexpectedly")
            return

        if not files:
            logger.debug("File picker cancelled by user")
            return

        selected_path = files[0].path
        if not selected_path:
            logger.warning("File picker returned a file with no path")
            return

        logger.info("File selected: %s", selected_path)
        self.on_file_selected(selected_path)
