import time
from enum import Enum, auto
from typing import TYPE_CHECKING

from ..flight_test.flight_state import FlightState
from ..flight_test.handlers.handler import FlightStateHandler
from . import navigator

if TYPE_CHECKING:
    from .goto_target_node import GotoTargetNode


class Phase(Enum):
    CLIMB = auto()
    SETTLE = auto()
    NAVIGATE = auto()
    CONFIRM = auto()


class GotoHandler(FlightStateHandler):
    CLIMB_TIMEOUT = 30.0
    SETTLE_TIME = 3.0
    NAVIGATE_TIMEOUT = 90.0
    CONFIRM_TIME = 2.0
    MAX_RETRIES = 3
    CLIMB_MARGIN = 0.15
    LOG_PERIOD = 1.0
    ALTITUDE_LOSS = 1.0

    def __init__(self):
        self.phase = Phase.CLIMB
        self.phase_started = None
        self.retries = 0
        self.last_log = 0.0

    def handle(self, node: "GotoTargetNode") -> None:
        if node.status is None or not node.status.armed:
            node.fail("Drone disarmed unexpectedly during flight")
            return

        if node.odometry is None:
            return

        now = time.monotonic()
        if self.phase_started is None:
            self.phase_started = now

        position = node.position()
        elapsed = now - self.phase_started

        # Різка втрата висоти після зльоту означає удар або падіння: далі летіти немає сенсу
        if self.phase != Phase.CLIMB and position[2] < node.start_z + node.TAKEOFF_ALTITUDE - self.ALTITUDE_LOSS:
            node.fail(f"Altitude lost ({position[2]:.2f} m), probable collision at ({position[0]:.2f}, {position[1]:.2f})")
            return

        if self.phase == Phase.CLIMB:
            self.climb(node, position, elapsed)
        elif self.phase == Phase.SETTLE:
            self.settle(node, elapsed)
        elif self.phase == Phase.NAVIGATE:
            self.navigate(node, position, elapsed)
        elif self.phase == Phase.CONFIRM:
            self.confirm(node, position, elapsed)

    def enter(self, node, phase: Phase, message: str) -> None:
        self.phase = phase
        self.phase_started = time.monotonic()
        node.get_logger().info(message)

    def climb(self, node, position, elapsed) -> None:
        goal_z = node.start_z + node.TAKEOFF_ALTITUDE
        if position[2] >= goal_z - self.CLIMB_MARGIN:
            self.enter(node, Phase.SETTLE, f"Altitude reached ({position[2]:.2f} m), stabilizing")
        elif elapsed > self.CLIMB_TIMEOUT:
            node.fail(f"Takeoff altitude not reached in {self.CLIMB_TIMEOUT:.0f} s")

    def settle(self, node, elapsed) -> None:
        node.send_velocity(0.0, 0.0)
        if elapsed >= self.SETTLE_TIME:
            self.enter(
                node,
                Phase.NAVIGATE,
                f"Flying to target ({node.target_xy[0]:.2f}, {node.target_xy[1]:.2f})",
            )

    def navigate(self, node, position, elapsed) -> None:
        distance, _ = navigator.distance_and_direction(position[:2], node.target_xy)

        if distance <= node.tolerance:
            self.enter(node, Phase.CONFIRM, f"Within tolerance ({distance:.2f} m), holding")
            return

        if elapsed > self.NAVIGATE_TIMEOUT:
            node.fail(f"Target not reached in {self.NAVIGATE_TIMEOUT:.0f} s, distance {distance:.2f} m")
            return

        vx, vy = navigator.velocity_command(position[:2], node.target_xy, node.kp, node.max_speed)
        node.send_velocity(vx, vy)
        self.log_progress(node, position, distance)

    def confirm(self, node, position, elapsed) -> None:
        node.send_velocity(0.0, 0.0)
        if elapsed < self.CONFIRM_TIME:
            return

        error = navigator.position_error(position[:2], node.target_xy)
        if error <= node.tolerance:
            node.record_result(position)
            node.state = FlightState.LANDING
            return

        self.retries += 1
        if self.retries > self.MAX_RETRIES:
            node.fail(f"Could not settle within tolerance, error {error:.2f} m")
            return
        self.enter(node, Phase.NAVIGATE, f"Drifted to {error:.2f} m, correcting (try {self.retries})")

    def log_progress(self, node, position, distance) -> None:
        now = time.monotonic()
        if now - self.last_log >= self.LOG_PERIOD:
            self.last_log = now
            node.get_logger().info(
                f"Position ({position[0]:.2f}, {position[1]:.2f}), distance to target {distance:.2f} m"
            )
