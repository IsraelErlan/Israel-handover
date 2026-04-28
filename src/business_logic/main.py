"""Public API for GPS data extraction from MAVLink binary logs."""
import logging
import time

import pandas as pd

from .gps_processor import GpsDataProcessor
from .mavlink_reader import MavlinkGpsReader

logger = logging.getLogger(__name__)


def get_clean_gps_data(file_path: str) -> pd.DataFrame:
    """Read a MAVLink .bin log and return a DataFrame with Latitude and Longitude.

    Filters for GPS messages where Instance (I) == 1, downsampled 1-in-10.
    """
    logger.info("Loading GPS data from: %s", file_path)

    try:
        t0 = time.perf_counter()
        reader = MavlinkGpsReader(file_path)
        raw_points = reader.get_raw_gps_data()
        t1 = time.perf_counter()

        processor = GpsDataProcessor()
        df = processor.to_dataframe(raw_points)
        df = processor.format_for_display(df)
        t2 = time.perf_counter()

        logger.debug(
            "Timing — mavlink read: %.3fs | dataframe build: %.3fs | total: %.3fs",
            t1 - t0,
            t2 - t1,
            t2 - t0,
        )
    except (FileNotFoundError, RuntimeError, ValueError):
        raise
    except Exception as ex:
        logger.exception("Unexpected error while loading GPS data from: %s", file_path)
        raise RuntimeError(f"Failed to load GPS data: {file_path}") from ex

    if df.empty:
        logger.warning("No GPS points found in file: %s", file_path)
    else:
        logger.info("GPS data ready: %d points", len(df))

    return df
