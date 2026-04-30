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


class AxisKalmanFilter:
    def __init__(self, process_var: float, measurement_var: float) -> None:
        self.process_var = process_var
        self.measurement_var = measurement_var
        self.initialized = False
        self.position = 0.0
        self.velocity = 0.0
        self.p00 = 1.0
        self.p01 = 0.0
        self.p10 = 0.0
        self.p11 = 1.0

    def initialize(self, measurement: float) -> None:
        self.initialized = True
        self.position = measurement
        self.velocity = 0.0
        self.p00 = self.measurement_var
        self.p01 = 0.0
        self.p10 = 0.0
        self.p11 = 1.0

    def predict(self, dt: float) -> None:
        if not self.initialized or dt <= 0.0:
            return

        q = self.process_var
        q00 = 0.25 * dt * dt * dt * dt * q
        q01 = 0.5 * dt * dt * dt * q
        q11 = dt * dt * q

        old_p00 = self.p00
        old_p01 = self.p01
        old_p10 = self.p10
        old_p11 = self.p11

        self.position = self.position + dt * self.velocity
        self.p00 = old_p00 + dt * (old_p10 + old_p01) + dt * dt * old_p11 + q00
        self.p01 = old_p01 + dt * old_p11 + q01
        self.p10 = old_p10 + dt * old_p11 + q01
        self.p11 = old_p11 + q11

    def update(self, measurement: float) -> None:
        if not self.initialized:
            self.initialize(measurement)
            return

        innovation = measurement - self.position
        residual = self.p00 + self.measurement_var
        if residual <= 0.0:
            return

        gain_pos = self.p00 / residual
        gain_vel = self.p10 / residual

        old_p00 = self.p00
        old_p01 = self.p01

        self.position = self.position + gain_pos * innovation
        self.velocity = self.velocity + gain_vel * innovation
        self.p00 = (1.0 - gain_pos) * old_p00
        self.p01 = (1.0 - gain_pos) * old_p01
        self.p10 = self.p10 - gain_vel * old_p00
        self.p11 = self.p11 - gain_vel * old_p01


class SpatialKalmanFilter:
    def __init__(self, process_var: float, measurement_var: float) -> None:
        self.x_filter = AxisKalmanFilter(process_var, measurement_var)
        self.y_filter = AxisKalmanFilter(process_var, measurement_var)
        self.z_filter = AxisKalmanFilter(process_var, measurement_var)
        self.last_time: float | None = None

    @property
    def initialized(self) -> bool:
        return self.x_filter.initialized

    def _predict_to(self, timestamp: float) -> None:
        if self.last_time is None:
            self.last_time = timestamp
            return
        dt = timestamp - self.last_time
        if dt > 0.0:
            self.x_filter.predict(dt)
            self.y_filter.predict(dt)
            self.z_filter.predict(dt)
            self.last_time = timestamp

    def update(self, timestamp: float, x: float, y: float, z: float) -> tuple[float, float, float]:
        self._predict_to(timestamp)
        self.x_filter.update(x)
        self.y_filter.update(y)
        self.z_filter.update(z)
        return self.state()

    def predict_only(self, timestamp: float) -> tuple[float, float, float] | None:
        if not self.initialized:
            return None
        self._predict_to(timestamp)
        return self.state()

    def state(self) -> tuple[float, float, float]:
        return (
            self.x_filter.position,
            self.y_filter.position,
            self.z_filter.position,
        )


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


