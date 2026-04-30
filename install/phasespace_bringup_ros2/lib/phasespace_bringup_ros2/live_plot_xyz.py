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
    return moving_average(median_filter(values, median_window), smooth_window)


class LivePlotter(Node):
    def __init__(
        self,
        topic: str,
        history: float,
        max_ids: int,
        min_cond: float,
        zero_epsilon: float,
        median_window: int,
        smooth_window: int,
        refresh_hz: float,
    ) -> None:
        super().__init__("phasespace_live_plotter")
        self._topic = topic
        self._history = history
        self._max_ids = max_ids
        self._min_cond = min_cond
        self._zero_epsilon = zero_epsilon
        self._median_window = median_window
        self._smooth_window = smooth_window
        self._start_time = self.get_clock().now()
        self._data: DefaultDict[int, Trace] = defaultdict(Trace)
        self._tracked_ids: list[int] = []

        self._figure, self._axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
        self._figure.canvas.manager.set_window_title("Phasespace Live XYZ")
        plt.ion()
        plt.show(block=False)

        if topic == "/phasespace/rigids":
            self.create_subscription(Rigids, topic, self._rigids_callback, 10)
        elif topic == "/phasespace/markers":
            self.create_subscription(Markers, topic, self._markers_callback, 10)
        else:
            raise ValueError("topic must be /phasespace/rigids or /phasespace/markers")

        self.create_timer(1.0 / refresh_hz, self._draw)
        self.get_logger().info(
            f"Live plotting {topic} with a {history:.1f} s history window for up to {max_ids} IDs"
        )

    def figure_open(self) -> bool:
        return plt.fignum_exists(self._figure.number)

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

    def _trim_history(self, trace: Trace) -> None:
        cutoff = self._elapsed() - self._history
        keep_from = 0
        for index, timestamp in enumerate(trace.times):
          if timestamp >= cutoff:
              keep_from = index
              break
        else:
          keep_from = len(trace.times)
        if keep_from == 0:
            return
        trace.times = trace.times[keep_from:]
        trace.xs = trace.xs[keep_from:]
        trace.ys = trace.ys[keep_from:]
        trace.zs = trace.zs[keep_from:]

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
        self._trim_history(trace)

    def _rigids_callback(self, msg: Rigids) -> None:
        for rigid in msg.rigids:
            self._store(rigid.id, rigid.x, rigid.y, rigid.z, rigid.cond)

    def _markers_callback(self, msg: Markers) -> None:
        for marker in msg.markers:
            self._store(marker.id, marker.x, marker.y, marker.z, marker.cond)

    def _draw_axis(self, axis, title: str, ylabel: str, traces: list[tuple[int, list[float], list[float]]]) -> None:
        axis.clear()
        for object_id, times, values in traces:
            if not times:
                continue
            axis.plot(
                times,
                smooth_trace(values, self._median_window, self._smooth_window),
                label=f"id {object_id}",
            )
        axis.set_title(title)
        axis.set_ylabel(ylabel)
        axis.grid(True)
        if traces:
            axis.legend(loc="best", ncol=2)

    def _draw(self) -> None:
        if not self.figure_open():
            return

        current = self._elapsed()
        traces = []
        for object_id in sorted(self._tracked_ids):
            trace = self._data[object_id]
            self._trim_history(trace)
            traces.append((object_id, trace.times, trace.xs, trace.ys, trace.zs))

        self._draw_axis(
            self._axes[0],
            f"{self._topic} X live view",
            "x [m]",
            [(object_id, times, xs) for object_id, times, xs, _, _ in traces],
        )
        self._draw_axis(
            self._axes[1],
            f"{self._topic} Y live view",
            "y [m]",
            [(object_id, times, ys) for object_id, times, _, ys, _ in traces],
        )
        self._draw_axis(
            self._axes[2],
            f"{self._topic} Z live view",
            "z [m]",
            [(object_id, times, zs) for object_id, times, _, _, zs in traces],
        )
        self._axes[2].set_xlabel("time [s]")

        start = max(0.0, current - self._history)
        self._axes[2].set_xlim(start, max(current, start + 1e-3))
        self._figure.tight_layout()
        self._figure.canvas.draw_idle()
        self._figure.canvas.flush_events()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Live plot filtered and smoothed x(t), y(t), and z(t) from Phasespace topics."
    )
    parser.add_argument(
        "--topic",
        default="/phasespace/markers",
        choices=["/phasespace/markers", "/phasespace/rigids"],
        help="Published Phasespace topic to visualize",
    )
    parser.add_argument(
        "--history",
        type=float,
        default=20.0,
        help="Rolling history window in seconds",
    )
    parser.add_argument(
        "--max-ids",
        type=int,
        default=8,
        help="Maximum number of unique IDs to display",
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
        help="Treat near-zero xyz values as invalid",
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
    parser.add_argument(
        "--refresh-hz",
        type=float,
        default=4.0,
        help="Plot refresh rate in Hz",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rclpy.init()
    node = LivePlotter(
        args.topic,
        args.history,
        args.max_ids,
        args.min_cond,
        args.zero_epsilon,
        args.median_window,
        args.smooth_window,
        args.refresh_hz,
    )

    try:
        while rclpy.ok() and node.figure_open():
            rclpy.spin_once(node, timeout_sec=0.1)
    finally:
        node.destroy_node()
        rclpy.shutdown()
        plt.close("all")


if __name__ == "__main__":
    main()
