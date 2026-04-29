"""MAVLink binary log reader for extracting GPS data."""

from pathlib import Path
from typing import Any, Dict, List, Optional

from pymavlink import mavutil

from utils.logger import get_logger

logger = get_logger(__name__)


class MavlinkReader:
    """Opens a MAVLink .bin log and streams GPS messages."""

    def __init__(self, file_path: str):
        """Store the path; connection is opened lazily on first read."""
        self.file_path: str = file_path
        self.connection: Optional[Any] = None

    def connect(self) -> None:
        """Open the MAVLink connection to the log file."""
        try:
            self.connection = mavutil.mavlink_connection(self.file_path)
            logger.debug("Opening MAVLink connection: %s", self.file_path)
        
        except FileNotFoundError:
            logger.error("Log file not found: %s", self.file_path)
        except Exception:
            logger.exception("Failed to open MAVLink connection: %s", self.file_path)
            raise

    def get_raw_gps_data(self, every_nth: int = 10) -> List[Dict[str, Any]]:
        """Return a downsampled list of GPS dicts, keeping one in every *every_nth* messages."""
        if every_nth < 1:
            raise ValueError(f"every_nth must be at least 1, got {every_nth}")
        raw_data: List[Dict[str, Any]] = []
        count = 0
        last_valid = None

        try:
            if not self.connection:
                self.connect()

            while True:
                gps_msg = self.connection.recv_match(type=["GPS"], blocking=False)
                if gps_msg is None:
                    break
                if getattr(gps_msg, "I", None) == 1:
                    last_valid = gps_msg
                    if count % every_nth == 0:
                        raw_data.append({"lat": gps_msg.Lat, "lon": gps_msg.Lng})
                    count += 1
            # Always include the last point so the track ends correctly.
            if last_valid is not None and (count - 1) % every_nth != 0:
                raw_data.append({"lat": last_valid.Lat, "lon": last_valid.Lng})

            logger.info(
                "Read %d valid GPS messages, kept %d (every_nth=%d)",
                count,
                len(raw_data),
                every_nth,
            )
            return raw_data        
        
        except Exception:
            logger.exception("Error while reading GPS data from: %s", self.file_path)
            raise
        finally:
            if self.connection is not None:
                self.connection.close()
                self.connection = None
                logger.debug("MAVLink connection closed: %s", self.file_path)


