import pytest
from unittest.mock import patch
from src.business_logic.main import get_clean_gps_data


def test_raises_for_missing_file():
    with pytest.raises(FileNotFoundError):
        get_clean_gps_data("/nonexistent/file.bin")


def test_returns_empty_dataframe_when_no_gps_points(tmp_path):
    fake_bin = tmp_path / "empty.bin"
    fake_bin.write_bytes(b"")

    with patch("src.business_logic.mavlink_reader.MavlinkGpsReader.connect"), \
         patch("src.business_logic.mavlink_reader.MavlinkGpsReader.get_raw_gps_data", return_value=[]):
        result = get_clean_gps_data(str(fake_bin))

    assert result.empty


def test_returns_correct_columns_and_values(tmp_path):
    fake_bin = tmp_path / "test.bin"
    fake_bin.write_bytes(b"")

    fake_points = [
        {"lat": 31.5, "lon": 35.0},
        {"lat": 31.6, "lon": 35.1},
    ]

    with patch("src.business_logic.mavlink_reader.MavlinkGpsReader.connect"), \
         patch("src.business_logic.mavlink_reader.MavlinkGpsReader.get_raw_gps_data", return_value=fake_points):
        result = get_clean_gps_data(str(fake_bin))

    assert list(result.columns) == ["Latitude", "Longitude"]
    assert len(result) == 2
    assert result["Latitude"].iloc[0] == pytest.approx(31.5)
    assert result["Longitude"].iloc[1] == pytest.approx(35.1)
