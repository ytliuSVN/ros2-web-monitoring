"""NavSatFix → JSON 契約 GpsFix。"""

from pydantic import BaseModel
from sensor_msgs.msg import NavSatFix


class GpsFix(BaseModel):
    latitude: float
    longitude: float
    altitude: float
    status: int
    timestamp: float
    frame_id: str
    seq: int

    @classmethod
    def from_nav_sat_fix(cls, msg: NavSatFix, seq: int) -> "GpsFix":
        """timestamp 來自 ROS header.stamp（Unix 秒），不是伺服器時間。

        seq 由呼叫端傳入：ROS 2 Header 已無 seq，Publisher 的計數也不在訊息裡。
        """
        stamp = msg.header.stamp
        timestamp = stamp.sec + stamp.nanosec * 1e-9
        return cls(
            latitude=msg.latitude,
            longitude=msg.longitude,
            altitude=msg.altitude,
            status=int(msg.status.status),
            timestamp=timestamp,
            frame_id=msg.header.frame_id,
            seq=seq,
        )
