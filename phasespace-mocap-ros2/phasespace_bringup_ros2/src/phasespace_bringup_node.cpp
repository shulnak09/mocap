#include <chrono>
#include <memory>
#include <stdexcept>
#include <string>

#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/string.hpp>

#include "phasespace_bringup_ros2/owl.hpp"
#include "phasespace_msgs_ros2/msg/camera.hpp"
#include "phasespace_msgs_ros2/msg/cameras.hpp"
#include "phasespace_msgs_ros2/msg/marker.hpp"
#include "phasespace_msgs_ros2/msg/markers.hpp"
#include "phasespace_msgs_ros2/msg/rigid.hpp"
#include "phasespace_msgs_ros2/msg/rigids.hpp"

class PhasespaceBringupNode : public rclcpp::Node {
public:
  PhasespaceBringupNode()
  : Node("phasespace_bringup")
  {
    const auto server_ip =
      this->declare_parameter<std::string>("server_ip", "192.168.0.101");
    const auto event_timeout_us =
      this->declare_parameter<int>("event_timeout_us", 1000);
    const auto init_options =
      this->declare_parameter<std::string>("init_options", "timebase=1,1000000");

    errors_pub_ = this->create_publisher<std_msgs::msg::String>("/phasespace/errors", 10);
    cameras_pub_ = this->create_publisher<phasespace_msgs_ros2::msg::Cameras>(
      "/phasespace/cameras", 10);
    markers_pub_ = this->create_publisher<phasespace_msgs_ros2::msg::Markers>(
      "/phasespace/markers", 10);
    rigids_pub_ = this->create_publisher<phasespace_msgs_ros2::msg::Rigids>(
      "/phasespace/rigids", 10);

    RCLCPP_INFO(this->get_logger(), "Opening Phasespace server at %s", server_ip.c_str());

    if (owl_.open(server_ip) <= 0 || owl_.initialize(init_options) <= 0) {
      throw std::runtime_error("Failed to open or initialize Phasespace OWL connection");
    }

    owl_.streaming(1);
    RCLCPP_INFO(this->get_logger(), "Phasespace streaming enabled");

    timer_ = this->create_wall_timer(
      std::chrono::milliseconds(1),
      [this, event_timeout_us]() { this->poll_once(event_timeout_us); });
  }

  ~PhasespaceBringupNode() override
  {
    owl_.done();
    owl_.close();
  }

private:
  void poll_once(long timeout_us)
  {
    if (!owl_.isOpen() || !owl_.property<int>("initialized")) {
      return;
    }

    const OWL::Event * event = owl_.nextEvent(timeout_us);
    if (!event) {
      return;
    }

    if (event->type_id() == OWL::Type::ERROR) {
      std_msgs::msg::String out;
      out.data = event->str();
      errors_pub_->publish(out);
      RCLCPP_ERROR(this->get_logger(), "%s: %s", event->name(), event->str().c_str());
      return;
    }

    if (event->type_id() == OWL::Type::CAMERA) {
      publish_cameras(*event);
      return;
    }

    if (event->type_id() == OWL::Type::FRAME) {
      publish_markers(*event);
      publish_rigids(*event);
    }
  }

  void publish_cameras(const OWL::Event & event)
  {
    if (event.name() != std::string("cameras") || event.get(cameras_) <= 0) {
      return;
    }

    phasespace_msgs_ros2::msg::Cameras out;
    out.header.stamp = this->now();
    out.header.frame_id = "phasespace_base";
    out.cameras.reserve(cameras_.size());

    for (const auto & camera : cameras_) {
      phasespace_msgs_ros2::msg::Camera msg;
      msg.id = camera.id;
      msg.flags = camera.flags;
      msg.cond = camera.cond;
      msg.x = camera.pose[0] / 1000.0f;
      msg.y = -camera.pose[2] / 1000.0f;
      msg.z = camera.pose[1] / 1000.0f;
      msg.qw = camera.pose[3];
      msg.qx = camera.pose[4];
      msg.qy = camera.pose[6];
      msg.qz = camera.pose[5];
      out.cameras.push_back(msg);
    }

    cameras_pub_->publish(out);
  }

  void publish_markers(const OWL::Event & event)
  {
    if (event.find("markers", markers_) <= 0) {
      return;
    }

    phasespace_msgs_ros2::msg::Markers out;
    out.header.stamp = this->now();
    out.header.frame_id = "phasespace_base";
    out.markers.reserve(markers_.size());

    for (const auto & marker : markers_) {
      phasespace_msgs_ros2::msg::Marker msg;
      msg.id = marker.id;
      msg.time = static_cast<uint64_t>(marker.time);
      msg.flags = marker.flags;
      msg.cond = marker.cond;
      msg.x = marker.x / 1000.0f;
      msg.y = marker.z / 1000.0f;
      msg.z = marker.y / 1000.0f;
      out.markers.push_back(msg);
    }

    markers_pub_->publish(out);
  }

  void publish_rigids(const OWL::Event & event)
  {
    if (event.find("rigids", rigids_) <= 0) {
      return;
    }

    phasespace_msgs_ros2::msg::Rigids out;
    out.header.stamp = this->now();
    out.header.frame_id = "phasespace_base";
    out.rigids.reserve(rigids_.size());

    for (const auto & rigid : rigids_) {
      phasespace_msgs_ros2::msg::Rigid msg;
      msg.id = rigid.id;
      msg.time = static_cast<uint64_t>(rigid.time);
      msg.flags = rigid.flags;
      msg.cond = rigid.cond;
      msg.x = rigid.pose[0] / 1000.0f;
      msg.y = -rigid.pose[2] / 1000.0f;
      msg.z = rigid.pose[1] / 1000.0f;
      msg.qw = rigid.pose[3];
      msg.qx = rigid.pose[4];
      msg.qy = -rigid.pose[6];
      msg.qz = rigid.pose[5];
      out.rigids.push_back(msg);
    }

    rigids_pub_->publish(out);
  }

  OWL::Context owl_;
  OWL::Cameras cameras_;
  OWL::Markers markers_;
  OWL::Rigids rigids_;

  rclcpp::TimerBase::SharedPtr timer_;
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr errors_pub_;
  rclcpp::Publisher<phasespace_msgs_ros2::msg::Cameras>::SharedPtr cameras_pub_;
  rclcpp::Publisher<phasespace_msgs_ros2::msg::Markers>::SharedPtr markers_pub_;
  rclcpp::Publisher<phasespace_msgs_ros2::msg::Rigids>::SharedPtr rigids_pub_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);

  try {
    auto node = std::make_shared<PhasespaceBringupNode>();
    rclcpp::spin(node);
  } catch (const std::exception & ex) {
    rclcpp::shutdown();
    throw;
  }

  rclcpp::shutdown();
  return 0;
}
