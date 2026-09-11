# Publisher 鏡像：ROS 2 Humble 只存在於此容器內。
# 本機不裝 Humble；Apple Silicon 優先走 image 的 linux/arm64。
FROM ros:humble-ros-base

ENV ROS_DOMAIN_ID=0 \
    RMW_IMPLEMENTATION=rmw_cyclonedds_cpp \
    GPS_CSV_PATH=/data/path_data.csv \
    PUBLISH_RATE_HZ=5

# ros:humble-ros-base 不含編譯工具；Cyclone DDS 避開 Fast DDS 跨容器 SHM。
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        build-essential \
        python3-colcon-common-extensions \
        ros-humble-rmw-cyclonedds-cpp \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /ros2_ws

COPY src ./src

# Phase 2 補齊 gps_publisher 原始碼後才會真正編譯套件；空 workspace 仍會產出 overlay。
RUN . /opt/ros/humble/setup.sh && colcon build

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["ros2", "launch", "gps_publisher", "gps_publisher.launch.py"]
