"""Public API for GPS data extraction from MAVLink binary logs."""
import time

import pandas as pd

from .gps_processor import GpsProcessor
from .mavlink_reader import MavlinkReader
from utils.logger import get_logger

logger = get_logger(__name__)


def get_clean_gps_data(file_path: str) -> pd.DataFrame:
    """Read a MAVLink .bin log and return a DataFrame with Latitude and Longitude.

    Filters for GPS messages where Instance (I) == 1, downsampled 1-in-10.
    """
    logger.info("Loading GPS data from: %s", file_path)

    start_time = time.perf_counter()
    reader = MavlinkReader(file_path)
    raw_points = reader.get_raw_gps_data()
    after_read_time = time.perf_counter()

    processor = GpsProcessor()
    df = processor.to_dataframe(raw_points)
    df = processor.format_for_display(df)
    after_process_time = time.perf_counter()

    logger.debug(
        "Timing — mavlink read: %.3fs | dataframe build: %.3fs | total: %.3fs",
        after_read_time - start_time,
        after_process_time - after_read_time,
        after_process_time - start_time,
    )

    if df.empty:
        logger.warning("No GPS points found in file: %s", file_path)
    else:
        logger.info("GPS data ready: %d points", len(df))

    return df
