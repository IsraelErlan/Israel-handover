"""Tests for GUI components: FilePickerScreen, MapScreen, Navigator."""

from unittest.mock import AsyncMock, MagicMock, patch

import flet as ft
import flet_map as fmap
import pandas as pd
import pytest

from file_picker_screen import FilePickerScreen
from map_screen import MapScreen
from navigator import Navigator


def _make_page() -> MagicMock:
    page = MagicMock(spec=ft.Page)
    return page


def _make_map_screen() -> tuple[MapScreen, MagicMock]:
    page = _make_page()
    screen = MapScreen(page, on_back=MagicMock())
    screen.gps_map.move_to = AsyncMock()
    return screen, page


_GPS_DF = pd.DataFrame({"lat": [31.5, 31.6, 31.7], "lon": [35.0, 35.1, 35.2]})
_EMPTY_DF = pd.DataFrame({"lat": [], "lon": []})


# ── FilePickerScreen ──────────────────────────────────────────────────────────


class TestFilePickerScreenOnPickClick:

    def _make_screen(self) -> tuple[FilePickerScreen, MagicMock]:
        callback = MagicMock()
        screen = FilePickerScreen(_make_page(), on_file_selected=callback)
        return screen, callback

    async def test_calls_callback_with_selected_path(self):
        screen, callback = self._make_screen()
        mock_file = MagicMock()
        mock_file.path = "/flights/log.bin"
        screen.file_picker.pick_files = AsyncMock(return_value=[mock_file])

        await screen._on_pick_click(MagicMock())

        callback.assert_called_once_with("/flights/log.bin")

    async def test_cancelled_does_not_call_callback(self):
        screen, callback = self._make_screen()
        screen.file_picker.pick_files = AsyncMock(return_value=None)

        await screen._on_pick_click(MagicMock())

        callback.assert_not_called()

    async def test_picker_exception_is_swallowed(self):
        screen, callback = self._make_screen()
        screen.file_picker.pick_files = AsyncMock(side_effect=RuntimeError("picker broke"))

        await screen._on_pick_click(MagicMock())  # must not raise

        callback.assert_not_called()


# ── MapScreen — _build_markers ────────────────────────────────────────────────


def _coord(lat: float = 31.5, lon: float = 35.0) -> fmap.MapLatitudeLongitude:
    return fmap.MapLatitudeLongitude(lat, lon)


class TestBuildMarkers:

    def test_empty_list_returns_empty(self):
        assert MapScreen._build_markers([]) == []

    def test_many_points_colors(self):
        coords = [_coord(31.0 + i * 0.1, 35.0) for i in range(5)]
        markers = MapScreen._build_markers(coords)
        assert markers[0].content.color == ft.Colors.GREEN
        assert markers[-1].content.color == ft.Colors.BLUE
        for m in markers[1:-1]:
            assert m.content.color == ft.Colors.RED_600


# ── MapScreen — _build_track ──────────────────────────────────────────────────


class TestBuildTrack:

    def test_coordinates_match_input(self):
        coords = [_coord(31.0 + i * 0.1, 35.0) for i in range(4)]
        track = MapScreen._build_track(coords)
        assert track.coordinates == coords


# ── MapScreen — load() ────────────────────────────────────────────────────────


class TestMapScreenLoad:

    def test_schedules_background_task(self):
        screen, page = _make_map_screen()
        screen.load("flight.bin")
        page.run_task.assert_called_once_with(screen._load_in_background, "flight.bin")


# ── MapScreen — _load_in_background() ────────────────────────────────────────


class TestLoadInBackground:

    async def test_success_moves_map_to_first_point(self):
        screen, _ = _make_map_screen()
        with patch("map_screen.get_clean_gps_data", return_value=_GPS_DF):
            await screen._load_in_background("flight.bin")
        screen.gps_map.move_to.assert_called_once()

    async def test_empty_df_shows_no_gps_message(self):
        screen, _ = _make_map_screen()
        with patch("map_screen.get_clean_gps_data", return_value=_EMPTY_DF):
            await screen._load_in_background("flight.bin")
        assert "No GPS points" in screen.status_text.value

    async def test_unexpected_error_shows_message(self):
        screen, _ = _make_map_screen()
        with patch("map_screen.get_clean_gps_data", side_effect=RuntimeError("disk full")):
            await screen._load_in_background("flight.bin")
        assert "disk full" in screen.status_text.value


# ── Navigator ─────────────────────────────────────────────────────────────────


class TestNavigator:

    def _make_navigator(self) -> tuple[Navigator, MagicMock]:
        page = _make_page()
        nav = Navigator(page)
        return nav, page

    def test_go_to_file_picker_adds_one_control(self):
        nav, page = self._make_navigator()
        nav.go_to_file_picker()
        page.add.assert_called_once()

    def test_go_to_map_calls_load_with_file_path(self):
        nav, page = self._make_navigator()
        nav.map_screen.load = MagicMock()
        nav._go_to_map("flight.bin")
        nav.map_screen.load.assert_called_once_with("flight.bin")
