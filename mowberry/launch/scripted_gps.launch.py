import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch.conditions import IfCondition, UnlessCondition
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Declare Launch Arguments

    # 1. GPS Driver Launch Arguments (from lc29h_da_rtk_gps_driver)
    gps_port_arg = DeclareLaunchArgument(
        'gps_port',
        default_value='/dev/ttyAMA0',
        description='Serial port for GPS device'
    )

    ntrip_host_arg = DeclareLaunchArgument(
        'ntrip_host',
        #default_value='rtk2go.com',
        default_value='192.168.4.252',
        description='NTRIP host'
    )

    ntrip_mountpoint_arg = DeclareLaunchArgument(
        'ntrip_mountpoint',
        #default_value='VN1',
        default_value='LittleElm_L1L5',
        description='NTRIP mountpoint'
    )

    ntrip_username_arg = DeclareLaunchArgument(
        'ntrip_username',
        default_value='paul.bouchier-at-gmail-d-com',
        description='NTRIP username'
    )

    origin_lat_arg = DeclareLaunchArgument(
        'origin_lat',
        default_value='33.15777543',
        description='Latitude of the origin point'
    )

    origin_lon_arg = DeclareLaunchArgument(
        'origin_lon',
        default_value='-96.93730808',
        description='Longitude of the origin point'
    )

    origin_alt_arg = DeclareLaunchArgument(
        'origin_alt',
        default_value='169.54',
        description='Altitude of the origin point'
    )

    # 2. Linorobot2 Bringup Launch Arguments (from linorobot2_bringup)
    base_serial_port_arg = DeclareLaunchArgument(
        name='base_serial_port', 
        default_value='/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0',
        description='ESP32 Base Serial Port'
    )

    # Linorobot2 Bringup launch file: bringup.launch.py
    bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('linorobot2_bringup'),
                'launch',
                'bringup.launch.py'
            )
        ),
        launch_arguments={
            'base_serial_port': LaunchConfiguration('base_serial_port')
        }.items()
    )

    # GPS Driver launch file: lc29h_da_rtk_gps_driver.launch.py
    lc29h_da_rtk_gps_driver_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('lc29h_da_rtk_gps_driver'),
                'launch',
                'lc29h_da_rtk_gps_driver.launch.py'
            )
        ),
        launch_arguments={
            'port': LaunchConfiguration('gps_port'),
            'ntrip_host': LaunchConfiguration('ntrip_host'),
            'ntrip_mountpoint': LaunchConfiguration('ntrip_mountpoint'),
            'ntrip_username': LaunchConfiguration('ntrip_username')
        }.items()
    )

    # Node that maps GPS coordinates to local map coordinates.
    # One would run it manually like this:
    # ros2 run mowberry gps_to_local_map_pose --ros-args -p origin_lat:=33.15777543 -p origin_lon:=-96.93730808 -p origin_alt:=169.54
    gps_to_local_map_pose_node = Node(
        package='mowberry',
        executable='gps_to_local_map_pose',
        name='gps_to_local_map_pose',
        output='screen',
        parameters=[{
            'origin_lat': LaunchConfiguration('origin_lat'),
            'origin_lon': LaunchConfiguration('origin_lon'),
            'origin_alt': LaunchConfiguration('origin_alt')
        }]
    )

    return LaunchDescription([
        # Launch Arguments
        gps_port_arg,
        ntrip_host_arg,
        ntrip_mountpoint_arg,
        ntrip_username_arg,
        base_serial_port_arg,
        origin_lat_arg,
        origin_lon_arg,
        origin_alt_arg,

        # Nodes and Included Launches
        lc29h_da_rtk_gps_driver_node,
        bringup_launch,
        gps_to_local_map_pose_node
    ])
