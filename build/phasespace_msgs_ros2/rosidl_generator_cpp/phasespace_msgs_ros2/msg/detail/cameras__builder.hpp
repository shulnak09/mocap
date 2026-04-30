// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from phasespace_msgs_ros2:msg/Cameras.idl
// generated code does not contain a copyright notice

#ifndef PHASESPACE_MSGS_ROS2__MSG__DETAIL__CAMERAS__BUILDER_HPP_
#define PHASESPACE_MSGS_ROS2__MSG__DETAIL__CAMERAS__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "phasespace_msgs_ros2/msg/detail/cameras__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace phasespace_msgs_ros2
{

namespace msg
{

namespace builder
{

class Init_Cameras_cameras
{
public:
  explicit Init_Cameras_cameras(::phasespace_msgs_ros2::msg::Cameras & msg)
  : msg_(msg)
  {}
  ::phasespace_msgs_ros2::msg::Cameras cameras(::phasespace_msgs_ros2::msg::Cameras::_cameras_type arg)
  {
    msg_.cameras = std::move(arg);
    return std::move(msg_);
  }

private:
  ::phasespace_msgs_ros2::msg::Cameras msg_;
};

class Init_Cameras_header
{
public:
  Init_Cameras_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Cameras_cameras header(::phasespace_msgs_ros2::msg::Cameras::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_Cameras_cameras(msg_);
  }

private:
  ::phasespace_msgs_ros2::msg::Cameras msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::phasespace_msgs_ros2::msg::Cameras>()
{
  return phasespace_msgs_ros2::msg::builder::Init_Cameras_header();
}

}  // namespace phasespace_msgs_ros2

#endif  // PHASESPACE_MSGS_ROS2__MSG__DETAIL__CAMERAS__BUILDER_HPP_
