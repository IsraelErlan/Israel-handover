"""Background GPS data loading and map update logic."""
import logging
import os
import sys
import threading
import time

import flet as ft
import flet_map as fmap

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from constants import TRACK_ZOOM
from map_layers import build_markers, build_track

from business_logic.main import get_clean_gps_data

logger = logging.getLogger(__name__)


class GpsDataLoader:
    """Loads GPS data from a MAVLink file in a background thread and updates the map."""

    def __init__(
        self,
        page: ft.Page,
        gps_map: fmap.Map,
        marker_layer: fmap.MarkerLayer,
        polyline_layer: fmap.PolylineLayer,
        status_text: ft.Text,
        point_counter: ft.Text,
        loading_ring: ft.ProgressRing,
    ) -> None:
        self.page = page
        self.gps_map = gps_map
        self.marker_layer = marker_layer
        self.polyline_layer = polyline_layer
        self.status_text = status_text
        self.point_counter = point_counter
        self.loading_ring = loading_ring

    def start(self, file_path: str) -> None:
        """Spawn a daemon thread to load GPS data and update the map."""
        threading.Thread(target=self._load, args=(file_path,), daemon=True).start()

    def _load(self, file_path: str) -> None:
        try:
            logger.info("Background load started for: %s", file_path)
            t0 = time.perf_counter()

            df = get_clean_gps_data(file_path)

            if df.empty:
                logger.warning("No GPS points — aborting map update")
                self.status_text.value = "No GPS points found in file."
                return

            t1 = time.perf_counter()
            coords = [
                fmap.MapLatitudeLongitude(lat, lon)
                for lat, lon in zip(df["Latitude"], df["Longitude"])
            ]
            t2 = time.perf_counter()
            logger.debug(
                "Timing — data load: %.3fs | build coords: %.3fs | total: %.3fs | points: %d",
                t1 - t0,
                t2 - t1,
                t2 - t0,
                len(coords),
            )

            self.marker_layer.markers = build_markers(coords)
            self.polyline_layer.polylines = [build_track(coords)]

            # move_to is a coroutine — must be scheduled on Flet's event loop.
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
