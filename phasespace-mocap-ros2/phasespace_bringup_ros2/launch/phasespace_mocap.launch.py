from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    server_ip = LaunchConfiguration("server_ip")

    return LaunchDescription([
        DeclareLaunchArgument(
            "server_ip",
            default_value="192.168.0.102",
            description="IP address of the Phasespace OWL server",
        ),
        Node(
            package="phasespace_bringup_ros2",
            executable="phasespace_bringup_node",
            name="phasespace_bringup",
            output="screen",
            parameters=[{"server_ip": server_ip}],
        ),
    ])
