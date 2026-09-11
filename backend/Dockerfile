# Backend 鏡像：FastAPI 與 rclpy 共存於 Humble 容器。
# 本機不裝 Humble；Apple Silicon 優先走 image 的 linux/arm64。
FROM ros:humble-ros-base

ENV ROS_DOMAIN_ID=0 \
    RMW_IMPLEMENTATION=rmw_cyclonedds_cpp \
    PYTHONUNBUFFERED=1

# python3-pip 未預裝；Cyclone DDS 避開 Fast DDS 跨容器 SHM。
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        python3-pip \
        ros-humble-rmw-cyclonedds-cpp \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# 沿用官方 /ros_entrypoint.sh，source Humble 後 rclpy 才可用。
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