class LiveSpatialPlotter(Node):
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
        combine_count: int,
        combine_ids: list[int],
        process_var: float,
        measurement_var: float,
    ) -> None:
        super().__init__("phasespace_live_spatial_plotter")
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
        self._combine_count = max(0, combine_count)
        self._combine_ids = list(combine_ids)
        self._combined_raw = Trace()
        self._combined_filtered = Trace()
        self._combined_filter = SpatialKalmanFilter(process_var, measurement_var)

        self._figure = plt.figure(figsize=(10, 8))
        self._axis = self._figure.add_subplot(111, projection="3d")
        self._figure.canvas.manager.set_window_title("Phasespace Live Spatial Plot")
        plt.ion()
        plt.show(block=False)

        if topic == "/phasespace/rigids":
            self.create_subscription(Rigids, topic, self._rigids_callback, 10)
        elif topic == "/phasespace/markers":
            self.create_subscription(Markers, topic, self._markers_callback, 10)
        else:
            raise ValueError("topic must be /phasespace/rigids or /phasespace/markers")

        self.create_timer(1.0 / refresh_hz, self._draw)
        mode = "combined-marker fusion" if self._use_combined_markers() else "per-id plotting"
        history_text = "full history" if history <= 0.0 else f"{history:.1f} s rolling history"
        self.get_logger().info(
            f"Live spatial plotting {topic} in {mode} mode with {history_text}"
        )

    def figure_open(self) -> bool:
        return plt.fignum_exists(self._figure.number)

    def _elapsed(self) -> float:
        return (self.get_clock().now() - self._start_time).nanoseconds / 1e9

    def _use_combined_markers(self) -> bool:
        return self._topic == "/phasespace/markers" and self._combine_count > 0

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
        if self._history <= 0.0:
            return
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

    def _append_trace(self, trace: Trace, timestamp: float, x: float, y: float, z: float) -> None:
        trace.times.append(timestamp)
        trace.xs.append(x)
        trace.ys.append(y)
        trace.zs.append(z)
        self._trim_history(trace)

    def _store(self, object_id: int, x: float, y: float, z: float, cond: float) -> None:
        if not self._is_valid_sample(x, y, z, cond):
            return
        if not self._track_id(object_id):
            return
        trace = self._data[object_id]
        self._append_trace(trace, self._elapsed(), x, y, z)

    def _remember_combine_ids(self, available_ids: list[int]) -> None:
        for object_id in available_ids:
            if object_id in self._combine_ids:
                continue
            if len(self._combine_ids) >= self._combine_count:
                return
            self._combine_ids.append(object_id)
            self.get_logger().info(f"Using marker id={object_id} for combined estimate")

    def _update_combined_markers(self, msg: Markers) -> None:
        timestamp = self._elapsed()
        valid_samples: dict[int, tuple[float, float, float]] = {}
        for marker in msg.markers:
            if self._is_valid_sample(marker.x, marker.y, marker.z, marker.cond):
                valid_samples[marker.id] = (marker.x, marker.y, marker.z)

        self._remember_combine_ids(sorted(valid_samples.keys()))
        selected_ids = self._combine_ids[: self._combine_count]
        selected_samples = [valid_samples[object_id] for object_id in selected_ids if object_id in valid_samples]

        if selected_samples:
            count = float(len(selected_samples))
            centroid_x = sum(sample[0] for sample in selected_samples) / count
            centroid_y = sum(sample[1] for sample in selected_samples) / count
            centroid_z = sum(sample[2] for sample in selected_samples) / count
            self._append_trace(self._combined_raw, timestamp, centroid_x, centroid_y, centroid_z)
            filtered_x, filtered_y, filtered_z = self._combined_filter.update(
                timestamp,
                centroid_x,
                centroid_y,
                centroid_z,
            )
            self._append_trace(
                self._combined_filtered,
                timestamp,
                filtered_x,
                filtered_y,
                filtered_z,
            )
            return

        predicted = self._combined_filter.predict_only(timestamp)
        if predicted is not None:
            self._append_trace(self._combined_filtered, timestamp, predicted[0], predicted[1], predicted[2])

    def _rigids_callback(self, msg: Rigids) -> None:
        for rigid in msg.rigids:
            self._store(rigid.id, rigid.x, rigid.y, rigid.z, rigid.cond)

    def _markers_callback(self, msg: Markers) -> None:
        if self._use_combined_markers():
            self._update_combined_markers(msg)
            return
        for marker in msg.markers:
            self._store(marker.id, marker.x, marker.y, marker.z, marker.cond)

    def _plot_combined(self) -> None:
        raw = self._combined_raw
        filtered = self._combined_filtered
        if raw.xs:
            self._axis.plot(raw.xs, raw.ys, raw.zs, "--", color="0.6", label="raw centroid")
            self._axis.scatter(raw.xs[-1], raw.ys[-1], raw.zs[-1], color="0.6", s=20)
        if filtered.xs:
            label = "kalman estimate"
            if self._combine_ids:
                label = f"kalman estimate ids {self._combine_ids[:self._combine_count]}"
            self._axis.plot(filtered.xs, filtered.ys, filtered.zs, color="tab:red", linewidth=2.0, label=label)
            self._axis.scatter(filtered.xs[-1], filtered.ys[-1], filtered.zs[-1], color="tab:red", s=35)

    def _plot_individual(self) -> None:
        for object_id in sorted(self._tracked_ids):
            trace = self._data[object_id]
            self._trim_history(trace)
            if not trace.xs:
                continue
            xs = smooth_trace(trace.xs, self._median_window, self._smooth_window)
            ys = smooth_trace(trace.ys, self._median_window, self._smooth_window)
            zs = smooth_trace(trace.zs, self._median_window, self._smooth_window)
            self._axis.plot(xs, ys, zs, label=f"id {object_id}")
            self._axis.scatter(xs[-1], ys[-1], zs[-1], s=30)

    def _set_equal_limits(self) -> None:
        lines = self._axis.lines
        if not lines:
            return

        all_x: list[float] = []
        all_y: list[float] = []
        all_z: list[float] = []
        for line in lines:
            xs, ys, zs = line.get_data_3d()
            all_x.extend(xs)
            all_y.extend(ys)
            all_z.extend(zs)

        if not all_x:
            return

        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)
        min_z, max_z = min(all_z), max(all_z)
        dx = max(max_x - min_x, 1e-3)
        dy = max(max_y - min_y, 1e-3)
        dz = max(max_z - min_z, 1e-3)
        cx = 0.5 * (min_x + max_x)
        cy = 0.5 * (min_y + max_y)
        cz = 0.5 * (min_z + max_z)
        radius = 0.5 * max(dx, dy, dz)
        self._axis.set_xlim(cx - radius, cx + radius)
        self._axis.set_ylim(cy - radius, cy + radius)
        self._axis.set_zlim(cz - radius, cz + radius)

    def _draw(self) -> None:
        if not self.figure_open():
            return

        self._axis.clear()
        if self._use_combined_markers():
            self._plot_combined()
        else:
            self._plot_individual()

        self._axis.set_title(f"{self._topic} live spatial view")
        self._axis.set_xlabel("x [m]")
        self._axis.set_ylabel("y [m]")
        self._axis.set_zlabel("z [m]")
        self._set_equal_limits()
        if self._axis.lines:
            self._axis.legend(loc="best")

        self._figure.tight_layout()
        self._figure.canvas.draw_idle()
        self._figure.canvas.flush_events()


