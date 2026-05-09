#!/usr/bin/python3

import json
import sys

import rclpy
from rclpy.node import Node

from phasespace_msgs_ros2.msg import Markers

try:
    import paho.mqtt.client as mqtt
except ImportError as exc:
    raise SystemExit(
        "paho-mqtt is required. Install it with 'pip install paho-mqtt' "
        "or 'sudo apt install python3-paho-mqtt'."
    ) from exc


def make_mqtt_client():
    callback_api = getattr(mqtt, "CallbackAPIVersion", None)
    if callback_api is not None:
        return mqtt.Client(callback_api.VERSION2)
    return mqtt.Client()


def markers_to_dict(msg: Markers) -> dict:
    return {
        "header": {
            "stamp": {
                "sec": int(msg.header.stamp.sec),
                "nanosec": int(msg.header.stamp.nanosec),
            },
            "frame_id": msg.header.frame_id,
        },
        "markers": [
            {
                "id": int(marker.id),
                "flags": int(marker.flags),
                "time": int(marker.time),
                "x": float(marker.x),
                "y": float(marker.y),
                "z": float(marker.z),
                "cond": float(marker.cond),
            }
            for marker in msg.markers
        ],
    }


class MarkerMqttPublisher(Node):
    def __init__(self) -> None:
        super().__init__("marker_mqtt_publisher")

        self.declare_parameter("ros_topic", "/phasespace/markers")
        self.declare_parameter("mqtt_host", "127.0.0.1")
        self.declare_parameter("mqtt_port", 1883)
        self.declare_parameter("mqtt_topic", "phasespace/markers")
        self.declare_parameter("mqtt_qos", 0)

        ros_topic = self.get_parameter("ros_topic").get_parameter_value().string_value
        mqtt_host = self.get_parameter("mqtt_host").get_parameter_value().string_value
        mqtt_port = self.get_parameter("mqtt_port").get_parameter_value().integer_value
        self._mqtt_topic = self.get_parameter("mqtt_topic").get_parameter_value().string_value
        self._mqtt_qos = self.get_parameter("mqtt_qos").get_parameter_value().integer_value

        self._mqtt_client = make_mqtt_client()
        self._mqtt_client.connect(mqtt_host, int(mqtt_port), 60)
        self._mqtt_client.loop_start()

        self.create_subscription(Markers, ros_topic, self._callback, 10)
        self.get_logger().info(
            f"Publishing {ros_topic} to MQTT broker {mqtt_host}:{mqtt_port} on topic {self._mqtt_topic}"
        )

    def _callback(self, msg: Markers) -> None:
        payload = json.dumps(markers_to_dict(msg))
        info = self._mqtt_client.publish(self._mqtt_topic, payload, qos=int(self._mqtt_qos))
        if info.rc != mqtt.MQTT_ERR_SUCCESS:
            self.get_logger().error(f"MQTT publish failed with code {info.rc}")

    def destroy_node(self):
        self._mqtt_client.loop_stop()
        self._mqtt_client.disconnect()
        return super().destroy_node()


def main() -> None:
    rclpy.init()
    node = MarkerMqttPublisher()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
