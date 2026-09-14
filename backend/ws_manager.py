"""WebSocket 連線管理與廣播。"""

import logging

from fastapi import WebSocket

from schemas import GpsFix

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        try:
            self._connections.remove(websocket)
        except ValueError:
            return

    async def broadcast(self, payload: GpsFix) -> None:
        if not self._connections:
            return
        data = payload.model_dump()
        stale: list[WebSocket] = []
        for websocket in self._connections:
            try:
                await websocket.send_json(data)
            except Exception as exc:
                logger.info("Dropping disconnected WebSocket client: %s", exc)
                stale.append(websocket)
        for websocket in stale:
            self.disconnect(websocket)
