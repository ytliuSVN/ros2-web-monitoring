# ROS 2 + Web 實時路徑監控系統

## 任務目標
開發一個端到端的監控系統，將 ROS 2 模擬產生的 GNSS（Global Navigation Satellite Systems）數據，透過後端橋接器即時推送到前端網頁儀表板，並在地圖上繪製路徑。

## 自行產出 GPS 檔案
`path_data.csv`: 包含一系列的 GPS 座標點（Latitude, Longitude）。

```csv
latitude,longitude
22.6273,120.3014
22.6275,120.3018
22.6278,120.3022
22.6282,120.3027
22.6285,120.3031
```

## 詳細需求
### GNSS Publisher (ROS 2)
* 功能： 撰寫一個 ROS 2 C++ Publisher (`gps_publisher_node.cpp`)。
* 讀取： 讀取提供的 GPS 路徑檔案 (`path_data.csv`)。
* 發佈： 以固定頻率 5Hz（`200ms`）循環發佈 `sensor_msgs/msg/NavSatFix` 訊息至 Topic `/gps/fix`。

### Backend Bridge (FastAPI)
* 功能： 建立一個 FastAPI 應用程式 (`main.py`) 作為 ROS 2 與 Web 的橋樑。
* 訂閱： 訂閱 ROS 2 的 `/gps/fix` Topic。
* 轉換： 將接收到的 ROS 2 訊息轉換為 JSON 格式。
* 發佈： 建立 WebSocket 端點，將即時座標數據推送至前端。

### Frontend View (Vue 3)
* 功能： 使用 Vue 3 建立應用頁面。
* 通訊： 連接後端 WebSocket 獲取即時數據。
* 地圖呈現： 整合地圖庫（如 OpenStreetMap）。
* 在圖標上標註當前位置，並繪製出無人載具走過的歷史路徑線段。

### 容器化與部署 (Docker)
* 獨立鏡像： 為 Publisher、 Backend、 Frontend 分別撰寫 Dockerfile。
* 一鍵啟動： 撰寫 `docker-compose.yml`，確保使用者執行 `docker-compose up` 後，系統能自動完成所有網路設定並正常運作。

## 目錄結構

採用 Polyglot Monorepo 的目錄架構，並直接讓 `docker-compose.yml` 擔任整體專案的編排核心。

```
ros2-web-monitoring/
├── ros2_ws/                 # 任務一：GNSS Publisher (ROS 2)
│   ├── src/
│   │   └── gps_publisher/   # 包含 gps_publisher_node.cpp, CMakeLists.txt, package.xml
│   └── Dockerfile
├── backend/                 # 任務二：Backend Bridge (FastAPI)
│   ├── main.py              # FastAPI 應用程式
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                # 任務三：Frontend View (Vue 3)
│   ├── src/
│   ├── package.json
│   └── Dockerfile
├── data/
│   └── path_data.csv        # 自行產出包含 Latitude, Longitude 的 GPS 檔案
├── docker-compose.yml       # 任務四：容器化與部署，確保執行 docker-compose up 自動完成網路設定
└── README.md                # 說明整體架構與一鍵啟動指令
```



