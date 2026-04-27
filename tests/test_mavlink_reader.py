import pytest
from unittest.mock import MagicMock
from src.business_logic.mavlink_reader import MavlinkGpsReader


def _make_gps_msg(status: int = 3, instance: int = 1, lat: float = 31.5, lon: float = 35.0) -> MagicMock:
    msg = MagicMock()
    msg.get_type.return_value = "GPS"
    msg.Status = status
    msg.I = instance
    msg.Lat = lat
    msg.Lng = lon
    return msg


# ── connect ───────────────────────────────────────────────────────────────────

def test_connect_raises_for_missing_file():
    reader = MavlinkGpsReader("/nonexistent/path/file.bin")
    with pytest.raises(FileNotFoundError, match="Log file not found"):
        reader.connect()


# ── _is_valid_gps ─────────────────────────────────────────────────────────────

def test_is_valid_gps_accepts_good_message():
    reader = MavlinkGpsReader("dummy.bin")
    assert reader._is_valid_gps(_make_gps_msg()) is True


def test_is_valid_gps_rejects_none():
    reader = MavlinkGpsReader("dummy.bin")
    assert reader._is_valid_gps(None) is False


def test_is_valid_gps_rejects_low_fix_status():
    reader = MavlinkGpsReader("dummy.bin")
    assert reader._is_valid_gps(_make_gps_msg(status=2)) is False


def test_is_valid_gps_rejects_secondary_instance():
    reader = MavlinkGpsReader("dummy.bin")
    assert reader._is_valid_gps(_make_gps_msg(instance=2)) is False


def test_is_valid_gps_accepts_minimum_valid_status():
    reader = MavlinkGpsReader("dummy.bin")
    assert reader._is_valid_gps(_make_gps_msg(status=3)) is True


# ── get_raw_gps_data ──────────────────────────────────────────────────────────

def test_get_raw_gps_data_filters_invalid_messages():
    reader = MavlinkGpsReader("dummy.bin")

    good = _make_gps_msg(status=3)
    bad = _make_gps_msg(status=1)

    mock_conn = MagicMock()
    mock_conn.recv_match.side_effect = [good, bad, None]
    reader.connection = mock_conn

    result = reader.get_raw_gps_data()
    assert len(result) == 1
    assert result[0] == {"lat": 31.5, "lon": 35.0}


def test_get_raw_gps_data_returns_empty_on_no_messages():
    reader = MavlinkGpsReader("dummy.bin")

    mock_conn = MagicMock()
    mock_conn.recv_match.return_value = None
    reader.connection = mock_conn

    assert reader.get_raw_gps_data() == []
