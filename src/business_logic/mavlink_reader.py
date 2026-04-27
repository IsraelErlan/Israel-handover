import logging
from pathlib import Path
from pymavlink import mavutil
from typing import List, Dict, Optional, Any

logger = logging.getLogger(__name__)


class MavlinkGpsReader:
    def __init__(self, file_path: str):
        self.file_path: str = file_path
        self.connection: Optional[Any] = None

    def connect(self) -> None:
        if not Path(self.file_path).exists():
            raise FileNotFoundError(f"Log file not found: {self.file_path}")
        logger.debug("Opening MAVLink connection: %s", self.file_path)
        self.connection = mavutil.mavlink_connection(self.file_path)

    def _is_valid_gps(self, msg: Any) -> bool:
        if msg is None:
            return False
        return bool(
            getattr(msg, "I", None) == 1
        )

    def _message_to_dict(self, msg: Any) -> Dict[str, Any]:
        return {"lat": msg.Lat, "lon": msg.Lng}

    def get_raw_gps_data(self, every_nth: int = 10) -> List[Dict[str, Any]]:
        if not self.connection:
            self.connect()

        raw_data: List[Dict[str, Any]] = []
        count = 0
        last_valid = None
        while True:
            msg = self.connection.recv_match(type=["GPS"], blocking=False)
            if msg is None:
                break
            if self._is_valid_gps(msg):
                last_valid = msg
                if count % every_nth == 0:
                    raw_data.append(self._message_to_dict(msg))
                count += 1

        # Always include the last point so the track ends correctly.
        if last_valid is not None and (count - 1) % every_nth != 0:
            raw_data.append(self._message_to_dict(last_valid))

        logger.info(
            "Read %d valid GPS messages, kept %d (every_nth=%d)",
            count, len(raw_data), every_nth,
        )
        return raw_data
