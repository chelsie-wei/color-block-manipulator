#!/usr/bin/env python3

import time
import threading

import rclpy
from rclpy.node import Node

import smach
from smach_ros import IntrospectionServer

from geometry_msgs.msg import PointStamped
from std_msgs.msg import String


WAIT_AT_PICK_SECONDS = 3.0


class Idle(smach.State):
    def __init__(self, node):
        smach.State.__init__(
            self,
            outcomes=["target_received"],
            output_keys=["target"]
        )

        self.node = node
        self.target = None

        self.node.create_subscription(
            PointStamped,
            "/target_point",   # from pixel_to_pose
            self.target_callback,
            10
        )

    def target_callback(self, msg):
        if self.target is None:
            self.target = msg
            self.node.get_logger().info(
                f"SMACH received target: "
                f"x={msg.point.x:.3f}, "
                f"y={msg.point.y:.3f}, "
                f"z={msg.point.z:.3f}"
            )

    def execute(self, userdata):
        self.node.get_logger().info("IDLE: Waiting for /target_point...")
        self.target = None

        while rclpy.ok():
            rclpy.spin_once(self.node, timeout_sec=0.1)

            if self.target is not None:
                userdata.target = self.target
                return "target_received"


class MoveToPick(smach.State):
    def __init__(self, node):
        smach.State.__init__(
            self,
            outcomes=["success", "failed"],
            input_keys=["target"]
        )

        self.node = node
        self.status = None

        self.pick_pub = self.node.create_publisher(
            PointStamped,
            "/pick_goal",      # to move_arm_node
            10
        )

        self.node.create_subscription(
            String,
            "/move_status",    # from move_arm_node
            self.status_callback,
            10
        )

    def status_callback(self, msg):
        self.status = msg.data

    def execute(self, userdata):
        self.node.get_logger().info("MOVE_TO_PICK: Publishing /pick_goal...")
        self.status = None

        self.pick_pub.publish(userdata.target)

        while rclpy.ok():
            rclpy.spin_once(self.node, timeout_sec=0.1)

            if self.status == "success":
                self.node.get_logger().info("MOVE_TO_PICK: Move succeeded")
                return "success"

            if self.status == "failed":
                self.node.get_logger().error("MOVE_TO_PICK: Move failed")
                return "failed"


class WaitAtPick(smach.State):
    def __init__(self, node):
        smach.State.__init__(self, outcomes=["done"])
        self.node = node

    def execute(self, userdata):
        self.node.get_logger().info(
            f"WAIT_AT_PICK: Waiting {WAIT_AT_PICK_SECONDS} seconds..."
        )

        start = time.time()

        while rclpy.ok() and time.time() - start < WAIT_AT_PICK_SECONDS:
            rclpy.spin_once(self.node, timeout_sec=0.1)

        return "done"


class DoneState(smach.State):
    def __init__(self, node):
        smach.State.__init__(self, outcomes=["done"])
        self.node = node

    def execute(self, userdata):
        self.node.get_logger().info("DONE: Pick sequence complete.")
        return "done"


def main(args=None):
    rclpy.init(args=args)

    node = Node("arm_state_machine")

    sm = smach.StateMachine(outcomes=["DONE", "FAILED"])

    with sm:
        smach.StateMachine.add(
            "IDLE",
            Idle(node),
            transitions={
                "target_received": "MOVE_TO_PICK"
            }
        )

        smach.StateMachine.add(
            "MOVE_TO_PICK",
            MoveToPick(node),
            transitions={
                "success": "WAIT_AT_PICK",
                "failed": "FAILED"
            }
        )

        smach.StateMachine.add(
            "WAIT_AT_PICK",
            WaitAtPick(node),
            transitions={
                "done": "DONE_STATE"
            }
        )

        smach.StateMachine.add(
            "DONE_STATE",
            DoneState(node),
            transitions={
                "done": "DONE"
            }
        )

    sis = IntrospectionServer(
        "arm_state_machine_server",
        sm,
        "/SM_ROOT"
    )
    sis.start()

    sm_thread = threading.Thread(target=sm.execute)
    sm_thread.start()

    try:
        rclpy.spin(node)
    finally:
        sis.stop()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()