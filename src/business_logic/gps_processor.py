"""GPS data processing utilities for converting raw MAVLink messages to DataFrames."""
from typing import Any, Dict, List

import pandas as pd

from utils.logger import get_logger

logger = get_logger(__name__)


class GpsProcessor:
    """Converts raw GPS message dicts into a display-ready DataFrame."""

    @staticmethod
    def to_dataframe(data_list: List[Dict[str, Any]]) -> pd.DataFrame:
        """Build a DataFrame from a list of GPS point dicts."""
        df = pd.DataFrame(data_list)
        logger.debug("Built DataFrame with %d rows", len(df))
        return df

    @staticmethod
    def format_for_display(df: pd.DataFrame) -> pd.DataFrame:
        """Rename columns to Latitude/Longitude for display."""
        if df.empty:
            return df
        df.columns = ["Latitude", "Longitude"]
        return df
