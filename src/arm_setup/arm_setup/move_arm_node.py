#!/usr/bin/env python3

# ---
# Move Arm ROS2 Node
# Step 4
# 
# Subscribe to PointStamped from Pixel to Pose, which is an adjusted coordinate
#           of the item that needs to be picked up
# Sends Moveit action goals 
#
# Acknowledgements: part of the code comes from teaching lab UR3e documentation
# ---

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from geometry_msgs.msg import PoseStamped
from moveit_msgs.msg import PositionConstraint, OrientationConstraint
from shape_msgs.msg import SolidPrimitive

from geometry_msgs.msg import PointStamped, Pose, Vector3
from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import (
    Constraints,
    PositionConstraint,
    OrientationConstraint,
    BoundingVolume,
    MotionPlanRequest,
    PlanningOptions,
    MoveItErrorCodes,
)
from shape_msgs.msg import SolidPrimitive


class MoveArmNode(Node):
    def __init__(self):
        super().__init__("move_arm_node")

        self.group_name = "ur_manipulator"
        self.ee_link = "tool0"
        self.frame_id = "base_link"

        self.busy = False

        self.moveit_client = ActionClient(
            self,
            MoveGroup,
            "/move_action"   # change to "/move_group" if that is your action name
        )

        self.get_logger().info("Waiting for MoveIt action server...")
        self.moveit_client.wait_for_server()
        self.get_logger().info("Connected to MoveIt action server.")

        self.create_subscription(
            PointStamped,
            "/target_point",
            self.target_callback,
            10
        )

        self.get_logger().info("MoveArm node started")

    def target_callback(self, msg):
        x = msg.point.x
        y = msg.point.y
        z = msg.point.z

        self.get_logger().info(
            f"Received target point: x={x:.3f}, y={y:.3f}, z={z:.3f}"
        )

        self.move_to_pose("Camera target", x, y, z)


    def move_to_pose(self, name, x, y, z):
        print(f"Moving to {name}: x={x}, y={y}, z={z}")

        if self.busy:
            self.get_logger().warn("Already moving; ignoring new target")
            return

        self.busy = True

        request = MotionPlanRequest()
        request.group_name = "ur_manipulator"
        request.num_planning_attempts = 20
        request.allowed_planning_time = 20.0
        request.max_velocity_scaling_factor = 0.3
        request.max_acceleration_scaling_factor = 0.3

        request.workspace_parameters.header.frame_id = "base_link"
        request.workspace_parameters.min_corner = Vector3(x=-1.0, y=-1.0, z=-1.0)
        request.workspace_parameters.max_corner = Vector3(x=1.0, y=1.0, z=1.0)

        constraints = Constraints()

        # -------------------------------
        # Position constraint
        # -------------------------------
        position_constraint = PositionConstraint()
        position_constraint.header.frame_id = "base_link"

        # IMPORTANT: check your actual end-effector link name in RViz/URDF
        position_constraint.link_name = "tool0"

        box = SolidPrimitive()
        box.type = SolidPrimitive.BOX
        box.dimensions = [0.02, 0.02, 0.02]  # allowed target tolerance box

        target_pose = PoseStamped()
        target_pose.header.frame_id = "base_link"
        target_pose.pose.position.x = x
        target_pose.pose.position.y = y
        target_pose.pose.position.z = z
        target_pose.pose.orientation.w = 1.0

        position_constraint.constraint_region.primitives.append(box)
        position_constraint.constraint_region.primitive_poses.append(target_pose.pose)
        position_constraint.weight = 1.0

        constraints.position_constraints.append(position_constraint)

        # -------------------------------
        # Orientation constraint
        # -------------------------------
        orientation_constraint = OrientationConstraint()
        orientation_constraint.header.frame_id = "base_link"
        orientation_constraint.link_name = "tool0"

        # Example neutral orientation
        # You may need to change this depending on how you want the wrist/tool pointed
        orientation_constraint.orientation.x = 1.0
        orientation_constraint.orientation.y = 0.0
        orientation_constraint.orientation.z = 0.0
        orientation_constraint.orientation.w = 0.0

        orientation_constraint.absolute_x_axis_tolerance = 0.4
        orientation_constraint.absolute_y_axis_tolerance = 0.4
        orientation_constraint.absolute_z_axis_tolerance = 0.4
        orientation_constraint.weight = 1.0

        constraints.orientation_constraints.append(orientation_constraint)

        request.goal_constraints.append(constraints)

        goal = MoveGroup.Goal()
        goal.request = request
        goal.planning_options.plan_only = False
        goal.planning_options.replan = True
        goal.planning_options.replan_attempts = 10
        goal.planning_options.planning_scene_diff.is_diff = True

        future = self.moveit_client.send_goal_async(goal)
        future.add_done_callback(self.goal_response_callback)
        #rclpy.spin_until_future_complete(self, future)

        #result_future = future.result().get_result_async()
        #rclpy.spin_until_future_complete(self, result_future)

    def goal_response_callback(self, future):
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().error("MoveIt rejected the goal")
            self.busy = False
            return

        self.get_logger().info("MoveIt accepted the goal")

        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    def result_callback(self, future):
        result = future.result().result
        error_code = result.error_code.val

        if error_code == 1:
            self.get_logger().info("MoveIt planning/execution succeeded")
        else:
            self.get_logger().error(f"MoveIt failed with error code: {error_code}")

        self.busy = False


def main(args=None):
    rclpy.init(args=args)

    node = MoveArmNode()

    try:

        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()