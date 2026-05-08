#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from geometry_msgs.msg import Point
from cv_bridge import CvBridge

import cv2
import numpy as np


class ColorDetector(Node):
    def __init__(self):
        super().__init__("color_detector")

        self.bridge = CvBridge()

        # subscribes to camera
        self.subscriber = self.create_subscription(
            Image,
            "/camera/image_raw",
            self.image_callback,
            10
        )

        # publish location of item? 
        self.pub = self.create_publisher(
            Point, 
            "/color_object_position", 
            10
        )

        self.collection_seconds = 5.0 # 5 seconds to collect locations
        self.detections = [] # save all detections

        self.start_time = self.get_clock().now() 
        self.published = False

    def image_callback(self, msg):

        if self.published:
            return
        
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception as e:
            self.get_logger().error(f"Image conversion failed:{e}")

        point, display_frame, mask = self.detect_color(frame)

        cv2.imshow("Color Detector View", display_frame)
        cv2.imshow("mask", mask)
        cv2.waitKey(1)

        if point is not None:
            self.detections.append(point)

        elapsed = (self.get_clock().now() - self.start_time).nanoseconds / 1e9

        if elapsed >= self.collection_seconds:
            self.publish_best_detections()
            self.published = True

    # right now, just yellow
    def detect_color(self, frame):
        hsvImage = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # YELLOW
        lowerLimit = np.array([20, 120, 120])
        upperLimit = np.array([42, 255, 255])

        # PINK
        # lowerLimit = np.array([140, 50, 50])
        # upperLimit = np.array([170, 255, 255])

        display_frame = frame.copy()
        mask = cv2.inRange(hsvImage, lowerLimit, upperLimit)

        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        if len(contours) == 0:
            return None, display_frame, mask

        largest = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest)

        # doesn't detect too small or too large items
        # TODO: verify area dimensions
        if area < 300 or area > 100000:
            return None, display_frame, mask
        
        x, y, w, h = cv2.boundingRect(largest)

        cx = x + w / 2
        cy = y + h / 2

        cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.circle(display_frame, (int(cx), int(cy)), 5, (0, 0, 255), -1)

        return (cx, cy), display_frame, mask
        #self.get_logger().info(f"Detected, but not published, yellow position: x={cx}, y={cy}")

    def publish_best_detections(self):

        if len(self.detections) == 0:
            self.get_logger().warn("No valid detections collected.")
        
        xs = [p[0] for p in self.detections]
        ys = [p[1] for p in self.detections]

        best_x = float(np.median(xs))
        best_y = float(np.median(ys))

        msg = Point()
        msg.x = best_x
        msg.y = best_y
        msg.z = 0.0

        self.pub.publish(msg)

        self.get_logger().info(
            f"Published best color position after {self.collection_seconds} sec: "
            f"x={best_x}, y={best_y}, samples={len(self.detections)}"
        )

    def destroyNode(self):
        cv2.destroyAllWindows()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = ColorDetector()

    try:
        rclpy.spin(node)
    finally:
        node.destroyNode()
        rclpy.shutdown()


if __name__ == "__main__":
    main()