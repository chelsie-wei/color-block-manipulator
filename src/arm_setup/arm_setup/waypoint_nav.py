#!/usr/bin/env python3

# Hardcoded turtlebot navigation
# Takes turtlebot from one side of the room to the robot arm

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
import math

WAYPOINTS = [
    {"x": -2.708914419344794, "y": 0.8628977559072915, "yaw": 0.0},  # start (across the room)
    {"x": -4.55,              "y": 2.79,               "yaw": 0.0},  # end (to robot arm, by the door)
]

class WaypointNav(Node):
    def __init__(self):
        super().__init__('waypoint_nav')
        self._client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self._index = 0
        self.get_logger().info('Waiting for Nav2...')
        self._client.wait_for_server()
        self.get_logger().info('Starting navigation')
        self.go_to_next()

    def go_to_next(self):
        if self._index >= len(WAYPOINTS):
            self.get_logger().info('Reached destination!')
            return

        wp = WAYPOINTS[self._index]
        goal = NavigateToPose.Goal()
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = wp['x']
        pose.pose.position.y = wp['y']
        pose.pose.orientation.z = math.sin(wp['yaw'] / 2)
        pose.pose.orientation.w = math.cos(wp['yaw'] / 2)
        goal.pose = pose

        self.get_logger().info(f"Going to waypoint {self._index}: x={wp['x']}, y={wp['y']}")
        future = self._client.send_goal_async(goal)
        future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected!')
            return
        goal_handle.get_result_async().add_done_callback(self.result_callback)

    def result_callback(self, future):
        self.get_logger().info(f'Waypoint {self._index} reached!')
        self._index += 1
        self.go_to_next()

def main():
    rclpy.init()
    rclpy.spin(WaypointNav())

if __name__ == '__main__':
    main()