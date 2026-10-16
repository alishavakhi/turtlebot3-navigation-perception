from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import AnyLaunchDescriptionSource, PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

    pkg_share = get_package_share_directory('group29_assignment_1')

    apriltag_launch = os.path.join(
        pkg_share,
        'launch',
        'camera_group29.launch.yml'
    )

    rviz_config_path = os.path.join(
        pkg_share,
        'cfg',
        'assignment_view.rviz'
    )

    ir_launch_pkg = get_package_share_directory('ir_launch')

    sim_launch = os.path.join(
        ir_launch_pkg,
        'launch',
        'assignment_1.launch.py'
    )

    return LaunchDescription([

        IncludeLaunchDescription(
            AnyLaunchDescriptionSource(apriltag_launch)
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(sim_launch),
            launch_arguments={
                'rviz_config_file': rviz_config_path
            }.items()
        ),

        Node(
            package='group29_assignment_1',
            executable='april_tag_node.py',
            name='AprilTag',
            output='log'
        ),

        Node(
            package='group29_assignment_1',
            executable='navigation_node.py',
            name='Navigation',
            output='log'
        ),

        Node(
            package='group29_assignment_1',
            executable='table_detector.py',
            name='TableDec',
            output='screen'
        ),
        Node(
            package='group29_assignment_1',
            executable='corridor_controller_node.py',
            name='CorridorController',
            output='screen'
        ),
])