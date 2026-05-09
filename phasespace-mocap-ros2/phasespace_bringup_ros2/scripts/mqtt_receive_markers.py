#!/usr/bin/python3

import json
import ssl
import threading

import rclpy
from rclpy.node import Node

from phasespace_msgs_ros2.msg import Marker, Markers

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


def configure_mqtt_client(
    client,
    host: str,
    port: int,
    keepalive: int,
    use_tls: bool,
    ca_file: str,
    insecure_tls: bool,
    username: str,
    password: str,
) -> None:
    if username:
        client.username_pw_set(username, password if password else None)

    if use_tls:
        tls_kwargs = {"cert_reqs": ssl.CERT_REQUIRED}
        if ca_file:
            tls_kwargs["ca_certs"] = ca_file
        client.tls_set(**tls_kwargs)
        if insecure_tls:
            client.tls_insecure_set(True)

    client.connect(host, port, keepalive)


def dict_to_markers(payload: dict) -> Markers:
    msg = Markers()
    header = payload.get("header", {})
    stamp = header.get("stamp", {})
    msg.header.stamp.sec = int(stamp.get("sec", 0))
    msg.header.stamp.nanosec = int(stamp.get("nanosec", 0))
    msg.header.frame_id = str(header.get("frame_id", ""))

    for marker_in in payload.get("markers", []):
        marker = Marker()
        marker.id = int(marker_in.get("id", 0))
        marker.flags = int(marker_in.get("flags", 0))
        marker.time = int(marker_in.get("time", 0))
        marker.x = float(marker_in.get("x", 0.0))
        marker.y = float(marker_in.get("y", 0.0))
        marker.z = float(marker_in.get("z", 0.0))
        marker.cond = float(marker_in.get("cond", 0.0))
        msg.markers.append(marker)

    return msg


class MarkerMqttReceiver(Node):
    def __init__(self) -> None:
        super().__init__("marker_mqtt_receiver")

        self.declare_parameter("mqtt_host", "127.0.0.1")
        self.declare_parameter("mqtt_port", 1883)
        self.declare_parameter("mqtt_topic", "phasespace/markers")
        self.declare_parameter("ros_topic", "/remote/phasespace/markers")
        self.declare_parameter("mqtt_qos", 0)
        self.declare_parameter("mqtt_keepalive", 60)
        self.declare_parameter("mqtt_use_tls", False)
        self.declare_parameter("mqtt_ca_file", "")
        self.declare_parameter("mqtt_insecure_tls", False)
        self.declare_parameter("mqtt_username", "")
        self.declare_parameter("mqtt_password", "")
        self.declare_parameter("mqtt_client_id", "")

        mqtt_host = self.get_parameter("mqtt_host").get_parameter_value().string_value
        mqtt_port = self.get_parameter("mqtt_port").get_parameter_value().integer_value
        mqtt_topic = self.get_parameter("mqtt_topic").get_parameter_value().string_value
        mqtt_qos = self.get_parameter("mqtt_qos").get_parameter_value().integer_value
        mqtt_keepalive = self.get_parameter("mqtt_keepalive").get_parameter_value().integer_value
        mqtt_use_tls = self.get_parameter("mqtt_use_tls").get_parameter_value().bool_value
        mqtt_ca_file = self.get_parameter("mqtt_ca_file").get_parameter_value().string_value
        mqtt_insecure_tls = self.get_parameter("mqtt_insecure_tls").get_parameter_value().bool_value
        mqtt_username = self.get_parameter("mqtt_username").get_parameter_value().string_value
        mqtt_password = self.get_parameter("mqtt_password").get_parameter_value().string_value
        mqtt_client_id = self.get_parameter("mqtt_client_id").get_parameter_value().string_value
        ros_topic = self.get_parameter("ros_topic").get_parameter_value().string_value

        self._publisher = self.create_publisher(Markers, ros_topic, 10)
        self._lock = threading.Lock()

        self._mqtt_client = make_mqtt_client()
        if mqtt_client_id:
            try:
                self._mqtt_client.reinitialise(client_id=mqtt_client_id)
            except AttributeError:
                self.get_logger().warning("MQTT client ID reinitialisation is not supported by this Paho version")
        self._mqtt_client.on_connect = self._on_connect
        self._mqtt_client.on_message = self._on_message
        self._mqtt_topic = mqtt_topic
        self._mqtt_qos = int(mqtt_qos)
        configure_mqtt_client(
            self._mqtt_client,
            mqtt_host,
            int(mqtt_port),
            int(mqtt_keepalive),
            mqtt_use_tls,
            mqtt_ca_file,
            mqtt_insecure_tls,
            mqtt_username,
            mqtt_password,
        )
        self._mqtt_client.loop_start()

        self.get_logger().info(
            f"Subscribing to MQTT {mqtt_host}:{mqtt_port}/{mqtt_topic} and republishing on {ros_topic}"
        )

    def _on_connect(self, client, userdata, connect_flags, reason_code, properties=None) -> None:
        if hasattr(reason_code, "is_failure"):
            if reason_code.is_failure:
                self.get_logger().error(f"MQTT connection failed: {reason_code}")
                return
        elif int(reason_code) != 0:
            self.get_logger().error(f"MQTT connection failed with code {reason_code}")
            return
        client.subscribe(self._mqtt_topic, qos=self._mqtt_qos)

    def _on_message(self, client, userdata, mqtt_message) -> None:
        try:
            payload = json.loads(mqtt_message.payload.decode("utf-8"))
            ros_msg = dict_to_markers(payload)
        except Exception as exc:
            self.get_logger().error(f"Failed to decode MQTT marker payload: {exc}")
            return

        with self._lock:
            self._publisher.publish(ros_msg)

    def destroy_node(self):
        self._mqtt_client.loop_stop()
        self._mqtt_client.disconnect()
        return super().destroy_node()


def main() -> None:
    rclpy.init()
    node = MarkerMqttReceiver()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
