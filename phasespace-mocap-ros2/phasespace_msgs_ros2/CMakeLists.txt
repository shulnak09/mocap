cmake_minimum_required(VERSION 3.8)
project(phasespace_msgs_ros2)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/Camera.msg"
  "msg/Cameras.msg"
  "msg/Marker.msg"
  "msg/Markers.msg"
  "msg/Rigid.msg"
  "msg/Rigids.msg"
  DEPENDENCIES std_msgs
)

ament_export_dependencies(rosidl_default_runtime)
ament_package()
