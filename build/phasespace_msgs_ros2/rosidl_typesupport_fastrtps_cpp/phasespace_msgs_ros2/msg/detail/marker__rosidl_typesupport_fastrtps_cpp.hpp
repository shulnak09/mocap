// generated from rosidl_typesupport_fastrtps_cpp/resource/idl__rosidl_typesupport_fastrtps_cpp.hpp.em
// with input from phasespace_msgs_ros2:msg/Marker.idl
// generated code does not contain a copyright notice

#ifndef PHASESPACE_MSGS_ROS2__MSG__DETAIL__MARKER__ROSIDL_TYPESUPPORT_FASTRTPS_CPP_HPP_
#define PHASESPACE_MSGS_ROS2__MSG__DETAIL__MARKER__ROSIDL_TYPESUPPORT_FASTRTPS_CPP_HPP_

#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_interface/macros.h"
#include "phasespace_msgs_ros2/msg/rosidl_typesupport_fastrtps_cpp__visibility_control.h"
#include "phasespace_msgs_ros2/msg/detail/marker__struct.hpp"

#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-parameter"
# ifdef __clang__
#  pragma clang diagnostic ignored "-Wdeprecated-register"
#  pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
# endif
#endif
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif

#include "fastcdr/Cdr.h"

namespace phasespace_msgs_ros2
{

namespace msg
{

namespace typesupport_fastrtps_cpp
{

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_phasespace_msgs_ros2
cdr_serialize(
  const phasespace_msgs_ros2::msg::Marker & ros_message,
  eprosima::fastcdr::Cdr & cdr);

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_phasespace_msgs_ros2
cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  phasespace_msgs_ros2::msg::Marker & ros_message);

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_phasespace_msgs_ros2
get_serialized_size(
  const phasespace_msgs_ros2::msg::Marker & ros_message,
  size_t current_alignment);

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_phasespace_msgs_ros2
max_serialized_size_Marker(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

}  // namespace typesupport_fastrtps_cpp

}  // namespace msg

}  // namespace phasespace_msgs_ros2

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_phasespace_msgs_ros2
const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, phasespace_msgs_ros2, msg, Marker)();

#ifdef __cplusplus
}
#endif

#endif  // PHASESPACE_MSGS_ROS2__MSG__DETAIL__MARKER__ROSIDL_TYPESUPPORT_FASTRTPS_CPP_HPP_
