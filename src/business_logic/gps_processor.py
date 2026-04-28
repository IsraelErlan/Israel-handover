"""GPS data processing utilities for converting raw MAVLink messages to DataFrames."""
import logging
from typing import Any, Dict, List

import pandas as pd

logger = logging.getLogger(__name__)


class GpsDataProcessor:
    """Converts raw GPS message dicts into a display-ready DataFrame."""

    @staticmethod
    def to_dataframe(data_list: List[Dict[str, Any]]) -> pd.DataFrame:
        """Build a DataFrame from a list of GPS point dicts."""
        try:
            df = pd.DataFrame(data_list)
            logger.debug("Built DataFrame with %d rows", len(df))
            return df
        except Exception as ex:
            logger.exception("Failed to build DataFrame from GPS data")
            raise ValueError("Could not convert GPS data to DataFrame") from ex

    @staticmethod
    def format_for_display(df: pd.DataFrame) -> pd.DataFrame:
        """Rename columns to Latitude/Longitude for display."""
        if df.empty:
            return df
        try:
            df.columns = ["Latitude", "Longitude"]
            return df
        except Exception as ex:
            logger.exception("Failed to rename DataFrame columns")
            raise ValueError("Could not format DataFrame for display") from ex
