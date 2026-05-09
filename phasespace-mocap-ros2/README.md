# ROS 2 Phasespace Port

This directory contains an initial ROS 2 Humble port of the Phasespace ROS 1
driver in this repository.

Packages:

- `phasespace_msgs_ros2`: ROS 2 message definitions for markers, rigids, and cameras.
- `phasespace_bringup_ros2`: ROS 2 C++ node that connects directly to the
  Phasespace OWL server and publishes `/phasespace/errors`,
  `/phasespace/cameras`, `/phasespace/markers`, and `/phasespace/rigids`.

Build:

```bash
source /opt/ros/humble/setup.bash
colcon build --base-paths phasespace-mocap-ros2
```

If `conda` is active and `rosidl` generation fails, either run `conda deactivate`
first or force the ROS 2 build to use the system Python:

```bash
source /opt/ros/humble/setup.bash
env PATH=/usr/bin:/bin:/usr/sbin:/sbin:/opt/ros/humble/bin \
    PYTHONPATH=/opt/ros/humble/lib/python3.10/site-packages:/opt/ros/humble/local/lib/python3.10/dist-packages \
    colcon build --base-paths phasespace-mocap-ros2 --cmake-clean-cache \
    --cmake-args -DPython3_EXECUTABLE=/usr/bin/python3
```

There is also a wrapper script in the workspace root that does the same thing:

```bash
./build_phasespace_ros2.sh
```

Run the driver:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch phasespace_bringup_ros2 phasespace_mocap.launch.py server_ip:=192.168.0.101
```

Read rigid data from Python:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run phasespace_bringup_ros2 read_rigids.py
```

Plot filtered and smoothed `x(t)`, `y(t)`, and `z(t)` for up to 8 marker IDs for 20 seconds:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run phasespace_bringup_ros2 plot_xy_data.py --topic /phasespace/markers --duration 20 --max-ids 8
```

To try the same on rigid bodies instead:

```bash
ros2 run phasespace_bringup_ros2 plot_xy_data.py --topic /phasespace/rigids --duration 20 --max-ids 8
```

Useful filtering knobs:

```bash
ros2 run phasespace_bringup_ros2 plot_xy_data.py \
  --topic /phasespace/markers \
  --duration 20 \
  --max-ids 8 \
  --min-cond 0.0 \
  --median-window 5 \
  --smooth-window 9
```

Live plotting from the marker topic with a rolling 20-second window:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run phasespace_bringup_ros2 live_plot_xyz.py --topic /phasespace/markers --history 20 --max-ids 8
```

Live spatial plotting in a single `x-y-z` view:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run phasespace_bringup_ros2 live_spatial_plot.py --topic /phasespace/markers
```

By default, the spatial plotter keeps the full path from `t=0` and fuses the
first 4 valid marker IDs it sees into one centroid-based Kalman estimate. To
lock the fusion to known marker IDs:

```bash
ros2 run phasespace_bringup_ros2 live_spatial_plot.py \
  --topic /phasespace/markers \
  --combine-ids 0,2,4,6 \
  --combine-count 4
```

Split raw markers into two device-specific topics:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run phasespace_bringup_ros2 split_markers_devices.py
```

If you know the marker IDs for each device, lock the split explicitly:

```bash
ros2 run phasespace_bringup_ros2 split_markers_devices.py \
  --ros-args \
  -p device0_ids:=0,1,2,3,4,5,6,7 \
  -p device1_ids:=8,9,10,11,12,13,14,15
```

Publish markers to MQTT:

```bash
ros2 run phasespace_bringup_ros2 mqtt_publish_markers.py \
  --ros-args \
  -p ros_topic:=/phasespace/device_0/markers \
  -p mqtt_host:=192.168.0.200 \
  -p mqtt_topic:=phasespace/device0/markers
```

Receive MQTT markers and republish them as ROS topics on another machine:

```bash
ros2 run phasespace_bringup_ros2 mqtt_receive_markers.py \
  --ros-args \
  -p mqtt_host:=192.168.0.200 \
  -p mqtt_topic:=phasespace/device0/markers \
  -p ros_topic:=/remote/phasespace/device_0/markers
```
