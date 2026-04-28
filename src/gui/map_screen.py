"""Map view screen: renders the GPS track and manages background data loading."""

import threading
import time
from typing import Callable

import flet as ft
import flet_map as fmap

from business_logic.main import get_clean_gps_data
from utils.constants import INITIAL_CENTER, INITIAL_ZOOM, TILE_URL, TRACK_ZOOM
from utils.logger import get_logger

logger = get_logger(__name__)


class MapScreen:
    """Map screen that owns the map widget, layers, and GPS loading logic."""

    def __init__(self, page: ft.Page, on_back: Callable[[], None]) -> None:
        self.page = page
        self.on_back = on_back

        self.status_text = ft.Text("Loading GPS data...", size=13, color=ft.Colors.BLUE_GREY_700)
        self.point_counter = ft.Text("", weight=ft.FontWeight.BOLD)
        self.loading_ring = ft.ProgressRing(width=18, height=18, stroke_width=2)

        self.marker_layer = fmap.MarkerLayer(markers=[])
        self.polyline_layer = fmap.PolylineLayer(polylines=[])
        self.gps_map = fmap.Map(
            expand=True,
            initial_center=INITIAL_CENTER,
            initial_zoom=INITIAL_ZOOM,
            min_zoom=3.0,
            max_zoom=18.0,
            layers=[
                fmap.TileLayer(url_template=TILE_URL),
                self.polyline_layer,
                self.marker_layer,
            ],
        )

    def build(self) -> ft.Control:
        """Return the full map view with toolbar and footer."""
        return ft.Column(
            controls=[
                self._build_toolbar(),
                self.gps_map,
                self._build_footer(),
            ],
            expand=True,
            spacing=0,
        )

    def load(self, file_path: str) -> None:
        """Start background GPS data loading for the given file."""
        self.status_text.value = "Loading GPS data..."
        self.loading_ring.visible = True
        threading.Thread(target=self._load_in_background, args=(file_path,), daemon=True).start()

    def _build_toolbar(self) -> ft.Container:
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        ft.Icons.ARROW_BACK,
                        tooltip="בחר קובץ אחר",
                        on_click=lambda _: self.on_back(),
                    ),
                    ft.VerticalDivider(),
                    ft.Text("GPS Track Viewer", size=18, weight=ft.FontWeight.BOLD),
                    ft.VerticalDivider(),
                    ft.Icon(ft.Icons.FLIGHT_TAKEOFF, color=ft.Colors.GREEN, size=16),
                    ft.Text("Takeoff"),
                    ft.Icon(ft.Icons.CIRCLE, color=ft.Colors.RED_600, size=10),
                    ft.Text("Track"),
                    ft.Icon(ft.Icons.FLIGHT_LAND, color=ft.Colors.BLUE, size=16),
                    ft.Text("Landing"),
                    ft.VerticalDivider(),
                    self.loading_ring,
                    self.point_counter,
                ],
                spacing=8,
            ),
            padding=ft.Padding.symmetric(horizontal=16, vertical=10),
            bgcolor=ft.Colors.SURFACE,
            border=ft.Border.only(bottom=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT)),
        )

    def _build_footer(self) -> ft.Container:
        return ft.Container(
            content=self.status_text,
            padding=ft.Padding.symmetric(horizontal=16, vertical=6),
            bgcolor=ft.Colors.SURFACE_CONTAINER,
        )

    def _load_in_background(self, file_path: str) -> None:
        try:
            logger.info("Background load started for: %s", file_path)
            start_time = time.perf_counter()

            df = get_clean_gps_data(file_path)

            if df.empty:
                logger.warning("No GPS points — aborting map update")
                self.status_text.value = "No GPS points found in file."
                return

            after_load_time = time.perf_counter()
            coords = [fmap.MapLatitudeLongitude(lat, lon) for lat, lon in zip(df["lat"], df["lon"])]
            after_coords_time = time.perf_counter()
            logger.debug(
                "Timing — data load: %.3fs | build coords: %.3fs | total: %.3fs | points: %d",
                after_load_time - start_time,
                after_coords_time - after_load_time,
                after_coords_time - start_time,
                len(coords),
            )

            self.marker_layer.markers = self._build_markers(coords)
            self.polyline_layer.polylines = [self._build_track(coords)]

            async def navigate() -> None:
                await self.gps_map.move_to(destination=coords[0], zoom=TRACK_ZOOM)

            self.page.run_task(navigate)

            self.point_counter.value = f"{len(coords)} points"
            self.status_text.value = "Track loaded successfully ✓"
            logger.info("Track rendered successfully (%d points)", len(coords))

        except FileNotFoundError:
            logger.error("Log file not found: %s", file_path)
            self.status_text.value = f"Error: file not found — {file_path}"
        except Exception as ex:
            logger.exception("Unexpected error during GPS load")
            self.status_text.value = f"Error: {ex}"
        finally:
            self.loading_ring.visible = False
            self.page.update()

    @staticmethod
    def _build_markers(coords: list[fmap.MapLatitudeLongitude]) -> list[fmap.Marker]:
        markers = [
            fmap.Marker(
                coordinates=c,
                content=ft.Icon(ft.Icons.CIRCLE, color=ft.Colors.RED_600, size=6),
            )
            for c in coords
        ]
        if len(coords) >= 1:
            markers[0] = fmap.Marker(
                coordinates=coords[0],
                content=ft.Icon(ft.Icons.FLIGHT_TAKEOFF, color=ft.Colors.GREEN, size=22),
            )
        if len(coords) >= 2:
            markers[-1] = fmap.Marker(
                coordinates=coords[-1],
                content=ft.Icon(ft.Icons.FLIGHT_LAND, color=ft.Colors.BLUE, size=22),
            )
        return markers

    @staticmethod
    def _build_track(coords: list[fmap.MapLatitudeLongitude]) -> fmap.PolylineMarker:
        return fmap.PolylineMarker(
            coordinates=coords,
            color=ft.Colors.ORANGE_600,
            stroke_width=2.5,
        )
