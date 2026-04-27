import logging
import time
import pandas as pd
from .mavlink_reader import MavlinkGpsReader
from .gps_processor import GpsDataProcessor

logger = logging.getLogger(__name__)


def get_clean_gps_data(file_path: str) -> pd.DataFrame:
    """Read a MAVLink .bin log and return a DataFrame with Latitude and Longitude.

    Filters for GPS messages where Instance (I) == 1, downsampled 1-in-10.
    """
    logger.info("Loading GPS data from: %s", file_path)

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
        t1 - t0, t2 - t1, t2 - t0,
    )

    if df.empty:
        logger.warning("No GPS points found in file: %s", file_path)
    else:
        logger.info("GPS data ready: %d points", len(df))

    return df


if __name__ == "__main__":
    import os
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "log_file_test_01.bin"))
    df = get_clean_gps_data(PATH)

    if not df.empty:
        print(f"Success — {len(df)} points retrieved.")
        print(df)
    else:
        print("No data found. Check the file path or GPS Instance (I) values.")
