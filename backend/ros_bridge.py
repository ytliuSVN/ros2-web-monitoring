"""訂閱 /gps/fix 的 rclpy 節點，QoS 對齊 Publisher 的 SensorDataQoS。"""

import asyncio
import threading
from concurrent.futures import Future

from rclpy.executors import SingleThreadedExecutor
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
        loop: asyncio.AbstractEventLoop,
        queue: asyncio.Queue[NavSatFix] | None = None,
    ) -> None:
        super().__init__("gps_ros_bridge")
        self._loop = loop
        self._queue: asyncio.Queue[NavSatFix] = (
            queue if queue is not None else asyncio.Queue()
        )
        self._last_msg: NavSatFix | None = None
        self._spin_thread: threading.Thread | None = None
        self._spin_executor: SingleThreadedExecutor | None = None
        self._subscription = self.create_subscription(
            NavSatFix,
            GPS_FIX_TOPIC,
            self._on_fix,
            SENSOR_DATA_QOS,
        )
        self.get_logger().info(
            f"Subscribed to {GPS_FIX_TOPIC} (BEST_EFFORT, depth {SENSOR_DATA_QOS.depth})"
        )

    @property
    def queue(self) -> asyncio.Queue[NavSatFix]:
        return self._queue

    @property
    def last_msg(self) -> NavSatFix | None:
        return self._last_msg

    @property
    def ros_connected(self) -> bool:
        """曾收到至少一筆 /gps/fix；Publisher 未啟動時為 False。"""
        return self._last_msg is not None

    def start(self) -> None:
        """在獨立 thread 執行 spin，避免阻塞 FastAPI event loop。"""
        if self._spin_thread is not None and self._spin_thread.is_alive():
            return
        self._spin_executor = SingleThreadedExecutor()
        self._spin_executor.add_node(self)
        self._spin_thread = threading.Thread(
            target=self._spin,
            name="rclpy-spin",
            daemon=True,
        )
        self._spin_thread.start()
        self.get_logger().info("rclpy spin thread started")

    def stop(self) -> None:
        """停止 spin thread。不呼叫 rclpy.shutdown()（由 FastAPI lifespan 負責）。"""
        if self._spin_executor is not None:
            self._spin_executor.shutdown()
            self._spin_executor = None
        if self._spin_thread is not None:
            self._spin_thread.join(timeout=5.0)
            if self._spin_thread.is_alive():
                self.get_logger().warning("rclpy spin thread did not stop within 5s")
            self._spin_thread = None

    def _spin(self) -> None:
        # Humble 的 rclpy.spin() 只看 context.ok()，必須 rclpy.shutdown() 才會返回，
        # 會與 FastAPI lifespan 搶關機。Executor.spin() 同樣在獨立 thread 阻塞處理
        # callback，但 stop() 可只關 executor。
        assert self._spin_executor is not None
        self._spin_executor.spin()

    def _on_fix(self, msg: NavSatFix) -> None:
        self._last_msg = msg
        try:
            future = asyncio.run_coroutine_threadsafe(self._queue.put(msg), self._loop)
        except RuntimeError as exc:
            self.get_logger().warning(
                f"Event loop closed; dropping GPS fix: {exc}"
            )
            return
        future.add_done_callback(self._on_enqueue_done)

    def _on_enqueue_done(self, future: Future[None]) -> None:
        if future.cancelled():
            return
        exc = future.exception()
        if exc is not None:
            self.get_logger().error(f"Failed to enqueue /gps/fix: {exc}")


# 明確標出 QoS 語意，避免日後誤改成 RELIABLE 預設而訂閱不到。
assert SENSOR_DATA_QOS.reliability == ReliabilityPolicy.BEST_EFFORT
assert SENSOR_DATA_QOS.durability == DurabilityPolicy.VOLATILE
assert SENSOR_DATA_QOS.history == HistoryPolicy.KEEP_LAST
assert SENSOR_DATA_QOS.depth == 10
