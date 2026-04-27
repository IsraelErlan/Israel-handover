import pandas as pd
from .mavlink_reader import MavlinkGpsReader
from .gps_processor import GpsDataProcessor


def get_clean_gps_data(file_path: str) -> pd.DataFrame:
    """Read a MAVLink .bin log and return a DataFrame with Latitude and Longitude.

    Filters for GPS messages where Instance (I) == 1 and fix status >= 3.
    """
    reader = MavlinkGpsReader(file_path)
    raw_points = reader.get_raw_gps_data()

    processor = GpsDataProcessor()
    df = processor.to_dataframe(raw_points)
    df = processor.normalize(df)
    df = processor.format_for_display(df)

    return df


if __name__ == "__main__":
    import os
    PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "log_file_test_01.bin"))
    df = get_clean_gps_data(PATH)

    if not df.empty:
        print(f"Success — {len(df)} points retrieved.")
        print(df)
    else:
        print("No data found. Check the file path or GPS Instance (I) values.")
