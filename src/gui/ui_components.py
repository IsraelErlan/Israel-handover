from typing import Callable

import flet as ft


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


def build_file_picker_screen(on_pick_click: Callable) -> ft.Container:
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(ft.Icons.FLIGHT, size=64, color=ft.Colors.BLUE_GREY_400),
                ft.Text("GPS Track Viewer", size=28, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Text("בחר קובץ MAVLink להצגת המסלול", size=14, color=ft.Colors.BLUE_GREY_600, text_align=ft.TextAlign.CENTER),
                ft.Button(
                    "בחר קובץ .bin",
                    icon=ft.Icons.FOLDER_OPEN,
                    on_click=on_pick_click,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
        ),
        expand=True,
        alignment=ft.Alignment.CENTER,
    )