def parse_ids(ids_text: str) -> list[int]:
    if not ids_text.strip():
        return []
    return [int(part.strip()) for part in ids_text.split(",") if part.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Live spatial plot of filtered and smoothed x-y-z trajectories from Phasespace topics."
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
        default=0.0,
        help="History window in seconds; use 0 or less to keep the full path from t=0",
    )
    parser.add_argument(
        "--max-ids",
        type=int,
        default=8,
        help="Maximum number of unique IDs to display in per-id mode",
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
        help="Median filter window size for spike rejection in per-id mode",
    )
    parser.add_argument(
        "--smooth-window",
        type=int,
        default=9,
        help="Moving-average window size for noise reduction in per-id mode",
    )
    parser.add_argument(
        "--refresh-hz",
        type=float,
        default=4.0,
        help="Plot refresh rate in Hz",
    )
    parser.add_argument(
        "--combine-count",
        type=int,
        default=4,
        help="For marker topics, combine this many marker IDs into one fused estimate; set to 0 to disable",
    )
    parser.add_argument(
        "--combine-ids",
        type=str,
        default="",
        help="Comma-separated marker IDs to fuse, for example '0,2,4,6'; empty means auto-select the first valid IDs seen",
    )
    parser.add_argument(
        "--process-var",
        type=float,
        default=0.05,
        help="Kalman process noise variance for the fused marker estimate",
    )
    parser.add_argument(
        "--measurement-var",
        type=float,
        default=0.0025,
        help="Kalman measurement noise variance for the fused marker estimate",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rclpy.init()
    node = LiveSpatialPlotter(
        args.topic,
        args.history,
        args.max_ids,
        args.min_cond,
        args.zero_epsilon,
        args.median_window,
        args.smooth_window,
        args.refresh_hz,
        args.combine_count,
        parse_ids(args.combine_ids),
        args.process_var,
        args.measurement_var,
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
