"""MAVLink binary log reader for extracting GPS data."""
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from pymavlink import mavutil

logger = logging.getLogger(__name__)


class MavlinkGpsReader:
    """Opens a MAVLink .bin log and streams GPS messages."""

    def __init__(self, file_path: str):
        """Store the path; connection is opened lazily on first read."""
        self.file_path: str = file_path
        self.connection: Optional[Any] = None

    def connect(self) -> None:
        """Open the MAVLink connection to the log file."""
        if not Path(self.file_path).exists():
            raise FileNotFoundError(f"Log file not found: {self.file_path}")
        logger.debug("Opening MAVLink connection: %s", self.file_path)
        try:
            self.connection = mavutil.mavlink_connection(self.file_path)
        except Exception as ex:
            logger.exception("Failed to open MAVLink connection: %s", self.file_path)
            raise RuntimeError(f"Could not open MAVLink file: {self.file_path}") from ex

    def _is_valid_gps(self, msg: Any) -> bool:
        if msg is None:
            return False
        return bool(getattr(msg, "I", None) == 1)

    def _message_to_dict(self, msg: Any) -> Optional[Dict[str, Any]]:
        try:
            return {"lat": msg.Lat, "lon": msg.Lng}
        except AttributeError:
            logger.warning("GPS message missing Lat/Lng fields, skipping")
            return None

    def get_raw_gps_data(self, every_nth: int = 10) -> List[Dict[str, Any]]:
        """Return a downsampled list of GPS dicts, keeping one in every *every_nth* messages."""
        if not self.connection:
            self.connect()

        if self.connection is None:
            raise RuntimeError("MAVLink connection is not initialized")

        raw_data: List[Dict[str, Any]] = []
        count = 0
        last_valid = None

        try:
            while True:
                msg = self.connection.recv_match(type=["GPS"], blocking=False)
                if msg is None:
                    break
                if self._is_valid_gps(msg):
                    last_valid = msg
                    if count % every_nth == 0:
                        point = self._message_to_dict(msg)
                        if point is not None:
                            raw_data.append(point)
                    count += 1
        except Exception as ex:
            logger.exception("Error while reading GPS messages")
            raise RuntimeError("Failed to read GPS data from file") from ex

        # Always include the last point so the track ends correctly.
        if last_valid is not None and (count - 1) % every_nth != 0:
            point = self._message_to_dict(last_valid)
            if point is not None:
                raw_data.append(point)

        logger.info(
            "Read %d valid GPS messages, kept %d (every_nth=%d)",
            count,
            len(raw_data),
            every_nth,
        )
        return raw_data
