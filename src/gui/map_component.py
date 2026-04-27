import flet as ft
import flet_map as fmap
import threading
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from business_logic.main import get_clean_gps_data

# ─────────────────────────────────────────────────────────────────────────────
# קבועים
# ─────────────────────────────────────────────────────────────────────────────

# בדוקר: DATA_FILE מגיע ממשתנה סביבה (מוגדר ב-docker-compose.yml)
# לוקאלי: fallback לנתיב Windows
DATA_FILE = os.getenv(
    "DATA_FILE",
    r"C:\Users\adika\OneDrive\Desktop\israel_handover\data\log_file_test_01.bin",
)

IS_DOCKER = os.getenv("FLET_ENV") == "docker"
INITIAL_CENTER = fmap.MapLatitudeLongitude(31.5, 35.0)
INITIAL_ZOOM = 8.0
TRACK_ZOOM = 13.0
TILE_URL = "https://basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png"


# ─────────────────────────────────────────────────────────────────────────────
# בניית רכיבי המפה
# ─────────────────────────────────────────────────────────────────────────────

def build_map(marker_layer: fmap.MarkerLayer, polyline_layer: fmap.PolylineLayer) -> fmap.Map:
    """יוצר את רכיב המפה עם שלוש שכבות: אריחים, מסלול, סמנים."""
    return fmap.Map(
        expand=True,
        initial_center=INITIAL_CENTER,
        initial_zoom=INITIAL_ZOOM,
        min_zoom=3.0,
        max_zoom=18.0,
        layers=[
            fmap.TileLayer(
                url_template=TILE_URL,
                user_agent_package_name="com.israelhandover.gpstracker",
            ),
            polyline_layer,
            marker_layer,
        ],
    )


def build_markers(coords: list[fmap.MapLatitudeLongitude]) -> list[fmap.Marker]:
    """בונה רשימת סמנים: עיגולים לנקודות ביניים, אייקונים מיוחדים להמראה/נחיתה."""
    markers = [
        fmap.Marker(
            coordinates=c,
            content=ft.Icon(ft.Icons.CIRCLE, color=ft.Colors.RED_600, size=6),
        )
        for c in coords
    ]
    markers[0] = fmap.Marker(
        coordinates=coords[0],
        content=ft.Icon(ft.Icons.FLIGHT_TAKEOFF, color=ft.Colors.GREEN, size=22),
    )
    markers[-1] = fmap.Marker(
        coordinates=coords[-1],
        content=ft.Icon(ft.Icons.FLIGHT_LAND, color=ft.Colors.BLUE, size=22),
    )
    return markers


def build_track(coords: list[fmap.MapLatitudeLongitude]) -> fmap.PolylineMarker:
    """בונה קו מסלול כתום שמחבר את כל הנקודות."""
    return fmap.PolylineMarker(
        coordinates=coords,
        color=ft.Colors.ORANGE_600,
        stroke_width=2.5,
    )


# ─────────────────────────────────────────────────────────────────────────────
# בניית רכיבי ה-UI
# ─────────────────────────────────────────────────────────────────────────────

def build_toolbar(loading_ring: ft.ProgressRing, point_counter: ft.Text) -> ft.Container:
    """בונה את סרגל הכלים העליון עם כותרת, מקרא וספירת נקודות."""
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Text("GPS Track Viewer", size=18, weight=ft.FontWeight.BOLD),
                ft.VerticalDivider(),
                ft.Icon(ft.Icons.FLIGHT_TAKEOFF, color=ft.Colors.GREEN, size=16),
                ft.Text("המראה"),
                ft.Icon(ft.Icons.CIRCLE, color=ft.Colors.RED_600, size=10),
                ft.Text("מסלול"),
                ft.Icon(ft.Icons.FLIGHT_LAND, color=ft.Colors.BLUE, size=16),
                ft.Text("נחיתה"),
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
    """בונה את שורת הסטטוס התחתונה."""
    return ft.Container(
        content=status_text,
        padding=ft.Padding.symmetric(horizontal=16, vertical=6),
        bgcolor=ft.Colors.SURFACE_CONTAINER,
    )


# ─────────────────────────────────────────────────────────────────────────────
# לוגיקת טעינת נתונים
# ─────────────────────────────────────────────────────────────────────────────

def start_loading(
    page: ft.Page,
    gps_map: fmap.Map,
    marker_layer: fmap.MarkerLayer,
    polyline_layer: fmap.PolylineLayer,
    status_text: ft.Text,
    point_counter: ft.Text,
    loading_ring: ft.ProgressRing,
) -> None:
    """מפעיל טעינת נתונים ב-thread נפרד כדי שה-UI יישאר רספונסיבי."""

    def load():
        try:
            df = get_clean_gps_data(DATA_FILE)

            if df.empty:
                status_text.value = "לא נמצאו נקודות GPS בקובץ"
                return

            coords = [
                fmap.MapLatitudeLongitude(row["Latitude"], row["Longitude"])
                for _, row in df.iterrows()
            ]

            marker_layer.markers = build_markers(coords)
            polyline_layer.polylines = [build_track(coords)]

            # move_to היא async — page.run_task מריץ אותה על ה-event loop של Flet
            async def navigate():
                await gps_map.move_to(destination=coords[0], zoom=TRACK_ZOOM)

            page.run_task(navigate)

            point_counter.value = f"{len(coords)} נקודות"
            status_text.value = "המסלול נטען בהצלחה ✓"

        except FileNotFoundError:
            status_text.value = f"שגיאה: קובץ לא נמצא — {DATA_FILE}"
        except Exception as ex:
            status_text.value = f"שגיאה: {ex}"
        finally:
            loading_ring.visible = False
            page.update()

    threading.Thread(target=load, daemon=True).start()


# ─────────────────────────────────────────────────────────────────────────────
# נקודת הכניסה של Flet
# ─────────────────────────────────────────────────────────────────────────────

def main(page: ft.Page) -> None:
    page.title = "GPS Track Viewer"
    page.window.width = 1000
    page.window.height = 750
    page.padding = 0

    # רכיבי state — אלה ישתנו בזמן הריצה
    status_text = ft.Text("טוען נתוני GPS...", size=13, color=ft.Colors.BLUE_GREY_700)
    point_counter = ft.Text("", weight=ft.FontWeight.BOLD)
    loading_ring = ft.ProgressRing(width=18, height=18, stroke_width=2)

    # שכבות המפה — נוצרות ריקות ומתמלאות אחרי הטעינה
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
        # FLET_APP_WEB: שרת ווב ללא פתיחת דפדפן — מתאים לדוקר
        # host="0.0.0.0" מאפשר גישה מחוץ לקונטיינר
        ft.run(main, view=ft.AppView.FLET_APP_WEB, host="0.0.0.0", port=8080)
    else:
        # לוקאלי: חלון דסקטופ רגיל
        ft.run(main)
