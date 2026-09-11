#!/bin/bash
set -euo pipefail

# 官方 image 的 /ros_entrypoint.sh 只 source /opt/ros/humble。
# 這裡再 source workspace overlay，讓 ros2 launch 找得到 gps_publisher。
# setup.bash 會讀取未設定變數，source 期間必須關掉 nounset。
set +u
source /opt/ros/humble/setup.bash
if [[ -f /ros2_ws/install/setup.bash ]]; then
  source /ros2_ws/install/setup.bash
fi
set -u

exec "$@"
