from pathlib import Path
from pymavlink import mavutil
from typing import List, Dict, Optional, Any


class MavlinkGpsReader:
    def __init__(self, file_path: str):
        self.file_path: str = file_path
        self.connection: Optional[Any] = None

    def connect(self) -> None:
        if not Path(self.file_path).exists():
            raise FileNotFoundError(f"Log file not found: {self.file_path}")
        self.connection = mavutil.mavlink_connection(self.file_path)

    def _is_valid_gps(self, msg: Any) -> bool:
        """Return True only for GPS messages with a 3D fix on Instance 1."""
        if msg is None:
            return False
        return bool(
            msg.get_type() == "GPS"
            and getattr(msg, "Status", 0) >= 3
            and getattr(msg, "I", None) == 1
        )

    def _message_to_dict(self, msg: Any) -> Dict[str, Any]:
        return {"lat": msg.Lat, "lon": msg.Lng}

    def get_raw_gps_data(self) -> List[Dict[str, Any]]:
        if not self.connection:
            self.connect()

        raw_data: List[Dict[str, Any]] = []
        while True:
            msg = self.connection.recv_match(type=["GPS"], blocking=False)
            if msg is None:
                break
            if self._is_valid_gps(msg):
                raw_data.append(self._message_to_dict(msg))
        return raw_data
