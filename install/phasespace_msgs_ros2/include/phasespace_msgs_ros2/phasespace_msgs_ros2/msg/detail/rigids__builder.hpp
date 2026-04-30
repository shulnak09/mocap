// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from phasespace_msgs_ros2:msg/Rigids.idl
// generated code does not contain a copyright notice

#ifndef PHASESPACE_MSGS_ROS2__MSG__DETAIL__RIGIDS__BUILDER_HPP_
#define PHASESPACE_MSGS_ROS2__MSG__DETAIL__RIGIDS__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "phasespace_msgs_ros2/msg/detail/rigids__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace phasespace_msgs_ros2
{

namespace msg
{

namespace builder
{

class Init_Rigids_rigids
{
public:
  explicit Init_Rigids_rigids(::phasespace_msgs_ros2::msg::Rigids & msg)
  : msg_(msg)
  {}
  ::phasespace_msgs_ros2::msg::Rigids rigids(::phasespace_msgs_ros2::msg::Rigids::_rigids_type arg)
  {
    msg_.rigids = std::move(arg);
    return std::move(msg_);
  }

private:
  ::phasespace_msgs_ros2::msg::Rigids msg_;
};

class Init_Rigids_header
{
public:
  Init_Rigids_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Rigids_rigids header(::phasespace_msgs_ros2::msg::Rigids::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_Rigids_rigids(msg_);
  }

private:
  ::phasespace_msgs_ros2::msg::Rigids msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::phasespace_msgs_ros2::msg::Rigids>()
{
  return phasespace_msgs_ros2::msg::builder::Init_Rigids_header();
}

}  // namespace phasespace_msgs_ros2

#endif  // PHASESPACE_MSGS_ROS2__MSG__DETAIL__RIGIDS__BUILDER_HPP_
