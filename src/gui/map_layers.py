"""Factory functions for flet_map layers used in the GPS Track Viewer."""
import flet as ft
import flet_map as fmap
from constants import INITIAL_CENTER, INITIAL_ZOOM, TILE_URL


def build_map(marker_layer: fmap.MarkerLayer, polyline_layer: fmap.PolylineLayer) -> fmap.Map:
    """Return a configured Map with tile, polyline, and marker layers."""
    return fmap.Map(
        expand=True,
        initial_center=INITIAL_CENTER,
        initial_zoom=INITIAL_ZOOM,
        min_zoom=3.0,
        max_zoom=18.0,
        layers=[
            fmap.TileLayer(
                url_template=TILE_URL,
            ),
            polyline_layer,
            marker_layer,
        ],
    )


def build_markers(coords: list[fmap.MapLatitudeLongitude]) -> list[fmap.Marker]:
    """Return Markers for every GPS point with takeoff/landing icons at the ends."""
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
    """Return a PolylineMarker connecting all GPS points."""
    return fmap.PolylineMarker(
        coordinates=coords,
        color=ft.Colors.ORANGE_600,
        stroke_width=2.5,
    )
