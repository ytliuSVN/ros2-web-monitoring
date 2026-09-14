"""FastAPI 入口：WebSocket `/ws/gps`、`GET /health`、lifespan 管理 rclpy。"""

import asyncio
import logging
from contextlib import asynccontextmanager, suppress

import rclpy
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from rclpy.signals import SignalHandlerOptions

from ros_bridge import GpsRosBridge
from schemas import GpsFix, HealthResponse, stamp_to_unix
from ws_manager import ConnectionManager

logger = logging.getLogger("gps_backend")

# 契約前端：Vite :5173、Nginx :8080。
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)
    manager = ConnectionManager()
    bridge = GpsRosBridge(asyncio.get_running_loop())
    seq = 0

    async def pump() -> None:
        nonlocal seq
        while True:
            msg = await bridge.queue.get()
            fix = GpsFix.from_nav_sat_fix(msg, seq)
            seq += 1
            await manager.broadcast(fix)

    app.state.manager = manager
    app.state.bridge = bridge
    bridge.start()
    pump_task = asyncio.create_task(pump(), name="gps-fix-pump")
    logger.info("Backend bridge started")
    try:
        yield
    finally:
        pump_task.cancel()
        with suppress(asyncio.CancelledError):
            await pump_task
        bridge.stop()
        with suppress(Exception):
            bridge.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
        logger.info("Backend bridge stopped")


app = FastAPI(title="gps-backend", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health(request: Request) -> HealthResponse:
    bridge: GpsRosBridge | None = getattr(request.app.state, "bridge", None)
    ros_connected = False
    last_message_time: float | None = None
    if bridge is not None:
        ros_connected = bridge.ros_connected
        last = bridge.last_msg
        if last is not None:
            last_message_time = stamp_to_unix(last.header.stamp)
    return HealthResponse(
        status="ok",
        ros_connected=ros_connected,
        last_message_time=last_message_time,
    )


@app.websocket("/ws/gps")
async def ws_gps(websocket: WebSocket) -> None:
    manager: ConnectionManager = websocket.app.state.manager
    await manager.connect(websocket)
    try:
        while True:
            message = await websocket.receive()
            if message["type"] == "websocket.disconnect":
                break
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)
