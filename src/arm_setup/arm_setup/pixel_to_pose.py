#!/usr/bin/env python3

import rclpy
import numpy as np

from rclpy.node import Node
from geometry_msgs.msg import Point, PointStamped
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge

import tf2_ros
import tf2_geometry_msgs

TABLE_Z = 0.01 # assume table is 2 cm above base plane
# grasp_z = TABLE_Z + 0.04 # 4 cm 

class PixelToPose(Node):
    def __init__(self):
        super().__init__("pixel_to_pose")

        self.get_logger().info("PixelToPose node started")

        self.fx = 600.0
        self.fy = 600.0
        self.cx = 320.0
        self.cy = 240.0

        self.bridge = CvBridge()

        # Latest data holders
        # self.depth_image = None
        self.camera_info = None

        self.target_frame = "base_link"
        # self.camera_frame = "camera_color_optical_frame"
        self.camera_frame = "camera_link"

        self.Z = 0.14  # approximate distance from camera to table

        # Subscribers
        # subscribes to camera information;
        # subscribes to vetted pixel of yellow item 
        self.create_subscription(Point, 
                                 "/color_object_position", 
                                 self.pixel_callback, 
                                 10)

        # self.create_subscription(CameraInfo, 
        #                          "/camera/color/camera_info", 
        #                          self.camera_info_callback, 
        #                          10)

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

        # if self.camera_info is None:
        #     self.get_logger().warn("Waiting for camera info...")
        #     return

        u = msg.x
        v = msg.y

        # Camera intrinsics
        # K = self.camera_info.k

        # fx = K[0]
        # fy = K[4]
        # cx = K[2]
        # cy = K[5]

        Z = self.Z

        # Pixel → 3D
        # X = (u - cx) * self.Z / fx
        # Y = (v - cy) * self.Z / fy
        X = (u - self.cx) * Z / self.fx
        Y = (v - self.cy) * Z / self.fy

        # Create PoseStamped
        point_cam = PointStamped()
        # point_cam.header.frame_id = self.camera_info.header.frame_id
        #point_cam.header.stamp = self.get_clock().now().to_msg()
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

            point_base.point.z = 0.15

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