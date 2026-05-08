#!/usr/bin/env python3

# ---
# Not used - used to record hard-coded, drop down positions
# 
# 
# ---

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

class JointRecorder(Node):
    def __init__(self):
        super().__init__('joint_recorder')
        self.create_subscription(
            JointState,
            '/joint_states',
            self.callback,
            10
        )
        self.get_logger().info("Press Ctrl+C to stop recording")

    def callback(self, msg):
        input("Move arm to position then press Enter to record...")
        self.get_logger().info("Joint positions recorded:")
        for name, pos in zip(msg.name, msg.position):
            self.get_logger().info(f"  {name}: {pos:.4f}")

def main():
    rclpy.init()
    node = JointRecorder()
    rclpy.spin(node)

def main():
    rclpy.init()
    node = JointRecorder()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()