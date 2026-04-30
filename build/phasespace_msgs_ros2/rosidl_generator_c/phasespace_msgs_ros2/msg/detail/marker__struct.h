// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from phasespace_msgs_ros2:msg/Marker.idl
// generated code does not contain a copyright notice

#ifndef PHASESPACE_MSGS_ROS2__MSG__DETAIL__MARKER__STRUCT_H_
#define PHASESPACE_MSGS_ROS2__MSG__DETAIL__MARKER__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in msg/Marker in the package phasespace_msgs_ros2.
/**
  * Messages
 */
typedef struct phasespace_msgs_ros2__msg__Marker
{
  uint32_t id;
  uint32_t flags;
  uint64_t time;
  float x;
  float y;
  float z;
  float cond;
} phasespace_msgs_ros2__msg__Marker;

// Struct for a sequence of phasespace_msgs_ros2__msg__Marker.
typedef struct phasespace_msgs_ros2__msg__Marker__Sequence
{
  phasespace_msgs_ros2__msg__Marker * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} phasespace_msgs_ros2__msg__Marker__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // PHASESPACE_MSGS_ROS2__MSG__DETAIL__MARKER__STRUCT_H_
