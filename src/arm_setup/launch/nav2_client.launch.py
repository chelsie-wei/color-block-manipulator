# Turtlebot launch file

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():

    # --- Tab 2: turtle_bridge.py (rosbridge client) ---
    turtle_bridge = Node(
        package='arm_setup',
        executable='turtle_bridge',
        name='turtle_bridge',
        output='screen'
    )

    # --- Tab 3: SLAM Toolbox ---
    slam_dir = get_package_share_directory('slam_toolbox')
    slam_launch = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(
        os.path.join(slam_dir, 'launch', 'online_async_launch.py')
    ),
    launch_arguments={
        'use_sim_time': 'False',
        #'slam_params_file': os.path.expanduser('~/slam_toolbox_params.yaml'),
    }.items()
)

    # --- Tab 4: RViz2 ---
    rviz2 = ExecuteProcess(
        cmd=['rviz2'],
        output='screen'
    )

    # --- Tab 5: Nav2 ---
    nav2_dir = get_package_share_directory('nav2_bringup')
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_dir, 'launch', 'navigation_launch.py')
        ),
        launch_arguments={
            'use_sim_time': 'false',
            'params_file': os.path.expanduser('~/nav2_params.yaml'),
        }.items()
    )

    return LaunchDescription([
        turtle_bridge,
        slam_launch,
        rviz2,
        nav2_launch,
    ])

