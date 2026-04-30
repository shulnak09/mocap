#!/usr/bin/python3

import rclpy
from rclpy.node import Node

from phasespace_msgs_ros2.msg import Rigids


class RigidReader(Node):
    def __init__(self) -> None:
        super().__init__("rigid_reader")
        self.create_subscription(Rigids, "/phasespace/rigids", self._callback, 10)

    def _callback(self, msg: Rigids) -> None:
        for rigid in msg.rigids:
            self.get_logger().info(
                f"id={rigid.id} pos=({rigid.x:.4f}, {rigid.y:.4f}, {rigid.z:.4f}) "
                f"quat=({rigid.qw:.4f}, {rigid.qx:.4f}, {rigid.qy:.4f}, {rigid.qz:.4f}) "
                f"cond={rigid.cond:.4f}"
            )


def main() -> None:
    rclpy.init()
    node = RigidReader()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
