import pandas as pd
import pytest
from src.business_logic.gps_processor import GpsDataProcessor


def test_to_dataframe_empty_list():
    result = GpsDataProcessor.to_dataframe([])
    assert result.empty


def test_to_dataframe_preserves_data():
    data = [{"lat": 31.5, "lon": 35.0}, {"lat": 31.6, "lon": 35.1}]
    result = GpsDataProcessor.to_dataframe(data)
    assert len(result) == 2
    assert list(result.columns) == ["lat", "lon"]
    assert result["lat"].iloc[0] == pytest.approx(31.5)


def test_format_for_display_empty_dataframe():
    result = GpsDataProcessor.format_for_display(pd.DataFrame())
    assert result.empty


def test_format_for_display_renames_columns():
    df = pd.DataFrame([{"lat": 31.5, "lon": 35.0}, {"lat": 31.6, "lon": 35.1}])
    result = GpsDataProcessor.format_for_display(df)
    assert list(result.columns) == ["Latitude", "Longitude"]
    assert result["Latitude"].iloc[0] == pytest.approx(31.5)
    assert result["Longitude"].iloc[0] == pytest.approx(35.0)


def test_format_for_display_mutates_original():
    df = pd.DataFrame([{"lat": 31.5, "lon": 35.0}])
    GpsDataProcessor.format_for_display(df)
    assert list(df.columns) == ["Latitude", "Longitude"]
