import flet as ft
import flet_map as fmap
import logging
import threading
import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from business_logic.main import get_clean_gps_data

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
# Only show DEBUG+ for our own code; keep flet's internal loggers silent.
for _name in ("__main__", "map_component", "business_logic"):
    logging.getLogger(_name).setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

# In Docker: DATA_FILE is injected via environment variable (see docker-compose.yml).
# Locally: falls back to the hardcoded Windows path.
_PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
DATA_FILE = os.getenv(
    "DATA_FILE",
    os.path.normpath(os.path.join(_PROJECT_ROOT, "data", "log_file_test_01.bin")),
)

IS_DOCKER = os.getenv("FLET_ENV") == "docker"

INITIAL_CENTER = fmap.MapLatitudeLongitude(31.5, 35.0)
INITIAL_ZOOM = 8.0
TRACK_ZOOM = 13.0
TILE_URL = "https://basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png"


# -----------------------------------------------------------------------------
# Map layer builders
# -----------------------------------------------------------------------------

def build_map(marker_layer: fmap.MarkerLayer, polyline_layer: fmap.PolylineLayer) -> fmap.Map:
    return fmap.Map(
        expand=True,
        initial_center=INITIAL_CENTER,
        initial_zoom=INITIAL_ZOOM,
        min_zoom=3.0,
        max_zoom=18.0,
        layers=[
            fmap.TileLayer(
                url_template=TILE_URL,
                # CartoDB requires an identifiable user-agent to avoid 403 blocks.
                user_agent_package_name="com.israelhandover.gpstracker",
            ),
            polyline_layer,
            marker_layer,
        ],
    )


def build_markers(coords: list[fmap.MapLatitudeLongitude]) -> list[fmap.Marker]:
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


def build_track(coords: list[fmap.MapLatitudeLongitude]) -> fmap.PolylineMarker:
    return fmap.PolylineMarker(
        coordinates=coords,
        color=ft.Colors.ORANGE_600,
        stroke_width=2.5,
    )


# -----------------------------------------------------------------------------
# UI component builders
# -----------------------------------------------------------------------------

def build_toolbar(loading_ring: ft.ProgressRing, point_counter: ft.Text) -> ft.Container:
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Text("GPS Track Viewer", size=18, weight=ft.FontWeight.BOLD),
                ft.VerticalDivider(),
                ft.Icon(ft.Icons.FLIGHT_TAKEOFF, color=ft.Colors.GREEN, size=16),
                ft.Text("Takeoff"),
                ft.Icon(ft.Icons.CIRCLE, color=ft.Colors.RED_600, size=10),
                ft.Text("Track"),
                ft.Icon(ft.Icons.FLIGHT_LAND, color=ft.Colors.BLUE, size=16),
                ft.Text("Landing"),
                ft.VerticalDivider(),
                loading_ring,
                point_counter,
            ],
            spacing=8,
        ),
        padding=ft.Padding.symmetric(horizontal=16, vertical=10),
        bgcolor=ft.Colors.SURFACE,
        border=ft.Border.only(bottom=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT)),
    )


def build_status_footer(status_text: ft.Text) -> ft.Container:
    return ft.Container(
        content=status_text,
        padding=ft.Padding.symmetric(horizontal=16, vertical=6),
        bgcolor=ft.Colors.SURFACE_CONTAINER,
    )


# -----------------------------------------------------------------------------
# Data loading
# -----------------------------------------------------------------------------

def start_loading(
    page: ft.Page,
    gps_map: fmap.Map,
    marker_layer: fmap.MarkerLayer,
    polyline_layer: fmap.PolylineLayer,
    status_text: ft.Text,
    point_counter: ft.Text,
    loading_ring: ft.ProgressRing,
) -> None:
    """Loads GPS data on a background thread so the map renders immediately."""

    def load() -> None:
        try:
            logger.info("Background load started for: %s", DATA_FILE)
            t0 = time.perf_counter()

            df = get_clean_gps_data(DATA_FILE)

            if df.empty:
                logger.warning("No GPS points — aborting map update")
                status_text.value = "No GPS points found in file."
                return

            t1 = time.perf_counter()
            coords = [
                fmap.MapLatitudeLongitude(lat, lon)
                for lat, lon in zip(df["Latitude"], df["Longitude"])
            ]
            t2 = time.perf_counter()
            logger.debug(
                "Timing — data load: %.3fs | build coords: %.3fs | total: %.3fs | points: %d",
                t1 - t0, t2 - t1, t2 - t0, len(coords),
            )

            marker_layer.markers = build_markers(coords)
            polyline_layer.polylines = [build_track(coords)]

            # move_to is a coroutine — must be scheduled on Flet's event loop.
            async def navigate() -> None:
                await gps_map.move_to(destination=coords[0], zoom=TRACK_ZOOM)

            page.run_task(navigate)

            point_counter.value = f"{len(coords)} points"
            status_text.value = "Track loaded successfully ✓"
            logger.info("Track rendered successfully (%d points)", len(coords))

        except FileNotFoundError:
            logger.error("Log file not found: %s", DATA_FILE)
            status_text.value = f"Error: file not found — {DATA_FILE}"
        except Exception as ex:
            logger.exception("Unexpected error during GPS load")
            status_text.value = f"Error: {ex}"
        finally:
            loading_ring.visible = False
            page.update()

    threading.Thread(target=load, daemon=True).start()


# -----------------------------------------------------------------------------
# Flet entry point
# -----------------------------------------------------------------------------

def main(page: ft.Page) -> None:
    page.title = "GPS Track Viewer"
    page.window.width = 1000
    page.window.height = 750
    page.padding = 0

    status_text = ft.Text("Loading GPS data...", size=13, color=ft.Colors.BLUE_GREY_700)
    point_counter = ft.Text("", weight=ft.FontWeight.BOLD)
    loading_ring = ft.ProgressRing(width=18, height=18, stroke_width=2)

    marker_layer = fmap.MarkerLayer(markers=[])
    polyline_layer = fmap.PolylineLayer(polylines=[])
    gps_map = build_map(marker_layer, polyline_layer)

    page.add(
        ft.Column(
            controls=[
                build_toolbar(loading_ring, point_counter),
                gps_map,
                build_status_footer(status_text),
            ],
            expand=True,
            spacing=0,
        )
    )

    start_loading(page, gps_map, marker_layer, polyline_layer,
                  status_text, point_counter, loading_ring)


if __name__ == "__main__":
    if IS_DOCKER:
        # FLET_APP_WEB: headless web server, no browser is opened automatically.
        # host="0.0.0.0" makes the server reachable from outside the container.
        ft.run(main, view=ft.AppView.FLET_APP_WEB, host="0.0.0.0", port=8080)
    else:
        ft.run(main)
