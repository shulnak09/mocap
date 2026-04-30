#!/usr/bin/python3

import argparse
from collections import defaultdict
from dataclasses import dataclass, field
from statistics import median
from typing import DefaultDict

import matplotlib.pyplot as plt
import rclpy
from rclpy.node import Node

from phasespace_msgs_ros2.msg import Markers, Rigids


@dataclass
class Trace:
    times: list[float] = field(default_factory=list)
    xs: list[float] = field(default_factory=list)
    ys: list[float] = field(default_factory=list)
    zs: list[float] = field(default_factory=list)


class XYPlotCollector(Node):
    def __init__(
        self,
        topic: str,
        duration: float,
        max_ids: int,
        min_cond: float,
        zero_epsilon: float,
    ) -> None:
        super().__init__("phasespace_xy_plotter")
        self._topic = topic
        self._duration = duration
        self._max_ids = max_ids
        self._min_cond = min_cond
        self._zero_epsilon = zero_epsilon
        self._start_time = self.get_clock().now()
        self._data: DefaultDict[int, Trace] = defaultdict(Trace)
        self._tracked_ids: list[int] = []
        self._done = False

        if topic == "/phasespace/rigids":
            self.create_subscription(Rigids, topic, self._rigids_callback, 10)
        elif topic == "/phasespace/markers":
            self.create_subscription(Markers, topic, self._markers_callback, 10)
        else:
            raise ValueError("topic must be /phasespace/rigids or /phasespace/markers")

        self._timer = self.create_timer(0.2, self._check_timeout)
        self.get_logger().info(
            f"Collecting {topic} for {duration:.1f} s; plotting up to {max_ids} IDs"
        )

    @property
    def done(self) -> bool:
        return self._done

    @property
    def data(self) -> dict[int, Trace]:
        return dict(self._data)

    def _elapsed(self) -> float:
        return (self.get_clock().now() - self._start_time).nanoseconds / 1e9

    def _track_id(self, object_id: int) -> bool:
        if object_id in self._tracked_ids:
            return True
        if len(self._tracked_ids) >= self._max_ids:
            return False
        self._tracked_ids.append(object_id)
        self.get_logger().info(f"Tracking id={object_id}")
        return True

    def _is_valid_sample(self, x: float, y: float, z: float, cond: float) -> bool:
        if cond <= self._min_cond:
            return False
        if (
            abs(x) <= self._zero_epsilon
            and abs(y) <= self._zero_epsilon
            and abs(z) <= self._zero_epsilon
        ):
            return False
        return True

    def _store(self, object_id: int, x: float, y: float, z: float, cond: float) -> None:
        if not self._is_valid_sample(x, y, z, cond):
            return
        if not self._track_id(object_id):
            return
        trace = self._data[object_id]
        trace.times.append(self._elapsed())
        trace.xs.append(x)
        trace.ys.append(y)
        trace.zs.append(z)

    def _rigids_callback(self, msg: Rigids) -> None:
        for rigid in msg.rigids:
            self._store(rigid.id, rigid.x, rigid.y, rigid.z, rigid.cond)

    def _markers_callback(self, msg: Markers) -> None:
        for marker in msg.markers:
            self._store(marker.id, marker.x, marker.y, marker.z, marker.cond)

    def _check_timeout(self) -> None:
        if self._elapsed() >= self._duration:
            self._done = True


def clamp_window(window: int, length: int) -> int:
    if length <= 1:
        return 1
    window = max(1, window)
    if window % 2 == 0:
        window += 1
    return min(window, length if length % 2 == 1 else length - 1)


def median_filter(values: list[float], window: int) -> list[float]:
    if len(values) < 3 or window <= 1:
        return list(values)
    half = window // 2
    filtered: list[float] = []
    for index in range(len(values)):
        start = max(0, index - half)
        stop = min(len(values), index + half + 1)
        filtered.append(median(values[start:stop]))
    return filtered


