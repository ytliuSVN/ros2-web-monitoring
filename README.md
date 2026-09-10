# ROS 2 + Web 實時路徑監控系統

將 ROS 2 模擬產生的 GNSS 數據，經由 FastAPI 橋接器即時推送至 Vue 3 儀表板，並在地圖上繪製無人載具的即時位置與歷史路徑。

本文件為跨子專案的介面契約。Topic 名稱、QoS、WebSocket 路徑、JSON 欄位與環境變數名稱一經鎖定，後續 Phase 不再更名。

---

## 架構

```
CSV ──5 Hz──► Publisher ──/gps/fix──► Backend ──/ws/gps──► Frontend
path_data.csv   rclcpp NavSatFix        FastAPI JSON         Vue 3 + Leaflet
```

| 層級 | 技術 | 責任 |
| :--- | :--- | :--- |
| Publisher | ROS 2 Humble + C++ (`rclcpp`) | 讀 CSV，以 5 Hz 循環發佈 `NavSatFix` |
| Backend | Python 3.10 + FastAPI + `rclpy` | 訂閱 Topic，轉 JSON，經 WebSocket 廣播 |
| Frontend | Vue 3 + Vite + Leaflet | 連線、繪製 Marker 與歷史路徑 |
| 部署 | Docker Compose | 三個獨立鏡像，共用 bridge network |

一鍵啟動（Phase 4 完成後生效）：

```bash
cp .env.example .env
docker compose up --build
```

瀏覽器開啟 `http://localhost:8080`。本機前端開發則為 `http://localhost:5173`。

---

## 介面契約

| 介面 | 位址 / 名稱 | 格式 |
| :--- | :--- | :--- |
| ROS 2 Topic | `/gps/fix` | `sensor_msgs/msg/NavSatFix` |
| QoS（兩端必須一致） | — | `SensorDataQoS`：BEST_EFFORT、depth 10 |
| WebSocket | `ws://localhost:8000/ws/gps` | JSON，每筆一則座標 |
| Health Check | `GET http://localhost:8000/health` | 見下方 |
| Frontend | `:5173`（Vite dev）/ `:8080`（Nginx） | SPA |

DDS：publisher 與 backend 共用 `ROS_DOMAIN_ID`，並使用 `RMW_IMPLEMENTATION=rmw_cyclonedds_cpp`。

### WebSocket 推播（`GpsFix`）

頻率與 Publisher 相同（預設 5 Hz）。欄位名稱、型別不可更改。

```json
{
  "latitude": 22.6273,
  "longitude": 120.3014,
  "altitude": 0.0,
  "status": 0,
  "timestamp": 1757423401.234,
  "frame_id": "gps_link",
  "seq": 42
}
```

| 欄位 | 型別 | 來源 | 說明 |
| :--- | :--- | :--- | :--- |
| `latitude` | `number` | `NavSatFix.latitude` | 緯度，十進位度 |
| `longitude` | `number` | `NavSatFix.longitude` | 經度，十進位度 |
| `altitude` | `number` | `NavSatFix.altitude` | 海拔，公尺；CSV 無此欄時填 `0.0` |
| `status` | `integer` | `NavSatFix.status.status` | `sensor_msgs/NavSatStatus`：`-1` NO_FIX、`0` FIX |
| `timestamp` | `number` | `header.stamp` | ROS 時間，秒（含小數）；**不是**伺服器牆鐘 |
| `frame_id` | `string` | `header.frame_id` | 預設 `"gps_link"` |
| `seq` | `integer` | Publisher 自增計數 | ROS 2 `Header` 無 `seq`，由節點從 0 遞增，循環重播不重置 |

新 WebSocket 連線會立即收到 ring buffer 中最近最多 500 筆歷史點，其後改收即時推播。

### Health Check

```json
{
  "status": "ok",
  "ros_connected": true,
  "last_message_time": 1757423401.234
}
```

| 欄位 | 型別 | 說明 |
| :--- | :--- | :--- |
| `status` | `string` | HTTP 服務存活即為 `"ok"` |
| `ros_connected` | `boolean` | 曾收到 `/gps/fix` 且訂閱仍有效時為 `true`；Publisher 未啟動時為 `false` |
| `last_message_time` | `number \| null` | 最近一筆 ROS `header.stamp`（秒）；尚無訊息時為 `null` |

Publisher 未啟動時：`GET /health` 仍回 200，`ros_connected` 為 `false`；`/ws/gps` 可連線、不丟例外。

---

## 環境變數

完整預設值見 [`.env.example`](.env.example)。複製為 `.env` 後覆寫。名稱不可更改。

| 變數 | 預設值 | 誰讀取 |
| :--- | :--- | :--- |
| `ROS_DOMAIN_ID` | `0` | publisher、backend |
| `RMW_IMPLEMENTATION` | `rmw_cyclonedds_cpp` | publisher、backend |
| `GPS_CSV_PATH` | `/data/path_data.csv` | publisher（容器內路徑；compose 掛載 `./data:/data:ro`） |
| `PUBLISH_RATE_HZ` | `5` | publisher |
| `BACKEND_PORT` | `8000` | backend、frontend（WS 目標） |
| `FRONTEND_PORT` | `8080` | frontend（Nginx） |
| `VITE_WS_URL` | `ws://localhost:8000/ws/gps` | frontend（Vite 建置時寫入） |

---

## 路徑資料

[`data/path_data.csv`](data/path_data.csv)：高雄市區封閉環路，91 點，相鄰約 50 m。Publisher 索引到底後回到第一筆，接縫與一般點距相同。

```csv
latitude,longitude
22.627300,120.301400
```

- 首行必須為 `latitude,longitude`（無空白）
- 其餘每行兩個十進位度，小數 6 位
- 不含 `altitude`；Publisher 填 `0.0`

---

## 目錄結構

```
ros2-web-monitoring/
├── ros2_ws/                          # GNSS Publisher (ROS 2 C++)
│   ├── src/gps_publisher/
│   │   ├── src/gps_publisher_node.cpp
│   │   ├── include/gps_publisher/csv_reader.hpp
│   │   ├── launch/gps_publisher.launch.py
│   │   ├── config/params.yaml
│   │   ├── CMakeLists.txt
│   │   └── package.xml
│   └── Dockerfile
├── backend/                          # FastAPI 橋接器
│   ├── main.py
│   ├── ros_bridge.py
│   ├── ws_manager.py
│   ├── schemas.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                         # Vue 3 儀表板
│   ├── src/
│   ├── nginx.conf
│   └── Dockerfile
├── data/path_data.csv
├── docker-compose.yml
├── .env.example
├── PLAN.md
└── README.md
```
