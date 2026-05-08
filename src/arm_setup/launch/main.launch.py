# ---
# Launch file
# 
# 
# ---

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription, TimerAction, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():

    ur_moveit_dir = get_package_share_directory('ur_moveit_config')
    ur_driver_dir = get_package_share_directory('ur_robot_driver')

    # Set CycloneDDS for ALL nodes in this launch file
    set_rmw = SetEnvironmentVariable(
        name='RMW_IMPLEMENTATION',
        value='rmw_cyclonedds_cpp'
    )

    # UR driver in fake/simulation mode
    ur_driver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ur_driver_dir, 'launch', 'ur_control.launch.py')
        ),
        launch_arguments={
            'ur_type': 'ur3e',
            'robot_ip': '192.168.56.101',
            'kinematics_params': os.path.expanduser('~/my_robot_calibration.yaml'),
            'launch_rviz': 'false',
            'use_fake_hardware': 'true',   # ← fake simulation mode
            'fake_sensor_commands': 'true',
        }.items()
    )

    # MoveIt - delayed to give driver time to start
    moveit = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ur_moveit_dir, 'launch', 'ur_moveit.launch.py')
        ),
        launch_arguments={
            'ur_type': 'ur3e',
            'launch_rviz': 'false',
        }.items()
    )

    # Static transform publisher
    static_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['0.30', '0.10', '0.10',
                   '-0.7854', '0.0', '-1.5708',
                   'base_link', 'camera_link'],
    )

    return LaunchDescription([

        ur_driver,
        moveit,
        static_tf,

        # Pixel to pose node
        Node(
            package='arm_setup',
            executable='pixel_to_pose',
            additional_env={'RMW_IMPLEMENTATION': 'rmw_cyclonedds_cpp'}
        ),

        # Move arm node
        Node(
            package='arm_setup',
            executable='move_arm_node',
            additional_env={'RMW_IMPLEMENTATION': 'rmw_cyclonedds_cpp'}
        ),

         # Move arm node
        Node(
            package='arm_setup',
            executable='color_detector_node',
            additional_env={'RMW_IMPLEMENTATION': 'rmw_cyclonedds_cpp'}
        ),

        Node(
            package='arm_setup',
            executable='camera_publisher',
            additional_env={'RMW_IMPLEMENTATION': 'rmw_cyclonedds_cpp'}
        ),
    ])