cmake_minimum_required(VERSION 3.8)
project(phasespace_msgs_ros2)

set(Python3_FIND_VIRTUALENV STANDARD)
if(DEFINED ENV{CONDA_PREFIX})
  set(Python3_EXECUTABLE /usr/bin/python3 CACHE FILEPATH
    "Force ROS 2 interface generation to use the system Python interpreter" FORCE)
  set(ENV{PATH} "/usr/bin:/bin:/usr/sbin:/sbin:/opt/ros/humble/bin")
  set(ENV{PYTHONPATH}
    "/opt/ros/humble/lib/python3.10/site-packages:/opt/ros/humble/local/lib/python3.10/dist-packages")
endif()

find_package(ament_cmake REQUIRED)
find_package(Python3 REQUIRED COMPONENTS Interpreter)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)

message(STATUS "phasespace_msgs_ros2 using Python3 interpreter: ${Python3_EXECUTABLE}")

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
