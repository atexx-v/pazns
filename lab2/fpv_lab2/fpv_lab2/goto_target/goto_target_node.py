import json
import time

from geometry_msgs.msg import TwistStamped
from rclpy.parameter import Parameter

from ..flight_test.flight_state import FlightState
from ..flight_test.flight_test_node import FlightTestNode
from ..flight_test.handlers import HANDLERS
from . import navigator
from .goto_handler import GotoHandler


class GotoTargetNode(FlightTestNode):
    TRAJECTORY_PERIOD = 0.1

    def __init__(self):
        super().__init__()

        self.declare_parameter("delta_x", Parameter.Type.DOUBLE)
        self.declare_parameter("delta_y", Parameter.Type.DOUBLE)
        self.declare_parameter("frame_sign", 1.0)
        self.declare_parameter("tolerance", 0.25)
        self.declare_parameter("kp", 0.8)
        self.declare_parameter("max_speed", 2.0)
        self.declare_parameter("trajectory_file", "")
        self.declare_parameter("result_file", "")

        self.delta_x = self.get_parameter("delta_x").value
        self.delta_y = self.get_parameter("delta_y").value
        if self.delta_x is None or self.delta_y is None:
            raise ValueError(
                "Задайте delta_x і delta_y свого варіанта (таблиця 2.3), "
                "наприклад: --ros-args -p delta_x:=7.0 -p delta_y:=-0.1"
            )

        # +1: як у /odometry, -1: осі x і y дзеркально (інакше ціль варіанта потрапляє в стіну)
        self.frame_sign = self.get_parameter("frame_sign").value
        self.tolerance = self.get_parameter("tolerance").value
        self.kp = self.get_parameter("kp").value
        self.max_speed = self.get_parameter("max_speed").value
        self.result_file = self.get_parameter("result_file").value

        self.start_xy = None
        self.start_z = None
        self.target_xy = None
        self.result = None
        self.last_trajectory_time = 0.0
        self.trajectory = None

        trajectory_file = self.get_parameter("trajectory_file").value
        if trajectory_file:
            self.trajectory = open(trajectory_file, "w")
            self.trajectory.write("t,x,y,z,x_odom,y_odom\n")
        self.t0 = time.monotonic()

        self.cmd_vel_publisher = self.create_publisher(TwistStamped, "/ap/v1/cmd_vel", 10)

        self._handlers = {**HANDLERS, FlightState.HOVERING: GotoHandler()}

    def odometry_callback(self, message):
        super().odometry_callback(message)
        position = message.pose.pose.position

        # перше повідомлення приходить, поки дрон ще на землі
        if self.start_xy is None:
            self.start_xy = (self.frame_sign * position.x, self.frame_sign * position.y)
            self.start_z = position.z
            self.target_xy = navigator.target_from_variant(self.start_xy, self.delta_x, self.delta_y)
            self.get_logger().info(
                f"Start ({self.start_xy[0]:.2f}, {self.start_xy[1]:.2f}), "
                f"offset ({self.delta_x}, {self.delta_y}), "
                f"target ({self.target_xy[0]:.2f}, {self.target_xy[1]:.2f}), "
                f"tolerance {self.tolerance} m"
            )

        self.write_trajectory(position)

    def position(self):
        position = self.odometry.pose.pose.position
        return (self.frame_sign * position.x, self.frame_sign * position.y, position.z)

    def send_velocity(self, vx, vy):
        message = TwistStamped()
        message.header.frame_id = "map"  # ArduPilot читає map як ENU
        message.header.stamp = self.get_clock().now().to_msg()
        message.twist.linear.x = float(self.frame_sign * vx)
        message.twist.linear.y = float(self.frame_sign * vy)
        self.cmd_vel_publisher.publish(message)

    def write_trajectory(self, position):
        now = time.monotonic()
        if self.trajectory is None or now - self.last_trajectory_time < self.TRAJECTORY_PERIOD:
            return
        self.last_trajectory_time = now
        self.trajectory.write(
            f"{now - self.t0:.2f},{self.frame_sign * position.x:.3f},{self.frame_sign * position.y:.3f},"
            f"{position.z:.3f},{position.x:.3f},{position.y:.3f}\n"
        )

    def record_result(self, position):
        error = navigator.position_error(position[:2], self.target_xy)
        self.result = {
            "start": list(self.start_xy),
            "target": list(self.target_xy),
            "before_landing": [position[0], position[1]],
            "error_m": error,
            "tolerance_m": self.tolerance,
        }
        self.get_logger().info(f"RESULT start:          ({self.start_xy[0]:.3f}, {self.start_xy[1]:.3f})")
        self.get_logger().info(f"RESULT target:         ({self.target_xy[0]:.3f}, {self.target_xy[1]:.3f})")
        self.get_logger().info(f"RESULT before landing: ({position[0]:.3f}, {position[1]:.3f})")
        self.get_logger().info(f"RESULT error:          {error:.3f} m (tolerance {self.tolerance} m)")

    def log_summary(self):
        if self.result is None or self.odometry is None:
            return
        landed = self.position()
        self.result["landed"] = [landed[0], landed[1]]
        self.result["landed_error_m"] = navigator.position_error(landed[:2], self.target_xy)
        self.get_logger().info(
            f"RESULT landed at:      ({landed[0]:.3f}, {landed[1]:.3f}), "
            f"error {self.result['landed_error_m']:.3f} m"
        )
        if self.result_file:
            with open(self.result_file, "w") as file:
                json.dump(self.result, file, indent=2)

    def destroy_node(self):
        if self.trajectory is not None:
            self.trajectory.close()
        super().destroy_node()
