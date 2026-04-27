# gps_processor.py
import pandas as pd
from typing import List, Dict, Any

class GpsDataProcessor:
    @staticmethod
    def to_dataframe(data_list: List[Dict[str, Any]]) -> pd.DataFrame:
        return pd.DataFrame(data_list)

    @staticmethod
    def normalize(df: pd.DataFrame) -> pd.DataFrame:
        """Scales Lat/Lon from integer to decimal degrees."""
        if df.empty:
            return df
        
        processed_df = df.copy()
        processed_df['lat'] = processed_df['lat'] / 1.0e7
        processed_df['lon'] = processed_df['lon'] / 1.0e7
        return processed_df

    @staticmethod
    def format_for_display(df: pd.DataFrame) -> pd.DataFrame:
        """Simple formatting for the final output."""
        if df.empty:
            return df
        
        display_df = df.copy()
        display_df.columns = ['Latitude', 'Longitude']
        return display_df