import os

import flet_map as fmap

IS_DOCKER = os.getenv("FLET_ENV") == "docker"

INITIAL_CENTER = fmap.MapLatitudeLongitude(31.5, 35.0)
INITIAL_ZOOM = 8.0
TRACK_ZOOM = 13.0
TILE_URL = "https://basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png"
