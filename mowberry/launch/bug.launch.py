"""bug: BringUp with GPS.

Equivalent to running:
  ros2 launch mowberry zedf9p_ntrip.launch.py
  ros2 launch linorobot2_bringup bringup.launch.py \
      base_serial_port:=/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    gps_launch_path = PathJoinSubstitution(
        [FindPackageShare('mowberry'), 'launch', 'zedf9p_ntrip.launch.py']
    )

    bringup_launch_path = PathJoinSubstitution(
        [FindPackageShare('linorobot2_bringup'), 'launch', 'bringup.launch.py']
    )

    base_serial_port_arg = DeclareLaunchArgument(
        'base_serial_port',
        default_value='/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0',
        description='Linorobot Base Serial Port'
    )

    gps_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gps_launch_path)
    )

    bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(bringup_launch_path),
        launch_arguments={
            'base_serial_port': LaunchConfiguration('base_serial_port')
        }.items()
    )

    return LaunchDescription([
        base_serial_port_arg,
        gps_launch,
        bringup_launch,
    ])
