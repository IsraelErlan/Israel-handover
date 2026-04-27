# mavlink_reader.py
from pymavlink import mavutil
from typing import List, Dict, Optional, Any

class MavlinkGpsReader:
    def __init__(self, file_path: str):
        self.file_path: str = file_path
        self.connection: Optional[Any] = None

    def connect(self) -> None:
        self.connection = mavutil.mavlink_connection(self.file_path)

    def _is_valid_gps(self, msg: Any) -> bool:
        """Checks for GPS type, fix status, and specifically Instance (I) == 1."""
        if msg is None:
            return False
            
        # We check if the message is 'GPS' and if the Instance field 'I' equals 1
        is_gps = msg.get_type() == 'GPS'
        has_fix = getattr(msg, 'Status', 0) >= 3
        is_instance_one = getattr(msg, 'I', None) == 1
        
        return bool(is_gps and has_fix and is_instance_one)

    def _message_to_dict(self, msg: Any) -> Dict[str, Any]:
        """Returns only Latitude and Longitude."""
        return {
            'lat': int(msg.Lat),
            'lon': int(msg.Lng)
        }

    def get_raw_gps_data(self) -> List[Dict[str, Any]]:
        if not self.connection:
            self.connect()
            
        raw_data: List[Dict[str, Any]] = []
        while True:
            msg = self.connection.recv_match(type=['GPS'], blocking=False)
            if msg is None:
                break
            if self._is_valid_gps(msg):
                raw_data.append(self._message_to_dict(msg))
        return raw_data