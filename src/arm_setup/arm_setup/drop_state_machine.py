#!/usr/bin/env python3

# ---
# State machine
# high level control and planning of program
# 
# subscribes to signal from the moveit! node (move_arm_node)
# and tells the arm to drop off the item at a hard-coded location
# ---
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from std_msgs.msg import Bool
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
from enum import Enum, auto

# in a complete program, there will be multiple colored letter blocks that need
# to be placed, so there will be many 'drop' joint states.
# for the sake of this project, there is only one drop joint state 
# as only one block is used.

DROP_JOINTS = [
    -0.12535522878170013,  
    -3.499516626397604,  
    -2.289940420781271,
    -1.0246430796435853,
    -4.658699814473287, 
     0.19780530035495758,
]
WAIT_SEC = 5.0
JOINT_NAMES = [
    'elbow_joint',
    'shoulder_lift_joint',
    'shoulder_pan_joint',
    'wrist_1_joint',
    'wrist_2_joint',
    'wrist_3_joint',
]

class State(Enum):
    IDLE = auto()
    BUSY = auto()

class DropStateMachine(Node):
    def __init__(self):
        super().__init__("drop_state_machine")

        self.state = State.IDLE # default idle state

        # wait for signal that item is picked up
        self.create_subscription(
            Bool, 
            '/move_complete', 
            self.move_complete_callback, 
            10)
        
        self.trajectory_client = ActionClient(
            self,
            FollowJointTrajectory,
            '/scaled_joint_trajectory_controller/follow_joint_trajectory'
        )

        self.get_logger().info("State machine ready, waiting for planning & execution...")

    def move_complete_callback(self, msg):
        if not msg.data or self.state != State.IDLE:
            return
        
        self.state = State.BUSY
        self.get_logger().info(f"Move complete, waiting {WAIT_SEC}s then going to drop")
        self._wait_timer = self.create_timer(WAIT_SEC, self.go_to_drop)

    def go_to_drop(self):
        self._wait_timer.cancel()
        self.send_joint_goal(DROP_JOINTS, on_done=self.done)

    def done(self):
        self.get_logger().info("Drop joint motion complete")
        self.state = State.IDLE

    def send_joint_goal(self, joint_positions, on_done):
        goal = FollowJointTrajectory.Goal()
        trajectory = JointTrajectory()
        trajectory.joint_names = JOINT_NAMES
        point = JointTrajectoryPoint()
        point.positions = joint_positions
        point.time_from_start = Duration(sec=3, nanosec=0)
        trajectory.points.append(point)
        goal.trajectory = trajectory
        self.trajectory_client.wait_for_server()
        future = self.trajectory_client.send_goal_async(goal)
        future.add_done_callback(lambda f: self._on_goal_response(f, on_done))

    def _on_goal_response(self, future, on_done):

        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().error("Joint goal rejected, returning to IDLE")
            self.state = State.IDLE
            return
        
        goal_handle.get_result_async().add_done_callback(lambda f: on_done())

def main(args=None):
    rclpy.init(args=args)
    node = DropStateMachine()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()