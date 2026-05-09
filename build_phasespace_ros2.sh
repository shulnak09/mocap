#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

set +u
source /opt/ros/humble/setup.bash
set -u

# Keep ROS 2 builds on the system Python even if Conda is active.
export PATH="/usr/bin:/bin:/usr/sbin:/sbin:/opt/ros/humble/bin"
export PYTHONPATH="/opt/ros/humble/lib/python3.10/site-packages:/opt/ros/humble/local/lib/python3.10/dist-packages"

cd "${ROOT_DIR}"
colcon build --base-paths phasespace-mocap-ros2 --cmake-clean-cache --cmake-args -DPython3_EXECUTABLE=/usr/bin/python3 "$@"
