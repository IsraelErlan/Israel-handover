# main.py
import pandas as pd
from typing import List, Dict, Any
from mavlink_reader import MavlinkGpsReader
from gps_processor import GpsDataProcessor

def get_clean_gps_data(file_path: str) -> pd.DataFrame:
    """
    This is the main function your Frontend will call.
    It returns a DataFrame with only Latitude and Longitude 
    where GPS Instance (I) == 1.
    """
    # 1. Initialize the Reader and extract data
    # (The Reader now filters for I=1 internally as we defined)
    reader = MavlinkGpsReader(file_path)
    raw_points = reader.get_raw_gps_data()
    
    # 2. Convert to DataFrame
    processor = GpsDataProcessor()
    df_raw = processor.to_dataframe(raw_points)
    
    # 3. Normalize (Scale the integers to decimal degrees)
    df_normalized = processor.normalize(df_raw)
    
    # 4. Format columns (Renaming to 'Latitude', 'Longitude')
    df_final = processor.format_for_display(df_normalized)
    
    return df_final

if __name__ == "__main__":
    # Internal test to make sure everything works
    PATH = r'C:\Users\adika\OneDrive\Desktop\israel_handover\data\log_file_test_01.bin'
    
    print("Running internal test...")
    test_df = get_clean_gps_data(PATH)
    
    if not test_df.empty:
        print(f"Success! Retrieved {len(test_df)} points.")
        # test_df = test_df.to_dict()
        print(test_df)
    else:
        print("No data found. Check the file path or GPS Instance (I) values.")