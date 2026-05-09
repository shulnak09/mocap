#!/usr/bin/python3

import argparse
import math
from typing import Iterable

import rclpy
from rclpy.node import Node

from phasespace_msgs_ros2.msg import Marker, Markers


def parse_ids(ids_text: str) -> list[int]:
    if not ids_text.strip():
        return []
    return [int(part.strip()) for part in ids_text.split(",") if part.strip()]


def marker_valid(marker: Marker, min_cond: float, zero_epsilon: float) -> bool:
    if marker.cond <= min_cond:
        return False
    if (
        abs(marker.x) <= zero_epsilon
        and abs(marker.y) <= zero_epsilon
        and abs(marker.z) <= zero_epsilon
    ):
        return False
    return True


def centroid(markers: Iterable[Marker]) -> tuple[float, float, float]:
    markers_list = list(markers)
    if not markers_list:
        return (0.0, 0.0, 0.0)
    count = float(len(markers_list))
    return (
        sum(marker.x for marker in markers_list) / count,
        sum(marker.y for marker in markers_list) / count,
        sum(marker.z for marker in markers_list) / count,
    )


def distance(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return math.sqrt(
        (a[0] - b[0]) ** 2 +
        (a[1] - b[1]) ** 2 +
        (a[2] - b[2]) ** 2
    )


def nearest_cluster(
    marker: Marker,
    center_a: tuple[float, float, float],
    center_b: tuple[float, float, float],
) -> int:
    marker_xyz = (marker.x, marker.y, marker.z)
    return 0 if distance(marker_xyz, center_a) <= distance(marker_xyz, center_b) else 1


def kmeans_two(markers: list[Marker], iterations: int = 6) -> tuple[list[Marker], list[Marker]]:
    if len(markers) <= 1:
        return markers, []

    seed_a = markers[0]
    seed_b = max(
        markers[1:],
        key=lambda marker: distance(
            (marker.x, marker.y, marker.z),
            (seed_a.x, seed_a.y, seed_a.z),
        ),
    )
    center_a = (seed_a.x, seed_a.y, seed_a.z)
    center_b = (seed_b.x, seed_b.y, seed_b.z)

    cluster_a: list[Marker] = []
    cluster_b: list[Marker] = []
    for _ in range(iterations):
        cluster_a = []
        cluster_b = []
        for marker in markers:
            if nearest_cluster(marker, center_a, center_b) == 0:
                cluster_a.append(marker)
            else:
                cluster_b.append(marker)

        if not cluster_a or not cluster_b:
            midpoint = max(1, len(markers) // 2)
            cluster_a = markers[:midpoint]
            cluster_b = markers[midpoint:]
            break

        center_a = centroid(cluster_a)
        center_b = centroid(cluster_b)

    return cluster_a, cluster_b


class MarkerDeviceSplitter(Node):
    def __init__(self) -> None:
        super().__init__("marker_device_splitter")

        self.declare_parameter("input_topic", "/phasespace/markers")
        self.declare_parameter("device0_topic", "/phasespace/device_0/markers")
        self.declare_parameter("device1_topic", "/phasespace/device_1/markers")
        self.declare_parameter("device0_ids", "")
        self.declare_parameter("device1_ids", "")
        self.declare_parameter("min_cond", 0.0)
        self.declare_parameter("zero_epsilon", 1e-6)

        input_topic = self.get_parameter("input_topic").get_parameter_value().string_value
        device0_topic = self.get_parameter("device0_topic").get_parameter_value().string_value
        device1_topic = self.get_parameter("device1_topic").get_parameter_value().string_value
        self._device0_ids = parse_ids(
            self.get_parameter("device0_ids").get_parameter_value().string_value
        )
        self._device1_ids = parse_ids(
            self.get_parameter("device1_ids").get_parameter_value().string_value
        )
        self._min_cond = self.get_parameter("min_cond").get_parameter_value().double_value
        self._zero_epsilon = self.get_parameter("zero_epsilon").get_parameter_value().double_value

        self._device0_pub = self.create_publisher(Markers, device0_topic, 10)
        self._device1_pub = self.create_publisher(Markers, device1_topic, 10)
        self.create_subscription(Markers, input_topic, self._callback, 10)

        self._previous_centroids: tuple[tuple[float, float, float], tuple[float, float, float]] | None = None

        mode = "id-based" if self._device0_ids or self._device1_ids else "spatial-cluster"
        self.get_logger().info(
            f"Splitting {input_topic} into {device0_topic} and {device1_topic} using {mode} mode"
        )

    def _group_by_ids(self, markers: list[Marker]) -> tuple[list[Marker], list[Marker]]:
        device0 = [marker for marker in markers if marker.id in self._device0_ids]
        device1 = [marker for marker in markers if marker.id in self._device1_ids]
        return device0, device1

    def _group_by_clusters(self, markers: list[Marker]) -> tuple[list[Marker], list[Marker]]:
        cluster0, cluster1 = kmeans_two(markers)
        centroid0 = centroid(cluster0)
        centroid1 = centroid(cluster1)

        if self._previous_centroids is not None:
            keep = (
                distance(centroid0, self._previous_centroids[0]) +
                distance(centroid1, self._previous_centroids[1])
            )
            swap = (
                distance(centroid0, self._previous_centroids[1]) +
                distance(centroid1, self._previous_centroids[0])
            )
            if swap < keep:
                cluster0, cluster1 = cluster1, cluster0
                centroid0, centroid1 = centroid1, centroid0

        self._previous_centroids = (centroid0, centroid1)
        return cluster0, cluster1

    def _publish_group(self, publisher, source_msg: Markers, markers: list[Marker]) -> None:
        out = Markers()
        out.header = source_msg.header
        out.markers = markers
        publisher.publish(out)

    def _callback(self, msg: Markers) -> None:
        valid_markers = [
            marker for marker in msg.markers
            if marker_valid(marker, self._min_cond, self._zero_epsilon)
        ]

        if self._device0_ids or self._device1_ids:
            device0, device1 = self._group_by_ids(valid_markers)
        else:
            device0, device1 = self._group_by_clusters(valid_markers)

        self._publish_group(self._device0_pub, msg, device0)
        self._publish_group(self._device1_pub, msg, device1)


def main() -> None:
    rclpy.init()
    node = MarkerDeviceSplitter()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
