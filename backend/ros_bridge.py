"""訂閱 /gps/fix 的 rclpy 節點，QoS 對齊 Publisher 的 SensorDataQoS。"""

from collections.abc import Callable

from rclpy.node import Node
from rclpy.qos import (
    DurabilityPolicy,
    HistoryPolicy,
    QoSProfile,
    ReliabilityPolicy,
    qos_profile_sensor_data,
)
from sensor_msgs.msg import NavSatFix

GPS_FIX_TOPIC = "/gps/fix"

# rclpy 的 SensorDataQoS 預設 depth 為 5；契約要求 depth 10。
# reliability / durability 仍複製 preset，才能與 rclcpp::SensorDataQoS() 相容。
SENSOR_DATA_QOS = QoSProfile(
    reliability=qos_profile_sensor_data.reliability,
    durability=qos_profile_sensor_data.durability,
    history=qos_profile_sensor_data.history,
    depth=10,
)


class GpsRosBridge(Node):
    def __init__(
        self,
        on_message: Callable[[NavSatFix], None] | None = None,
    ) -> None:
        super().__init__("gps_ros_bridge")
        self._on_message = on_message
        self._last_msg: NavSatFix | None = None
        self._subscription = self.create_subscription(
            NavSatFix,
            GPS_FIX_TOPIC,
            self._on_fix,
            SENSOR_DATA_QOS,
        )
        self.get_logger().info(
            "Subscribed to %s (BEST_EFFORT, depth %d)",
            GPS_FIX_TOPIC,
            SENSOR_DATA_QOS.depth,
        )

    @property
    def last_msg(self) -> NavSatFix | None:
        return self._last_msg

    @property
    def ros_connected(self) -> bool:
        """曾收到至少一筆 /gps/fix；Publisher 未啟動時為 False。"""
        return self._last_msg is not None

    def _on_fix(self, msg: NavSatFix) -> None:
        self._last_msg = msg
        if self._on_message is not None:
            self._on_message(msg)


# 明確標出 QoS 語意，避免日後誤改成 RELIABLE 預設而訂閱不到。
assert SENSOR_DATA_QOS.reliability == ReliabilityPolicy.BEST_EFFORT
assert SENSOR_DATA_QOS.durability == DurabilityPolicy.VOLATILE
assert SENSOR_DATA_QOS.history == HistoryPolicy.KEEP_LAST
assert SENSOR_DATA_QOS.depth == 10
