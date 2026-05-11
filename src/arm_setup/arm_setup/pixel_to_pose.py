#!/usr/bin/env python3

# ---
# Pixel to Pose ROS2 Node
# Step 3
# 
# Subscribe to a point from color detector node, which
#           identified the object in frame
# Publish point stamped, which is a coordinate of the item
#         to be picked up by the robot arm, given information on the robot,
#         to MoveArm Node, a moveit node
# ---

import rclpy
import numpy as np

from rclpy.node import Node
from geometry_msgs.msg import Point, PointStamped
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge

import tf2_ros
import tf2_geometry_msgs

TABLE_Z = -0.9 # assume table is 0.17 cm below base plane

class PixelToPose(Node):
    def __init__(self):
        super().__init__("pixel_to_pose")

        self.get_logger().info("PixelToPose node started")

        # Approximate camera, as I can't find any camera info online
        self.fx = 600.0
        self.fy = 600.0
        self.cx = 320.0
        self.cy = 240.0

        self.bridge = CvBridge()

        # Latest data holders
        self.camera_info = None
        self.target_frame = "base_link"
        self.camera_frame = "camera_link"

        self.Z = 0.14  # hard coded depth

        # Subscribers
        # subscribes to camera information;
        # subscribes to vetted pixel of yellow item 
        self.create_subscription(Point, 
                                 "/color_object_position", 
                                 self.pixel_callback, 
                                 10)

        # Publisher
        self.point_pub = self.create_publisher(
            PointStamped, 
            "/target_point", 
            10)
        
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

    def camera_info_callback(self, msg):
        self.camera_info = msg

    def pixel_callback(self, msg):

        u = msg.x
        v = msg.y

        # Pixel → 3D
        Z = self.Z
        X = (u - self.cx) * Z / self.fx
        Y = (v - self.cy) * Z / self.fy

        # Create PoseStamped
        point_cam = PointStamped()
        point_cam.header.stamp = rclpy.time.Time().to_msg()
        point_cam.header.frame_id = self.camera_frame # doesn't need cam info

        point_cam.point.x = X
        point_cam.point.y = Y
        point_cam.point.z = Z

        try:
            point_base = self.tf_buffer.transform(
                point_cam,
                self.target_frame,
                timeout=rclpy.duration.Duration(seconds=1.0)
            )

            point_base.point.z = -0.1  # table 

        except Exception as e:
            self.get_logger().error(f"TF transform failed: {e}")
            return

        self.point_pub.publish(point_base)

        self.get_logger().info(
            f"Target in base_link: "
            f"x={point_base.point.x:.3f}, "
            f"y={point_base.point.y:.3f}, "
            f"z={point_base.point.z:.3f}"
        )


def main():
    rclpy.init()
    node = PixelToPose()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()