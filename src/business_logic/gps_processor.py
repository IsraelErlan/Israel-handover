import pandas as pd
from typing import List, Dict, Any


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
