// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from phasespace_msgs_ros2:msg/Rigid.idl
// generated code does not contain a copyright notice

#ifndef PHASESPACE_MSGS_ROS2__MSG__DETAIL__RIGID__BUILDER_HPP_
#define PHASESPACE_MSGS_ROS2__MSG__DETAIL__RIGID__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "phasespace_msgs_ros2/msg/detail/rigid__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace phasespace_msgs_ros2
{

namespace msg
{

namespace builder
{

class Init_Rigid_cond
{
public:
  explicit Init_Rigid_cond(::phasespace_msgs_ros2::msg::Rigid & msg)
  : msg_(msg)
  {}
  ::phasespace_msgs_ros2::msg::Rigid cond(::phasespace_msgs_ros2::msg::Rigid::_cond_type arg)
  {
    msg_.cond = std::move(arg);
    return std::move(msg_);
  }

private:
  ::phasespace_msgs_ros2::msg::Rigid msg_;
};

class Init_Rigid_qz
{
public:
  explicit Init_Rigid_qz(::phasespace_msgs_ros2::msg::Rigid & msg)
  : msg_(msg)
  {}
  Init_Rigid_cond qz(::phasespace_msgs_ros2::msg::Rigid::_qz_type arg)
  {
    msg_.qz = std::move(arg);
    return Init_Rigid_cond(msg_);
  }

private:
  ::phasespace_msgs_ros2::msg::Rigid msg_;
};

class Init_Rigid_qy
{
public:
  explicit Init_Rigid_qy(::phasespace_msgs_ros2::msg::Rigid & msg)
  : msg_(msg)
  {}
  Init_Rigid_qz qy(::phasespace_msgs_ros2::msg::Rigid::_qy_type arg)
  {
    msg_.qy = std::move(arg);
    return Init_Rigid_qz(msg_);
  }

private:
  ::phasespace_msgs_ros2::msg::Rigid msg_;
};

class Init_Rigid_qx
{
public:
  explicit Init_Rigid_qx(::phasespace_msgs_ros2::msg::Rigid & msg)
  : msg_(msg)
  {}
  Init_Rigid_qy qx(::phasespace_msgs_ros2::msg::Rigid::_qx_type arg)
  {
    msg_.qx = std::move(arg);
    return Init_Rigid_qy(msg_);
  }

private:
  ::phasespace_msgs_ros2::msg::Rigid msg_;
};

class Init_Rigid_qw
{
public:
  explicit Init_Rigid_qw(::phasespace_msgs_ros2::msg::Rigid & msg)
  : msg_(msg)
  {}
  Init_Rigid_qx qw(::phasespace_msgs_ros2::msg::Rigid::_qw_type arg)
  {
    msg_.qw = std::move(arg);
    return Init_Rigid_qx(msg_);
  }

private:
  ::phasespace_msgs_ros2::msg::Rigid msg_;
};

class Init_Rigid_z
{
public:
  explicit Init_Rigid_z(::phasespace_msgs_ros2::msg::Rigid & msg)
  : msg_(msg)
  {}
  Init_Rigid_qw z(::phasespace_msgs_ros2::msg::Rigid::_z_type arg)
  {
    msg_.z = std::move(arg);
    return Init_Rigid_qw(msg_);
  }

private:
  ::phasespace_msgs_ros2::msg::Rigid msg_;
};

class Init_Rigid_y
{
public:
  explicit Init_Rigid_y(::phasespace_msgs_ros2::msg::Rigid & msg)
  : msg_(msg)
  {}
  Init_Rigid_z y(::phasespace_msgs_ros2::msg::Rigid::_y_type arg)
  {
    msg_.y = std::move(arg);
    return Init_Rigid_z(msg_);
  }

private:
  ::phasespace_msgs_ros2::msg::Rigid msg_;
};

class Init_Rigid_x
{
public:
  explicit Init_Rigid_x(::phasespace_msgs_ros2::msg::Rigid & msg)
  : msg_(msg)
  {}
  Init_Rigid_y x(::phasespace_msgs_ros2::msg::Rigid::_x_type arg)
  {
    msg_.x = std::move(arg);
    return Init_Rigid_y(msg_);
  }

private:
  ::phasespace_msgs_ros2::msg::Rigid msg_;
};

class Init_Rigid_time
{
public:
  explicit Init_Rigid_time(::phasespace_msgs_ros2::msg::Rigid & msg)
  : msg_(msg)
  {}
  Init_Rigid_x time(::phasespace_msgs_ros2::msg::Rigid::_time_type arg)
  {
    msg_.time = std::move(arg);
    return Init_Rigid_x(msg_);
  }

private:
  ::phasespace_msgs_ros2::msg::Rigid msg_;
};

class Init_Rigid_flags
{
public:
  explicit Init_Rigid_flags(::phasespace_msgs_ros2::msg::Rigid & msg)
  : msg_(msg)
  {}
  Init_Rigid_time flags(::phasespace_msgs_ros2::msg::Rigid::_flags_type arg)
  {
    msg_.flags = std::move(arg);
    return Init_Rigid_time(msg_);
  }

private:
  ::phasespace_msgs_ros2::msg::Rigid msg_;
};

class Init_Rigid_id
{
public:
  Init_Rigid_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Rigid_flags id(::phasespace_msgs_ros2::msg::Rigid::_id_type arg)
  {
    msg_.id = std::move(arg);
    return Init_Rigid_flags(msg_);
  }

private:
  ::phasespace_msgs_ros2::msg::Rigid msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::phasespace_msgs_ros2::msg::Rigid>()
{
  return phasespace_msgs_ros2::msg::builder::Init_Rigid_id();
}

}  // namespace phasespace_msgs_ros2

#endif  // PHASESPACE_MSGS_ROS2__MSG__DETAIL__RIGID__BUILDER_HPP_
