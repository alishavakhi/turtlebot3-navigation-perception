#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped
from nav2_msgs.action import NavigateToPose
from nav2_msgs.srv import ManageLifecycleNodes
from rclpy.action import ActionClient
import subprocess
import time
from std_msgs.msg import Bool


class NavigationNode(Node):
    def __init__(self):
        super().__init__("navigation_node")
        self.get_logger().set_level(rclpy.logging.LoggingSeverity.INFO)

        self.state = "IDLE"
        self.is_transitioning_lock = False
        self.transition_timer = None
        self.TRANSITION_DURATION = 1.0

        self.max_retries = 3
        self.retry_count = 0
        self.current_goal_pose = None
        self.last_goal = None
        self.goal_handle = None
        self.retry_timer = None

        self.loc_client = self.create_client(
            ManageLifecycleNodes,
            "/lifecycle_manager_localization/manage_nodes"
        )
        self.nav_client = self.create_client(
            ManageLifecycleNodes,
            "/lifecycle_manager_navigation/manage_nodes"
        )

        self.initial_pub = self.create_publisher(
            PoseWithCovarianceStamped,
            "/initialpose",
            10
        )

        self.completion_pub = self.create_publisher(
            Bool,
            "/navigation_completed",
            10
        )

        self.nav_action_client = ActionClient(
            self, NavigateToPose, "/navigate_to_pose"
        )

        self.create_subscription(
            PoseStamped,
            "/midpoint",
            self.midpoint_callback,
            10
        )

        self.create_subscription(
            Bool,
            "/corridor_status",
            self.corridor_status_callback,
            10
        )

        self.activate_nav2()

    def activate_nav2(self):
        self.get_logger().info("[Nav] Initializing Nav2...")
        self.loc_client.wait_for_service()
        self.nav_client.wait_for_service()

        req = ManageLifecycleNodes.Request()
        req.command = ManageLifecycleNodes.Request.STARTUP

        self.loc_client.call_async(req)
        self.nav_client.call_async(req)

        time.sleep(2.0)
        self.wait_for_nav2_ready()

        self.publish_initial_pose()
        time.sleep(3.0)

        self.state = "WAITING_TARGET"
        self.get_logger().info("[Nav] Ready. Waiting for midpoint...")

    def wait_for_nav2_ready(self):
        self.get_logger().info("[Nav] Waiting for bt_navigator active...")
        for _ in range(25):
            try:
                out = subprocess.check_output(
                    "ros2 lifecycle get /bt_navigator",
                    shell=True
                )
                if b"active" in out:
                    self.get_logger().info("[Nav] bt_navigator ACTIVE")
                    return
            except Exception:
                pass
            time.sleep(1)
        self.get_logger().error("[Nav] Nav2 failed to activate")

    def publish_initial_pose(self):
        msg = PoseWithCovarianceStamped()
        msg.header.frame_id = "map"
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.pose.pose.orientation.w = 1.0

        msg.pose.covariance = [
            0.25, 0, 0, 0, 0, 0,
            0, 0.25, 0, 0, 0, 0,
            0, 0, 0.0, 0, 0, 0,
            0, 0, 0, 0.068, 0, 0,
            0, 0, 0, 0, 0.068, 0,
            0, 0, 0, 0, 0, 0.068
        ]

        self.initial_pub.publish(msg)
        self.get_logger().info("[Nav] Initial pose published.")

    def midpoint_callback(self, msg: PoseStamped):
        if self.state in ["NAVIGATING", "RETRYING", "MANUAL_CONTROL"] or self.is_transitioning_lock:
            return

        x = msg.pose.position.x
        y = msg.pose.position.y

        if self.last_goal:
            lx, ly = self.last_goal
            if abs(x - lx) < 0.05 and abs(y - ly) < 0.05:
                return

        self.last_goal = (x, y)
        self.current_goal_pose = msg
        self.retry_count = 0

        self.send_goal(msg)

    def send_goal(self, pose: PoseStamped):
        if pose is None:
            return

        self.state = "NAVIGATING"
        goal = NavigateToPose.Goal()
        goal.pose.header.frame_id = pose.header.frame_id
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        goal.pose.pose = pose.pose

        self.nav_action_client.wait_for_server()
        future = self.nav_action_client.send_goal_async(
            goal,
            feedback_callback=self.feedback_callback
        )
        future.add_done_callback(self.goal_response_callback)

    def feedback_callback(self, fb):
        pass

    def goal_response_callback(self, future):
        self.goal_handle = future.result()

        if not self.goal_handle.accepted:
            if self.retry_count < self.max_retries:
                self.retry_count += 1
                self.state = "RETRYING"
                self.retry_timer = self.create_timer(1.0, self.retry_handler)
            else:
                self.state = "WAITING_TARGET"
            return

        result_future = self.goal_handle.get_result_async()
        result_future.add_done_callback(self.goal_done_callback)

    def retry_handler(self):
        if self.retry_timer:
            self.retry_timer.cancel()
        self.send_goal(self.current_goal_pose)

    def goal_done_callback(self, future):
        result = future.result()
        status = result.status

        if status == 2:
            self.goal_handle = None
            return

        if status == 4:
            self.completion_pub.publish(Bool(data=True))
            self.current_goal_pose = None
            self.last_goal = None

        self.goal_handle = None
        self.state = "WAITING_TARGET"

    def corridor_status_callback(self, msg: Bool):
        if msg.data is True:
            self.get_logger().warn("[Nav] CORRIDOR DETECTED → FULL STOP")

            if self.goal_handle:
                cancel_future = self.goal_handle.cancel_goal_async()
                cancel_future.add_done_callback(lambda _: None)
            self.goal_handle = None

            req = ManageLifecycleNodes.Request()
            req.command = ManageLifecycleNodes.Request.PAUSE
            self.nav_client.call_async(req)

            self.state = "MANUAL_CONTROL"
            self.is_transitioning_lock = True
            self.transition_timer = self.create_timer(
                self.TRANSITION_DURATION,
                self.clear_transition_lock
            )
            return

        if msg.data is False:
            self.get_logger().warn("[Nav] EXIT CORRIDOR → RESUME")

            req = ManageLifecycleNodes.Request()
            req.command = ManageLifecycleNodes.Request.RESUME
            self.nav_client.call_async(req)

            self.is_transitioning_lock = False
            if self.transition_timer:
                self.transition_timer.cancel()
                self.transition_timer = None

            if self.current_goal_pose:
                self.create_timer(1.0, lambda: self.send_goal(self.current_goal_pose))
                self.state = "NAVIGATING"
            else:
                self.state = "WAITING_TARGET"

    def clear_transition_lock(self):
        self.is_transitioning_lock = False
        if self.transition_timer:
            self.transition_timer.cancel()
            self.transition_timer = None


def main(args=None):
    rclpy.init(args=args)
    node = NavigationNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
