#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import cv2
from cv_bridge import CvBridge
from sensor_msgs.msg import Image


class CameraPublisher(Node):
    def __init__(self):
        super().__init__("camera_publisher")

        self.publisher = self.create_publisher(
            Image,
            "/camera/image_raw",
            10
        )

        self.bridge = CvBridge()
        self.cap = cv2.VideoCapture(0)
        self.timer = self.create_timer(0.033, self.publish_frame)

    def publish_frame(self):
        ret, frame = self.cap.read()

        msg = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")

        self.publisher.publish(msg)

    def destroy_node(self):
        if self.cap.isOpened():
            self.cap.release()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)

    node = CameraPublisher()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()