import logging
import os
import sys

import flet as ft
import flet_map as fmap

sys.path.insert(0, os.path.dirname(__file__))

from constants import IS_DOCKER
from data_loader import GpsDataLoader
from map_layers import build_map
from ui_components import build_file_picker_screen, build_status_footer, build_toolbar

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
for _name in ("__main__", "app", "data_loader", "business_logic"):
    logging.getLogger(_name).setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)


class MapApp:
    def __init__(self, page: ft.Page) -> None:
        self.page = page
        page.title = "GPS Track Viewer"
        page.window.width = 1000
        page.window.height = 750
        page.padding = 0

        self.status_text = ft.Text("Loading GPS data...", size=13, color=ft.Colors.BLUE_GREY_700)
        self.point_counter = ft.Text("", weight=ft.FontWeight.BOLD)
        self.loading_ring = ft.ProgressRing(width=18, height=18, stroke_width=2)

        self.marker_layer = fmap.MarkerLayer(markers=[])
        self.polyline_layer = fmap.PolylineLayer(polylines=[])
        self.gps_map = build_map(self.marker_layer, self.polyline_layer)

        self.file_picker = ft.FilePicker()
        self.loader = GpsDataLoader(
            page=page,
            gps_map=self.gps_map,
            marker_layer=self.marker_layer,
            polyline_layer=self.polyline_layer,
            status_text=self.status_text,
            point_counter=self.point_counter,
            loading_ring=self.loading_ring,
        )

    def show_file_picker(self) -> None:
        self.page.add(build_file_picker_screen(self._on_pick_click))

    def show_map(self, file_path: str) -> None:
        self.page.controls.clear()
        self.page.add(
            ft.Column(
                controls=[
                    build_toolbar(self.loading_ring, self.point_counter),
                    self.gps_map,
                    build_status_footer(self.status_text),
                ],
                expand=True,
                spacing=0,
            )
        )
        self.loader.start(file_path)

    async def _on_pick_click(self, _: ft.ControlEvent) -> None:
        files = await self.file_picker.pick_files(
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["bin"],
        )
        if not files:
            return
        selected_path = files[0].path
        logger.info("File selected: %s", selected_path)
        self.show_map(selected_path)


def main(page: ft.Page) -> None:
    app = MapApp(page)
    app.show_file_picker()


if __name__ == "__main__":
    if IS_DOCKER:
        # FLET_APP_WEB: headless web server, no browser is opened automatically.
        # host="0.0.0.0" makes the server reachable from outside the container.
        ft.run(main, view=ft.AppView.FLET_APP_WEB, host="0.0.0.0", port=8080)
    else:
        ft.run(main)
