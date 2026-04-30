cmake_minimum_required(VERSION 3.8)
project(phasespace_bringup_ros2)

find_package(ament_cmake REQUIRED)
find_package(phasespace_msgs_ros2 REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)

include_directories(
  include
)

add_library(owlsock SHARED IMPORTED GLOBAL)
set_target_properties(owlsock PROPERTIES
  IMPORTED_LOCATION ${CMAKE_CURRENT_SOURCE_DIR}/bin/libowlsock.so
)

add_executable(phasespace_bringup_node src/phasespace_bringup_node.cpp)
ament_target_dependencies(phasespace_bringup_node
  phasespace_msgs_ros2
  rclcpp
  std_msgs
)
target_link_libraries(phasespace_bringup_node owlsock)

install(
  TARGETS phasespace_bringup_node
  DESTINATION lib/${PROJECT_NAME}
)

install(
  DIRECTORY include/
  DESTINATION include
)

install(
  FILES bin/libowlsock.so
  DESTINATION lib
)

install(
  PROGRAMS
    scripts/read_rigids.py
    scripts/plot_xy_data.py
    scripts/live_plot_xyz.py
    scripts/live_spatial_plot.py
  DESTINATION lib/${PROJECT_NAME}
)

install(
  DIRECTORY launch/
  DESTINATION share/${PROJECT_NAME}/launch
)

ament_package()
