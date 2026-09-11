#!/bin/bash
set -euo pipefail

# 官方 image 的 /ros_entrypoint.sh 只 source /opt/ros/humble。
# 這裡再 source workspace overlay，讓 ros2 launch 找得到 gps_publisher。
source /opt/ros/humble/setup.bash
if [[ -f /ros2_ws/install/setup.bash ]]; then
  source /ros2_ws/install/setup.bash
fi

exec "$@"
