from typing import Any, Dict, List

import pandas as pd


class GpsDataProcessor:
    @staticmethod
    def to_dataframe(data_list: List[Dict[str, Any]]) -> pd.DataFrame:
        return pd.DataFrame(data_list)

    @staticmethod
    def format_for_display(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        df.columns = ["Latitude", "Longitude"]
        return df
