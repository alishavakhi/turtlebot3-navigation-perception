#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped
from nav2_msgs.action import NavigateToPose
from nav2_msgs.srv import ManageLifecycleNodes
from rclpy.action import ActionClient
import subprocess
import time
import tf2_ros
from geometry_msgs.msg import TransformStamped
from std_msgs.msg import Bool 


class NavigationNode(Node):
    
    def __init__(self):
        super().__init__("navigation_node")

        self.get_logger().set_level(rclpy.logging.LoggingSeverity.ERROR)


        self.state = "IDLE"

        self.max_retries = 3
        self.retry_count = 0
        self.current_goal_pose = None 
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

        self.last_goal = None
        self.goal_handle = None

        self.create_subscription(
            PoseStamped,
            "/midpoint",
            self.midpoint_callback,
            10
        )


        self.activate_nav2()





    def activate_nav2(self):
        self.get_logger().info("[navigation_node] waiting for Nav2...")

        self.loc_client.wait_for_service()
        self.nav_client.wait_for_service()

        req = ManageLifecycleNodes.Request()
        req.command = ManageLifecycleNodes.Request.STARTUP

        self.get_logger().info("[navigation_node] Sending STARTUP to Nav2...")
        self.loc_client.call_async(req)
        self.nav_client.call_async(req)
        
        self.get_logger().info("[navigation_node] waiting for deploy...")
        time.sleep(2.0)

        self.wait_for_nav2_ready()
        
        self.publish_initial_pose()

        self.get_logger().info("[navigation_node] waiting for AMCL...")
        time.sleep(4.0) 
        
        self.state = "WAITING_TARGET"
        self.get_logger().info("[navigation_node] ready. waiting for midpoint...")





    def wait_for_nav2_ready(self):
        self.get_logger().info("[navigation_node] waiting for bt_navigator active...")

        for _ in range(25):
            try:
                out = subprocess.check_output(
                    "ros2 lifecycle get /bt_navigator",
                    shell=True
                )
                if b"active" in out:
                    self.get_logger().info("[navigation_node] Nav2 active")
                    return
            except:
                pass
            time.sleep(1)

        self.get_logger().error("[navigation_node] Nav2 failed to activate")





    def publish_initial_pose(self):
        
        msg = PoseWithCovarianceStamped()
        msg.header.frame_id = "map"
        msg.header.stamp = self.get_clock().now().to_msg()

        msg.pose.pose.position.x = 0.0 
        msg.pose.pose.position.y = 0.0 
        msg.pose.pose.position.z = 0.0

        msg.pose.pose.orientation.x = 0.0
        msg.pose.pose.orientation.y = 0.0
        msg.pose.pose.orientation.z = 0.0
        msg.pose.pose.orientation.w = 1.0 

        msg.pose.covariance = [
            0.25, 0, 0, 0, 0, 0,
            0, 0.25, 0, 0, 0, 0,
            0, 0, 0.0, 0, 0, 0,
            0, 0, 0, 0.068, 0, 0,
            0, 0, 0, 0, 0.068, 0,
            0, 0, 0, 0, 0, 0.068
        ]

        self.get_logger().info("Initial pose published.")
        self.initial_pub.publish(msg)


    def midpoint_callback(self, msg: PoseStamped):

        if self.state in ["NAVIGATING", "RETRYING"]:
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
        
        self.get_logger().info(f"[Nav] new target received: ({x:.2f}, {y:.2f})")
        
        self.send_goal(msg)


    def send_goal(self, pose: PoseStamped):

        self.state = "NAVIGATING"

        goal = NavigateToPose.Goal()
        goal.pose.header.frame_id = pose.header.frame_id 
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        goal.pose.pose = pose.pose
        goal.pose.pose.position.z = 0.0 

        self.nav_action_client.wait_for_server()

        self.get_logger().info(f"[Nav] sending goal... (attempt {self.retry_count + 1})")

        future = self.nav_action_client.send_goal_async(
            goal,
            feedback_callback=self.feedback_callback
        )
        future.add_done_callback(self.goal_response_callback)

    def feedback_callback(self, fb):
        pos = fb.feedback.current_pose.pose.position

        self.get_logger().info(
            f"[navigation_node] Feedback x={pos.x:.2f}, y={pos.y:.2f}"
        )



    def goal_response_callback(self, future):
        self.goal_handle = future.result()

        if not self.goal_handle.accepted:
            self.get_logger().warn(f"[Nav] Goal rejected. (attempt {self.retry_count + 1}/{self.max_retries})")

            if self.retry_count < self.max_retries:
                self.retry_count += 1
                self.state = "RETRYING" 
                
                if self.retry_timer:
                    self.retry_timer.cancel()
                
                self.retry_timer = self.create_timer(1.0, self.retry_handler)
                
            else:
                self.get_logger().error("[Nav] max retries reached. giving up.")
                self.state = "WAITING_TARGET" 
            
            return

        self.get_logger().info("[Nav] Goal accepted. moving...")
        
        result_future = self.goal_handle.get_result_async()
        result_future.add_done_callback(self.goal_done_callback)

    def retry_handler(self):

        if self.retry_timer:
            self.retry_timer.cancel()
            self.retry_timer = None
        
        self.get_logger().info("[Nav] timer fired. retrying now...")
        
        if self.current_goal_pose:
            self.send_goal(self.current_goal_pose)
        else:
            self.state = "WAITING_TARGET"


    def goal_done_callback(self, future):
        result = future.result()
        status = result.status
        
        if status == 4: 
            self.get_logger().info("[Nav] Goal succeeded")
            self.last_goal = None 

            msg = Bool()
            msg.data = True
            self.completion_pub.publish(msg)
            
        else:
            self.get_logger().warn(f"[Nav] goal failed{status} ")
            self.last_goal = None

        self.state = "WAITING_TARGET"


def main(args=None):
    rclpy.init(args=args)
    node = NavigationNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()