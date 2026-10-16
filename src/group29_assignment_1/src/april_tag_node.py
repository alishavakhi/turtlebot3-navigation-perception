#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.time import Time

import tf2_ros
from geometry_msgs.msg import PoseStamped




class AprilTagNode(Node):
    def __init__(self):
        super().__init__("april_tag_node")
        self.get_logger().set_level(rclpy.logging.LoggingSeverity.ERROR)

    
        self.last_mid = None

        self.declare_parameter("target_frame", "map")
        self.declare_parameter("tag_frame_1", "tag36h11:1")
        self.declare_parameter("tag_frame_2", "tag36h11:10")

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        self.timer = self.create_timer(0.5, self.timer_callback)

        self.get_logger().info("AprilTagNode started. looking for tag frames in TF.")
        self.mid_pub = self.create_publisher(PoseStamped, "/midpoint", 10)


    def lookup_tag_pose(self, tag_frame: str) -> PoseStamped | None:
        target_frame = self.get_parameter("target_frame").get_parameter_value().string_value

        try:
            transform = self.tf_buffer.lookup_transform(
                target_frame,
                tag_frame,
                Time()
            )

            pose = PoseStamped()
            pose.header = transform.header
            pose.pose.position.x = transform.transform.translation.x
            pose.pose.position.y = transform.transform.translation.y
            pose.pose.position.z = transform.transform.translation.z
            pose.pose.orientation = transform.transform.rotation

            return pose
        except Exception as e:
            self.get_logger().debug(f"cannot get TF {target_frame} <- {tag_frame}: {e}")
            return None

    def timer_callback(self):
        tag_frame_1 = self.get_parameter("tag_frame_1").get_parameter_value().string_value
        tag_frame_2 = self.get_parameter("tag_frame_2").get_parameter_value().string_value
        target_frame = self.get_parameter("target_frame").get_parameter_value().string_value

        pose1 = self.lookup_tag_pose(tag_frame_1)
        pose2 = self.lookup_tag_pose(tag_frame_2)


        if pose1 is None or pose2 is None:
            self.get_logger().warn(" midpoint not updated.")
            self.last_mid = None
            return

        x1, y1 = pose1.pose.position.x, pose1.pose.position.y
        x2, y2 = pose2.pose.position.x, pose2.pose.position.y

        mid_x = 0.5 * (x1 + x2)
        mid_y = 0.5 * (y1 + y2)

        mid_x_r = round(mid_x, 2)
        mid_y_r = round(mid_y, 2)

        mid_str = f"{mid_x_r},{mid_y_r}"

        if self.last_mid == mid_str:
            return  

        self.last_mid = mid_str


        self.get_logger().info(f"last mindpoint {self.last_mid}")

        mid = PoseStamped()
       #mid.header.frame_id = target_frame
        mid.header.frame_id = "map"
        mid.header.stamp = self.get_clock().now().to_msg()
        mid.pose.position.x = mid_x_r
        mid.pose.position.y = mid_y_r
        mid.pose.position.z = 0.0
        mid.pose.orientation.w = 1.0  


        self.get_logger().info(

            f"{tag_frame_1} in {target_frame}: x={x1:.2f}, y={y1:.2f} | "
            f"{tag_frame_2} in {target_frame}: x={x2:.2f}, y={y2:.2f}"
            # f"midpoint: x={mid_x_r}, y={mid_y_r}"
        )

        self.mid_pub.publish(mid)
        self.get_logger().info(f"midpoint changed. new midpoint: {mid_str}")




def main(args=None):
    rclpy.init(args=args)
    node = AprilTagNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()