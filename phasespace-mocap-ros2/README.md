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
