import pytest
from unittest.mock import MagicMock
from src.business_logic.mavlink_reader import MavlinkReader


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
    reader = MavlinkReader("/nonexistent/path/file.bin")
    with pytest.raises(FileNotFoundError, match="Log file not found"):
        reader.connect()


# ── get_raw_gps_data ──────────────────────────────────────────────────────────

def test_get_raw_gps_data_every_nth_sampling():
    reader = MavlinkReader("dummy.bin")

    msg1 = _make_gps_msg(lat=31.5, lon=35.0)
    msg2 = _make_gps_msg(lat=31.6, lon=35.1)

    mock_conn = MagicMock()
    mock_conn.recv_match.side_effect = [msg1, msg2, None]
    reader.connection = mock_conn

    # every_nth=10: only msg1 (count=0) is sampled; msg2 (count=1) is skipped
    # but msg2 is appended as last_valid since it wasn't already included
    result = reader.get_raw_gps_data(every_nth=10)
    assert len(result) == 2
    assert result[0] == {"lat": 31.5, "lon": 35.0}
    assert result[1] == {"lat": 31.6, "lon": 35.1}


def test_get_raw_gps_data_returns_empty_on_no_messages():
    reader = MavlinkReader("dummy.bin")

    mock_conn = MagicMock()
    mock_conn.recv_match.return_value = None
    reader.connection = mock_conn

    assert reader.get_raw_gps_data() == []
