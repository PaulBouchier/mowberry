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
    # Paths for linorobot2_bringup
    sensors_launch_path = PathJoinSubstitution(
        [FindPackageShare('linorobot2_bringup'), 'launch', 'sensors.launch.py']
    )

    joy_launch_path = PathJoinSubstitution(
        [FindPackageShare('linorobot2_bringup'), 'launch', 'joy_teleop.launch.py']
    )

    description_launch_path = PathJoinSubstitution(
        [FindPackageShare('linorobot2_description'), 'launch', 'description.launch.py']
    )

    ekf_config_path = PathJoinSubstitution(
        [FindPackageShare("linorobot2_base"), "config", "ekf.yaml"]
    )

    default_robot_launch_path = PathJoinSubstitution(
        [FindPackageShare('linorobot2_bringup'), 'launch', 'default_robot.launch.py']
    )

    custom_robot_launch_path = PathJoinSubstitution(
        [FindPackageShare('linorobot2_bringup'), 'launch', 'custom_robot.launch.py']
    )

    extra_launch_path = PathJoinSubstitution(
        [FindPackageShare('linorobot2_bringup'), 'launch', 'extra.launch.py']
    )

    # Declare Launch Arguments
    # 1. GPS Driver Launch Arguments (from lc29h_da_rtk_gps_driver)
    gps_port_arg = DeclareLaunchArgument(
        'gps_port',
        default_value='/dev/ttyAMA0',
        description='Serial port for GPS device'
    )

    gps_baudrate_arg = DeclareLaunchArgument(
        'gps_baudrate',
        default_value='115200',
        description='Baudrate for GPS device'
    )

    ntrip_host_arg = DeclareLaunchArgument(
        'ntrip_host',
        default_value='',
        description='NTRIP host'
    )

    ntrip_port_arg = DeclareLaunchArgument(
        'ntrip_port',
        default_value='2101',
        description='NTRIP port'
    )

    ntrip_mountpoint_arg = DeclareLaunchArgument(
        'ntrip_mountpoint',
        default_value='VN1',
        description='NTRIP mountpoint'
    )

    ntrip_username_arg = DeclareLaunchArgument(
        'ntrip_username',
        default_value='paul.bouchier-at-gmail-d-com',
        description='NTRIP username'
    )

    ntrip_password_arg = DeclareLaunchArgument(
        'ntrip_password',
        default_value='none',
        description='NTRIP password'
    )

    ntrip_authenticate_arg = DeclareLaunchArgument(
        'ntrip_authenticate',
        default_value='true',
        description='NTRIP authenticate'
    )

    ntrip_send_nmea_arg = DeclareLaunchArgument(
        'ntrip_send_nmea',
        default_value='false',
        description='NTRIP send_nmea'
    )

    # 2. Linorobot2 Bringup Launch Arguments (from linorobot2_bringup)
    custom_robot_arg = DeclareLaunchArgument(
        name='custom_robot', 
        default_value='false',
        description='Use custom robot'
    )

    extra_arg = DeclareLaunchArgument(
        name='extra', 
        default_value='false',
        description='Launch extra launch file'
    )

    base_serial_port_arg = DeclareLaunchArgument(
        name='base_serial_port', 
        default_value='/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0',
        description='ESP32 Base Serial Port'
    )

    micro_ros_transport_arg = DeclareLaunchArgument(
        name='micro_ros_transport',
        default_value='serial',
        description='micro-ROS transport'
    )

    odom_topic_arg = DeclareLaunchArgument(
        name='odom_topic', 
        default_value='/odom',
        description='EKF out odometry topic'
    )

    # lc29h_da_rtk_gps_driver node
    lc29h_da_rtk_gps_driver_node = Node(
        package='lc29h_da_rtk_gps_driver',
        executable='lc29h_da_rtk_gps_driver',
        name='lc29h_da_rtk_gps_driver',
        output='screen',
        parameters=[{
            'port': LaunchConfiguration('gps_port'),
            'baudrate': LaunchConfiguration('gps_baudrate')
        }]
    )

    # ntrip_client launch
    ntrip_client_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('ntrip_client'),
                'ntrip_client_launch.py'
            )
        ),
        launch_arguments={
            'host': LaunchConfiguration('ntrip_host'),
            'port': LaunchConfiguration('ntrip_port'),
            'mountpoint': LaunchConfiguration('ntrip_mountpoint'),
            'username': LaunchConfiguration('ntrip_username'),
            'password': LaunchConfiguration('ntrip_password'),
            'authenticate': LaunchConfiguration('ntrip_authenticate'),
            'send_nmea': LaunchConfiguration('ntrip_send_nmea')
        }.items()
    )

    # Nodes/includes from linorobot2_bringup:
    ekf_filter_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[
            ekf_config_path
        ],
        remappings=[("odometry/filtered", LaunchConfiguration("odom_topic"))]
    )

    default_robot_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(default_robot_launch_path),
        condition=UnlessCondition(LaunchConfiguration("custom_robot")),
        launch_arguments={
            'base_serial_port': LaunchConfiguration("base_serial_port")
        }.items()
    )

    extra_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(extra_launch_path),
        condition=IfCondition(LaunchConfiguration("extra")),
    )

    custom_robot_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(custom_robot_launch_path),
        condition=IfCondition(LaunchConfiguration("custom_robot")),
    )

    # Nodes from servers_launch:
    stop_node = Node(
        package='scripted_bot_driver',
        executable='stop',
        name='stop',
        output='screen',
        emulate_tty=True
    )

    drive_straight_odom_node = Node(
        package='scripted_bot_driver',
        executable='drive_straight_odom',
        name='drive_straight_odom',
        output='screen',
        emulate_tty=True
    )

    drive_straight_map_node = Node(
        package='scripted_bot_driver',
        executable='drive_straight_map',
        name='drive_straight_map',
        output='screen',
        emulate_tty=True
    )

    rotate_odom_node = Node(
        package='scripted_bot_driver',
        executable='rotate_odom',
        name='rotate_odom',
        output='screen',
        emulate_tty=True
    )

    drive_waypoints_node = Node(
        package='scripted_bot_driver',
        executable='drive_waypoints',
        name='drive_waypoints',
        output='screen',
        emulate_tty=True
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
            'origin_lat': 33.15777543,
            'origin_lon': -96.93730808,
            'origin_alt': 169.54
        }]
    )

    return LaunchDescription([
        # Launch Arguments
        gps_port_arg,
        gps_baudrate_arg,
        ntrip_host_arg,
        ntrip_port_arg,
        ntrip_mountpoint_arg,
        ntrip_username_arg,
        ntrip_password_arg,
        ntrip_authenticate_arg,
        ntrip_send_nmea_arg,
        custom_robot_arg,
        extra_arg,
        base_serial_port_arg,
        micro_ros_transport_arg,
        odom_topic_arg,

        # Nodes and Included Launches
        lc29h_da_rtk_gps_driver_node,
        ntrip_client_launch,
        ekf_filter_node,
        default_robot_launch,
        extra_launch,
        custom_robot_launch,
        stop_node,
        drive_straight_odom_node,
        drive_straight_map_node,
        rotate_odom_node,
        drive_waypoints_node,
        gps_to_local_map_pose_node,
    ])
