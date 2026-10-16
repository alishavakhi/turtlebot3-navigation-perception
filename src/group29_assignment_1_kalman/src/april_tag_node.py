#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import tf2_ros
from geometry_msgs.msg import PoseStamped, Quaternion
import numpy as np


class AprilTagNode(Node):
    def __init__(self):
        super().__init__("april_tag_node")
        self.get_logger().set_level(rclpy.logging.LoggingSeverity.ERROR)


        self.last_midpoint = None
        self.midpoint_tolerance = 0.07  
        self.declare_parameter("target_frame", "map")
        self.declare_parameter("tag_frame_1", "tag36h11:1")
        self.declare_parameter("tag_frame_2", "tag36h11:10")
        self.target_frame = self.get_parameter("target_frame").value
        self.tag_frame_1 = self.get_parameter("tag_frame_1").value
        self.tag_frame_2 = self.get_parameter("tag_frame_2").value

        self.dt = 0.1
        self.initialized = False
        self.initialize_kalman_filter()
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        self.midpoint_pub = self.create_publisher(PoseStamped, "/midpoint", 10)
        self.timer = self.create_timer(self.dt, self.timer_callback)

    def initialize_kalman_filter(self):

        self.x_hat = np.zeros((4, 1))
        self.F = np.eye(4)
        self.F[0, 2] = self.dt
        self.F[1, 3] = self.dt

        self.H = np.array([[1, 0, 0, 0],
                           [0, 1, 0, 0]])


        self.P = np.eye(4) * 1.0
        self.R = np.eye(2) * 15.0   
        self.Q = np.eye(4) * 0.0001   


    def kalman_predict(self):
        self.x_hat = self.F @ self.x_hat
        self.P = self.F @ self.P @ self.F.T + self.Q


    def kalman_update(self, z):
        y = z - (self.H @ self.x_hat)
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)
        self.x_hat = self.x_hat + K @ y
        self.P = (np.eye(4) - K @ self.H) @ self.P



    def get_tag_pos(self, tag_frame):
        try:
            t = self.tf_buffer.lookup_transform(
                self.target_frame,
                tag_frame,
                rclpy.time.Time()
            )
            return t.transform.translation.x, t.transform.translation.y
        except:
            return None, None


    def midpoint_changed(self, x, y):
        if self.last_midpoint is None:
            return True
        dx = abs(x - self.last_midpoint[0])
        dy = abs(y - self.last_midpoint[1])
        return (dx > self.midpoint_tolerance) or (dy > self.midpoint_tolerance)


    def timer_callback(self):
        x1, y1 = self.get_tag_pos(self.tag_frame_1)
        x2, y2 = self.get_tag_pos(self.tag_frame_2)

        if x1 is None or x2 is None:
            return

        mx = (x1 + x2) / 2.0
        my = (y1 + y2) / 2.0


        z = np.array([[mx], [my]])

 
        if not self.initialized:
            
            self.x_hat = np.array([[mx],
                                   [my],
                                   [0.0],
                                   [0.0]])
            self.initialized = True
        else:
            self.kalman_predict()
            self.kalman_update(z)

        final_x = float(self.x_hat[0, 0])
        final_y = float(self.x_hat[1, 0])

        if not self.midpoint_changed(final_x, final_y):
            return

        self.last_midpoint = (final_x, final_y)

        msg = PoseStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.target_frame
        msg.pose.position.x = final_x
        msg.pose.position.y = final_y
        msg.pose.orientation = Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)

        self.midpoint_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = AprilTagNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
