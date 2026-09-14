"""WebSocket 連線管理、廣播與歷史軌跡回填。"""

import logging
from collections import deque

from fastapi import WebSocket

from schemas import GpsFix

logger = logging.getLogger(__name__)

HISTORY_SIZE = 500


class ConnectionManager:
    def __init__(self, history_size: int = HISTORY_SIZE) -> None:
        self._connections: list[WebSocket] = []
        self._history: deque[dict] = deque(maxlen=history_size)

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        await self._replay_history(websocket)
        self._connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        try:
            self._connections.remove(websocket)
        except ValueError:
            return

    async def broadcast(self, payload: GpsFix) -> None:
        data = payload.model_dump()
        self._history.append(data)
        if not self._connections:
            return
        stale: list[WebSocket] = []
        for websocket in self._connections:
            try:
                await websocket.send_json(data)
            except Exception as exc:
                logger.info("Dropping disconnected WebSocket client: %s", exc)
                stale.append(websocket)
        for websocket in stale:
            self.disconnect(websocket)

    async def _replay_history(self, websocket: WebSocket) -> None:
        """補送最近的歷史點，讓新連線不必等下一筆才有軌跡。

        補送期間仍可能有新點進來；以 seq 追上進度後才註冊為即時連線，
        避免該客戶端漏點或收到重複、亂序的點。
        """
        last_seq = -1
        while True:
            pending = [data for data in self._history if data["seq"] > last_seq]
            if not pending:
                return
            for data in pending:
                await websocket.send_json(data)
            last_seq = pending[-1]["seq"]
