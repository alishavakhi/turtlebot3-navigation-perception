#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import PointStamped
from std_msgs.msg import Bool
from visualization_msgs.msg import Marker

import math
import tf2_ros
import tf2_geometry_msgs
from tf2_ros import LookupException, ConnectivityException, ExtrapolationException

class TableDetector(Node):
    def __init__(self):
        super().__init__("table_detector")

        
        self.nav_completed = False
        self.detected = False
        self.started = False

        
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

       
        self.create_subscription(Bool, "/navigation_completed", self.completion_callback, 10)
        self.create_subscription(LaserScan, "/scan", self.scan_callback, 10)

        
        self.table_pub = self.create_publisher(PointStamped, "/tables", 10)
        
        self.marker_pub = self.create_publisher(Marker, "/table_markers", 10)

        self.get_logger().info("TableDetector started. Waiting for navigation completion...")

    def completion_callback(self, msg: Bool):
        
        if msg.data is True and not self.nav_completed:
            self.get_logger().info("Navigation completion signal received. Detector activated.")
            self.nav_completed = True

    def publish_marker(self, x, y, table_id):
        marker = Marker()
        marker.header.frame_id = "map"  
        marker.header.stamp = self.get_clock().now().to_msg()

        marker.ns = "tables"
        marker.id = table_id
        marker.type = Marker.CYLINDER
        marker.action = Marker.ADD

        marker.pose.position.x = x
        marker.pose.position.y = y
        marker.pose.position.z = 0.25  

        marker.scale.x = 0.4   
        marker.scale.y = 0.4
        marker.scale.z = 0.5  

        
        marker.color.a = 1.0
        if table_id == 1:
            marker.color.r, marker.color.g, marker.color.b = 0.0, 0.2, 1.0 
        elif table_id == 2:
            marker.color.r, marker.color.g, marker.color.b = 0.0, 1.0, 0.0 
        else:
            marker.color.r, marker.color.g, marker.color.b = 1.0, 0.0, 0.0 

        self.marker_pub.publish(marker)

    def scan_callback(self, scan: LaserScan):
        if self.detected or not self.nav_completed:
            return

        if not self.started:
            self.get_logger().info("Starting detection logic...")
            self.started = True

        points = []
        angle = scan.angle_min
        for r in scan.ranges:
            if scan.range_min < r < scan.range_max:
                x = r * math.cos(angle)
                y = r * math.sin(angle)
                points.append((x, y))
            angle += scan.angle_increment

        if not points:
            return

        
        clusters = []
        current_cluster = []
        
        CLUSTER_THRESHOLD = 0.4 

        for p in points:
            if not current_cluster:
                current_cluster.append(p)
            else:
                last_p = current_cluster[-1]
                dist = math.hypot(p[0] - last_p[0], p[1] - last_p[1])
                if dist < CLUSTER_THRESHOLD:
                    current_cluster.append(p)
                else:
                    if len(current_cluster) >= 3: 
                        clusters.append(current_cluster)
                    current_cluster = [p]
        
        if len(current_cluster) >= 3:
            clusters.append(current_cluster)

        tables_found = 0
        
        try:
            transform = self.tf_buffer.lookup_transform("map", "base_scan", rclpy.time.Time())
        except Exception as e:
            self.get_logger().warn(f"TF Error: {e}")
            return

        detected_positions = []

        for cluster in clusters:
            p_start = cluster[0]
            p_end = cluster[-1]
            width = math.hypot(p_start[0] - p_end[0], p_start[1] - p_end[1])

       
            MIN_WIDTH = 0.05
            MAX_WIDTH = 0.45 

            if width > MAX_WIDTH or width < MIN_WIDTH:
                
                continue 

            
            cx = sum(p[0] for p in cluster) / len(cluster)
            cy = sum(p[1] for p in cluster) / len(cluster)

            
            is_duplicate = False
            for (dx, dy) in detected_positions:
                if math.hypot(cx - dx, cy - dy) < 0.5:
                    is_duplicate = True
                    break
            
            if is_duplicate:
                continue

            detected_positions.append((cx, cy))

            
            point = PointStamped()
            point.header.frame_id = "base_scan"
            point.header.stamp = self.get_clock().now().to_msg()
            point.point.x = cx
            point.point.y = cy
            point.point.z = 0.0

            point_transformed = tf2_geometry_msgs.do_transform_point(point, transform)
            tables_found += 1
            
            self.table_pub.publish(point_transformed)
            self.publish_marker(point_transformed.point.x, point_transformed.point.y, tables_found)

            self.get_logger().info(
                f"Table {tables_found} detected! Width of table: {width:.2f}m at map pose: "
                f"({point_transformed.point.x:.2f}, {point_transformed.point.y:.2f})"
            )

            if tables_found >= 3:
                break

        if tables_found >= 3:
            self.detected = True
            self.get_logger().info("SUCCESS: All 3 tables found.")
def main(args=None):
    rclpy.init(args=args)
    node = TableDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()