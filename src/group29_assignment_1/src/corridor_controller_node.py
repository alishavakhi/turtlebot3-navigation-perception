#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool
import numpy as np

class CorridorControllerNode(Node):
    def __init__(self):
        super().__init__("corridor_controller_node")

        self.CORRIDOR_THRESHOLD = 0.55
        self.EXIT_MULTIPLIER = 1.5
        self.FRONT_CLEARANCE = 0.45
        self.LINEAR_SPEED = 0.35
        self.KP_ANGULAR = -0.05

        self.in_corridor = False

        self.corridor_pub = self.create_publisher(Bool, "/corridor_status", 10)
        self.cmd_vel_pub = self.create_publisher(Twist, "/cmd_vel", 10)

        self.create_subscription(LaserScan, "/scan", self.scan_callback, 10)

    def safe_range(self, ranges, index):
        if 0 <= index < len(ranges):
            v = ranges[index]
            return v if np.isfinite(v) else 10.0
        return 10.0

    def scan_callback(self, msg: LaserScan):
        ranges = np.array(msg.ranges)
        inc = msg.angle_increment
        angles = np.arange(len(ranges)) * inc

        def mean_range(deg_min, deg_max):
            m = (angles >= np.deg2rad(deg_min)) & (angles <= np.deg2rad(deg_max))
            v = ranges[m]
            v = v[np.isfinite(v)]
            return np.mean(v) if len(v) > 0 else 10.0

        front = self.safe_range(ranges, int(np.deg2rad(0) / inc))
        left  = mean_range(85, 95)
        right = mean_range(265, 275)

        enter = left < self.CORRIDOR_THRESHOLD and right < self.CORRIDOR_THRESHOLD
        exit  = left > self.CORRIDOR_THRESHOLD * self.EXIT_MULTIPLIER or \
                right > self.CORRIDOR_THRESHOLD * self.EXIT_MULTIPLIER

        if enter and not self.in_corridor:
            self.in_corridor = True
            self.publish_status(True)

        elif exit and self.in_corridor:
            self.in_corridor = False
            self.publish_twist(0.0, 0.0)
            self.publish_status(False)

        if self.in_corridor:
            t = Twist()
            t.linear.x = self.LINEAR_SPEED if front > self.FRONT_CLEARANCE else 0.0
            t.angular.z = (right - left) * self.KP_ANGULAR
            self.cmd_vel_pub.publish(t)

    def publish_status(self, s):
        msg = Bool()
        msg.data = s
        self.corridor_pub.publish(msg)

    def publish_twist(self, x, z):
        t = Twist()
        t.linear.x = x
        t.angular.z = z
        self.cmd_vel_pub.publish(t)

def main(args=None):
    rclpy.init(args=args)
    node = CorridorControllerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