def moving_average(values: list[float], window: int) -> list[float]:
    if len(values) < 3 or window <= 1:
        return list(values)
    half = window // 2
    smoothed: list[float] = []
    for index in range(len(values)):
        start = max(0, index - half)
        stop = min(len(values), index + half + 1)
        segment = values[start:stop]
        smoothed.append(sum(segment) / len(segment))
    return smoothed


def smooth_trace(values: list[float], median_window: int, smooth_window: int) -> list[float]:
    median_window = clamp_window(median_window, len(values))
    smooth_window = clamp_window(smooth_window, len(values))
    filtered = median_filter(values, median_window)
    return moving_average(filtered, smooth_window)


def plot_traces(
    topic: str,
    data: dict[int, Trace],
    duration: float,
    median_window: int,
    smooth_window: int,
) -> None:
    if not data:
        print(f"No samples received from {topic} in {duration:.1f} s")
        return

    fig, (ax_x, ax_y, ax_z) = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    sorted_ids = sorted(data.keys())
    for object_id in sorted_ids:
        trace = data[object_id]
        if not trace.times:
            continue
        ax_x.plot(
            trace.times,
            smooth_trace(trace.xs, median_window, smooth_window),
            label=f"id {object_id}",
        )
        ax_y.plot(
            trace.times,
            smooth_trace(trace.ys, median_window, smooth_window),
            label=f"id {object_id}",
        )
        ax_z.plot(
            trace.times,
            smooth_trace(trace.zs, median_window, smooth_window),
            label=f"id {object_id}",
        )

    ax_x.set_title(f"{topic} X over time (filtered and smoothed)")
    ax_x.set_ylabel("x [m]")
    ax_x.grid(True)
    ax_x.legend(loc="best", ncol=2)

    ax_y.set_title(f"{topic} Y over time (filtered and smoothed)")
    ax_y.set_ylabel("y [m]")
    ax_y.grid(True)
    ax_y.legend(loc="best", ncol=2)

    ax_z.set_title(f"{topic} Z over time (filtered and smoothed)")
    ax_z.set_xlabel("time [s]")
    ax_z.set_ylabel("z [m]")
    ax_z.grid(True)
    ax_z.legend(loc="best", ncol=2)

    fig.tight_layout()
    plt.show()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot filtered and smoothed x(t), y(t), and z(t) for Phasespace markers or rigids."
    )
    parser.add_argument(
        "--topic",
        default="/phasespace/markers",
        choices=["/phasespace/markers", "/phasespace/rigids"],
        help="Published Phasespace topic to record",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=20.0,
        help="Acquisition duration in seconds",
    )
    parser.add_argument(
        "--max-ids",
        type=int,
        default=8,
        help="Maximum number of unique IDs to plot",
    )
    parser.add_argument(
        "--min-cond",
        type=float,
        default=0.0,
        help="Ignore samples with cond less than or equal to this threshold",
    )
    parser.add_argument(
        "--zero-epsilon",
        type=float,
        default=1e-6,
        help="Treat samples with near-zero xyz values as invalid",
    )
    parser.add_argument(
        "--median-window",
        type=int,
        default=5,
        help="Median filter window size for spike rejection",
    )
    parser.add_argument(
        "--smooth-window",
        type=int,
        default=9,
        help="Moving-average window size for noise reduction",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rclpy.init()
    node = XYPlotCollector(
        args.topic,
        args.duration,
        args.max_ids,
        args.min_cond,
        args.zero_epsilon,
    )

    try:
        while rclpy.ok() and not node.done:
            rclpy.spin_once(node, timeout_sec=0.1)
    finally:
        data = node.data
        node.destroy_node()
        rclpy.shutdown()

    plot_traces(
        args.topic,
        data,
        args.duration,
        args.median_window,
        args.smooth_window,
    )


if __name__ == "__main__":
    main()
